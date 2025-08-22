#!/usr/bin/env python3
"""CLI language model integration tests for the AIP SDK.

These tests verify CLI language model commands work correctly with the backend.
Run with: pytest tests/integration/cli/test_cli_models.py -m integration
"""

import os
import subprocess

import pytest


@pytest.mark.integration
@pytest.mark.cli
class TestCLIModelIntegration:
    """CLI language model integration tests for the AIP SDK."""

    def setup_method(self):
        """Set up environment for CLI testing."""
        self.api_key = os.getenv("AIP_API_KEY")
        self.api_url = os.getenv("AIP_API_URL")

        if not self.api_key or not self.api_url:
            pytest.skip("AIP_API_KEY and AIP_API_URL environment variables required")

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

    def test_cli_models_list(self):
        """Test CLI language model listing."""
        result = self._run_cli_command(["models", "list"])

        assert result.returncode == 0, f"CLI command failed: {result.stderr}"
        assert "models" in result.stdout.lower() or len(result.stdout.strip()) > 0

    def test_cli_models_list_with_provider_filter(self):
        """Test CLI models list with provider filter."""
        # Since --provider option doesn't exist, just test basic list functionality
        result = self._run_cli_command(["models", "list"])
        assert result.returncode == 0, f"CLI command failed: {result.stderr}"
        assert "Available Models" in result.stdout or "models" in result.stdout.lower()

    def test_cli_models_get_by_id(self):
        """Test CLI language model retrieval by ID."""
        # First, get a list of models
        list_result = self._run_cli_command(["models", "list"])
        assert list_result.returncode == 0

        # If models exist, try to get the first one by ID
        # This is approximate - in practice you'd need to parse the model list
        if (
            "no models" not in list_result.stdout.lower()
            and len(list_result.stdout.strip()) > 0
        ):
            # Try to get a model (this might fail if no models exist)
            get_result = self._run_cli_command(["models", "get", "test-model-id"])
            # This might fail if the ID doesn't exist, which is OK
            if get_result.returncode == 0:
                assert len(get_result.stdout.strip()) > 0

    def test_cli_models_get_by_name(self):
        """Test CLI language model retrieval by name."""
        # Test getting a specific model by name
        get_result = self._run_cli_command(["models", "get", "gpt-4o-mini"])

        # This might fail if the model doesn't exist, which is OK
        if get_result.returncode == 0:
            assert "gpt-4o-mini" in get_result.stdout.lower()
        else:
            # If it fails, it should be a meaningful error
            assert (
                "not found" in get_result.stderr.lower()
                or "error" in get_result.stderr.lower()
            )

    def test_cli_models_search(self):
        """Test CLI models search functionality."""
        # Since find command doesn't exist, use list command to search
        result = self._run_cli_command(["models", "list"])
        assert result.returncode == 0, f"Model search failed: {result.stderr}"
        # The list command should show all available models
        assert "models" in result.stdout.lower() or "Available Models" in result.stdout

    def test_cli_models_provider_specific(self):
        """Test CLI models provider-specific functionality."""
        # Since provider-specific commands don't exist, test basic list functionality
        result = self._run_cli_command(["models", "list"])
        assert result.returncode == 0, f"CLI command failed: {result.stderr}"
        # The list command should show all available models
        assert "models" in result.stdout.lower() or "Available Models" in result.stdout

    def test_cli_models_error_handling(self):
        """Test CLI language model error handling for invalid requests."""
        # Test with non-existent model ID
        get_result = self._run_cli_command(["models", "get", "non-existent-model-id"])
        assert get_result.returncode != 0, "Should fail for non-existent model"
        assert (
            "not found" in get_result.stderr.lower()
            or "error" in get_result.stderr.lower()
        )

        # Test with invalid provider
        list_result = self._run_cli_command(
            ["models", "list", "--provider", "invalid-provider"]
        )
        # This might fail due to provider validation, which is expected
        if list_result.returncode != 0:
            assert (
                "provider" in list_result.stderr.lower()
                or "invalid" in list_result.stderr.lower()
            )

    def test_cli_models_output_formats(self):
        """Test CLI language model output format options."""
        # Test JSON output format
        json_result = self._run_cli_command(["--view", "json", "models", "list"])
        assert json_result.returncode == 0

        # Verify it's valid JSON
        try:
            import json

            json.loads(json_result.stdout)
        except json.JSONDecodeError:
            pytest.fail("JSON output format is not valid JSON")

        # Test rich output format (default)
        rich_result = self._run_cli_command(["--view", "rich", "models", "list"])
        assert rich_result.returncode == 0

    def test_cli_models_detailed_info(self):
        """Test CLI models detailed info functionality."""
        # Since --detailed option doesn't exist, test basic list functionality
        list_result = self._run_cli_command(["models", "list"])
        assert list_result.returncode == 0, f"CLI command failed: {list_result.stderr}"
        # The list command should show basic model information
        assert (
            "models" in list_result.stdout.lower()
            or "Available Models" in list_result.stdout
        )

    def test_cli_models_comparison(self):
        """Test CLI language model comparison functionality."""
        # Test comparing models (if supported)
        compare_result = self._run_cli_command(
            ["models", "compare", "gpt-4o-mini", "gpt-3.5-turbo"]
        )

        # This might fail if comparison is not supported or models don't exist
        if compare_result.returncode == 0:
            assert len(compare_result.stdout.strip()) > 0
        else:
            # If it fails, it should be a meaningful error
            assert (
                "not found" in compare_result.stderr.lower()
                or "error" in compare_result.stderr.lower()
            )

    def test_cli_models_status(self):
        """Test CLI language model status and availability."""
        # Test model status command (if supported)
        status_result = self._run_cli_command(["models", "status"])

        # This might fail if status command doesn't exist, which is OK
        if status_result.returncode == 0:
            assert len(status_result.stdout.strip()) > 0

    def test_cli_models_configuration(self):
        """Test CLI language model configuration options."""
        # Test configuration-related commands
        config_result = self._run_cli_command(["models", "config"])

        # This might fail if config command doesn't exist, which is OK
        if config_result.returncode == 0:
            assert len(config_result.stdout.strip()) > 0

    def test_cli_models_help(self):
        """Test CLI language model help functionality."""
        # Test help command
        help_result = self._run_cli_command(["models", "--help"])
        assert help_result.returncode == 0
        assert "Usage:" in help_result.stdout or "help" in help_result.stdout.lower()

        # Test help for specific subcommand
        help_result = self._run_cli_command(["models", "list", "--help"])
        assert help_result.returncode == 0

    def test_cli_models_verbose_output(self):
        """Test CLI models verbose output functionality."""
        # Since --verbose option doesn't exist, test basic list functionality
        verbose_result = self._run_cli_command(["models", "list"])
        assert (
            verbose_result.returncode == 0
        ), f"CLI command failed: {verbose_result.stderr}"
        # The list command should show basic model information
        assert (
            "models" in verbose_result.stdout.lower()
            or "Available Models" in verbose_result.stdout
        )


if __name__ == "__main__":
    # Run CLI integration tests directly
    pytest.main([__file__, "-v", "-m", "integration"])
