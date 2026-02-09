"""
ChannelSmith entry point script.

Run with: python -m channelsmith

This module:
- Configures logging
- Launches the Flask web UI
- Handles startup/shutdown gracefully
"""

import argparse
import logging
import os
import sys
import webbrowser
from threading import Timer

from channelsmith import __version__

# Detect if running as PyInstaller executable
IS_PYINSTALLER = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Suppress werkzeug development server warning in production/executable mode
if IS_PYINSTALLER:
    logging.getLogger("werkzeug").setLevel(logging.ERROR)


def launch_web_ui() -> int:
    """Launch the Flask web UI.

    Returns:
        0 on success, 1 on error
    """
    logger.info("Starting ChannelSmith Web UI v%s", __version__)

    try:
        from channelsmith.api.app import create_app

        app = create_app()

        # Auto-open browser after 1 second (only in main process, not reloader)
        def open_browser() -> None:
            """Open the default browser to the app."""
            try:
                webbrowser.open("http://localhost:5000")
            except Exception as e:
                logger.warning("Failed to open browser: %s", e)

        # Only open browser in main process, not in Flask's reloader subprocess
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            Timer(1.0, open_browser).start()

        if IS_PYINSTALLER:
            logger.info("Starting ChannelSmith Web UI server...")
        else:
            logger.info("Starting Flask development server...")
        logger.info("ChannelSmith Web UI: http://localhost:5000")
        logger.info("Press Ctrl+C to stop")

        # Run Flask: debug mode for development, production mode for executables
        app.run(
            host="127.0.0.1",
            port=5000,
            debug=not IS_PYINSTALLER,
            use_reloader=not IS_PYINSTALLER,
        )

        logger.info("ChannelSmith closed normally")
        return 0

    except Exception as e:
        logger.exception("Unexpected error in web UI: %s", e)
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
        "--version",
        action="version",
        version=f"ChannelSmith {__version__}",
    )

    args = parser.parse_args()

    return launch_web_ui()


if __name__ == "__main__":
    sys.exit(main())
