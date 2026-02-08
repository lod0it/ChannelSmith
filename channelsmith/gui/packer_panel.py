"""
Texture packing panel widget.

PackerPanel is a frame widget that provides:
- Template selector for choosing packing templates
- Three image selectors for Ambient Occlusion, Roughness, and Metallic channels
- Preview panel showing the packed texture result
- Pack button to execute the packing operation

Task B5: Implement this class
See: BETA_TASKS.md (B5)
"""

import tkinter as tk
from tkinter import messagebox
import logging
from typing import Optional, Dict

from PIL import Image

from channelsmith.gui.template_selector import TemplateSelector
from channelsmith.gui.image_selector import ImageSelector
from channelsmith.gui.preview_panel import PreviewPanel
from channelsmith.templates.template_loader import load_template
from channelsmith.core import pack_texture_from_template

logger = logging.getLogger(__name__)


class PackerPanel(tk.Frame):
    """Frame widget for packing texture channels into a single image.

    Combines a template selector, three image selectors (AO, Roughness, Metallic),
    a preview panel, and a pack button to compose grayscale channels into a packed
    texture according to a template.

    Attributes:
        _template_selector: TemplateSelector widget
        _ao_selector: ImageSelector for ambient occlusion
        _roughness_selector: ImageSelector for roughness
        _metallic_selector: ImageSelector for metallic
        _preview_panel: PreviewPanel showing the packed result
        _pack_btn: Pack button
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """Initialize packer panel.

        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to tk.Frame
        """
        super().__init__(parent, borderwidth=2, relief="groove", **kwargs)

        # Create main layout frame
        self._create_widgets()

        logger.info("PackerPanel initialized")

    def _create_widgets(self) -> None:
        """Create and layout all widgets."""
        # Create left frame for selectors and controls
        left_frame = tk.Frame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Header label
        header_label = tk.Label(
            left_frame, text="Texture Packing", font=("Arial", 12, "bold")
        )
        header_label.pack(fill="x", pady=5)

        # Template selector
        self._template_selector = TemplateSelector(left_frame)
        self._template_selector.pack(fill="x", pady=5)

        # Image selectors for channels
        self._ao_selector = ImageSelector(left_frame, "Ambient Occlusion")
        self._ao_selector.pack(fill="x", pady=5)

        self._roughness_selector = ImageSelector(left_frame, "Roughness")
        self._roughness_selector.pack(fill="x", pady=5)

        self._metallic_selector = ImageSelector(left_frame, "Metallic")
        self._metallic_selector.pack(fill="x", pady=5)

        # Pack button
        self._pack_btn = tk.Button(
            left_frame, text="Pack Texture", command=self._on_pack, height=2
        )
        self._pack_btn.pack(fill="x", pady=10)

        # Create right frame for preview
        right_frame = tk.Frame(self)
        right_frame.pack(side="right", fill="both", padx=5, pady=5)

        # Preview panel
        self._preview_panel = PreviewPanel(right_frame, label_text="Packed Result")
        self._preview_panel.pack()

    def _on_pack(self) -> None:
        """Handle Pack button click.

        Retrieves the template and images, calls pack_texture_from_template,
        and displays the result in the preview panel.
        """
        try:
            # Get template
            template_name = self._template_selector.get_selected_template()
            template = load_template(template_name)

            # Get images from selectors
            ao_img = self._ao_selector.get_image()
            roughness_img = self._roughness_selector.get_image()
            metallic_img = self._metallic_selector.get_image()

            # Build textures dictionary
            textures: Dict[str, Optional[Image.Image]] = {
                "ambient_occlusion": ao_img,
                "roughness": roughness_img,
                "metallic": metallic_img,
            }

            # Pack the texture
            packed = pack_texture_from_template(textures, template)

            # Display result
            self._preview_panel.show_image(packed)
            logger.info("Texture packed successfully with template '%s'", template.name)

        except FileNotFoundError as e:
            messagebox.showerror("Template Error", f"Could not load template: {e}")
            logger.error("Template load error: %s", e)
        except Exception as e:
            messagebox.showerror("Packing Error", f"Failed to pack texture: {e}")
            logger.error("Packing error: %s", e)


if __name__ == "__main__":
    # Test the widget
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.title("PackerPanel Test")
    root.geometry("900x500")

    packer = PackerPanel(root)
    packer.pack(fill="both", expand=True, padx=10, pady=10)

    root.mainloop()
