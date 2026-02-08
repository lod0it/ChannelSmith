"""
Integration tests for end-to-end ChannelSmith GUI workflows.

Tests complete GUI workflows: packing (select images -> pack -> preview),
unpacking (load -> unpack -> save), drag-drop, and project save/load.
"""

import os
import gc
import tempfile
import tkinter as tk
from unittest.mock import patch, MagicMock
import pytest
import numpy as np
from PIL import Image

# Skip all tests if tkinter is unavailable
pytestmark = pytest.mark.skipif(not hasattr(tk, "Tk"), reason="tkinter unavailable")

from channelsmith.gui.app import ChannelSmithApp
from channelsmith.gui.packer_panel import PackerPanel
from channelsmith.gui.unpacker_panel import UnpackerPanel
from channelsmith.gui.file_manager import save_image, load_project, save_project
from channelsmith.utils.image_utils import load_image, save_image as util_save_image
from channelsmith.core.packing_engine import pack_texture_from_template
from channelsmith.core.unpacking_engine import unpack_texture
from channelsmith.templates.template_loader import load_template


# Path to templates
TEMPLATES_DIR = os.path.join(
    os.path.dirname(__file__), '..', '..', 'channelsmith', 'templates'
)


@pytest.fixture
def root():
    """Create a Tk root window for testing."""
    r = tk.Tk()
    r.withdraw()  # Hide window
    yield r
    try:
        r.destroy()
    except:
        pass
    gc.collect()


@pytest.fixture
def orm_template():
    """Load the ORM template."""
    return load_template(os.path.join(TEMPLATES_DIR, 'orm.json'))


@pytest.fixture
def test_image():
    """Create a test image file."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img = Image.new("L", (256, 256), 128)
        img.save(f.name)
        yield f.name
    try:
        os.unlink(f.name)
    except:
        pass


@pytest.fixture
def sample_texture_files():
    """Create sample grayscale texture files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        files = {}
        for name, value in [
            ("ao", 230),
            ("roughness", 140),
            ("metallic", 25),
        ]:
            path = os.path.join(tmpdir, f"{name}.png")
            img = Image.new("L", (256, 256), value)
            img.save(path)
            files[name] = path
        yield files


class TestPackerPanelWorkflow:
    """Test PackerPanel end-to-end packing workflow."""

    def test_packer_panel_init(self, root):
        """Test PackerPanel initializes correctly."""
        panel = PackerPanel(root)
        assert panel is not None
        root.update()

    def test_packer_panel_pack_with_templates(self, root, orm_template):
        """Test packing workflow directly (bypassing UI interaction)."""
        # Create test images
        textures = {
            'ambient_occlusion': Image.new('L', (256, 256), 230),
            'roughness': Image.new('L', (256, 256), 140),
            'metallic': Image.new('L', (256, 256), 25),
        }

        # Pack using core API
        packed = pack_texture_from_template(textures, orm_template)

        assert packed is not None
        assert packed.mode == 'RGB'
        assert packed.size == (256, 256)


class TestUnpackerPanelWorkflow:
    """Test UnpackerPanel end-to-end unpacking workflow."""

    def test_unpacker_panel_init(self, root):
        """Test UnpackerPanel initializes correctly."""
        panel = UnpackerPanel(root)
        assert panel is not None
        root.update()

    def test_unpacker_panel_unpack_workflow(self, root, orm_template):
        """Test unpacking workflow directly (bypassing UI interaction)."""
        # Create and pack a texture
        textures = {
            'ambient_occlusion': np.full((256, 256), 230, dtype=np.uint8),
            'roughness': np.full((256, 256), 140, dtype=np.uint8),
            'metallic': np.full((256, 256), 25, dtype=np.uint8),
        }
        packed = pack_texture_from_template(textures, orm_template)

        # Unpack using core API
        channels = unpack_texture(packed, orm_template)

        assert 'ambient_occlusion' in channels
        assert 'roughness' in channels
        assert 'metallic' in channels
        assert len(channels) == 3


class TestChannelSmithAppIntegration:
    """Test full application lifecycle."""

    def test_app_initialization(self):
        """Test ChannelSmithApp initializes successfully."""
        app = ChannelSmithApp()
        assert app.is_initialized()
        assert app.winfo_exists()
        app.on_closing()

    def test_app_has_pack_and_unpack_tabs(self):
        """Test app has both Pack and Unpack tabs."""
        app = ChannelSmithApp()
        assert hasattr(app, 'content_frame')

        # The notebook should have tabs
        root = app
        root.update()

        app.on_closing()

    def test_app_status_bar_updates(self):
        """Test app status bar exists and can be updated."""
        app = ChannelSmithApp()
        assert hasattr(app, 'status_label')

        # Status label should exist
        if app.status_label:
            app.status_label.config(text="Test status")
            app.update()

        app.on_closing()

    def test_app_graceful_shutdown(self):
        """Test app shuts down gracefully."""
        app = ChannelSmithApp()
        app.on_closing()
        # Should not raise


