"""
Tests for PackerPanel widget.

Task B5: Test texture packing panel functionality
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
    from channelsmith.gui.packer_panel import PackerPanel
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
def packer_panel(root):
    """Create a PackerPanel widget."""
    panel = PackerPanel(root)
    panel.pack()
    root.update()
    return panel


@pytest.fixture
def test_image():
    """Create a temporary test image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        img = Image.new("RGB", (256, 256), color="gray")
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


class TestPackerPanelInitialization:
    """Tests for PackerPanel initialization."""

    def test_initialization(self, packer_panel):
        """Test PackerPanel initializes with correct widgets."""
        assert packer_panel._template_selector is not None
        assert packer_panel._ao_selector is not None
        assert packer_panel._roughness_selector is not None
        assert packer_panel._metallic_selector is not None
        assert packer_panel._preview_panel is not None
        assert packer_panel._pack_btn is not None

    def test_widget_types(self, packer_panel):
        """Test all widgets have correct types."""
        assert isinstance(packer_panel._template_selector, tk.Frame)
        assert isinstance(packer_panel._ao_selector, tk.Frame)
        assert isinstance(packer_panel._roughness_selector, tk.Frame)
        assert isinstance(packer_panel._metallic_selector, tk.Frame)
        assert isinstance(packer_panel._preview_panel, tk.Frame)
        assert isinstance(packer_panel._pack_btn, tk.Button)

    def test_selector_channel_names(self, packer_panel):
        """Test image selectors have correct channel names."""
        assert packer_panel._ao_selector._channel_name == "Ambient Occlusion"
        assert packer_panel._roughness_selector._channel_name == "Roughness"
        assert packer_panel._metallic_selector._channel_name == "Metallic"


class TestPackerPanelPacking:
    """Tests for texture packing functionality."""

    @patch("channelsmith.gui.packer_panel.load_template")
    @patch("channelsmith.gui.packer_panel.pack_texture_from_template")
    def test_pack_with_no_images(self, mock_pack, mock_load, packer_panel, orm_template):
        """Test packing with no images selected (uses defaults)."""
        mock_load.return_value = orm_template
        mock_pack.return_value = Image.new("RGB", (256, 256), color="gray")

        packer_panel._on_pack()

        # Should call pack with None values
        assert mock_pack.called
        call_args = mock_pack.call_args[0]
        textures_dict = call_args[0]
        assert textures_dict["ambient_occlusion"] is None
        assert textures_dict["roughness"] is None
        assert textures_dict["metallic"] is None

    @patch("channelsmith.gui.packer_panel.load_template")
    @patch("channelsmith.gui.packer_panel.pack_texture_from_template")
    def test_pack_with_images(self, mock_pack, mock_load, packer_panel,
                             orm_template, test_image):
        """Test packing with all three images selected."""
        mock_load.return_value = orm_template
        packed_img = Image.new("RGB", (256, 256), color="gray")
        mock_pack.return_value = packed_img

        # Load images
        packer_panel._ao_selector._load_image(test_image)
        packer_panel._roughness_selector._load_image(test_image)
        packer_panel._metallic_selector._load_image(test_image)

        packer_panel._on_pack()

        # Should call pack with image objects
        assert mock_pack.called
        call_args = mock_pack.call_args[0]
        textures_dict = call_args[0]
        assert textures_dict["ambient_occlusion"] is not None
        assert textures_dict["roughness"] is not None
        assert textures_dict["metallic"] is not None

    @patch("channelsmith.gui.packer_panel.load_template")
    @patch("channelsmith.gui.packer_panel.pack_texture_from_template")
    def test_preview_updates_after_pack(self, mock_pack, mock_load, packer_panel,
                                       orm_template, test_image):
        """Test that preview panel shows result after packing."""
        mock_load.return_value = orm_template
        packed_img = Image.new("RGB", (256, 256), color=(255, 128, 0))
        mock_pack.return_value = packed_img

        packer_panel._ao_selector._load_image(test_image)

        packer_panel._on_pack()

        # Preview should be updated with packed image
        assert mock_pack.called
        # The preview panel's show_image should have been called
        assert packer_panel._preview_panel._photo is not None

    @patch("channelsmith.gui.packer_panel.messagebox.showerror")
    @patch("channelsmith.gui.packer_panel.load_template")
    def test_pack_with_invalid_template(self, mock_load, mock_error, packer_panel):
        """Test error handling with invalid template."""
        mock_load.side_effect = FileNotFoundError("Template not found")

        packer_panel._on_pack()

        # Should show error dialog
        assert mock_error.called
        assert "Template Error" in str(mock_error.call_args)

    @patch("channelsmith.gui.packer_panel.messagebox.showerror")
    @patch("channelsmith.gui.packer_panel.load_template")
    @patch("channelsmith.gui.packer_panel.pack_texture_from_template")
    def test_pack_with_packing_error(self, mock_pack, mock_load, mock_error,
                                    packer_panel, orm_template):
        """Test error handling when packing fails."""
        mock_load.return_value = orm_template
        mock_pack.side_effect = ValueError("Invalid texture data")

        packer_panel._on_pack()

        # Should show error dialog
        assert mock_error.called
        assert "Packing Error" in str(mock_error.call_args)


