#!/usr/bin/env python3
"""Data models for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from typing import Any

from pydantic import BaseModel


class Agent(BaseModel):
    """Agent model for API responses."""

    id: str
    name: str
    instruction: str | None = None
    description: str | None = None  # Add missing description field
    type: str | None = None
    framework: str | None = None
    version: str | None = None
    tools: list[dict[str, Any]] | None = None  # Backend returns ToolReference objects
    agents: list[dict[str, Any]] | None = None  # Backend returns AgentReference objects
    agent_config: dict[str, Any] | None = None
    timeout: int = 300
    metadata: dict[str, Any] | None = None
    language_model_id: str | None = None
    a2a_profile: dict[str, Any] | None = None
    _client: Any = None

    def _set_client(self, client):
        """Set the client reference for this resource."""
        self._client = client
        return self

    def run(self, message: str, **kwargs) -> str:
        """Run the agent with a message."""
        if not self._client:
            raise RuntimeError(
                "No client available. Use client.get_agent_by_id() to get a client-connected agent."
            )
        # Automatically pass the agent name for better renderer display
        kwargs.setdefault("agent_name", self.name)
        return self._client.run_agent(self.id, message, **kwargs)

    def update(self, **kwargs) -> "Agent":
        """Update agent attributes."""
        if not self._client:
            raise RuntimeError(
                "No client available. Use client.get_agent_by_id() to get a client-connected agent."
            )
        updated_agent = self._client.update_agent(self.id, **kwargs)
        # Update current instance with new data
        for key, value in updated_agent.model_dump().items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def delete(self) -> None:
        """Delete the agent."""
        if not self._client:
            raise RuntimeError(
                "No client available. Use client.get_agent_by_id() to get a client-connected agent."
            )
        self._client.delete_agent(self.id)


class Tool(BaseModel):
    """Tool model for API responses."""

    id: str
    name: str
    tool_type: str | None = None
    description: str | None = None
    framework: str | None = None
    version: str | None = None
    tool_script: str | None = None
    tool_file: str | None = None
    _client: Any = None  # Will hold client reference

    def _set_client(self, client):
        """Set the client reference for this resource."""
        self._client = client
        return self

    def get_script(self) -> str:
        """Get the tool script content."""
        if self.tool_script:
            return self.tool_script
        elif self.tool_file:
            return f"Script content from file: {self.tool_file}"
        else:
            return "No script content available"

    def update(self, **kwargs) -> "Tool":
        """Update tool attributes."""
        if not self._client:
            raise RuntimeError(
                "No client available. Use client.get_tool_by_id() to get a client-connected tool."
            )
        updated_tool = self._client.tools.update_tool(self.id, **kwargs)
        # Update current instance with new data
        for key, value in updated_tool.model_dump().items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def delete(self) -> None:
        """Delete the tool."""
        if not self._client:
            raise RuntimeError(
                "No client available. Use client.get_tool_by_id() to get a client-connected tool."
            )
        self._client.tools.delete_tool(self.id)


class MCP(BaseModel):
    """MCP model for API responses."""

    id: str
    name: str
    description: str | None = None
    config: dict[str, Any] | None = None
    framework: str | None = None
    version: str | None = None
    transport: str | None = None  # "sse" or "http"
    authentication: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    _client: Any = None  # Will hold client reference

    def _set_client(self, client):
        """Set the client reference for this resource."""
        self._client = client
        return self

    def get_tools(self) -> list[dict[str, Any]]:
        """Get tools available from this MCP."""
        if not self._client:
            raise RuntimeError(
                "No client available. Use client.get_mcp_by_id() to get a client-connected MCP."
            )
        # This would delegate to the client's MCP tools endpoint
        # For now, return empty list as placeholder
        return []

    def update(self, **kwargs) -> "MCP":
        """Update MCP attributes."""
        if not self._client:
            raise RuntimeError(
                "No client available. Use client.get_mcp_by_id() to get a client-connected MCP."
            )
        updated_mcp = self._client.update_mcp(self.id, **kwargs)
        # Update current instance with new data
        for key, value in updated_mcp.model_dump().items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    def delete(self) -> None:
        """Delete the MCP."""
        if not self._client:
            raise RuntimeError(
                "No client available. Use client.get_mcp_by_id() to get a client-connected MCP."
            )
        self._client.delete_mcp(self.id)


class LanguageModelResponse(BaseModel):
    """Language model response model."""

    name: str
    provider: str
    description: str | None = None
    capabilities: list[str] | None = None
    max_tokens: int | None = None
    supports_streaming: bool = False


class TTYRenderer:
    """Simple TTY renderer for non-Rich environments."""

    def __init__(self, use_color: bool = True):
        self.use_color = use_color

    def render_message(self, message: str, event_type: str = "message"):
        """Render a message with optional color."""
        if event_type == "error":
            print(f"ERROR: {message}", flush=True)
        elif event_type == "done":
            print(f"\n✅ {message}", flush=True)
        else:
            print(message, flush=True)
