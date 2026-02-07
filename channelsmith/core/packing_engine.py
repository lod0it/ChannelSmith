"""
Texture channel packing engine.

This module provides the core functionality for packing multiple grayscale
texture channels into a single RGB or RGBA image.
"""

from typing import List, Dict, Optional, Tuple, Union
import numpy as np
from PIL import Image

from channelsmith.core.validator import (
    validate_channel_data,
    validate_arrays_for_packing,
    get_max_resolution,
)
from channelsmith.core.packing_template import PackingTemplate
from channelsmith.utils.image_utils import to_grayscale, from_grayscale


def normalize_resolution(
    arrays: List[np.ndarray],
    target_size: Tuple[int, int]
) -> List[np.ndarray]:
    """
    Normalize all arrays to the target resolution using bilinear interpolation.

    Upscales arrays that are smaller than the target size. Arrays already
    at the target size are returned unchanged.

    Args:
        arrays: List of 2D NumPy arrays to normalize
        target_size: Target (width, height) tuple

    Returns:
        List of normalized NumPy arrays, all with shape (height, width)
        matching the target size

    Raises:
        ValueError: If target_size is invalid or arrays list is empty

    Example:
        >>> arr1 = np.zeros((512, 512), dtype=np.uint8)
        >>> arr2 = np.zeros((1024, 1024), dtype=np.uint8)
        >>> normalized = normalize_resolution([arr1, arr2], (1024, 1024))
        >>> normalized[0].shape
        (1024, 1024)
        >>> normalized[1].shape
        (1024, 1024)
    """
    if not arrays:
        raise ValueError("Arrays list cannot be empty")

    if len(target_size) != 2 or target_size[0] <= 0 or target_size[1] <= 0:
        raise ValueError(
            f"Invalid target_size: {target_size}. Must be (width, height) with positive values"
        )

    target_width, target_height = target_size
    normalized = []

    for arr in arrays:
        # Validate the array
        validate_channel_data(arr)

        # Get current size (height, width)
        current_height, current_width = arr.shape

        # Check if resizing is needed
        if current_width == target_width and current_height == target_height:
            # Already at target size
            normalized.append(arr)
        else:
            # Convert to PIL Image for resizing
            img = from_grayscale(arr)

            # Resize using bilinear interpolation
            resized_img = img.resize((target_width, target_height), Image.BILINEAR)

            # Convert back to NumPy array
            resized_arr = to_grayscale(resized_img)
            normalized.append(resized_arr)

    return normalized


def pack_channels(
    r: Optional[np.ndarray] = None,
    g: Optional[np.ndarray] = None,
    b: Optional[np.ndarray] = None,
    a: Optional[np.ndarray] = None
) -> Image.Image:
    """
    Pack grayscale channel arrays into a single RGB or RGBA image.

    Stacks up to 4 grayscale channels into a multi-channel image. At least
    one channel must be provided. If channels have different resolutions,
    they will be normalized to the maximum resolution.

    Args:
        r: Red channel as 2D NumPy array (or None)
        g: Green channel as 2D NumPy array (or None)
        b: Blue channel as 2D NumPy array (or None)
        a: Alpha channel as 2D NumPy array (or None)

    Returns:
        PIL Image in RGB mode (if no alpha) or RGBA mode (if alpha provided)

    Raises:
        ValueError: If all channels are None
        InvalidChannelDataError: If channel data is invalid

    Example:
        >>> r_channel = np.full((1024, 1024), 255, dtype=np.uint8)
        >>> g_channel = np.full((1024, 1024), 128, dtype=np.uint8)
        >>> b_channel = np.zeros((1024, 1024), dtype=np.uint8)
        >>> packed = pack_channels(r_channel, g_channel, b_channel)
        >>> packed.mode
        'RGB'
        >>> packed.size
        (1024, 1024)
    """
    # Collect non-None channels
    channels = [r, g, b, a]
    channel_names = ['R', 'G', 'B', 'A']

    valid_channels = [(ch, name) for ch, name in zip(channels, channel_names) if ch is not None]

    if not valid_channels:
        raise ValueError("At least one channel must be provided (not None)")

    # Validate each array individually
    valid_arrays = [ch for ch, _ in valid_channels]
    for arr in valid_arrays:
        validate_channel_data(arr)

    # Get maximum resolution from all channels (they may have different sizes)
    max_height = max(arr.shape[0] for arr in valid_arrays)
    max_width = max(arr.shape[1] for arr in valid_arrays)
    target_size = (max_width, max_height)

    # Normalize all channels to the same resolution
    normalized_channels = normalize_resolution(valid_arrays, target_size)

    # Map normalized arrays back to RGBA slots
    normalized_map = dict(zip([name for _, name in valid_channels], normalized_channels))

    # Build the final channel list with zeros for missing channels
    final_channels = []
    for ch_name in ['R', 'G', 'B']:
        if ch_name in normalized_map:
            final_channels.append(normalized_map[ch_name])
        else:
            # Fill missing RGB channels with zeros
            final_channels.append(np.zeros((max_height, max_width), dtype=np.uint8))

    # Determine if we need alpha channel
    has_alpha = 'A' in normalized_map

    if has_alpha:
        final_channels.append(normalized_map['A'])
        mode = 'RGBA'
    else:
        mode = 'RGB'

    # Stack channels along the third axis
    stacked = np.stack(final_channels, axis=2)

    # Create PIL Image
    packed_image = Image.fromarray(stacked, mode=mode)

    return packed_image


