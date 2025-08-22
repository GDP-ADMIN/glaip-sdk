#!/usr/bin/env python3
"""Unit tests for the AIP SDK ToolClient.

Tests the ToolClient class functionality without external dependencies.
"""

from unittest.mock import patch
from uuid import uuid4

import pytest

from glaip_sdk.client.tools import ToolClient


@pytest.mark.unit
class TestToolClient:
    """Test the tool client functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch("glaip_sdk.client.base.load_dotenv"):
            self.client = ToolClient(api_url="http://test.com", api_key="test-key")

    @patch.object(ToolClient, "_request")
    def test_list_tools(self, mock_request):
        """Test listing tools."""
        mock_response_data = [
            {"id": str(uuid4()), "name": "tool1", "description": "Test tool"}
        ]
        mock_request.return_value = mock_response_data

        tools = self.client.list_tools()
        assert len(tools) == 1
        assert tools[0].name == "tool1"
        mock_request.assert_called_once_with("GET", "/tools/")

    @patch.object(ToolClient, "_request")
    def test_get_tool_by_id(self, mock_request):
        """Test getting tool by ID."""
        tool_id = str(uuid4())
        mock_response_data = {
            "id": tool_id,
            "name": "test-tool",
            "description": "Test tool",
        }
        mock_request.return_value = mock_response_data

        tool = self.client.get_tool_by_id(tool_id)
        assert str(tool.id) == tool_id
        assert tool.name == "test-tool"
        mock_request.assert_called_once_with("GET", f"/tools/{tool_id}")

    @patch.object(ToolClient, "_request")
    def test_create_tool(self, mock_request):
        """Test creating a tool."""
        tool_id = str(uuid4())
        mock_response_data = {
            "id": tool_id,
            "name": "new-tool",
            "description": "New tool",
        }
        mock_request.return_value = mock_response_data

        # ToolClient.create_tool uses **kwargs, so test with simple kwargs
        tool = self.client.create_tool(name="new-tool", description="New tool")
        assert str(tool.id) == tool_id
        assert tool.name == "new-tool"

        # Verify the request was made to /tools/ endpoint (not /tools/upload)
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "POST"  # method
        assert call_args[0][1] == "/tools/"  # endpoint

    @patch.object(ToolClient, "_request")
    def test_update_tool(self, mock_request):
        """Test updating a tool."""
        tool_id = str(uuid4())
        mock_response_data = {
            "id": tool_id,
            "name": "updated-tool",
            "description": "Updated",
        }
        mock_request.return_value = mock_response_data

        # ToolClient.update_tool uses **kwargs
        tool = self.client.update_tool(tool_id, name="updated-tool")
        assert str(tool.id) == tool_id
        assert tool.name == "updated-tool"
        mock_request.assert_called_once_with(
            "PUT", f"/tools/{tool_id}", json={"name": "updated-tool"}
        )

    @patch.object(ToolClient, "_request")
    def test_delete_tool(self, mock_request):
        """Test deleting a tool."""
        tool_id = str(uuid4())
        mock_request.return_value = {"success": True}

        result = self.client.delete_tool(tool_id)
        assert result is None  # delete_tool returns None
        mock_request.assert_called_once_with("DELETE", f"/tools/{tool_id}")

    @patch.object(ToolClient, "_request")
    def test_find_tools(self, mock_request):
        """Test finding tools by name."""
        mock_response_data = [
            {"id": str(uuid4()), "name": "test-tool-1", "description": "Test 1"},
            {"id": str(uuid4()), "name": "test-tool-2", "description": "Test 2"},
        ]
        mock_request.return_value = mock_response_data

        tools = self.client.find_tools("test")
        assert len(tools) == 2
        assert all("test" in tool.name for tool in tools)
        mock_request.assert_called_once_with("GET", "/tools/")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
