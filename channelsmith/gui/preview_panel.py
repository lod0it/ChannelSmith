"""
Preview panel widget for displaying texture previews.

PreviewPanel is a frame widget that provides:
- Configurable label (default "Preview")
- 300x300 canvas for displaying texture images
- Graceful placeholder when no image is shown
- Methods to display PIL Images

Task B4: Implement this class
See: BETA_TASKS.md (B4)
"""

import tkinter as tk
from typing import Optional
import logging

from PIL import Image, ImageTk

logger = logging.getLogger(__name__)

# Canvas dimensions for preview display
CANVAS_SIZE = 300
CANVAS_BG_COLOR = "#d0d0d0"
PLACEHOLDER_COLOR = 128  # Grayscale value for placeholder


class PreviewPanel(tk.Frame):
    """Frame widget for displaying texture previews on a canvas.

    Attributes:
        _label_text: Text to display in the header label
        _canvas: Canvas widget for image display (300x300 pixels)
        _photo: Current PhotoImage reference (prevents garbage collection)
    """

    def __init__(self, parent: tk.Widget, label_text: str = "Preview", **kwargs):
        """Initialize preview panel.

        Args:
            parent: Parent widget
            label_text: Text to display in header label (default "Preview")
            **kwargs: Additional arguments passed to tk.Frame
        """
        super().__init__(parent, **kwargs)

        self._label_text = label_text
        self._photo: Optional[ImageTk.PhotoImage] = None

        # Create header label
        label = tk.Label(self, text=label_text, font=("Arial", 10, "bold"))
        label.pack(pady=5)

        # Create canvas for image display
        self._canvas = tk.Canvas(
            self,
            width=CANVAS_SIZE,
            height=CANVAS_SIZE,
            bg=CANVAS_BG_COLOR,
            relief="sunken",
            borderwidth=2,
        )
        self._canvas.pack(padx=5, pady=5)

        # Show placeholder initially
        self._display_placeholder()

        logger.info("PreviewPanel initialized with label: %s", label_text)

    def show_image(self, image: Optional[Image.Image]) -> None:
        """Display an image on the canvas.

        If image is None, displays a placeholder. Otherwise, resizes the image
        to fit the 300x300 canvas while maintaining aspect ratio and displays it.

        Args:
            image: PIL Image to display, or None to show placeholder
        """
        if image is None:
            self._display_placeholder()
            return

        # Copy image to avoid modifying original
        display_image = image.copy()

        # Resize to fit canvas while maintaining aspect ratio
        display_image.thumbnail(
            (CANVAS_SIZE, CANVAS_SIZE), Image.Resampling.LANCZOS
        )

        # Convert to PhotoImage and display
        self._display_on_canvas(display_image)

        logger.debug(
            "Displayed image on preview (size: %s)", display_image.size
        )

    def _display_placeholder(self) -> None:
        """Display a placeholder image on the canvas."""
        # Create gray placeholder image
        placeholder = Image.new("L", (CANVAS_SIZE, CANVAS_SIZE), PLACEHOLDER_COLOR)

        # Convert to PhotoImage and display
        self._display_on_canvas(placeholder)

        logger.debug("Displayed placeholder on preview")

    def _display_on_canvas(self, pil_image: Image.Image) -> None:
        """Display a PIL Image on the canvas.

        Converts PIL Image to PhotoImage and displays it centered on the canvas.

        Args:
            pil_image: PIL Image to display
        """
        # Clear canvas
        self._canvas.delete("all")

        # Convert to PhotoImage
        self._photo = ImageTk.PhotoImage(pil_image)

        # Display at center of canvas
        self._canvas.create_image(
            CANVAS_SIZE // 2, CANVAS_SIZE // 2, image=self._photo
        )


if __name__ == "__main__":
    # Test the widget
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.title("PreviewPanel Test")
    root.geometry("400x400")

    # Create preview panel
    preview_panel = PreviewPanel(root, label_text="Preview")
    preview_panel.pack(padx=10, pady=10)

    # Test buttons
    def show_test_image():
        """Create and display a test image."""
        test_img = Image.new("RGB", (500, 300), color=(128, 64, 192))
        preview_panel.show_image(test_img)

    def show_tall_image():
        """Create and display a tall test image."""
        test_img = Image.new("RGB", (100, 500), color=(192, 128, 64))
        preview_panel.show_image(test_img)

    def show_wide_image():
        """Create and display a wide test image."""
        test_img = Image.new("RGB", (500, 100), color=(64, 192, 128))
        preview_panel.show_image(test_img)

    def clear_preview():
        """Clear the preview."""
        preview_panel.show_image(None)

    # Create test button frame
    button_frame = tk.Frame(root)
    button_frame.pack(padx=10, pady=10, fill="x")

    tk.Button(button_frame, text="Show Test Image", command=show_test_image).pack(
        side="left", padx=5
    )
    tk.Button(button_frame, text="Show Tall Image", command=show_tall_image).pack(
        side="left", padx=5
    )
    tk.Button(button_frame, text="Show Wide Image", command=show_wide_image).pack(
        side="left", padx=5
    )
    tk.Button(button_frame, text="Clear Preview", command=clear_preview).pack(
        side="left", padx=5
    )

    root.mainloop()
