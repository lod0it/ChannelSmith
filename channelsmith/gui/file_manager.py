"""
File operations manager for GUI.

Provides utilities for saving/loading images and projects.

Task B11: Implement this module
See: BETA_TASKS.md (B11)
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from tkinter import filedialog

from PIL import Image

logger = logging.getLogger(__name__)

# Supported image formats for saving
IMAGE_SAVE_FORMATS = [
    ("PNG Images", "*.png"),
    ("JPEG Images", "*.jpg"),
    ("TGA Images", "*.tga"),
    ("TIFF Images", "*.tiff"),
    ("All Files", "*.*"),
]

# Project file extension
PROJECT_FILE_EXT = ".csproj"


def save_image(image: Image.Image, default_name: str = "output") -> str:
    """Save an image using file dialog.

    Prompts user to choose save location and format, then saves the image.

    Args:
        image: PIL Image to save
        default_name: Default filename (without extension)

    Returns:
        Path to saved file, or empty string if cancelled

    Raises:
        ValueError: If image is None
    """
    if image is None:
        raise ValueError("Cannot save None image")

    # Show save dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        initialfile=default_name,
        filetypes=IMAGE_SAVE_FORMATS,
    )

    if not file_path:
        logger.info("Save cancelled by user")
        return ""

    try:
        # Determine format from extension
        ext = Path(file_path).suffix.lower()
        pil_format = {
            ".png": "PNG",
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
            ".tga": "TGA",
            ".tiff": "TIFF",
            ".tif": "TIFF",
        }.get(ext, "PNG")

        # Convert to RGB if saving as JPEG (doesn't support alpha)
        if pil_format == "JPEG" and image.mode == "RGBA":
            image = image.convert("RGB")

        # Save the image
        image.save(file_path, format=pil_format)
        logger.info("Image saved to: %s", file_path)
        return file_path

    except Exception as e:
        logger.error("Failed to save image: %s", e)
        raise


def load_project(file_path: str) -> Dict[str, Any]:
    """Load a project file.

    Loads project state from a JSON file.

    Args:
        file_path: Path to project file

    Returns:
        Dictionary containing project state

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Project file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            project_data = json.load(f)
        logger.info("Project loaded from: %s", file_path)
        return project_data
    except json.JSONDecodeError as e:
        logger.error("Invalid project file format: %s", e)
        raise


def save_project(state: Dict[str, Any], file_path: Optional[str] = None) -> str:
    """Save project state to file.

    Saves project configuration to a JSON file. If no path provided,
    prompts user with save dialog.

    Args:
        state: Dictionary containing project state
        file_path: Path to save to (if None, shows save dialog)

    Returns:
        Path to saved file

    Raises:
        ValueError: If state is None or file_path is empty
        IOError: If write fails
    """
    if state is None:
        raise ValueError("Cannot save None state")

    # If no path provided, show save dialog
    if not file_path:
        file_path = filedialog.asksaveasfilename(
            defaultextension=PROJECT_FILE_EXT,
            filetypes=[
                ("ChannelSmith Projects", f"*{PROJECT_FILE_EXT}"),
                ("JSON Files", "*.json"),
                ("All Files", "*.*"),
            ],
        )

        if not file_path:
            logger.info("Save cancelled by user")
            return ""

    try:
        # Ensure parent directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # Save as pretty-printed JSON
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        logger.info("Project saved to: %s", file_path)
        return file_path

    except IOError as e:
        logger.error("Failed to save project: %s", e)
        raise


def get_project_from_file_dialog(title: str = "Load Project") -> Optional[Dict[str, Any]]:
    """Show dialog to load a project file.

    Convenience function that shows load dialog and loads the selected file.

    Args:
        title: Title for the file dialog

    Returns:
        Project data if file loaded, None if cancelled

    Raises:
        FileNotFoundError: If selected file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=[
            ("ChannelSmith Projects", f"*{PROJECT_FILE_EXT}"),
            ("JSON Files", "*.json"),
            ("All Files", "*.*"),
        ],
    )

    if not file_path:
        logger.info("Load cancelled by user")
        return None

    return load_project(file_path)
