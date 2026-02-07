"""
Validation functions for texture channel packing operations.

This module provides validation utilities to ensure data integrity before
packing/unpacking operations, including resolution checking and channel
data validation.
"""

from typing import List, Tuple, Optional
import numpy as np
from PIL import Image


class ResolutionMismatchError(Exception):
    """Raised when image resolutions don't match."""
    pass


class InvalidChannelDataError(Exception):
    """Raised when channel data is invalid or malformed."""
    pass


def check_resolution_match(images: List[Image.Image]) -> bool:
    """
    Check if all images have the same resolution.

    Args:
        images: List of PIL Image instances to check

    Returns:
        True if all images have matching resolutions, False otherwise

    Raises:
        ValueError: If images list is empty
        TypeError: If any item in the list is not a PIL Image

    Example:
        >>> img1 = Image.new('RGB', (1024, 1024))
        >>> img2 = Image.new('L', (1024, 1024))
        >>> img3 = Image.new('RGB', (512, 512))
        >>> check_resolution_match([img1, img2])
        True
        >>> check_resolution_match([img1, img3])
        False
    """
    if not images:
        raise ValueError("Images list cannot be empty")

    # Validate that all items are PIL Images
    for i, img in enumerate(images):
        if not isinstance(img, Image.Image):
            raise TypeError(
                f"Item at index {i} is not a PIL Image instance, got {type(img).__name__}"
            )

    # Get the first image's resolution as reference
    reference_size = images[0].size

    # Check if all images match the reference resolution
    for img in images[1:]:
        if img.size != reference_size:
            return False

    return True


def get_max_resolution(images: List[Image.Image]) -> Tuple[int, int]:
    """
    Get the maximum resolution from a list of images.

    Finds the largest width and height independently, returning the
    maximum dimensions that encompass all images.

    Args:
        images: List of PIL Image instances

    Returns:
        Tuple of (max_width, max_height)

    Raises:
        ValueError: If images list is empty
        TypeError: If any item in the list is not a PIL Image

    Example:
        >>> img1 = Image.new('RGB', (1024, 512))
        >>> img2 = Image.new('RGB', (512, 1024))
        >>> img3 = Image.new('RGB', (2048, 768))
        >>> get_max_resolution([img1, img2, img3])
        (2048, 1024)
    """
    if not images:
        raise ValueError("Images list cannot be empty")

    # Validate that all items are PIL Images
    for i, img in enumerate(images):
        if not isinstance(img, Image.Image):
            raise TypeError(
                f"Item at index {i} is not a PIL Image instance, got {type(img).__name__}"
            )

    # Find maximum width and height
    max_width = max(img.size[0] for img in images)
    max_height = max(img.size[1] for img in images)

    return (max_width, max_height)


def validate_channel_data(
    data: np.ndarray,
    expected_shape: Optional[Tuple[int, int]] = None,
    allow_empty: bool = False
) -> None:
    """
    Validate that channel data is suitable for packing operations.

    Checks that the data is a valid 2D NumPy array with appropriate
    dtype and dimensions.

    Args:
        data: NumPy array containing channel data
        expected_shape: Optional (height, width) tuple to validate against
        allow_empty: If True, allows zero-sized arrays

    Raises:
        TypeError: If data is not a NumPy array
        InvalidChannelDataError: If data has invalid properties

    Example:
        >>> data = np.zeros((1024, 1024), dtype=np.uint8)
        >>> validate_channel_data(data)  # No exception
        >>> validate_channel_data(data, expected_shape=(1024, 1024))  # No exception
        >>> validate_channel_data(data, expected_shape=(512, 512))  # Raises error
        Traceback (most recent call last):
        ...
        InvalidChannelDataError: ...
    """
    # Check if data is a NumPy array
    if not isinstance(data, np.ndarray):
        raise TypeError(
            f"Channel data must be a NumPy array, got {type(data).__name__}"
        )

    # Check dimensions
    if data.ndim != 2:
        raise InvalidChannelDataError(
            f"Channel data must be 2D array, got {data.ndim}D array with shape {data.shape}"
        )

    # Check if empty
    if data.size == 0 and not allow_empty:
        raise InvalidChannelDataError(
            "Channel data cannot be empty (zero-sized array)"
        )

    # Check expected shape if provided
    if expected_shape is not None:
        if data.shape != expected_shape:
            raise InvalidChannelDataError(
                f"Channel data shape {data.shape} does not match expected shape {expected_shape}"
            )

    # Check dtype - should be numeric
    if not np.issubdtype(data.dtype, np.number):
        raise InvalidChannelDataError(
            f"Channel data must have numeric dtype, got {data.dtype}"
        )


