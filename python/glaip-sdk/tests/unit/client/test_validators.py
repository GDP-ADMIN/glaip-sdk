#!/usr/bin/env python3
"""Unit tests for the AIP SDK ResourceValidator.

Tests the ResourceValidator class functionality without external dependencies.
"""

from unittest.mock import Mock
from uuid import uuid4

import pytest

from glaip_sdk.client.validators import ResourceValidator
from glaip_sdk.exceptions import NotFoundError, ValidationError


@pytest.mark.unit
class TestResourceValidator:
    """Test the resource validator functionality."""

    def test_is_reserved_name_true(self):
        """Test reserved name detection for true cases."""
        assert ResourceValidator.is_reserved_name("research-agent") is True
        assert ResourceValidator.is_reserved_name("github-agent") is True
        assert (
            ResourceValidator.is_reserved_name("aws-pricing-filter-generator-agent")
            is True
        )

    def test_is_reserved_name_false(self):
        """Test reserved name detection for false cases."""
        assert ResourceValidator.is_reserved_name("my-custom-agent") is False
        assert ResourceValidator.is_reserved_name("test-agent") is False
        assert ResourceValidator.is_reserved_name("") is False

    def test_extract_tool_ids_with_uuid_strings(self):
        """Test extracting tool IDs when tools are already UUID strings."""
        mock_client = Mock()
        tool_uuid1 = str(uuid4())
        tool_uuid2 = str(uuid4())

        tools = [tool_uuid1, tool_uuid2]
        result = ResourceValidator.extract_tool_ids(tools, mock_client)

        assert result == [tool_uuid1, tool_uuid2]
        # Should not call client methods for UUIDs
        mock_client.find_tools.assert_not_called()

    def test_extract_tool_ids_with_tool_objects_having_ids(self):
        """Test extracting tool IDs from tool objects that have IDs."""
        mock_client = Mock()
        tool_id1 = str(uuid4())
        tool_id2 = str(uuid4())

        # Create mock tool objects with IDs
        tool1 = Mock()
        tool1.id = tool_id1
        tool2 = Mock()
        tool2.id = tool_id2

        tools = [tool1, tool2]
        result = ResourceValidator.extract_tool_ids(tools, mock_client)

        assert result == [tool_id1, tool_id2]

    def test_extract_tool_ids_with_tool_names_single_match(self):
        """Test extracting tool IDs from tool names with single matches."""
        mock_client = Mock()
        tool_id = str(uuid4())

        # Mock tool object returned by find_tools
        mock_tool = Mock()
        mock_tool.id = tool_id
        mock_client.find_tools.return_value = [mock_tool]

        tools = ["my-tool"]
        result = ResourceValidator.extract_tool_ids(tools, mock_client)

        assert result == [tool_id]
        mock_client.find_tools.assert_called_once_with(name="my-tool")

    def test_extract_tool_ids_with_tool_names_multiple_matches(self):
        """Test extracting tool IDs from tool names with multiple matches raises error."""
        mock_client = Mock()

        # Mock multiple tools returned by find_tools
        mock_tool1 = Mock()
        mock_tool1.id = str(uuid4())
        mock_tool2 = Mock()
        mock_tool2.id = str(uuid4())
        mock_client.find_tools.return_value = [mock_tool1, mock_tool2]

        tools = ["ambiguous-tool"]

        with pytest.raises(
            ValidationError,
            match="Failed to resolve tool name 'ambiguous-tool' to ID: Multiple tools found with name 'ambiguous-tool'",
        ):
            ResourceValidator.extract_tool_ids(tools, mock_client)

    def test_extract_tool_ids_with_tool_names_no_matches(self):
        """Test extracting tool IDs from tool names with no matches raises error."""
        mock_client = Mock()
        mock_client.find_tools.return_value = []

        tools = ["nonexistent-tool"]

        with pytest.raises(
            ValidationError,
            match="Failed to resolve tool name 'nonexistent-tool' to ID: Tool not found: nonexistent-tool",
        ):
            ResourceValidator.extract_tool_ids(tools, mock_client)

    def test_extract_tool_ids_with_tool_names_client_error(self):
        """Test extracting tool IDs when client raises an exception."""
        mock_client = Mock()
        mock_client.find_tools.side_effect = Exception("Client error")

        tools = ["tool-name"]

        with pytest.raises(
            ValidationError, match="Failed to resolve tool name 'tool-name' to ID"
        ):
            ResourceValidator.extract_tool_ids(tools, mock_client)

    def test_extract_tool_ids_with_tool_objects_having_names(self):
        """Test extracting tool IDs from tool objects that have names but no IDs."""
        mock_client = Mock()
        tool_id = str(uuid4())

        # Mock tool object returned by find_tools
        mock_found_tool = Mock()
        mock_found_tool.id = tool_id
        mock_client.find_tools.return_value = [mock_found_tool]

        # Create tool object with name but no ID
        tool_obj = Mock()
        tool_obj.name = "my-tool"
        tool_obj.id = None

        tools = [tool_obj]
        result = ResourceValidator.extract_tool_ids(tools, mock_client)

        assert result == [tool_id]
        mock_client.find_tools.assert_called_once_with(name="my-tool")

    def test_extract_tool_ids_with_tool_objects_multiple_matches_by_name(self):
        """Test extracting tool IDs from tool objects with names that have multiple matches."""
        mock_client = Mock()

        # Mock multiple tools returned by find_tools
        mock_tool1 = Mock()
        mock_tool1.id = str(uuid4())
        mock_tool2 = Mock()
        mock_tool2.id = str(uuid4())
        mock_client.find_tools.return_value = [mock_tool1, mock_tool2]

        # Create tool object with ambiguous name
        tool_obj = Mock()
        tool_obj.name = "ambiguous-tool"
        tool_obj.id = None

        tools = [tool_obj]

        with pytest.raises(
            ValidationError,
            match="Failed to resolve tool name 'ambiguous-tool' to ID: Multiple tools found with name 'ambiguous-tool'",
        ):
            ResourceValidator.extract_tool_ids(tools, mock_client)

    def test_extract_tool_ids_with_tool_objects_no_matches_by_name(self):
        """Test extracting tool IDs from tool objects with names that have no matches."""
        mock_client = Mock()
        mock_client.find_tools.return_value = []

        # Create tool object with nonexistent name
        tool_obj = Mock()
        tool_obj.name = "nonexistent-tool"
        tool_obj.id = None

        tools = [tool_obj]

        with pytest.raises(
            ValidationError,
            match="Failed to resolve tool name 'nonexistent-tool' to ID: Tool not found: nonexistent-tool",
        ):
            ResourceValidator.extract_tool_ids(tools, mock_client)

    def test_extract_tool_ids_with_invalid_tool_object(self):
        """Test extracting tool IDs from invalid tool objects raises error."""
        mock_client = Mock()

        # Create invalid tool object with neither ID nor name
        invalid_tool = Mock()
        invalid_tool.id = None
        invalid_tool.name = None

        tools = [invalid_tool]

        with pytest.raises(
            ValidationError,
            match="Invalid tool reference.*must have 'id' or 'name' attribute",
        ):
            ResourceValidator.extract_tool_ids(tools, mock_client)

    def test_extract_agent_names_with_strings(self):
        """Test extracting agent IDs from string names."""
        mock_client = Mock()

        # Mock agents with IDs
        mock_agent1 = Mock()
        mock_agent1.id = "550e8400-e29b-41d4-a716-446655440001"
        mock_agent2 = Mock()
        mock_agent2.id = "550e8400-e29b-41d4-a716-446655440002"
        mock_agent3 = Mock()
        mock_agent3.id = "550e8400-e29b-41d4-a716-446655440003"

        # Setup find_agents to return appropriate agents
        def mock_find_agents(name=None):
            if name == "agent1":
                return [mock_agent1]
            elif name == "agent2":
                return [mock_agent2]
            elif name == "agent3":
                return [mock_agent3]
            return []

        mock_client.find_agents = mock_find_agents

        agents = ["agent1", "agent2", "agent3"]
        result = ResourceValidator.extract_agent_ids(agents, mock_client)

        expected = [
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002",
            "550e8400-e29b-41d4-a716-446655440003",
        ]
        assert result == expected

    def test_extract_agent_names_with_agent_objects_having_names(self):
        """Test extracting agent IDs from agent objects with names."""
        mock_client = Mock()

        # Create agent objects with names - but extract_agent_ids expects IDs, not names
        # So we should test with agent objects that have IDs
        agent1 = Mock()
        agent1.id = "550e8400-e29b-41d4-a716-446655440001"
        agent2 = Mock()
        agent2.id = "550e8400-e29b-41d4-a716-446655440002"

        agents = [agent1, agent2]
        result = ResourceValidator.extract_agent_ids(agents, mock_client)

        assert result == [
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002",
        ]

    def test_extract_agent_names_with_agent_objects_having_ids_fallback(self):
        """Test extracting agent names from agent objects with IDs as fallback."""
        mock_client = Mock()
        agent_id = str(uuid4())

        # Create agent object with ID but no name
        agent = Mock()
        agent.name = None
        agent.id = agent_id

        agents = [agent]
        result = ResourceValidator.extract_agent_ids(agents, mock_client)

        assert result == [agent_id]

    def test_extract_agent_names_with_invalid_agent_object(self):
        """Test extracting agent names from invalid agent objects raises error."""
        mock_client = Mock()

        # Create invalid agent object with neither name nor ID
        invalid_agent = Mock()
        invalid_agent.name = None
        invalid_agent.id = None

        agents = [invalid_agent]

        with pytest.raises(
            ValidationError,
            match="Invalid agent reference.*must have 'id' or 'name' attribute",
        ):
            ResourceValidator.extract_agent_ids(agents, mock_client)

    def test_validate_tools_exist_success(self):
        """Test successful tool validation when all tools exist."""
        mock_client = Mock()
        tool_id1 = str(uuid4())
        tool_id2 = str(uuid4())

        # Mock successful tool retrieval
        mock_client.get_tool_by_id.return_value = Mock()

        tool_ids = [tool_id1, tool_id2]

        # Should not raise any exception
        ResourceValidator.validate_tools_exist(tool_ids, mock_client)

        # Verify all tools were checked
        assert mock_client.get_tool_by_id.call_count == 2
        mock_client.get_tool_by_id.assert_any_call(tool_id1)
        mock_client.get_tool_by_id.assert_any_call(tool_id2)

    def test_validate_tools_exist_not_found(self):
        """Test tool validation when a tool doesn't exist."""
        mock_client = Mock()
        tool_id = str(uuid4())

        # Mock tool not found
        mock_client.get_tool_by_id.side_effect = NotFoundError("Tool not found")

        tool_ids = [tool_id]

        with pytest.raises(ValidationError, match=f"Tool not found: {tool_id}"):
            ResourceValidator.validate_tools_exist(tool_ids, mock_client)

    def test_validate_agents_exist_success(self):
        """Test successful agent validation when all agents exist."""
        mock_client = Mock()

        # Mock get_agent_by_id to return agents successfully
        mock_agent1 = Mock()
        mock_agent1.id = "550e8400-e29b-41d4-a716-446655440001"
        mock_agent2 = Mock()
        mock_agent2.id = "550e8400-e29b-41d4-a716-446655440002"

        def mock_get_agent_by_id(agent_id):
            if agent_id == "550e8400-e29b-41d4-a716-446655440001":
                return mock_agent1
            elif agent_id == "550e8400-e29b-41d4-a716-446655440002":
                return mock_agent2
            else:
                from glaip_sdk.exceptions import NotFoundError

                raise NotFoundError(f"Agent not found: {agent_id}")

        mock_client.get_agent_by_id = mock_get_agent_by_id

        agent_ids = [
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002",
        ]

        # Should not raise any exception
        ResourceValidator.validate_agents_exist(agent_ids, mock_client)

    def test_validate_agents_exist_not_found(self):
        """Test agent validation when an agent doesn't exist."""
        mock_client = Mock()

        # Mock get_agent_by_id to raise NotFoundError
        def mock_get_agent_by_id(agent_id):
            from glaip_sdk.exceptions import NotFoundError

            raise NotFoundError(f"Agent not found: {agent_id}")

        mock_client.get_agent_by_id = mock_get_agent_by_id

        agent_ids = ["550e8400-e29b-41d4-a716-446655440000"]

        with pytest.raises(
            ValidationError,
            match="Agent not found: 550e8400-e29b-41d4-a716-446655440000",
        ):
            ResourceValidator.validate_agents_exist(agent_ids, mock_client)

    def test_validate_agents_exist_client_error(self):
        """Test agent validation when client raises an exception."""
        mock_client = Mock()

        # Mock client error on get_agent_by_id - this will bubble up as a general exception
        mock_client.get_agent_by_id.side_effect = Exception("Client error")

        agent_ids = ["550e8400-e29b-41d4-a716-446655440001"]

        with pytest.raises(Exception, match="Client error"):
            ResourceValidator.validate_agents_exist(agent_ids, mock_client)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "unit"])
