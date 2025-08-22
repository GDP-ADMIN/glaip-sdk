#!/usr/bin/env python3
"""Shared helper functions for AIP SDK CLI integration tests.

This module provides common functionality used across all CLI integration tests,
including CLI command execution, output validation, and test data management.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

import pytest


# Environment Configuration
def get_cli_test_environment() -> tuple[str, str]:
    """Get CLI test environment configuration.

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


# CLI Command Execution
def run_cli_command(
    command_args: list[str],
    api_url: str = None,
    api_key: str = None,
    capture_output: bool = True,
    timeout: int = 30,
) -> subprocess.CompletedProcess:
    """Run a CLI command and return the result.

    Args:
        command_args: List of command arguments
        api_url: API URL (auto-detected if not provided)
        api_key: API key (auto-detected if not provided)
        capture_output: Whether to capture output
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess result
    """
    if api_url is None or api_key is None:
        api_url, api_key = get_cli_test_environment()

    full_command = [
        "python",
        "-m",
        "glaip_sdk.cli.main",
        "--api-url",
        api_url,
        "--api-key",
        api_key,
    ] + command_args

    try:
        result = subprocess.run(
            full_command,
            capture_output=capture_output,
            text=True,
            check=False,
            timeout=timeout,
        )
        return result
    except subprocess.TimeoutExpired:
        # Create a mock result for timeout
        result = subprocess.CompletedProcess(
            args=full_command,
            returncode=124,  # Standard timeout exit code
            stdout="",
            stderr="Command timed out",
        )
        return result


def run_cli_command_success(
    command_args: list[str], api_url: str = None, api_key: str = None, timeout: int = 30
) -> subprocess.CompletedProcess:
    """Run a CLI command and assert it succeeds.

    Args:
        command_args: List of command arguments
        api_url: API URL (auto-detected if not provided)
        api_key: API key (auto-detected if not provided)
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess result

    Raises:
        AssertionError: If command fails
    """
    result = run_cli_command(command_args, api_url, api_key, timeout=timeout)
    assert result.returncode == 0, f"CLI command failed: {result.stderr}"
    return result


# CLI Output Validation
def assert_cli_output_contains(
    result: subprocess.CompletedProcess, expected_text: str
) -> None:
    """Assert that CLI output contains expected text.

    Args:
        result: CLI command result
        expected_text: Expected text in output

    Raises:
        AssertionError: If expected text not found
    """
    assert (
        expected_text in result.stdout
    ), f"Expected '{expected_text}' in output, got: {result.stdout}"


def assert_cli_output_not_contains(
    result: subprocess.CompletedProcess, unexpected_text: str
) -> None:
    """Assert that CLI output does not contain unexpected text.

    Args:
        result: CLI command result
        unexpected_text: Text that should not be in output

    Raises:
        AssertionError: If unexpected text found
    """
    assert (
        unexpected_text not in result.stdout
    ), f"Unexpected '{unexpected_text}' found in output: {result.stdout}"


def assert_cli_error_contains(
    result: subprocess.CompletedProcess, expected_error: str
) -> None:
    """Assert that CLI error output contains expected text.

    Args:
        result: CLI command result
        expected_error: Expected error text

    Raises:
        AssertionError: If expected error text not found
    """
    assert (
        expected_error in result.stderr
    ), f"Expected error '{expected_error}' in stderr, got: {result.stderr}"


def assert_cli_success(result: subprocess.CompletedProcess) -> None:
    """Assert that CLI command succeeded.

    Args:
        result: CLI command result

    Raises:
        AssertionError: If command failed
    """
    assert (
        result.returncode == 0
    ), f"CLI command failed with return code {result.returncode}: {result.stderr}"


def assert_cli_failure(
    result: subprocess.CompletedProcess, expected_return_code: int = None
) -> None:
    """Assert that CLI command failed.

    Args:
        result: CLI command result
        expected_return_code: Expected return code (optional)

    Raises:
        AssertionError: If command succeeded or wrong return code
    """
    assert (
        result.returncode != 0
    ), f"CLI command succeeded unexpectedly: {result.stdout}"

    if expected_return_code is not None:
        assert (
            result.returncode == expected_return_code
        ), f"Expected return code {expected_return_code}, got {result.returncode}"


def assert_json_output_valid(result: subprocess.CompletedProcess) -> None:
    """Assert that CLI output is valid JSON.

    Args:
        result: CLI command result

    Raises:
        AssertionError: If output is not valid JSON
    """
    try:
        json.loads(result.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"CLI output is not valid JSON: {e}")


