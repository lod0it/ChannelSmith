"""
Integration tests for end-to-end ChannelSmith workflows.

Tests the full pipeline from loading templates and images through
packing, unpacking, repacking, and saving results to disk.
"""

import os
import pytest
import numpy as np
from PIL import Image

from channelsmith.core.packing_engine import (
    pack_channels,
    pack_texture_from_template,
)
from channelsmith.core.unpacking_engine import (
    extract_channel,
    unpack_texture,
)
from channelsmith.core.packing_template import PackingTemplate
from channelsmith.core.channel_map import ChannelMap
from channelsmith.templates.template_loader import load_template, save_template
from channelsmith.utils.image_utils import (
    load_image,
    save_image,
    to_grayscale,
)


# Path to the bundled template JSON files
TEMPLATES_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'channelsmith', 'templates'
)


@pytest.fixture
def orm_template():
    """Load the ORM template from the bundled JSON file."""
    return load_template(os.path.join(TEMPLATES_DIR, 'orm.json'))


@pytest.fixture
def ord_template():
    """Load the ORD template from the bundled JSON file."""
    return load_template(os.path.join(TEMPLATES_DIR, 'ord.json'))


@pytest.fixture
def sample_textures():
    """Create sample grayscale texture arrays for testing."""
    return {
        'ambient_occlusion': np.full((512, 512), 230, dtype=np.uint8),
        'roughness': np.full((512, 512), 140, dtype=np.uint8),
        'metallic': np.full((512, 512), 25, dtype=np.uint8),
        'displacement': np.full((512, 512), 180, dtype=np.uint8),
    }


@pytest.fixture
def sample_texture_files(tmp_path, sample_textures):
    """Save sample textures as PNG files and return their paths."""
    paths = {}
    for name, array in sample_textures.items():
        img = Image.fromarray(array, mode='L')
        path = tmp_path / f"{name}.png"
        img.save(path)
        paths[name] = str(path)
    return paths


class TestWorkflow1PackTextures:
    """Workflow 1: Load grayscale images and pack into a single texture."""

    def test_pack_from_arrays_with_orm_template(self, orm_template, sample_textures):
        """Test packing NumPy arrays using the ORM template."""
        packed = pack_texture_from_template(sample_textures, orm_template)

        assert isinstance(packed, Image.Image)
        assert packed.mode == 'RGB'
        assert packed.size == (512, 512)

    def test_pack_from_files_with_orm_template(self, orm_template, sample_texture_files):
        """Test packing from file paths using the ORM template."""
        packed = pack_texture_from_template(sample_texture_files, orm_template)

        assert isinstance(packed, Image.Image)
        assert packed.mode == 'RGB'
        assert packed.size == (512, 512)

    def test_pack_from_pil_images_with_orm_template(self, orm_template):
        """Test packing from PIL Image objects using the ORM template."""
        textures = {
            'ambient_occlusion': Image.new('L', (512, 512), 230),
            'roughness': Image.new('L', (512, 512), 140),
            'metallic': Image.new('L', (512, 512), 25),
        }

        packed = pack_texture_from_template(textures, orm_template)

        assert packed.mode == 'RGB'
        assert packed.size == (512, 512)

    def test_pack_channel_values_are_correct(self, orm_template, sample_textures):
        """Test that packed pixel values match the input textures."""
        packed = pack_texture_from_template(sample_textures, orm_template)
        packed_array = np.array(packed)

        # ORM: R=AO, G=Roughness, B=Metallic
        assert packed_array[0, 0, 0] == 230   # AO
        assert packed_array[0, 0, 1] == 140   # Roughness
        assert packed_array[0, 0, 2] == 25    # Metallic

    def test_pack_and_save_to_disk(self, orm_template, sample_textures, tmp_path):
        """Test packing and saving result to a PNG file."""
        packed = pack_texture_from_template(sample_textures, orm_template)

        output_path = str(tmp_path / "packed_orm.png")
        save_image(packed, output_path)

        # Reload and verify
        reloaded = load_image(output_path)
        assert reloaded.size == (512, 512)
        assert reloaded.mode == 'RGB'

        reloaded_array = np.array(reloaded)
        assert reloaded_array[0, 0, 0] == 230


