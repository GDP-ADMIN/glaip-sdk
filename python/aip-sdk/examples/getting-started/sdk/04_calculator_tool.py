#!/usr/bin/env python3
"""04_calculator_tool.py - Calculator Tool Example

Goal: Create and use a calculator tool with the AIP SDK

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from _utils import (
    cleanup_temp_file,
    create_calculator_tool_script,
    generate_unique_name,
)

from glaip_sdk import Client

client = Client()
temp_script_path = create_calculator_tool_script()

try:
    tool = client.create_tool(
        name=generate_unique_name("calculator-tool"),
        file_path=str(temp_script_path),
        framework="langchain",
        tool_type="custom",
        description="A simple calculator for basic math operations",
    )

    agent = client.create_agent(
        name="calculator-agent",
        instruction="You are a helpful AI assistant with access to a calculator tool. Use the calculator for math problems.",
        tools=[tool],
        timeout=300,
    )

    agent.run("What is 15 + 27?")
    agent.run("Calculate 8 × 6")
    agent.run("What is 100 ÷ 4?")

    agent.delete()
    tool.delete()

finally:
    cleanup_temp_file(temp_script_path)
