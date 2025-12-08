"""
Development runner script for PortKodiakAIShield.

This script provides a convenient way to run the application in development mode.
"""

import sys
import logging
from pathlib import Path


def setup_logging() -> None:
    """Setup logging for development."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('portkodiak_dev.log')
        ]
    )


def run_dev() -> None:
    """Run development environment."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("PortKodiakAIShield - Development Mode")
    logger.info("=" * 60)
    
    # Check if running on Windows
    if sys.platform != "win32":
        logger.error("This application requires Windows")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 11):
        logger.error("Python 3.11 or higher required")
        sys.exit(1)
    
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {Path.cwd()}")
    
    # TODO: Start service in debug mode
    # TODO: Launch UI
    
    logger.info("Development environment ready!")
    logger.info("Press Ctrl+C to stop")
    
    try:
        # Keep running
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    run_dev()
