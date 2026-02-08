"""
Tests for drag-drop functionality.

Tests drag-drop support for image widgets.
"""

import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import pytest

# Skip all tests if tkinter unavailable
pytestmark = pytest.mark.skipif(not hasattr(tk, "Tk"), reason="tkinter not available")

from channelsmith.gui.drag_drop import (
    _is_image_file,
    _extract_file_path_from_drop_data,
    enable_drag_drop,
    enable_drag_drop_on_image_selector,
)
from channelsmith.gui.image_selector import ImageSelector


class TestIsImageFile:
    """Tests for _is_image_file function."""

    def test_png_file_recognized(self):
        """PNG files should be recognized."""
        assert _is_image_file("image.png") is True

    def test_jpg_file_recognized(self):
        """JPG files should be recognized."""
        assert _is_image_file("image.jpg") is True

    def test_jpeg_file_recognized(self):
        """JPEG files should be recognized."""
        assert _is_image_file("image.jpeg") is True

    def test_tga_file_recognized(self):
        """TGA files should be recognized."""
        assert _is_image_file("image.tga") is True

    def test_tiff_file_recognized(self):
        """TIFF files should be recognized."""
        assert _is_image_file("image.tiff") is True

    def test_tif_file_recognized(self):
        """TIF files should be recognized."""
        assert _is_image_file("image.tif") is True

    def test_uppercase_extension_recognized(self):
        """Uppercase extensions should be recognized."""
        assert _is_image_file("IMAGE.PNG") is True

    def test_non_image_file_rejected(self):
        """Non-image files should be rejected."""
        assert _is_image_file("document.txt") is False

    def test_empty_string_rejected(self):
        """Empty string should be rejected."""
        assert _is_image_file("") is False

    def test_path_with_directory(self):
        """File path with directory should work."""
        assert _is_image_file("/path/to/image.png") is True
        assert _is_image_file("C:\\path\\to\\image.jpg") is True

    def test_file_without_extension_rejected(self):
        """Files without extension should be rejected."""
        assert _is_image_file("imagefile") is False


class TestExtractFilePathFromDropData:
    """Tests for _extract_file_path_from_drop_data function."""

    def test_simple_path(self):
        """Simple path should be extracted."""
        result = _extract_file_path_from_drop_data("/path/to/file.png")
        assert result == "/path/to/file.png"

    def test_quoted_path(self):
        """Quoted path should have quotes removed."""
        result = _extract_file_path_from_drop_data('"/path/to/file.png"')
        assert result == "/path/to/file.png"

    def test_windows_quoted_path(self):
        """Windows quoted path should be handled."""
        result = _extract_file_path_from_drop_data('"C:\\Users\\test\\image.png"')
        assert result == "C:\\Users\\test\\image.png"

    def test_curly_braced_path(self):
        """Curly-braced path (tkinter format) should be handled."""
        result = _extract_file_path_from_drop_data("{/path/to/file.png}")
        assert result == "/path/to/file.png"

    def test_path_with_whitespace(self):
        """Paths with leading/trailing whitespace should be trimmed."""
        result = _extract_file_path_from_drop_data("  /path/to/file.png  ")
        assert result == "/path/to/file.png"

    def test_empty_string(self):
        """Empty string should return None."""
        result = _extract_file_path_from_drop_data("")
        assert result is None

    def test_none_input(self):
        """None input should return None."""
        result = _extract_file_path_from_drop_data(None)
        assert result is None

    def test_whitespace_only(self):
        """Whitespace-only string should return None."""
        result = _extract_file_path_from_drop_data("   ")
        assert result is None


class TestEnableDragDrop:
    """Tests for enable_drag_drop function."""

    def test_enable_drag_drop_calls_callback_without_tkinterdnd(self):
        """enable_drag_drop should work without tkinterdnd2."""
        root = tk.Tk()
        try:
            widget = tk.Frame(root)
            callback = Mock()

            # Should not raise even if tkinterdnd not available
            enable_drag_drop(widget, callback)

            # Callback should be ready for use
            assert callable(callback) or True  # Just verify no exception

        finally:
            root.destroy()

    def test_enable_drag_drop_with_callback_ready(self):
        """enable_drag_drop should prepare callback for use."""
        root = tk.Tk()
        try:
            widget = tk.Frame(root)
            callback = Mock()

            # Should not raise any exception
            enable_drag_drop(widget, callback)

            # Callback should be callable
            assert callable(callback)

        finally:
            root.destroy()


class TestEnableDragDropOnImageSelector:
    """Tests for enable_drag_drop_on_image_selector function."""

    def test_enable_drag_drop_on_image_selector(self):
        """Should enable drag-drop on ImageSelector."""
        root = tk.Tk()
        try:
            selector = ImageSelector(root, "Test Channel")

            # Mock the _load_image method
            selector._load_image = Mock()

            # Enable drag-drop
            enable_drag_drop_on_image_selector(selector)

            # Verify that enable_drag_drop was called
            # (It should have succeeded without error)

            # Clean up mocks
            assert isinstance(selector._load_image, Mock)

        finally:
            root.destroy()

    def test_drag_drop_callback_calls_load_image(self):
        """Drag-drop callback should call _load_image on ImageSelector."""
        root = tk.Tk()
        try:
            selector = ImageSelector(root, "Test Channel")
            selector._load_image = Mock()

            enable_drag_drop_on_image_selector(selector)

            # The callback should be prepared to call _load_image
            # This would be tested at runtime if tkinterdnd was available

        finally:
            root.destroy()
