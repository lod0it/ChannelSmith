"""
Edge case and error handling tests for ChannelSmith.

Tests boundary conditions, unusual inputs, and error paths across the full
packing/unpacking pipeline that are not covered by individual unit tests.
"""

import pytest
import numpy as np
from PIL import Image

from channelsmith.core.packing_engine import (
    pack_channels,
    pack_texture_from_template,
    create_default_channel,
    normalize_resolution,
)
from channelsmith.core.unpacking_engine import (
    extract_channel,
    unpack_texture,
)
from channelsmith.core.packing_template import PackingTemplate
from channelsmith.core.channel_map import ChannelMap
from channelsmith.core.validator import InvalidChannelDataError
from channelsmith.templates.template_loader import (
    load_template,
    TemplateValidationError,
)
from channelsmith.utils.image_utils import (
    load_image,
    save_image,
    to_grayscale,
    ImageLoadError,
)


class TestAllChannelsMissing:
    """Test packing when all channels are missing (should use template defaults)."""

    def test_all_defaults_orm_values_correct(self):
        """Test ORM all-defaults produces correct R/G/B pixel values."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )

        packed = pack_texture_from_template({}, template)
        arr = np.array(packed)

        # AO=1.0→255, Roughness=0.5→127, Metallic=0.0→0
        assert arr[0, 0, 0] == 255
        assert arr[0, 0, 1] in [127, 128]
        assert arr[0, 0, 2] == 0

    def test_all_defaults_unpack_round_trip(self):
        """Test that all-default packed texture unpacks to default values."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )

        packed = pack_texture_from_template({}, template)
        channels = unpack_texture(packed, template)

        assert np.all(channels['ambient_occlusion'] == 255)
        assert np.all((channels['roughness'] == 127) | (channels['roughness'] == 128))
        assert np.all(channels['metallic'] == 0)

    def test_all_defaults_rgba_template(self):
        """Test all-defaults with RGBA template."""
        template = PackingTemplate(
            'ORMA', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
                'A': ChannelMap('alpha', 1.0),
            }
        )

        packed = pack_texture_from_template({}, template)

        assert packed.mode == 'RGBA'
        arr = np.array(packed)
        assert arr[0, 0, 3] == 255  # Alpha default = 1.0


class TestSingleChannelPacking:
    """Test packing with only a single channel provided."""

    def test_single_channel_r_only(self):
        """Test packing with only R channel provided via template."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )
        textures = {
            'ambient_occlusion': np.full((256, 256), 200, dtype=np.uint8),
        }

        packed = pack_texture_from_template(textures, template)
        arr = np.array(packed)

        assert arr[0, 0, 0] == 200   # Provided AO
        assert arr[0, 0, 1] in [127, 128]  # Default roughness
        assert arr[0, 0, 2] == 0     # Default metallic

    def test_single_channel_b_only(self):
        """Test packing with only B channel provided via template."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )
        textures = {
            'metallic': np.full((256, 256), 180, dtype=np.uint8),
        }

        packed = pack_texture_from_template(textures, template)
        arr = np.array(packed)

        assert arr[0, 0, 0] == 255   # Default AO
        assert arr[0, 0, 2] == 180   # Provided metallic

    def test_single_channel_pack_unpack_round_trip(self):
        """Test that single-channel pack/unpack preserves the provided channel."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )
        original = np.full((128, 128), 42, dtype=np.uint8)
        textures = {'roughness': original}

        packed = pack_texture_from_template(textures, template)
        channels = unpack_texture(packed, template)

        assert np.array_equal(channels['roughness'], original)


class TestVerySmallImages:
    """Test 1x1 pixel images through the full pipeline."""

    def test_1x1_pack_unpack_pipeline(self):
        """Test full pack/unpack with 1x1 pixel textures."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )
        textures = {
            'ambient_occlusion': np.array([[10]], dtype=np.uint8),
            'roughness': np.array([[20]], dtype=np.uint8),
            'metallic': np.array([[30]], dtype=np.uint8),
        }

        packed = pack_texture_from_template(textures, template)
        assert packed.size == (1, 1)

        channels = unpack_texture(packed, template)
        assert channels['ambient_occlusion'][0, 0] == 10
        assert channels['roughness'][0, 0] == 20
        assert channels['metallic'][0, 0] == 30

    def test_1x1_save_reload(self, tmp_path):
        """Test saving and reloading a 1x1 packed texture."""
        r = np.array([[42]], dtype=np.uint8)
        g = np.array([[84]], dtype=np.uint8)
        b = np.array([[126]], dtype=np.uint8)

        packed = pack_channels(r, g, b)
        path = str(tmp_path / "tiny.png")
        save_image(packed, path)

        reloaded = load_image(path)
        assert reloaded.size == (1, 1)

        r_out = extract_channel(reloaded, 'R')
        assert r_out[0, 0] == 42

    def test_2x2_image(self):
        """Test 2x2 pixel image packing."""
        r = np.array([[0, 255], [128, 64]], dtype=np.uint8)
        g = np.array([[255, 0], [64, 128]], dtype=np.uint8)
        b = np.array([[128, 128], [0, 255]], dtype=np.uint8)

        packed = pack_channels(r, g, b)
        assert packed.size == (2, 2)

        arr = np.array(packed)
        assert arr[0, 0, 0] == 0
        assert arr[0, 1, 0] == 255
        assert arr[1, 0, 2] == 0
        assert arr[1, 1, 2] == 255


