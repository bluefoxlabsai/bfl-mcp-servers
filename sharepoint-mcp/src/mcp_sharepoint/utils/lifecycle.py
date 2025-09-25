"""Lifecycle management utilities."""

import logging
import signal
import sys
from typing import Any

logger = logging.getLogger(__name__)


def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals gracefully.
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # On Windows, also handle SIGBREAK
    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, signal_handler)


def ensure_clean_exit() -> None:
    """Ensure clean exit procedures are followed."""
    logger.debug("Performing cleanup before exit...")
    # Add any cleanup logic here if needed