class TestPackerPanelIntegration:
    """Integration tests for PackerPanel."""

    def test_multiple_packing_operations(self, packer_panel, test_image):
        """Test performing multiple pack operations in sequence."""
        # First pack (with no images)
        with patch("channelsmith.gui.packer_panel.load_template") as mock_load, \
             patch("channelsmith.gui.packer_panel.pack_texture_from_template") as mock_pack:
            mock_load.return_value = PackingTemplate(
                name="ORM",
                description="Test",
                channels={
                    "R": ChannelMap("ambient_occlusion", 1.0),
                    "G": ChannelMap("roughness", 0.5),
                    "B": ChannelMap("metallic", 0.0),
                }
            )
            mock_pack.return_value = Image.new("RGB", (256, 256))
            packer_panel._on_pack()
            assert mock_pack.call_count == 1

        # Second pack (with images)
        with patch("channelsmith.gui.packer_panel.load_template") as mock_load, \
             patch("channelsmith.gui.packer_panel.pack_texture_from_template") as mock_pack:
            mock_load.return_value = PackingTemplate(
                name="ORM",
                description="Test",
                channels={
                    "R": ChannelMap("ambient_occlusion", 1.0),
                    "G": ChannelMap("roughness", 0.5),
                    "B": ChannelMap("metallic", 0.0),
                }
            )
            mock_pack.return_value = Image.new("RGB", (256, 256))
            packer_panel._ao_selector._load_image(test_image)
            packer_panel._on_pack()
            assert mock_pack.called

    def test_widget_independence(self, root):
        """Test multiple PackerPanel instances work independently."""
        panel1 = PackerPanel(root)
        panel2 = PackerPanel(root)
        panel1.pack()
        panel2.pack()
        root.update()

        assert panel1._ao_selector is not panel2._ao_selector
        assert panel1._preview_panel is not panel2._preview_panel

    def test_pack_button_state(self, packer_panel):
        """Test pack button is enabled."""
        # Pack button should always be enabled
        assert packer_panel._pack_btn.cget("state") in ("normal", "")


class TestPackerPanelEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_pack_with_different_resolution_images(self, packer_panel, root):
        """Test packing images with different resolutions."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f1, \
             tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f2:
            img1 = Image.new("RGB", (256, 256), color="gray")
            img2 = Image.new("RGB", (512, 512), color="white")
            img1.save(f1.name)
            img2.save(f2.name)
            path1, path2 = f1.name, f2.name

        try:
            packer_panel._ao_selector._load_image(path1)
            packer_panel._roughness_selector._load_image(path2)

            with patch("channelsmith.gui.packer_panel.load_template") as mock_load, \
                 patch("channelsmith.gui.packer_panel.pack_texture_from_template") as mock_pack:
                mock_load.return_value = PackingTemplate(
                    name="ORM",
                    description="Test",
                    channels={
                        "R": ChannelMap("ambient_occlusion", 1.0),
                        "G": ChannelMap("roughness", 0.5),
                        "B": ChannelMap("metallic", 0.0),
                    }
                )
                mock_pack.return_value = Image.new("RGB", (512, 512))
                packer_panel._on_pack()
                assert mock_pack.called
        finally:
            gc.collect()
            try:
                Path(path1).unlink()
                Path(path2).unlink()
            except PermissionError:
                pass

    def test_pack_with_single_image(self, packer_panel, test_image):
        """Test packing with only one image selected."""
        packer_panel._ao_selector._load_image(test_image)

        with patch("channelsmith.gui.packer_panel.load_template") as mock_load, \
             patch("channelsmith.gui.packer_panel.pack_texture_from_template") as mock_pack:
            mock_load.return_value = PackingTemplate(
                name="ORM",
                description="Test",
                channels={
                    "R": ChannelMap("ambient_occlusion", 1.0),
                    "G": ChannelMap("roughness", 0.5),
                    "B": ChannelMap("metallic", 0.0),
                }
            )
            mock_pack.return_value = Image.new("RGB", (256, 256))
            packer_panel._on_pack()

            # Should have packed with one image and None for others
            call_args = mock_pack.call_args[0]
            textures_dict = call_args[0]
            assert textures_dict["ambient_occlusion"] is not None
            assert textures_dict["roughness"] is None
            assert textures_dict["metallic"] is None

    @patch("channelsmith.gui.packer_panel.messagebox.showerror")
    def test_error_handling_graceful(self, mock_error, packer_panel):
        """Test that errors are handled gracefully without crashing."""
        with patch("channelsmith.gui.packer_panel.load_template") as mock_load:
            mock_load.side_effect = Exception("Unexpected error")
            packer_panel._on_pack()
            assert mock_error.called


class TestPackerPanelConstants:
    """Tests for widget constants and defaults."""

    def test_preview_panel_label(self, packer_panel):
        """Test preview panel has correct label."""
        # Get the label text from preview panel
        labels = [child for child in packer_panel._preview_panel.winfo_children()
                  if isinstance(child, tk.Label)]
        assert any("Packed" in child.cget("text") for child in labels)

    def test_pack_button_label(self, packer_panel):
        """Test pack button has correct label."""
        assert packer_panel._pack_btn.cget("text") == "Pack Texture"
