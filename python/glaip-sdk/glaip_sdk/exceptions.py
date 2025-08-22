#!/usr/bin/env python3
"""Custom exceptions for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from typing import Any


class AIPError(Exception):
    """Base exception for AIP SDK."""

    pass


class APIError(AIPError):
    """Base API exception with rich context."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_type: str | None = None,
        payload: Any = None,
        request_id: str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_type = error_type
        self.payload = payload
        self.request_id = request_id


class AuthenticationError(APIError):
    """Authentication failed."""

    pass


class ValidationError(APIError):
    """Validation failed."""

    pass


class ForbiddenError(APIError):
    """Access forbidden."""

    pass


class NotFoundError(APIError):
    """Resource not found."""

    pass


class ConflictError(APIError):
    """Resource conflict."""

    pass


class AmbiguousResourceError(APIError):
    """Multiple resources match the query."""

    pass


class ServerError(APIError):
    """Server error."""

    pass


class RateLimitError(APIError):
    """Rate limit exceeded."""

    pass


class TimeoutError(APIError):
    """Request timeout."""

    pass


class ClientError(APIError):
    """Client-side error (e.g., invalid request format, missing parameters)."""

    pass
