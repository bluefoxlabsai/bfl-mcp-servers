"""Logging utilities for MCP Teams."""

import logging
import sys
from typing import TextIO


def setup_logging(level: int = logging.INFO, stream: TextIO = sys.stderr) -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        level: Logging level
        stream: Output stream for logs
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("mcp_teams")
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger