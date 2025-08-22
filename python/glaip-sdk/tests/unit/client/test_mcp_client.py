#!/usr/bin/env python3
"""Unit tests for the AIP SDK MCPClient.

Tests the MCPClient class functionality without external dependencies.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from glaip_sdk.client.mcps import MCPClient


@pytest.mark.unit
class TestMCPClient:
    """Test the MCP client functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        with (
            patch("glaip_sdk.client.base.Path.exists") as mock_exists,
            patch("glaip_sdk.client.base.yaml.safe_load") as mock_yaml_load,
            patch("builtins.open", new_callable=MagicMock),
        ):
            mock_exists.return_value = False  # No config file
            mock_yaml_load.return_value = {}
            self.client = MCPClient(api_url="http://test.com", api_key="test-key")

    @patch.object(MCPClient, "_request")
    def test_list_mcps(self, mock_request):
        """Test listing MCPs."""
        mock_response_data = [
            {"id": str(uuid4()), "name": "mcp1", "description": "Test MCP"}
        ]
        mock_request.return_value = mock_response_data

        mcps = self.client.list_mcps()
        assert len(mcps) == 1
        assert mcps[0].name == "mcp1"
        mock_request.assert_called_once_with("GET", "/mcps")

    @patch.object(MCPClient, "_request")
    def test_get_mcp_by_id(self, mock_request):
        """Test getting MCP by ID."""
        mcp_id = str(uuid4())
        mock_response_data = {
            "id": mcp_id,
            "name": "test-mcp",
            "description": "Test MCP",
        }
        mock_request.return_value = mock_response_data

        mcp = self.client.get_mcp_by_id(mcp_id)
        assert str(mcp.id) == mcp_id
        assert mcp.name == "test-mcp"
        mock_request.assert_called_once_with("GET", f"/mcps/{mcp_id}")

    @patch.object(MCPClient, "_request")
    def test_create_mcp(self, mock_request):
        """Test creating an MCP."""
        mcp_id = str(uuid4())
        mock_response_data = {"id": mcp_id, "name": "new-mcp", "description": "New MCP"}
        mock_request.return_value = mock_response_data

        mcp = self.client.create_mcp(
            name="new-mcp", description="New MCP", config={"url": "https://test.com"}
        )
        assert str(mcp.id) == mcp_id
        assert mcp.name == "new-mcp"

        # Verify the request was made
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"  # method
        assert call_args[0][1] == "/mcps"  # endpoint

    @patch.object(MCPClient, "_request")
    def test_update_mcp(self, mock_request):
        """Test updating an MCP."""
        mcp_id = str(uuid4())
        mock_response_data = {
            "id": mcp_id,
            "name": "updated-mcp",
            "description": "Updated",
        }
        mock_request.return_value = mock_response_data

        # MCPClient.update_mcp uses **kwargs
        mcp = self.client.update_mcp(mcp_id, name="updated-mcp")
        assert str(mcp.id) == mcp_id
        assert mcp.name == "updated-mcp"
        mock_request.assert_called_once_with(
            "PUT", f"/mcps/{mcp_id}", json={"name": "updated-mcp"}
        )

    @patch.object(MCPClient, "_request")
    def test_delete_mcp(self, mock_request):
        """Test deleting an MCP."""
        mcp_id = str(uuid4())
        mock_request.return_value = {"success": True}

        result = self.client.delete_mcp(mcp_id)
        assert result is True
        mock_request.assert_called_once_with("DELETE", f"/mcps/{mcp_id}")

    @patch.object(MCPClient, "_request")
    def test_find_mcps(self, mock_request):
        """Test finding MCPs by name."""
        # MCPClient.find_mcps gets all MCPs and filters client-side
        mock_response_data = [
            {"id": str(uuid4()), "name": "test-mcp-1", "description": "Test 1"},
            {"id": str(uuid4()), "name": "test-mcp-2", "description": "Test 2"},
            {"id": str(uuid4()), "name": "other-mcp", "description": "Other"},
        ]
        mock_request.return_value = mock_response_data

        mcps = self.client.find_mcps("test")
        assert len(mcps) == 2
        assert all("test" in mcp.name for mcp in mcps)
        # MCPClient.find_mcps calls GET /mcps without params and filters client-side
        mock_request.assert_called_once_with("GET", "/mcps")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
