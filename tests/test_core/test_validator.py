"""
Tests for the validator module.

This module contains unit tests for validation functions used in
texture channel packing operations.
"""

import pytest
import numpy as np
from PIL import Image
from channelsmith.core.validator import (
    check_resolution_match,
    get_max_resolution,
    validate_channel_data,
    validate_images_for_packing,
    validate_arrays_for_packing,
    ResolutionMismatchError,
    InvalidChannelDataError,
)


class TestCheckResolutionMatch:
    """Test checking if image resolutions match."""

    def test_matching_resolutions_returns_true(self):
        """Test that matching resolutions return True."""
        img1 = Image.new('RGB', (1024, 1024))
        img2 = Image.new('L', (1024, 1024))
        img3 = Image.new('RGBA', (1024, 1024))

        assert check_resolution_match([img1, img2, img3]) is True

    def test_mismatched_resolutions_returns_false(self):
        """Test that mismatched resolutions return False."""
        img1 = Image.new('RGB', (1024, 1024))
        img2 = Image.new('RGB', (512, 512))

        assert check_resolution_match([img1, img2]) is False

    def test_mismatched_width_only_returns_false(self):
        """Test that mismatched width returns False."""
        img1 = Image.new('RGB', (1024, 512))
        img2 = Image.new('RGB', (512, 512))

        assert check_resolution_match([img1, img2]) is False

    def test_mismatched_height_only_returns_false(self):
        """Test that mismatched height returns False."""
        img1 = Image.new('RGB', (1024, 1024))
        img2 = Image.new('RGB', (1024, 512))

        assert check_resolution_match([img1, img2]) is False

    def test_single_image_returns_true(self):
        """Test that a single image returns True."""
        img = Image.new('RGB', (1024, 1024))

        assert check_resolution_match([img]) is True

    def test_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="Images list cannot be empty"):
            check_resolution_match([])

    def test_non_image_raises_error(self):
        """Test that non-Image item raises TypeError."""
        img = Image.new('RGB', (1024, 1024))

        with pytest.raises(TypeError, match="not a PIL Image instance"):
            check_resolution_match([img, "not an image"])


class TestGetMaxResolution:
    """Test getting maximum resolution from images."""

    def test_get_max_from_matching_resolutions(self):
        """Test getting max resolution when all images match."""
        img1 = Image.new('RGB', (1024, 1024))
        img2 = Image.new('L', (1024, 1024))

        max_res = get_max_resolution([img1, img2])

        assert max_res == (1024, 1024)

    def test_get_max_from_different_resolutions(self):
        """Test getting max resolution from different sizes."""
        img1 = Image.new('RGB', (1024, 512))
        img2 = Image.new('RGB', (512, 1024))
        img3 = Image.new('RGB', (2048, 768))

        max_res = get_max_resolution([img1, img2, img3])

        assert max_res == (2048, 1024)

    def test_get_max_from_single_image(self):
        """Test getting max resolution from single image."""
        img = Image.new('RGB', (1024, 1024))

        max_res = get_max_resolution([img])

        assert max_res == (1024, 1024)

    def test_get_max_with_varying_aspect_ratios(self):
        """Test getting max with different aspect ratios."""
        img1 = Image.new('RGB', (1920, 1080))  # 16:9
        img2 = Image.new('RGB', (1024, 1024))  # 1:1
        img3 = Image.new('RGB', (800, 600))    # 4:3

        max_res = get_max_resolution([img1, img2, img3])

        assert max_res == (1920, 1080)

    def test_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="Images list cannot be empty"):
            get_max_resolution([])

    def test_non_image_raises_error(self):
        """Test that non-Image item raises TypeError."""
        img = Image.new('RGB', (1024, 1024))

        with pytest.raises(TypeError, match="not a PIL Image instance"):
            get_max_resolution([img, None])


