"""Validation utilities for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from typing import Any
from uuid import UUID

from glaip_sdk.exceptions import AmbiguousResourceError, NotFoundError, ValidationError
from glaip_sdk.models import Tool


class ResourceValidator:
    """Validates and resolves resource references."""

    RESERVED_NAMES = {
        "research-agent",
        "github-agent",
        "aws-pricing-filter-generator-agent",
    }

    @classmethod
    def is_reserved_name(cls, name: str) -> bool:
        """Check if a name is reserved."""
        return name in cls.RESERVED_NAMES

    @classmethod
    def extract_tool_ids(cls, tools: list[str | Tool], client) -> list[str]:
        """Extract tool IDs from a list of tool names, IDs, or Tool objects.

        For agent creation, the backend expects tool IDs (UUIDs).
        This method handles:
        - Tool objects (extracts their ID)
        - UUID strings (passes through)
        - Tool names (finds tool and extracts ID)
        """
        tool_ids = []
        for tool in tools:
            if isinstance(tool, str):
                # Check if it's already a UUID
                try:
                    UUID(tool)
                    tool_ids.append(tool)  # Already a UUID string
                except ValueError:
                    # It's a name, try to find the tool and get its ID
                    try:
                        found_tools = client.find_tools(name=tool)
                        if len(found_tools) == 1:
                            tool_ids.append(str(found_tools[0].id))
                        elif len(found_tools) > 1:
                            raise AmbiguousResourceError(
                                f"Multiple tools found with name '{tool}': {[t.id for t in found_tools]}"
                            )
                        else:
                            raise NotFoundError(f"Tool not found: {tool}")
                    except Exception as e:
                        raise ValidationError(
                            f"Failed to resolve tool name '{tool}' to ID: {e}"
                        )
            elif hasattr(tool, "id") and tool.id is not None:  # Tool object with ID
                tool_ids.append(str(tool.id))
            elif isinstance(tool, UUID):  # UUID object
                tool_ids.append(str(tool))
            elif (
                hasattr(tool, "name") and tool.name is not None
            ):  # Tool object with name but no ID
                # Try to find the tool by name and get its ID
                try:
                    found_tools = client.find_tools(name=tool.name)
                    if len(found_tools) == 1:
                        tool_ids.append(str(found_tools[0].id))
                    elif len(found_tools) > 1:
                        raise AmbiguousResourceError(
                            f"Multiple tools found with name '{tool.name}': {[t.id for t in found_tools]}"
                        )
                    else:
                        raise NotFoundError(f"Tool not found: {tool.name}")
                except Exception as e:
                    raise ValidationError(
                        f"Failed to resolve tool name '{tool.name}' to ID: {e}"
                    )
            else:
                raise ValidationError(
                    f"Invalid tool reference: {tool} - must have 'id' or 'name' attribute"
                )
        return tool_ids

    @classmethod
    def extract_agent_ids(cls, agents: list[str | Any], client) -> list[str]:
        """Extract agent IDs from a list of agent names, IDs, or agent objects.

        For agent creation, the backend expects agent IDs (UUIDs).
        This method handles:
        - Agent objects (extracts their ID)
        - UUID strings (passes through)
        - Agent names (finds agent and extracts ID)
        """
        agent_ids = []
        for agent in agents:
            if isinstance(agent, str):
                # Check if it's already a UUID
                try:
                    UUID(agent)
                    agent_ids.append(agent)  # Already a UUID string
                except ValueError:
                    # It's a name, try to find the agent and get its ID
                    try:
                        found_agents = client.find_agents(name=agent)
                        if len(found_agents) == 1:
                            agent_ids.append(str(found_agents[0].id))
                        elif len(found_agents) > 1:
                            raise AmbiguousResourceError(
                                f"Multiple agents found with name '{agent}': {[a.id for a in found_agents]}"
                            )
                        else:
                            raise NotFoundError(f"Agent not found: {agent}")
                    except Exception as e:
                        raise ValidationError(
                            f"Failed to resolve agent name '{agent}' to ID: {e}"
                        )
            elif hasattr(agent, "id") and agent.id is not None:  # Agent object with ID
                agent_ids.append(str(agent.id))
            elif isinstance(agent, UUID):  # UUID object
                agent_ids.append(str(agent))
            elif (
                hasattr(agent, "name") and agent.name is not None
            ):  # Agent object with name but no ID
                # Try to find the agent by name and get its ID
                try:
                    found_agents = client.find_agents(name=agent.name)
                    if len(found_agents) == 1:
                        agent_ids.append(str(found_agents[0].id))
                    elif len(found_agents) > 1:
                        raise AmbiguousResourceError(
                            f"Multiple agents found with name '{agent.name}': {[a.id for a in found_agents]}"
                        )
                    else:
                        raise NotFoundError(f"Agent not found: {agent.name}")
                except Exception as e:
                    raise ValidationError(
                        f"Failed to resolve agent name '{agent.name}' to ID: {e}"
                    )
            else:
                raise ValidationError(
                    f"Invalid agent reference: {agent} - must have 'id' or 'name' attribute"
                )
        return agent_ids

    @classmethod
    def validate_tools_exist(cls, tool_ids: list[str], client) -> None:
        """Validate that all tool IDs exist."""
        for tool_id in tool_ids:
            try:
                client.get_tool_by_id(tool_id)
            except NotFoundError:
                raise ValidationError(f"Tool not found: {tool_id}")

    @classmethod
    def validate_agents_exist(cls, agent_ids: list[str], client) -> None:
        """Validate that all agent IDs exist."""
        for agent_id in agent_ids:
            try:
                client.get_agent_by_id(agent_id)
            except NotFoundError:
                raise ValidationError(f"Agent not found: {agent_id}")
