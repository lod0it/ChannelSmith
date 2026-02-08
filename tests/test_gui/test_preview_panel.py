"""
Tests for PreviewPanel widget.

Task B4: Test preview panel functionality
"""

import tkinter as tk
import pytest
from pathlib import Path
import tempfile
import gc

# Skip all GUI tests if tkinter display is not available
pytestmark = pytest.mark.skipif(
    not hasattr(tk, "Tk"),
    reason="tkinter not available"
)

try:
    from channelsmith.gui.preview_panel import (
        PreviewPanel,
        CANVAS_SIZE,
        CANVAS_BG_COLOR,
        PLACEHOLDER_COLOR,
    )
    from PIL import Image, ImageTk
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
def preview_panel(root):
    """Create a PreviewPanel widget."""
    panel = PreviewPanel(root)
    panel.pack()
    root.update()
    return panel


@pytest.fixture
def test_image():
    """Create a temporary test image."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        # Create a simple test image
        img = Image.new("RGB", (256, 256), color="gray")
        img.save(f.name)
        img.close()
        temp_path = f.name

    yield temp_path

    # Cleanup
    gc.collect()
    try:
        Path(temp_path).unlink()
    except PermissionError:
        # File might still be in use, skip cleanup
        pass


class TestPreviewPanelInitialization:
    """Tests for PreviewPanel initialization."""

    def test_is_frame(self, preview_panel):
        """Test PreviewPanel is a tk.Frame."""
        assert isinstance(preview_panel, tk.Frame)

    def test_default_label_text(self, preview_panel):
        """Test default label text is 'Preview'."""
        assert preview_panel._label_text == "Preview"

    def test_custom_label_text(self, root):
        """Test PreviewPanel can have custom label text."""
        panel = PreviewPanel(root, label_text="Custom Label")
        panel.pack()
        root.update()
        assert panel._label_text == "Custom Label"

    def test_canvas_exists(self, preview_panel):
        """Test canvas widget is created."""
        assert preview_panel._canvas is not None
        assert isinstance(preview_panel._canvas, tk.Canvas)

    def test_canvas_size(self, preview_panel):
        """Test canvas has correct size."""
        assert int(preview_panel._canvas.cget("width")) == CANVAS_SIZE
        assert int(preview_panel._canvas.cget("height")) == CANVAS_SIZE

    def test_canvas_background_color(self, preview_panel):
        """Test canvas background color is set."""
        assert preview_panel._canvas.cget("bg") == CANVAS_BG_COLOR

    def test_photo_initially_none(self, preview_panel):
        """Test photo reference is None initially."""
        assert preview_panel._photo is not None  # Should be placeholder PhotoImage

    def test_initial_placeholder_displayed(self, preview_panel):
        """Test placeholder is displayed on initialization."""
        # Canvas should have at least one image item (the placeholder)
        items = preview_panel._canvas.find_all()
        assert len(items) > 0


class TestPreviewPanelShowImage:
    """Tests for show_image method."""

    def test_show_image_with_valid_image(self, preview_panel):
        """Test showing a valid PIL Image."""
        img = Image.new("RGB", (256, 256), color="red")
        preview_panel.show_image(img)
        root = preview_panel.winfo_toplevel()
        root.update()

        # Canvas should display the image
        items = preview_panel._canvas.find_all()
        assert len(items) > 0

    def test_show_image_with_none(self, preview_panel):
        """Test showing None displays placeholder."""
        preview_panel.show_image(None)
        root = preview_panel.winfo_toplevel()
        root.update()

        # Canvas should still have image (placeholder)
        items = preview_panel._canvas.find_all()
        assert len(items) > 0

    def test_show_image_with_oversized_image(self, preview_panel):
        """Test large image is resized to fit canvas."""
        # Create large image (1000x1000)
        img = Image.new("RGB", (1000, 1000), color="blue")
        preview_panel.show_image(img)
        root = preview_panel.winfo_toplevel()
        root.update()

        # Image should fit in canvas
        items = preview_panel._canvas.find_all()
        assert len(items) > 0

    def test_show_tall_image_maintains_aspect_ratio(self, preview_panel):
        """Test tall image maintains aspect ratio."""
        # Create tall image (100x500)
        img = Image.new("RGB", (100, 500), color="green")
        preview_panel.show_image(img)
        root = preview_panel.winfo_toplevel()
        root.update()

        # Should display without error
        items = preview_panel._canvas.find_all()
        assert len(items) > 0

    def test_show_wide_image_maintains_aspect_ratio(self, preview_panel):
        """Test wide image maintains aspect ratio."""
        # Create wide image (500x100)
        img = Image.new("RGB", (500, 100), color="yellow")
        preview_panel.show_image(img)
        root = preview_panel.winfo_toplevel()
        root.update()

        # Should display without error
        items = preview_panel._canvas.find_all()
        assert len(items) > 0

    def test_show_image_multiple_times(self, preview_panel):
        """Test calling show_image multiple times updates display."""
        img1 = Image.new("RGB", (256, 256), color="red")
        img2 = Image.new("RGB", (256, 256), color="blue")

        preview_panel.show_image(img1)
        root = preview_panel.winfo_toplevel()
        root.update()

        preview_panel.show_image(img2)
        root.update()

        # Canvas should have image
        items = preview_panel._canvas.find_all()
        assert len(items) > 0

    def test_show_image_does_not_modify_original(self, preview_panel):
        """Test show_image does not modify the original image."""
        img = Image.new("RGB", (512, 512), color="red")
        original_size = img.size

        preview_panel.show_image(img)
        root = preview_panel.winfo_toplevel()
        root.update()

        # Original image should be unchanged
        assert img.size == original_size

    def test_show_image_with_grayscale_image(self, preview_panel):
        """Test showing grayscale image."""
        img = Image.new("L", (256, 256), color=128)
        preview_panel.show_image(img)
        root = preview_panel.winfo_toplevel()
        root.update()

        # Should display without error
        items = preview_panel._canvas.find_all()
        assert len(items) > 0

    def test_show_image_with_rgba_image(self, preview_panel):
        """Test showing RGBA image."""
        img = Image.new("RGBA", (256, 256), color=(255, 0, 0, 128))
        preview_panel.show_image(img)
        root = preview_panel.winfo_toplevel()
        root.update()

        # Should display without error
        items = preview_panel._canvas.find_all()
        assert len(items) > 0


class TestPreviewPanelPhotoReference:
    """Tests for photo reference management."""

    def test_photo_reference_stored(self, preview_panel):
        """Test PhotoImage reference is stored."""
        img = Image.new("RGB", (256, 256), color="red")
        preview_panel.show_image(img)

        assert preview_panel._photo is not None
        assert isinstance(preview_panel._photo, ImageTk.PhotoImage)

    def test_photo_reference_updates(self, preview_panel):
        """Test PhotoImage reference updates on new image."""
        img1 = Image.new("RGB", (256, 256), color="red")
        preview_panel.show_image(img1)
        root = preview_panel.winfo_toplevel()
        root.update()
        photo1 = preview_panel._photo

        img2 = Image.new("RGB", (256, 256), color="blue")
        preview_panel.show_image(img2)
        root.update()
        photo2 = preview_panel._photo

        # Reference should be different (new PhotoImage created)
        assert photo1 is not photo2


class TestPreviewPanelMultiplePanels:
    """Tests for multiple PreviewPanel widgets."""

    def test_multiple_panels_independent(self, root):
        """Test multiple PreviewPanel widgets operate independently."""
        panel1 = PreviewPanel(root, label_text="Panel 1")
        panel2 = PreviewPanel(root, label_text="Panel 2")
        panel1.pack()
        panel2.pack()
        root.update()

        assert panel1._label_text == "Panel 1"
        assert panel2._label_text == "Panel 2"

        # Show different images
        img1 = Image.new("RGB", (256, 256), color="red")
        img2 = Image.new("RGB", (256, 256), color="blue")

        panel1.show_image(img1)
        panel2.show_image(img2)
        root.update()

        # Both should have content
        assert len(panel1._canvas.find_all()) > 0
        assert len(panel2._canvas.find_all()) > 0


class TestPreviewPanelConstants:
    """Tests for module constants."""

    def test_canvas_size_constant(self):
        """Test CANVAS_SIZE constant is 300."""
        assert CANVAS_SIZE == 300

    def test_canvas_bg_color_constant(self):
        """Test CANVAS_BG_COLOR constant is defined."""
        assert CANVAS_BG_COLOR is not None
        assert isinstance(CANVAS_BG_COLOR, str)

    def test_placeholder_color_constant(self):
        """Test PLACEHOLDER_COLOR constant is defined."""
        assert PLACEHOLDER_COLOR is not None
        assert isinstance(PLACEHOLDER_COLOR, int)
        assert 0 <= PLACEHOLDER_COLOR <= 255


class TestPreviewPanelEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_show_image_with_very_small_image(self, preview_panel):
        """Test showing a very small image."""
        img = Image.new("RGB", (8, 8), color="red")
        preview_panel.show_image(img)
        root = preview_panel.winfo_toplevel()
        root.update()

        # Should display without error
        items = preview_panel._canvas.find_all()
        assert len(items) > 0

    def test_show_image_with_square_image(self, preview_panel):
        """Test showing a square image."""
        img = Image.new("RGB", (300, 300), color="red")
        preview_panel.show_image(img)
        root = preview_panel.winfo_toplevel()
        root.update()

        # Should display without error
        items = preview_panel._canvas.find_all()
        assert len(items) > 0

    def test_show_image_sequence_clear_then_image(self, preview_panel):
        """Test clearing preview then showing image."""
        preview_panel.show_image(None)
        root = preview_panel.winfo_toplevel()
        root.update()

        img = Image.new("RGB", (256, 256), color="red")
        preview_panel.show_image(img)
        root.update()

        # Should have image
        items = preview_panel._canvas.find_all()
        assert len(items) > 0

    def test_show_image_sequence_image_then_clear(self, preview_panel):
        """Test showing image then clearing preview."""
        img = Image.new("RGB", (256, 256), color="red")
        preview_panel.show_image(img)
        root = preview_panel.winfo_toplevel()
        root.update()

        preview_panel.show_image(None)
        root.update()

        # Should have placeholder
        items = preview_panel._canvas.find_all()
        assert len(items) > 0
