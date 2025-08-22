#!/usr/bin/env python3
"""Shared helper functions for AIP SDK integration tests.

This module provides common functionality used across all SDK integration tests,
including client setup, resource management, test data creation, and utility functions.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from glaip_sdk import Client
from glaip_sdk.exceptions import AIPError, NotFoundError
from glaip_sdk.models import Agent


# Environment Configuration
def get_test_environment() -> tuple[str, str]:
    """Get test environment configuration.

    Returns:
        Tuple of (api_url, api_key)

    Raises:
        pytest.skip: If required environment variables are missing
    """
    api_key = os.getenv("AIP_API_KEY")
    api_url = os.getenv("AIP_API_URL")

    if not api_key or not api_url:
        pytest.skip("AIP_API_KEY and AIP_API_URL environment variables required")

    return api_url, api_key


def create_test_client(timeout: float = 30.0) -> Client:
    """Create a test client with proper configuration.

    Args:
        timeout: Request timeout in seconds

    Returns:
        Configured Client instance

    Raises:
        pytest.skip: If required environment variables are missing
    """
    api_url, api_key = get_test_environment()
    return Client(api_url=api_url, api_key=api_key, timeout=timeout)


# Test Data Generation
def generate_test_name(prefix: str = "test-sdk", max_length: int = 8) -> str:
    """Generate a unique test name with UUID.

    Args:
        prefix: Prefix for the test name
        max_length: Maximum length for the UUID part

    Returns:
        Unique test name
    """
    uuid_part = uuid.uuid4().hex[:max_length]
    return f"{prefix}-{uuid_part}"


def generate_test_instruction(agent_type: str = "general") -> str:
    """Generate test agent instruction based on type.

    Args:
        agent_type: Type of agent instruction to generate

    Returns:
        Test instruction string
    """
    base_instruction = {
        "general": "You are a helpful AI assistant. Answer questions clearly and concisely.",
        "math": "You are a math expert. Solve problems step by step and show your work.",
        "writing": "You are a writing expert. Help with composition, editing, and language tasks.",
        "research": "You are a research expert. Analyze information and provide insights.",
        "simple": "You are a simple assistant. Respond briefly and directly.",
    }

    return base_instruction.get(agent_type, base_instruction["general"])


def create_test_tool_file(content: str = None, filename: str = None) -> str:
    """Create a temporary test tool file.

    Args:
        content: Tool script content (defaults to simple test tool)
        filename: Custom filename (defaults to auto-generated)

    Returns:
        Path to the created temporary file
    """
    if content is None:
        content = '''from glaip_sdk import tool_plugin

@tool_plugin
def test_tool(input_text: str = "Hello") -> str:
    """A simple test tool for integration testing."""
    return f"Test tool executed with input: {input_text}"
'''

    if filename is None:
        filename = f"test_tool_{uuid.uuid4().hex[:8]}.py"

    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    temp_file.write(content)
    temp_file.close()

    return temp_file.name


# Resource Management
class ResourceManager:
    """Manages test resources for automatic cleanup."""

    def __init__(self, client: Client):
        """Initialize resource manager.

        Args:
            client: SDK client instance
        """
        self.client = client
        self.agents = []
        self.tools = []
        self.mcps = []
        self.temp_files = []

    def add_agent(self, agent_id: str) -> None:
        """Add agent to cleanup list.

        Args:
            agent_id: Agent ID to track
        """
        self.agents.append(agent_id)

    def add_tool(self, tool_id: str) -> None:
        """Add tool to cleanup list.

        Args:
            tool_id: Tool ID to track
        """
        self.tools.append(tool_id)

    def add_mcp(self, mcp_id: str) -> None:
        """Add MCP to cleanup list.

        Args:
            mcp_id: MCP ID to track
        """
        self.mcps.append(mcp_id)

    def add_temp_file(self, file_path: str) -> None:
        """Add temporary file to cleanup list.

        Args:
            file_path: Path to temporary file
        """
        self.temp_files.append(file_path)

    def cleanup(self) -> None:
        """Clean up all tracked resources."""
        # Clean up agents
        for agent_id in self.agents:
            try:
                self.client.delete_agent(agent_id)
            except Exception as e:
                print(f"Warning: Failed to clean up agent {agent_id}: {e}")

        # Clean up tools
        for tool_id in self.tools:
            try:
                self.client.delete_tool(tool_id)
            except Exception as e:
                print(f"Warning: Failed to clean up tool {tool_id}: {e}")

        # Clean up MCPs
        for mcp_id in self.mcps:
            try:
                self.client.delete_mcp(mcp_id)
            except Exception as e:
                print(f"Warning: Failed to clean up MCP {mcp_id}: {e}")

        # Clean up temporary files
        for file_path in self.temp_files:
            try:
                Path(file_path).unlink(missing_ok=True)
            except Exception as e:
                print(f"Warning: Failed to clean up temp file {file_path}: {e}")

        # Clear lists
        self.agents.clear()
        self.tools.clear()
        self.mcps.clear()
        self.temp_files.clear()


# Resource Creation Helpers
def create_test_agent(
    client: Client,
    name: str = None,
    instruction: str = None,
    tools: list[str] = None,
    agents: list[str] = None,
    timeout: int = 300,
    cleanup: bool = True,
) -> Agent:
    """Create a test agent for integration testing.

    Args:
        client: Client instance
        name: Agent name (auto-generated if not provided)
        instruction: Agent instruction (auto-generated if not provided)
        tools: Tool names to attach
        agents: Sub-agent names to attach
        timeout: Execution timeout
        cleanup: Whether to register for cleanup

    Returns:
        Created agent instance
    """
    if name is None:
        name = f"test-agent-{uuid4().hex[:8]}"

    if instruction is None:
        instruction = generate_test_instruction("simple")

    # Create resource manager for cleanup
    resource_manager = ResourceManager(client)

    try:
        # Create agent
        agent = client.create_agent(
            name=name,
            instruction=instruction,
            tools=tools or [],
            agents=agents or [],
            timeout=timeout,
        )

        # Track for cleanup
        resource_manager.add_agent(agent.id)

        return agent, resource_manager

    except Exception as e:
        resource_manager.cleanup()
        raise e


def create_test_tool(
    client: Client,
    file_path: str = None,
    framework: str = "langchain",
    description: str = None,
) -> tuple[Any, ResourceManager]:
    """Create a test tool with automatic cleanup.

    Args:
        client: SDK client instance
        file_path: Path to tool file (auto-created if not provided)
        framework: Tool framework
        description: Tool description

    Returns:
        Tuple of (created_tool, resource_manager)
    """
    # Create resource manager for cleanup
    resource_manager = ResourceManager(client)

    try:
        # Create tool file if not provided
        if file_path is None:
            file_path = create_test_tool_file()
            resource_manager.add_temp_file(file_path)

        # Create tool
        tool = client.create_tool(
            file_path=file_path,
            framework=framework,
            description=description or "Test tool for integration testing",
        )

        # Track for cleanup
        resource_manager.add_tool(tool.id)

        return tool, resource_manager

    except Exception as e:
        resource_manager.cleanup()
        raise e


def create_test_mcp(
    client: Client,
    name: str = None,
    description: str = None,
    config: dict[str, Any] = None,
    **kwargs,
) -> tuple[Any, ResourceManager]:
    """Create a test MCP with automatic cleanup.

    Args:
        client: SDK client instance
        name: MCP name (auto-generated if not provided)
        description: MCP description
        config: MCP configuration
        **kwargs: Additional MCP creation parameters

    Returns:
        Tuple of (created_mcp, resource_manager)
    """
    if name is None:
        name = generate_test_name("test-mcp")

    if description is None:
        description = "Test MCP for integration testing"

    if config is None:
        config = {"url": "https://mcp.obrol.id/f/sse"}

    # Create resource manager for cleanup
    resource_manager = ResourceManager(client)

    try:
        # Create MCP
        mcp = client.create_mcp(
            name=name, description=description, config=config, **kwargs
        )

        # Track for cleanup
        resource_manager.add_mcp(mcp.id)

        return mcp, resource_manager

    except Exception as e:
        resource_manager.cleanup()
        raise e


# Validation Helpers
def assert_agent_created(agent: Any, expected_name: str = None) -> None:
    """Assert that an agent was created successfully.

    Args:
        agent: Created agent object
        expected_name: Expected agent name (optional)
    """
    assert agent is not None, "Agent should not be None"
    assert hasattr(agent, "id"), "Agent should have an ID"
    assert agent.id is not None, "Agent ID should not be None"

    if expected_name:
        assert agent.name == expected_name, f"Agent name should be '{expected_name}'"


def assert_tool_created(tool: Any, expected_framework: str = None) -> None:
    """Assert that a tool was created successfully.

    Args:
        tool: Created tool object
        expected_framework: Expected tool framework (optional)
    """
    assert tool is not None, "Tool should not be None"
    assert hasattr(tool, "id"), "Tool should have an ID"
    assert tool.id is not None, "Tool ID should not be None"

    if expected_framework:
        assert (
            tool.framework == expected_framework
        ), f"Tool framework should be '{expected_framework}'"


def assert_mcp_created(mcp: Any, expected_name: str = None) -> None:
    """Assert that an MCP was created successfully.

    Args:
        mcp: Created MCP object
        expected_name: Expected MCP name (optional)
    """
    assert mcp is not None, "MCP should not be None"
    assert hasattr(mcp, "id"), "MCP should have an ID"
    assert mcp.id is not None, "MCP ID should not be None"

    if expected_name:
        assert mcp.name == expected_name, f"MCP name should be '{expected_name}'"


# Error Testing Helpers
def assert_raises_not_found(func, *args, **kwargs):
    """Assert that a function raises NotFoundError.

    Args:
        func: Function to call
        *args: Function arguments
        **kwargs: Function keyword arguments
    """
    with pytest.raises(NotFoundError):
        func(*args, **kwargs)


def assert_raises_validation_error(func, *args, **kwargs):
    """Assert that a function raises ValidationError.

    Args:
        func: Function to call
        *args: Function arguments
        **kwargs: Function keyword arguments
    """
    from glaip_sdk.exceptions import ValidationError

    with pytest.raises(ValidationError):
        func(*args, **kwargs)


def assert_raises_aip_error(func, *args, **kwargs):
    """Assert that a function raises any AIPError.

    Args:
        func: Function to call
        *args: Function arguments
        **kwargs: Function keyword arguments
    """
    with pytest.raises(AIPError):
        func(*args, **kwargs)


# Test Data Utilities
def create_test_payload(
    input_text: str = "Hello", chat_history: list[dict[str, str]] = None
) -> dict[str, Any]:
    """Create a test payload for agent execution.

    Args:
        input_text: Input text for the agent
        chat_history: Optional chat history

    Returns:
        Test payload dictionary
    """
    payload = {"input": input_text}

    if chat_history:
        payload["chat_history"] = chat_history

    return payload


def create_test_chat_history(
    messages: list[tuple[str, str]] = None,
) -> list[dict[str, str]]:
    """Create test chat history.

    Args:
        messages: List of (role, content) tuples

    Returns:
        Chat history list
    """
    if messages is None:
        messages = [
            ("user", "Hello"),
            ("assistant", "Hi there! How can I help you today?"),
            ("user", "What's the weather like?"),
        ]

    return [{"role": role, "content": content} for role, content in messages]


# File Handling Helpers
def create_test_file(content: str, suffix: str = ".txt") -> str:
    """Create a temporary test file.

    Args:
        content: File content
        suffix: File suffix

    Returns:
        Path to the created temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False)
    temp_file.write(content)
    temp_file.close()
    return temp_file.name