def pack_texture_from_template(
    textures: Dict[str, Optional[Union[str, Image.Image, np.ndarray]]],
    template: PackingTemplate
) -> Image.Image:
    """
    Pack textures according to a template's channel mapping.

    Takes a dictionary mapping texture types to image sources, and packs
    them according to the template's channel assignments. Missing textures
    are filled with default values from the template.

    Args:
        textures: Dictionary mapping texture types (e.g., 'ambient_occlusion',
                 'roughness') to image sources. Values can be:
                 - File path (str)
                 - PIL Image
                 - NumPy array
                 - None (will use template default)
        template: PackingTemplate defining how channels are mapped to RGBA

    Returns:
        Packed PIL Image in RGB or RGBA mode

    Raises:
        ValueError: If template is invalid or no valid textures provided
        InvalidChannelDataError: If texture data is invalid

    Example:
        >>> from channelsmith.templates import load_template
        >>> template = load_template('channelsmith/templates/orm.json')
        >>> textures = {
        ...     'ambient_occlusion': 'textures/ao.png',
        ...     'roughness': 'textures/roughness.png',
        ...     'metallic': 'textures/metallic.png'
        ... }
        >>> packed = pack_texture_from_template(textures, template)
        >>> packed.mode
        'RGB'
    """
    from channelsmith.utils.image_utils import load_image

    if not isinstance(template, PackingTemplate):
        raise TypeError(
            f"Expected PackingTemplate instance, got {type(template).__name__}"
        )

    # Build channel arrays for RGBA slots
    channel_arrays = {}

    for channel_key in ['R', 'G', 'B', 'A']:
        channel_map = template.get_channel(channel_key)

        if channel_map is None:
            # Channel not used in template
            channel_arrays[channel_key] = None
            continue

        # Get texture for this channel's map_type
        texture_source = textures.get(channel_map.map_type)

        if texture_source is None:
            # No texture provided - use default value
            # We'll create this later once we know the target resolution
            channel_arrays[channel_key] = None
        elif isinstance(texture_source, str):
            # File path - load it
            img = load_image(texture_source)
            channel_arrays[channel_key] = to_grayscale(img)
        elif isinstance(texture_source, Image.Image):
            # PIL Image - convert to grayscale
            channel_arrays[channel_key] = to_grayscale(texture_source)
        elif isinstance(texture_source, np.ndarray):
            # NumPy array - validate it
            validate_channel_data(texture_source)
            channel_arrays[channel_key] = texture_source
        else:
            raise TypeError(
                f"Invalid texture source for '{channel_map.map_type}': "
                f"expected str, Image, or ndarray, got {type(texture_source).__name__}"
            )

    # Check if we have at least one valid texture
    valid_textures = [arr for arr in channel_arrays.values() if arr is not None]

    if not valid_textures:
        # No textures provided - need to determine default resolution
        # Use a reasonable default (1024x1024)
        default_resolution = (1024, 1024)
        target_width, target_height = default_resolution
    else:
        # Validate each texture array
        for arr in valid_textures:
            validate_channel_data(arr)

        # Get maximum resolution from all textures (they may have different sizes)
        max_height = max(arr.shape[0] for arr in valid_textures)
        max_width = max(arr.shape[1] for arr in valid_textures)
        target_width, target_height = max_width, max_height

    # Fill missing channels with default values
    for channel_key in ['R', 'G', 'B', 'A']:
        if channel_arrays[channel_key] is None:
            channel_map = template.get_channel(channel_key)
            if channel_map is not None:
                # Create array filled with default value
                default_value_uint8 = int(channel_map.default_value * 255)
                channel_arrays[channel_key] = np.full(
                    (target_height, target_width),
                    default_value_uint8,
                    dtype=np.uint8
                )

    # Pack the channels
    packed = pack_channels(
        r=channel_arrays.get('R'),
        g=channel_arrays.get('G'),
        b=channel_arrays.get('B'),
        a=channel_arrays.get('A')
    )

    return packed


def create_default_channel(
    size: Tuple[int, int],
    default_value: float
) -> np.ndarray:
    """
    Create a channel array filled with a default value.

    Args:
        size: (width, height) tuple
        default_value: Fill value in range 0.0-1.0

    Returns:
        2D NumPy array filled with the default value (converted to uint8)

    Example:
        >>> channel = create_default_channel((512, 512), 0.5)
        >>> channel.shape
        (512, 512)
        >>> channel[0, 0]
        127
    """
    if not (0.0 <= default_value <= 1.0):
        raise ValueError(
            f"default_value must be between 0.0 and 1.0, got {default_value}"
        )

    width, height = size
    value_uint8 = int(default_value * 255)

    return np.full((height, width), value_uint8, dtype=np.uint8)
