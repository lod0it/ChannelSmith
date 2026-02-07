"""
Image utility functions for loading, saving, and converting images.

This module provides helper functions for working with images using PIL/Pillow
and NumPy, including loading/saving images from disk and converting between
PIL Image and NumPy array formats.
"""

from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image


class ImageLoadError(Exception):
    """Raised when an image file cannot be loaded."""
    pass


class ImageSaveError(Exception):
    """Raised when an image file cannot be saved."""
    pass


class ImageConversionError(Exception):
    """Raised when image conversion fails."""
    pass


def load_image(path: str) -> Image.Image:
    """
    Load an image from a file path.

    Supports common image formats including PNG, JPEG, TGA, TIFF, BMP, etc.

    Args:
        path: Path to the image file

    Returns:
        PIL Image instance

    Raises:
        FileNotFoundError: If the image file does not exist
        ImageLoadError: If the file exists but cannot be loaded as an image

    Example:
        >>> image = load_image('textures/roughness.png')
        >>> image.size
        (1024, 1024)
    """
    image_path = Path(path)

    # Check if file exists
    if not image_path.exists():
        raise FileNotFoundError(
            f"Image file not found: {path}"
        )

    # Attempt to load the image
    try:
        image = Image.open(image_path)
        # Force load the image data to catch corrupted files early
        image.load()
        return image
    except (IOError, OSError) as e:
        raise ImageLoadError(
            f"Failed to load image from '{path}': {e}"
        ) from e
    except Exception as e:
        raise ImageLoadError(
            f"Unexpected error loading image from '{path}': {e}"
        ) from e


def save_image(
    image: Image.Image,
    path: str,
    format: Optional[str] = None
) -> None:
    """
    Save a PIL Image to a file.

    Args:
        image: PIL Image instance to save
        path: Path where the image should be saved
        format: Optional format string (e.g., 'PNG', 'JPEG', 'TGA').
                If not provided, format is inferred from file extension.

    Raises:
        ImageSaveError: If the image cannot be saved
        TypeError: If image is not a PIL Image instance

    Example:
        >>> image = Image.new('RGB', (512, 512))
        >>> save_image(image, 'output/packed.png')
        >>> save_image(image, 'output/packed.tga', format='TGA')
    """
    if not isinstance(image, Image.Image):
        raise TypeError(
            f"Expected PIL Image instance, got {type(image).__name__}"
        )

    output_path = Path(path)

    # Create parent directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine format
    if format is None:
        # Infer from file extension
        format = output_path.suffix.upper().lstrip('.')
        if not format:
            raise ImageSaveError(
                f"Cannot determine image format from path '{path}'. "
                f"Please provide a file extension or specify format parameter."
            )

    # Normalize format aliases (JPG -> JPEG)
    format_aliases = {
        'JPG': 'JPEG',
        'TIF': 'TIFF',
    }
    format = format_aliases.get(format, format)

    # Attempt to save the image
    try:
        image.save(output_path, format=format)
    except (IOError, OSError) as e:
        raise ImageSaveError(
            f"Failed to save image to '{path}': {e}"
        ) from e
    except (ValueError, KeyError) as e:
        raise ImageSaveError(
            f"Invalid format '{format}' for saving image: {e}"
        ) from e
    except Exception as e:
        raise ImageSaveError(
            f"Unexpected error saving image to '{path}': {e}"
        ) from e


def to_grayscale(image: Image.Image) -> np.ndarray:
    """
    Convert a PIL Image to a grayscale NumPy array.

    If the image is already grayscale, it is converted directly.
    If the image is RGB/RGBA, it is converted to grayscale first.

    Args:
        image: PIL Image instance (can be grayscale, RGB, or RGBA)

    Returns:
        2D NumPy array of uint8 values (0-255) representing grayscale intensities

    Raises:
        TypeError: If image is not a PIL Image instance
        ImageConversionError: If conversion fails

    Example:
        >>> image = Image.open('texture.png')
        >>> gray_array = to_grayscale(image)
        >>> gray_array.shape
        (1024, 1024)
        >>> gray_array.dtype
        dtype('uint8')
    """
    if not isinstance(image, Image.Image):
        raise TypeError(
            f"Expected PIL Image instance, got {type(image).__name__}"
        )

    try:
        # Convert to grayscale if not already
        if image.mode != 'L':
            image = image.convert('L')

        # Convert to NumPy array
        array = np.array(image, dtype=np.uint8)

        # Ensure it's 2D
        if array.ndim != 2:
            raise ImageConversionError(
                f"Expected 2D array after grayscale conversion, got shape {array.shape}"
            )

        return array

    except ImageConversionError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        raise ImageConversionError(
            f"Failed to convert image to grayscale: {e}"
        ) from e


