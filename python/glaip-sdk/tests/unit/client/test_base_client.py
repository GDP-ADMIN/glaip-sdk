#!/usr/bin/env python3
"""Unit tests for the AIP SDK BaseClient.

Tests the BaseClient class functionality without external dependencies.
"""

import os
from unittest.mock import Mock, patch

import httpx
import pytest

from glaip_sdk.client.base import BaseClient
from glaip_sdk.exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ServerError,
    ValidationError,
)


@pytest.mark.unit
class TestBaseClient:
    """Test the base client functionality."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_initialization(self, mock_load_dotenv):
        """Test base client initialization."""
        client = BaseClient(api_url="http://test.com", api_key="test-key", timeout=60.0)
        assert client.api_url == "http://test.com"
        assert client.api_key == "test-key"
        assert client._timeout == 60.0
        mock_load_dotenv.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_request_retry_logic(self, mock_load_dotenv):
        """Test base client request retry logic."""
        client = BaseClient(api_url="http://test.com", api_key="test-key")

        # Mock httpx client to raise ConnectError
        with patch.object(client.http_client, "request") as mock_request:
            mock_request.side_effect = httpx.ConnectError("Connection failed")

            with pytest.raises(httpx.ConnectError):
                client._request("GET", "/test")

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_response_handling(self, mock_load_dotenv):
        """Test base client response handling."""
        client = BaseClient(api_url="http://test.com", api_key="test-key")

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_response.content = b'{"success": True, "data": "test"}'
        mock_response.headers = {"content-type": "application/json"}

        # Test successful response
        data = client._handle_response(mock_response)
        assert data == "test"

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_error_mapping(self, mock_load_dotenv):
        """Test base client error status code mapping."""
        client = BaseClient(api_url="http://test.com", api_key="test-key")

        # Test various error status codes
        error_codes = {
            400: ValidationError,
            401: AuthenticationError,
            403: ForbiddenError,
            404: NotFoundError,
            409: ConflictError,
            500: ServerError,
        }

        for status_code, expected_exception in error_codes.items():
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.text = f"Error {status_code}"
            mock_response.headers = {"content-type": "text/plain"}

            with pytest.raises(expected_exception):
                client._handle_response(mock_response)

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_headers_safe(self, mock_load_dotenv):
        """Test base client headers are safe."""
        client = BaseClient(api_url="http://test.com", api_key="test-key")

        # Check that API key is properly set in X-API-Key header
        assert "X-API-Key" in client.http_client.headers
        assert client.http_client.headers["X-API-Key"] == "test-key"

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_timeout_setter(self, mock_load_dotenv):
        """Test base client timeout setter rebuilds client."""
        client = BaseClient(api_url="http://test.com", api_key="test-key")
        original_client = client.http_client

        # Change timeout
        client.timeout = 120.0

        # Check that timeout was updated
        assert client._timeout == 120.0
        # Check that client was rebuilt (different object)
        assert client.http_client is not original_client

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_parent_client_pattern(self, mock_load_dotenv):
        """Test base client parent-client pattern."""
        parent = BaseClient(api_url="http://parent.com", api_key="parent-key")
        child = BaseClient(parent_client=parent)

        # Child should adopt parent's configuration
        assert child.api_url == parent.api_url
        assert child.api_key == parent.api_key
        assert child._timeout == parent._timeout
        assert child.http_client is parent.http_client
        assert child._parent_client is parent

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_parent_client_timeout_setter(self, mock_load_dotenv):
        """Test that child clients don't rebuild parent's client on timeout change."""
        parent = BaseClient(api_url="http://parent.com", api_key="parent-key")
        child = BaseClient(parent_client=parent)
        original_parent_client = parent.http_client

        # Change child timeout - should not affect parent
        child.timeout = 120.0

        # Parent client should remain unchanged
        assert parent.http_client is original_parent_client
        # Child timeout should be updated but client not rebuilt
        assert child._timeout == 120.0
        assert child.http_client is original_parent_client

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_context_manager(self, mock_load_dotenv):
        """Test base client context manager."""
        with BaseClient(api_url="http://test.com", api_key="test-key") as client:
            assert client.api_url == "http://test.com"
            # Client should be closed when exiting context
            assert hasattr(client, "close")

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_no_env_vars(self, mock_load_dotenv):
        """Test base client fails without environment variables."""
        with pytest.raises(ValueError, match="AIP_API_URL not found"):
            BaseClient()

        with pytest.raises(ValueError, match="AIP_API_KEY not found"):
            BaseClient(api_url="http://test.com")

    @patch.dict(
        os.environ,
        {"AIP_API_URL": "http://env.com", "AIP_API_KEY": "env-key"},
        clear=True,
    )
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_env_vars(self, mock_load_dotenv):
        """Test base client uses environment variables."""
        client = BaseClient()
        assert client.api_url == "http://env.com"
        assert client.api_key == "env-key"

    @patch.dict(
        os.environ,
        {"AIP_API_URL": "http://env.com", "AIP_API_KEY": "env-key"},
        clear=True,
    )
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_kwargs_override_env(self, mock_load_dotenv):
        """Test base client kwargs override environment variables."""
        client = BaseClient(api_url="http://kwarg.com", api_key="kwarg-key")
        assert client.api_url == "http://kwarg.com"
        assert client.api_key == "kwarg-key"

    @patch.dict(
        os.environ,
        {"AIP_API_URL": "http://env.com", "AIP_API_KEY": "env-key"},
        clear=True,
    )
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_optional_dotenv(self, mock_load_dotenv):
        """Test base client can disable dotenv loading."""
        client = BaseClient(load_env=False)
        mock_load_dotenv.assert_not_called()
        assert client.api_url == "http://env.com"
        assert client.api_key == "env-key"

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_http2_enabled(self, mock_load_dotenv):
        """Test base client connection limits are configured."""
        client = BaseClient(api_url="http://test.com", api_key="test-key")

        # Check that the client was created successfully with limits configuration
        assert client.http_client is not None
        assert hasattr(client.http_client, "timeout")
        assert client.http_client.timeout.connect == 30.0

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.load_dotenv")
    def test_base_client_user_agent(self, mock_load_dotenv):
        """Test base client sets proper user agent."""
        client = BaseClient(api_url="http://test.com", api_key="test-key")

        # Check that user agent is set
        assert "User-Agent" in client.http_client.headers
        assert "glaip-sdk" in client.http_client.headers["User-Agent"]