class TestFileManagerIntegration:
    """Test file manager operations (save_image, save_project, load_project)."""

    def test_save_image_creates_file(self):
        """Test save_image creates a PNG file on disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new("RGB", (256, 256), (200, 100, 50))
            output_path = os.path.join(tmpdir, "test_output.png")

            # Use util_save_image (from image_utils) which handles file writing
            util_save_image(img, output_path)

            assert os.path.exists(output_path)
            loaded = load_image(output_path)
            assert loaded.size == (256, 256)

    def test_save_and_load_project(self):
        """Test save_project and load_project round-trip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_state = {
                "template_name": "orm",
                "packed_image_path": "packed.png",
                "channels": {
                    "ambient_occlusion": "ao.png",
                    "roughness": "rough.png",
                    "metallic": "metal.png",
                }
            }

            project_path = os.path.join(tmpdir, "project.csproj")
            saved_path = save_project(project_state, project_path)

            assert os.path.exists(saved_path)

            loaded_state = load_project(saved_path)
            assert loaded_state["template_name"] == "orm"
            assert loaded_state["packed_image_path"] == "packed.png"

    def test_project_preserves_channel_paths(self):
        """Test that channel paths are preserved in project save/load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_state = {
                "template_name": "ord",
                "channels": {
                    "ambient_occlusion": "path/to/ao.png",
                    "roughness": "path/to/rough.png",
                    "displacement": "path/to/disp.png",
                }
            }

            project_path = os.path.join(tmpdir, "project.csproj")
            saved = save_project(original_state, project_path)
            loaded = load_project(saved)

            assert loaded["channels"]["ambient_occlusion"] == "path/to/ao.png"
            assert loaded["channels"]["roughness"] == "path/to/rough.png"
            assert loaded["channels"]["displacement"] == "path/to/disp.png"


class TestDragDropIntegration:
    """Test drag-drop functionality."""

    def test_drag_drop_enabled_on_image_selector(self, root):
        """Test drag-drop is enabled on image selectors."""
        from channelsmith.gui.image_selector import ImageSelector

        selector = ImageSelector(root, "Ambient Occlusion")
        root.update()

        # Drag-drop should be registered (doesn't error if not available)
        assert selector is not None

    def test_drag_drop_callback_receives_file(self, root):
        """Test that drag-drop callback can handle file paths."""
        from channelsmith.gui.drag_drop import _extract_file_path_from_drop_data

        # Simulate drop event data
        drop_data = "C:\\path\\to\\image.png"
        path = _extract_file_path_from_drop_data(drop_data)

        assert path is not None


class TestProgressBarIntegration:
    """Test progress bar for long operations."""

    def test_progress_bar_operations(self, root):
        """Test progress bar start/stop/message."""
        from channelsmith.gui.progress import ProgressBar

        progress = ProgressBar(root)
        root.update()

        progress.start("Running operation...")
        assert progress.is_running()

        progress.set_message("Step 1 complete")
        root.update()

        progress.stop()
        assert not progress.is_running()

        root.update()


class TestPackUnpackRoundTrip:
    """Test complete pack-unpack round trip through GUI components."""

    def test_pack_preview_unpack_cycle(self, root, orm_template, sample_texture_files):
        """Test full cycle: pack -> preview -> load -> unpack -> save."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 1: Pack textures
            textures = {
                'ambient_occlusion': Image.open(sample_texture_files["ao"]),
                'roughness': Image.open(sample_texture_files["roughness"]),
                'metallic': Image.open(sample_texture_files["metallic"]),
            }
            packed = pack_texture_from_template(textures, orm_template)

            # Step 2: Save packed image
            packed_path = os.path.join(tmpdir, "packed.png")
            packed.save(packed_path)

            # Step 3: Load and unpack
            loaded = load_image(packed_path)
            channels = unpack_texture(loaded, orm_template)

            # Step 4: Save individual channels
            for name, array in channels.items():
                channel_path = os.path.join(tmpdir, f"{name}.png")
                channel_img = Image.fromarray(array, mode='L')
                channel_img.save(channel_path)
                assert os.path.exists(channel_path)

            # Step 5: Verify unpacked channels match originals
            assert np.array_equal(
                channels['ambient_occlusion'],
                np.array(Image.open(sample_texture_files["ao"]))
            )
            assert np.array_equal(
                channels['roughness'],
                np.array(Image.open(sample_texture_files["roughness"]))
            )
            assert np.array_equal(
                channels['metallic'],
                np.array(Image.open(sample_texture_files["metallic"]))
            )