class TestValidateChannelData:
    """Test validating channel data arrays."""

    def test_valid_uint8_array(self):
        """Test that valid uint8 array passes validation."""
        data = np.zeros((1024, 1024), dtype=np.uint8)

        # Should not raise any exception
        validate_channel_data(data)

    def test_valid_float_array(self):
        """Test that valid float array passes validation."""
        data = np.zeros((512, 512), dtype=np.float32)

        # Should not raise any exception
        validate_channel_data(data)

    def test_valid_with_expected_shape(self):
        """Test validation with matching expected shape."""
        data = np.zeros((1024, 1024), dtype=np.uint8)

        # Should not raise any exception
        validate_channel_data(data, expected_shape=(1024, 1024))

    def test_mismatched_expected_shape_raises_error(self):
        """Test that mismatched shape raises error."""
        data = np.zeros((1024, 1024), dtype=np.uint8)

        with pytest.raises(InvalidChannelDataError, match="does not match expected shape"):
            validate_channel_data(data, expected_shape=(512, 512))

    def test_non_array_raises_error(self):
        """Test that non-array input raises TypeError."""
        with pytest.raises(TypeError, match="must be a NumPy array"):
            validate_channel_data("not an array")

    def test_1d_array_raises_error(self):
        """Test that 1D array raises error."""
        data = np.zeros(1024, dtype=np.uint8)

        with pytest.raises(InvalidChannelDataError, match="must be 2D array"):
            validate_channel_data(data)

    def test_3d_array_raises_error(self):
        """Test that 3D array raises error."""
        data = np.zeros((1024, 1024, 3), dtype=np.uint8)

        with pytest.raises(InvalidChannelDataError, match="must be 2D array"):
            validate_channel_data(data)

    def test_empty_array_raises_error(self):
        """Test that empty array raises error by default."""
        data = np.zeros((0, 0), dtype=np.uint8)

        with pytest.raises(InvalidChannelDataError, match="cannot be empty"):
            validate_channel_data(data)

    def test_empty_array_allowed_with_flag(self):
        """Test that empty array passes when allow_empty=True."""
        data = np.zeros((0, 0), dtype=np.uint8)

        # Should not raise any exception
        validate_channel_data(data, allow_empty=True)

    def test_non_numeric_dtype_raises_error(self):
        """Test that non-numeric dtype raises error."""
        data = np.array([['a', 'b'], ['c', 'd']])

        with pytest.raises(InvalidChannelDataError, match="must have numeric dtype"):
            validate_channel_data(data)


class TestValidateImagesForPacking:
    """Test validating images for packing operations."""

    def test_valid_images_returns_resolution(self):
        """Test that valid images return common resolution."""
        img1 = Image.new('L', (1024, 1024))
        img2 = Image.new('L', (1024, 1024))

        resolution = validate_images_for_packing([img1, img2])

        assert resolution == (1024, 1024)

    def test_with_none_values_returns_resolution(self):
        """Test that images with None values return valid resolution."""
        img1 = Image.new('L', (1024, 1024))
        img2 = Image.new('L', (1024, 1024))

        resolution = validate_images_for_packing([img1, None, img2, None])

        assert resolution == (1024, 1024)

    def test_single_image_with_nones_returns_resolution(self):
        """Test single image with None values."""
        img = Image.new('L', (1024, 1024))

        resolution = validate_images_for_packing([None, img, None])

        assert resolution == (1024, 1024)

    def test_mismatched_resolutions_raises_error(self):
        """Test that mismatched resolutions raise error."""
        img1 = Image.new('L', (1024, 1024))
        img2 = Image.new('L', (512, 512))

        with pytest.raises(ResolutionMismatchError, match="must have the same resolution"):
            validate_images_for_packing([img1, img2])

    def test_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="Images list cannot be empty"):
            validate_images_for_packing([])

    def test_all_none_raises_error(self):
        """Test that all None values raise error."""
        with pytest.raises(ValueError, match="At least one image must be provided"):
            validate_images_for_packing([None, None, None])

    def test_require_all_with_none_raises_error(self):
        """Test that require_all=True raises error when None present."""
        img = Image.new('L', (1024, 1024))

        with pytest.raises(ValueError, match="All images are required"):
            validate_images_for_packing([img, None], require_all=True)

    def test_require_all_without_none_succeeds(self):
        """Test that require_all=True succeeds when no None values."""
        img1 = Image.new('L', (1024, 1024))
        img2 = Image.new('L', (1024, 1024))

        resolution = validate_images_for_packing([img1, img2], require_all=True)

        assert resolution == (1024, 1024)

    def test_non_image_raises_error(self):
        """Test that non-Image item raises TypeError."""
        img = Image.new('L', (1024, 1024))

        with pytest.raises(TypeError, match="not a PIL Image instance"):
            validate_images_for_packing([img, "not an image"])


