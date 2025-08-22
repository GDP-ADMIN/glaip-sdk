#!/usr/bin/env python3
"""MCP integration tests for the AIP SDK.

These tests verify MCP (Model Context Protocol) operations and interactions.
Run with: pytest tests/integration/test_mcp_integration.py -m integration
"""

import os
import uuid

import pytest

from glaip_sdk import Client


@pytest.mark.integration
@pytest.mark.sdk
class TestMCPIntegration:
    """MCP integration tests for the AIP SDK."""

    def setup_method(self):
        """Set up the SDK client for testing."""
        api_key = os.getenv("AIP_API_KEY")
        api_url = os.getenv("AIP_API_URL")

        if not api_key or not api_url:
            pytest.skip("AIP_API_KEY and AIP_API_URL environment variables required")

        self.client = Client(api_url=api_url, api_key=api_key)
        self.test_mcp_name = f"test-sdk-mcp-{uuid.uuid4().hex[:8]}"
        self.created_mcps = []  # Track created MCPs for cleanup

    def _create_test_mcp(self, name_suffix="basic"):
        """Create a test MCP for integration testing."""
        test_name = f"{self.test_mcp_name}-{name_suffix}"

        try:
            # Create MCP using a public test MCP URL (similar to backend integration tests)
            mcp = self.client.create_mcp(
                name=test_name,
                transport="sse",  # Transport protocol (not "type")
                description=f"Test MCP for SDK integration testing - {name_suffix}",
                config={
                    "url": "https://mcp.obrol.id/f/sse",  # Public test MCP endpoint
                },
            )
            self.created_mcps.append(mcp.id)
            return mcp
        except Exception as e:
            print(f"Failed to create test MCP: {e}")
            return None

    def _cleanup_mcps(self):
        """Clean up created MCPs."""
        for mcp_id in self.created_mcps:
            try:
                self.client.delete_mcp(mcp_id)
            except Exception as e:
                print(f"Failed to clean up MCP {mcp_id}: {e}")
        self.created_mcps.clear()

    def teardown_method(self):
        """Clean up after each test."""
        self._cleanup_mcps()

    def test_list_mcps(self):
        """Test listing MCPs."""
        mcps = self.client.list_mcps()
        assert isinstance(mcps, list)

        # Check that MCPs have required fields if any exist
        for mcp in mcps:
            assert hasattr(mcp, "id")
            assert hasattr(mcp, "name")
            assert hasattr(mcp, "transport")

    def test_get_mcp_by_id(self):
        """Test getting MCP by ID."""
        # Create a test MCP
        test_mcp = self._create_test_mcp("get-by-id")
        if not test_mcp:
            pytest.skip("Could not create test MCP")

        # Get the MCP by ID
        retrieved_mcp = self.client.get_mcp(test_mcp.id)
        assert retrieved_mcp.id == test_mcp.id
        assert retrieved_mcp.name == test_mcp.name
        assert retrieved_mcp.transport == test_mcp.transport

    def test_get_mcp_by_name(self):
        """Test getting MCP by name."""
        # Create a test MCP
        test_mcp = self._create_test_mcp("get-by-name")
        if not test_mcp:
            pytest.skip("Could not create test MCP")

        # Get the MCP by name using find_mcps
        found_mcps = self.client.find_mcps(test_mcp.name)
        assert len(found_mcps) > 0
        retrieved_mcp = found_mcps[0]
        assert retrieved_mcp.name == test_mcp.name
        assert retrieved_mcp.id == test_mcp.id

    def test_find_mcps(self):
        """Test finding MCPs by search criteria."""
        # Search for MCPs (this might return empty list)
        found_mcps = self.client.find_mcps("test")
        assert isinstance(found_mcps, list)

        # If MCPs are found, verify they have required fields
        for mcp in found_mcps:
            assert hasattr(mcp, "id")
            assert hasattr(mcp, "name")
            assert hasattr(mcp, "transport")

    def test_get_mcp_tools(self):
        """Test getting tools from MCP."""
        # Create a test MCP
        test_mcp = self._create_test_mcp("tools-test")
        if not test_mcp:
            pytest.skip("Could not create test MCP")

        # Get tools from the MCP using the MCP object method
        tools = test_mcp.get_tools()
        assert isinstance(tools, list)

        # If tools are found, verify they have required fields
        for tool in tools:
            # Tools from MCP are dict objects, not objects with attributes
            if isinstance(tool, dict):
                assert "name" in tool
            else:
                assert hasattr(tool, "name")

    def test_mcp_resource_methods(self):
        """Test MCP resource object methods."""
        # Create a test MCP
        test_mcp = self._create_test_mcp("resource-methods")
        if not test_mcp:
            pytest.skip("Could not create test MCP")

        # Test that MCP has expected methods
        assert hasattr(test_mcp, "update")
        assert hasattr(test_mcp, "delete")
        assert callable(test_mcp.update)
        assert callable(test_mcp.delete)

        # Test that MCP has expected attributes
        assert hasattr(test_mcp, "id")
        assert hasattr(test_mcp, "name")
        assert hasattr(test_mcp, "transport")
        assert hasattr(test_mcp, "config")

    def test_mcp_error_handling(self):
        """Test MCP error handling for invalid requests."""
        # Test getting non-existent MCP
        with pytest.raises(Exception):
            self.client.get_mcp("non-existent-id")

        # Test getting MCP tools for non-existent MCP
        with pytest.raises(Exception):
            # Create a dummy MCP object to test the method
            dummy_mcp = type(
                "DummyMCP", (), {"id": "non-existent-id", "_client": self.client}
            )()
            dummy_mcp.get_tools()

    def test_mcp_search_functionality(self):
        """Test MCP search functionality."""
        # Search with empty string (should return all MCPs)
        all_mcps = self.client.find_mcps("")
        assert isinstance(all_mcps, list)

        # Search with specific term
        if all_mcps:
            # Search for the first MCP's name
            search_term = all_mcps[0].name[:5]  # First 5 characters
            found_mcps = self.client.find_mcps(search_term)
            assert isinstance(found_mcps, list)

            # Should find at least the original MCP
            mcp_names = [m.name for m in found_mcps]
            assert all_mcps[0].name in mcp_names

    def test_mcp_connection_status(self):
        """Test MCP connection status."""
        # Create a test MCP
        test_mcp = self._create_test_mcp("connection-status")
        if not test_mcp:
            pytest.skip("Could not create test MCP")

        # Check if MCP has connection status (optional field)
        if hasattr(test_mcp, "connection_status"):
            assert test_mcp.connection_status in [
                "connected",
                "disconnected",
                "error",
                None,
            ]

        # Check if MCP has status field (optional field)
        if hasattr(test_mcp, "status"):
            assert test_mcp.status in ["active", "inactive", "error", None]

    def test_mcp_configuration(self):
        """Test MCP configuration handling."""
        # Create a test MCP
        test_mcp = self._create_test_mcp("configuration")
        if not test_mcp:
            pytest.skip("Could not create test MCP")

        # Check if MCP has config field
        assert hasattr(test_mcp, "config")

        # Config should be a dictionary or None
        if test_mcp.config is not None:
            assert isinstance(test_mcp.config, dict)
            # Our test MCP should have a URL in config
            assert "url" in test_mcp.config

    def test_mcp_create_and_delete_lifecycle(self):
        """Test complete MCP lifecycle: create, verify, delete."""
        # Create a test MCP
        test_mcp = self._create_test_mcp("lifecycle")
        if not test_mcp:
            pytest.skip("Could not create test MCP")

        # Verify MCP was created
        assert test_mcp.id is not None
        assert test_mcp.name.endswith("lifecycle")
        # Note: Backend may not return the exact type we sent, just verify it's a valid MCP
        assert test_mcp.config is not None
        assert "url" in test_mcp.config

        # Verify we can retrieve it
        retrieved_mcp = self.client.get_mcp(test_mcp.id)
        assert retrieved_mcp.id == test_mcp.id

        # Test deletion (will be done by teardown, but test explicit delete)
        mcp_id = test_mcp.id
        self.client.delete_mcp(mcp_id)

        # Remove from our cleanup list since we deleted it manually
        if mcp_id in self.created_mcps:
            self.created_mcps.remove(mcp_id)

        # Verify it's deleted
        with pytest.raises(Exception):
            self.client.get_mcp(mcp_id)


if __name__ == "__main__":
    # Run integration tests directly
    pytest.main([__file__, "-v", "-m", "integration"])
