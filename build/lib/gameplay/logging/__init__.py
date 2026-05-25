"""
High-Performance Game Development Logging Library

Features:
- Log levels: TRACE, DEBUG, INFO, WARN, ERROR, FATAL, ASSERT (extendable Enum)
- Ergonomic API: logger.debug(...), logger.warn(...), logger.error(...), logger.trace(...)
- Auto category detection from folder name (PascalCase)
- Log format: [Category][LEVEL] file.py:line: message
- Filtering by category and level
- Assertion logging: logger.assert(condition, "message")
- Async file writing, colorized console
- File naming: log_{year}_{month}_{day}_{hour}_{minute}_{second}.log + latest.log

Usage:
        from gameplay.logging import logger, Level, initialize
        
        # Initialize with log directory
        initialize(log_dir="logs", min_level=Level.DEBUG)
        
        # Use module-level functions
        debug("player position: {}", x, y)
        warn("collision detected")
        error("failed to load: {}", filename)
        
        # Or use logger instance
        logger = Logger.get_instance()
        logger.debug("message")
        
        # Filtering
        logger.disable("audio")      # Disable audio category
        logger.disable(Level.WARN)  # Disable WARN level globally
        
        # Assertion
        logger.assert(health > 0, "health should be positive")
"""

from gameplay.logging.levels import Level
from gameplay.logging.logger import (
        Logger,
        trace,
        debug,
        info,
        warn,
        error,
        fatal,
        assert_,
        disable,
        enable,
        set_verbosity,
        initialize,
)

# Re-export for convenience
__all__ = [
        "Level",
        "Logger",
        "trace",
        "debug",
        "info",
        "warn",
        "error",
        "fatal",
        "assert_",
        "disable",
        "enable",
        "set_verbosity",
        "initialize",
]