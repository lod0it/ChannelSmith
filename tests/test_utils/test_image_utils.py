"""
Tests for the image_utils module.

This module contains unit tests for image loading, saving, and conversion
functions.
"""

import pytest
import numpy as np
from pathlib import Path
from PIL import Image
from channelsmith.utils.image_utils import (
    load_image,
    save_image,
    to_grayscale,
    from_grayscale,
    normalize_to_float,
    denormalize_to_uint8,
    get_image_info,
    ImageLoadError,
    ImageSaveError,
    ImageConversionError,
)


@pytest.fixture
def test_image_rgb(tmp_path):
    """Create a test RGB image."""
    img = Image.new('RGB', (256, 256), color=(128, 64, 32))
    path = tmp_path / "test_rgb.png"
    img.save(path)
    return path


@pytest.fixture
def test_image_rgba(tmp_path):
    """Create a test RGBA image."""
    img = Image.new('RGBA', (256, 256), color=(128, 64, 32, 255))
    path = tmp_path / "test_rgba.png"
    img.save(path)
    return path


@pytest.fixture
def test_image_grayscale(tmp_path):
    """Create a test grayscale image."""
    img = Image.new('L', (256, 256), color=128)
    path = tmp_path / "test_gray.png"
    img.save(path)
    return path


@pytest.fixture
def test_image_jpeg(tmp_path):
    """Create a test JPEG image."""
    img = Image.new('RGB', (256, 256), color=(100, 150, 200))
    path = tmp_path / "test.jpg"
    img.save(path, format='JPEG')
    return path


@pytest.fixture
def test_image_tga(tmp_path):
    """Create a test TGA image."""
    img = Image.new('RGB', (256, 256), color=(100, 150, 200))
    path = tmp_path / "test.tga"
    img.save(path, format='TGA')
    return path


