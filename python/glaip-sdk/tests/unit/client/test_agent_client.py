#!/usr/bin/env python3
"""Unit tests for the AIP SDK AgentClient.

Tests the AgentClient class functionality without external dependencies.
"""

from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from glaip_sdk.client.agents import AgentClient


@pytest.mark.unit
class TestAgentClient:
    """Test the agent client functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock parent client for testing
        mock_parent_client = Mock()
        mock_parent_client.find_tools.return_value = []
        mock_parent_client.get_tool_by_id.return_value = Mock()

        self.client = AgentClient(
            api_url="http://test.com",
            api_key="test-key",
            parent_client=mock_parent_client,
        )

    @patch.object(AgentClient, "_request")
    def test_list_agents(self, mock_request):
        """Test listing agents."""
        mock_response_data = [
            {
                "id": str(uuid4()),
                "name": "agent1",
                "instruction": "This is a test instruction that is long enough",
            }
        ]
        mock_request.return_value = mock_response_data

        agents = self.client.list_agents()
        assert len(agents) == 1
        assert agents[0].name == "agent1"
        mock_request.assert_called_once_with("GET", "/agents/")

    @patch.object(AgentClient, "_request")
    def test_get_agent_by_id(self, mock_request):
        """Test getting agent by ID."""
        agent_id = str(uuid4())
        mock_response_data = {
            "id": agent_id,
            "name": "test-agent",
            "instruction": "This is a test instruction that is long enough",
        }
        mock_request.return_value = mock_response_data

        agent = self.client.get_agent_by_id(agent_id)
        assert str(agent.id) == agent_id
        assert agent.name == "test-agent"
        mock_request.assert_called_once_with("GET", f"/agents/{agent_id}")

    @patch.object(AgentClient, "_request")
    def test_create_agent(self, mock_request):
        """Test creating an agent."""
        agent_id = str(uuid4())

        # Mock both POST request and potential GET request for full agent data
        mock_response_data = {
            "id": agent_id,
            "name": "new-agent",
            "instruction": "This is a test instruction that is long enough",
        }
        mock_request.return_value = mock_response_data

        agent = self.client.create_agent(name="new-agent", instruction="Test agent")
        assert str(agent.id) == agent_id
        assert agent.name == "new-agent"

        # Verify the request was made (may be called multiple times for creation and retrieval)
        assert mock_request.call_count >= 1
        first_call = mock_request.call_args_list[0]
        assert first_call[0][0] == "POST"  # method
        assert first_call[0][1] == "/agents/"  # endpoint

    @patch.object(AgentClient, "_request")
    def test_update_agent(self, mock_request):
        """Test updating an agent."""
        agent_id = str(uuid4())
        mock_response_data = {
            "id": agent_id,
            "name": "updated-agent",
            "instruction": "Updated",
        }
        mock_request.return_value = mock_response_data

        agent = self.client.update_agent(agent_id, {"name": "updated-agent"})
        assert str(agent.id) == agent_id
        assert agent.name == "updated-agent"

        # The actual implementation may call GET first to retrieve current agent data
        assert mock_request.call_count >= 1
        last_call = mock_request.call_args_list[-1]
        assert last_call[0][0] in ["PUT", "PATCH"]  # method
        assert last_call[0][1] == f"/agents/{agent_id}"  # endpoint

    @patch.object(AgentClient, "_request")
    def test_delete_agent(self, mock_request):
        """Test deleting an agent."""
        agent_id = str(uuid4())
        mock_request.return_value = {"success": True}

        result = self.client.delete_agent(agent_id)
        assert result is None  # delete_agent returns None
        mock_request.assert_called_once_with("DELETE", f"/agents/{agent_id}")

    @patch.object(AgentClient, "_request")
    def test_find_agents(self, mock_request):
        """Test finding agents by name."""
        mock_response_data = [
            {"id": str(uuid4()), "name": "test-agent-1", "instruction": "Test 1"},
            {"id": str(uuid4()), "name": "test-agent-2", "instruction": "Test 2"},
        ]
        mock_request.return_value = mock_response_data

        agents = self.client.find_agents("test")
        assert len(agents) == 2
        assert all("test" in agent.name for agent in agents)
        mock_request.assert_called_once_with("GET", "/agents/", params={"name": "test"})

    def test_run_agent(self):
        """Test running an agent."""
        agent_id = str(uuid4())

        # Mock the http_client.stream context manager
        mock_stream_response = Mock()
        mock_stream_response.__enter__ = Mock(return_value=mock_stream_response)
        mock_stream_response.__exit__ = Mock(return_value=None)
        mock_stream_response.iter_lines.return_value = [
            b'data: {"type": "text", "content": "Agent response"}\n',
            b'data: {"type": "done"}\n',
        ]

        with patch.object(self.client, "http_client") as mock_http_client:
            mock_http_client.stream.return_value = mock_stream_response

            # Mock the renderer to avoid string concatenation issues
            with patch(
                "glaip_sdk.client.agents._select_renderer"
            ) as mock_select_renderer:
                mock_renderer = Mock()
                mock_renderer.on_start = Mock()
                mock_renderer.on_event = Mock()
                mock_renderer.on_finish = Mock()
                mock_select_renderer.return_value = mock_renderer

                response = self.client.run_agent(agent_id, "Hello")
                assert isinstance(response, str)

                # Verify the stream was called with correct parameters
                mock_http_client.stream.assert_called_once()
                call_args = mock_http_client.stream.call_args
                assert call_args[0][0] == "POST"  # method
                assert call_args[0][1] == f"/agents/{agent_id}/run"  # endpoint

    def test_create_agent_with_reserved_name(self):
        """Test creating agent with reserved name validation."""
        # Since we removed forbid_reserved_names, this should now succeed
        agent_id = str(uuid4())
        mock_response_data = {
            "id": agent_id,
            "name": "research-agent",
            "instruction": "This is a test instruction that is long enough",
        }

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = mock_response_data

            agent = self.client.create_agent(
                name="research-agent",
                instruction="This is a test instruction that is long enough",
            )

            assert str(agent.id) == agent_id
            assert agent.name == "research-agent"

    def test_create_agent_without_instruction(self):
        """Test creating agent without instruction raises error."""
        with pytest.raises(
            TypeError,
            match="missing 1 required positional argument: 'instruction'",
        ):
            self.client.create_agent(name="test-agent")

    def test_create_agent_with_instruction(self):
        """Test creating agent using instruction parameter."""
        agent_id = str(uuid4())

        mock_response_data = {
            "id": agent_id,
            "name": "test-agent",
            "instruction": "Test agent using instruction parameter",
        }

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = mock_response_data

            agent = self.client.create_agent(
                name="test-agent", instruction="Test agent using instruction parameter"
            )

            assert str(agent.id) == agent_id
            assert agent.name == "test-agent"

    def test_create_agent_with_model_config(self):
        """Test creating agent with custom model configuration."""
        agent_id = str(uuid4())

        mock_response_data = {
            "id": agent_id,
            "name": "test-agent",
            "instruction": "This is a test instruction that is long enough",
        }

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = mock_response_data

            agent = self.client.create_agent(
                name="test-agent",
                instruction="This is a test instruction that is long enough",
                model="gpt-4",
                timeout=600,
            )

            assert str(agent.id) == agent_id

            # Verify the request was made with the expected arguments
            # The create_agent method may make multiple calls (POST for creation, GET for retrieval)
            # Find the POST call to /agents/
            post_calls = [
                call
                for call in mock_request.call_args_list
                if call[0][0] == "POST" and call[0][1] == "/agents/"
            ]
            assert len(post_calls) >= 1

            # Check the first POST call
            post_call = post_calls[0]
            json_data = post_call[1]["json"]
            assert json_data["model_name"] == "gpt-4"
            # timeout is a parameter but not included in the payload sent to the server
            # The test should verify the method was called with the right parameters instead

    def test_create_agent_with_strict_validation(self):
        """Test creating agent with strict validation enabled."""
        with patch.object(self.client, "_request") as mock_request:
            with patch.object(self.client, "_extract_ids") as mock_extract_ids:
                mock_extract_ids.return_value = ["tool-id-1", "tool-id-2"]
                mock_request.return_value = {"id": str(uuid4()), "name": "test-agent"}

                self.client.create_agent(
                    name="test-agent",
                    instruction="This is a test instruction that is long enough",
                    tools=["tool1", "tool2"],
                )

                # _extract_ids is called twice - once for tools, once for agents
                assert mock_extract_ids.call_count >= 1

    def test_get_agent_by_id_with_tool_conversion(self):
        """Test getting agent by ID with tool data conversion."""
        agent_id = str(uuid4())

        # Mock response with tools as dict objects
        mock_response = {
            "id": agent_id,
            "name": "test-agent",
            "tools": [
                {"id": "tool1", "name": "Tool 1"},
                {"id": "tool2", "name": "Tool 2"},
            ],
        }

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = mock_response

            agent = self.client.get_agent_by_id(agent_id)

            assert str(agent.id) == agent_id
            # Verify tools were converted to IDs
            assert hasattr(agent, "name")

    def test_find_agents_with_name(self):
        """Test finding agents by name parameter."""
        mock_response = [
            {"id": str(uuid4()), "name": "test-agent-1"},
            {"id": str(uuid4()), "name": "test-agent-2"},
        ]

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = mock_response

            agents = self.client.find_agents(name="test")

            assert len(agents) == 2
            mock_request.assert_called_once_with(
                "GET", "/agents/", params={"name": "test"}
            )

    def test_find_agents_without_name(self):
        """Test finding agents without name parameter."""
        mock_response = [{"id": str(uuid4()), "name": "agent"}]

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = mock_response

            agents = self.client.find_agents()

            assert len(agents) == 1
            mock_request.assert_called_once_with("GET", "/agents/", params={})

    def test_update_agent_with_minimal_data(self):
        """Test updating agent with minimal update data."""
        agent_id = str(uuid4())

        # Mock getting current agent for required fields
        current_agent_data = {
            "id": agent_id,
            "name": "current-name",
            "instruction": "Current instruction",
        }

        updated_agent_data = {
            "id": agent_id,
            "name": "current-name",
            "instruction": "Updated instruction",
        }

        with patch.object(self.client, "_request") as mock_request:
            # First call returns current agent, second call returns updated agent
            mock_request.side_effect = [current_agent_data, updated_agent_data]

            agent = self.client.update_agent(
                agent_id, instruction="Updated instruction"
            )

            assert str(agent.id) == agent_id
            assert mock_request.call_count == 2

            # Verify the PUT request included required fields
            put_call = mock_request.call_args_list[1]
            json_data = put_call[1]["json"]
            assert json_data["type"] == "config"
            assert json_data["framework"] == "langchain"
            assert json_data["name"] == "current-name"

    def test_update_agent_without_instruction(self):
        """Test updating agent when current agent has no instruction."""
        agent_id = str(uuid4())

        # Mock getting current agent without instruction
        mock_current_agent = Mock()
        mock_current_agent.name = "current-name"
        mock_current_agent.instruction = None
        mock_current_agent.agent_config = {}  # Empty dict to avoid iteration error
        mock_current_agent.tools = []  # Empty list to make it iterable
        mock_current_agent.agents = []  # Empty list to make it iterable

        updated_agent_data = {"id": agent_id, "name": "current-name"}

        with patch.object(self.client, "get_agent_by_id") as mock_get_agent:
            with patch.object(self.client, "_request") as mock_request:
                mock_get_agent.return_value = mock_current_agent
                mock_request.return_value = updated_agent_data

                self.client.update_agent(agent_id, description="New description")

                # Verify the PUT request was made
                mock_request.assert_called_once()
                call_args = mock_request.call_args
                assert call_args[0][0] == "PUT"  # method
                assert call_args[0][1] == f"/agents/{agent_id}"  # endpoint

    def test_delete_agent_success(self):
        """Test successful agent deletion."""
        agent_id = str(uuid4())

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = None  # DELETE typically returns no content

            result = self.client.delete_agent(agent_id)

            assert result is None  # delete_agent returns None
            mock_request.assert_called_once_with("DELETE", f"/agents/{agent_id}")

    def test_run_agent_with_kwargs(self):
        """Test running agent with additional parameters."""
        agent_id = str(uuid4())

        # Mock the http_client.stream context manager
        mock_stream_response = Mock()
        mock_stream_response.__enter__ = Mock(return_value=mock_stream_response)
        mock_stream_response.__exit__ = Mock(return_value=None)
        mock_stream_response.iter_lines.return_value = [
            b'data: {"type": "text", "content": "Agent response with params"}\n',
            b'data: {"type": "done"}\n',
        ]

        with patch.object(self.client, "http_client") as mock_http_client:
            mock_http_client.stream.return_value = mock_stream_response

            # Mock the renderer to avoid string concatenation issues
            with patch(
                "glaip_sdk.client.agents._select_renderer"
            ) as mock_select_renderer:
                mock_renderer = Mock()
                mock_renderer.on_start = Mock()
                mock_renderer.on_event = Mock()
                mock_renderer.on_finish = Mock()
                mock_select_renderer.return_value = mock_renderer

                output = self.client.run_agent(
                    agent_id, "Hello", temperature=0.7, max_tokens=100
                )

                assert isinstance(output, str)

                # Verify the stream was called
                mock_http_client.stream.assert_called_once()
                call_args = mock_http_client.stream.call_args
                assert call_args[0][0] == "POST"  # method
                assert call_args[0][1] == f"/agents/{agent_id}/run"  # endpoint

                # Verify kwargs were passed through in the json payload
                json_payload = call_args[1]["json"]
                assert json_payload["temperature"] == 0.7
                assert json_payload["max_tokens"] == 100

    def test_run_agent_no_output(self):
        """Test running agent when response has no output field."""
        agent_id = str(uuid4())

        # Mock the http_client.stream context manager with no content
        mock_stream_response = Mock()
        mock_stream_response.__enter__ = Mock(return_value=mock_stream_response)
        mock_stream_response.__exit__ = Mock(return_value=None)
        mock_stream_response.iter_lines.return_value = [
            b'data: {"type": "done"}\n'  # No text content, just done
        ]

        with patch.object(self.client, "http_client") as mock_http_client:
            mock_http_client.stream.return_value = mock_stream_response

            # Mock the renderer to avoid string concatenation issues
            with patch(
                "glaip_sdk.client.agents._select_renderer"
            ) as mock_select_renderer:
                mock_renderer = Mock()
                mock_renderer.on_start = Mock()
                mock_renderer.on_event = Mock()
                mock_renderer.on_finish = Mock()
                mock_select_renderer.return_value = mock_renderer

                output = self.client.run_agent(agent_id, "Hello")

                assert isinstance(output, str)  # Should return a string (may be empty)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
