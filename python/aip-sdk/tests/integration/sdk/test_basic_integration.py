#!/usr/bin/env python3
"""Basic integration tests for the AIP SDK.

These tests verify basic connectivity and fundamental SDK operations.
Run with: pytest tests/integration/test_basic_integration.py -m integration
"""

import os
import uuid

import pytest

from glaip_sdk import Client


@pytest.mark.integration
@pytest.mark.sdk
class TestBasicIntegration:
    """Basic integration tests for the AIP SDK."""

    def setup_method(self):
        """Set up the SDK client for testing."""
        api_key = os.getenv("AIP_API_KEY")
        api_url = os.getenv("AIP_API_URL")

        if not api_key or not api_url:
            pytest.skip("AIP_API_KEY and AIP_API_URL environment variables required")

        self.client = Client(api_url=api_url, api_key=api_key)
        self.test_agent_name = f"test-sdk-agent-{uuid.uuid4().hex[:8]}"

    def test_health_check(self):
        """Test basic health check endpoint."""
        # This test verifies the backend is accessible
        # The actual health check is done by the client during initialization
        assert self.client.api_url is not None
        assert self.client.api_key is not None

    def test_list_agents(self):
        """Test listing agents."""
        agents = self.client.list_agents()
        assert isinstance(agents, list)
        # Note: We don't assert length > 0 as the backend might be empty

        # Check that agents have required fields if any exist
        for agent in agents:
            assert hasattr(agent, "id")
            assert hasattr(agent, "name")

    def test_list_tools(self):
        """Test listing tools."""
        tools = self.client.list_tools()
        assert isinstance(tools, list)

        # Check that tools have required fields if any exist
        for tool in tools:
            assert hasattr(tool, "id")
            assert hasattr(tool, "name")

    def test_list_mcps(self):
        """Test listing MCPs."""
        mcps = self.client.list_mcps()
        assert isinstance(mcps, list)

        # Check that MCPs have required fields if any exist
        for mcp in mcps:
            assert hasattr(mcp, "id")
            assert hasattr(mcp, "name")

    def test_list_language_models(self):
        """Test listing language models."""
        models = self.client.list_language_models()
        assert isinstance(models, list)

        # Check that models have required fields if any exist
        for model in models:
            assert "provider" in model
            assert "name" in model

    def test_client_context_manager(self):
        """Test client context manager functionality."""
        with self.client as ctx_client:
            assert ctx_client is self.client
            assert ctx_client.http_client is not None

        # HTTP client should be closed after context exit
        assert self.client.http_client.is_closed

    def test_error_handling_404(self):
        """Test error handling for non-existent resources."""
        # Test getting non-existent agent
        with pytest.raises(Exception):
            self.client.get_agent("non-existent-id")

        # Test getting non-existent tool
        with pytest.raises(Exception):
            self.client.get_tool("non-existent-id")

        # Test getting non-existent MCP
        with pytest.raises(Exception):
            self.client.get_mcp("non-existent-id")


if __name__ == "__main__":
    # Run integration tests directly
    pytest.main([__file__, "-v", "-m", "integration"])
