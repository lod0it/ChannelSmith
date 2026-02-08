"""
Tests for UnpackerPanel widget.

Task B6: Test texture unpacking panel functionality
"""

import tkinter as tk
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import gc

# Skip all GUI tests if tkinter is not available
pytestmark = pytest.mark.skipif(
    not hasattr(tk, "Tk"),
    reason="tkinter not available"
)

try:
    from channelsmith.gui.unpacker_panel import UnpackerPanel
    from channelsmith.core.packing_template import PackingTemplate
    from channelsmith.core.channel_map import ChannelMap
    from PIL import Image
    import numpy as np
    HAS_TKINTER = True
except Exception:
    HAS_TKINTER = False


@pytest.fixture
def root():
    """Create a test root window."""
    try:
        root = tk.Tk()
        yield root
        root.destroy()
    except Exception as e:
        pytest.skip(f"Could not create tk.Tk: {e}")


@pytest.fixture
def unpacker_panel(root):
    """Create an UnpackerPanel widget."""
    panel = UnpackerPanel(root)
    panel.pack()
    root.update()
    return panel


@pytest.fixture
def packed_image():
    """Create a test packed image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img = Image.new("RGB", (256, 256), color=(255, 128, 0))
        img.save(f.name)
        temp_path = f.name

    yield temp_path

    # Cleanup
    gc.collect()
    try:
        Path(temp_path).unlink()
    except PermissionError:
        pass


@pytest.fixture
def orm_template():
    """Create a test ORM template."""
    return PackingTemplate(
        name="ORM",
        description="Occlusion-Roughness-Metallic",
        channels={
            "R": ChannelMap("ambient_occlusion", 1.0),
            "G": ChannelMap("roughness", 0.5),
            "B": ChannelMap("metallic", 0.0),
        }
    )


class TestUnpackerPanelInitialization:
    """Tests for UnpackerPanel initialization."""

    def test_initialization(self, unpacker_panel):
        """Test UnpackerPanel initializes with correct widgets."""
        assert unpacker_panel._template_selector is not None
        assert unpacker_panel._preview_panel is not None
        assert unpacker_panel._status_label is not None
        # Should have buttons for each non-None channel in the template
        assert len(unpacker_panel._save_buttons) > 0

    def test_initial_state(self, unpacker_panel):
        """Test UnpackerPanel initial state."""
        assert unpacker_panel._packed_image is None
        assert unpacker_panel._unpacked_channels == {}

    def test_save_buttons_initial_state(self, unpacker_panel):
        """Test all save buttons are disabled initially."""
        for btn in unpacker_panel._save_buttons.values():
            assert btn.cget("state") == "disabled"

    def test_status_label_initial_text(self, unpacker_panel):
        """Test status label shows initial message."""
        assert "No image loaded" in unpacker_panel._status_label.cget("text")


class TestUnpackerPanelLoading:
    """Tests for image loading functionality."""

    @patch("channelsmith.gui.unpacker_panel.filedialog.askopenfilename")
    @patch("channelsmith.gui.unpacker_panel.load_image")
    @patch("channelsmith.gui.unpacker_panel.unpack_texture")
    def test_load_packed_image(self, mock_unpack, mock_load_img, mock_dialog,
                               unpacker_panel, orm_template):
        """Test loading a packed image."""
        mock_dialog.return_value = "/path/to/image.png"
        test_img = Image.new("RGB", (256, 256), color="gray")
        mock_load_img.return_value = test_img
        mock_unpack.return_value = {
            "ambient_occlusion": np.ones((256, 256), dtype=np.uint8) * 255,
            "roughness": np.ones((256, 256), dtype=np.uint8) * 128,
            "metallic": np.zeros((256, 256), dtype=np.uint8),
        }

        with patch("channelsmith.gui.unpacker_panel.load_template") as mock_load:
            mock_load.return_value = orm_template
            unpacker_panel._on_load_packed()

        assert unpacker_panel._packed_image == test_img
        assert len(unpacker_panel._unpacked_channels) == 3

    @patch("channelsmith.gui.unpacker_panel.filedialog.askopenfilename")
    def test_load_cancelled(self, mock_dialog, unpacker_panel):
        """Test cancelling file dialog."""
        mock_dialog.return_value = ""
        unpacker_panel._on_load_packed()
        assert unpacker_panel._packed_image is None

    @patch("channelsmith.gui.unpacker_panel.messagebox.showerror")
    @patch("channelsmith.gui.unpacker_panel.filedialog.askopenfilename")
    @patch("channelsmith.gui.unpacker_panel.load_image")
    def test_load_image_error(self, mock_load_img, mock_dialog, mock_error,
                             unpacker_panel):
        """Test error handling when loading fails."""
        mock_dialog.return_value = "/path/to/invalid.png"
        mock_load_img.side_effect = Exception("Invalid image file")

        unpacker_panel._on_load_packed()

        assert mock_error.called
        assert "Load Error" in str(mock_error.call_args)
        assert unpacker_panel._packed_image is None


class TestUnpackerPanelUnpacking:
    """Tests for texture unpacking functionality."""

    @patch("channelsmith.gui.unpacker_panel.load_template")
    @patch("channelsmith.gui.unpacker_panel.unpack_texture")
    def test_unpack_with_all_channels(self, mock_unpack, mock_load, unpacker_panel,
                                     orm_template):
        """Test unpacking texture with all channels."""
        unpacker_panel._packed_image = Image.new("RGB", (256, 256))
        mock_load.return_value = orm_template
        mock_unpack.return_value = {
            "ambient_occlusion": np.ones((256, 256), dtype=np.uint8) * 255,
            "roughness": np.ones((256, 256), dtype=np.uint8) * 128,
            "metallic": np.zeros((256, 256), dtype=np.uint8),
        }

        unpacker_panel._on_unpack()

        assert len(unpacker_panel._unpacked_channels) == 3
        assert "ambient_occlusion" in unpacker_panel._unpacked_channels
        assert "roughness" in unpacker_panel._unpacked_channels
        assert "metallic" in unpacker_panel._unpacked_channels

    @patch("channelsmith.gui.unpacker_panel.messagebox.showerror")
    @patch("channelsmith.gui.unpacker_panel.load_template")
    def test_unpack_error(self, mock_load, mock_error, unpacker_panel):
        """Test error handling when unpacking fails."""
        unpacker_panel._packed_image = Image.new("RGB", (256, 256))
        mock_load.side_effect = FileNotFoundError("Template not found")

        unpacker_panel._on_unpack()

        assert mock_error.called
        assert "Unpack Error" in str(mock_error.call_args)


class TestUnpackerPanelSaving:
    """Tests for channel saving functionality."""

    @patch("channelsmith.gui.unpacker_panel.filedialog.asksaveasfilename")
    @patch("channelsmith.gui.unpacker_panel.save_image")
    @patch("channelsmith.gui.unpacker_panel.messagebox.showinfo")
    def test_save_channel(self, mock_info, mock_save, mock_dialog, unpacker_panel):
        """Test saving a single channel."""
        mock_dialog.return_value = "/path/to/ao.png"
        unpacker_panel._unpacked_channels = {
            "ambient_occlusion": np.ones((256, 256), dtype=np.uint8) * 255,
        }

        unpacker_panel._on_save_channel("ambient_occlusion")

        assert mock_save.called
        assert mock_info.called

    @patch("channelsmith.gui.unpacker_panel.messagebox.showwarning")
    def test_save_unavailable_channel(self, mock_warning, unpacker_panel):
        """Test saving a channel that is not available."""
        unpacker_panel._unpacked_channels = {}
        unpacker_panel._on_save_channel("ambient_occlusion")

        assert mock_warning.called
        assert "not available" in str(mock_warning.call_args).lower()

    @patch("channelsmith.gui.unpacker_panel.filedialog.asksaveasfilename")
    def test_save_cancelled(self, mock_dialog, unpacker_panel):
        """Test cancelling save file dialog."""
        mock_dialog.return_value = ""
        unpacker_panel._unpacked_channels = {
            "ambient_occlusion": np.ones((256, 256), dtype=np.uint8),
        }

        with patch("channelsmith.gui.unpacker_panel.save_image") as mock_save:
            unpacker_panel._on_save_channel("ambient_occlusion")
            assert not mock_save.called

    @patch("channelsmith.gui.unpacker_panel.messagebox.showerror")
    @patch("channelsmith.gui.unpacker_panel.filedialog.asksaveasfilename")
    @patch("channelsmith.gui.unpacker_panel.save_image")
    def test_save_error(self, mock_save, mock_dialog, mock_error, unpacker_panel):
        """Test error handling when saving fails."""
        mock_dialog.return_value = "/path/to/ao.png"
        unpacker_panel._unpacked_channels = {
            "ambient_occlusion": np.ones((256, 256), dtype=np.uint8),
        }
        mock_save.side_effect = Exception("Failed to save")

        unpacker_panel._on_save_channel("ambient_occlusion")

        assert mock_error.called
        assert "Save Error" in str(mock_error.call_args)


class TestUnpackerPanelSaveButtons:
    """Tests for save button state management."""

    def test_save_buttons_enabled_for_available_channels(self, unpacker_panel):
        """Test save buttons are enabled only for available channels."""
        unpacker_panel._unpacked_channels = {
            "ambient_occlusion": np.ones((256, 256), dtype=np.uint8),
            "roughness": np.ones((256, 256), dtype=np.uint8),
        }

        unpacker_panel._update_save_buttons()

        # Check that available channels have enabled buttons
        assert unpacker_panel._save_buttons["ambient_occlusion"].cget("state") == "normal"
        assert unpacker_panel._save_buttons["roughness"].cget("state") == "normal"

        # Check that unavailable channels (if they exist as buttons) have disabled buttons
        for channel, btn in unpacker_panel._save_buttons.items():
            if channel in unpacker_panel._unpacked_channels:
                assert btn.cget("state") == "normal"
            else:
                assert btn.cget("state") == "disabled"

    def test_all_buttons_disabled_when_no_channels(self, unpacker_panel):
        """Test all save buttons are disabled when no channels."""
        unpacker_panel._unpacked_channels = {}
        unpacker_panel._update_save_buttons()

        for btn in unpacker_panel._save_buttons.values():
            assert btn.cget("state") == "disabled"

    def test_status_label_updated(self, unpacker_panel):
        """Test status label is updated with channel information."""
        unpacker_panel._unpacked_channels = {
            "ambient_occlusion": np.ones((256, 256), dtype=np.uint8),
        }
        unpacker_panel._update_save_buttons()

        status_text = unpacker_panel._status_label.cget("text")
        assert "Ambient" in status_text or "ambient" in status_text.lower()


class TestUnpackerPanelIntegration:
    """Integration tests for UnpackerPanel."""

    def test_load_and_save_workflow(self, unpacker_panel, packed_image, orm_template):
        """Test complete load-unpack-save workflow."""
        with patch("channelsmith.gui.unpacker_panel.load_image") as mock_load_img, \
             patch("channelsmith.gui.unpacker_panel.load_template") as mock_load_tmpl, \
             patch("channelsmith.gui.unpacker_panel.unpack_texture") as mock_unpack, \
             patch("channelsmith.gui.unpacker_panel.filedialog.askopenfilename") as mock_dialog:

            mock_dialog.return_value = packed_image
            test_img = Image.new("RGB", (256, 256))
            mock_load_img.return_value = test_img
            mock_load_tmpl.return_value = orm_template
            mock_unpack.return_value = {
                "ambient_occlusion": np.ones((256, 256), dtype=np.uint8) * 255,
            }

            unpacker_panel._on_load_packed()

            assert unpacker_panel._packed_image is not None
            assert len(unpacker_panel._unpacked_channels) == 1

    def test_widget_independence(self, root):
        """Test multiple UnpackerPanel instances work independently."""
        panel1 = UnpackerPanel(root)
        panel2 = UnpackerPanel(root)
        panel1.pack()
        panel2.pack()
        root.update()

        assert panel1._preview_panel is not panel2._preview_panel
        assert panel1._unpacked_channels is not panel2._unpacked_channels

    def test_reload_with_different_image(self, unpacker_panel, packed_image,
                                        orm_template):
        """Test reloading with a different image."""
        with patch("channelsmith.gui.unpacker_panel.load_image") as mock_load_img, \
             patch("channelsmith.gui.unpacker_panel.load_template") as mock_load_tmpl, \
             patch("channelsmith.gui.unpacker_panel.unpack_texture") as mock_unpack, \
             patch("channelsmith.gui.unpacker_panel.filedialog.askopenfilename") as mock_dialog:

            mock_load_tmpl.return_value = orm_template

            # First load
            mock_dialog.return_value = packed_image
            img1 = Image.new("RGB", (256, 256), color="gray")
            mock_load_img.return_value = img1
            mock_unpack.return_value = {
                "ambient_occlusion": np.ones((256, 256), dtype=np.uint8) * 255,
            }
            unpacker_panel._on_load_packed()
            assert unpacker_panel._packed_image == img1

            # Second load (different image)
            img2 = Image.new("RGB", (512, 512), color="white")
            mock_load_img.return_value = img2
            unpacker_panel._on_load_packed()
            assert unpacker_panel._packed_image == img2


class TestUnpackerPanelEdgeCases:
    """Tests for edge cases and error conditions."""

    @patch("channelsmith.gui.unpacker_panel.load_template")
    @patch("channelsmith.gui.unpacker_panel.unpack_texture")
    def test_unpack_rgba_image(self, mock_unpack, mock_load, unpacker_panel,
                              orm_template):
        """Test unpacking an RGBA image."""
        unpacker_panel._packed_image = Image.new("RGBA", (256, 256))
        mock_load.return_value = orm_template
        mock_unpack.return_value = {
            "ambient_occlusion": np.ones((256, 256), dtype=np.uint8) * 255,
            "roughness": np.ones((256, 256), dtype=np.uint8) * 128,
            "metallic": np.zeros((256, 256), dtype=np.uint8),
            "alpha": np.ones((256, 256), dtype=np.uint8) * 255,
        }

        unpacker_panel._on_unpack()

        assert len(unpacker_panel._unpacked_channels) == 4
        assert "alpha" in unpacker_panel._unpacked_channels

    def test_save_channel_array_to_image(self, unpacker_panel):
        """Test converting channel arrays to images for saving."""
        unpacker_panel._unpacked_channels = {
            "ambient_occlusion": np.ones((256, 256), dtype=np.uint8) * 255,
        }

        with patch("channelsmith.gui.unpacker_panel.filedialog.asksaveasfilename") as mock_dialog, \
             patch("channelsmith.gui.unpacker_panel.save_image") as mock_save:
            mock_dialog.return_value = "/path/to/ao.png"
            unpacker_panel._on_save_channel("ambient_occlusion")

            # Check that from_grayscale was used and save_image was called
            assert mock_save.called
            call_args = mock_save.call_args[0]
            saved_img = call_args[0]
            assert isinstance(saved_img, Image.Image)

    @patch("channelsmith.gui.unpacker_panel.messagebox.showerror")
    @patch("channelsmith.gui.unpacker_panel.filedialog.askopenfilename")
    @patch("channelsmith.gui.unpacker_panel.load_image")
    def test_graceful_error_recovery(self, mock_load_img, mock_dialog, mock_error,
                                    unpacker_panel):
        """Test graceful recovery from errors."""
        mock_dialog.return_value = "/path/to/image.png"
        mock_load_img.side_effect = Exception("Load failed")

        unpacker_panel._on_load_packed()

        # Panel should be in clean state
        assert unpacker_panel._packed_image is None
        assert unpacker_panel._unpacked_channels == {}
        assert all(btn.cget("state") == "disabled"
                  for btn in unpacker_panel._save_buttons.values())


class TestUnpackerPanelConstants:
    """Tests for widget constants and defaults."""

    def test_preview_panel_label(self, unpacker_panel):
        """Test preview panel has correct label."""
        labels = [child for child in unpacker_panel._preview_panel.winfo_children()
                  if isinstance(child, tk.Label)]
        assert any("Packed" in child.cget("text") for child in labels)

    def test_save_button_labels(self, unpacker_panel):
        """Test save buttons have correct RGB/A labels."""
        # Check that buttons exist for template channels
        assert "ambient_occlusion" in unpacker_panel._save_buttons
        assert "roughness" in unpacker_panel._save_buttons

        # Get the template to check which RGB channels should have buttons
        template = unpacker_panel._current_template
        expected_channel_keys = ["R", "G", "B", "A"]
        button_count = 0

        # Verify buttons match template structure
        for channel_key in expected_channel_keys:
            if template.channels.get(channel_key) is not None:
                button_count += 1

        assert len(unpacker_panel._save_buttons) == button_count

        # Verify label format is "Export R", "Export G", "Export B", "Export A"
        for channel_type, btn in unpacker_panel._save_buttons.items():
            text = btn.cget("text")
            assert text.startswith("Export ") and text[7] in "RGBA"