class TestWorkflow2UnpackTextures:
    """Workflow 2: Load a packed texture and extract individual channels."""

    def test_unpack_orm_extracts_all_channels(self, orm_template, sample_textures):
        """Test unpacking an ORM texture returns all 3 channel types."""
        packed = pack_texture_from_template(sample_textures, orm_template)

        channels = unpack_texture(packed, orm_template)

        assert set(channels.keys()) == {'ambient_occlusion', 'roughness', 'metallic'}

    def test_unpack_orm_channels_match_originals(self, orm_template, sample_textures):
        """Test unpacked channels contain the same data as the originals."""
        packed = pack_texture_from_template(sample_textures, orm_template)
        channels = unpack_texture(packed, orm_template)

        assert np.array_equal(channels['ambient_occlusion'], sample_textures['ambient_occlusion'])
        assert np.array_equal(channels['roughness'], sample_textures['roughness'])
        assert np.array_equal(channels['metallic'], sample_textures['metallic'])

    def test_unpack_from_saved_file(self, orm_template, sample_textures, tmp_path):
        """Test unpacking a texture that was saved to disk."""
        packed = pack_texture_from_template(sample_textures, orm_template)
        output_path = str(tmp_path / "packed_orm.png")
        save_image(packed, output_path)

        # Load from disk and unpack
        loaded = load_image(output_path)
        channels = unpack_texture(loaded, orm_template)

        assert np.array_equal(channels['ambient_occlusion'], sample_textures['ambient_occlusion'])
        assert np.array_equal(channels['roughness'], sample_textures['roughness'])
        assert np.array_equal(channels['metallic'], sample_textures['metallic'])

    def test_unpack_and_save_individual_channels(self, orm_template, sample_textures, tmp_path):
        """Test unpacking and saving each channel as a separate grayscale file."""
        packed = pack_texture_from_template(sample_textures, orm_template)
        channels = unpack_texture(packed, orm_template)

        for name, array in channels.items():
            channel_path = str(tmp_path / f"{name}.png")
            channel_img = Image.fromarray(array, mode='L')
            save_image(channel_img, channel_path)

            # Verify saved file
            reloaded = load_image(channel_path)
            reloaded_array = to_grayscale(reloaded)
            assert np.array_equal(reloaded_array, array)


class TestWorkflow3RepackOrmToOrd:
    """Workflow 3: Unpack an ORM texture, then repack as ORD."""

    def test_repack_orm_to_ord_full_workflow(
        self, orm_template, ord_template, sample_textures
    ):
        """Test full ORM -> ORD repacking workflow."""
        # Step 1: Pack with ORM template
        orm_packed = pack_texture_from_template(sample_textures, orm_template)
        assert orm_packed.mode == 'RGB'

        # Step 2: Unpack the ORM texture
        orm_channels = unpack_texture(orm_packed, orm_template)
        assert 'ambient_occlusion' in orm_channels
        assert 'roughness' in orm_channels
        assert 'metallic' in orm_channels

        # Step 3: Build new texture dict for ORD (reuse AO and roughness, add displacement)
        ord_textures = {
            'ambient_occlusion': orm_channels['ambient_occlusion'],
            'roughness': orm_channels['roughness'],
            'displacement': sample_textures['displacement'],
        }

        # Step 4: Pack with ORD template
        ord_packed = pack_texture_from_template(ord_textures, ord_template)
        assert ord_packed.mode == 'RGB'
        assert ord_packed.size == orm_packed.size

        # Step 5: Verify ORD packed values
        ord_array = np.array(ord_packed)
        assert ord_array[0, 0, 0] == 230  # AO (preserved from ORM)
        assert ord_array[0, 0, 1] == 140  # Roughness (preserved from ORM)
        assert ord_array[0, 0, 2] == 180  # Displacement (new)

    def test_repack_preserves_shared_channels(
        self, orm_template, ord_template, sample_textures
    ):
        """Test that shared channels (AO, roughness) are preserved during repack."""
        orm_packed = pack_texture_from_template(sample_textures, orm_template)
        orm_channels = unpack_texture(orm_packed, orm_template)

        ord_textures = {
            'ambient_occlusion': orm_channels['ambient_occlusion'],
            'roughness': orm_channels['roughness'],
            'displacement': sample_textures['displacement'],
        }
        ord_packed = pack_texture_from_template(ord_textures, ord_template)

        # Unpack the ORD texture and compare shared channels
        ord_channels = unpack_texture(ord_packed, ord_template)

        assert np.array_equal(
            ord_channels['ambient_occlusion'],
            orm_channels['ambient_occlusion']
        )
        assert np.array_equal(
            ord_channels['roughness'],
            orm_channels['roughness']
        )

    def test_repack_with_disk_io(
        self, orm_template, ord_template, sample_textures, tmp_path
    ):
        """Test ORM -> ORD repacking with file save/load between steps."""
        # Pack and save ORM
        orm_packed = pack_texture_from_template(sample_textures, orm_template)
        orm_path = str(tmp_path / "packed_orm.png")
        save_image(orm_packed, orm_path)

        # Load ORM from disk and unpack
        loaded_orm = load_image(orm_path)
        orm_channels = unpack_texture(loaded_orm, orm_template)

        # Create displacement file
        disp_path = str(tmp_path / "displacement.png")
        Image.fromarray(sample_textures['displacement'], mode='L').save(disp_path)

        # Build ORD textures with mix of arrays and file path
        ord_textures = {
            'ambient_occlusion': orm_channels['ambient_occlusion'],
            'roughness': orm_channels['roughness'],
            'displacement': disp_path,
        }
        ord_packed = pack_texture_from_template(ord_textures, ord_template)

        # Save and reload ORD
        ord_path = str(tmp_path / "packed_ord.png")
        save_image(ord_packed, ord_path)

        loaded_ord = load_image(ord_path)
        ord_channels = unpack_texture(loaded_ord, ord_template)

        assert ord_channels['displacement'][0, 0] == 180


