#!/usr/bin/env python3
"""MCP client for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import logging
from typing import Any

from glaip_sdk.client.base import BaseClient
from glaip_sdk.models import MCP

# Set up module-level logger
logger = logging.getLogger("glaip_sdk.mcps")


class MCPClient(BaseClient):
    """Client for MCP operations."""

    def __init__(self, *, parent_client: BaseClient | None = None, **kwargs):
        """Initialize the MCP client.

        Args:
            parent_client: Parent client to adopt session/config from
            **kwargs: Additional arguments for standalone initialization
        """
        super().__init__(parent_client=parent_client, **kwargs)

    def list_mcps(self) -> list[MCP]:
        """List all MCPs."""
        data = self._request("GET", "/mcps/")
        return [MCP(**mcp_data)._set_client(self) for mcp_data in (data or [])]

    def get_mcp_by_id(self, mcp_id: str) -> MCP:
        """Get MCP by ID."""
        data = self._request("GET", f"/mcps/{mcp_id}")
        return MCP(**data)._set_client(self)

    def find_mcps(self, name: str | None = None) -> list[MCP]:
        """Find MCPs by name."""
        # Backend doesn't support name query parameter, so we fetch all and filter client-side
        data = self._request("GET", "/mcps/")
        mcps = [MCP(**mcp_data)._set_client(self) for mcp_data in (data or [])]

        if name:
            # Client-side filtering by name (case-insensitive)
            mcps = [mcp for mcp in mcps if name.lower() in mcp.name.lower()]

        return mcps

    def create_mcp(
        self,
        name: str,
        description: str,
        config: dict[str, Any] | None = None,
        **kwargs,
    ) -> MCP:
        """Create a new MCP."""
        payload = {
            "name": name,
            "description": description,
            **kwargs,
        }

        if config:
            payload["config"] = config

        # Create the MCP (backend returns only the ID)
        response_data = self._request("POST", "/mcps/", json=payload)

        # Extract the ID from the response
        if isinstance(response_data, dict) and "id" in response_data:
            mcp_id = response_data["id"]
        else:
            # Fallback: assume response_data is the ID directly
            mcp_id = str(response_data)

        # Fetch the full MCP details
        return self.get_mcp_by_id(mcp_id)

    def update_mcp(self, mcp_id: str, **kwargs) -> MCP:
        """Update an existing MCP."""
        data = self._request("PUT", f"/mcps/{mcp_id}", json=kwargs)
        return MCP(**data)._set_client(self)

    def delete_mcp(self, mcp_id: str) -> None:
        """Delete an MCP."""
        self._request("DELETE", f"/mcps/{mcp_id}")

    def get_mcp_tools(self, mcp_id: str) -> list[dict[str, Any]]:
        """Get tools available from an MCP."""
        data = self._request("GET", f"/mcps/{mcp_id}/tools")
        return data or []