class TestLoadImage:
    """Test loading images from disk."""

    def test_load_png_image(self, test_image_rgb):
        """Test loading a PNG image."""
        image = load_image(str(test_image_rgb))

        assert isinstance(image, Image.Image)
        assert image.size == (256, 256)
        assert image.mode == 'RGB'

    def test_load_jpeg_image(self, test_image_jpeg):
        """Test loading a JPEG image."""
        image = load_image(str(test_image_jpeg))

        assert isinstance(image, Image.Image)
        assert image.size == (256, 256)
        assert image.mode == 'RGB'

    def test_load_tga_image(self, test_image_tga):
        """Test loading a TGA image."""
        image = load_image(str(test_image_tga))

        assert isinstance(image, Image.Image)
        assert image.size == (256, 256)

    def test_load_rgba_image(self, test_image_rgba):
        """Test loading an RGBA image."""
        image = load_image(str(test_image_rgba))

        assert isinstance(image, Image.Image)
        assert image.mode == 'RGBA'

    def test_load_grayscale_image(self, test_image_grayscale):
        """Test loading a grayscale image."""
        image = load_image(str(test_image_grayscale))

        assert isinstance(image, Image.Image)
        assert image.mode == 'L'

    def test_load_nonexistent_file_raises_error(self):
        """Test that loading a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Image file not found"):
            load_image('nonexistent_image.png')

    def test_load_corrupted_image_raises_error(self, tmp_path):
        """Test that loading a corrupted file raises ImageLoadError."""
        corrupted = tmp_path / "corrupted.png"
        corrupted.write_text("This is not an image file", encoding='utf-8')

        with pytest.raises(ImageLoadError, match="Failed to load image"):
            load_image(str(corrupted))

    def test_load_invalid_format_raises_error(self, tmp_path):
        """Test that loading an invalid format raises ImageLoadError."""
        invalid = tmp_path / "invalid.txt"
        invalid.write_text("Plain text file", encoding='utf-8')

        with pytest.raises(ImageLoadError):
            load_image(str(invalid))


class TestSaveImage:
    """Test saving images to disk."""

    def test_save_image_png(self, tmp_path):
        """Test saving an image as PNG."""
        image = Image.new('RGB', (128, 128), color=(255, 0, 0))
        output_path = tmp_path / "output.png"

        save_image(image, str(output_path))

        assert output_path.exists()
        loaded = Image.open(output_path)
        assert loaded.size == (128, 128)
        assert loaded.mode == 'RGB'

    def test_save_image_jpeg(self, tmp_path):
        """Test saving an image as JPEG."""
        image = Image.new('RGB', (128, 128), color=(0, 255, 0))
        output_path = tmp_path / "output.jpg"

        save_image(image, str(output_path))

        assert output_path.exists()
        loaded = Image.open(output_path)
        assert loaded.size == (128, 128)

    def test_save_image_tga(self, tmp_path):
        """Test saving an image as TGA."""
        image = Image.new('RGB', (128, 128), color=(0, 0, 255))
        output_path = tmp_path / "output.tga"

        save_image(image, str(output_path))

        assert output_path.exists()
        loaded = Image.open(output_path)
        assert loaded.size == (128, 128)

    def test_save_image_with_explicit_format(self, tmp_path):
        """Test saving with explicitly specified format."""
        image = Image.new('RGB', (128, 128))
        output_path = tmp_path / "output.custom"

        save_image(image, str(output_path), img_format='PNG')

        assert output_path.exists()

    def test_save_image_creates_parent_directory(self, tmp_path):
        """Test that save_image creates parent directories."""
        image = Image.new('RGB', (128, 128))
        nested_path = tmp_path / "subdir" / "nested" / "output.png"

        save_image(image, str(nested_path))

        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_save_non_image_raises_error(self, tmp_path):
        """Test that saving a non-Image raises TypeError."""
        output_path = tmp_path / "output.png"

        with pytest.raises(TypeError, match="Expected PIL Image instance"):
            save_image("not an image", str(output_path))

    def test_save_without_extension_and_format_raises_error(self, tmp_path):
        """Test that saving without extension or format raises error."""
        image = Image.new('RGB', (128, 128))
        output_path = tmp_path / "output"

        with pytest.raises(ImageSaveError, match="Cannot determine image format"):
            save_image(image, str(output_path))

    def test_save_with_invalid_format_raises_error(self, tmp_path):
        """Test that saving with invalid format raises error."""
        image = Image.new('RGB', (128, 128))
        output_path = tmp_path / "output.png"

        with pytest.raises(ImageSaveError, match="Invalid format"):
            save_image(image, str(output_path), img_format='INVALID_FORMAT')


class TestToGrayscale:
    """Test converting images to grayscale arrays."""

    def test_to_grayscale_from_rgb(self, test_image_rgb):
        """Test converting RGB image to grayscale array."""
        image = load_image(str(test_image_rgb))
        array = to_grayscale(image)

        assert isinstance(array, np.ndarray)
        assert array.ndim == 2
        assert array.dtype == np.uint8
        assert array.shape == (256, 256)

    def test_to_grayscale_from_rgba(self, test_image_rgba):
        """Test converting RGBA image to grayscale array."""
        image = load_image(str(test_image_rgba))
        array = to_grayscale(image)

        assert isinstance(array, np.ndarray)
        assert array.ndim == 2
        assert array.dtype == np.uint8
        assert array.shape == (256, 256)

    def test_to_grayscale_from_grayscale(self, test_image_grayscale):
        """Test converting already-grayscale image to array."""
        image = load_image(str(test_image_grayscale))
        array = to_grayscale(image)

        assert isinstance(array, np.ndarray)
        assert array.ndim == 2
        assert array.dtype == np.uint8
        assert array.shape == (256, 256)

    def test_to_grayscale_values_correct(self):
        """Test that grayscale conversion produces correct values."""
        # Create image with known grayscale value
        image = Image.new('L', (10, 10), color=128)
        array = to_grayscale(image)

        # All values should be 128
        assert np.all(array == 128)

    def test_to_grayscale_non_image_raises_error(self):
        """Test that non-Image input raises TypeError."""
        with pytest.raises(TypeError, match="Expected PIL Image instance"):
            to_grayscale("not an image")


class TestFromGrayscale:
    """Test converting grayscale arrays to images."""

    def test_from_grayscale_uint8_array(self):
        """Test converting uint8 array to grayscale image."""
        array = np.full((128, 128), 100, dtype=np.uint8)
        image = from_grayscale(array)

        assert isinstance(image, Image.Image)
        assert image.mode == 'L'
        assert image.size == (128, 128)

    def test_from_grayscale_values_preserved(self):
        """Test that array values are preserved in image."""
        array = np.array([[0, 128, 255]], dtype=np.uint8)
        image = from_grayscale(array)

        result_array = np.array(image)
        assert np.array_equal(result_array, array)

    def test_from_grayscale_float_array_converts(self):
        """Test converting float array to grayscale image."""
        array = np.full((64, 64), 0.5, dtype=np.float32) * 255
        image = from_grayscale(array)

        assert isinstance(image, Image.Image)
        assert image.mode == 'L'

    def test_from_grayscale_non_uint8_clips(self):
        """Test that values outside uint8 range are clipped."""
        array = np.array([[0, 128, 300]], dtype=np.int16)
        image = from_grayscale(array)

        result_array = np.array(image)
        assert result_array[0, 2] == 255  # 300 clipped to 255

    def test_from_grayscale_non_array_raises_error(self):
        """Test that non-array input raises TypeError."""
        with pytest.raises(TypeError, match="Expected NumPy array"):
            from_grayscale("not an array")

    def test_from_grayscale_wrong_dimensions_raises_error(self):
        """Test that non-2D array raises ImageConversionError."""
        array_1d = np.array([1, 2, 3], dtype=np.uint8)

        with pytest.raises(ImageConversionError, match="Expected 2D array"):
            from_grayscale(array_1d)

        array_3d = np.zeros((10, 10, 3), dtype=np.uint8)

        with pytest.raises(ImageConversionError, match="Expected 2D array"):
            from_grayscale(array_3d)


class TestRoundTrip:
    """Test round-trip conversions."""

    def test_round_trip_grayscale_conversion(self):
        """Test that to_grayscale -> from_grayscale preserves data."""
        original_array = np.random.randint(0, 256, (128, 128), dtype=np.uint8)
        image = from_grayscale(original_array)
        result_array = to_grayscale(image)

        assert np.array_equal(result_array, original_array)

    def test_round_trip_save_load(self, tmp_path):
        """Test that save -> load preserves image."""
        original = Image.new('RGB', (100, 100), color=(50, 100, 150))
        path = tmp_path / "roundtrip.png"

        save_image(original, str(path))
        loaded = load_image(str(path))

        assert loaded.size == original.size
        assert loaded.mode == original.mode


class TestNormalizationFunctions:
    """Test normalization and denormalization functions."""

    def test_normalize_to_float(self):
        """Test normalizing uint8 array to float."""
        array = np.array([[0, 128, 255]], dtype=np.uint8)
        normalized = normalize_to_float(array)

        assert normalized.dtype == np.float32
        assert normalized[0, 0] == pytest.approx(0.0, abs=0.01)
        assert normalized[0, 1] == pytest.approx(0.502, abs=0.01)
        assert normalized[0, 2] == pytest.approx(1.0, abs=0.01)

    def test_denormalize_to_uint8(self):
        """Test denormalizing float array to uint8."""
        array = np.array([[0.0, 0.5, 1.0]], dtype=np.float32)
        denormalized = denormalize_to_uint8(array)

        assert denormalized.dtype == np.uint8
        assert denormalized[0, 0] == 0
        # 0.5 * 255 = 127.5, which can round to 127 or 128
        assert denormalized[0, 1] in [127, 128]
        assert denormalized[0, 2] == 255

    def test_denormalize_clips_values(self):
        """Test that denormalization clips out-of-range values."""
        array = np.array([[-0.5, 0.5, 1.5]], dtype=np.float32)
        denormalized = denormalize_to_uint8(array)

        assert denormalized[0, 0] == 0  # -0.5 clipped to 0
        assert denormalized[0, 2] == 255  # 1.5 clipped to 1.0 -> 255

    def test_normalize_denormalize_round_trip(self):
        """Test that normalize -> denormalize preserves values."""
        original = np.array([[0, 64, 128, 192, 255]], dtype=np.uint8)
        normalized = normalize_to_float(original)
        result = denormalize_to_uint8(normalized)

        # Allow small differences due to floating point precision
        assert np.allclose(result, original, atol=1)


class TestGetImageInfo:
    """Test getting image information."""

    def test_get_image_info_png(self, test_image_rgb):
        """Test getting info from PNG image."""
        info = get_image_info(str(test_image_rgb))

        assert info['size'] == (256, 256)
        assert info['mode'] == 'RGB'
        assert info['format'] == 'PNG'

    def test_get_image_info_jpeg(self, test_image_jpeg):
        """Test getting info from JPEG image."""
        info = get_image_info(str(test_image_jpeg))

        assert info['size'] == (256, 256)
        assert info['mode'] == 'RGB'
        assert info['format'] == 'JPEG'

    def test_get_image_info_nonexistent_file_raises_error(self):
        """Test that non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_image_info('nonexistent.png')

    def test_get_image_info_invalid_file_raises_error(self, tmp_path):
        """Test that invalid image file raises ImageLoadError."""
        invalid = tmp_path / "invalid.png"
        invalid.write_text("Not an image", encoding='utf-8')

        with pytest.raises(ImageLoadError):
            get_image_info(str(invalid))