class TestVeryLargeImages:
    """Test large images (4096x4096) through the pipeline."""

    def test_4096_pack_channels(self):
        """Test packing 4096x4096 channels."""
        r = np.full((4096, 4096), 100, dtype=np.uint8)
        g = np.full((4096, 4096), 150, dtype=np.uint8)
        b = np.full((4096, 4096), 200, dtype=np.uint8)

        packed = pack_channels(r, g, b)

        assert packed.size == (4096, 4096)
        assert packed.mode == 'RGB'

    def test_4096_pack_unpack_round_trip(self):
        """Test that 4096x4096 survives pack/unpack round-trip."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )
        textures = {
            'ambient_occlusion': np.full((4096, 4096), 200, dtype=np.uint8),
            'roughness': np.full((4096, 4096), 100, dtype=np.uint8),
            'metallic': np.full((4096, 4096), 50, dtype=np.uint8),
        }

        packed = pack_texture_from_template(textures, template)
        channels = unpack_texture(packed, template)

        assert channels['ambient_occlusion'].shape == (4096, 4096)
        assert np.all(channels['ambient_occlusion'] == 200)
        assert np.all(channels['roughness'] == 100)
        assert np.all(channels['metallic'] == 50)

    def test_4096_save_reload(self, tmp_path):
        """Test saving and reloading a 4096x4096 texture."""
        packed = Image.new('RGB', (4096, 4096), (100, 150, 200))
        path = str(tmp_path / "large.png")
        save_image(packed, path)

        reloaded = load_image(path)
        assert reloaded.size == (4096, 4096)


class TestInvalidTemplates:
    """Test handling of invalid and malformed templates."""

    def test_malformed_json_file(self, tmp_path):
        """Test loading a file with invalid JSON syntax."""
        bad_path = tmp_path / "bad.json"
        bad_path.write_text("{not valid json!!!", encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="Invalid JSON"):
            load_template(str(bad_path))

    def test_json_missing_name(self, tmp_path):
        """Test loading a JSON file missing the 'name' field."""
        path = tmp_path / "noname.json"
        path.write_text('{"description": "test", "channels": {}}', encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="missing required field: 'name'"):
            load_template(str(path))

    def test_json_missing_description(self, tmp_path):
        """Test loading a JSON file missing the 'description' field."""
        path = tmp_path / "nodesc.json"
        path.write_text('{"name": "Test", "channels": {}}', encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="missing required field: 'description'"):
            load_template(str(path))

    def test_json_invalid_channel_key(self, tmp_path):
        """Test loading a template with an invalid channel key."""
        import json
        data = {
            "name": "Bad",
            "description": "Bad template",
            "channels": {
                "X": {"type": "roughness", "default": 0.5}
            }
        }
        path = tmp_path / "badkey.json"
        path.write_text(json.dumps(data), encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="Invalid channel key"):
            load_template(str(path))

    def test_json_channel_default_out_of_range(self, tmp_path):
        """Test loading a template with default value outside 0-1 range."""
        import json
        data = {
            "name": "Bad",
            "description": "Bad template",
            "channels": {
                "R": {"type": "roughness", "default": 2.0}
            }
        }
        path = tmp_path / "baddefault.json"
        path.write_text(json.dumps(data), encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="Invalid channel data"):
            load_template(str(path))

    def test_nonexistent_template_file(self):
        """Test loading a template that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_template("does/not/exist.json")

    def test_empty_json_object(self, tmp_path):
        """Test loading an empty JSON object."""
        path = tmp_path / "empty.json"
        path.write_text('{}', encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="missing required field"):
            load_template(str(path))

    def test_json_array_instead_of_object(self, tmp_path):
        """Test loading a JSON array instead of an object."""
        path = tmp_path / "array.json"
        path.write_text('[1, 2, 3]', encoding='utf-8')

        with pytest.raises(TemplateValidationError, match="must contain a JSON object"):
            load_template(str(path))


