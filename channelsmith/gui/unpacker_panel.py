"""
Texture unpacking panel widget.

UnpackerPanel is a frame widget that provides:
- Template selector for choosing unpacking templates
- Load button and preview panel for the input packed texture
- Save buttons for each extracted channel (AO, Roughness, Metallic, Alpha)
- Status display showing available channels

Task B6: Implement this class
See: BETA_TASKS.md (B6)
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import logging
from typing import Optional, Dict

import numpy as np
from PIL import Image

from channelsmith.gui.template_selector import TemplateSelector
from channelsmith.gui.preview_panel import PreviewPanel
from channelsmith.templates.template_loader import load_template
from channelsmith.core import unpack_texture
from channelsmith.utils.image_utils import load_image, save_image, from_grayscale

logger = logging.getLogger(__name__)


class UnpackerPanel(tk.Frame):
    """Frame widget for unpacking individual channels from a packed texture.

    Provides interface to load a packed texture, unpack it according to a template,
    and save individual channels to separate files.

    Attributes:
        _template_selector: TemplateSelector widget
        _preview_panel: PreviewPanel showing loaded packed image
        _unpacked_channels: Dictionary mapping channel names to numpy arrays
        _packed_image: Currently loaded packed image
        _status_label: Label showing channel status
        _save_buttons: Dictionary mapping channel names to save buttons
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """Initialize unpacker panel.

        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to tk.Frame
        """
        super().__init__(parent, borderwidth=2, relief="groove", **kwargs)

        self._packed_image: Optional[Image.Image] = None
        self._unpacked_channels: Dict[str, np.ndarray] = {}
        self._save_buttons: Dict[str, tk.Button] = {}

        self._create_widgets()

        logger.info("UnpackerPanel initialized")

    def _create_widgets(self) -> None:
        """Create and layout all widgets."""
        # Header label
        header_label = tk.Label(
            self, text="Texture Unpacking", font=("Arial", 12, "bold")
        )
        header_label.pack(fill="x", padx=5, pady=5)

        # Template selector
        self._template_selector = TemplateSelector(self)
        self._template_selector.pack(fill="x", padx=5, pady=5)

        # Create middle frame for preview and save buttons
        middle_frame = tk.Frame(self)
        middle_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Left frame for preview
        left_frame = tk.Frame(middle_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5)

        # Load button
        load_btn = tk.Button(
            left_frame, text="Load Packed Image", command=self._on_load_packed
        )
        load_btn.pack(fill="x", pady=5)

        # Preview panel
        self._preview_panel = PreviewPanel(left_frame, label_text="Packed Image")
        self._preview_panel.pack()

        # Right frame for save buttons
        right_frame = tk.Frame(middle_frame)
        right_frame.pack(side="right", fill="both", padx=5)

        # Channel save buttons (will be enabled/disabled based on unpacked channels)
        button_frame = tk.Frame(right_frame)
        button_frame.pack(fill="x")

        channels = ["ambient_occlusion", "roughness", "metallic", "alpha"]
        channel_labels = ["Ambient Occlusion", "Roughness", "Metallic", "Alpha"]

        for channel, label in zip(channels, channel_labels):
            btn = tk.Button(
                button_frame,
                text=f"Save {label}",
                command=lambda ch=channel: self._on_save_channel(ch),
                width=20,
                state="disabled",
            )
            btn.pack(fill="x", pady=3)
            self._save_buttons[channel] = btn

        # Status label
        self._status_label = tk.Label(
            right_frame,
            text="No image loaded",
            font=("Arial", 9),
            fg="gray",
            wraplength=150,
            justify="left",
        )
        self._status_label.pack(fill="both", expand=True, pady=10)

    def _on_load_packed(self) -> None:
        """Handle Load Packed Image button click."""
        file_path = filedialog.askopenfilename(
            title="Select Packed Texture Image",
            filetypes=[
                ("PNG Images", "*.png"),
                ("JPEG Images", "*.jpg *.jpeg"),
                ("TGA Images", "*.tga"),
                ("TIFF Images", "*.tif *.tiff"),
                ("All Images", "*.png *.jpg *.jpeg *.tga *.tif *.tiff"),
                ("All Files", "*.*"),
            ],
        )

        if file_path:
            try:
                # Load the image
                self._packed_image = load_image(file_path)
                self._preview_panel.show_image(self._packed_image)

                # Unpack using current template
                self._on_unpack()
                logger.info("Loaded packed image: %s", file_path)
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load image: {e}")
                logger.error("Failed to load image: %s", e)
                self._packed_image = None
                self._unpacked_channels = {}
                self._update_save_buttons()

    def _on_unpack(self) -> None:
        """Unpack the loaded image using the selected template."""
        if self._packed_image is None:
            return

        try:
            # Get template
            template_path = self._template_selector.get_template_path()
            template = load_template(template_path)

            # Unpack the texture
            self._unpacked_channels = unpack_texture(self._packed_image, template)

            # Update save buttons
            self._update_save_buttons()
            logger.info(
                "Unpacked texture with template '%s' (%d channels)",
                template.name,
                len(self._unpacked_channels),
            )
        except Exception as e:
            messagebox.showerror("Unpack Error", f"Failed to unpack texture: {e}")
            logger.error("Failed to unpack texture: %s", e)
            self._unpacked_channels = {}
            self._update_save_buttons()

    def _update_save_buttons(self) -> None:
        """Update save button states based on available channels."""
        status_text = ""
        if not self._unpacked_channels:
            status_text = "No image loaded"
        else:
            status_text = f"Available channels:\n"
            for channel in self._unpacked_channels:
                status_text += f"• {channel.replace('_', ' ').title()}\n"

        self._status_label.config(text=status_text)

        # Enable/disable save buttons based on available channels
        for channel, btn in self._save_buttons.items():
            if channel in self._unpacked_channels:
                btn.config(state="normal")
            else:
                btn.config(state="disabled")

    def _on_save_channel(self, channel: str) -> None:
        """Handle save channel button click.

        Args:
            channel: Channel name (e.g., 'roughness')
        """
        if channel not in self._unpacked_channels:
            messagebox.showwarning(
                "Channel Not Available", f"Channel '{channel}' is not available"
            )
            return

        # Ask user where to save
        default_name = channel.replace("_", "_") + ".png"
        file_path = filedialog.asksaveasfilename(
            title=f"Save {channel.replace('_', ' ').title()} Channel",
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[
                ("PNG Images", "*.png"),
                ("JPEG Images", "*.jpg *.jpeg"),
                ("TGA Images", "*.tga"),
                ("TIFF Images", "*.tif *.tiff"),
                ("All Files", "*.*"),
            ],
        )

        if file_path:
            try:
                # Get the channel array
                channel_array = self._unpacked_channels[channel]

                # Convert to PIL Image
                channel_image = from_grayscale(channel_array)

                # Save the image
                save_image(channel_image, file_path)
                messagebox.showinfo(
                    "Save Successful",
                    f"Saved {channel.replace('_', ' ').title()} to:\n{file_path}",
                )
                logger.info("Saved channel '%s' to %s", channel, file_path)
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save channel: {e}")
                logger.error("Failed to save channel '%s': %s", channel, e)


if __name__ == "__main__":
    # Test the widget
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.title("UnpackerPanel Test")
    root.geometry("700x600")

    unpacker = UnpackerPanel(root)
    unpacker.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()
