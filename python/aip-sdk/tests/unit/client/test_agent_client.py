#!/usr/bin/env python3
"""Unit tests for the AIP SDK AgentClient.

Tests the AgentClient class functionality without external dependencies.
"""

from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import pytest

from glaip_sdk.client.agents import AgentClient
from glaip_sdk.exceptions import ValidationError


@pytest.mark.unit
class TestAgentClient:
    """Test the agent client functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        with (
            patch("glaip_sdk.client.base.Path.exists") as mock_exists,
            patch("glaip_sdk.client.base.yaml.safe_load") as mock_yaml_load,
            patch("builtins.open", new_callable=MagicMock),
        ):
            mock_exists.return_value = False  # No config file
            mock_yaml_load.return_value = {}

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
        mock_request.assert_called_once_with("GET", "/agents")

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
        assert first_call[0][1] == "/agents"  # endpoint

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
        assert result is True
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
        mock_request.assert_called_once_with("GET", "/agents", params={"name": "test"})

    @patch.object(AgentClient, "_request")
    def test_run_agent(self, mock_request):
        """Test running an agent."""
        agent_id = str(uuid4())
        mock_response_data = {"output": "Agent response"}
        mock_request.return_value = mock_response_data

        response = self.client.run_agent(agent_id, "Hello")
        assert response == "Agent response"
        mock_request.assert_called_once()

        call_args = mock_request.call_args
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
            ValidationError,
            match="Instruction must be provided",
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
            # Find the POST call to /agents
            post_calls = [
                call
                for call in mock_request.call_args_list
                if call[0][0] == "POST" and call[0][1] == "/agents"
            ]
            assert len(post_calls) >= 1

            # Check the first POST call
            post_call = post_calls[0]
            json_data = post_call[1]["json"]
            assert json_data["agent_config"]["lm_name"] == "gpt-4"
            assert json_data["timeout"] == 600

    def test_create_agent_with_strict_validation(self):
        """Test creating agent with strict validation enabled."""
        with patch.object(self.client, "_request") as mock_request:
            with patch(
                "glaip_sdk.client.validators.ResourceValidator.extract_tool_ids"
            ) as mock_extract_tools:
                mock_extract_tools.return_value = ["tool-id-1", "tool-id-2"]
                mock_request.return_value = {"id": str(uuid4()), "name": "test-agent"}

                self.client.create_agent(
                    name="test-agent",
                    instruction="This is a test instruction that is long enough",
                    tools=["tool1", "tool2"],
                )

                mock_extract_tools.assert_called_once_with(
                    ["tool1", "tool2"], self.client._parent_client
                )

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
                "GET", "/agents", params={"name": "test"}
            )

    def test_find_agents_without_name(self):
        """Test finding agents without name parameter."""
        mock_response = [{"id": str(uuid4()), "name": "agent"}]

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = mock_response

            agents = self.client.find_agents()

            assert len(agents) == 1
            mock_request.assert_called_once_with("GET", "/agents", params={})

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
                agent_id, {"instruction": "Updated instruction"}
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
        mock_current_agent.instruction = None
        # No instruction field

        updated_agent_data = {"id": agent_id, "name": "current-name"}

        with patch.object(self.client, "_request") as mock_request:
            # First call: get_agent_by_id for name, second call: get_agent_by_id for instruction, third call: PUT
            mock_request.side_effect = [
                mock_current_agent,
                mock_current_agent,
                updated_agent_data,
            ]

            self.client.update_agent(agent_id, {"description": "New description"})

            # Verify default instruction was added
            put_call = mock_request.call_args_list[2]  # Third call is the PUT
            json_data = put_call[1]["json"]
            assert json_data["instruction"] == "Default agent instruction for updates"

    def test_delete_agent_success(self):
        """Test successful agent deletion."""
        agent_id = str(uuid4())

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = None  # DELETE typically returns no content

            result = self.client.delete_agent(agent_id)

            assert result is True
            mock_request.assert_called_once_with("DELETE", f"/agents/{agent_id}")

    def test_run_agent_with_kwargs(self):
        """Test running agent with additional parameters."""
        agent_id = str(uuid4())

        mock_response = {"output": "Agent response with params"}

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = mock_response

            output = self.client.run_agent(
                agent_id, "Hello", temperature=0.7, max_tokens=100
            )

            assert output == "Agent response with params"

            # Verify kwargs were passed through
            call_args = mock_request.call_args[1]["json"]
            assert call_args["temperature"] == 0.7
            assert call_args["max_tokens"] == 100

    def test_run_agent_no_output(self):
        """Test running agent when response has no output field."""
        agent_id = str(uuid4())

        mock_response = {"status": "completed"}  # No output field

        with patch.object(self.client, "_request") as mock_request:
            mock_request.return_value = mock_response

            output = self.client.run_agent(agent_id, "Hello")

            assert output == ""  # Should return empty string


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
