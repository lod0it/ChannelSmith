"""
Image selector widget for choosing texture channel images.

ImageSelector is a frame widget that provides:
- Label for channel name (e.g., "Roughness")
- Button to choose image file
- Label showing selected file path
- Button to preview selected image
- Methods to get the loaded image and file path

Task B3: Implement this class
See: BETA_TASKS.md (B3)
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import logging
from pathlib import Path
from typing import Optional

from PIL import Image, ImageTk

from channelsmith.gui.drag_drop import enable_drag_drop
from channelsmith.utils.image_utils import load_image, ImageLoadError

logger = logging.getLogger(__name__)

# Supported image file types
SUPPORTED_FORMATS = [
    ("PNG Images", "*.png"),
    ("JPEG Images", "*.jpg *.jpeg"),
    ("TGA Images", "*.tga"),
    ("TIFF Images", "*.tif *.tiff"),
    ("All Images", "*.png *.jpg *.jpeg *.tga *.tif *.tiff"),
    ("All Files", "*.*"),
]


class ImageSelector(tk.Frame):
    """Frame widget for selecting texture channel images.

    Attributes:
        _channel_name: Name of the channel (e.g., "Roughness")
        _file_path: Path to the selected image file
        _image: Loaded PIL Image object (None if no image selected)
        _path_label: Label showing the current file path
    """

    def __init__(self, parent: tk.Widget, channel_name: str, **kwargs):
        """Initialize image selector.

        Args:
            parent: Parent widget
            channel_name: Name of the channel (e.g., "Roughness", "Metallic")
            **kwargs: Additional arguments passed to tk.Frame
        """
        super().__init__(parent, **kwargs)

        self._channel_name = channel_name
        self._file_path: str = ""
        self._image: Optional[Image.Image] = None

        # Create label for channel name
        label = tk.Label(self, text=f"{channel_name}:", font=("Arial", 10))
        label.pack(side="left", padx=5, pady=5)

        # Create Choose Image button
        choose_btn = tk.Button(
            self, text="Choose Image", command=self._on_choose_image, width=15
        )
        choose_btn.pack(side="left", padx=5, pady=5)

        # Create label showing file path
        self._path_label = tk.Label(
            self, text="No image selected", font=("Arial", 9), fg="gray"
        )
        self._path_label.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        # Create Preview button
        preview_btn = tk.Button(
            self, text="Preview", command=self._on_preview, width=10
        )
        preview_btn.pack(side="left", padx=5, pady=5)

        # Enable drag-drop on the path label for convenient file loading
        enable_drag_drop(self._path_label, self._load_image)

        logger.info("ImageSelector initialized for channel: %s", channel_name)

    def _on_choose_image(self) -> None:
        """Handle Choose Image button click."""
        file_path = filedialog.askopenfilename(
            title=f"Select {self._channel_name} Image",
            filetypes=SUPPORTED_FORMATS,
        )

        if file_path:
            self._load_image(file_path)

    def _load_image(self, file_path: str) -> None:
        """Load an image from the given file path.

        Args:
            file_path: Path to the image file
        """
        try:
            self._image = load_image(file_path)
            self._file_path = file_path
            # Update path label to show only the filename
            filename = Path(file_path).name
            self._path_label.config(text=filename, fg="black")
            logger.info("Loaded image for %s: %s", self._channel_name, file_path)
        except (FileNotFoundError, ImageLoadError) as e:
            messagebox.showerror(
                "Image Load Error", f"Failed to load image: {e}"
            )
            logger.error("Failed to load image: %s", e)
            self._image = None
            self._file_path = ""
            self._path_label.config(text="No image selected", fg="gray")

    def _on_preview(self) -> None:
        """Handle Preview button click."""
        if self._image is None:
            messagebox.showwarning("No Image", "Please select an image first")
            return

        # Create a new window for preview
        preview_window = tk.Toplevel(self)
        preview_window.title(f"Preview: {self._channel_name}")

        # Display image info
        info_text = f"Size: {self._image.size[0]}x{self._image.size[1]} | Mode: {self._image.mode}"
        info_label = tk.Label(preview_window, text=info_text, font=("Arial", 9))
        info_label.pack(pady=5)

        # Convert PIL Image to PhotoImage for tkinter display
        # Resize if too large for display
        display_image = self._image.copy()
        max_display_size = 400
        if display_image.width > max_display_size or display_image.height > max_display_size:
            display_image.thumbnail((max_display_size, max_display_size), Image.Resampling.LANCZOS)

        # Convert PIL Image to PhotoImage
        photo = ImageTk.PhotoImage(display_image)
        # Store a reference to prevent garbage collection
        preview_window.photo = photo

        # Display in label
        image_label = tk.Label(preview_window, image=photo, bg="white")
        image_label.pack(pady=10)

        logger.debug("Showing preview for %s", self._file_path)

    def get_image(self) -> Optional[Image.Image]:
        """Get the loaded PIL Image object.

        Returns:
            PIL Image instance if an image is loaded, None otherwise
        """
        return self._image

    def get_file_path(self) -> str:
        """Get the path to the selected image file.

        Returns:
            File path as string, empty string if no image selected
        """
        return self._file_path


if __name__ == "__main__":
    # Test the widget
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.title("ImageSelector Test")
    root.geometry("600x150")

    # Create selectors for different channels
    roughness_selector = ImageSelector(root, "Roughness")
    roughness_selector.pack(fill="x", padx=10, pady=5)

    metallic_selector = ImageSelector(root, "Metallic")
    metallic_selector.pack(fill="x", padx=10, pady=5)

    ao_selector = ImageSelector(root, "Ambient Occlusion")
    ao_selector.pack(fill="x", padx=10, pady=5)

    # Test button to print selections
    def print_selections():
        print(f"Roughness: {roughness_selector.get_file_path()}")
        print(f"Metallic: {metallic_selector.get_file_path()}")
        print(f"AO: {ao_selector.get_file_path()}")

    test_btn = tk.Button(root, text="Print Selections", command=print_selections)
    test_btn.pack(pady=10)

    root.mainloop()
