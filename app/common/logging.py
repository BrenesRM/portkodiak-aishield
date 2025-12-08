"""
Centralized logging configuration for PortKodiakAIShield.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
import logging.handlers

def setup_logging(
    name: str = "portkodiak",
    log_level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> None:
    """
    Setup logging configuration.
    
    Args:
        name: Logger name
        log_level: Logging level
        log_file: Path to log file. If None, logs only to stderr.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        # Ensure directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Capture warnings
    logging.captureWarnings(True)