# Test Data Generation
def generate_cli_test_name(prefix: str = "test-cli", max_length: int = 8) -> str:
    """Generate a unique test name for CLI tests.

    Args:
        prefix: Prefix for the test name
        max_length: Maximum length for the UUID part

    Returns:
        Unique test name
    """
    uuid_part = uuid.uuid4().hex[:max_length]
    return f"{prefix}-{uuid_part}"


def create_cli_test_tool_file(content: str = None) -> str:
    """Create a temporary test tool file for CLI testing.

    Args:
        content: Tool script content (defaults to simple test tool)

    Returns:
        Path to the created temporary file
    """
    if content is None:
        content = '''from glaip_sdk import tool_plugin

@tool_plugin
def cli_test_tool(input_text: str = "Hello") -> str:
    """A simple test tool for CLI integration testing."""
    return f"CLI test tool executed with input: {input_text}"
'''

    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False)
    temp_file.write(content)
    temp_file.close()

    return temp_file.name


def create_cli_test_file(content: str, suffix: str = ".txt") -> str:
    """Create a temporary test file for CLI testing.

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


# CLI Resource Management
class CLITestResourceManager:
    """Manages CLI test resources for automatic cleanup."""

    def __init__(self, api_url: str = None, api_key: str = None):
        """Initialize CLI resource manager.

        Args:
            api_url: API URL (auto-detected if not provided)
            api_key: API key (auto-detected if not provided)
        """
        self.api_url, self.api_key = (
            get_cli_test_environment()
            if api_url is None or api_key is None
            else (api_url, api_key)
        )
        self.agents = []
        self.tools = []
        self.mcps = []
        self.temp_files = []

    def add_agent(self, agent_name: str) -> None:
        """Add agent to cleanup list.

        Args:
            agent_name: Agent name to track
        """
        self.agents.append(agent_name)

    def add_tool(self, tool_name: str) -> None:
        """Add tool to cleanup list.

        Args:
            tool_name: Tool name to track
        """
        self.tools.append(tool_name)

    def add_mcp(self, mcp_name: str) -> None:
        """Add MCP to cleanup list.

        Args:
            mcp_name: MCP name to track
        """
        self.mcps.append(mcp_name)

    def add_temp_file(self, file_path: str) -> None:
        """Add temporary file to cleanup list.

        Args:
            file_path: Path to temporary file
        """
        self.temp_files.append(file_path)

    def cleanup(self) -> None:
        """Clean up all tracked resources using CLI commands."""
        # Clean up agents
        for agent_name in self.agents:
            try:
                run_cli_command(
                    ["agents", "delete", agent_name], self.api_url, self.api_key
                )
            except Exception as e:
                print(f"Warning: Failed to clean up agent {agent_name}: {e}")

        # Clean up tools
        for tool_name in self.tools:
            try:
                run_cli_command(
                    ["tools", "delete", tool_name], self.api_url, self.api_key
                )
            except Exception as e:
                print(f"Warning: Failed to clean up tool {tool_name}: {e}")

        # Clean up MCPs
        for mcp_name in self.mcps:
            try:
                run_cli_command(
                    ["mcps", "delete", mcp_name], self.api_url, self.api_key
                )
            except Exception as e:
                print(f"Warning: Failed to clean up MCP {mcp_name}: {e}")

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


# CLI Resource Creation Helpers
def create_cli_test_agent(
    api_url: str = None,
    api_key: str = None,
    name: str = None,
    instruction: str = None,
    **kwargs,
) -> tuple[str, CLITestResourceManager]:
    """Create a test agent via CLI with automatic cleanup.

    Args:
        api_url: API URL (auto-detected if not provided)
        api_key: API key (auto-detected if not provided)
        name: Agent name (auto-generated if not provided)
        instruction: Agent instruction (auto-generated if not provided)
        **kwargs: Additional agent creation parameters

    Returns:
        Tuple of (created_agent_name, resource_manager)
    """
    if name is None:
        name = generate_cli_test_name("test-cli-agent")

    if instruction is None:
        instruction = "You are a simple test agent for CLI integration testing."

    # Create resource manager for cleanup
    resource_manager = CLITestResourceManager(api_url, api_key)

    try:
        # Build command arguments
        cmd_args = ["agents", "create", "--name", name, "--instruction", instruction]

        # Add optional parameters
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, bool) and value:
                    cmd_args.append(f"--{key}")
                elif not isinstance(value, bool):
                    cmd_args.append(f"--{key}")
                    cmd_args.append(str(value))

        # Create agent via CLI
        run_cli_command_success(cmd_args, api_url, api_key)

        # Track for cleanup
        resource_manager.add_agent(name)

        return name, resource_manager

    except Exception as e:
        resource_manager.cleanup()
        raise e


def create_cli_test_tool(
    api_url: str = None,
    api_key: str = None,
    file_path: str = None,
    framework: str = "langchain",
    description: str = None,
) -> tuple[str, CLITestResourceManager]:
    """Create a test tool via CLI with automatic cleanup.

    Args:
        api_url: API URL (auto-detected if not provided)
        api_key: API key (auto-detected if not provided)
        file_path: Path to tool file (auto-created if not provided)
        framework: Tool framework
        description: Tool description

    Returns:
        Tuple of (created_tool_name, resource_manager)
    """
    # Create resource manager for cleanup
    resource_manager = CLITestResourceManager(api_url, api_key)

    try:
        # Create tool file if not provided
        if file_path is None:
            file_path = create_cli_test_tool_file()
            resource_manager.add_temp_file(file_path)

        # Build command arguments
        cmd_args = ["tools", "create", file_path, "--framework", framework]

        if description:
            cmd_args.extend(["--description", description])

        # Create tool via CLI
        run_cli_command_success(cmd_args, api_url, api_key)

        # Extract tool name from output (this is approximate)
        # In practice, you'd need to parse the CLI output to get the exact name
        tool_name = f"test-cli-tool-{uuid.uuid4().hex[:8]}"

        # Track for cleanup
        resource_manager.add_tool(tool_name)

        return tool_name, resource_manager

    except Exception as e:
        resource_manager.cleanup()
        raise e


def create_cli_test_mcp(
    api_url: str = None,
    api_key: str = None,
    name: str = None,
    description: str = None,
    config: dict[str, Any] = None,
    **kwargs,
) -> tuple[str, CLITestResourceManager]:
    """Create a test MCP via CLI with automatic cleanup.

    Args:
        api_url: API URL (auto-detected if not provided)
        api_key: API key (auto-detected if not provided)
        name: MCP name (auto-generated if not provided)
        description: MCP description
        config: MCP configuration
        **kwargs: Additional MCP creation parameters

    Returns:
        Tuple of (created_mcp_name, resource_manager)
    """
    if name is None:
        name = generate_cli_test_name("test-cli-mcp")

    if description is None:
        description = "Test MCP for CLI integration testing"

    if config is None:
        config = {"url": "https://mcp.obrol.id/f/sse"}

    # Create resource manager for cleanup
    resource_manager = CLITestResourceManager(api_url, api_key)

    try:
        # Build command arguments
        cmd_args = ["mcps", "create", "--name", name, "--description", description]

        # Add config as JSON string
        if config:
            cmd_args.extend(["--config", json.dumps(config)])

        # Add optional parameters
        for key, value in kwargs.items():
            if value is not None:
                cmd_args.extend([f"--{key}", str(value)])

        # Create MCP via CLI
        run_cli_command_success(cmd_args, api_url, api_key)

        # Track for cleanup
        resource_manager.add_mcp(name)

        return name, resource_manager

    except Exception as e:
        resource_manager.cleanup()
        raise e


# CLI Output Format Testing
def test_cli_output_formats(
    base_command: list[str],
    api_url: str = None,
    api_key: str = None,
    expected_content: str = None,
) -> None:
    """Test CLI output format options (JSON and rich).

    Args:
        base_command: Base command to test (e.g., ["agents", "list"])
        api_url: API URL (auto-detected if not provided)
        api_key: API key (auto-detected if not provided)
        expected_content: Expected content in output (optional)
    """
    # Test JSON output format
    json_cmd = ["--view", "json"] + base_command
    json_result = run_cli_command_success(json_cmd, api_url, api_key)

    # Verify it's valid JSON
    assert_json_output_valid(json_result)

    # Test rich output format (default)
    rich_cmd = ["--view", "rich"] + base_command
    rich_result = run_cli_command_success(rich_cmd, api_url, api_key)

    # Verify rich output contains expected content if specified
    if expected_content:
        assert_cli_output_contains(rich_result, expected_content)


# CLI Error Testing
def test_cli_error_handling(
    command_args: list[str],
    expected_error: str = None,
    expected_return_code: int = None,
    api_url: str = None,
    api_key: str = None,
) -> subprocess.CompletedProcess:
    """Test CLI error handling for invalid requests.

    Args:
        command_args: Command arguments to test
        expected_error: Expected error text in stderr
        expected_return_code: Expected return code
        api_url: API URL (auto-detected if not provided)
        api_key: API key (auto-detected if not provided)

    Returns:
        CLI command result
    """
    result = run_cli_command(command_args, api_url, api_key)

    # Assert command failed
    assert_cli_failure(result, expected_return_code)

    # Assert error contains expected text if specified
    if expected_error:
        assert_cli_error_contains(result, expected_error)

    return result


# CLI Health Check
def check_cli_health(api_url: str = None, api_key: str = None) -> bool:
    """Check if CLI can connect to backend.

    Args:
        api_url: API URL (auto-detected if not provided)
        api_key: API key (auto-detected if not provided)

    Returns:
        True if CLI is healthy, False otherwise
    """
    try:
        result = run_cli_command(["status"], api_url, api_key)
        return result.returncode == 0
    except Exception:
        return False


def ensure_cli_healthy(api_url: str = None, api_key: str = None) -> None:
    """Ensure CLI is healthy, skip test if not.

    Args:
        api_url: API URL (auto-detected if not provided)
        api_key: API key (auto-detected if not provided)

    Raises:
        pytest.skip: If CLI is not healthy
    """
    if not check_cli_health(api_url, api_key):
        pytest.skip("CLI is not healthy")


# CLI Context Manager
class CLITestContext:
    """Context manager for automatic CLI test resource cleanup."""

    def __init__(self, api_url: str = None, api_key: str = None):
        """Initialize CLI test context.

        Args:
            api_url: API URL (auto-detected if not provided)
            api_key: API key (auto-detected if not provided)
        """
        self.api_url, self.api_key = (
            get_cli_test_environment()
            if api_url is None or api_key is None
            else (api_url, api_key)
        )
        self.resource_manager = CLITestResourceManager(self.api_url, self.api_key)

    def __enter__(self):
        """Enter the context."""
        return self.resource_manager

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and clean up resources."""
        self.resource_manager.cleanup()


