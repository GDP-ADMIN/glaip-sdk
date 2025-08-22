"""Test configuration and fixtures for the AI Agent Platform SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from unittest.mock import Mock
from uuid import uuid4

import pytest

from glaip_sdk.client import Client


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    return Mock(spec=Client)


@pytest.fixture
def valid_uuid():
    """Generate a valid UUID for testing."""
    return str(uuid4())


@pytest.fixture
def sample_agent_data(valid_uuid):
    """Sample agent data for testing."""
    return {
        "id": valid_uuid,
        "name": "test-agent",
        "type": "config",
        "framework": "langchain",
        "version": "1.0",
        "instruction": "Test instruction for the agent",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "metadata": {"test": "value"},
        "status": "active",
    }


@pytest.fixture
def sample_tool_data(valid_uuid):
    """Sample tool data for testing."""
    return {
        "id": valid_uuid,
        "name": "test-tool",
        "framework": "langchain",
        "script": "def test_function(): pass",
        "description": "Test tool",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "active",
    }


@pytest.fixture
def sample_mcp_data(valid_uuid):
    """Sample MCP data for testing."""
    return {
        "id": valid_uuid,
        "name": "test-mcp",
        "type": "openai",
        "transport": "http",
        "config": {"api_key": "test-key"},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "connected",
        "connection_status": "active",
    }


@pytest.fixture
def sample_base_resource_data(valid_uuid):
    """Sample base resource data for testing."""
    return {
        "id": valid_uuid,
        "name": "test-resource",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "metadata": {"test": "value"},
    }


@pytest.fixture
def sample_agent_create_data():
    """Sample agent creation data for testing."""
    return {
        "name": "test-agent",
        "instruction": "Test instruction for the agent",
        "type": "config",
        "framework": "langchain",
        "version": "1.0",
        "timeout": 300,
    }


@pytest.fixture
def sample_tool_create_data():
    """Sample tool creation data for testing."""
    return {
        "name": "test-tool",
        "framework": "langchain",
        "description": "Test tool description",
    }


@pytest.fixture
def sample_mcp_create_data():
    """Sample MCP creation data for testing."""
    return {
        "name": "test-mcp",
        "type": "openai",
        "transport": "http",
        "config": {"api_key": "test-key"},
    }


@pytest.fixture
def sample_language_model_data():
    """Sample language model data for testing."""
    return {
        "provider": "openai",
        "name": "gpt-4o-mini",
        "capabilities": ["text-generation", "chat"],
        "max_tokens": 4096,
        "pricing": {"input": 0.00001, "output": 0.00003},
    }
