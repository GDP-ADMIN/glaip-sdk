#!/usr/bin/env python3
"""Tool integration tests for the AIP SDK.

These tests verify tool management operations and interactions.
Run with: pytest tests/integration/test_tool_integration.py -m integration
"""

import os
import uuid

import pytest

from glaip_sdk import Client
from glaip_sdk.exceptions import NotFoundError


@pytest.mark.integration
@pytest.mark.sdk
class TestToolIntegration:
    """Tool integration tests for the AIP SDK."""

    def setup_method(self):
        """Set up the SDK client for testing."""
        api_key = os.getenv("AIP_API_KEY")
        api_url = os.getenv("AIP_API_URL")

        if not api_key or not api_url:
            pytest.skip("AIP_API_KEY and AIP_API_URL environment variables required")

        self.client = Client(api_url=api_url, api_key=api_key)
        self.test_tool_name = f"test-sdk-tool-{uuid.uuid4().hex[:8]}"
        self.created_tools = []  # Track created tools for cleanup

    def test_list_tools(self):
        """Test listing tools."""
        tools = self.client.list_tools()
        assert isinstance(tools, list)

        # Check that tools have required fields if any exist
        for tool in tools:
            assert hasattr(tool, "id")
            assert hasattr(tool, "name")

    def test_get_tool_by_id(self):
        """Test getting tool by ID."""
        # First, get a list of tools
        tools = self.client.list_tools()
        if not tools:
            pytest.skip("No tools available for testing")

        # Get the first tool by ID
        tool = self.client.get_tool(tools[0].id)
        assert tool.id == tools[0].id
        assert tool.name == tools[0].name

    def test_get_tool_by_name(self):
        """Test getting tool by name."""
        # First, get a list of tools
        tools = self.client.list_tools()
        if not tools:
            pytest.skip("No tools available for testing")

        # Find a tool with a unique name to avoid ambiguity
        name_counts = {}
        for tool in tools:
            name_counts[tool.name] = name_counts.get(tool.name, 0) + 1

        # Find a name that appears only once
        unique_name = None
        for name, count in name_counts.items():
            if count == 1:
                unique_name = name
                break

        if not unique_name:
            # If no unique names, test the expected behavior with a common name
            # This should return multiple tools, which is expected
            tool_name = tools[0].name
            found_tools = self.client.find_tools(tool_name)
            assert len(found_tools) >= 1  # Should return at least 1 tool
            # Verify all returned tools have the expected name
            for tool in found_tools:
                assert tool.name == tool_name
            print(
                f"✅ Found {len(found_tools)} tools with name '{tool_name}' (expected multiple)"
            )
            return

        # Test with a unique name
        found_tools = self.client.find_tools(unique_name)
        assert len(found_tools) == 1
        tool = found_tools[0]
        assert tool is not None
        assert tool.name == unique_name

    def test_find_tools(self):
        """Test finding tools by search criteria."""
        # Search for tools (this might return empty list)
        found_tools = self.client.find_tools("test")
        assert isinstance(found_tools, list)

        # If tools are found, verify they have required fields
        for tool in found_tools:
            assert hasattr(tool, "id")
            assert hasattr(tool, "name")

    def test_get_tool_script(self):
        """Test getting tool script."""
        # First, get a list of tools
        tools = self.client.list_tools()
        if not tools:
            pytest.skip("No tools available for testing")

        # Try to get script for the first tool using the tool object method
        # Note: Many tools don't have scripts, so this is expected to fail
        try:
            script = tools[0].get_script()
            # If we get here, the tool has a script
            assert script is not None
            assert isinstance(script, str)
        except NotFoundError:
            # This is expected for tools without scripts
            pass

    def test_tool_resource_methods(self):
        """Test tool resource object methods."""
        # First, get a list of tools
        tools = self.client.list_tools()
        if not tools:
            pytest.skip("No tools available for testing")

        tool = tools[0]

        # Test that tool has expected methods
        assert hasattr(tool, "update")
        assert hasattr(tool, "delete")
        assert callable(tool.update)
        assert callable(tool.delete)

        # Test that tool has expected attributes
        assert hasattr(tool, "id")
        assert hasattr(tool, "name")
        assert hasattr(tool, "framework")

    def test_tool_error_handling(self):
        """Test tool error handling for invalid requests."""
        # Test getting non-existent tool
        with pytest.raises(Exception):
            self.client.get_tool("non-existent-id")

        # Test getting tool script for non-existent tool
        with pytest.raises(Exception):
            self.client.get_tool_script("non-existent-id")

    def test_tool_search_functionality(self):
        """Test tool search functionality."""
        # Search with empty string (should return all tools)
        all_tools = self.client.find_tools("")
        assert isinstance(all_tools, list)

        # Search with specific term
        if all_tools:
            # Search for the first tool's name
            search_term = all_tools[0].name[:5]  # First 5 characters
            found_tools = self.client.find_tools(search_term)
            assert isinstance(found_tools, list)

            # Should find at least the original tool
            tool_names = [t.name for t in found_tools]
            assert all_tools[0].name in tool_names


if __name__ == "__main__":
    # Run integration tests directly
    pytest.main([__file__, "-v", "-m", "integration"])
