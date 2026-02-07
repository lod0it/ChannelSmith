"""
Tests for the packing_engine module.

This module contains unit tests for texture channel packing operations.
"""

import pytest
import numpy as np
from PIL import Image
from channelsmith.core.packing_engine import (
    normalize_resolution,
    pack_channels,
    pack_texture_from_template,
    create_default_channel,
)
from channelsmith.core.packing_template import PackingTemplate
from channelsmith.core.channel_map import ChannelMap
from channelsmith.core.validator import InvalidChannelDataError


class TestNormalizeResolution:
    """Test normalizing arrays to a target resolution."""

    def test_normalize_matching_resolution(self):
        """Test that arrays at target size are unchanged."""
        arr1 = np.zeros((1024, 1024), dtype=np.uint8)
        arr2 = np.ones((1024, 1024), dtype=np.uint8) * 255

        normalized = normalize_resolution([arr1, arr2], (1024, 1024))

        assert len(normalized) == 2
        assert normalized[0].shape == (1024, 1024)
        assert normalized[1].shape == (1024, 1024)
        assert np.array_equal(normalized[0], arr1)
        assert np.array_equal(normalized[1], arr2)

    def test_normalize_upscale_smaller_arrays(self):
        """Test upscaling smaller arrays to target size."""
        arr1 = np.zeros((512, 512), dtype=np.uint8)
        arr2 = np.zeros((256, 256), dtype=np.uint8)

        normalized = normalize_resolution([arr1, arr2], (1024, 1024))

        assert len(normalized) == 2
        assert normalized[0].shape == (1024, 1024)
        assert normalized[1].shape == (1024, 1024)

    def test_normalize_preserves_values(self):
        """Test that normalization preserves general value ranges."""
        # Create array with known pattern
        arr = np.full((512, 512), 128, dtype=np.uint8)

        normalized = normalize_resolution([arr], (1024, 1024))

        # Values should be approximately preserved (bilinear interpolation)
        assert np.mean(normalized[0]) == pytest.approx(128, abs=2)

    def test_normalize_non_square_target(self):
        """Test normalizing to non-square resolution."""
        arr = np.zeros((512, 512), dtype=np.uint8)

        normalized = normalize_resolution([arr], (1920, 1080))

        assert normalized[0].shape == (1080, 1920)

    def test_normalize_empty_list_raises_error(self):
        """Test that empty list raises ValueError."""
        with pytest.raises(ValueError, match="Arrays list cannot be empty"):
            normalize_resolution([], (1024, 1024))

    def test_normalize_invalid_target_size_raises_error(self):
        """Test that invalid target size raises ValueError."""
        arr = np.zeros((512, 512), dtype=np.uint8)

        with pytest.raises(ValueError, match="Invalid target_size"):
            normalize_resolution([arr], (0, 1024))

        with pytest.raises(ValueError, match="Invalid target_size"):
            normalize_resolution([arr], (1024, -1))


