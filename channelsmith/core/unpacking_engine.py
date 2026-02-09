"""
Texture channel unpacking engine.

This module provides the core functionality for extracting individual grayscale
channels from packed RGB or RGBA texture images using template definitions.
"""

import logging
from typing import Dict

import numpy as np
from PIL import Image

from channelsmith.core.packing_template import PackingTemplate

logger = logging.getLogger(__name__)

# Mapping of channel keys to array indices
_CHANNEL_INDEX = {
    "R": 0,
    "G": 1,
    "B": 2,
    "A": 3,
}


def extract_channel(image: Image.Image, channel: str) -> np.ndarray:
    """
    Extract a single channel from a packed texture image.

    Converts the image to a NumPy array and extracts the specified
    R, G, B, or A channel as a 2D grayscale array.

    Args:
        image: Packed texture image (RGB or RGBA)
        channel: Channel key to extract ('R', 'G', 'B', or 'A')

    Returns:
        2D NumPy array (uint8) containing the extracted channel data

    Raises:
        TypeError: If image is not a PIL Image instance
        ValueError: If channel key is invalid or the requested channel
                   is not available in the image (e.g., 'A' from an RGB image)

    Example:
        >>> packed = Image.new('RGB', (512, 512), (255, 128, 64))
        >>> r_channel = extract_channel(packed, 'R')
        >>> r_channel[0, 0]
        255
        >>> g_channel = extract_channel(packed, 'G')
        >>> g_channel[0, 0]
        128
    """
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected PIL Image instance, got {type(image).__name__}")

    if channel not in _CHANNEL_INDEX:
        raise ValueError(
            f"Invalid channel key: '{channel}'. Must be 'R', 'G', 'B', or 'A'"
        )

    # Check if image has the requested channel
    if channel == "A" and image.mode != "RGBA":
        raise ValueError(
            f"Cannot extract alpha channel from '{image.mode}' image. "
            f"Image must be RGBA mode to extract the alpha channel."
        )

    # Convert grayscale images to RGB for consistent indexing
    if image.mode == "L":
        image = image.convert("RGB")
    elif image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if channel == "A" else "RGB")

    # Convert to NumPy array
    image_array = np.array(image, dtype=np.uint8)

    # Extract the requested channel
    channel_index = _CHANNEL_INDEX[channel]
    extracted = image_array[:, :, channel_index]

    return extracted


def unpack_texture(
    image: Image.Image, template: PackingTemplate
) -> Dict[str, np.ndarray]:
    """
    Extract individual channels from a packed texture using a template.

    Maps each channel defined in the template back to its texture type,
    returning a dictionary of texture type names to grayscale arrays.

    Args:
        image: Packed texture image (RGB or RGBA)
        template: Template defining how channels are mapped to texture types

    Returns:
        Dictionary mapping texture type names (e.g., 'ambient_occlusion',
        'roughness') to 2D NumPy arrays (uint8)

    Raises:
        TypeError: If image is not a PIL Image or template is not a PackingTemplate
        ValueError: If the image mode doesn't match the template expectations
                   (e.g., template requires alpha but image is RGB)

    Example:
        >>> from channelsmith.core.packing_template import PackingTemplate
        >>> from channelsmith.core.channel_map import ChannelMap
        >>> template = PackingTemplate('ORM', 'Occlusion-Roughness-Metallic', {
        ...     'R': ChannelMap('ambient_occlusion', 1.0),
        ...     'G': ChannelMap('roughness', 0.5),
        ...     'B': ChannelMap('metallic', 0.0)
        ... })
        >>> packed = Image.new('RGB', (512, 512), (255, 128, 0))
        >>> channels = unpack_texture(packed, template)
        >>> channels['ambient_occlusion'][0, 0]
        255
        >>> channels['roughness'][0, 0]
        128
    """
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected PIL Image instance, got {type(image).__name__}")

    if not isinstance(template, PackingTemplate):
        raise TypeError(
            f"Expected PackingTemplate instance, got {type(template).__name__}"
        )

    # Note: Alpha channel is optional for unpacking, even if template defines it.
    # We only extract alpha if the image actually has it (RGBA mode).

    # Extract each channel defined in the template
    result = {}
    used_channels = template.get_used_channels()

    for channel_key, channel_map in used_channels.items():
        # Skip alpha channel if image doesn't have it (RGB images have no alpha)
        if channel_key == "A" and image.mode != "RGBA":
            continue

        extracted = extract_channel(image, channel_key)
        result[channel_map.map_type] = extracted

    # AUTO-EXTRACT ALPHA: If image is RGBA and template doesn't already define alpha,
    # automatically extract it so users can preview/download
    if image.mode == "RGBA" and not template.is_channel_used("A"):
        try:
            alpha_data = extract_channel(image, "A")
            result["alpha"] = alpha_data
            logger.info(
                "Auto-extracted alpha channel from RGBA image (not in template '%s')",
                template.name,
            )
        except Exception as e:
            logger.warning("Failed to auto-extract alpha channel: %s", e)
            # Don't fail the entire operation if alpha extraction fails

    logger.info(
        "Unpacked %d channels from %s image using template '%s'",
        len(result),
        image.mode,
        template.name,
    )
    return result