class TestWorkflow4SelectiveChannelUpdate:
    """Workflow 4: Unpack, replace one channel, repack with same template."""

    def test_replace_roughness_channel(self, orm_template, sample_textures):
        """Test replacing only the roughness channel in an ORM texture."""
        # Step 1: Pack original textures
        packed = pack_texture_from_template(sample_textures, orm_template)

        # Step 2: Unpack
        channels = unpack_texture(packed, orm_template)

        # Step 3: Replace roughness with a new value
        new_roughness = np.full((512, 512), 200, dtype=np.uint8)
        channels['roughness'] = new_roughness

        # Step 4: Repack with the same template
        repacked = pack_texture_from_template(channels, orm_template)
        repacked_array = np.array(repacked)

        # Step 5: Verify only roughness changed
        assert repacked_array[0, 0, 0] == 230   # AO unchanged
        assert repacked_array[0, 0, 1] == 200   # Roughness updated
        assert repacked_array[0, 0, 2] == 25    # Metallic unchanged

    def test_replace_ao_channel(self, orm_template, sample_textures):
        """Test replacing only the AO channel."""
        packed = pack_texture_from_template(sample_textures, orm_template)
        channels = unpack_texture(packed, orm_template)

        new_ao = np.full((512, 512), 100, dtype=np.uint8)
        channels['ambient_occlusion'] = new_ao

        repacked = pack_texture_from_template(channels, orm_template)
        repacked_array = np.array(repacked)

        assert repacked_array[0, 0, 0] == 100   # AO updated
        assert repacked_array[0, 0, 1] == 140   # Roughness unchanged
        assert repacked_array[0, 0, 2] == 25    # Metallic unchanged

    def test_replace_metallic_channel(self, orm_template, sample_textures):
        """Test replacing only the metallic channel."""
        packed = pack_texture_from_template(sample_textures, orm_template)
        channels = unpack_texture(packed, orm_template)

        new_metallic = np.full((512, 512), 255, dtype=np.uint8)
        channels['metallic'] = new_metallic

        repacked = pack_texture_from_template(channels, orm_template)
        repacked_array = np.array(repacked)

        assert repacked_array[0, 0, 0] == 230   # AO unchanged
        assert repacked_array[0, 0, 1] == 140   # Roughness unchanged
        assert repacked_array[0, 0, 2] == 255   # Metallic updated

    def test_replace_preserves_other_channels_exactly(self, orm_template):
        """Test that untouched channels are bit-for-bit identical after repack."""
        # Use gradient textures for more rigorous verification
        ao = np.tile(np.arange(256, dtype=np.uint8), (256, 1))
        roughness = np.flipud(ao)
        metallic = np.fliplr(ao)

        textures = {
            'ambient_occlusion': ao,
            'roughness': roughness,
            'metallic': metallic,
        }

        packed = pack_texture_from_template(textures, orm_template)
        channels = unpack_texture(packed, orm_template)

        # Replace only roughness
        channels['roughness'] = np.full((256, 256), 42, dtype=np.uint8)
        repacked = pack_texture_from_template(channels, orm_template)

        # Verify unchanged channels are identical
        final_channels = unpack_texture(repacked, orm_template)
        assert np.array_equal(final_channels['ambient_occlusion'], ao)
        assert np.array_equal(final_channels['metallic'], metallic)
        # Verify updated channel
        assert np.all(final_channels['roughness'] == 42)

    def test_selective_update_with_disk_io(self, orm_template, sample_textures, tmp_path):
        """Test selective channel update with save/load between steps."""
        # Pack and save
        packed = pack_texture_from_template(sample_textures, orm_template)
        packed_path = str(tmp_path / "original.png")
        save_image(packed, packed_path)

        # Load, unpack, modify
        loaded = load_image(packed_path)
        channels = unpack_texture(loaded, orm_template)
        channels['roughness'] = np.full((512, 512), 200, dtype=np.uint8)

        # Repack and save
        repacked = pack_texture_from_template(channels, orm_template)
        updated_path = str(tmp_path / "updated.png")
        save_image(repacked, updated_path)

        # Load and verify
        final = load_image(updated_path)
        final_channels = unpack_texture(final, orm_template)

        assert np.array_equal(final_channels['ambient_occlusion'], sample_textures['ambient_occlusion'])
        assert np.all(final_channels['roughness'] == 200)
        assert np.array_equal(final_channels['metallic'], sample_textures['metallic'])


