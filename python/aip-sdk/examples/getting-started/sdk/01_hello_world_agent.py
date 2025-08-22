#!/usr/bin/env python3
"""01_hello_world_agent.py - Hello World Agent Example

Goal: Create and run a simple AI agent using the AIP SDK

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from glaip_sdk import Client

client = Client()
agent = client.create_agent(
    name="hello-world-agent",
    instruction="You are a friendly AI assistant.",
)
agent.run("Hello! How are you today?")
agent.delete()
