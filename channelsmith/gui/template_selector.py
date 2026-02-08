"""
Template selector widget for choosing packing templates.

TemplateSelector is a frame widget that provides:
- Dropdown to select built-in templates (ORM, ORD)
- Button to load custom template files
- Method to get the selected template name

Task B2: Implement this class
See: BETA_TASKS.md (B2)
"""

import tkinter as tk
from tkinter import ttk, filedialog
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Built-in templates
BUILTIN_TEMPLATES = ["ORM", "ORD"]


class TemplateSelector(tk.Frame):
    """Frame widget for selecting texture packing templates.

    Attributes:
        _selected_template: Currently selected template name
        _combo: ttk.Combobox for template selection
    """

    def __init__(self, parent: tk.Widget, **kwargs):
        """Initialize template selector.

        Args:
            parent: Parent widget
            **kwargs: Additional arguments passed to tk.Frame
        """
        super().__init__(parent, **kwargs)

        self._selected_template: str = BUILTIN_TEMPLATES[0]

        # Create label
        label = tk.Label(self, text="Template:", font=("Arial", 10))
        label.pack(side="left", padx=5, pady=5)

        # Create dropdown
        self._combo = ttk.Combobox(
            self,
            values=BUILTIN_TEMPLATES,
            state="readonly",
            width=15,
        )
        self._combo.set(self._selected_template)
        self._combo.pack(side="left", padx=5, pady=5)
        self._combo.bind("<<ComboboxSelected>>", self._on_template_selected)

        # Create Load Custom button
        load_custom_btn = tk.Button(
            self, text="Load Custom", command=self._on_load_custom
        )
        load_custom_btn.pack(side="left", padx=5, pady=5)

        logger.info("TemplateSelector initialized")

    def _on_template_selected(self, event: tk.Event) -> None:
        """Handle template selection from dropdown.

        Args:
            event: Tkinter event
        """
        self._selected_template = self._combo.get()
        logger.debug("Template selected: %s", self._selected_template)

    def _on_load_custom(self) -> None:
        """Handle Load Custom button click."""
        file_path = filedialog.askopenfilename(
            title="Select Custom Template",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
        )

        if file_path:
            # Extract template name from file (without extension)
            template_name = Path(file_path).stem
            self._selected_template = file_path
            self._combo.set(template_name)
            logger.info("Custom template loaded: %s", file_path)

    def get_selected_template(self) -> str:
        """Get the selected template name or path.

        Returns:
            Template name (e.g., 'ORM') or file path for custom templates
        """
        return self._selected_template


if __name__ == "__main__":
    # Test the widget
    logging.basicConfig(level=logging.INFO)
    root = tk.Tk()
    root.title("TemplateSelector Test")
    root.geometry("400x100")

    selector = TemplateSelector(root)
    selector.pack(fill="x", padx=10, pady=10)

    def print_selection():
        print(f"Selected: {selector.get_selected_template()}")

    test_btn = tk.Button(root, text="Print Selection", command=print_selection)
    test_btn.pack(pady=10)

    root.mainloop()
