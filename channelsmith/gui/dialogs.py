"""
Dialog helper functions for user interactions.

Provides standardized dialogs for errors, success messages, and file selection.
Task B8: Implement this module.
See: BETA_TASKS.md (B8)
"""

from tkinter import messagebox, filedialog
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def show_error(title: str, message: str) -> None:
    """Show error dialog.

    Args:
        title: Dialog title
        message: Error message to display
    """
    logger.error("Error: %s - %s", title, message)
    messagebox.showerror(title, message)


def show_success(title: str, message: str) -> None:
    """Show success dialog.

    Args:
        title: Dialog title
        message: Success message to display
    """
    logger.info("Success: %s - %s", title, message)
    messagebox.showinfo(title, message)


def ask_file(title: str, file_types: List[tuple]) -> Optional[str]:
    """Show file open dialog.

    Args:
        title: Dialog title
        file_types: List of (label, pattern) tuples
                   e.g., [("PNG Images", "*.png"), ("All Files", "*.*")]

    Returns:
        Selected file path or None if cancelled
    """
    file_path = filedialog.askopenfilename(title=title, filetypes=file_types)
    if file_path:
        logger.info("File selected: %s", file_path)
    return file_path if file_path else None


def ask_directory(title: str) -> Optional[str]:
    """Show directory selection dialog.

    Args:
        title: Dialog title

    Returns:
        Selected directory path or None if cancelled
    """
    directory = filedialog.askdirectory(title=title)
    if directory:
        logger.info("Directory selected: %s", directory)
    return directory if directory else None
