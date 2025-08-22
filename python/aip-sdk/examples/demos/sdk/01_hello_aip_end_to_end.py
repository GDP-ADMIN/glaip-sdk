#!/usr/bin/env python3
"""01_hello_aip_end_to_end.py - Complete AIP Workflow Demo

Goal: Demonstrate a complete end-to-end workflow using the AI Agent Platform
Estimated time: 10-15 minutes
Prerequisites: Backend services running, valid API credentials
Run: poetry run python examples/demos/sdk/01_hello_aip_end_to_end.py
Cleanup: Automatic cleanup of all created resources

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import sys
from pathlib import Path

# Add the parent directory to sys.path to import shared utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples._shared import (
    fail,
    h1,
    h2,
    info,
    load_env,
    ok,
    print_run_info,
    register_cleanup,
    step,
)
from glaip_sdk import Client


def main() -> bool:
    """Main function demonstrating complete AIP workflow."""
    try:
        h1("AI Agent Platform - End-to-End Demo")
        print_run_info()

        # Step 1: Environment Setup
        h2("Environment Setup")
        step("Loading environment variables...")
        load_env()
        ok("Environment loaded successfully")

        # Step 2: Client Initialization
        h2("Client Initialization")
        step("Creating AIP client...")
        client = Client()
        ok("Client created successfully")

        # Step 3: Tool Creation
        h2("Tool Creation")
        step("Creating a simple greeting tool...")

        tool_code = '''
def greet_user(name: str, time_of_day: str = "day") -> str:
    """Greet a user with a personalized message."""
    return f"Good {time_of_day}, {name}! Welcome to the AI Agent Platform."
'''

        tool = client.create_tool(
            name="greeting_tool",
            description="Simple greeting tool for demo purposes",
            code=tool_code,
        )
        ok(f"Tool created: {tool.name} (ID: {tool.id})")

        # Register cleanup for tool
        register_cleanup(lambda: client.delete_tool(tool.id), f"delete_tool_{tool.id}")

        # Step 4: Agent Creation
        h2("Agent Creation")
        step("Creating an agent with the greeting tool...")

        agent = client.create_agent(
            name="demo_agent",
            instructions=(
                "You are a helpful AI assistant for demonstrating the AI Agent Platform. "
                "You have access to a greeting tool that you should use when appropriate. "
                "Always be friendly and informative."
            ),
            tools=[tool],  # Use tool object directly instead of ID
        )
        ok(f"Agent created: {agent.name} (ID: {agent.id})")

        # Register cleanup for agent
        register_cleanup(
            lambda: client.delete_agent(agent.id), f"delete_agent_{agent.id}"
        )

        # Step 5: Agent Execution
        h2("Agent Execution")
        step("Running the agent with a simple query...")

        agent.run("Hello! Can you introduce yourself and greet me?")
        ok("Agent executed successfully")

        # Step 6: Tool Integration Test
        h2("Tool Integration Test")
        step("Testing agent with tool usage...")

        agent.run("Please greet Raymond using your greeting tool")
        ok("Tool integration test completed")

        # Step 7: Agent Update
        h2("Agent Update")
        step("Updating agent instructions...")

        updated_agent = client.update_agent(
            agent.id,
            instructions=(
                "You are a helpful AI assistant for demonstrating the AI Agent Platform. "
                "You have access to a greeting tool that you should use when appropriate. "
                "Always be friendly, informative, and mention that this is a demo. "
                "Keep responses concise but helpful."
            ),
        )
        ok("Agent updated successfully")
        info(f"Updated instructions: {updated_agent.instructions[:100]}...")

        # Step 8: Final Test
        h2("Final Test")
        step("Running final test with updated agent...")

        agent.run("What can you do and how do you work?")
        ok("Final test completed")

        # Step 9: Summary
        h2("Demo Summary")
        ok("✅ Environment setup completed")
        ok("✅ Client initialized successfully")
        ok("✅ Tool created and integrated")
        ok("✅ Agent created and configured")
        ok("✅ Agent execution tested")
        ok("✅ Tool integration verified")
        ok("✅ Agent update demonstrated")
        ok("✅ Final test completed")

        info("All resources will be automatically cleaned up on exit")

        return True

    except Exception as e:
        fail(f"Demo failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
