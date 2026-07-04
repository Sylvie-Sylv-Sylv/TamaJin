from __future__ import annotations
import os
import sys
import threading
import queue
from datetime import datetime
from pathlib import Path
from typing import Callable

from diagnostics.levels import Level


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


# Level to color mapping
LEVEL_COLORS = {
    Level.TRACE: Colors.GRAY,
    Level.DEBUG: Colors.BLUE,
    Level.INFO: Colors.GREEN,
    Level.WARN: Colors.YELLOW,
    Level.ERROR: Colors.RED,
    Level.FATAL: Colors.MAGENTA,
    Level.ASSERT: Colors.RED,
}


def _to_pascal_case(name: str) -> str:
    """Convert folder name to PascalCase."""
    # Split on underscores, hyphens, or spaces
    parts = name.replace("-", "_").replace(" ", "_").split("_")
    return "".join(part.capitalize() for part in parts if part)


class LogHandler:
    """Base handler interface."""

    def emit(self, message: str, level: Level, category: str) -> None:
        raise NotImplementedError

    def flush(self) -> None:
        pass


class ConsoleHandler(LogHandler):
    """Colorized console output handler."""

    def __init__(self, use_colors: bool = True):
        self._use_colors = use_colors and sys.stdout.isatty()

    def emit(self, message: str, level: Level, category: str) -> None:
        color = LEVEL_COLORS.get(level, "") if self._use_colors else ""
        reset = Colors.RESET if self._use_colors else ""
        print(f"{color}{message}{reset}")


class FileHandler(LogHandler):
    """Async file handler with session duplication."""

    def __init__(self, log_dir: str):
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._queue: queue.Queue[str | None] = queue.Queue()
        self._thread = threading.Thread(target=self._writer_loop, daemon=True)
        self._running = True
        self._thread.start()

    def emit(self, message: str, level: Level, category: str) -> None:
        self._queue.put(message)

    def flush(self) -> None:
        self._queue.put(None)
        self._thread.join(timeout=2.0)

    def _writer_loop(self) -> None:
        current_file = None
        while self._running:
            try:
                message = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if message is None:
                continue

            now = datetime.now()
            filename = f"log_{now.year}_{now.month:02d}_{now.day:02d}_{now.hour:02d}_{now.minute:02d}_{now.second:02d}.log"
            filepath = self._log_dir / filename
            latest_path = self._log_dir / "latest.log"

            # Open new file if hour changed
            if current_file != filepath:
                current_file = filepath

            # Write to both dated file and latest.log
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(message + "\n")
            with open(latest_path, "w", encoding="utf-8") as f:
                f.write(message + "\n")

    def close(self) -> None:
        self._running = False


class FilteredHandler(LogHandler):
    """Handler that filters by level and category."""

    def __init__(
        self,
        handler: LogHandler,
        min_level: Level = Level.TRACE,
        categories: set[str] | None = None,
    ):
        self._handler = handler
        self._min_level = min_level
        self._categories: set[str] | None = categories
        self._disabled_levels: set[Level] = set()
        self._disabled_categories: set[str] = set()

    def emit(self, message: str, level: Level, category: str) -> None:
        # Check level filter
        if level in self._disabled_levels:
            return
        if int(level) < int(self._min_level):
            return
        # Check category filter
        if category in self._disabled_categories:
            return
        if self._categories is not None and category not in self._categories:
            return
        self._handler.emit(message, level, category)

    def disable_level(self, level: Level) -> None:
        self._disabled_levels.add(level)

    def enable_level(self, level: Level) -> None:
        self._disabled_levels.discard(level)

    def disable_category(self, category: str) -> None:
        self._disabled_categories.add(category)

    def enable_category(self, category: str) -> None:
        self._disabled_categories.discard(category)

    def flush(self) -> None:
        self._handler.flush()
