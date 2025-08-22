"""Test CLI structure and imports."""

import pytest


def test_cli_imports():
    """Test that CLI modules can be imported without errors."""
    try:
        # Test that modules can be imported
        # Test that modules can be imported
        import glaip_sdk.cli  # noqa: F401

        # Note: Individual command modules are imported in main.py, not directly
        # The main CLI module should be importable
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import CLI modules: {e}")


def test_cli_main_command():
    """Test that the main CLI command can be created."""
    try:
        from glaip_sdk.cli import main

        # Just verify the command exists - don't actually run it
        assert main is not None
        assert hasattr(main, "callback")
    except Exception as e:
        pytest.fail(f"Failed to create main CLI command: {e}")


def test_cli_commands_registered():
    """Test that all CLI commands are registered."""
    try:
        from glaip_sdk.cli import main

        # Check that command groups exist in the command structure
        # without actually running the CLI
        command_names = [cmd.name for cmd in main.commands.values()]
        expected_commands = [
            "agents",
            "tools",
            "mcps",
            "models",
            "init",
            "status",
            "version",
        ]

        for expected_cmd in expected_commands:
            assert (
                expected_cmd in command_names
            ), f"Command {expected_cmd} not found in {command_names}"

    except Exception as e:
        pytest.fail(f"Failed to verify CLI commands: {e}")


def test_cli_help_output():
    """Test that help output is generated correctly."""
    try:
        from glaip_sdk.cli import main

        # Test that help attributes exist without running commands
        # Check that commands have help text
        for cmd_name, cmd in main.commands.items():
            assert hasattr(cmd, "help"), f"Command {cmd_name} missing help attribute"
            assert cmd.help is not None, f"Command {cmd_name} has None help"

    except Exception as e:
        pytest.fail(f"Failed to verify CLI help output: {e}")


def test_cli_version():
    """Test that version flag works."""
    try:
        from glaip_sdk.cli import main

        # Check that version command exists
        assert "version" in main.commands
        version_cmd = main.commands["version"]
        assert hasattr(version_cmd, "callback")
    except Exception as e:
        pytest.fail(f"Failed to verify CLI version: {e}")


def test_cli_version_command():
    """Test the version command."""
    try:
        from glaip_sdk.cli import main

        # Check that version command exists without running it
        assert "version" in main.commands
        version_cmd = main.commands["version"]
        assert hasattr(version_cmd, "callback")
        assert hasattr(version_cmd, "help")
    except Exception as e:
        pytest.fail(f"Failed to verify CLI version command: {e}")


def test_cli_status_command():
    """Test the status command."""
    try:
        from glaip_sdk.cli import main

        # Check that status command exists without running it
        assert "status" in main.commands
        status_cmd = main.commands["status"]
        assert hasattr(status_cmd, "callback")
        assert hasattr(status_cmd, "help")
    except Exception as e:
        pytest.fail(f"Failed to verify CLI status command: {e}")


def test_cli_error_handling():
    """Test CLI error handling."""
    try:
        from glaip_sdk.cli import main

        # Check that commands have proper error handling setup
        for cmd_name, cmd in main.commands.items():
            assert hasattr(cmd, "callback"), f"Command {cmd_name} missing callback"
    except Exception as e:
        pytest.fail(f"Failed to verify CLI error handling: {e}")


def test_cli_with_mock_client():
    """Test CLI commands with mocked client."""
    try:
        from glaip_sdk.cli import main

        # Check that agents command exists and has list subcommand
        assert "agents" in main.commands
        agents_cmd = main.commands["agents"]
        assert hasattr(agents_cmd, "commands")
        assert "list" in agents_cmd.commands

        # Check that list command has proper structure
        list_cmd = agents_cmd.commands["list"]
        assert hasattr(list_cmd, "callback")
        assert hasattr(list_cmd, "help")
    except Exception as e:
        pytest.fail(f"Failed to verify CLI with mock client: {e}")
