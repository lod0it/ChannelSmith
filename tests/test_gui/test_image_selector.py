"""
Tests for ImageSelector widget.

Task B3: Test image selector functionality
"""

import tkinter as tk
from tkinter import ttk
import pytest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile

# Skip all GUI tests if tkinter display is not available
pytestmark = pytest.mark.skipif(
    not hasattr(tk, "Tk"),
    reason="tkinter not available"
)

try:
    from channelsmith.gui.image_selector import ImageSelector, SUPPORTED_FORMATS
    from channelsmith.utils.image_utils import load_image
    from PIL import Image
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
def selector(root):
    """Create an ImageSelector widget."""
    selector = ImageSelector(root, "Roughness")
    selector.pack()
    root.update()
    return selector


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

    # Cleanup - close any open image files first
    import gc
    gc.collect()
    try:
        Path(temp_path).unlink()
    except PermissionError:
        # File might still be in use, skip cleanup
        pass


class TestImageSelector:
    """Tests for ImageSelector widget."""

    def test_initialization(self, selector):
        """Test ImageSelector initializes with correct defaults."""
        assert selector._channel_name == "Roughness"
        assert selector.get_file_path() == ""
        assert selector.get_image() is None

    def test_initialization_with_custom_channel(self, root):
        """Test ImageSelector initializes with custom channel name."""
        selector = ImageSelector(root, "Metallic")
        selector.pack()
        root.update()
        assert selector._channel_name == "Metallic"

    def test_path_label_initial_state(self, selector):
        """Test path label shows 'No image selected' initially."""
        assert selector._path_label.cget("text") == "No image selected"
        assert selector._path_label.cget("fg") == "gray"

    def test_supported_formats_constant(self):
        """Test SUPPORTED_FORMATS constant is defined."""
        assert SUPPORTED_FORMATS is not None
        assert len(SUPPORTED_FORMATS) > 0
        assert any("PNG" in f[0] for f in SUPPORTED_FORMATS)

    def test_get_image_returns_none_initially(self, selector):
        """Test get_image returns None when no image is loaded."""
        assert selector.get_image() is None

    def test_get_file_path_returns_empty_initially(self, selector):
        """Test get_file_path returns empty string when no image is loaded."""
        assert selector.get_file_path() == ""

    def test_get_image_returns_pil_image(self, selector, test_image):
        """Test get_image returns PIL Image after loading."""
        selector._load_image(test_image)
        image = selector.get_image()
        assert image is not None
        assert isinstance(image, Image.Image)

    def test_get_file_path_returns_path_after_loading(self, selector, test_image):
        """Test get_file_path returns correct path after loading."""
        selector._load_image(test_image)
        assert selector.get_file_path() == test_image

    def test_path_label_updates_after_load(self, selector, test_image):
        """Test path label updates when image is loaded."""
        selector._load_image(test_image)
        filename = Path(test_image).name
        assert selector._path_label.cget("text") == filename
        assert selector._path_label.cget("fg") == "black"

    @patch("tkinter.messagebox.showerror")
    def test_load_image_invalid_file(self, mock_error, selector):
        """Test loading an invalid file path."""
        selector._load_image("/nonexistent/path/image.png")
        assert selector.get_image() is None
        assert selector.get_file_path() == ""
        assert selector._path_label.cget("text") == "No image selected"
        mock_error.assert_called_once()

    def test_load_image_preserves_image_object(self, selector, test_image):
        """Test that loaded image object matches the original."""
        selector._load_image(test_image)
        loaded = selector.get_image()
        original = Image.open(test_image)
        assert loaded.size == original.size
        assert loaded.mode == original.mode

    @patch("tkinter.filedialog.askopenfilename")
    def test_choose_image_opens_dialog(self, mock_dialog, selector):
        """Test that Choose Image button opens file dialog."""
        mock_dialog.return_value = ""
        selector._on_choose_image()
        mock_dialog.assert_called_once()

    @patch("tkinter.filedialog.askopenfilename")
    def test_choose_image_with_valid_file(self, mock_dialog, selector, test_image):
        """Test Choose Image with valid file path."""
        mock_dialog.return_value = test_image
        selector._on_choose_image()
        assert selector.get_file_path() == test_image
        assert selector.get_image() is not None

    @patch("tkinter.filedialog.askopenfilename")
    def test_choose_image_cancelled(self, mock_dialog, selector):
        """Test cancelling Choose Image dialog."""
        mock_dialog.return_value = ""
        original_path = selector.get_file_path()
        selector._on_choose_image()
        assert selector.get_file_path() == original_path

    @patch("tkinter.messagebox.showwarning")
    def test_preview_without_image(self, mock_warning, selector):
        """Test Preview button with no image loaded."""
        selector._on_preview()
        mock_warning.assert_called_once()

    @patch("tkinter.Toplevel")
    def test_preview_with_image_creates_window(self, mock_toplevel, selector, test_image):
        """Test Preview button with image loaded."""
        mock_toplevel.return_value = MagicMock()
        selector._load_image(test_image)
        selector._on_preview()
        # Verify Toplevel was called (would create preview window)
        mock_toplevel.assert_called_once()

    def test_widget_is_frame(self, selector):
        """Test ImageSelector is a tk.Frame."""
        assert isinstance(selector, tk.Frame)

    def test_multiple_selectors_independent(self, root):
        """Test multiple ImageSelector widgets operate independently."""
        selector1 = ImageSelector(root, "Roughness")
        selector2 = ImageSelector(root, "Metallic")
        selector1.pack()
        selector2.pack()
        root.update()

        assert selector1._channel_name == "Roughness"
        assert selector2._channel_name == "Metallic"
        assert selector1.get_image() is None
        assert selector2.get_image() is None

    def test_image_selector_with_different_image(self, root, test_image):
        """Test loading different images in separate selectors."""
        selector1 = ImageSelector(root, "Channel1")
        selector2 = ImageSelector(root, "Channel2")
        selector1.pack()
        selector2.pack()
        root.update()

        selector1._load_image(test_image)
        assert selector1.get_image() is not None
        assert selector2.get_image() is None
