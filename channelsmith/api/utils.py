"""
Utility functions for the Flask API.

This module provides helper functions for file handling, image conversion,
and validation.
"""

import base64
import io
import logging
from typing import Optional

from PIL import Image

from channelsmith.core.packing_template import PackingTemplate

logger = logging.getLogger(__name__)


def image_to_base64(img: Image.Image) -> str:
    """
    Convert PIL Image to Base64-encoded PNG data URL.

    Args:
        img: PIL Image object

    Returns:
        Data URL string (data:image/png;base64,...)
    """
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    b64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def base64_to_image(data: str) -> Image.Image:
    """
    Convert Base64-encoded data to PIL Image.

    Args:
        data: Base64 string or data URL

    Returns:
        PIL Image object

    Raises:
        ValueError: If data is invalid
    """
    try:
        # Remove data URL prefix if present
        if data.startswith("data:image"):
            data = data.split(",", 1)[1]

        img_bytes = base64.b64decode(data)
        return Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        raise ValueError(f"Invalid Base64 image data: {e}") from e


def validate_image_file(
    img: Image.Image, template: Optional[PackingTemplate] = None
) -> bool:
    """
    Validate that an image is suitable for processing.

    Args:
        img: PIL Image object to validate
        template: Optional template for validation

    Returns:
        True if valid

    Raises:
        ValueError: If image is invalid
    """
    # Check image mode
    if img.mode not in ("RGB", "RGBA", "L", "LA"):
        raise ValueError(
            f"Invalid image mode: {img.mode}. "
            "Supported modes: RGB, RGBA, L, LA"
        )

    # Check dimensions
    width, height = img.size
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image dimensions: {width}x{height}")

    # Max resolution check (8K)
    max_res = 8192
    if width > max_res or height > max_res:
        raise ValueError(
            f"Image too large: {width}x{height}. "
            f"Maximum supported: {max_res}x{max_res}"
        )

    return True


def create_default_image(width: int, height: int, value: int = 128) -> Image.Image:
    """
    Create a solid grayscale image with a default value.

    Args:
        width: Image width
        height: Image height
        value: Pixel value (0-255, default 128 for mid-gray)

    Returns:
        PIL Image object
    """
    return Image.new("L", (width, height), value)
