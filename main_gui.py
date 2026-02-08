#!/usr/bin/env python3
"""
ChannelSmith GUI Entry Point

Run this to launch the GUI:
    python main_gui.py

Or from within Python:
    from channelsmith.gui.app import ChannelSmithApp
    app = ChannelSmithApp()
    app.mainloop()
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("channelsmith.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def main():
    """Launch the ChannelSmith GUI application."""
    try:
        from channelsmith.gui.app import ChannelSmithApp

        logger.info("Starting ChannelSmith GUI...")
        app = ChannelSmithApp()
        app.mainloop()
    except Exception as e:
        logger.exception("Failed to start GUI")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
