#!/usr/bin/env python3
"""Base client for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import logging
import os
from typing import Any, Union

import httpx
from dotenv import load_dotenv

from glaip_sdk.exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)

# Set up logging without basicConfig (library best practice)
logger = logging.getLogger("glaip_sdk")
logger.addHandler(logging.NullHandler())

client_log = logging.getLogger("glaip_sdk.client")
client_log.addHandler(logging.NullHandler())


class BaseClient:
    """Base client with HTTP operations and authentication."""

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
        *,
        parent_client: Union["BaseClient", None] = None,
        load_env: bool = True,
    ):
        """Initialize the base client.

        Args:
            api_url: API base URL
            api_key: API authentication key
            timeout: Request timeout in seconds
            parent_client: Parent client to adopt session/config from
            load_env: Whether to load environment variables
        """
        self._parent_client = parent_client

        if parent_client is not None:
            # Adopt parent's session/config; DO NOT call super().__init__
            client_log.debug("Adopting parent client configuration")
            self.api_url = parent_client.api_url
            self.api_key = parent_client.api_key
            self._timeout = parent_client._timeout
            self.http_client = parent_client.http_client
        else:
            # Initialize as standalone client
            if load_env:
                load_dotenv()

            self.api_url = api_url or os.getenv("AIP_API_URL")
            self.api_key = api_key or os.getenv("AIP_API_KEY")
            self._timeout = timeout

            if not self.api_url:
                client_log.error("AIP_API_URL not found in environment or parameters")
                raise ValueError("AIP_API_URL not found")
            if not self.api_key:
                client_log.error("AIP_API_KEY not found in environment or parameters")
                raise ValueError("AIP_API_KEY not found")

            client_log.info(f"Initializing client with API URL: {self.api_url}")
            self.http_client = self._build_client(timeout)

    def _build_client(self, timeout: float) -> httpx.Client:
        """Build HTTP client with configuration."""
        from glaip_sdk.config.constants import SDK_NAME, SDK_VERSION

        return httpx.Client(
            base_url=self.api_url,
            headers={
                "X-API-Key": self.api_key,
                "User-Agent": f"{SDK_NAME}/{SDK_VERSION}",
            },
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            http2=False,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=100),
        )

    @property
    def timeout(self) -> float:
        """Get current timeout value."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: float):
        """Set timeout and rebuild client."""
        self._timeout = value
        if (
            hasattr(self, "http_client")
            and self.http_client
            and not self._parent_client
        ):
            self.http_client.close()
            self.http_client = self._build_client(value)

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make HTTP request with error handling."""
        client_log.debug(f"Making {method} request to {endpoint}")
        try:
            response = self.http_client.request(method, endpoint, **kwargs)
            client_log.debug(f"Response status: {response.status_code}")
            return self._handle_response(response)
        except httpx.ConnectError as e:
            client_log.warning(
                f"Connection error on {method} {endpoint}, retrying once: {e}"
            )
            try:
                response = self.http_client.request(method, endpoint, **kwargs)
                client_log.debug(
                    f"Retry successful, response status: {response.status_code}"
                )
                return self._handle_response(response)
            except httpx.ConnectError:
                client_log.error(f"Retry failed for {method} {endpoint}: {e}")
                raise e

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response with proper error handling."""
        if response.status_code == 204:
            return None

        parsed = None
        content_type = response.headers.get("content-type", "").lower()
        if "json" in content_type:
            try:
                parsed = response.json()
            except ValueError:
                pass

        if parsed is None:
            if 200 <= response.status_code < 300:
                return response.text
            else:
                self._raise_api_error(response.status_code, response.text)

        if isinstance(parsed, dict) and "success" in parsed:
            if parsed.get("success"):
                return parsed.get("data", parsed)
            else:
                error_type = parsed.get("error", "UnknownError")
                message = parsed.get("message", "Unknown error")
                self._raise_api_error(
                    response.status_code, message, error_type, payload=parsed
                )

        if 200 <= response.status_code < 300:
            return parsed

        message = parsed.get("message") if isinstance(parsed, dict) else str(parsed)
        self._raise_api_error(response.status_code, message, payload=parsed)

    def _raise_api_error(
        self, status: int, message: str, error_type: str | None = None, *, payload=None
    ):
        """Raise appropriate exception with rich context."""
        request_id = None
        try:
            request_id = self.http_client.headers.get("X-Request-Id")
        except Exception:
            pass

        mapping = {
            400: ValidationError,
            401: AuthenticationError,
            403: ForbiddenError,
            404: NotFoundError,
            408: TimeoutError,
            409: ConflictError,
            429: RateLimitError,
            500: ServerError,
            503: ServerError,
            504: TimeoutError,
        }

        exception_class = mapping.get(status, ValidationError)
        error_msg = f"HTTP {status}: {message}"
        if request_id:
            error_msg += f" (Request ID: {request_id})"

        raise exception_class(
            error_msg,
            status_code=status,
            error_type=error_type,
            payload=payload,
            request_id=request_id,
        )

    def close(self):
        """Close the HTTP client."""
        if (
            hasattr(self, "http_client")
            and self.http_client
            and not self._parent_client
        ):
            self.http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
