"""
Main application class.

ChannelSmithApp is the main application controller that ties all GUI
components together.

Task B12: Implement this class
See: BETA_TASKS.md (B12)
"""

import logging
from channelsmith.gui.main_window import MainWindow

logger = logging.getLogger(__name__)


class ChannelSmithApp(MainWindow):
    """Main application class.

    Extends MainWindow to add application-level logic and control flow.

    Usage:
        app = ChannelSmithApp()
        app.mainloop()
    """

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        logger.info("ChannelSmithApp initialized")

        # TODO: Initialize pack/unpack panels (B5, B6)
        # TODO: Set up event handlers
        # TODO: Load default project (B11)

    def on_closing(self) -> None:
        """Handle application closing."""
        logger.info("ChannelSmithApp closing")
        # TODO: Save project state (B11)
        self.destroy()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ChannelSmithApp()
    app.mainloop()
