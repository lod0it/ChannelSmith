"""
Main application window.

MainWindow is the root tk.Tk widget that contains:
- Menu bar (File, Help)
- Status bar
- Notebook with Pack/Unpack tabs

Task B1: Implement this class
See: BETA_TASKS.md (B1)
"""

import tkinter as tk
from tkinter import ttk
import logging

from channelsmith.gui.packer_panel import PackerPanel
from channelsmith.gui.unpacker_panel import UnpackerPanel

logger = logging.getLogger(__name__)


class MainWindow(tk.Tk):
    """Root application window.

    Attributes:
        status_label: tk.Label showing current status
        content_frame: tk.Frame for main content (tabs go here)
    """

    def __init__(self):
        """Initialize main window with default settings."""
        super().__init__()

        # Configuration
        self.title("ChannelSmith - Texture Channel Packer")
        self.geometry("1200x800")
        self.minsize(800, 600)

        # Create UI
        self._create_menu()
        self._create_content()
        self._create_status_bar()

        logger.info("MainWindow initialized")

    def _create_menu(self) -> None:
        """Create menu bar with File and Help menus."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Project", command=self._on_open_project)
        file_menu.add_command(label="Save Project", command=self._on_save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._on_about)
        help_menu.add_command(label="Documentation", command=self._on_docs)

    def _create_content(self) -> None:
        """Create main content frame with notebook tabs."""
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create notebook with Pack/Unpack tabs
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill="both", expand=True)

        # Pack tab
        self._packer_panel = PackerPanel(self.notebook)
        self.notebook.add(self._packer_panel, text="Pack")

        # Unpack tab
        self._unpacker_panel = UnpackerPanel(self.notebook)
        self.notebook.add(self._unpacker_panel, text="Unpack")

    def _create_status_bar(self) -> None:
        """Create status bar at bottom of window."""
        status_frame = tk.Frame(self, relief="sunken", borderwidth=1)
        status_frame.pack(side="bottom", fill="x")

        self.status_label = tk.Label(
            status_frame, text="Ready", anchor="w", padx=5, pady=2
        )
        self.status_label.pack(fill="x")

    def set_status(self, message: str) -> None:
        """Update status bar message.

        Args:
            message: Status text to display
        """
        self.status_label.config(text=message)
        self.update_idletasks()

    def _on_open_project(self) -> None:
        """Handle File > Open Project."""
        logger.info("Open Project clicked")
        self.set_status("Opening project...")
        # TODO: Implement file dialog

    def _on_save_project(self) -> None:
        """Handle File > Save Project."""
        logger.info("Save Project clicked")
        self.set_status("Saving project...")
        # TODO: Implement file save

    def _on_about(self) -> None:
        """Handle Help > About."""
        logger.info("About clicked")
        # TODO: Show about dialog

    def _on_docs(self) -> None:
        """Handle Help > Documentation."""
        logger.info("Documentation clicked")
        # TODO: Open documentation link


if __name__ == "__main__":
    # Test window
    logging.basicConfig(level=logging.INFO)
    app = MainWindow()
    app.mainloop()
