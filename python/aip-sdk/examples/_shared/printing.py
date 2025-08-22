"""Printing utilities for AI Agent Platform examples.

Provides consistent output formatting and styling across all examples
for better user experience and readability.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import sys
from typing import Any


def h1(text: str) -> None:
    """Print a main heading.

    Args:
        text: Heading text to display
    """
    print(f"\n{'=' * 60}")
    print(f"🚀 {text}")
    print(f"{'=' * 60}")


def h2(text: str) -> None:
    """Print a secondary heading.

    Args:
        text: Heading text to display
    """
    print(f"\n{'-' * 40}")
    print(f"📁 {text}")
    print(f"{'-' * 40}")


def h3(text: str) -> None:
    """Print a tertiary heading.

    Args:
        text: Heading text to display
    """
    print(f"\n🔧 {text}")
    print("-" * 20)


def step(text: str) -> None:
    """Print a step in a process.

    Args:
        text: Step description
    """
    print(f"  📝 {text}")


def ok(text: str) -> None:
    """Print a success message.

    Args:
        text: Success message
    """
    print(f"  ✅ {text}")


def warn(text: str) -> None:
    """Print a warning message.

    Args:
        text: Warning message
    """
    print(f"  ⚠️  {text}")


def fail(text: str) -> None:
    """Print a failure message.

    Args:
        text: Failure message
    """
    print(f"  ❌ {text}")


def info(text: str) -> None:
    """Print an informational message.

    Args:
        text: Information message
    """
    print(f"  ℹ️  {text}")


def code(text: str) -> None:
    """Print code or command text.

    Args:
        text: Code or command to display
    """
    print(f"  💻 {text}")


def data(text: str) -> None:
    """Print data or output text.

    Args:
        text: Data or output to display
    """
    print(f"  📊 {text}")


def separator(char: str = "-", length: int = 60) -> None:
    """Print a separator line.

    Args:
        char: Character to use for separation
        length: Length of the separator line
    """
    print(char * length)


def blank_line() -> None:
    """Print a blank line."""
    print()


def print_table(
    headers: list[str], rows: list[list[Any]], title: str | None = None
) -> None:
    """Print a formatted table.

    Args:
        headers: Column headers
        rows: Table data rows
        title: Optional table title
    """
    if title:
        h3(title)

    if not headers or not rows:
        return

    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Print header
    header_row = " | ".join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
    print(f"  {header_row}")
    print(f"  {'-' * len(header_row)}")

    # Print rows
    for row in rows:
        row_str = " | ".join(
            str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
        )
        print(f"  {row_str}")


def print_json(data: Any, title: str | None = None) -> None:
    """Print data in JSON format.

    Args:
        data: Data to print
        title: Optional title for the JSON output
    """
    if title:
        h3(title)

    try:
        import json

        formatted = json.dumps(data, indent=2, default=str)
        print(f"  {formatted}")
    except ImportError:
        # Fallback if json module not available
        print(f"  {data}")


def print_list(items: list[Any], title: str | None = None, bullet: str = "•") -> None:
    """Print a list of items.

    Args:
        items: List of items to print
        title: Optional title for the list
        bullet: Bullet character to use
    """
    if title:
        h3(title)

    for item in items:
        print(f"  {bullet} {item}")


def print_dict(data: dict[str, Any], title: str | None = None) -> None:
    """Print a dictionary in a readable format.

    Args:
        data: Dictionary to print
        title: Optional title for the dictionary
    """
    if title:
        h3(title)

    for key, value in data.items():
        print(f"  {key}: {value}")


def print_progress(current: int, total: int, description: str = "Progress") -> None:
    """Print a progress bar.

    Args:
        current: Current progress value
        total: Total value to reach
        description: Description of the progress
    """
    if total <= 0:
        return

    percentage = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)

    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    print(f"\r  {description}: |{bar}| {percentage:.1f}% ({current}/{total})", end="")

    if current >= total:
        print()  # New line when complete


def clear_line() -> None:
    """Clear the current line."""
    print("\r" + " " * 80 + "\r", end="")


def flush_output() -> None:
    """Flush stdout to ensure immediate output."""
    sys.stdout.flush()
