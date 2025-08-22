#!/usr/bin/env python3
"""02_hello_world_tool.py - Hello World Tool Example

Goal: Create and use a simple custom tool with the AIP SDK

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from _utils import cleanup_temp_file, create_hello_tool_script, generate_unique_name

from glaip_sdk import Client

client = Client()
temp_script_path = create_hello_tool_script()

try:
    tool = client.create_tool(
        name=generate_unique_name("hello-world-tool"),
        file_path=str(temp_script_path),
        framework="langchain",
        tool_type="custom",
        description="A simple tool that says hello to users",
    )

    agent = client.create_agent(
        name="hello-agent",
        instruction="You are a friendly AI assistant. Use the hello world tool to greet users.",
        tools=[tool],
        timeout=300,
    )

    agent.run("Please greet me using your hello world tool!")
    agent.run("Use your tool to say hello to Alice!")

    agent.delete()
    tool.delete()

finally:
    cleanup_temp_file(temp_script_path)