class TestWorkflow5ResolutionMismatchHandling:
    """Workflow 5: Pack textures with mismatched resolutions."""

    def test_mismatched_resolutions_normalize_to_max(self, orm_template):
        """Test that mismatched resolutions are upscaled to the maximum."""
        textures = {
            'ambient_occlusion': np.full((256, 256), 230, dtype=np.uint8),
            'roughness': np.full((512, 512), 140, dtype=np.uint8),
            'metallic': np.full((1024, 1024), 25, dtype=np.uint8),
        }

        packed = pack_texture_from_template(textures, orm_template)

        assert packed.size == (1024, 1024)

    def test_mismatched_resolutions_preserve_values(self, orm_template):
        """Test that uniform textures maintain their values after upscaling."""
        textures = {
            'ambient_occlusion': np.full((128, 128), 200, dtype=np.uint8),
            'roughness': np.full((512, 512), 100, dtype=np.uint8),
            'metallic': np.full((256, 256), 50, dtype=np.uint8),
        }

        packed = pack_texture_from_template(textures, orm_template)
        packed_array = np.array(packed)

        # Uniform values should be preserved after bilinear upscaling
        assert packed_array[0, 0, 0] == pytest.approx(200, abs=1)
        assert packed_array[0, 0, 1] == pytest.approx(100, abs=1)
        assert packed_array[0, 0, 2] == pytest.approx(50, abs=1)

    def test_mismatched_unpack_round_trip(self, orm_template):
        """Test unpack after packing mismatched resolutions gives correct size."""
        textures = {
            'ambient_occlusion': np.full((256, 256), 200, dtype=np.uint8),
            'roughness': np.full((1024, 1024), 100, dtype=np.uint8),
            'metallic': np.full((512, 512), 50, dtype=np.uint8),
        }

        packed = pack_texture_from_template(textures, orm_template)
        channels = unpack_texture(packed, orm_template)

        # All unpacked channels should be at the max resolution
        for name, arr in channels.items():
            assert arr.shape == (1024, 1024), f"Shape mismatch for {name}"

    def test_non_square_mismatched_resolutions(self, orm_template):
        """Test mismatched non-square resolutions."""
        textures = {
            'ambient_occlusion': np.full((256, 512), 200, dtype=np.uint8),
            'roughness': np.full((512, 1024), 100, dtype=np.uint8),
            'metallic': np.full((128, 256), 50, dtype=np.uint8),
        }

        packed = pack_texture_from_template(textures, orm_template)

        # Max width=1024, max height=512
        assert packed.size == (1024, 512)

    def test_missing_channels_use_template_defaults(self, orm_template):
        """Test that missing channels are filled with template defaults at max resolution."""
        # Only provide roughness
        textures = {
            'roughness': np.full((512, 512), 140, dtype=np.uint8),
        }

        packed = pack_texture_from_template(textures, orm_template)
        packed_array = np.array(packed)

        assert packed.size == (512, 512)
        # R = AO default (1.0 * 255 = 255)
        assert packed_array[0, 0, 0] == 255
        # G = provided roughness
        assert packed_array[0, 0, 1] == 140
        # B = Metallic default (0.0 * 255 = 0)
        assert packed_array[0, 0, 2] == 0

    def test_all_defaults_produces_valid_image(self, orm_template):
        """Test packing with no textures at all uses all defaults."""
        packed = pack_texture_from_template({}, orm_template)

        assert isinstance(packed, Image.Image)
        assert packed.mode == 'RGBA'  # Now RGBA because template defines alpha
        # Default size should be 1024x1024
        assert packed.size == (1024, 1024)

        packed_array = np.array(packed)
        # AO default=1.0 (255), Roughness default=0.5 (127), Metallic default=0.0 (0)
        assert packed_array[0, 0, 0] == 255
        assert packed_array[0, 0, 1] in [127, 128]
        assert packed_array[0, 0, 2] == 0