def validate_images_for_packing(
    images: List[Optional[Image.Image]],
    require_all: bool = False
) -> Tuple[int, int]:
    """
    Validate a list of images for channel packing operations.

    Checks that images are valid PIL Images and determines the target
    resolution for packing. None values are allowed (representing missing
    channels that will use default values).

    Args:
        images: List of PIL Images or None values
        require_all: If True, raises error if any image is None

    Returns:
        Tuple of (width, height) representing the target resolution for packing

    Raises:
        ValueError: If images list is empty or all images are None
        TypeError: If any non-None item is not a PIL Image
        ResolutionMismatchError: If images have mismatched resolutions

    Example:
        >>> img1 = Image.new('L', (1024, 1024))
        >>> img2 = Image.new('L', (1024, 1024))
        >>> validate_images_for_packing([img1, img2, None])
        (1024, 1024)
    """
    if not images:
        raise ValueError("Images list cannot be empty")

    # Filter out None values
    valid_images = [img for img in images if img is not None]

    # Check if we have at least one valid image
    if not valid_images:
        raise ValueError("At least one image must be provided (not None)")

    # Check if all images required
    if require_all and len(valid_images) != len(images):
        none_count = len(images) - len(valid_images)
        raise ValueError(
            f"All images are required, but {none_count} image(s) are None"
        )

    # Validate that all non-None items are PIL Images
    for i, img in enumerate(images):
        if img is not None and not isinstance(img, Image.Image):
            raise TypeError(
                f"Item at index {i} is not a PIL Image instance, got {type(img).__name__}"
            )

    # Check resolution match
    if not check_resolution_match(valid_images):
        # Get all resolutions for error message
        resolutions = [img.size for img in valid_images]
        raise ResolutionMismatchError(
            f"All images must have the same resolution. Found resolutions: {resolutions}"
        )

    # Return the common resolution
    return valid_images[0].size


def validate_arrays_for_packing(
    arrays: List[Optional[np.ndarray]],
    require_all: bool = False
) -> Tuple[int, int]:
    """
    Validate a list of NumPy arrays for channel packing operations.

    Checks that arrays are valid 2D NumPy arrays and have matching shapes.
    None values are allowed (representing missing channels).

    Args:
        arrays: List of NumPy arrays or None values
        require_all: If True, raises error if any array is None

    Returns:
        Tuple of (height, width) representing the common array shape

    Raises:
        ValueError: If arrays list is empty or all arrays are None
        TypeError: If any non-None item is not a NumPy array
        InvalidChannelDataError: If arrays have mismatched shapes or invalid properties

    Example:
        >>> arr1 = np.zeros((1024, 1024), dtype=np.uint8)
        >>> arr2 = np.zeros((1024, 1024), dtype=np.uint8)
        >>> validate_arrays_for_packing([arr1, arr2, None])
        (1024, 1024)
    """
    if not arrays:
        raise ValueError("Arrays list cannot be empty")

    # Filter out None values
    valid_arrays = [arr for arr in arrays if arr is not None]

    # Check if we have at least one valid array
    if not valid_arrays:
        raise ValueError("At least one array must be provided (not None)")

    # Check if all arrays required
    if require_all and len(valid_arrays) != len(arrays):
        none_count = len(arrays) - len(valid_arrays)
        raise ValueError(
            f"All arrays are required, but {none_count} array(s) are None"
        )

    # Validate each non-None array
    for i, arr in enumerate(arrays):
        if arr is not None:
            try:
                validate_channel_data(arr)
            except (TypeError, InvalidChannelDataError) as e:
                raise InvalidChannelDataError(
                    f"Array at index {i} is invalid: {e}"
                ) from e

    # Check shape match
    reference_shape = valid_arrays[0].shape
    for i, arr in enumerate(valid_arrays[1:], start=1):
        if arr.shape != reference_shape:
            shapes = [arr.shape for arr in valid_arrays]
            raise InvalidChannelDataError(
                f"All arrays must have the same shape. Found shapes: {shapes}"
            )

    # Return the common shape
    return reference_shape