def cleanup_temp_file(file_path: str) -> None:
    """Clean up a temporary file.

    Args:
        file_path: Path to the temporary file
    """
    try:
        Path(file_path).unlink(missing_ok=True)
    except Exception as e:
        print(f"Warning: Failed to clean up temp file {file_path}: {e}")


# Context Manager for Resource Management
class TestResourceContext:
    """Context manager for automatic test resource cleanup."""

    def __init__(self, client: Client):
        """Initialize test resource context.

        Args:
            client: SDK client instance
        """
        self.client = client
        self.resource_manager = ResourceManager(client)

    def __enter__(self):
        """Enter the context."""
        return self.resource_manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and clean up resources."""
        self.resource_manager.cleanup()


# Decorator for automatic cleanup
def with_resource_cleanup(func):
    """Decorator to automatically clean up test resources.

    This decorator creates a ResourceManager and passes it as the last argument
    to the decorated function, then automatically cleans up after the function completes.

    Usage:
        @with_resource_cleanup
        def test_something(client, resource_manager):
            # Test code here
            pass
    """

    def wrapper(*args, **kwargs):
        # Find the client argument
        client = None
        for arg in args:
            if isinstance(arg, Client):
                client = arg
                break

        if not client:
            for value in kwargs.values():
                if isinstance(value, Client):
                    client = value
                    break

        if not client:
            raise ValueError("No Client instance found in arguments")

        # Create resource manager
        resource_manager = ResourceManager(client)

        try:
            # Call the function with resource manager
            result = func(*args, resource_manager, **kwargs)
            return result
        finally:
            # Always clean up
            resource_manager.cleanup()

    return wrapper


# Health Check Helpers
def check_backend_health(client: Client) -> bool:
    """Check if the backend is healthy by making a simple API call.

    Args:
        client: SDK client instance

    Returns:
        True if backend is healthy, False otherwise
    """
    try:
        # Try to list agents as a health check
        client.list_agents()
        return True
    except Exception:
        return False


def ensure_backend_healthy(client: Client) -> None:
    """Ensure the backend is healthy, skip test if not.

    Args:
        client: SDK client instance

    Raises:
        pytest.skip: If backend is not healthy
    """
    if not check_backend_health(client):
        pytest.skip("Backend is not healthy")


# Test Configuration
def get_test_config() -> dict[str, Any]:
    """Get test configuration.

    Returns:
        Test configuration dictionary
    """
    return {
        "default_model": "gpt-4o-mini",
        "default_timeout": 300,
        "default_framework": "langchain",
        "test_mcp_url": "https://mcp.obrol.id/f/sse",
        "max_retries": 3,
        "retry_delay": 1.0,
    }


# Retry Helpers
def retry_on_failure(func, max_retries: int = 3, delay: float = 1.0):
    """Retry a function on failure.

    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Delay between retries in seconds

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    import time

    last_exception = None
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                time.sleep(delay)
                continue
            else:
                raise last_exception


# Logging Helpers
def log_test_step(step_name: str) -> None:
    """Log a test step for debugging.

    Args:
        step_name: Name of the test step
    """
    print(f"\n{'='*20} {step_name} {'='*20}")


def log_resource_creation(
    resource_type: str, resource_id: str, resource_name: str = None
) -> None:
    """Log resource creation for debugging.

    Args:
        resource_type: Type of resource (agent, tool, mcp)
        resource_id: Resource ID
        resource_name: Resource name (optional)
    """
    name_info = f" ({resource_name})" if resource_name else ""
    print(f"✅ Created {resource_type}: {resource_id}{name_info}")


def log_resource_cleanup(resource_type: str, resource_id: str) -> None:
    """Log resource cleanup for debugging.

    Args:
        resource_type: Type of resource (agent, tool, mcp)
        resource_id: Resource ID
    """
    print(f"🧹 Cleaned up {resource_type}: {resource_id}")