def from_grayscale(array: np.ndarray) -> Image.Image:
    """
    Convert a grayscale NumPy array to a PIL Image.

    Args:
        array: 2D NumPy array of grayscale values.
               Should be uint8 (0-255) or will be converted.

    Returns:
        PIL Image in 'L' (grayscale) mode

    Raises:
        TypeError: If array is not a NumPy array
        ImageConversionError: If array has invalid shape or cannot be converted

    Example:
        >>> array = np.zeros((512, 512), dtype=np.uint8)
        >>> image = from_grayscale(array)
        >>> image.mode
        'L'
        >>> image.size
        (512, 512)
    """
    if not isinstance(array, np.ndarray):
        raise TypeError(
            f"Expected NumPy array, got {type(array).__name__}"
        )

    try:
        # Validate array dimensions
        if array.ndim != 2:
            raise ImageConversionError(
                f"Expected 2D array, got {array.ndim}D array with shape {array.shape}"
            )

        # Convert to uint8 if necessary
        if array.dtype != np.uint8:
            # Clip and convert
            array = np.clip(array, 0, 255).astype(np.uint8)

        # Create PIL Image
        image = Image.fromarray(array, mode='L')
        return image

    except ImageConversionError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        raise ImageConversionError(
            f"Failed to convert array to grayscale image: {e}"
        ) from e


def normalize_to_float(array: np.ndarray) -> np.ndarray:
    """
    Normalize a uint8 array (0-255) to float array (0.0-1.0).

    Args:
        array: NumPy array with uint8 values (0-255)

    Returns:
        NumPy array with float32 values (0.0-1.0)

    Example:
        >>> array = np.array([[0, 128, 255]], dtype=np.uint8)
        >>> normalized = normalize_to_float(array)
        >>> normalized
        array([[0.0, 0.502, 1.0]], dtype=float32)
    """
    return array.astype(np.float32) / 255.0


def denormalize_to_uint8(array: np.ndarray) -> np.ndarray:
    """
    Denormalize a float array (0.0-1.0) to uint8 array (0-255).

    Args:
        array: NumPy array with float values (0.0-1.0)

    Returns:
        NumPy array with uint8 values (0-255)

    Example:
        >>> array = np.array([[0.0, 0.5, 1.0]], dtype=np.float32)
        >>> denormalized = denormalize_to_uint8(array)
        >>> denormalized
        array([[0, 128, 255]], dtype=uint8)
    """
    return np.clip(array * 255.0, 0, 255).astype(np.uint8)


def get_image_info(path: str) -> dict:
    """
    Get information about an image file without fully loading it.

    Args:
        path: Path to the image file

    Returns:
        Dictionary containing image information:
        - 'size': (width, height) tuple
        - 'mode': Image mode (e.g., 'RGB', 'RGBA', 'L')
        - 'format': Image format (e.g., 'PNG', 'JPEG')

    Raises:
        FileNotFoundError: If the image file does not exist
        ImageLoadError: If the file cannot be opened as an image

    Example:
        >>> info = get_image_info('texture.png')
        >>> info['size']
        (1024, 1024)
        >>> info['mode']
        'RGB'
    """
    image_path = Path(path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image file not found: {path}"
        )

    try:
        with Image.open(image_path) as img:
            return {
                'size': img.size,
                'mode': img.mode,
                'format': img.format
            }
    except (IOError, OSError) as e:
        raise ImageLoadError(
            f"Failed to get image info from '{path}': {e}"
        ) from e
