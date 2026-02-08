"""
Progress indicator widget for long-running operations.

Provides an animated progress bar widget that shows during pack/unpack operations.

Task B10: Implement this class
See: BETA_TASKS.md (B10)
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Animation speed (milliseconds between updates)
ANIMATION_SPEED = 50


class ProgressBar(tk.Frame):
    """Animated progress bar widget for long-running operations.

    Displays an indeterminate progress bar with optional status text.
    Used during pack/unpack operations to show that work is happening.

    Attributes:
        _progress_var: StringVar for progress bar
        _status_label: Label for status text
        _is_running: Whether progress animation is currently running
        _animation_id: ID of scheduled animation update
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """Initialize progress bar widget.

        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to tk.Frame
        """
        super().__init__(parent, **kwargs)

        self._is_running = False
        self._animation_id: Optional[str] = None
        self._progress_var = tk.DoubleVar(value=0)
        self._status_text = ""

        # Create status label
        self._status_label = tk.Label(
            self, text="", font=("Arial", 9), fg="darkblue"
        )
        self._status_label.pack(pady=5)

        # Create progress bar (indeterminate mode)
        self._progress = ttk.Progressbar(
            self,
            variable=self._progress_var,
            mode="indeterminate",
            length=300,
        )
        self._progress.pack(padx=10, pady=10, fill="x")

        # Initially hidden
        self.pack_forget()

        logger.info("ProgressBar widget initialized")

    def start(self, message: str = "Processing...") -> None:
        """Start progress animation with optional status message.

        Args:
            message: Status message to display (default: "Processing...")
        """
        if self._is_running:
            logger.debug("Progress already running, skipping start")
            return

        self._status_text = message
        self._status_label.config(text=message)
        self._is_running = True

        # Show the widget
        self.pack(fill="x", padx=10, pady=10)

        # Start progress bar animation
        self._progress.start(interval=ANIMATION_SPEED)

        logger.info("Progress started: %s", message)

    def stop(self) -> None:
        """Stop progress animation and hide the widget."""
        if not self._is_running:
            logger.debug("Progress not running, skipping stop")
            return

        self._is_running = False

        # Stop progress bar animation
        self._progress.stop()

        # Reset to 0
        self._progress_var.set(0)

        # Hide the widget
        self.pack_forget()

        logger.info("Progress stopped")

    def set_message(self, message: str) -> None:
        """Update status message without stopping progress.

        Args:
            message: New status message
        """
        self._status_text = message
        self._status_label.config(text=message)
        logger.debug("Progress message updated: %s", message)

    def is_running(self) -> bool:
        """Check if progress animation is currently running.

        Returns:
            True if progress is currently animating
        """
        return self._is_running


if __name__ == "__main__":
    # Test the widget
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.title("ProgressBar Test")
    root.geometry("400x200")

    progress = ProgressBar(root)
    progress.pack(fill="x", padx=10, pady=10)

    def start_progress():
        progress.start("Packing textures...")

    def update_message():
        if progress.is_running():
            progress.set_message("Still working...")

    def stop_progress():
        progress.stop()

    # Test buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    start_btn = tk.Button(btn_frame, text="Start", command=start_progress)
    start_btn.pack(side="left", padx=5)

    update_btn = tk.Button(btn_frame, text="Update", command=update_message)
    update_btn.pack(side="left", padx=5)

    stop_btn = tk.Button(btn_frame, text="Stop", command=stop_progress)
    stop_btn.pack(side="left", padx=5)

    root.mainloop()