class TestWorkflowCustomTemplates:
    """Test workflows with custom user-created templates."""

    def test_create_save_load_pack_unpack(self, tmp_path):
        """Test creating a custom template, saving/loading it, then using it."""
        # Step 1: Create custom template
        custom = PackingTemplate(
            'RMH',
            'Roughness-Metallic-Height',
            {
                'R': ChannelMap('roughness', 0.5),
                'G': ChannelMap('metallic', 0.0),
                'B': ChannelMap('height', 0.5),
            }
        )

        # Step 2: Save to disk
        template_path = str(tmp_path / "rmh.json")
        save_template(custom, template_path)

        # Step 3: Load from disk
        loaded_template = load_template(template_path)
        assert loaded_template.name == 'RMH'

        # Step 4: Pack textures
        textures = {
            'roughness': np.full((256, 256), 180, dtype=np.uint8),
            'metallic': np.full((256, 256), 60, dtype=np.uint8),
            'height': np.full((256, 256), 128, dtype=np.uint8),
        }
        packed = pack_texture_from_template(textures, loaded_template)

        # Step 5: Unpack and verify
        channels = unpack_texture(packed, loaded_template)
        assert np.array_equal(channels['roughness'], textures['roughness'])
        assert np.array_equal(channels['metallic'], textures['metallic'])
        assert np.array_equal(channels['height'], textures['height'])

    def test_rgba_template_workflow(self, tmp_path):
        """Test full workflow with an RGBA template."""
        template = PackingTemplate(
            'ORMA',
            'ORM with Alpha',
            {
                'R': ChannelMap('ambient_occlusion', 1.0),
                'G': ChannelMap('roughness', 0.5),
                'B': ChannelMap('metallic', 0.0),
                'A': ChannelMap('opacity', 1.0),
            }
        )

        textures = {
            'ambient_occlusion': np.full((256, 256), 200, dtype=np.uint8),
            'roughness': np.full((256, 256), 100, dtype=np.uint8),
            'metallic': np.full((256, 256), 50, dtype=np.uint8),
            'opacity': np.full((256, 256), 180, dtype=np.uint8),
        }

        # Pack
        packed = pack_texture_from_template(textures, template)
        assert packed.mode == 'RGBA'

        # Save and reload
        output_path = str(tmp_path / "packed_orma.png")
        save_image(packed, output_path)
        loaded = load_image(output_path)

        # Unpack
        channels = unpack_texture(loaded, template)
        assert len(channels) == 4
        assert np.array_equal(channels['ambient_occlusion'], textures['ambient_occlusion'])
        assert np.array_equal(channels['roughness'], textures['roughness'])
        assert np.array_equal(channels['metallic'], textures['metallic'])
        assert np.array_equal(channels['opacity'], textures['opacity'])