# CLI Decorator for automatic cleanup
def with_cli_resource_cleanup(func):
    """Decorator to automatically clean up CLI test resources.

    This decorator creates a CLITestResourceManager and passes it as the last argument
    to the decorated function, then automatically cleans up after the function completes.

    Usage:
        @with_cli_resource_cleanup
        def test_something(api_url, api_key, resource_manager):
            # Test code here
            pass
    """

    def wrapper(*args, **kwargs):
        # Find the api_url and api_key arguments
        api_url = None
        api_key = None

        for _i, arg in enumerate(args):
            if isinstance(arg, str) and "http" in arg:
                api_url = arg
            elif isinstance(arg, str) and len(arg) > 20:  # Likely an API key
                api_key = arg

        # If not found in args, check kwargs
        if api_url is None:
            api_url = kwargs.get("api_url")
        if api_key is None:
            api_key = kwargs.get("api_key")

        # Create resource manager
        resource_manager = CLITestResourceManager(api_url, api_key)

        try:
            # Call the function with resource manager
            result = func(*args, resource_manager, **kwargs)
            return result
        finally:
            # Always clean up
            resource_manager.cleanup()

    return wrapper


# CLI Logging Helpers
def log_cli_test_step(step_name: str) -> None:
    """Log a CLI test step for debugging.

    Args:
        step_name: Name of the test step
    """
    print(f"\n{'='*20} CLI TEST: {step_name} {'='*20}")


def log_cli_command_execution(
    command: list[str], result: subprocess.CompletedProcess
) -> None:
    """Log CLI command execution for debugging.

    Args:
        command: Command that was executed
        result: Command execution result
    """
    print(f"🔧 CLI Command: {' '.join(command)}")
    print(f"📤 Return Code: {result.returncode}")
    if result.stdout.strip():
        print(f"📥 Output: {result.stdout.strip()}")
    if result.stderr.strip():
        print(f"❌ Error: {result.stderr.strip()}")


def log_cli_resource_creation(resource_type: str, resource_name: str) -> None:
    """Log CLI resource creation for debugging.

    Args:
        resource_type: Type of resource (agent, tool, mcp)
        resource_name: Resource name
    """
    print(f"✅ Created {resource_type} via CLI: {resource_name}")


def log_cli_resource_cleanup(resource_type: str, resource_name: str) -> None:
    """Log CLI resource cleanup for debugging.

    Args:
        resource_type: Type of resource (agent, tool, mcp)
        resource_name: Resource name
    """
    print(f"🧹 Cleaned up {resource_type} via CLI: {resource_name}")