class TestPackChannels:
    """Test packing grayscale channels into RGB/RGBA images."""

    def test_pack_rgb_channels(self):
        """Test packing 3 channels produces RGB image."""
        r = np.full((1024, 1024), 255, dtype=np.uint8)
        g = np.full((1024, 1024), 128, dtype=np.uint8)
        b = np.zeros((1024, 1024), dtype=np.uint8)

        packed = pack_channels(r, g, b)

        assert isinstance(packed, Image.Image)
        assert packed.mode == 'RGB'
        assert packed.size == (1024, 1024)

    def test_pack_rgba_channels(self):
        """Test packing 4 channels produces RGBA image."""
        r = np.full((1024, 1024), 255, dtype=np.uint8)
        g = np.full((1024, 1024), 128, dtype=np.uint8)
        b = np.zeros((1024, 1024), dtype=np.uint8)
        a = np.full((1024, 1024), 200, dtype=np.uint8)

        packed = pack_channels(r, g, b, a)

        assert packed.mode == 'RGBA'
        assert packed.size == (1024, 1024)

    def test_pack_preserves_channel_values(self):
        """Test that packed image contains correct channel values."""
        r = np.full((256, 256), 255, dtype=np.uint8)
        g = np.full((256, 256), 128, dtype=np.uint8)
        b = np.full((256, 256), 64, dtype=np.uint8)

        packed = pack_channels(r, g, b)
        packed_array = np.array(packed)

        # Check a sample pixel
        assert packed_array[0, 0, 0] == 255  # Red
        assert packed_array[0, 0, 1] == 128  # Green
        assert packed_array[0, 0, 2] == 64   # Blue

    def test_pack_with_missing_channels_fills_zeros(self):
        """Test that missing RGB channels are filled with zeros."""
        r = np.full((256, 256), 255, dtype=np.uint8)

        packed = pack_channels(r=r)
        packed_array = np.array(packed)

        assert packed_array[0, 0, 0] == 255  # Red
        assert packed_array[0, 0, 1] == 0    # Green (missing)
        assert packed_array[0, 0, 2] == 0    # Blue (missing)

    def test_pack_with_mismatched_resolutions_normalizes(self):
        """Test that mismatched resolutions are normalized."""
        r = np.full((512, 512), 255, dtype=np.uint8)
        g = np.full((1024, 1024), 128, dtype=np.uint8)
        b = np.full((256, 256), 64, dtype=np.uint8)

        packed = pack_channels(r, g, b)

        # Should be normalized to max resolution (1024x1024)
        assert packed.size == (1024, 1024)

    def test_pack_all_none_raises_error(self):
        """Test that all None channels raise ValueError."""
        with pytest.raises(ValueError, match="At least one channel must be provided"):
            pack_channels()

    def test_pack_invalid_channel_data_raises_error(self):
        """Test that invalid channel data raises error."""
        r = np.full((1024, 1024, 3), 255, dtype=np.uint8)  # 3D array (invalid)

        with pytest.raises(InvalidChannelDataError):
            pack_channels(r=r)

    def test_pack_single_channel_only(self):
        """Test packing with only one channel."""
        g = np.full((512, 512), 128, dtype=np.uint8)

        packed = pack_channels(g=g)

        assert packed.mode == 'RGB'
        assert packed.size == (512, 512)


class TestPackTextureFromTemplate:
    """Test packing textures using templates."""

    def test_pack_with_orm_template_from_arrays(self):
        """Test packing with ORM template using NumPy arrays."""
        template = PackingTemplate(
            'ORM',
            'Test ORM',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )

        textures = {
            'ambient_occlusion': np.full((1024, 1024), 255, dtype=np.uint8),
            'roughness': np.full((1024, 1024), 128, dtype=np.uint8),
            'metallic': np.zeros((1024, 1024), dtype=np.uint8)
        }

        packed = pack_texture_from_template(textures, template)

        assert packed.mode == 'RGB'
        assert packed.size == (1024, 1024)

    def test_pack_with_orm_template_from_images(self, tmp_path):
        """Test packing with ORM template using PIL Images."""
        template = PackingTemplate(
            'ORM',
            'Test ORM',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )

        textures = {
            'ambient_occlusion': Image.new('L', (1024, 1024), 255),
            'roughness': Image.new('L', (1024, 1024), 128),
            'metallic': Image.new('L', (1024, 1024), 0)
        }

        packed = pack_texture_from_template(textures, template)

        assert packed.mode == 'RGB'
        assert packed.size == (1024, 1024)

    def test_pack_with_file_paths(self, tmp_path):
        """Test packing with file path sources."""
        template = PackingTemplate(
            'ORM',
            'Test ORM',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )

        # Create test images
        ao_path = tmp_path / "ao.png"
        roughness_path = tmp_path / "roughness.png"
        metallic_path = tmp_path / "metallic.png"

        Image.new('L', (512, 512), 255).save(ao_path)
        Image.new('L', (512, 512), 128).save(roughness_path)
        Image.new('L', (512, 512), 0).save(metallic_path)

        textures = {
            'ambient_occlusion': str(ao_path),
            'roughness': str(roughness_path),
            'metallic': str(metallic_path)
        }

        packed = pack_texture_from_template(textures, template)

        assert packed.mode == 'RGB'
        assert packed.size == (512, 512)

    def test_pack_with_missing_textures_uses_defaults(self):
        """Test that missing textures are filled with default values."""
        template = PackingTemplate(
            'ORM',
            'Test ORM',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )

        # Only provide one texture
        textures = {
            'ambient_occlusion': np.full((1024, 1024), 255, dtype=np.uint8)
        }

        packed = pack_texture_from_template(textures, template)
        packed_array = np.array(packed)

        # R channel should have the provided texture
        assert packed_array[0, 0, 0] == 255
        # G channel should have default (0.5 * 255 = 127)
        assert packed_array[0, 0, 1] in [127, 128]  # Allow rounding
        # B channel should have default (0.0 * 255 = 0)
        assert packed_array[0, 0, 2] == 0

    def test_pack_with_all_defaults(self):
        """Test packing with all default values (no textures provided)."""
        template = PackingTemplate(
            'ORM',
            'Test ORM',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )

        textures = {}

        packed = pack_texture_from_template(textures, template)

        # Should use default resolution (1024x1024)
        assert packed.size == (1024, 1024)
        assert packed.mode == 'RGB'

    def test_pack_with_rgba_template(self):
        """Test packing with template that includes alpha channel."""
        template = PackingTemplate(
            'ORMA',
            'ORM with Alpha',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
                'A': ChannelMap('alpha', 1.0)
            }
        )

        textures = {
            'ambient_occlusion': np.full((512, 512), 255, dtype=np.uint8),
            'roughness': np.full((512, 512), 128, dtype=np.uint8),
            'metallic': np.zeros((512, 512), dtype=np.uint8),
            'alpha': np.full((512, 512), 200, dtype=np.uint8)
        }

        packed = pack_texture_from_template(textures, template)

        assert packed.mode == 'RGBA'
        assert packed.size == (512, 512)

    def test_pack_with_mismatched_resolutions(self):
        """Test packing with textures of different resolutions."""
        template = PackingTemplate(
            'ORM',
            'Test ORM',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )

        textures = {
            'ambient_occlusion': np.full((512, 512), 255, dtype=np.uint8),
            'roughness': np.full((1024, 1024), 128, dtype=np.uint8),
            'metallic': np.full((256, 256), 0, dtype=np.uint8)
        }

        packed = pack_texture_from_template(textures, template)

        # Should normalize to max resolution (1024x1024)
        assert packed.size == (1024, 1024)

    def test_pack_with_invalid_template_raises_error(self):
        """Test that invalid template raises TypeError."""
        textures = {
            'ambient_occlusion': np.zeros((512, 512), dtype=np.uint8)
        }

        with pytest.raises(TypeError, match="Expected PackingTemplate instance"):
            pack_texture_from_template(textures, "not a template")

    def test_pack_with_invalid_texture_source_raises_error(self):
        """Test that invalid texture source raises TypeError."""
        template = PackingTemplate(
            'ORM',
            'Test ORM',
            {
                'R': ChannelMap('ambient_occlusion', 1.0)
            }
        )

        textures = {
            'ambient_occlusion': 12345  # Invalid type
        }

        with pytest.raises(TypeError, match="Invalid texture source"):
            pack_texture_from_template(textures, template)


