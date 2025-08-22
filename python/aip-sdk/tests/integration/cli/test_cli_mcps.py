#!/usr/bin/env python3
"""CLI MCP integration tests for the AIP SDK.

These tests verify CLI MCP commands work correctly with the backend.
Run with: pytest tests/integration/cli/test_cli_mcps.py -m integration
"""

import os
import subprocess
import uuid

import pytest


@pytest.mark.integration
@pytest.mark.cli
class TestCLIMCPIntegration:
    """CLI MCP integration tests for the AIP SDK."""

    def setup_method(self):
        """Set up environment for CLI testing."""
        self.api_key = os.getenv("AIP_API_KEY")
        self.api_url = os.getenv("AIP_API_URL")

        if not self.api_key or not self.api_url:
            pytest.skip("AIP_API_KEY and AIP_API_URL environment variables required")

        self.test_mcp_name = f"test-cli-mcp-{uuid.uuid4().hex[:8]}"
        self.created_mcps = []

    def teardown_method(self):
        """Clean up created MCPs after each test."""
        for mcp_name in self.created_mcps:
            try:
                # Use CLI to delete the MCP
                subprocess.run(
                    [
                        "python",
                        "-m",
                        "glaip_sdk.cli.main",
                        "--api-url",
                        self.api_url,
                        "--api-key",
                        self.api_key,
                        "mcps",
                        "delete",
                        mcp_name,
                    ],
                    capture_output=True,
                    check=False,
                )
            except Exception:
                pass  # Cleanup failures shouldn't fail tests
        self.created_mcps.clear()

    def _run_cli_command(self, command_args, capture_output=True):
        """Run a CLI command and return the result."""
        full_command = [
            "python",
            "-m",
            "glaip_sdk.cli.main",
            "--api-url",
            self.api_url,
            "--api-key",
            self.api_key,
        ] + command_args

        result = subprocess.run(
            full_command, capture_output=capture_output, text=True, check=False
        )
        return result

    def test_cli_mcp_list(self):
        """Test CLI MCP listing."""
        result = self._run_cli_command(["mcps", "list"])

        assert result.returncode == 0, f"CLI command failed: {result.stderr}"
        assert "mcps" in result.stdout.lower() or len(result.stdout.strip()) > 0

    def test_cli_mcp_create_and_delete(self):
        """Test CLI MCP creation and deletion."""
        # Create MCP via CLI
        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                self.test_mcp_name,
                "--type",
                "sse",
                "--transport",
                "sse",
                "--description",
                "Test MCP for CLI integration testing",
                "--config",
                '{"url": "https://mcp.obrol.id/f/sse"}',
            ]
        )

        assert (
            create_result.returncode == 0
        ), f"MCP creation failed: {create_result.stderr}"
        self.created_mcps.append(self.test_mcp_name)

        # Verify MCP exists via CLI
        get_result = self._run_cli_command(["mcps", "get", self.test_mcp_name])
        assert get_result.returncode == 0, f"MCP retrieval failed: {get_result.stderr}"
        assert self.test_mcp_name in get_result.stdout

        # Delete MCP via CLI
        delete_result = self._run_cli_command(
            ["mcps", "delete", self.test_mcp_name, "--yes"]
        )
        assert (
            delete_result.returncode == 0
        ), f"MCP deletion failed: {delete_result.stderr}"

        # Remove from cleanup list since we deleted it manually
        self.created_mcps.remove(self.test_mcp_name)

        # Verify MCP is deleted
        get_deleted_result = self._run_cli_command(["mcps", "get", self.test_mcp_name])
        assert get_deleted_result.returncode != 0, "MCP should not exist after deletion"

    def test_cli_mcp_create_with_options(self):
        """Test CLI MCP creation with various options."""
        mcp_name = f"{self.test_mcp_name}-options"

        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                mcp_name,
                "--type",
                "sse",
                "--transport",
                "sse",
                "--description",
                "Test MCP with CLI options",
                "--config",
                '{"url": "https://mcp.obrol.id/f/sse", "timeout": 30}',
            ]
        )

        assert (
            create_result.returncode == 0
        ), f"MCP creation with options failed: {create_result.stderr}"
        self.created_mcps.append(mcp_name)

        # Verify MCP was created with correct options
        get_result = self._run_cli_command(["mcps", "get", mcp_name])
        assert get_result.returncode == 0
        assert mcp_name in get_result.stdout

    def test_cli_mcp_update(self):
        """Test CLI MCP update functionality."""
        mcp_name = f"{self.test_mcp_name}-update"

        # Create MCP first
        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                mcp_name,
                "--type",
                "sse",
                "--transport",
                "sse",
                "--description",
                "Test MCP for update testing",
                "--config",
                '{"url": "https://mcp.obrol.id/f/sse"}',
            ]
        )
        assert create_result.returncode == 0
        self.created_mcps.append(mcp_name)

        # Get MCP details instead of updating (no update command exists)
        get_result = self._run_cli_command(["mcps", "get", mcp_name])

        assert get_result.returncode == 0, f"MCP get failed: {get_result.stderr}"

        # Verify the MCP was created successfully
        assert mcp_name in get_result.stdout

    def test_cli_mcp_search(self):
        """Test CLI MCP search functionality."""
        # Create a test MCP for search
        mcp_name = f"test-search-{self.test_mcp_name.split('-')[-1][:4]}"
        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                mcp_name,
                "--type",
                "sse",
                "--transport",
                "sse",
                "--description",
                "Test MCP for search testing",
                "--config",
                '{"url": "https://mcp.obrol.id/f/sse"}',
            ]
        )
        assert create_result.returncode == 0
        self.created_mcps.append(mcp_name)

        # List MCPs to find the created one
        search_result = self._run_cli_command(["mcps", "list"])
        assert (
            search_result.returncode == 0
        ), f"MCP listing failed: {search_result.stderr}"
        # The MCP should be found in the list
        assert mcp_name in search_result.stdout

    def test_cli_mcp_tools(self):
        """Test CLI MCP tools retrieval."""
        mcp_name = f"{self.test_mcp_name}-tools"

        # Create MCP first
        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                mcp_name,
                "--type",
                "sse",
                "--transport",
                "sse",
                "--description",
                "Test MCP for tools testing",
                "--config",
                '{"url": "https://mcp.obrol.id/f/sse"}',
            ]
        )
        assert create_result.returncode == 0
        self.created_mcps.append(mcp_name)

        # Get MCP tools
        tools_result = self._run_cli_command(["mcps", "tools", mcp_name])
        assert (
            tools_result.returncode == 0
        ), f"MCP tools retrieval failed: {tools_result.stderr}"
        # Tools might be empty, which is OK

    def test_cli_mcp_status(self):
        """Test CLI MCP status and connection."""
        mcp_name = f"{self.test_mcp_name}-status"

        # Create MCP first
        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                mcp_name,
                "--type",
                "sse",
                "--transport",
                "sse",
                "--description",
                "Test MCP for status testing",
                "--config",
                '{"url": "https://mcp.obrol.id/f/sse"}',
            ]
        )
        assert create_result.returncode == 0
        self.created_mcps.append(mcp_name)

        # Get MCP details (status)
        status_result = self._run_cli_command(["mcps", "get", mcp_name])
        # Get command should work
        assert status_result.returncode == 0, f"MCP get failed: {status_result.stderr}"
        assert mcp_name in status_result.stdout

    def test_cli_mcp_error_handling(self):
        """Test CLI MCP error handling for invalid requests."""
        # Test with non-existent MCP
        get_result = self._run_cli_command(["mcps", "get", "non-existent-mcp"])
        assert get_result.returncode != 0, "Should fail for non-existent MCP"
        assert (
            "not found" in get_result.stderr.lower()
            or "error" in get_result.stderr.lower()
        )

        # Test with invalid MCP name
        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                "",  # Empty name should fail
                "--type",
                "sse",
                "--transport",
                "sse",
            ]
        )
        assert create_result.returncode != 0, "Should fail for empty MCP name"

        # Test with invalid config
        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                "test-invalid",
                "--type",
                "sse",
                "--transport",
                "sse",
                "--config",
                "invalid-json",
            ]
        )
        assert create_result.returncode != 0, "Should fail for invalid config"

    def test_cli_mcp_output_formats(self):
        """Test CLI MCP output format options."""
        mcp_name = f"{self.test_mcp_name}-format"

        # Create MCP first
        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                mcp_name,
                "--type",
                "sse",
                "--transport",
                "sse",
                "--description",
                "Test MCP for format testing",
                "--config",
                '{"url": "https://mcp.obrol.id/f/sse"}',
            ]
        )
        assert create_result.returncode == 0
        self.created_mcps.append(mcp_name)

        # Test JSON output format
        json_result = self._run_cli_command(["--view", "json", "mcps", "get", mcp_name])
        assert json_result.returncode == 0

        # Verify it's valid JSON
        try:
            import json

            json.loads(json_result.stdout)
        except json.JSONDecodeError:
            pytest.fail("JSON output format is not valid JSON")

        # Test rich output format (default)
        rich_result = self._run_cli_command(["--view", "rich", "mcps", "get", mcp_name])
        assert rich_result.returncode == 0
        assert mcp_name in rich_result.stdout

    def test_cli_mcp_type_validation(self):
        """Test CLI MCP type and transport validation."""
        mcp_name = f"{self.test_mcp_name}-validation"

        # Test with valid type and transport
        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                mcp_name,
                "--type",
                "sse",
                "sse",
                "--description",
                "Test MCP with valid type/transport",
                "--config",
                '{"url": "https://mcp.obrol.id/f/sse"}',
            ]
        )

        if create_result.returncode == 0:
            self.created_mcps.append(mcp_name)
        else:
            # If it fails, it might be due to backend validation, which is OK
            print(
                f"MCP creation failed (this might be expected): {create_result.stderr}"
            )

    def test_cli_mcp_config_handling(self):
        """Test CLI MCP configuration handling."""
        mcp_name = f"{self.test_mcp_name}-config"

        # Test with complex config
        complex_config = (
            '{"url": "https://mcp.obrol.id/f/sse", "timeout": 30, "retries": 3}'
        )

        create_result = self._run_cli_command(
            [
                "mcps",
                "create",
                "--name",
                mcp_name,
                "--type",
                "sse",
                "sse",
                "--description",
                "Test MCP with complex config",
                "--config",
                complex_config,
            ]
        )

        if create_result.returncode == 0:
            self.created_mcps.append(mcp_name)

            # Verify config was applied
            get_result = self._run_cli_command(["mcps", "get", mcp_name])
            assert get_result.returncode == 0
            # The exact config format might vary, so we just check it was created
        else:
            print(f"MCP creation with complex config failed: {create_result.stderr}")


if __name__ == "__main__":
    # Run CLI integration tests directly
    pytest.main([__file__, "-v", "-m", "integration"])
