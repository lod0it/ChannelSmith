"""
ChannelSmith entry point script.

Run with: python -m channelsmith

This module:
- Configures logging
- Launches the Flask web UI by default
- Supports legacy GUI with --gui flag
- Handles startup/shutdown gracefully
"""

import argparse
import logging
import sys
import webbrowser
from threading import Timer
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def launch_web_ui() -> int:
    """Launch the Flask web UI.

    Returns:
        0 on success, 1 on error
    """
    logger.info("Starting ChannelSmith Web UI v0.1.0")

    try:
        from channelsmith.api.app import create_app

        app = create_app()

        # Auto-open browser after 1 second
        def open_browser() -> None:
            """Open the default browser to the app."""
            try:
                webbrowser.open("http://localhost:5000")
            except Exception as e:
                logger.warning("Failed to open browser: %s", e)

        Timer(1.0, open_browser).start()

        logger.info("Starting Flask development server...")
        logger.info("ChannelSmith Web UI: http://localhost:5000")
        logger.info("Press Ctrl+C to stop")

        # Run Flask in debug mode (development)
        app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

        logger.info("ChannelSmith closed normally")
        return 0

    except Exception as e:
        logger.exception("Unexpected error in web UI: %s", e)
        return 1


def launch_gui() -> int:
    """Launch the legacy tkinter GUI.

    Returns:
        0 on success, 1 on error
    """
    logger.info("Starting ChannelSmith GUI v0.1.0 (Legacy)")

    try:
        from channelsmith.gui.app import ChannelSmithApp

        app: Optional[ChannelSmithApp] = None
        app = ChannelSmithApp()

        if not app.is_initialized():
            logger.error("Application failed to initialize")
            return 1

        logger.info("Application initialized, entering main loop")
        app.mainloop()

        logger.info("ChannelSmith closed normally")
        return 0

    except Exception as e:
        logger.exception("Unexpected error in GUI: %s", e)
        return 1


def main() -> int:
    """Launch ChannelSmith application.

    Returns:
        0 on success, 1 on error
    """
    parser = argparse.ArgumentParser(
        description="ChannelSmith - Texture Channel Packer",
        prog="python -m channelsmith",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch legacy tkinter GUI instead of web UI",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="ChannelSmith 0.1.0",
    )

    args = parser.parse_args()

    if args.gui:
        return launch_gui()
    else:
        return launch_web_ui()


if __name__ == "__main__":
    sys.exit(main())
