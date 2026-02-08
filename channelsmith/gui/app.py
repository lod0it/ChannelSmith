"""
Main application class.

ChannelSmithApp is the main application controller that ties all GUI
components together and manages the application lifecycle.

Task B12: Implement this class
See: BETA_TASKS.md (B12)
"""

import logging
from typing import Optional

from channelsmith.gui.main_window import MainWindow
from channelsmith.gui.theme import configure_styles, COLORS

logger = logging.getLogger(__name__)


class ChannelSmithApp(MainWindow):
    """Main application class.

    Extends MainWindow to add application-level logic, event handling,
    and lifecycle management.

    Attributes:
        _initialized: Flag indicating if the app has been fully initialized

    Usage:
        app = ChannelSmithApp()
        app.mainloop()
    """

    def __init__(self) -> None:
        """Initialize the application.

        Sets up:
        - Main window and UI components (via MainWindow.__init__)
        - Modern dark theme
        - Window close handler
        - Logging
        """
        super().__init__()

        # Apply modern dark theme
        configure_styles(self)
        self.configure(bg=COLORS["bg_dark"])

        self._initialized = True

        # Bind the close button (X) to our cleanup handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        logger.info("ChannelSmithApp initialized successfully")

    def on_closing(self) -> None:
        """Handle application closing.

        Called when the user closes the window via the close button or
        File > Exit menu. Performs cleanup and destroys the window.
        """
        logger.info("ChannelSmithApp closing")
        try:
            self.destroy()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            # Force destroy even if cleanup fails
            try:
                self.quit()
            except Exception:
                pass

    def is_initialized(self) -> bool:
        """Check if the application is fully initialized.

        Returns:
            True if the app has been fully initialized, False otherwise
        """
        return self._initialized


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ChannelSmithApp()
    app.mainloop()
