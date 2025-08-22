#!/usr/bin/env python3
"""Unit tests for data models.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from unittest.mock import Mock, patch

import pytest

from glaip_sdk.models import MCP, Agent, LanguageModelResponse, Tool, TTYRenderer


class TestAgent:
    """Test the Agent model."""

    def test_agent_creation_with_minimal_fields(self):
        """Test creating an agent with only required fields."""
        agent = Agent(id="test-id", name="Test Agent", instruction="Test instruction")

        assert agent.id == "test-id"
        assert agent.name == "Test Agent"
        assert agent.instruction == "Test instruction"
        assert agent.description is None
        assert agent.type is None
        assert agent.framework is None
        assert agent.version is None
        assert agent.tools is None
        assert agent.agents is None
        assert agent.agent_config is None
        assert agent.timeout == 300
        assert agent.metadata is None
        assert agent.language_model_id is None
        assert agent.a2a_profile is None
        assert agent._client is None

    def test_agent_creation_with_all_fields(self):
        """Test creating an agent with all fields."""
        agent = Agent(
            id="test-id",
            name="Test Agent",
            instruction="Test instruction",
            description="Test description",
            type="assistant",
            framework="openai",
            version="1.0.0",
            tools=[{"id": "tool1", "name": "Test Tool"}],
            agents=[{"id": "agent1", "name": "Sub Agent"}],
            agent_config={"model": "gpt-4"},
            timeout=600,
            metadata={"tags": ["test", "demo"]},
            language_model_id="gpt-4",
            a2a_profile={"capabilities": ["reasoning"]},
        )

        assert agent.id == "test-id"
        assert agent.name == "Test Agent"
        assert agent.instruction == "Test instruction"
        assert agent.description == "Test description"
        assert agent.type == "assistant"
        assert agent.framework == "openai"
        assert agent.version == "1.0.0"
        assert agent.tools == [{"id": "tool1", "name": "Test Tool"}]
        assert agent.agents == [{"id": "agent1", "name": "Sub Agent"}]
        assert agent.agent_config == {"model": "gpt-4"}
        assert agent.timeout == 600
        assert agent.metadata == {"tags": ["test", "demo"]}
        assert agent.language_model_id == "gpt-4"
        assert agent.a2a_profile == {"capabilities": ["reasoning"]}

    def test_agent_set_client(self):
        """Test setting client reference."""
        agent = Agent(id="test-id", name="Test Agent")
        mock_client = Mock()

        result = agent._set_client(mock_client)

        assert result is agent
        assert agent._client is mock_client

    def test_agent_run_without_client(self):
        """Test running agent without client raises error."""
        agent = Agent(id="test-id", name="Test Agent")

        with pytest.raises(RuntimeError, match="No client available"):
            agent.run("test message")

    def test_agent_run_with_client(self):
        """Test running agent with client."""
        agent = Agent(id="test-id", name="Test Agent")
        mock_client = Mock()
        mock_client.run_agent.return_value = "test response"
        agent._set_client(mock_client)

        result = agent.run("test message")

        assert result == "test response"
        mock_client.run_agent.assert_called_once_with(
            "test-id", "test message", agent_name="Test Agent"
        )

    def test_agent_run_with_kwargs(self):
        """Test running agent with additional kwargs."""
        agent = Agent(id="test-id", name="Test Agent")
        mock_client = Mock()
        mock_client.run_agent.return_value = "test response"
        agent._set_client(mock_client)

        result = agent.run("test message", temperature=0.7, max_tokens=100)

        assert result == "test response"
        mock_client.run_agent.assert_called_once_with(
            "test-id",
            "test message",
            agent_name="Test Agent",
            temperature=0.7,
            max_tokens=100,
        )

    def test_agent_update_without_client(self):
        """Test updating agent without client raises error."""
        agent = Agent(id="test-id", name="Test Agent")

        with pytest.raises(RuntimeError, match="No client available"):
            agent.update(name="New Name")

    def test_agent_update_with_client(self):
        """Test updating agent with client."""
        agent = Agent(id="test-id", name="Test Agent")
        mock_client = Mock()
        updated_agent = Agent(
            id="test-id", name="Updated Agent", description="New description"
        )
        mock_client.update_agent.return_value = updated_agent
        agent._set_client(mock_client)

        result = agent.update(name="Updated Agent", description="New description")

        assert result is agent
        assert agent.name == "Updated Agent"
        assert agent.description == "New description"
        mock_client.update_agent.assert_called_once_with(
            "test-id", name="Updated Agent", description="New description"
        )

    def test_agent_delete_without_client(self):
        """Test deleting agent without client raises error."""
        agent = Agent(id="test-id", name="Test Agent")

        with pytest.raises(RuntimeError, match="No client available"):
            agent.delete()

    def test_agent_delete_with_client(self):
        """Test deleting agent with client."""
        agent = Agent(id="test-id", name="Test Agent")
        mock_client = Mock()
        agent._set_client(mock_client)

        agent.delete()

        mock_client.delete_agent.assert_called_once_with("test-id")


class TestTool:
    """Test the Tool model."""

    def test_tool_creation_with_minimal_fields(self):
        """Test creating a tool with only required fields."""
        tool = Tool(id="tool-id", name="Test Tool")

        assert tool.id == "tool-id"
        assert tool.name == "Test Tool"
        assert tool.tool_type is None
        assert tool.description is None
        assert tool.framework is None
        assert tool.version is None
        assert tool.tool_script is None
        assert tool.tool_file is None
        assert tool._client is None

    def test_tool_creation_with_all_fields(self):
        """Test creating a tool with all fields."""
        tool = Tool(
            id="tool-id",
            name="Test Tool",
            tool_type="function",
            description="Test tool description",
            framework="python",
            version="1.0.0",
            tool_script="def test(): pass",
            tool_file="test.py",
        )

        assert tool.id == "tool-id"
        assert tool.name == "Test Tool"
        assert tool.tool_type == "function"
        assert tool.description == "Test tool description"
        assert tool.framework == "python"
        assert tool.version == "1.0.0"
        assert tool.tool_script == "def test(): pass"
        assert tool.tool_file == "test.py"

    def test_tool_set_client(self):
        """Test setting client reference."""
        tool = Tool(id="tool-id", name="Test Tool")
        mock_client = Mock()

        result = tool._set_client(mock_client)

        assert result is tool
        assert tool._client is mock_client

    def test_tool_get_script_with_script(self):
        """Test getting script when tool_script is available."""
        tool = Tool(id="tool-id", name="Test Tool", tool_script="def test(): pass")

        result = tool.get_script()

        assert result == "def test(): pass"

    def test_tool_get_script_with_file(self):
        """Test getting script when only tool_file is available."""
        tool = Tool(id="tool-id", name="Test Tool", tool_file="test.py")

        result = tool.get_script()

        assert result == "Script content from file: test.py"

    def test_tool_get_script_without_content(self):
        """Test getting script when neither script nor file is available."""
        tool = Tool(id="tool-id", name="Test Tool")

        result = tool.get_script()

        assert result == "No script content available"

    def test_tool_update_without_client(self):
        """Test updating tool without client raises error."""
        tool = Tool(id="tool-id", name="Test Tool")

        with pytest.raises(RuntimeError, match="No client available"):
            tool.update(name="New Name")

    def test_tool_update_with_client(self):
        """Test updating tool with client."""
        tool = Tool(id="tool-id", name="Test Tool")
        mock_client = Mock()
        mock_client.tools = Mock()
        updated_tool = Tool(
            id="tool-id", name="Updated Tool", description="New description"
        )
        mock_client.tools.update_tool.return_value = updated_tool
        tool._set_client(mock_client)

        result = tool.update(name="Updated Tool", description="New description")

        assert result is tool
        assert tool.name == "Updated Tool"
        assert tool.description == "New description"
        mock_client.tools.update_tool.assert_called_once_with(
            "tool-id", name="Updated Tool", description="New description"
        )

    def test_tool_delete_without_client(self):
        """Test deleting tool without client raises error."""
        tool = Tool(id="tool-id", name="Test Tool")

        with pytest.raises(RuntimeError, match="No client available"):
            tool.delete()

    def test_tool_delete_with_client(self):
        """Test deleting tool with client."""
        tool = Tool(id="tool-id", name="Test Tool")
        mock_client = Mock()
        mock_client.tools = Mock()
        tool._set_client(mock_client)

        tool.delete()

        mock_client.tools.delete_tool.assert_called_once_with("tool-id")


class TestMCP:
    """Test the MCP model."""

    def test_mcp_creation_with_minimal_fields(self):
        """Test creating an MCP with only required fields."""
        mcp = MCP(id="mcp-id", name="Test MCP")

        assert mcp.id == "mcp-id"
        assert mcp.name == "Test MCP"
        assert mcp.description is None
        assert mcp.config is None
        assert mcp.framework is None
        assert mcp.version is None
        assert mcp.transport is None
        assert mcp.authentication is None
        assert mcp.metadata is None
        assert mcp._client is None

    def test_mcp_creation_with_all_fields(self):
        """Test creating an MCP with all fields."""
        mcp = MCP(
            id="mcp-id",
            name="Test MCP",
            description="Test MCP description",
            config={"endpoint": "http://example.com"},
            framework="python",
            version="1.0.0",
            transport="http",
            authentication={"type": "bearer"},
            metadata={"tags": ["test"]},
        )

        assert mcp.id == "mcp-id"
        assert mcp.name == "Test MCP"
        assert mcp.description == "Test MCP description"
        assert mcp.config == {"endpoint": "http://example.com"}
        assert mcp.framework == "python"
        assert mcp.version == "1.0.0"
        assert mcp.transport == "http"
        assert mcp.authentication == {"type": "bearer"}
        assert mcp.metadata == {"tags": ["test"]}

    def test_mcp_set_client(self):
        """Test setting client reference."""
        mcp = MCP(id="mcp-id", name="Test MCP")
        mock_client = Mock()

        result = mcp._set_client(mock_client)

        assert result is mcp
        assert mcp._client is mock_client

    def test_mcp_get_tools_without_client(self):
        """Test getting tools without client raises error."""
        mcp = MCP(id="mcp-id", name="Test MCP")

        with pytest.raises(RuntimeError, match="No client available"):
            mcp.get_tools()

    def test_mcp_get_tools_with_client(self):
        """Test getting tools with client (placeholder implementation)."""
        mcp = MCP(id="mcp-id", name="Test MCP")
        mock_client = Mock()
        mcp._set_client(mock_client)

        result = mcp.get_tools()

        # Currently returns empty list as placeholder
        assert result == []

    def test_mcp_update_without_client(self):
        """Test updating MCP without client raises error."""
        mcp = MCP(id="mcp-id", name="Test MCP")

        with pytest.raises(RuntimeError, match="No client available"):
            mcp.update(name="New Name")

    def test_mcp_update_with_client(self):
        """Test updating MCP with client."""
        mcp = MCP(id="mcp-id", name="Test MCP")
        mock_client = Mock()
        updated_mcp = MCP(
            id="mcp-id", name="Updated MCP", description="New description"
        )
        mock_client.update_mcp.return_value = updated_mcp
        mcp._set_client(mock_client)

        result = mcp.update(name="Updated MCP", description="New description")

        assert result is mcp
        assert mcp.name == "Updated MCP"
        assert mcp.description == "New description"
        mock_client.update_mcp.assert_called_once_with(
            "mcp-id", name="Updated MCP", description="New description"
        )

    def test_mcp_delete_without_client(self):
        """Test deleting MCP without client raises error."""
        mcp = MCP(id="mcp-id", name="Test MCP")

        with pytest.raises(RuntimeError, match="No client available"):
            mcp.delete()

    def test_mcp_delete_with_client(self):
        """Test deleting MCP with client."""
        mcp = MCP(id="mcp-id", name="Test MCP")
        mock_client = Mock()
        mcp._set_client(mock_client)

        mcp.delete()

        mock_client.delete_mcp.assert_called_once_with("mcp-id")


class TestLanguageModelResponse:
    """Test the LanguageModelResponse model."""

    def test_language_model_response_creation_with_minimal_fields(self):
        """Test creating a language model response with only required fields."""
        response = LanguageModelResponse(name="gpt-4", provider="openai")

        assert response.name == "gpt-4"
        assert response.provider == "openai"
        assert response.description is None
        assert response.capabilities is None
        assert response.max_tokens is None
        assert response.supports_streaming is False

    def test_language_model_response_creation_with_all_fields(self):
        """Test creating a language model response with all fields."""
        response = LanguageModelResponse(
            name="gpt-4",
            provider="openai",
            description="Advanced language model",
            capabilities=["text-generation", "reasoning"],
            max_tokens=8192,
            supports_streaming=True,
        )

        assert response.name == "gpt-4"
        assert response.provider == "openai"
        assert response.description == "Advanced language model"
        assert response.capabilities == ["text-generation", "reasoning"]
        assert response.max_tokens == 8192
        assert response.supports_streaming is True


class TestTTYRenderer:
    """Test the TTYRenderer class."""

    def test_tty_renderer_initialization_with_color(self):
        """Test TTY renderer initialization with color enabled."""
        renderer = TTYRenderer(use_color=True)
        assert renderer.use_color is True

    def test_tty_renderer_initialization_without_color(self):
        """Test TTY renderer initialization with color disabled."""
        renderer = TTYRenderer(use_color=False)
        assert renderer.use_color is False

    def test_tty_renderer_render_message_default(self):
        """Test rendering default message."""
        renderer = TTYRenderer()

        with patch("builtins.print") as mock_print:
            renderer.render_message("test message")
            mock_print.assert_called_once_with("test message", flush=True)

    def test_tty_renderer_render_message_error(self):
        """Test rendering error message."""
        renderer = TTYRenderer()

        with patch("builtins.print") as mock_print:
            renderer.render_message("error occurred", "error")
            mock_print.assert_called_once_with("ERROR: error occurred", flush=True)

    def test_tty_renderer_render_message_done(self):
        """Test rendering done message."""
        renderer = TTYRenderer()

        with patch("builtins.print") as mock_print:
            renderer.render_message("task completed", "done")
            mock_print.assert_called_once_with("\n✅ task completed", flush=True)

    def test_tty_renderer_render_message_custom_type(self):
        """Test rendering message with custom event type."""
        renderer = TTYRenderer()

        with patch("builtins.print") as mock_print:
            renderer.render_message("custom message", "custom")
            mock_print.assert_called_once_with("custom message", flush=True)


class TestModelIntegration:
    """Test integration between models."""

    def test_agent_with_tools_and_sub_agents(self):
        """Test agent with tools and sub-agents."""
        tool = Tool(id="tool1", name="Calculator")
        sub_agent = Agent(id="agent1", name="Math Specialist")

        agent = Agent(
            id="main-agent",
            name="Main Agent",
            tools=[{"id": tool.id, "name": tool.name}],
            agents=[{"id": sub_agent.id, "name": sub_agent.name}],
        )

        assert len(agent.tools) == 1
        assert len(agent.agents) == 1
        assert agent.tools[0]["id"] == "tool1"
        assert agent.agents[0]["id"] == "agent1"

    def test_model_serialization(self):
        """Test that models can be serialized to dict."""
        agent = Agent(
            id="test-id",
            name="Test Agent",
            instruction="Test instruction",
            metadata={"tags": ["test"]},
        )

        agent_dict = agent.model_dump()

        assert agent_dict["id"] == "test-id"
        assert agent_dict["name"] == "Test Agent"
        assert agent_dict["instruction"] == "Test instruction"
        assert agent_dict["metadata"] == {"tags": ["test"]}

    def test_model_validation(self):
        """Test model validation with invalid data."""
        # Test that required fields are enforced
        with pytest.raises(ValueError):
            Agent()  # Missing required id and name

        with pytest.raises(ValueError):
            Tool()  # Missing required id and name

        with pytest.raises(ValueError):
            MCP()  # Missing required id and name

        with pytest.raises(ValueError):
            LanguageModelResponse()  # Missing required name and provider
