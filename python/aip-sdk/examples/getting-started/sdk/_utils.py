"""Utility functions for getting-started examples."""

import tempfile
import uuid
from pathlib import Path
from typing import Any


def create_hello_tool_script() -> Path:
    """Create a simple hello world tool script."""
    script_content = '''#!/usr/bin/env python3
"""Hello World Tool - A simple example tool for the AIP SDK."""

def hello_world(name: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {name}! Welcome to the AI Agent Platform! 🚀"

def get_tool_info() -> dict:
    """Get information about this tool."""
    return {
        "name": "hello_world",
        "description": "A simple tool that says hello",
        "functions": ["hello_world", "get_tool_info"]
    }
'''

    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    temp_file.write(script_content)
    temp_file.close()
    return Path(temp_file.name)


def create_calculator_tool_script() -> Path:
    """Create a simple calculator tool script."""
    script_content = '''#!/usr/bin/env python3
"""Calculator Tool - A simple example tool for the AIP SDK."""

def calculator(operation: str, a: float, b: float) -> str:
    """Basic calculator operations."""
    if operation == "add":
        return f"{a} + {b} = {a + b}"
    elif operation == "multiply":
        return f"{a} × {b} = {a * b}"
    elif operation == "divide":
        return f"{a} ÷ {b} = {a / b}" if b != 0 else "Error: Cannot divide by zero"
    return f"Error: Unknown operation '{operation}'"
'''

    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    temp_file.write(script_content)
    temp_file.close()
    return Path(temp_file.name)


def generate_unique_name(prefix: str) -> str:
    """Generate a unique name with prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def cleanup_temp_file(file_path: Path) -> None:
    """Clean up temporary file."""
    if file_path and file_path.exists():
        file_path.unlink()


class SimpleMCPServer:
    """A simple MCP server implementation for demonstration."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.is_running = False
        self.connected_clients = 0
        self.tools = {
            "hello": {
                "name": "hello",
                "description": "Say hello to someone",
                "parameters": {"name": "string"},
                "returns": "string",
            },
            "time": {
                "name": "time",
                "description": "Get current time",
                "parameters": {},
                "returns": "string",
            },
        }

    def start(self) -> bool:
        """Start the MCP server."""
        self.is_running = True
        return True

    def stop(self) -> bool:
        """Stop the MCP server."""
        self.is_running = False
        return True

    def handshake(self, client_id: str) -> dict[str, Any]:
        """Perform MCP handshake with a client."""
        if not self.is_running:
            raise RuntimeError("Server is not running")

        self.connected_clients += 1
        return {
            "protocol": "mcp",
            "version": "1.0.0",
            "capabilities": {
                "tools": list(self.tools.keys()),
                "resources": ["time", "hello"],
                "prompts": [],
            },
            "server": {"name": self.name, "description": self.description},
        }

    def call_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool call."""
        if not self.is_running:
            raise RuntimeError("Server is not running")

        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        if tool_name == "hello":
            name = kwargs.get("name", "World")
            return f"Hello, {name}! Welcome to the MCP server."
        elif tool_name == "time":
            import datetime

            return (
                f"Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        else:
            return f"Tool {tool_name} executed with parameters: {kwargs}"

    def get_status(self) -> dict[str, Any]:
        """Get server status."""
        return {
            "name": self.name,
            "running": self.is_running,
            "connected_clients": self.connected_clients,
            "available_tools": list(self.tools.keys()),
            "uptime": "demonstration mode",
        }


def demonstrate_mcp_lifecycle() -> bool:
    """Demonstrate complete MCP server lifecycle."""
    server = SimpleMCPServer(
        name="demo-mcp-server",
        description="A demonstration MCP server with basic tools",
    )

    try:
        server.start()
        client_id = "demo-client-001"
        server.handshake(client_id)
        server.call_tool("hello", name="Alice")
        server.call_tool("time")
        server.stop()
        return True
    except Exception:
        return False