class TestCreateDefaultChannel:
    """Test creating default channel arrays."""

    def test_create_default_channel_mid_value(self):
        """Test creating channel with mid-range value."""
        channel = create_default_channel((512, 512), 0.5)

        assert channel.shape == (512, 512)
        assert channel.dtype == np.uint8
        assert channel[0, 0] in [127, 128]  # 0.5 * 255

    def test_create_default_channel_min_value(self):
        """Test creating channel with minimum value."""
        channel = create_default_channel((256, 256), 0.0)

        assert np.all(channel == 0)

    def test_create_default_channel_max_value(self):
        """Test creating channel with maximum value."""
        channel = create_default_channel((256, 256), 1.0)

        assert np.all(channel == 255)

    def test_create_default_channel_non_square(self):
        """Test creating non-square channel."""
        channel = create_default_channel((1920, 1080), 0.5)

        assert channel.shape == (1080, 1920)

    def test_create_default_channel_invalid_value_raises_error(self):
        """Test that invalid default value raises ValueError."""
        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            create_default_channel((512, 512), 1.5)

        with pytest.raises(ValueError, match="must be between 0.0 and 1.0"):
            create_default_channel((512, 512), -0.1)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_pack_very_small_texture(self):
        """Test packing very small textures."""
        r = np.full((1, 1), 255, dtype=np.uint8)
        g = np.full((1, 1), 128, dtype=np.uint8)
        b = np.zeros((1, 1), dtype=np.uint8)

        packed = pack_channels(r, g, b)

        assert packed.size == (1, 1)

    def test_pack_very_large_texture(self):
        """Test packing very large textures."""
        r = np.full((4096, 4096), 255, dtype=np.uint8)

        packed = pack_channels(r=r)

        assert packed.size == (4096, 4096)

    def test_pack_non_square_textures(self):
        """Test packing non-square textures."""
        r = np.full((1080, 1920), 255, dtype=np.uint8)
        g = np.full((1080, 1920), 128, dtype=np.uint8)

        packed = pack_channels(r, g)

        assert packed.size == (1920, 1080)