class TestCorruptedImages:
    """Test handling of corrupted and invalid image files."""

    def test_corrupted_file_raises_error(self, tmp_path):
        """Test loading a corrupted image file."""
        path = tmp_path / "corrupted.png"
        path.write_bytes(b"not a real image file content here")

        with pytest.raises(ImageLoadError):
            load_image(str(path))

    def test_empty_file_raises_error(self, tmp_path):
        """Test loading an empty file."""
        path = tmp_path / "empty.png"
        path.write_bytes(b"")

        with pytest.raises(ImageLoadError):
            load_image(str(path))

    def test_corrupted_path_in_template_packing(self, tmp_path):
        """Test packing with a file path that points to a corrupted image."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )

        corrupted = tmp_path / "corrupted.png"
        corrupted.write_bytes(b"not an image")

        textures = {
            'ambient_occlusion': str(corrupted),
            'roughness': np.full((256, 256), 128, dtype=np.uint8),
        }

        with pytest.raises(ImageLoadError):
            pack_texture_from_template(textures, template)

    def test_nonexistent_path_in_template_packing(self):
        """Test packing with a file path that doesn't exist."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
            }
        )

        textures = {
            'ambient_occlusion': '/nonexistent/path/ao.png',
        }

        with pytest.raises(FileNotFoundError):
            pack_texture_from_template(textures, template)

    def test_truncated_png_raises_error(self, tmp_path):
        """Test loading a truncated PNG (valid header, incomplete data)."""
        # PNG header bytes
        png_header = b'\x89PNG\r\n\x1a\n'
        path = tmp_path / "truncated.png"
        path.write_bytes(png_header + b'\x00' * 20)

        with pytest.raises(ImageLoadError):
            load_image(str(path))


class TestUnsupportedImageFormats:
    """Test handling of unsupported or unusual image modes."""

    def test_extract_channel_from_palette_mode(self):
        """Test extracting a channel from a palette (P) mode image."""
        img = Image.new('P', (64, 64))
        # Should convert internally and extract
        r = extract_channel(img, 'R')
        assert r.shape == (64, 64)

    def test_extract_channel_from_cmyk_mode(self):
        """Test extracting a channel from CMYK mode image."""
        img = Image.new('CMYK', (64, 64), (100, 50, 25, 10))
        # Should convert to RGB internally
        r = extract_channel(img, 'R')
        assert r.shape == (64, 64)

    def test_extract_channel_from_1bit_mode(self):
        """Test extracting a channel from 1-bit (binary) mode image."""
        img = Image.new('1', (64, 64), 1)
        r = extract_channel(img, 'R')
        assert r.shape == (64, 64)

    def test_pack_from_rgb_image_source(self):
        """Test packing when a source texture is an RGB image (not grayscale)."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )
        textures = {
            'ambient_occlusion': Image.new('RGB', (256, 256), (200, 200, 200)),
            'roughness': Image.new('L', (256, 256), 128),
            'metallic': Image.new('L', (256, 256), 0),
        }

        # RGB image gets converted to grayscale by to_grayscale()
        packed = pack_texture_from_template(textures, template)
        assert packed.mode == 'RGB'
        assert packed.size == (256, 256)


class TestGrayscaleInputWhenColorExpected:
    """Test behavior when grayscale images are used where color is expected."""

    def test_unpack_grayscale_image_with_rgb_template(self):
        """Test unpacking a grayscale image (L mode) with an RGB template."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )
        # Grayscale image - all channels will be the same value
        image = Image.new('L', (128, 128), 180)

        channels = unpack_texture(image, template)

        # All channels should have the same value (grayscale → RGB conversion)
        assert channels['ambient_occlusion'][0, 0] == 180
        assert channels['roughness'][0, 0] == 180
        assert channels['metallic'][0, 0] == 180

    def test_extract_all_rgb_from_grayscale(self):
        """Test that extracting R, G, B from grayscale gives identical values."""
        image = Image.new('L', (64, 64), 100)

        r = extract_channel(image, 'R')
        g = extract_channel(image, 'G')
        b = extract_channel(image, 'B')

        assert np.array_equal(r, g)
        assert np.array_equal(g, b)
        assert r[0, 0] == 100


