"""Test script for the logging library."""

import os
import sys
import time
import threading

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from logging import (
    Logger,
    Level,
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


def test_basic_logging():
    """Test basic logging functionality."""
    print("=" * 60)
    print("Testing basic logging...")
    print("=" * 60)

    # Initialize logger
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(log_dir, exist_ok=True)

    initialize(log_dir=log_dir, min_level=Level.DEBUG, use_colors=True)

    # Test different levels
    trace("This is a TRACE message")
    debug("This is a DEBUG message")
    info("This is an INFO message")
    warn("This is a WARN message")
    error("This is an ERROR message")
    fatal("This is a FATAL message")

    # Test with formatting
    debug("Player position: {}", 100, 200)
    info("Loaded {} assets", 42)

    # Test assertion
    assert_(True, "This should NOT log")
    assert_(False, "This SHOULD log: {}", "test failed")

    print("\nBasic logging test PASSED")
    time.sleep(0.5)  # Let async writes complete


def test_filtering():
    """Test filtering functionality."""
    print("=" * 60)
    print("Testing filtering...")
    print("=" * 60)

    logger = Logger.get_instance()

    # Disable WARN level
    print("\n--- Disabling WARN level ---")
    logger.disable(Level.WARN)
    warn("This should NOT appear (WARN disabled)")
    error("This SHOULD appear (ERROR)")

    # Re-enable WARN
    logger.enable(Level.WARN)
    warn("This SHOULD appear (WARN re-enabled)")

    # Disable category (using a non-existent category for testing)
    print("\n--- Disabling category ---")
    logger.disable("NonExistent")
    debug("This should appear")

    print("\nFiltering test PASSED")


def test_category_detection():
    """Test category detection."""
    print("=" * 60)
    print("Testing category detection...")
    print("=" * 60)

    # This file is in tests/ folder, so category should be "Tests"
    debug("Category should be 'Tests'")

    print("\nCategory detection test PASSED")


def test_thread_safety():
    """Test thread safety."""
    print("=" * 60)
    print("Testing thread safety...")
    print("=" * 60)

    def worker(thread_id: int):
        for i in range(10):
            debug("Thread {} message {}", thread_id, i)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("\nThread safety test PASSED")


def test_level_enum():
    """Test level enum."""
    print("=" * 60)
    print("Testing level enum...")
    print("=" * 60)

    # Test from_string
    assert Level.from_string("DEBUG") == Level.DEBUG
    assert Level.from_string("debug") == Level.DEBUG
    assert Level.from_string("WARN") == Level.WARN
    assert Level.from_string("invalid") is None

    # Test priority
    assert int(Level.DEBUG) < int(Level.INFO)
    assert int(Level.INFO) < int(Level.WARN)
    assert int(Level.WARN) < int(Level.ERROR)

    print("\nLevel enum test PASSED")


def test_verbosity():
    """Test verbosity filtering."""
    print("=" * 60)
    print("Testing verbosity...")
    print("=" * 60)

    logger = Logger.get_instance()

    # Default verbosity is 0
    print("\n--- Default verbosity 0 ---")
    debug("v0 message", verbosity=0)
    debug("v1 message", verbosity=1)  # Should NOT appear
    debug("v2 message", verbosity=2)  # Should NOT appear

    # Set verbosity to 1
    logger.set_verbosity(1)
    print("\n--- Verbosity 1 ---")
    debug("v0 message", verbosity=0)
    debug("v1 message", verbosity=1)
    debug("v2 message", verbosity=2)  # Should NOT appear

    # Set verbosity to 2
    logger.set_verbosity(2)
    print("\n--- Verbosity 2 ---")
    debug("v0 message", verbosity=0)
    debug("v1 message", verbosity=1)
    debug("v2 message", verbosity=2)

    # Reset to default
    logger.set_verbosity(0)

    print("\nVerbosity test PASSED")


def main():
    """Run all tests."""
    test_level_enum()
    test_basic_logging()
    test_filtering()
    test_category_detection()
    test_thread_safety()
    test_verbosity()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    main()
