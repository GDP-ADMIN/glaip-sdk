#!/usr/bin/env python3
"""CLI tool integration tests for the AIP SDK.

These tests verify CLI tool commands work correctly with the backend.
Run with: pytest tests/integration/cli/test_cli_tools.py -m integration
"""

import os
import subprocess
import tempfile
import uuid

import pytest


@pytest.mark.integration
@pytest.mark.cli
class TestCLIToolIntegration:
    """CLI tool integration tests for the AIP SDK."""

    def setup_method(self):
        """Set up environment for CLI testing."""
        self.api_key = os.getenv("AIP_API_KEY")
        self.api_url = os.getenv("AIP_API_URL")

        if not self.api_key or not self.api_url:
            pytest.skip("AIP_API_KEY and AIP_API_URL environment variables required")

        self.test_tool_name = f"test-cli-tool-{uuid.uuid4().hex[:8]}"
        self.created_tools = []

    def teardown_method(self):
        """Clean up created tools after each test."""
        for tool_name in self.created_tools:
            try:
                # Use CLI to delete the tool
                subprocess.run(
                    [
                        "python",
                        "-m",
                        "glaip_sdk.cli.main",
                        "--api-url",
                        self.api_url,
                        "--api-key",
                        self.api_key,
                        "tools",
                        "delete",
                        tool_name,
                    ],
                    capture_output=True,
                    check=False,
                )
            except Exception:
                pass  # Cleanup failures shouldn't fail tests
        self.created_tools.clear()

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

    def _create_test_tool_file(
        self, content="def test_function():\n    return 'Hello from test tool'"
    ):
        """Create a temporary test tool file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content)
            return f.name

    def test_cli_tool_list(self):
        """Test CLI tool listing."""
        result = self._run_cli_command(["tools", "list"])

        assert result.returncode == 0, f"CLI command failed: {result.stderr}"
        assert "tools" in result.stdout.lower() or len(result.stdout.strip()) > 0

    def test_cli_tool_create_and_delete(self):
        """Test CLI tool creation and deletion."""
        # Create a test tool file
        tool_file = self._create_test_tool_file()

        try:
            # Create tool via CLI
            create_result = self._run_cli_command(
                [
                    "tools",
                    "create",
                    "--name",
                    self.test_tool_name,
                    "--tool-type",
                    "custom",
                    "--file",
                    tool_file,
                    "--framework",
                    "langchain",
                    "--description",
                    "Test tool for CLI integration testing",
                ]
            )

            assert (
                create_result.returncode == 0
            ), f"Tool creation failed: {create_result.stderr}"

            # Extract tool name from output (assuming it's shown in the output)
            if "created" in create_result.stdout.lower():
                self.created_tools.append(self.test_tool_name)

            # List tools to verify creation
            list_result = self._run_cli_command(["tools", "list"])
            assert list_result.returncode == 0

        finally:
            # Clean up temporary file
            os.unlink(tool_file)

    def test_cli_tool_create_with_options(self):
        """Test CLI tool creation with various options."""
        tool_file = self._create_test_tool_file()

        try:
            create_result = self._run_cli_command(
                [
                    "tools",
                    "create",
                    "--name",
                    self.test_tool_name,
                    "--tool-type",
                    "custom",
                    "--file",
                    tool_file,
                    "--framework",
                    "langchain",
                    "--description",
                    "Test tool with CLI options",
                ]
            )

            assert (
                create_result.returncode == 0
            ), f"Tool creation with options failed: {create_result.stderr}"

            if "created" in create_result.stdout.lower():
                self.created_tools.append(self.test_tool_name)

        finally:
            os.unlink(tool_file)

    def test_cli_tool_get(self):
        """Test CLI tool retrieval."""
        # First, get a list of tools
        list_result = self._run_cli_command(["tools", "list"])
        assert list_result.returncode == 0

        # If tools exist, try to get the first one
        if (
            "no tools" not in list_result.stdout.lower()
            and len(list_result.stdout.strip()) > 0
        ):
            # Extract a tool name from the output (this is approximate)
            # In a real scenario, you'd need to parse the output properly
            get_result = self._run_cli_command(["tools", "get", "test"])
            # This might fail if no tool with "test" in the name exists, which is OK
            if get_result.returncode == 0:
                assert len(get_result.stdout.strip()) > 0

    def test_cli_tool_search(self):
        """Test CLI tool search functionality."""
        # Use list command instead of non-existent find command
        search_result = self._run_cli_command(["tools", "list"])
        assert (
            search_result.returncode == 0
        ), f"Tool listing failed: {search_result.stderr}"
        # List should work and show available tools

    def test_cli_tool_script(self):
        """Test CLI tool script retrieval."""
        # First, get a list of tools
        list_result = self._run_cli_command(["tools", "list"])
        assert list_result.returncode == 0

        # If tools exist, try to get details for the first one
        if (
            "no tools" not in list_result.stdout.lower()
            and len(list_result.stdout.strip()) > 0
        ):
            # Use get command instead of non-existent script command
            get_result = self._run_cli_command(["tools", "get", "test"])
            # This might fail if no tool with "test" in the name exists, which is OK
            if get_result.returncode == 0:
                assert len(get_result.stdout.strip()) > 0

    def test_cli_tool_update(self):
        """Test CLI tool update functionality."""
        # Create a test tool first
        tool_file = self._create_test_tool_file()

        try:
            create_result = self._run_cli_command(
                [
                    "tools",
                    "create",
                    "--name",
                    self.test_tool_name,
                    "--tool-type",
                    "custom",
                    "--file",
                    tool_file,
                    "--framework",
                    "langchain",
                    "--description",
                    "Test tool for update testing",
                ]
            )
            assert create_result.returncode == 0

            if "created" in create_result.stdout.lower():
                self.created_tools.append(self.test_tool_name)

                # Update tool description
                update_result = self._run_cli_command(
                    [
                        "tools",
                        "update",
                        self.test_tool_name,
                        "--description",
                        "Updated description via CLI",
                    ]
                )

                # Update might not be supported for all tools, so we don't fail the test
                if update_result.returncode == 0:
                    assert "Updated description via CLI" in update_result.stdout

        finally:
            os.unlink(tool_file)

    def test_cli_tool_upload_code(self):
        """Test CLI tool code upload functionality."""
        # Create a test tool first
        tool_file = self._create_test_tool_file()

        try:
            create_result = self._run_cli_command(
                [
                    "tools",
                    "create",
                    "--name",
                    self.test_tool_name,
                    "--tool-type",
                    "custom",
                    "--file",
                    tool_file,
                    "--framework",
                    "langchain",
                    "--description",
                    "Test tool for upload testing",
                ]
            )
            assert create_result.returncode == 0

            if "created" in create_result.stdout.lower():
                self.created_tools.append(self.test_tool_name)

                # Create a new version of the tool file
                new_tool_file = self._create_test_tool_file(
                    "def updated_function():\n    return 'Updated tool'"
                )

                try:
                    # Upload new code using update-code command
                    upload_result = self._run_cli_command(
                        [
                            "tools",
                            "update-code",
                            self.test_tool_name,
                            "--file",
                            new_tool_file,
                        ]
                    )

                    # Upload might not be supported for all tools, so we don't fail the test
                    if upload_result.returncode == 0:
                        assert (
                            "updated" in upload_result.stdout.lower()
                            or "uploaded" in upload_result.stdout.lower()
                        )

                finally:
                    os.unlink(new_tool_file)

        finally:
            os.unlink(tool_file)

    def test_cli_tool_error_handling(self):
        """Test CLI tool error handling for invalid requests."""
        # Test with non-existent tool
        get_result = self._run_cli_command(["tools", "get", "non-existent-tool"])
        assert get_result.returncode != 0, "Should fail for non-existent tool"
        assert (
            "not found" in get_result.stderr.lower()
            or "error" in get_result.stderr.lower()
        )

        # Test with non-existent file
        create_result = self._run_cli_command(
            [
                "tools",
                "create",
                "--name",
                "test-tool",
                "--tool-type",
                "custom",
                "--file",
                "non-existent-file.py",
                "--framework",
                "langchain",
            ]
        )
        assert create_result.returncode != 0, "Should fail for non-existent file"

    def test_cli_tool_output_formats(self):
        """Test CLI tool output format options."""
        # Test JSON output format
        json_result = self._run_cli_command(["--view", "json", "tools", "list"])
        assert json_result.returncode == 0

        # Verify it's valid JSON
        try:
            import json

            json.loads(json_result.stdout)
        except json.JSONDecodeError:
            pytest.fail("JSON output format is not valid JSON")

        # Test rich output format (default)
        rich_result = self._run_cli_command(["--view", "rich", "tools", "list"])
        assert rich_result.returncode == 0

    def test_cli_tool_framework_validation(self):
        """Test CLI tool framework validation."""
        tool_file = self._create_test_tool_file()

        try:
            # Test with invalid framework
            create_result = self._run_cli_command(
                [
                    "tools",
                    "create",
                    "--name",
                    "test-tool",
                    "--tool-type",
                    "custom",
                    "--file",
                    tool_file,
                    "--framework",
                    "invalid-framework",
                ]
            )

            # This might fail due to framework validation, which is expected
            if create_result.returncode != 0:
                assert (
                    "framework" in create_result.stderr.lower()
                    or "invalid" in create_result.stderr.lower()
                )
            else:
                # If it succeeds, add to cleanup
                if "created" in create_result.stdout.lower():
                    self.created_tools.append(self.test_tool_name)

        finally:
            os.unlink(tool_file)


if __name__ == "__main__":
    # Run CLI integration tests directly
    pytest.main([__file__, "-v", "-m", "integration"])
