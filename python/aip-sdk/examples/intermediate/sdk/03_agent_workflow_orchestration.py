#!/usr/bin/env python3
"""03_agent_workflow_orchestration.py - Simple Agent Workflow Example

Goal: Demonstrate basic agent workflow patterns with tool integration
Estimated time: 8-10 minutes
Prerequisites: Backend services running, valid API credentials
Run: poetry run python examples/intermediate/sdk/03_agent_workflow_orchestration.py
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
    """Main function demonstrating simple agent workflow patterns."""
    try:
        h1("Simple Agent Workflow Orchestration")
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

        # Step 3: Create Simple Tools
        h2("Tool Creation")
        step("Creating a simple calculation tool...")

        calc_tool_code = '''
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle."""
    return length * width
'''

        calc_tool = client.create_tool(
            name="calculation_tool",
            description="Simple mathematical operations for workflow demonstration",
            code=calc_tool_code,
        )
        ok(f"Calculation tool created: {calc_tool.name} (ID: {calc_tool.id})")

        # Register cleanup for tool
        register_cleanup(
            lambda: client.delete_tool(calc_tool.id), f"delete_calc_tool_{calc_tool.id}"
        )

        # Step 4: Create Specialized Agents
        h2("Agent Creation")
        step("Creating a math specialist agent...")

        math_agent = client.create_agent(
            name="math_specialist",
            instruction=(
                "You are a math specialist agent. You excel at mathematical calculations "
                "and always show your work step by step. Use your calculation tools "
                "when performing math operations."
            ),
            tools=[calc_tool],  # Use tool object directly instead of ID
        )
        ok(f"Math specialist agent created: {math_agent.name} (ID: {math_agent.id})")

        # Register cleanup for math agent
        register_cleanup(
            lambda: client.delete_agent(math_agent.id),
            f"delete_math_agent_{math_agent.id}",
        )

        step("Creating a workflow coordinator agent...")

        coordinator_agent = client.create_agent(
            name="workflow_coordinator",
            instruction=(
                "You are a workflow coordinator. You can delegate mathematical tasks "
                "to the math specialist agent. Always explain your workflow and "
                "coordinate between different agents when needed."
            ),
            agents=[math_agent],  # Use agent object directly instead of ID
        )
        ok(
            f"Workflow coordinator created: {coordinator_agent.name} (ID: {coordinator_agent.id})"
        )

        # Register cleanup for coordinator agent
        register_cleanup(
            lambda: client.delete_agent(coordinator_agent.id),
            f"delete_coordinator_agent_{coordinator_agent.id}",
        )

        # Step 5: Test Basic Workflow
        h2("Basic Workflow Testing")
        step("Testing math specialist with direct calculation...")

        math_agent.run("Please calculate 15 + 27 and show your work")
        ok("Math specialist executed successfully")

        # Step 6: Test Agent Coordination
        h2("Agent Coordination Testing")
        step("Testing workflow coordinator with delegation...")

        coordinator_agent.run(
            "I need to calculate the area of a rectangle that is 8.5 meters long "
            "and 6.2 meters wide. Please coordinate with your math specialist to "
            "get this done and explain the workflow."
        )
        ok("Workflow coordination completed")

        # Step 7: Test Complex Workflow
        h2("Complex Workflow Testing")
        step("Testing multi-step mathematical workflow...")

        coordinator_agent.run(
            "I need to solve this problem: A rectangular garden has a length of 12 meters "
            "and a width of 8 meters. I want to add a path around it that's 1 meter wide. "
            "What's the new total area? Please work through this step by step."
        )
        ok("Complex workflow completed")

        # Step 8: Workflow Summary
        h2("Workflow Summary")
        ok("✅ Environment setup completed")
        ok("✅ Client initialized successfully")
        ok("✅ Calculation tool created and integrated")
        ok("✅ Math specialist agent created")
        ok("✅ Workflow coordinator agent created")
        ok("✅ Basic workflow tested")
        ok("✅ Agent coordination verified")
        ok("✅ Complex workflow executed")

        info("All resources will be automatically cleaned up on exit")
        info("This demonstrates basic agent workflow patterns suitable for MVP")

        return True

    except Exception as e:
        fail(f"Workflow demo failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