class TestNonUint8ArrayInputs:
    """Test handling of arrays with non-standard dtypes."""

    def test_float32_array_in_pack_channels(self):
        """Test that float32 arrays work in pack_channels."""
        r = np.full((128, 128), 200.0, dtype=np.float32)
        g = np.full((128, 128), 100.0, dtype=np.float32)
        b = np.full((128, 128), 50.0, dtype=np.float32)

        packed = pack_channels(r, g, b)
        assert packed.size == (128, 128)

    def test_int16_array_in_pack_channels(self):
        """Test that int16 arrays work in pack_channels."""
        r = np.full((128, 128), 200, dtype=np.int16)
        g = np.full((128, 128), 100, dtype=np.int16)
        b = np.full((128, 128), 50, dtype=np.int16)

        packed = pack_channels(r, g, b)
        assert packed.size == (128, 128)

    def test_float64_array_in_template_packing(self):
        """Test that float64 arrays work with template packing."""
        template = PackingTemplate(
            'ORM', 'Test', {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
            }
        )
        textures = {
            'ambient_occlusion': np.full((128, 128), 200.0, dtype=np.float64),
            'roughness': np.full((128, 128), 100.0, dtype=np.float64),
            'metallic': np.full((128, 128), 50.0, dtype=np.float64),
        }

        packed = pack_texture_from_template(textures, template)
        assert packed.mode == 'RGB'


class TestNormalizeResolutionEdgeCases:
    """Test edge cases in resolution normalization."""

    def test_normalize_single_array(self):
        """Test normalizing a single array."""
        arr = np.full((128, 128), 100, dtype=np.uint8)
        result = normalize_resolution([arr], (256, 256))

        assert len(result) == 1
        assert result[0].shape == (256, 256)

    def test_normalize_downscale_not_supported_but_works(self):
        """Test that resizing to smaller dimensions still works."""
        arr = np.full((512, 512), 100, dtype=np.uint8)
        result = normalize_resolution([arr], (128, 128))

        assert result[0].shape == (128, 128)
        # Value should be approximately preserved
        assert np.mean(result[0]) == pytest.approx(100, abs=2)

    def test_normalize_asymmetric_resize(self):
        """Test resizing with different width and height scaling factors."""
        arr = np.full((64, 128), 200, dtype=np.uint8)
        result = normalize_resolution([arr], (256, 512))

        assert result[0].shape == (512, 256)


class TestCreateDefaultChannelEdgeCases:
    """Test edge cases for default channel creation."""

    def test_create_default_1x1(self):
        """Test creating a 1x1 default channel."""
        channel = create_default_channel((1, 1), 0.5)
        assert channel.shape == (1, 1)
        assert channel[0, 0] in [127, 128]

    def test_create_default_boundary_values(self):
        """Test default channel with exact boundary values."""
        ch_zero = create_default_channel((8, 8), 0.0)
        ch_one = create_default_channel((8, 8), 1.0)

        assert np.all(ch_zero == 0)
        assert np.all(ch_one == 255)

    def test_create_default_fine_precision(self):
        """Test default channel with fine float precision values."""
        ch = create_default_channel((8, 8), 0.123456789)
        # 0.123456789 * 255 = 31.48 → int(31.48) = 31
        assert np.all(ch == 31)


class TestSaveImageEdgeCases:
    """Test edge cases in saving images."""

    def test_save_and_reload_tga(self, tmp_path):
        """Test saving and reloading a TGA file."""
        packed = Image.new('RGB', (64, 64), (100, 150, 200))
        path = str(tmp_path / "output.tga")
        save_image(packed, path)

        reloaded = load_image(path)
        assert reloaded.size == (64, 64)

    def test_save_and_reload_tiff(self, tmp_path):
        """Test saving and reloading a TIFF file."""
        packed = Image.new('RGB', (64, 64), (100, 150, 200))
        path = str(tmp_path / "output.tiff")
        save_image(packed, path)

        reloaded = load_image(path)
        assert reloaded.size == (64, 64)

    def test_save_and_reload_bmp(self, tmp_path):
        """Test saving and reloading a BMP file."""
        packed = Image.new('RGB', (64, 64), (100, 150, 200))
        path = str(tmp_path / "output.bmp")
        save_image(packed, path)

        reloaded = load_image(path)
        assert reloaded.size == (64, 64)

    def test_save_rgba_as_png(self, tmp_path):
        """Test saving RGBA image preserves alpha through disk round-trip."""
        packed = Image.new('RGBA', (64, 64), (100, 150, 200, 180))
        path = str(tmp_path / "rgba.png")
        save_image(packed, path)

        reloaded = load_image(path)
        assert reloaded.mode == 'RGBA'
        arr = np.array(reloaded)
        assert arr[0, 0, 3] == 180
