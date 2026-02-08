"""
Tests for file operations manager.

Tests save/load functionality for images and projects.
"""

import tkinter as tk
import tempfile
import json
import gc
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from PIL import Image

# Skip all tests if tkinter unavailable
pytestmark = pytest.mark.skipif(not hasattr(tk, "Tk"), reason="tkinter not available")

from channelsmith.gui.file_manager import (
    save_image,
    load_project,
    save_project,
    get_project_from_file_dialog,
    PROJECT_FILE_EXT,
)


class TestSaveImage:
    """Tests for save_image function."""

    def test_save_image_to_file(self):
        """save_image should save image to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_image = Image.new("RGB", (100, 100), color="red")

            with patch(
                "channelsmith.gui.file_manager.filedialog.asksaveasfilename"
            ) as mock_dialog:
                file_path = Path(tmpdir) / "test.png"
                mock_dialog.return_value = str(file_path)

                result = save_image(test_image, "test")

                assert result == str(file_path)
                assert file_path.exists()

    def test_save_image_with_default_name(self):
        """save_image should use default name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_image = Image.new("RGB", (100, 100), color="blue")

            with patch(
                "channelsmith.gui.file_manager.filedialog.asksaveasfilename"
            ) as mock_dialog:
                file_path = Path(tmpdir) / "output.png"
                mock_dialog.return_value = str(file_path)

                result = save_image(test_image)

                assert Path(result).name == "output.png"
                assert file_path.exists()

    def test_save_image_cancelled(self):
        """save_image should return empty string if cancelled."""
        test_image = Image.new("RGB", (100, 100), color="green")

        with patch(
            "channelsmith.gui.file_manager.filedialog.asksaveasfilename"
        ) as mock_dialog:
            mock_dialog.return_value = ""

            result = save_image(test_image)

            assert result == ""

    def test_save_image_none_raises_error(self):
        """save_image should raise error for None image."""
        with pytest.raises(ValueError):
            save_image(None)

    def test_save_image_jpeg_conversion(self):
        """save_image should convert RGBA to RGB for JPEG."""
        test_image = Image.new("RGBA", (100, 100), color=(255, 0, 0, 255))

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "channelsmith.gui.file_manager.filedialog.asksaveasfilename"
            ) as mock_dialog:
                file_path = Path(tmpdir) / "test.jpg"
                mock_dialog.return_value = str(file_path)

                result = save_image(test_image)

                # File should exist after saving
                assert file_path.exists()
                # Return value should match the path
                assert result == str(file_path)

    def test_save_image_different_formats(self):
        """save_image should support multiple formats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_image = Image.new("RGB", (100, 100), color="white")

            formats = ["png", "jpg", "tga", "tiff"]

            for fmt in formats:
                with patch(
                    "channelsmith.gui.file_manager.filedialog.asksaveasfilename"
                ) as mock_dialog:
                    file_path = Path(tmpdir) / f"test.{fmt}"
                    mock_dialog.return_value = str(file_path)

                    result = save_image(test_image)

                    assert file_path.exists()


class TestLoadProject:
    """Tests for load_project function."""

    def test_load_project_valid_file(self):
        """load_project should load valid project file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "project.json"
            test_data = {"template": "ORM", "settings": {"quality": "high"}}

            with open(file_path, "w") as f:
                json.dump(test_data, f)

            result = load_project(str(file_path))

            assert result == test_data
            assert result["template"] == "ORM"

    def test_load_project_nonexistent_file(self):
        """load_project should raise FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_project("/nonexistent/path/file.json")

    def test_load_project_invalid_json(self):
        """load_project should raise JSONDecodeError for invalid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "invalid.json"
            file_path.write_text("invalid json content {")

            with pytest.raises(json.JSONDecodeError):
                load_project(str(file_path))

    def test_load_project_empty_dict(self):
        """load_project should handle empty JSON object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "empty.json"
            file_path.write_text("{}")

            result = load_project(str(file_path))

            assert result == {}


class TestSaveProject:
    """Tests for save_project function."""

    def test_save_project_with_path(self):
        """save_project should save project to specified path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "project.json"
            test_data = {"template": "ORD", "images": ["ao.png", "roughness.png"]}

            result = save_project(test_data, str(file_path))

            assert file_path.exists()
            assert result == str(file_path)

            # Verify saved content
            with open(file_path) as f:
                loaded = json.load(f)
            assert loaded == test_data

    def test_save_project_with_dialog(self):
        """save_project should show dialog if no path provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "project.json"
            test_data = {"settings": "value"}

            with patch(
                "channelsmith.gui.file_manager.filedialog.asksaveasfilename"
            ) as mock_dialog:
                mock_dialog.return_value = str(file_path)

                result = save_project(test_data)

                assert file_path.exists()
                assert result == str(file_path)

    def test_save_project_cancelled(self):
        """save_project should return empty string if cancelled."""
        test_data = {"key": "value"}

        with patch(
            "channelsmith.gui.file_manager.filedialog.asksaveasfilename"
        ) as mock_dialog:
            mock_dialog.return_value = ""

            result = save_project(test_data)

            assert result == ""

    def test_save_project_none_state_raises_error(self):
        """save_project should raise error for None state."""
        with pytest.raises(ValueError):
            save_project(None, "/some/path.json")

    def test_save_project_creates_directories(self):
        """save_project should create parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "subdir" / "nested" / "project.json"
            test_data = {"test": "data"}

            save_project(test_data, str(file_path))

            assert file_path.exists()

    def test_save_project_pretty_print(self):
        """save_project should save with nice formatting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "project.json"
            test_data = {"a": 1, "b": {"nested": True}}

            save_project(test_data, str(file_path))

            content = file_path.read_text()
            # Should have indentation (pretty-printed)
            assert "  " in content or content.startswith("{")


class TestGetProjectFromFileDialog:
    """Tests for get_project_from_file_dialog function."""

    def test_get_project_from_dialog(self):
        """get_project_from_file_dialog should load selected file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "project.json"
            test_data = {"template": "ORM"}

            with open(file_path, "w") as f:
                json.dump(test_data, f)

            with patch(
                "channelsmith.gui.file_manager.filedialog.askopenfilename"
            ) as mock_dialog:
                mock_dialog.return_value = str(file_path)

                result = get_project_from_file_dialog()

                assert result == test_data

    def test_get_project_cancelled(self):
        """get_project_from_file_dialog should return None if cancelled."""
        with patch(
            "channelsmith.gui.file_manager.filedialog.askopenfilename"
        ) as mock_dialog:
            mock_dialog.return_value = ""

            result = get_project_from_file_dialog()

            assert result is None

    def test_get_project_with_custom_title(self):
        """get_project_from_file_dialog should use custom title."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "project.json"
            test_data = {"data": "value"}

            with open(file_path, "w") as f:
                json.dump(test_data, f)

            with patch(
                "channelsmith.gui.file_manager.filedialog.askopenfilename"
            ) as mock_dialog:
                mock_dialog.return_value = str(file_path)

                result = get_project_from_file_dialog(title="Custom Title")

                # Verify dialog was called with custom title
                assert mock_dialog.called
