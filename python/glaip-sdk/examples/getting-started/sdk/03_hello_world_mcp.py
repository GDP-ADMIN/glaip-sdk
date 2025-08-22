#!/usr/bin/env python3
"""03_hello_world_mcp.py - Hello World MCP Example

Goal: Create and manage a simple MCP (Model Context Protocol) server using the AIP SDK

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from _utils import demonstrate_mcp_lifecycle

from glaip_sdk import Client

client = Client()

demonstrate_mcp_lifecycle()

mcp = client.create_mcp(
    name="hello-world-mcp",
    description="A simple MCP server for demonstration",
    transport="http",
    config={
        "url": "http://localhost:8080",
        "message": "Hello from MCP!",
        "version": "1.0.0",
        "tools": ["hello", "time"],
    },
)

mcp.delete()
