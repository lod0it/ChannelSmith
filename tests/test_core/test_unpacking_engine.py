"""
Tests for the unpacking_engine module.

This module contains unit tests for texture channel unpacking operations.
"""

import pytest
import numpy as np
from PIL import Image
from channelsmith.core.unpacking_engine import (
    extract_channel,
    unpack_texture,
)
from channelsmith.core.packing_template import PackingTemplate
from channelsmith.core.channel_map import ChannelMap
from channelsmith.core.packing_engine import pack_channels


class TestExtractChannel:
    """Test extracting individual channels from packed images."""

    def test_extract_r_channel(self):
        """Test extracting the red channel."""
        image = Image.new('RGB', (256, 256), (255, 128, 64))

        r = extract_channel(image, 'R')

        assert r.shape == (256, 256)
        assert r.dtype == np.uint8
        assert r[0, 0] == 255

    def test_extract_g_channel(self):
        """Test extracting the green channel."""
        image = Image.new('RGB', (256, 256), (255, 128, 64))

        g = extract_channel(image, 'G')

        assert g.shape == (256, 256)
        assert g[0, 0] == 128

    def test_extract_b_channel(self):
        """Test extracting the blue channel."""
        image = Image.new('RGB', (256, 256), (255, 128, 64))

        b = extract_channel(image, 'B')

        assert b.shape == (256, 256)
        assert b[0, 0] == 64

    def test_extract_a_channel_from_rgba(self):
        """Test extracting the alpha channel from an RGBA image."""
        image = Image.new('RGBA', (256, 256), (255, 128, 64, 200))

        a = extract_channel(image, 'A')

        assert a.shape == (256, 256)
        assert a[0, 0] == 200

    def test_extract_a_channel_from_rgb_raises_error(self):
        """Test that extracting alpha from an RGB image raises ValueError."""
        image = Image.new('RGB', (256, 256), (255, 128, 64))

        with pytest.raises(ValueError, match="Cannot extract alpha channel"):
            extract_channel(image, 'A')

    def test_extract_from_grayscale_image(self):
        """Test extracting channels from a grayscale image."""
        image = Image.new('L', (256, 256), 128)

        r = extract_channel(image, 'R')

        assert r.shape == (256, 256)
        # Grayscale converted to RGB puts the same value in all channels
        assert r[0, 0] == 128

    def test_extract_preserves_pixel_values(self):
        """Test that extraction preserves exact pixel values across image."""
        # Create an image with a gradient pattern
        arr = np.zeros((64, 64, 3), dtype=np.uint8)
        arr[:, :, 0] = np.arange(64, dtype=np.uint8).reshape(1, 64)  # R gradient
        arr[:, :, 1] = 100  # G constant
        arr[:, :, 2] = 200  # B constant
        image = Image.fromarray(arr, mode='RGB')

        r = extract_channel(image, 'R')
        g = extract_channel(image, 'G')
        b = extract_channel(image, 'B')

        # Verify R has the gradient
        assert np.array_equal(r, arr[:, :, 0])
        # Verify G and B are constant
        assert np.all(g == 100)
        assert np.all(b == 200)

    def test_extract_invalid_channel_key_raises_error(self):
        """Test that an invalid channel key raises ValueError."""
        image = Image.new('RGB', (256, 256))

        with pytest.raises(ValueError, match="Invalid channel key"):
            extract_channel(image, 'X')

    def test_extract_non_image_raises_error(self):
        """Test that non-Image input raises TypeError."""
        with pytest.raises(TypeError, match="Expected PIL Image instance"):
            extract_channel("not an image", 'R')

    def test_extract_non_square_image(self):
        """Test extracting from a non-square image."""
        image = Image.new('RGB', (1920, 1080), (10, 20, 30))

        r = extract_channel(image, 'R')

        assert r.shape == (1080, 1920)
        assert r[0, 0] == 10

    def test_extract_1x1_image(self):
        """Test extracting from a 1x1 image."""
        image = Image.new('RGB', (1, 1), (42, 84, 126))

        r = extract_channel(image, 'R')
        g = extract_channel(image, 'G')
        b = extract_channel(image, 'B')

        assert r.shape == (1, 1)
        assert r[0, 0] == 42
        assert g[0, 0] == 84
        assert b[0, 0] == 126

    def test_extract_rgb_from_rgba_image(self):
        """Test extracting RGB channels from an RGBA image works."""
        image = Image.new('RGBA', (256, 256), (10, 20, 30, 40))

        r = extract_channel(image, 'R')
        g = extract_channel(image, 'G')
        b = extract_channel(image, 'B')

        assert r[0, 0] == 10
        assert g[0, 0] == 20
        assert b[0, 0] == 30


