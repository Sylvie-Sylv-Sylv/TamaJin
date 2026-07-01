from __future__ import annotations
import sys
from pathlib import Path

from logging.levels import Level
from logging.handlers import (
    ConsoleHandler,
    FileHandler,
    FilteredHandler,
    _to_pascal_case,
)


class Logger:
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
        self._verbosity = default_verbosity
        self._initialized = False

    @classmethod
    def get_instance(cls) -> Logger:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, logger: Logger):
        cls._instance = logger

    def initialize(
        self,
        log_dir: str | None = None,
        min_level: Level = Level.TRACE,
        use_colors: bool = True,
        console_output: bool = True,
        default_verbosity: int = 0,
    ):
        if self._initialized:
            return

        self._min_level = min_level
        self._verbosity = default_verbosity

        if console_output:
            self._handlers.append(
                FilteredHandler(ConsoleHandler(use_colors), min_level=min_level)
            )

        if log_dir:
            self._handlers.append(
                FilteredHandler(FileHandler(log_dir), min_level=min_level)
            )

        self._initialized = True
        Logger.set_instance(self)

    def _get_caller_frame(self):
        frame = sys._getframe()

        while frame:
            if "logging" not in frame.f_code.co_filename:
                return frame
            frame = frame.f_back

        return None

    def _get_category(self, frame) -> str:
        folder = Path(frame.f_code.co_filename).parent.name

        if not folder:
            return "Unknown"

        return _to_pascal_case(folder)

    def _format_message(
        self,
        message: str,
        level: Level,
        category: str,
        file_path: str,
        line: int,
    ) -> str:
        return f"[{category}][{level.value}] {file_path}:{line}: {message}"

    def _emit(self, level: Level, message: str, *args, verbosity: int = 0):
        if not self._initialized:
            return

        if int(level) < int(self._min_level):
            return

        if verbosity > self._verbosity:
            return

        message = message.format(*args) if args else message

        frame = self._get_caller_frame()

        if frame:
            file_path = Path(frame.f_code.co_filename).name
            line = frame.f_lineno
            category = self._get_category(frame)
        else:
            file_path = "unknown"
            line = 0
            category = "Unknown"

        formatted = self._format_message(message, level, category, file_path, line)

        for handler in self._handlers:
            handler.emit(formatted, level, category)

    def trace(self, message, *args, verbosity=0):
        self._emit(Level.TRACE, message, *args, verbosity=verbosity)

    def debug(self, message, *args, verbosity=0):
        self._emit(Level.DEBUG, message, *args, verbosity=verbosity)

    def info(self, message, *args, verbosity=0):
        self._emit(Level.INFO, message, *args, verbosity=verbosity)

    def warn(self, message, *args, verbosity=0):
        self._emit(Level.WARN, message, *args, verbosity=verbosity)

    def error(self, message, *args, verbosity=0):
        self._emit(Level.ERROR, message, *args, verbosity=verbosity)

    def fatal(self, message, *args, verbosity=0):
        self._emit(Level.FATAL, message, *args, verbosity=verbosity)

    def assert_(self, condition, message, *args, verbosity=0):
        if not condition:
            self._emit(
                Level.ASSERT, f"ASSERTION FAILED: {message}", *args, verbosity=verbosity
            )

    def disable(self, category_or_level):
        for handler in self._handlers:
            if isinstance(category_or_level, Level):
                handler.disable_level(category_or_level)
            else:
                handler.disable_category(category_or_level)

    def enable(self, category_or_level):
        for handler in self._handlers:
            if isinstance(category_or_level, Level):
                handler.enable_level(category_or_level)
            else:
                handler.enable_category(category_or_level)

    def set_level(self, level: Level):
        self._min_level = level

        for handler in self._handlers:
            handler._min_level = level

    def set_verbosity(self, value: int):
        self._verbosity = value

    def flush(self):
        for handler in self._handlers:
            handler.flush()


def _get_logger():
    return Logger.get_instance()


def trace(message, *args, verbosity=0):
    _get_logger().trace(message, *args, verbosity=verbosity)


def debug(message, *args, verbosity=0):
    _get_logger().debug(message, *args, verbosity=verbosity)


def info(message, *args, verbosity=0):
    _get_logger().info(message, *args, verbosity=verbosity)


def warn(message, *args, verbosity=0):
    _get_logger().warn(message, *args, verbosity=verbosity)


def error(message, *args, verbosity=0):
    _get_logger().error(message, *args, verbosity=verbosity)


def fatal(message, *args, verbosity=0):
    _get_logger().fatal(message, *args, verbosity=verbosity)


def assert_(condition, message, *args, verbosity=0):
    _get_logger().assert_(condition, message, *args, verbosity=verbosity)


def disable(category_or_level):
    _get_logger().disable(category_or_level)


def enable(category_or_level):
    _get_logger().enable(category_or_level)


def set_verbosity(value):
    _get_logger().set_verbosity(value)


def initialize(
    log_dir=None,
    min_level=Level.TRACE,
    use_colors=True,
    console_output=True,
    default_verbosity=0,
):
    Logger.get_instance().initialize(
        log_dir, min_level, use_colors, console_output, default_verbosity
    )
