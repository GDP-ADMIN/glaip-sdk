#!/usr/bin/env python3
"""Integration tests for the AIP SDK.

These tests require a running backend and test actual API interactions.
Run with: pytest tests/integration/ -m integration
"""

import os
import uuid

import pytest

from glaip_sdk import Client


@pytest.mark.integration
@pytest.mark.sdk
class TestSDKIntegration:
    """Integration tests for the AIP SDK."""

    def setup_method(self):
        """Set up the SDK client for testing."""
        api_key = os.getenv("AIP_API_KEY")
        api_url = os.getenv("AIP_API_URL")

        if not api_key or not api_url:
            pytest.skip("AIP_API_KEY and AIP_API_URL environment variables required")

        self.client = Client(api_url=api_url, api_key=api_key)
        self.test_agent_name = f"test-sdk-agent-{uuid.uuid4().hex[:8]}"

    def test_list_agents(self):
        """Test listing agents."""
        agents = self.client.list_agents()
        assert isinstance(agents, list)
        assert len(agents) > 0

        # Check that agents have required fields
        for agent in agents:
            assert hasattr(agent, "id")
            assert hasattr(agent, "name")

    def test_create_and_delete_agent(self):
        """Test creating and deleting an agent."""
        # Create agent
        agent = self.client.create_agent(
            name=self.test_agent_name,
            instruction="Test agent for SDK integration testing",
        )

        assert agent.id is not None
        assert agent.name == self.test_agent_name

        # Verify agent exists
        retrieved_agent = self.client.get_agent(agent.id)
        assert retrieved_agent.id == agent.id
        assert retrieved_agent.name == agent.name

        # Clean up
        self.client.delete_agent(agent.id)

        # Verify agent is deleted
        with pytest.raises(Exception):  # Should raise 404 or similar
            self.client.get_agent(agent.id)

    def test_agent_lifecycle(self):
        """Test complete agent lifecycle."""
        # Create
        agent = self.client.create_agent(
            name=f"{self.test_agent_name}-lifecycle",
            instruction="Test agent for lifecycle testing",
        )

        # Update
        updated_agent = self.client.update_agent(
            agent.id, {"description": "Updated description"}
        )
        assert updated_agent.description == "Updated description"

        # Clean up
        self.client.delete_agent(agent.id)

    def test_list_tools(self):
        """Test listing tools."""
        tools = self.client.list_tools()
        assert isinstance(tools, list)

        # Check that tools have required fields
        for tool in tools:
            assert hasattr(tool, "id")
            assert hasattr(tool, "name")

    def test_list_mcps(self):
        """Test listing MCPs."""
        mcps = self.client.list_mcps()
        assert isinstance(mcps, list)

        # Check that MCPs have required fields
        for mcp in mcps:
            assert hasattr(mcp, "id")
            assert hasattr(mcp, "name")

    def test_list_language_models(self):
        """Test listing language models."""
        models = self.client.list_language_models()
        assert isinstance(models, list)

        # Check that models have required fields
        for model in models:
            assert "provider" in model
            assert "name" in model

    def test_error_handling(self):
        """Test error handling for invalid requests."""
        # Test getting non-existent agent
        with pytest.raises(Exception):
            self.client.get_agent("non-existent-id")

        # Test creating agent with invalid data
        with pytest.raises(Exception):
            self.client.create_agent(
                name="",  # Empty name should fail
                instruction="Test",
            )


if __name__ == "__main__":
    # Run integration tests directly
    pytest.main([__file__, "-v", "-m", "integration"])
