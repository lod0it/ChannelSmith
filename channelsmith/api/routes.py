"""
REST API routes for ChannelSmith.

This module defines all HTTP endpoints that wrap the core packing/unpacking
functionality and provide template management.
"""

import io
import logging
from pathlib import Path

from flask import Blueprint, request, jsonify, send_file
from PIL import Image

import numpy as np

from channelsmith.core import pack_texture_from_template, unpack_texture
from channelsmith.templates.template_loader import load_template
from channelsmith.api.utils import image_to_base64, base64_to_image, validate_image_file
from channelsmith.utils.image_utils import from_grayscale

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)


def get_template_names() -> list:
    """Get list of built-in template names."""
    templates_dir = Path(__file__).parent.parent / "templates"
    built_in = []

    for json_file in templates_dir.glob("*.json"):
        name = json_file.stem.upper()
        built_in.append(name)

    return sorted(built_in)


def get_template_path(template_name: str) -> Path:
    """Get full path to template JSON file."""
    templates_dir = Path(__file__).parent.parent / "templates"
    return templates_dir / f"{template_name.lower()}.json"


@api_bp.route("/health", methods=["GET"])
def health() -> tuple:
    """
    Health check endpoint.

    Returns:
        JSON response with status and version
    """
    return jsonify({"status": "ok", "version": "0.1.0-web"}), 200


@api_bp.route("/templates", methods=["GET"])
def get_templates() -> tuple:
    """
    Get list of available templates.

    Returns:
        JSON response with template names
    """
    try:
        templates = get_template_names()
        return jsonify({"templates": templates, "custom": []}), 200
    except Exception as e:
        logger.exception("Error getting templates: %s", e)
        return jsonify({"error": str(e)}), 500


@api_bp.route("/pack", methods=["POST"])
def pack() -> tuple:
    """
    Pack texture channels into a single image.

    Expected form data:
        - template: Template name (e.g., "ORM", "ORD")
        - red_channel: (optional) Image file for red channel
        - green_channel: (optional) Image file for green channel
        - blue_channel: (optional) Image file for blue channel
        - alpha_channel: (optional) Image file for alpha channel

    Returns:
        Packed PNG image or error response
    """
    try:
        # Get template name
        template_name = request.form.get("template", "ORM")
        template_path = get_template_path(template_name)

        if not template_path.exists():
            return jsonify({"error": f"Template not found: {template_name}"}), 400

        # Load template
        template = load_template(str(template_path))

        # Mapping from file field names to texture types
        field_to_texture_type = {
            "red_channel": "ambient_occlusion",
            "green_channel": "roughness",
            "blue_channel": "metallic",
            "alpha_channel": "opacity",
        }

        # Load channel images and map to texture types
        textures = {}
        for file_key, texture_type in field_to_texture_type.items():
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    try:
                        img = Image.open(file.stream).convert("L")
                        textures[texture_type] = img
                    except Exception as e:
                        logger.error("Error loading %s channel: %s", file_key, e)
                        return jsonify({"error": f"Invalid {file_key} image"}), 400

        # Pack texture using the template
        try:
            packed_img = pack_texture_from_template(textures, template)
        except Exception as e:
            logger.error("Error packing texture: %s", e)
            return jsonify({"error": f"Failed to pack texture: {str(e)}"}), 400

        # Convert to PNG bytes
        img_bytes = io.BytesIO()
        packed_img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return send_file(img_bytes, mimetype="image/png"), 200

    except Exception as e:
        logger.exception("Error in pack endpoint: %s", e)
        return jsonify({"error": str(e)}), 500


@api_bp.route("/unpack", methods=["POST"])
def unpack() -> tuple:
    """
    Unpack a texture image into individual channels.

    Expected form data:
        - image: Packed image file
        - template: Template name (e.g., "ORM", "ORD")

    Returns:
        JSON response with Base64-encoded channel images
    """
    try:
        # Get template name
        template_name = request.form.get("template", "ORM")
        template_path = get_template_path(template_name)

        if not template_path.exists():
            return jsonify({"error": f"Template not found: {template_name}"}), 400

        # Load template
        template = load_template(str(template_path))

        # Get image file
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        if not file or not file.filename:
            return jsonify({"error": "No image file selected"}), 400

        # Validate and load image
        try:
            img = Image.open(file.stream)
            validate_image_file(img, template)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error("Error loading image: %s", e)
            return jsonify({"error": "Invalid image file"}), 400

        # Unpack texture
        try:
            unpacked = unpack_texture(img, template)
        except Exception as e:
            logger.error("Error unpacking texture: %s", e)
            return jsonify({"error": f"Failed to unpack texture: {str(e)}"}), 400

        # Build reverse mapping from semantic names to channel positions
        position_map = {}
        for channel_pos, channel_map in template.get_used_channels().items():
            position_map[channel_map.map_type] = channel_pos

        # Convert numpy arrays to PIL images, then to Base64 for response
        # Use channel position as key (Red Channel, Green Channel, etc.)
        channels_base64 = {}
        for channel_name, channel_array in unpacked.items():
            # channel_array is a numpy array, convert to PIL Image
            if isinstance(channel_array, np.ndarray):
                channel_img = from_grayscale(channel_array)
            else:
                channel_img = channel_array

            # Use channel position (R, G, B, A) as key for clearer labeling
            channel_pos = position_map.get(channel_name, channel_name)
            channels_base64[channel_pos] = image_to_base64(channel_img)

        return jsonify({"channels": channels_base64}), 200

    except Exception as e:
        logger.exception("Error in unpack endpoint: %s", e)
        return jsonify({"error": str(e)}), 500
