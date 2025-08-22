"""Utility modules for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import re
from uuid import UUID

from .run_renderer import (
    RichStreamRenderer,
    RunStats,
    Step,
    StepManager,
)

__all__ = [
    "RichStreamRenderer",
    "RunStats",
    "Step",
    "StepManager",
    "is_uuid",
    "sanitize_name",
    "format_file_size",
    "progress_bar",
]


def is_uuid(value: str) -> bool:
    """Check if a string is a valid UUID.

    Args:
        value: String to check

    Returns:
        True if value is a valid UUID, False otherwise
    """
    try:
        UUID(value)
        return True
    except (ValueError, TypeError):
        return False


def sanitize_name(name: str) -> str:
    """Sanitize a name for resource creation.

    Args:
        name: Raw name input

    Returns:
        Sanitized name suitable for resource creation
    """
    # Remove special characters and normalize
    sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "-", name.strip())
    sanitized = re.sub(r"-+", "-", sanitized)  # Collapse multiple dashes
    return sanitized.lower().strip("-")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Human readable size string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def progress_bar(iterable, description: str = "Processing"):
    """Simple progress bar using click.

    Args:
        iterable: Iterable to process
        description: Progress description

    Yields:
        Items from iterable with progress display
    """
    try:
        import click

        with click.progressbar(iterable, label=description) as bar:
            for item in bar:
                yield item
    except ImportError:
        # Fallback if click not available
        for item in iterable:
            yield item
