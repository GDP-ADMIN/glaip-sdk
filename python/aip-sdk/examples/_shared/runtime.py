"""Runtime utilities for AI Agent Platform examples.

Provides runtime management functionality including cleanup registration,
timeout handling, and run identification across examples.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import atexit
import signal
import time
import uuid
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any

# Global run ID for this execution
RUN_ID = str(uuid.uuid4())[:8]

# Cleanup registry
_cleanup_functions: list[Callable[[], None]] = []
_cleanup_registry: dict[str, Any] = {}


def register_cleanup(func: Callable[[], None], name: str | None = None) -> None:
    """Register a cleanup function to be called on exit.

    Args:
        func: Cleanup function to register
        name: Optional name for the cleanup function
    """
    _cleanup_functions.append(func)
    if name:
        _cleanup_registry[name] = func


def unregister_cleanup(func: Callable[[], None]) -> None:
    """Unregister a cleanup function.

    Args:
        func: Cleanup function to unregister
    """
    if func in _cleanup_functions:
        _cleanup_functions.remove(func)


def get_cleanup_count() -> int:
    """Get the number of registered cleanup functions.

    Returns:
        Number of registered cleanup functions
    """
    return len(_cleanup_functions)


def run_cleanup() -> None:
    """Run all registered cleanup functions."""
    if not _cleanup_functions:
        return

    print(f"\n🧹 Running cleanup for {len(_cleanup_functions)} registered functions...")

    for i, cleanup_func in enumerate(_cleanup_functions, 1):
        try:
            cleanup_func()
            print(f"  ✅ Cleanup {i}/{len(_cleanup_functions)} completed")
        except Exception as e:
            print(f"  ❌ Cleanup {i}/{len(_cleanup_functions)} failed: {e}")

    # Clear the registry
    _cleanup_functions.clear()
    _cleanup_registry.clear()


@contextmanager
def timeout_handler(seconds: float, timeout_message: str = "Operation timed out"):
    """Context manager for handling timeouts.

    Args:
        seconds: Timeout duration in seconds
        timeout_message: Message to display on timeout

    Yields:
        None

    Raises:
        TimeoutError: If the operation exceeds the timeout
    """

    def timeout_signal_handler(signum, frame):
        raise TimeoutError(timeout_message)

    # Set up signal handler for timeout
    old_handler = signal.signal(signal.SIGALRM, timeout_signal_handler)
    signal.alarm(int(seconds))

    try:
        yield
    finally:
        # Restore original signal handler and cancel alarm
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


@contextmanager
def retry_handler(
    max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0
):
    """Context manager for handling retries with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds

    Yields:
        Tuple of (attempt_number, should_retry)
    """
    for attempt in range(max_retries + 1):
        try:
            yield (attempt, attempt < max_retries)
            break
        except Exception as e:
            if attempt >= max_retries:
                raise e

            # Calculate delay with exponential backoff
            delay = min(base_delay * (2**attempt), max_delay)
            print(f"  ⏳ Attempt {attempt + 1} failed, retrying in {delay:.1f}s...")
            time.sleep(delay)


@contextmanager
def resource_tracker(resource_name: str):
    """Context manager for tracking resource creation and cleanup.

    Args:
        resource_name: Name of the resource being tracked

    Yields:
        None
    """
    print(f"  📝 Creating {resource_name}...")
    try:
        yield
        print(f"  ✅ {resource_name} created successfully")
    except Exception as e:
        print(f"  ❌ Failed to create {resource_name}: {e}")
        raise


def get_run_info() -> dict[str, Any]:
    """Get information about the current run.

    Returns:
        Dictionary with run information
    """
    return {
        "run_id": RUN_ID,
        "timestamp": time.time(),
        "cleanup_count": get_cleanup_count(),
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
    }


def print_run_info() -> None:
    """Print information about the current run."""
    info = get_run_info()
    print("\n🔍 Run Information:")
    print(f"  Run ID: {info['run_id']}")
    print(
        f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['timestamp']))}"
    )
    print(f"  Cleanup Functions: {info['cleanup_count']}")
    print(f"  Python Version: {info['python_version']}")


# Register cleanup function to run on exit
atexit.register(run_cleanup)


# Handle signals for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\n🛑 Received signal {signum}, running cleanup...")
    run_cleanup()
    exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# Performance measurement utilities
class PerformanceTimer:
    """Context manager for measuring execution time."""

    def __init__(self, operation_name: str = "Operation"):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        print(f"  ⏱️  Starting {self.operation_name}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"  ✅ {self.operation_name} completed in {duration:.2f}s")

    @property
    def duration(self) -> float:
        """Get the duration of the operation."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return 0.0


def measure_time(func: Callable) -> Callable:
    """Decorator to measure function execution time.

    Args:
        func: Function to measure

    Returns:
        Wrapped function with timing
    """

    def wrapper(*args, **kwargs):
        with PerformanceTimer(func.__name__):
            return func(*args, **kwargs)

    return wrapper