class TestValidateArraysForPacking:
    """Test validating arrays for packing operations."""

    def test_valid_arrays_returns_shape(self):
        """Test that valid arrays return common shape."""
        arr1 = np.zeros((1024, 1024), dtype=np.uint8)
        arr2 = np.ones((1024, 1024), dtype=np.uint8)

        shape = validate_arrays_for_packing([arr1, arr2])

        assert shape == (1024, 1024)

    def test_with_none_values_returns_shape(self):
        """Test that arrays with None values return valid shape."""
        arr1 = np.zeros((1024, 1024), dtype=np.uint8)
        arr2 = np.ones((1024, 1024), dtype=np.uint8)

        shape = validate_arrays_for_packing([arr1, None, arr2, None])

        assert shape == (1024, 1024)

    def test_single_array_with_nones_returns_shape(self):
        """Test single array with None values."""
        arr = np.zeros((1024, 1024), dtype=np.uint8)

        shape = validate_arrays_for_packing([None, arr, None])

        assert shape == (1024, 1024)

    def test_mismatched_shapes_raises_error(self):
        """Test that mismatched shapes raise error."""
        arr1 = np.zeros((1024, 1024), dtype=np.uint8)
        arr2 = np.zeros((512, 512), dtype=np.uint8)

        with pytest.raises(InvalidChannelDataError, match="must have the same shape"):
            validate_arrays_for_packing([arr1, arr2])

    def test_invalid_array_raises_error(self):
        """Test that invalid array raises error."""
        arr1 = np.zeros((1024, 1024), dtype=np.uint8)
        arr2 = np.zeros((1024, 1024, 3), dtype=np.uint8)  # 3D array

        with pytest.raises(InvalidChannelDataError, match="Array at index 1 is invalid"):
            validate_arrays_for_packing([arr1, arr2])

    def test_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="Arrays list cannot be empty"):
            validate_arrays_for_packing([])

    def test_all_none_raises_error(self):
        """Test that all None values raise error."""
        with pytest.raises(ValueError, match="At least one array must be provided"):
            validate_arrays_for_packing([None, None, None])

    def test_require_all_with_none_raises_error(self):
        """Test that require_all=True raises error when None present."""
        arr = np.zeros((1024, 1024), dtype=np.uint8)

        with pytest.raises(ValueError, match="All arrays are required"):
            validate_arrays_for_packing([arr, None], require_all=True)

    def test_require_all_without_none_succeeds(self):
        """Test that require_all=True succeeds when no None values."""
        arr1 = np.zeros((1024, 1024), dtype=np.uint8)
        arr2 = np.ones((1024, 1024), dtype=np.uint8)

        shape = validate_arrays_for_packing([arr1, arr2], require_all=True)

        assert shape == (1024, 1024)

    def test_non_array_raises_error(self):
        """Test that non-array item raises error."""
        arr = np.zeros((1024, 1024), dtype=np.uint8)

        with pytest.raises(InvalidChannelDataError, match="Array at index 1 is invalid"):
            validate_arrays_for_packing([arr, "not an array"])


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_small_images(self):
        """Test validation with very small images."""
        img1 = Image.new('L', (1, 1))
        img2 = Image.new('L', (1, 1))

        assert check_resolution_match([img1, img2]) is True
        assert get_max_resolution([img1, img2]) == (1, 1)

    def test_very_large_images(self):
        """Test validation with very large images."""
        img1 = Image.new('L', (8192, 8192))
        img2 = Image.new('L', (8192, 8192))

        assert check_resolution_match([img1, img2]) is True
        assert get_max_resolution([img1, img2]) == (8192, 8192)

    def test_non_square_images(self):
        """Test validation with non-square images."""
        img1 = Image.new('L', (1920, 1080))
        img2 = Image.new('L', (1920, 1080))

        assert check_resolution_match([img1, img2]) is True

    def test_different_color_modes_same_resolution(self):
        """Test that different color modes with same resolution match."""
        img_rgb = Image.new('RGB', (1024, 1024))
        img_l = Image.new('L', (1024, 1024))
        img_rgba = Image.new('RGBA', (1024, 1024))

        assert check_resolution_match([img_rgb, img_l, img_rgba]) is True