class TestUnpackTexture:
    """Test unpacking textures using templates."""

    def _create_orm_template(self):
        """Helper to create ORM template."""
        return PackingTemplate(
            'ORM',
            'Occlusion-Roughness-Metallic',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )

    def _create_ord_template(self):
        """Helper to create ORD template."""
        return PackingTemplate(
            'ORD',
            'Occlusion-Roughness-Displacement',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('displacement', 0.5)
            }
        )

    def test_unpack_with_orm_template(self):
        """Test unpacking an RGB image with ORM template."""
        template = self._create_orm_template()
        image = Image.new('RGB', (512, 512), (255, 128, 0))

        channels = unpack_texture(image, template)

        assert 'ambient_occlusion' in channels
        assert 'roughness' in channels
        assert 'metallic' in channels
        assert len(channels) == 3

        assert channels['ambient_occlusion'][0, 0] == 255
        assert channels['roughness'][0, 0] == 128
        assert channels['metallic'][0, 0] == 0

    def test_unpack_with_ord_template(self):
        """Test unpacking an RGB image with ORD template."""
        template = self._create_ord_template()
        image = Image.new('RGB', (512, 512), (200, 100, 50))

        channels = unpack_texture(image, template)

        assert 'ambient_occlusion' in channels
        assert 'roughness' in channels
        assert 'displacement' in channels
        assert len(channels) == 3

        assert channels['ambient_occlusion'][0, 0] == 200
        assert channels['roughness'][0, 0] == 100
        assert channels['displacement'][0, 0] == 50

    def test_unpack_rgba_template(self):
        """Test unpacking an RGBA image with a 4-channel template."""
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
        image = Image.new('RGBA', (512, 512), (255, 128, 0, 200))

        channels = unpack_texture(image, template)

        assert len(channels) == 4
        assert channels['ambient_occlusion'][0, 0] == 255
        assert channels['roughness'][0, 0] == 128
        assert channels['metallic'][0, 0] == 0
        assert channels['alpha'][0, 0] == 200

    def test_unpack_rgba_template_with_rgb_image_raises_error(self):
        """Test that an RGBA template with an RGB image raises ValueError."""
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
        image = Image.new('RGB', (512, 512), (255, 128, 0))

        with pytest.raises(ValueError, match="requires alpha channel"):
            unpack_texture(image, template)

    def test_unpack_rgb_template_with_rgba_image(self):
        """Test that an RGB template with an RGBA image works (ignores alpha)."""
        template = self._create_orm_template()
        image = Image.new('RGBA', (512, 512), (255, 128, 0, 200))

        channels = unpack_texture(image, template)

        # Should only extract R, G, B (no alpha)
        assert len(channels) == 3
        assert 'alpha' not in channels
        assert channels['ambient_occlusion'][0, 0] == 255

    def test_unpack_preserves_array_shapes(self):
        """Test that unpacked arrays have the correct shape."""
        template = self._create_orm_template()
        image = Image.new('RGB', (1024, 768))

        channels = unpack_texture(image, template)

        for name, arr in channels.items():
            assert arr.shape == (768, 1024), f"Shape mismatch for {name}"
            assert arr.dtype == np.uint8

    def test_unpack_partial_template(self):
        """Test unpacking with a template that only uses 2 channels."""
        template = PackingTemplate(
            'OR',
            'Occlusion-Roughness',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5)
            }
        )
        image = Image.new('RGB', (256, 256), (200, 100, 50))

        channels = unpack_texture(image, template)

        assert len(channels) == 2
        assert 'ambient_occlusion' in channels
        assert 'roughness' in channels

    def test_unpack_invalid_image_raises_error(self):
        """Test that non-Image input raises TypeError."""
        template = self._create_orm_template()

        with pytest.raises(TypeError, match="Expected PIL Image instance"):
            unpack_texture("not an image", template)

    def test_unpack_invalid_template_raises_error(self):
        """Test that non-PackingTemplate input raises TypeError."""
        image = Image.new('RGB', (256, 256))

        with pytest.raises(TypeError, match="Expected PackingTemplate instance"):
            unpack_texture(image, "not a template")

    def test_unpack_empty_template(self):
        """Test unpacking with a template that has no channels used."""
        template = PackingTemplate('Empty', 'No channels')
        image = Image.new('RGB', (256, 256))

        channels = unpack_texture(image, template)

        assert channels == {}


