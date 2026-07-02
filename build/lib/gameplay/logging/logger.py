from __future__ import annotations
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable

from diagnostics.levels import Level
from logging.handlers import (
        LogHandler,
        ConsoleHandler,
        FileHandler,
        FilteredHandler,
        _to_pascal_case,
)


# Global logger instance
_logger: Logger | None = None


class Logger:
        """
        High-performance game development logger.
        
        Features:
        - Ergonomic API: logger.debug(...), logger.warn(...), etc.
        - Auto category detection from folder name (PascalCase)
        - Log format: [Frame N][Category][LEVEL] file.py:line: message
        - Filtering by category and level
        - Async file writing
        - Colorized console output
        - Assertion logging
        """
        _instance: Logger | None = None

        def __init__(
                self,
                log_dir: str | None = None,
                min_level: Level = Level.TRACE,
                use_colors: bool = True,
                console_output: bool = True,
                default_verbosity: int = 0,
        ):
                self._handlers: list[FilteredHandler] = []
                self._min_level = min_level
                self._use_colors = use_colors
                self._console_output = console_output
                self._log_dir = log_dir
                self._default_verbosity = default_verbosity
                self._verbosity = default_verbosity
                self._initialized = False

        @classmethod
        def get_instance(cls) -> Logger:
                """Get the global logger instance."""
                if cls._instance is None:
                        cls._instance = cls()
                return cls._instance

        @classmethod
        def set_instance(cls, logger: Logger) -> None:
                """Set the global logger instance."""
                cls._instance = logger

        def initialize(
                self,
                log_dir: str | None = None,
                min_level: Level = Level.TRACE,
                use_colors: bool = True,
                console_output: bool = True,
                default_verbosity: int = 0,
        ) -> None:
                """Initialize the logging system."""
                if self._initialized:
                        return

                self._min_level = min_level
                self._use_colors = use_colors
                self._console_output = console_output
                self._log_dir = log_dir
                self._default_verbosity = default_verbosity
                self._verbosity = default_verbosity

                # Console handler
                if console_output:
                        console = ConsoleHandler(use_colors=use_colors)
                        self._handlers.append(FilteredHandler(console, min_level=min_level))

                # File handler
                if log_dir:
                        file_handler = FileHandler(log_dir)
                        self._handlers.append(FilteredHandler(file_handler, min_level=min_level))

                self._initialized = True
                Logger.set_instance(self)

        def _get_category(self) -> str:
                """Detect category from caller's file path."""
                # Walk up the stack to find the actual caller
                frame = sys._getframe()
                # Go back 4 frames to get past the logging module
                for _ in range(4):
                        frame = frame.f_back
                        if frame is None:
                                return "Unknown"

                # Try module name first (only if not __main__)
                module = frame.f_globals.get("__name__", "")
                if module and module != "__main__":
                        parts = module.split(".")
                        # For gameplay.physics.something -> Physics
                        if len(parts) >= 2 and parts[0] == "gameplay":
                                return _to_pascal_case(parts[1])
                        # For tests.something -> Tests
                        elif len(parts) >= 1 and parts[0] == "tests":
                                return "Tests"
                        elif len(parts) >= 1:
                                return _to_pascal_case(parts[0])
                
                # Fallback to filepath - get the gameplay subfolder
                filepath = frame.f_code.co_filename
                path = Path(filepath)
                
                # Navigate from file up to find gameplay subfolder
                # e.g., C:/Users/.../TamaJin/src/gameplay/physics/test_logging.py -> physics
                parts = list(path.parts)
                for i, part in enumerate(parts):
                        if part == "gameplay" and i + 1 < len(parts):
                                return _to_pascal_case(parts[i + 1])
                        if part == "tests" and i + 1 < len(parts):
                                return "Tests"
                
                # Last resort: use parent folder name
                parent_name = path.parent.name
                if parent_name in ("src", "tests", "", "logging"):
                        return "Unknown"
                return _to_pascal_case(parent_name)

        def _format_message(
                self,
                message: str,
                level: Level,
                category: str,
                file_path: str,
                line: int,
        ) -> str:
                """Format log message."""
                return f"[{category}][{level.value}] {file_path}:{line}: {message}"

        def _emit(self, level: Level, message: str, *args, verbosity: int = 0) -> None:
                """Emit a log message."""
                if not self._initialized:
                        return

                # Fast path: check if logging is disabled
                if int(level) < int(self._min_level):
                        return

                # Verbosity check: message verbosity must be <= global verbosity
                if verbosity > self._verbosity:
                        return

                # Format message
                full_message = message.format(*args) if args else message

                # Get caller info
                frame = sys._getframe(3)  # Go back to caller's caller
                file_path = Path(frame.f_code.co_filename).name
                line = frame.f_lineno
                category = self._get_category()

                formatted = self._format_message(
                        full_message, level, category, file_path, line
                )

                # Emit to all handlers
                for handler in self._handlers:
                        handler.emit(formatted, level, category)

        # -----------------
        # Public API
        # -----------------

        def trace(self, message: str, *args, verbosity: int = 0) -> None:
                """Log at TRACE level."""
                self._emit(Level.TRACE, message, *args, verbosity=verbosity)

        def debug(self, message: str, *args, verbosity: int = 0) -> None:
                """Log at DEBUG level."""
                self._emit(Level.DEBUG, message, *args, verbosity=verbosity)

        def info(self, message: str, *args, verbosity: int = 0) -> None:
                """Log at INFO level."""
                self._emit(Level.INFO, message, *args, verbosity=verbosity)

        def warn(self, message: str, *args, verbosity: int = 0) -> None:
                """Log at WARN level."""
                self._emit(Level.WARN, message, *args, verbosity=verbosity)

        def error(self, message: str, *args, verbosity: int = 0) -> None:
                """Log at ERROR level."""
                self._emit(Level.ERROR, message, *args, verbosity=verbosity)

        def fatal(self, message: str, *args, verbosity: int = 0) -> None:
                """Log at FATAL level."""
                self._emit(Level.FATAL, message, *args, verbosity=verbosity)

        def assert_(self, condition: bool, message: str, *args, verbosity: int = 0) -> None:
                """
                Log assertion failure.
                
                Usage: logger.assert(condition, "expected {} but got {}", expected, actual)
                Logs at ASSERT level if condition is False.
                """
                if not condition:
                        full_message = f"ASSERTION FAILED: {message}"
                        self._emit(Level.ASSERT, full_message, *args)

        # Alias for assert_ since assert is a keyword
        def assertion(self, condition: bool, message: str, *args) -> None:
                """Alias for assert_()."""
                self.assert_(condition, message, *args)

        # -----------------
        # Filtering API
        # -----------------

        def disable(self, category_or_level: str | Level) -> None:
                """
                Disable logging by category or level.
                
                Usage:
                        logger.disable("audio")    # Disable category
                        logger.disable(Level.WARN)  # Disable level
                """
                if isinstance(category_or_level, Level):
                        for handler in self._handlers:
                                handler.disable_level(category_or_level)
                else:
                        for handler in self._handlers:
                                handler.disable_category(category_or_level)

        def enable(self, category_or_level: str | Level) -> None:
                """Enable logging by category or level."""
                if isinstance(category_or_level, Level):
                        for handler in self._handlers:
                                handler.enable_level(category_or_level)
                else:
                        for handler in self._handlers:
                                handler.enable_category(category_or_level)

        def set_level(self, level: Level) -> None:
                """Set minimum log level."""
                self._min_level = level
                for handler in self._handlers:
                        handler._min_level = level

        @property
        def verbosity(self) -> int:
                """Get global verbosity level."""
                return self._verbosity

        @verbosity.setter
        def verbosity(self, value: int) -> None:
                """Set global verbosity level."""
                self._verbosity = value

        def set_verbosity(self, value: int) -> None:
                """Set global verbosity level."""
                self._verbosity = value

        def flush(self) -> None:
                """Flush all handlers."""
                for handler in self._handlers:
                        handler.flush()


