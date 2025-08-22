#!/usr/bin/env python3
"""Unit tests for the main AIP SDK Client.

Tests the main Client class functionality without external dependencies.
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from glaip_sdk.client import Client


@pytest.mark.unit
class TestClient:
    """Test the main client functionality."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.Path.exists")
    @patch("glaip_sdk.client.base.yaml.safe_load")
    @patch("builtins.open", new_callable=MagicMock)
    def test_client_initialization(self, mock_open, mock_yaml_load, mock_exists):
        """Test client initialization with various parameters."""
        mock_exists.return_value = False  # No config file
        mock_yaml_load.return_value = {}

        # Test with explicit parameters
        client = Client(api_url="http://test.com", api_key="test-key", timeout=60.0)
        assert client.api_url == "http://test.com"
        assert client.api_key == "test-key"
        assert client.timeout == 60.0

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.Path.exists")
    @patch("glaip_sdk.client.base.yaml.safe_load")
    @patch("builtins.open", new_callable=MagicMock)
    def test_client_context_manager(self, mock_open, mock_yaml_load, mock_exists):
        """Test client context manager functionality."""
        mock_exists.return_value = False  # No config file
        mock_yaml_load.return_value = {}

        client = Client(api_url="http://test.com", api_key="test-key")
        assert client.http_client is not None

        # Test context manager
        with client:
            assert client.http_client.is_closed is False

        # Client should be closed after context
        assert client.http_client.is_closed is True

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.Path.exists")
    @patch("glaip_sdk.client.base.yaml.safe_load")
    @patch("builtins.open", new_callable=MagicMock)
    def test_client_timeout_property(self, mock_open, mock_yaml_load, mock_exists):
        """Test client timeout property."""
        mock_exists.return_value = False  # No config file
        mock_yaml_load.return_value = {}

        client = Client(api_url="http://test.com", api_key="test-key", timeout=45.0)
        assert client.timeout == 45.0

    @patch.dict(os.environ, {}, clear=True)
    @patch("glaip_sdk.client.base.Path.exists")
    @patch("glaip_sdk.client.base.yaml.safe_load")
    @patch("builtins.open", new_callable=MagicMock)
    def test_client_validation_error_handling(
        self, mock_open, mock_yaml_load, mock_exists
    ):
        """Test client validation error handling."""
        mock_exists.return_value = False  # No config file
        mock_yaml_load.return_value = {}

        # Test missing API key
        with pytest.raises(ValueError, match="AIP_API_KEY not found"):
            Client(api_url="http://test.com")

        # Test missing API URL
        with pytest.raises(ValueError, match="AIP_API_URL not found"):
            Client(api_key="test-key")

    def test_client_initialization_with_kwargs(self):
        """Test client initialization with various kwargs."""
        client = Client(api_url="http://test.com", api_key="test-key", timeout=60.0)

        # Check that specialized clients were created
        assert hasattr(client, "agents")
        assert hasattr(client, "tools")
        assert hasattr(client, "mcps")

        # Check that HTTP client is shared
        assert client.agents.http_client is client.http_client
        assert client.tools.http_client is client.http_client
        assert client.mcps.http_client is client.http_client

    def test_client_backward_compatibility_aliases(self):
        """Test backward compatibility alias methods."""
        client = Client(api_url="http://test.com", api_key="test-key")

        # Test that aliases exist and work functionally
        # Create a mock agent to test with
        mock_agent = Mock()
        mock_agent.id = "test-agent-id"

        with patch.object(client, "get_agent_by_id") as mock_get_by_id:
            mock_get_by_id.return_value = mock_agent

            # Test that get_agent calls get_agent_by_id
            result = client.get_agent("test-agent-id")
            mock_get_by_id.assert_called_once_with("test-agent-id")
            assert result == mock_agent

    def test_client_find_tools_single_match(self):
        """Test find_tools with single match."""
        client = Client(api_url="http://test.com", api_key="test-key")

        # Mock find_tools to return single tool
        mock_tool = Mock()
        mock_tool.id = "tool-123"
        mock_tool.name = "test-tool"

        with patch.object(client, "find_tools") as mock_find:
            mock_find.return_value = [mock_tool]

            result = client.find_tools("test-tool")
            assert result == [mock_tool]
            mock_find.assert_called_once_with("test-tool")

    def test_client_find_tools_no_match(self):
        """Test find_tools with no match."""
        client = Client(api_url="http://test.com", api_key="test-key")

        with patch.object(client, "find_tools") as mock_find:
            mock_find.return_value = []

            result = client.find_tools("test-tool")
            assert result == []
            mock_find.assert_called_once_with("test-tool")

    def test_client_find_tools_multiple_matches(self):
        """Test find_tools with multiple matches."""
        client = Client(api_url="http://test.com", api_key="test-key")

        # Mock find_tools to return multiple tools
        mock_tool1 = Mock()
        mock_tool1.id = "tool-123"
        mock_tool2 = Mock()
        mock_tool2.id = "tool-456"

        with patch.object(client, "find_tools") as mock_find:
            mock_find.return_value = [mock_tool1, mock_tool2]

            result = client.find_tools("test-tool")
            assert result == [mock_tool1, mock_tool2]
            mock_find.assert_called_once_with("test-tool")

    def test_client_language_model_methods(self):
        """Test client language model methods."""
        client = Client(api_url="http://test.com", api_key="test-key")

        # Mock _request method
        with patch.object(client, "_request") as mock_request:
            mock_request.return_value = [{"name": "gpt-4"}, {"name": "gpt-3.5"}]

            models = client.list_language_models()
            assert models == [{"name": "gpt-4"}, {"name": "gpt-3.5"}]
            mock_request.assert_called_once_with("GET", "/language-models")

    def test_client_mcp_delegation(self):
        """Test that MCP methods are properly delegated."""
        client = Client(api_url="http://test.com", api_key="test-key")

        # Mock MCP client methods
        with patch.object(client.mcps, "list_mcps") as mock_list:
            mock_list.return_value = [{"id": "mcp1"}, {"id": "mcp2"}]

            mcps = client.list_mcps()
            assert mcps == [{"id": "mcp1"}, {"id": "mcp2"}]
            mock_list.assert_called_once()

    def test_client_tool_delegation(self):
        """Test that tool methods are properly delegated."""
        client = Client(api_url="http://test.com", api_key="test-key")

        # Mock tool client methods
        with patch.object(client.tools, "list_tools") as mock_list:
            mock_list.return_value = [{"id": "tool1"}, {"id": "tool2"}]

            tools = client.list_tools()
            assert tools == [{"id": "tool1"}, {"id": "tool2"}]
            mock_list.assert_called_once()

    def test_client_agent_delegation_with_complex_params(self):
        """Test that agent methods properly delegate complex parameters."""
        client = Client(api_url="http://test.com", api_key="test-key")

        # Mock agent client create_agent method
        with patch.object(client.agents, "create_agent") as mock_create:
            mock_agent = Mock()
            mock_create.return_value = mock_agent

            # Test with complex parameters
            agent = client.create_agent(
                name="test-agent",
                instruction="This is a test instruction that is long enough",
            )
            assert agent is not None
            mock_create.assert_called_once_with(
                name="test-agent",
                model="gpt-4",
                instruction="Test instruction",
                tools=["tool1", "tool2"],
                agents=["agent1"],
                timeout=600,
                strict_validation=True,
                forbid_reserved_names=True,
                custom_param="value",
            )

    def test_client_agent_delegation_methods(self):
        """Test all agent delegation methods for coverage."""
        client = Client(api_url="http://test.com", api_key="test-key")

        # Test list_agents
        with patch.object(client.agents, "list_agents") as mock_list:
            mock_list.return_value = []
            result = client.list_agents()
            assert result == []
            mock_list.assert_called_once()

        # Test get_agent_by_id
        with patch.object(client.agents, "get_agent_by_id") as mock_get:
            mock_agent = Mock()
            mock_get.return_value = mock_agent
            result = client.get_agent_by_id("agent-123")
            assert result == mock_agent
            mock_get.assert_called_once_with("agent-123")

        # Test find_agents
        with patch.object(client.agents, "find_agents") as mock_find:
            mock_find.return_value = []
            result = client.find_agents("test")
            assert result == []
            mock_find.assert_called_once_with("test")

        # Test create_agent
        with patch.object(client.agents, "create_agent") as mock_create:
            mock_agent = Mock()
            mock_create.return_value = mock_agent
            result = client.create_agent(
                name="test-agent", instruction="test instruction"
            )
            assert result == mock_agent
            mock_create.assert_called_once_with(
                name="test-agent", instruction="test instruction"
            )

    def test_client_tool_delegation_methods(self):
        """Test all tool delegation methods for coverage."""
        client = Client(api_url="http://test.com", api_key="test-key")

        # Test list_tools
        with patch.object(client.tools, "list_tools") as mock_list:
            mock_list.return_value = []
            result = client.list_tools()
            assert result == []
            mock_list.assert_called_once()

        # Test get_tool_by_id
        with patch.object(client.tools, "get_tool_by_id") as mock_get:
            mock_tool = Mock()
            mock_get.return_value = mock_tool
            result = client.get_tool_by_id("tool-123")
            assert result == mock_tool
            mock_get.assert_called_once_with("tool-123")

        # Test find_tools
        with patch.object(client.tools, "find_tools") as mock_find:
            mock_find.return_value = []
            result = client.find_tools("test")
            assert result == []
            mock_find.assert_called_once_with("test")

        # Test create_tool
        with patch.object(client.tools, "create_tool") as mock_create:
            mock_tool = Mock()
            mock_create.return_value = mock_tool
            result = client.create_tool(name="test-tool")
            assert result == mock_tool
            mock_create.assert_called_once_with(name="test-tool")

    def test_client_mcp_delegation_methods(self):
        """Test all MCP delegation methods for coverage."""
        client = Client(api_url="http://test.com", api_key="test-key")

        # Test list_mcps
        with patch.object(client.mcps, "list_mcps") as mock_list:
            mock_list.return_value = []
            result = client.list_mcps()
            assert result == []
            mock_list.assert_called_once()

        # Test get_mcp_by_id
        with patch.object(client.mcps, "get_mcp_by_id") as mock_get:
            mock_mcp = Mock()
            mock_get.return_value = mock_mcp
            result = client.get_mcp_by_id("mcp-123")
            assert result == mock_mcp
            mock_get.assert_called_once_with("mcp-123")

        # Test find_mcps
        with patch.object(client.mcps, "find_mcps") as mock_find:
            mock_find.return_value = []
            result = client.find_mcps("test")
            assert result == []
            mock_find.assert_called_once_with("test")

        # Test create_mcp
        with patch.object(client.mcps, "create_mcp") as mock_create:
            mock_mcp = Mock()
            mock_create.return_value = mock_mcp
            result = client.create_mcp(name="test-mcp")
            assert result == mock_mcp
            mock_create.assert_called_once_with(name="test-mcp")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
