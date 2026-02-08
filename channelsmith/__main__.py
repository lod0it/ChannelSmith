"""
ChannelSmith entry point script.

Run with: python -m channelsmith

This module:
- Configures logging
- Instantiates ChannelSmithApp
- Handles startup/shutdown gracefully
- Logs application lifecycle events
"""

import logging
import sys
from typing import Optional

from channelsmith.gui.app import ChannelSmithApp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> int:
    """Launch ChannelSmith application.

    Returns:
        0 on success, 1 on error
    """
    logger.info("Starting ChannelSmith v0.1.0")

    try:
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
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