# Module-level convenience functions
def _get_logger() -> Logger:
        """Get or create logger instance."""
        return Logger.get_instance()


def trace(message: str, *args, verbosity: int = 0) -> None:
        _get_logger().trace(message, *args, verbosity=verbosity)


def debug(message: str, *args, verbosity: int = 0) -> None:
        _get_logger().debug(message, *args, verbosity=verbosity)


def info(message: str, *args, verbosity: int = 0) -> None:
        _get_logger().info(message, *args, verbosity=verbosity)


def warn(message: str, *args, verbosity: int = 0) -> None:
        _get_logger().warn(message, *args, verbosity=verbosity)


def error(message: str, *args, verbosity: int = 0) -> None:
        _get_logger().error(message, *args, verbosity=verbosity)


def fatal(message: str, *args, verbosity: int = 0) -> None:
        _get_logger().fatal(message, *args, verbosity=verbosity)


def assert_(condition: bool, message: str, *args, verbosity: int = 0) -> None:
        _get_logger().assert_(condition, message, *args, verbosity=verbosity)


def disable(category_or_level: str | Level) -> None:
        _get_logger().disable(category_or_level)


def enable(category_or_level: str | Level) -> None:
        _get_logger().enable(category_or_level)


def set_verbosity(value: int) -> None:
        """Set global verbosity level."""
        _get_logger().set_verbosity(value)


@property
def verbosity() -> int:
        """Get global verbosity level."""
        return _get_logger().verbosity


def initialize(
        log_dir: str | None = None,
        min_level: Level = Level.TRACE,
        use_colors: bool = True,
        console_output: bool = True,
        default_verbosity: int = 0,
) -> None:
        logger = Logger.get_instance()
        logger.initialize(
                log_dir=log_dir,
                min_level=min_level,
                use_colors=use_colors,
                console_output=console_output,
                default_verbosity=default_verbosity,
        )