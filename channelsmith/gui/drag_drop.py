"""
Drag-and-drop support for image widgets.

Provides functions to add drag-drop capabilities to ImageSelector widgets,
allowing users to drag image files directly onto the widget.

Task B9: Implement this module
See: BETA_TASKS.md (B9)
"""

import tkinter as tk
import logging
from pathlib import Path
from typing import Optional, Callable, List

logger = logging.getLogger(__name__)

# Supported image extensions for drag-drop
SUPPORTED_EXTENSIONS = {".png", ".tga", ".jpg", ".jpeg", ".tiff", ".tif"}


def _is_image_file(file_path: str) -> bool:
    """Check if file path is a supported image file.

    Args:
        file_path: Path to file

    Returns:
        True if file has supported image extension
    """
    try:
        ext = Path(file_path).suffix.lower()
        return ext in SUPPORTED_EXTENSIONS
    except Exception:
        return False


def _extract_file_path_from_drop_data(drop_data: str) -> Optional[str]:
    """Extract file path from tkinterdnd drop data.

    Handles both Unix and Windows path formats, and quoted paths.

    Args:
        drop_data: Raw drop event data

    Returns:
        Cleaned file path or None if not a valid path
    """
    if not drop_data:
        return None

    # Handle quoted paths (Windows)
    path = drop_data.strip()
    if path.startswith("{") and path.endswith("}"):
        path = path[1:-1]

    # Remove quotes if present
    if path.startswith('"') and path.endswith('"'):
        path = path[1:-1]

    # Remove leading/trailing whitespace
    path = path.strip()

    return path if path else None


def enable_drag_drop(
    widget: tk.Widget,
    on_drop: Callable[[str], None],
    extensions: Optional[List[str]] = None,
) -> None:
    """Enable drag-drop functionality on a widget.

    Allows users to drag image files onto the widget. When a file is dropped,
    calls the on_drop callback with the file path.

    Args:
        widget: tk.Widget to enable drag-drop on
        on_drop: Callback function that receives file path (str)
        extensions: Optional list of allowed extensions (default: SUPPORTED_EXTENSIONS)

    Example:
        def handle_drop(file_path: str):
            print(f"Dropped: {file_path}")

        enable_drag_drop(image_selector, handle_drop)
    """
    allowed_exts = extensions or SUPPORTED_EXTENSIONS

    try:
        # Try to import tkinterdnd for proper drag-drop support
        from tkinterdnd2 import DND_FILES, DND_TEXT

        def drop_handler(event):
            """Handle DND drop event."""
            drop_data = event.data
            file_path = _extract_file_path_from_drop_data(drop_data)

            if file_path and _is_image_file(file_path):
                logger.debug("Drag-drop received file: %s", file_path)
                on_drop(file_path)
            else:
                logger.warning("Drag-drop received unsupported file: %s", file_path)

        # Register drag-drop target
        widget.drop_target_register(DND_FILES, DND_TEXT)
        widget.dnd_bind("<<Drop>>", drop_handler)
        logger.info("Drag-drop enabled with tkinterdnd2")

    except ImportError:
        # Fallback: tkinterdnd not available, provide basic drag-drop via paste
        logger.debug(
            "tkinterdnd2 not available, drag-drop support limited. "
            "Install with: pip install tkinterdnd2"
        )
        # Could implement fallback here (e.g., clipboard paste), but for now
        # we just log that tkinterdnd is needed for full support


def enable_drag_drop_on_image_selector(widget) -> None:
    """Enable drag-drop specifically for ImageSelector widgets.

    Args:
        widget: ImageSelector widget instance
    """
    def on_drop(file_path: str):
        """Handle dropped file - load it in the ImageSelector."""
        widget._load_image(file_path)

    enable_drag_drop(widget, on_drop)
    logger.info("Drag-drop enabled for ImageSelector: %s", widget._channel_name)
