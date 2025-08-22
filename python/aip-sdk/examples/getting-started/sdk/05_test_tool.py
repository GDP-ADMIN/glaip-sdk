#!/usr/bin/env python3
"""05_test_tool.py - Tool Plugin Structure Template

Goal: Demonstrate the correct tool plugin structure required for CLI tool creation

Note: This file is a template showing the required structure for CLI tool creation.
      It cannot be run directly as a Python script due to missing dependencies.
      Use it as a reference when creating tools for the CLI.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

# This is a template showing the required structure for CLI tool creation
# The gllm_plugin module is only available in the backend environment

"""
from gllm_plugin.tools import tool_plugin
from langchain_core.tools import BaseTool

@tool_plugin(version="1.0.0")
class HelloWorldTool(BaseTool):
    # A simple tool that demonstrates the required plugin structure for CLI tool creation

    name: str = "hello_world"
    description: str = "A simple tool that says hello to users"

    def _run(self, name: str = "World") -> str:
        # Say hello to someone

        Args:
            name: The name to greet (default: "World")

        Returns:
            A friendly greeting message

        return f"Hello, {name}! Welcome to the AI Agent Platform!"
"""

print(
    "This is a template file showing the required tool plugin structure for CLI tool creation."
)
print("It cannot be run directly as a Python script.")
print("Use it as a reference when creating tools for the CLI.")
print("\nRequired structure:")
print("- Use @tool_plugin decorator")
print("- Inherit from BaseTool")
print("- Define name and description as class attributes")
print("- Implement _run method")