class TestPackUnpackRoundTrip:
    """Test that packing then unpacking preserves channel data."""

    def test_round_trip_rgb(self):
        """Test pack then unpack preserves RGB channel values."""
        r = np.full((512, 512), 200, dtype=np.uint8)
        g = np.full((512, 512), 100, dtype=np.uint8)
        b = np.full((512, 512), 50, dtype=np.uint8)

        packed = pack_channels(r, g, b)

        template = PackingTemplate(
            'ORM',
            'Test',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )
        unpacked = unpack_texture(packed, template)

        assert np.array_equal(unpacked['ambient_occlusion'], r)
        assert np.array_equal(unpacked['roughness'], g)
        assert np.array_equal(unpacked['metallic'], b)

    def test_round_trip_rgba(self):
        """Test pack then unpack preserves RGBA channel values."""
        r = np.full((256, 256), 255, dtype=np.uint8)
        g = np.full((256, 256), 128, dtype=np.uint8)
        b = np.full((256, 256), 64, dtype=np.uint8)
        a = np.full((256, 256), 32, dtype=np.uint8)

        packed = pack_channels(r, g, b, a)

        template = PackingTemplate(
            'ORMA',
            'Test',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
                'A': ChannelMap('alpha', 1.0)
            }
        )
        unpacked = unpack_texture(packed, template)

        assert np.array_equal(unpacked['ambient_occlusion'], r)
        assert np.array_equal(unpacked['roughness'], g)
        assert np.array_equal(unpacked['metallic'], b)
        assert np.array_equal(unpacked['alpha'], a)

    def test_round_trip_with_gradient(self):
        """Test round-trip preserves gradient patterns exactly."""
        gradient = np.tile(
            np.arange(256, dtype=np.uint8), (256, 1)
        )  # 256x256 horizontal gradient

        r = gradient
        g = np.flipud(gradient)
        b = np.fliplr(gradient)

        packed = pack_channels(r, g, b)

        template = PackingTemplate(
            'ORM',
            'Test',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )
        unpacked = unpack_texture(packed, template)

        assert np.array_equal(unpacked['ambient_occlusion'], r)
        assert np.array_equal(unpacked['roughness'], g)
        assert np.array_equal(unpacked['metallic'], b)

    def test_round_trip_1x1_image(self):
        """Test round-trip with a 1x1 image."""
        r = np.array([[42]], dtype=np.uint8)
        g = np.array([[84]], dtype=np.uint8)
        b = np.array([[126]], dtype=np.uint8)

        packed = pack_channels(r, g, b)

        template = PackingTemplate(
            'ORM',
            'Test',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0)
            }
        )
        unpacked = unpack_texture(packed, template)

        assert unpacked['ambient_occlusion'][0, 0] == 42
        assert unpacked['roughness'][0, 0] == 84
        assert unpacked['metallic'][0, 0] == 126
