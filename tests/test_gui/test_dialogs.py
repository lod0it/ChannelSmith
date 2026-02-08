"""
Tests for dialog helper functions.

Task B8: Test dialog functionality
"""

import tkinter as tk
import pytest
from unittest.mock import patch, MagicMock, call


# Skip all GUI tests if tkinter is not available
pytestmark = pytest.mark.skipif(
    not hasattr(tk, "Tk"),
    reason="tkinter not available"
)

try:
    from channelsmith.gui.dialogs import show_error, show_success, ask_file, ask_directory
    HAS_TKINTER = True
except Exception:
    HAS_TKINTER = False


class TestShowError:
    """Tests for show_error function."""

    @patch("channelsmith.gui.dialogs.messagebox.showerror")
    def test_show_error(self, mock_showerror):
        """Test show_error displays error dialog."""
        show_error("Test Error", "This is a test error")
        mock_showerror.assert_called_once_with("Test Error", "This is a test error")

    @patch("channelsmith.gui.dialogs.messagebox.showerror")
    @patch("channelsmith.gui.dialogs.logger")
    def test_show_error_logs_message(self, mock_logger, mock_showerror):
        """Test show_error logs the error."""
        show_error("Error Title", "Error message")
        mock_logger.error.assert_called_once()
        assert "Error Title" in str(mock_logger.error.call_args)
        assert "Error message" in str(mock_logger.error.call_args)


class TestShowSuccess:
    """Tests for show_success function."""

    @patch("channelsmith.gui.dialogs.messagebox.showinfo")
    def test_show_success(self, mock_showinfo):
        """Test show_success displays success dialog."""
        show_success("Success", "Operation completed")
        mock_showinfo.assert_called_once_with("Success", "Operation completed")

    @patch("channelsmith.gui.dialogs.messagebox.showinfo")
    @patch("channelsmith.gui.dialogs.logger")
    def test_show_success_logs_message(self, mock_logger, mock_showinfo):
        """Test show_success logs the message."""
        show_success("Test Title", "Test message")
        mock_logger.info.assert_called_once()
        assert "Test Title" in str(mock_logger.info.call_args)
        assert "Test message" in str(mock_logger.info.call_args)


class TestAskFile:
    """Tests for ask_file function."""

    @patch("channelsmith.gui.dialogs.filedialog.askopenfilename")
    def test_ask_file_returns_path(self, mock_dialog):
        """Test ask_file returns selected file path."""
        mock_dialog.return_value = "/path/to/file.png"
        file_types = [("PNG Images", "*.png"), ("All Files", "*.*")]

        result = ask_file("Select Image", file_types)

        assert result == "/path/to/file.png"
        mock_dialog.assert_called_once()

    @patch("channelsmith.gui.dialogs.filedialog.askopenfilename")
    def test_ask_file_cancelled(self, mock_dialog):
        """Test ask_file returns None when cancelled."""
        mock_dialog.return_value = ""

        result = ask_file("Select Image", [])

        assert result is None

    @patch("channelsmith.gui.dialogs.filedialog.askopenfilename")
    def test_ask_file_passes_filetypes(self, mock_dialog):
        """Test ask_file passes file types correctly."""
        mock_dialog.return_value = ""
        file_types = [("PNG Images", "*.png"), ("JPEG Images", "*.jpg")]

        ask_file("Select Image", file_types)

        call_kwargs = mock_dialog.call_args[1]
        assert call_kwargs["filetypes"] == file_types

    @patch("channelsmith.gui.dialogs.filedialog.askopenfilename")
    def test_ask_file_passes_title(self, mock_dialog):
        """Test ask_file passes title correctly."""
        mock_dialog.return_value = ""

        ask_file("Custom Title", [])

        call_kwargs = mock_dialog.call_args[1]
        assert call_kwargs["title"] == "Custom Title"

    @patch("channelsmith.gui.dialogs.filedialog.askopenfilename")
    @patch("channelsmith.gui.dialogs.logger")
    def test_ask_file_logs_selection(self, mock_logger, mock_dialog):
        """Test ask_file logs selected path."""
        mock_dialog.return_value = "/path/to/selected.png"

        ask_file("Select", [])

        mock_logger.info.assert_called_once()
        assert "/path/to/selected.png" in str(mock_logger.info.call_args)


class TestAskDirectory:
    """Tests for ask_directory function."""

    @patch("channelsmith.gui.dialogs.filedialog.askdirectory")
    def test_ask_directory_returns_path(self, mock_dialog):
        """Test ask_directory returns selected directory path."""
        mock_dialog.return_value = "/home/user/textures"

        result = ask_directory("Select Directory")

        assert result == "/home/user/textures"
        mock_dialog.assert_called_once()

    @patch("channelsmith.gui.dialogs.filedialog.askdirectory")
    def test_ask_directory_cancelled(self, mock_dialog):
        """Test ask_directory returns None when cancelled."""
        mock_dialog.return_value = ""

        result = ask_directory("Select Directory")

        assert result is None

    @patch("channelsmith.gui.dialogs.filedialog.askdirectory")
    def test_ask_directory_passes_title(self, mock_dialog):
        """Test ask_directory passes title correctly."""
        mock_dialog.return_value = ""

        ask_directory("Custom Title")

        call_kwargs = mock_dialog.call_args[1]
        assert call_kwargs["title"] == "Custom Title"

    @patch("channelsmith.gui.dialogs.filedialog.askdirectory")
    @patch("channelsmith.gui.dialogs.logger")
    def test_ask_directory_logs_selection(self, mock_logger, mock_dialog):
        """Test ask_directory logs selected path."""
        mock_dialog.return_value = "/home/user/projects"

        ask_directory("Select")

        mock_logger.info.assert_called_once()
        assert "/home/user/projects" in str(mock_logger.info.call_args)
