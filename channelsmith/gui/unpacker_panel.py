"""
Texture unpacking panel widget.

UnpackerPanel is a frame widget that provides:
- Load button and preview panel for the input packed texture (with drag-drop support)
- Save buttons for each extracted channel (Export R/G/B/A)
- Export All Channels button for batch export

Task B6: Implement this class
See: BETA_TASKS.md (B6)
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import logging
from pathlib import Path
from typing import Optional, Dict

import numpy as np
from PIL import Image

from channelsmith.gui.preview_panel import PreviewPanel
from channelsmith.gui.drag_drop import enable_drag_drop
from channelsmith.templates.template_loader import load_template
from channelsmith.core import unpack_texture
from channelsmith.core.packing_template import PackingTemplate
from channelsmith.utils.image_utils import load_image, save_image, from_grayscale

logger = logging.getLogger(__name__)

# Get the package root directory and construct path to default template
PACKAGE_ROOT = Path(__file__).parent.parent
DEFAULT_TEMPLATE_PATH = str(PACKAGE_ROOT / "templates" / "orm.json")

# Common texture name suffixes to strip
TEMPLATE_SUFFIXES = ["_ORM", "_ORD", "_ORH", "_PBR", "_ARM", "_MRA"]


def _extract_base_filename(file_path: str) -> str:
    """Extract base filename without template suffix.

    Examples:
        T_fabric_ORM.png → T_fabric
        texture_ORD.tga → texture
        image.png → image

    Args:
        file_path: Path to the image file

    Returns:
        Base filename without extension and template suffix
    """
    name = Path(file_path).stem  # Remove extension

    # Try to remove known template suffixes (case-insensitive)
    for suffix in TEMPLATE_SUFFIXES:
        if name.upper().endswith(suffix.upper()):
            return name[: -len(suffix)]

    return name


class UnpackerPanel(tk.Frame):
    """Frame widget for unpacking individual channels from a packed texture.

    Provides interface to load a packed texture, unpack it according to ORM template,
    and save individual channels to separate files. Supports drag-drop loading.

    Attributes:
        _preview_panel: PreviewPanel showing loaded packed image
        _unpacked_channels: Dictionary mapping channel names to numpy arrays
        _packed_image: Currently loaded packed image
        _save_buttons: Dictionary mapping channel names to save buttons
        _current_template: Currently loaded template (ORM by default)
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """Initialize unpacker panel.

        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to tk.Frame
        """
        super().__init__(parent, borderwidth=2, relief="groove", **kwargs)

        self._packed_image: Optional[Image.Image] = None
        self._packed_image_path: Optional[str] = None
        self._unpacked_channels: Dict[str, np.ndarray] = {}
        self._save_buttons: Dict[str, tk.Button] = {}
        self._button_frame: Optional[tk.Frame] = None
        self._current_template: Optional[PackingTemplate] = None
        self._preview_panel: Optional[PreviewPanel] = None

        # Load default template before creating widgets (needed for button creation)
        self._load_default_template()
        self._create_widgets()

        logger.info("UnpackerPanel initialized")

    def _create_widgets(self) -> None:
        """Create and layout all widgets."""
        # Header label
        header_label = tk.Label(
            self, text="Texture Unpacking", font=("Arial", 12, "bold")
        )
        header_label.pack(fill="x", padx=5, pady=5)

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

        # Preview panel with drag-drop support
        self._preview_panel = PreviewPanel(left_frame, label_text="Packed Image")
        self._preview_panel.pack()
        # Enable drag-drop on preview panel
        enable_drag_drop(self._preview_panel, self._on_image_dropped)

        # Right frame for save buttons
        right_frame = tk.Frame(middle_frame)
        right_frame.pack(side="right", fill="both", padx=5)

        # Channel save buttons (will be created dynamically based on template)
        self._button_frame = tk.Frame(right_frame)
        self._button_frame.pack(fill="x")

        # Initialize buttons based on default template
        self._rebuild_buttons_for_template()

    def _load_default_template(self) -> None:
        """Load the default ORM template."""
        try:
            self._current_template = load_template(DEFAULT_TEMPLATE_PATH)
            logger.debug("Loaded default template: %s", self._current_template.name)
        except Exception as e:
            logger.error("Failed to load default template: %s", e)
            messagebox.showerror(
                "Template Error", f"Failed to load default template: {e}"
            )

    def _rebuild_buttons_for_template(self) -> None:
        """Rebuild save buttons based on the current template's RGB/A channels."""
        if self._current_template is None:
            return

        try:
            template = self._current_template

            # Clear existing buttons
            for btn in self._save_buttons.values():
                btn.destroy()
            self._save_buttons.clear()

            # Create buttons for each RGB(A) channel in the template
            # Store mapping: channel_type -> button (e.g., "ambient_occlusion" -> Button)
            channel_key_order = ["R", "G", "B", "A"]
            for channel_key in channel_key_order:
                channel_map = template.channels.get(channel_key)
                if channel_map is None:
                    continue

                channel_type = channel_map.map_type

                btn = tk.Button(
                    self._button_frame,
                    text=f"Export {channel_key}",
                    command=lambda ch=channel_type: self._on_save_channel(ch),
                    width=20,
                    state="disabled",
                )
                btn.pack(fill="x", pady=3)
                # Store with channel_type as key so we can find it when unpacking
                self._save_buttons[channel_type] = btn

            # Add "Export All Channels" button
            export_all_btn = tk.Button(
                self._button_frame,
                text="Export All Channels",
                command=self._on_export_all_channels,
                width=20,
                state="disabled",
            )
            export_all_btn.pack(fill="x", pady=3)
            self._save_buttons["_export_all"] = export_all_btn

            logger.debug("Rebuilt save buttons for template '%s'", template.name)

        except Exception as e:
            logger.error("Failed to rebuild buttons for template: %s", e)

    def _on_load_packed(self) -> None:
        """Handle Load Packed Image button click."""
        file_path = filedialog.askopenfilename(
            title="Select Packed Texture Image",
            filetypes=[
                ("All Images", "*.png *.jpg *.jpeg *.tga *.tif *.tiff"),
                ("PNG Images", "*.png"),
                ("JPEG Images", "*.jpg *.jpeg"),
                ("TGA Images", "*.tga"),
                ("TIFF Images", "*.tif *.tiff"),
                ("All Files", "*.*"),
            ],
        )

        if file_path:
            self._load_packed_image(file_path)

    def _on_image_dropped(self, file_path: str) -> None:
        """Handle drag-drop of image file.

        Args:
            file_path: Path to the dropped image file
        """
        self._load_packed_image(file_path)

    def _load_packed_image(self, file_path: str) -> None:
        """Load a packed image from file.

        Args:
            file_path: Path to the image file
        """
        try:
            # Load the image
            self._packed_image = load_image(file_path)
            self._packed_image_path = file_path  # Store path for naming exports
            self._preview_panel.show_image(self._packed_image)

            # Unpack using current template
            self._on_unpack()
            logger.info("Loaded packed image: %s", file_path)
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load image: {e}")
            logger.error("Failed to load image: %s", e)
            self._packed_image = None
            self._packed_image_path = None
            self._unpacked_channels = {}
            self._update_save_buttons()

    def _on_unpack(self) -> None:
        """Unpack the loaded image using the current template."""
        if self._packed_image is None or self._current_template is None:
            return

        try:
            # Unpack the texture
            self._unpacked_channels = unpack_texture(
                self._packed_image, self._current_template
            )

            # Update save buttons
            self._update_save_buttons()
            logger.info(
                "Unpacked texture with template '%s' (%d channels)",
                self._current_template.name,
                len(self._unpacked_channels),
            )
        except Exception as e:
            messagebox.showerror("Unpack Error", f"Failed to unpack texture: {e}")
            logger.error("Failed to unpack texture: %s", e)
            self._unpacked_channels = {}
            self._update_save_buttons()

    def _update_save_buttons(self) -> None:
        """Update save button states based on available channels."""
        # Enable/disable save buttons based on available channels
        for channel_type, btn in self._save_buttons.items():
            if channel_type == "_export_all":
                # Enable Export All Channels button if any channels are available
                btn.config(state="normal" if self._unpacked_channels else "disabled")
            elif channel_type in self._unpacked_channels:
                btn.config(state="normal")
            else:
                btn.config(state="disabled")

    def _get_channel_display_name(self, channel_type: str) -> str:
        """Get display name for a channel type in RGB format.

        Args:
            channel_type: Channel type (e.g., 'ambient_occlusion', 'roughness')

        Returns:
            Display name (e.g., 'Red', 'Green', 'Blue')
        """
        # Map channel types to their RGB components
        channel_to_rgb = {
            "ambient_occlusion": "Red",
            "roughness": "Green",
            "metallic": "Blue",
            "displacement": "Blue",
            "alpha": "Alpha",
        }
        return channel_to_rgb.get(channel_type, channel_type.title())

    def _get_export_filename(self, channel_type: str) -> str:
        """Generate export filename based on base name and channel.

        Examples:
            T_fabric + Red → T_fabric_Red_Channel.png
            image + Green → image_Green_Channel.png

        Args:
            channel_type: Channel type (e.g., 'roughness')

        Returns:
            Suggested export filename
        """
        base_name = "texture"
        if self._packed_image_path:
            base_name = _extract_base_filename(self._packed_image_path)

        display_name = self._get_channel_display_name(channel_type)
        return f"{base_name}_{display_name}_Channel.png"

    def _on_save_channel(self, channel: str) -> None:
        """Handle save channel button click.

        Args:
            channel: Channel type (e.g., 'roughness')
        """
        if channel not in self._unpacked_channels:
            messagebox.showwarning(
                "Channel Not Available", f"Channel '{channel}' is not available"
            )
            return

        display_name = self._get_channel_display_name(channel)
        default_name = self._get_export_filename(channel)

        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            title=f"Save {display_name} Channel",
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
                    f"Saved {display_name} Channel to:\n{file_path}",
                )
                logger.info("Saved channel '%s' to %s", channel, file_path)
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save channel: {e}")
                logger.error("Failed to save channel '%s': %s", channel, e)

    def _on_export_all_channels(self) -> None:
        """Handle Export All Channels button click.

        Exports all unpacked channels to a user-selected directory.
        """
        if not self._unpacked_channels:
            messagebox.showwarning("No Channels", "No channels available to export")
            return

        # Ask user to select output directory
        output_dir = filedialog.askdirectory(
            title="Select Output Directory for Channel Exports"
        )

        if not output_dir:
            return

        try:
            saved_count = 0
            for channel_type, channel_array in self._unpacked_channels.items():
                try:
                    # Create filename based on base name and channel
                    filename = self._get_export_filename(channel_type)
                    file_path = f"{output_dir}/{filename}"

                    # Convert to PIL Image and save
                    channel_image = from_grayscale(channel_array)
                    save_image(channel_image, file_path)

                    logger.info("Exported channel '%s' to %s", channel_type, file_path)
                    saved_count += 1
                except Exception as e:
                    logger.error("Failed to export channel '%s': %s", channel_type, e)

            messagebox.showinfo(
                "Export Complete",
                f"Successfully exported {saved_count} channel(s) to:\n{output_dir}",
            )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export channels: {e}")
            logger.error("Failed to export channels: %s", e)


if __name__ == "__main__":
    # Test the widget
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.title("UnpackerPanel Test")
    root.geometry("700x600")

    unpacker = UnpackerPanel(root)
    unpacker.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()
