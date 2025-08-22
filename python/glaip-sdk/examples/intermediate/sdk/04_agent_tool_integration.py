#!/usr/bin/env python3
"""04_agent_tool_integration.py - Comprehensive Agent Tool Integration Example

Goal: Demonstrate agent tool integration patterns including native tools, custom tools,
and sub-agent delegation with tools
Estimated time: 10-15 minutes
Prerequisites: Backend services running, valid API credentials
Run: poetry run python examples/intermediate/sdk/04_agent_tool_integration.py
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


def create_custom_weather_tool(client: Client, suffix: str = "") -> str:
    """Create a custom weather tool for testing."""
    weather_tool_code = f"""
from typing import Any
from gllm_plugin.tools import tool_plugin
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class WeatherToolInput(BaseModel):
    location: str = Field(..., description="The city and state, e.g., San Francisco, CA")

@tool_plugin(version="1.0.0")
class WeatherTool(BaseTool):
    name: str = "weather{suffix}"
    description: str = "Useful for when you need to know the weather in a specific location."
    args_schema: type[BaseModel] = WeatherToolInput

    def _run(self, location: str, **kwargs: Any) -> str:
        return f"The weather in {{location}} is sunny with a temperature of 22°C."
"""

    # Use the new create_tool_from_code method which properly uploads tool plugins
    weather_tool = client.create_tool_from_code(
        name=f"custom_weather_tool{suffix}",
        code=weather_tool_code,
    )

    ok(f"Custom weather tool created: {weather_tool.name} (ID: {weather_tool.id})")
    return weather_tool.id


def get_native_tools(client: Client) -> list[str]:
    """Get available native tools for testing."""
    step("Discovering available native tools...")

    try:
        # Get all tools and filter for native ones
        all_tools = client.list_tools()
        native_tools = [tool for tool in all_tools if tool.tool_type == "native"]

        if not native_tools:
            info("No native tools found - this is normal in some environments")
            return []

        # Prioritize time and date tools as they're most reliable
        time_tools = [tool for tool in native_tools if "time" in tool.name.lower()]
        date_tools = [tool for tool in native_tools if "date" in tool.name.lower()]

        selected_tools = []
        if time_tools:
            selected_tools.append(time_tools[0].id)
            ok(f"Selected time tool: {time_tools[0].name}")
        if date_tools:
            selected_tools.append(date_tools[0].id)
            ok(f"Selected date tool: {date_tools[0].name}")

        # Add other simple tools if available
        other_tools = [
            tool for tool in native_tools if tool not in time_tools + date_tools
        ]
        if other_tools and len(selected_tools) < 2:
            selected_tools.append(other_tools[0].id)
            ok(f"Selected additional tool: {other_tools[0].name}")

        return selected_tools

    except Exception as e:
        info(f"Could not discover native tools: {e}")
        return []


def test_native_tools_only(client: Client) -> bool:
    """Test agent with native tools only."""
    h2("Testing Native Tools Only")

    try:
        # Get native tools
        native_tool_ids = get_native_tools(client)
        if not native_tool_ids:
            info("Skipping native tools test - no tools available")
            return True

        # Create agent with native tools
        step("Creating agent with native tools only...")
        native_agent = client.create_agent(
            name="native-tools-agent",
            instruction=(
                "You are a utility assistant with access to native tools. "
                "Use your available tools to answer questions about time, dates, and other utilities. "
                "Always provide clear, formatted answers after using tools."
            ),
            tools=native_tool_ids,
        )
        ok(f"Native tools agent created: {native_agent.name} (ID: {native_agent.id})")

        # Register cleanup
        register_cleanup(
            lambda: client.delete_agent(native_agent.id),
            f"delete_native_agent_{native_agent.id}",
        )

        # Test basic functionality
        step("Testing native tool functionality...")
        response = native_agent.run("What is the current time?")

        if response and len(response) > 10:
            ok("Native tools test successful")
            return True
        else:
            fail("Native tools test failed - insufficient response")
            return False

    except Exception as e:
        fail(f"Native tools test failed: {e}")
        return False


def test_custom_tool_integration(client: Client) -> bool:
    """Test agent with custom tool integration."""
    h2("Testing Custom Tool Integration")

    try:
        # Create custom weather tool
        step("Creating custom weather tool...")
        weather_tool_id = create_custom_weather_tool(client, "_main")

        # Register cleanup
        register_cleanup(
            lambda: client.delete_tool(weather_tool_id),
            f"delete_weather_tool_{weather_tool_id}",
        )

        # Create agent with custom tool
        step("Creating agent with custom weather tool...")
        custom_agent = client.create_agent(
            name="custom-tool-agent",
            instruction=(
                "You are a weather assistant with access to a custom weather tool. "
                "When asked about weather, ALWAYS use your weather tool and provide "
                "ONLY the information from the tool. Do not make up weather information. "
                "CRITICAL: You must use the weather tool for any weather-related questions."
            ),
            tools=[weather_tool_id],
        )
        ok(f"Custom tool agent created: {custom_agent.name} (ID: {custom_agent.id})")

        # Register cleanup
        register_cleanup(
            lambda: client.delete_agent(custom_agent.id),
            f"delete_custom_agent_{custom_agent.id}",
        )

        # Test custom tool functionality
        step("Testing custom weather tool...")

        # Debug: Show tool details
        tool_details = client.get_tool(weather_tool_id)
        info(
            f"Tool details: {tool_details.name}, type: {tool_details.tool_type}, framework: {tool_details.framework}"
        )

        # Debug: Show agent configuration
        agent_details = client.get_agent(custom_agent.id)
        info(f"Agent tools: {agent_details.tools}")

        response = custom_agent.run("What's the weather like in London?")

        # Check if the tool was actually used (should contain the exact tool output)
        if response and "London" in response and "22°C" in response:
            ok("Custom tool integration test successful")
            return True
        else:
            fail(
                f"Custom tool integration test failed - tool not used properly. Response: {response[:200]}..."
            )
            return False

    except Exception as e:
        fail(f"Custom tool integration test failed: {e}")
        return False


def test_sub_agent_with_tools(client: Client) -> bool:
    """Test sub-agent delegation with tools."""
    h2("Testing Sub-Agent Delegation with Tools")

    try:
        # Create custom weather tool
        step("Creating weather tool for sub-agent...")
        weather_tool_id = create_custom_weather_tool(client, "_sub")

        # Register cleanup
        register_cleanup(
            lambda: client.delete_tool(weather_tool_id),
            f"delete_weather_tool_sub_{weather_tool_id}",
        )

        # Get native time tool
        native_tool_ids = get_native_tools(client)
        time_tool_id = None
        if native_tool_ids:
            time_tool_id = native_tool_ids[0]  # Use first available native tool

        # Create weather sub-agent
        step("Creating weather sub-agent...")
        weather_agent = client.create_agent(
            name="weather-sub-agent",
            instruction=(
                "You are a weather expert. Always use your weather tool when asked about weather. "
                "Provide clear, helpful weather information."
            ),
            tools=[weather_tool_id],
        )
        ok(f"Weather sub-agent created: {weather_agent.name} (ID: {weather_agent.id})")

        # Register cleanup
        register_cleanup(
            lambda: client.delete_agent(weather_agent.id),
            f"delete_weather_sub_agent_{weather_agent.id}",
        )

        # Create time sub-agent (if native tools available)
        time_agent = None
        if time_tool_id:
            step("Creating time sub-agent...")
            time_agent = client.create_agent(
                name="time-sub-agent",
                instruction="You are a time expert. Use your time tool to provide current time information.",
                tools=[time_tool_id],
            )
            ok(f"Time sub-agent created: {time_agent.name} (ID: {time_agent.id})")

            # Register cleanup
            register_cleanup(
                lambda: client.delete_agent(time_agent.id),
                f"delete_time_sub_agent_{time_agent.id}",
            )

        # Create master agent with sub-agents
        step("Creating master agent with sub-agents...")
        sub_agents = [weather_agent.id]
        if time_agent:
            sub_agents.append(time_agent.id)

        master_agent = client.create_agent(
            name="master-agent-with-tools",
            instruction=(
                "You are a master agent that delegates tasks to specialized sub-agents. "
                "Delegate weather questions to your weather sub-agent "
                "and time questions to your time sub-agent if available. "
                "Always coordinate effectively between your sub-agents."
            ),
            agents=sub_agents,
        )
        ok(f"Master agent created: {master_agent.name} (ID: {master_agent.id})")

        # Register cleanup
        register_cleanup(
            lambda: client.delete_agent(master_agent.id),
            f"delete_master_agent_{master_agent.id}",
        )

        # Test delegation with tools
        step("Testing sub-agent delegation with tools...")
        if time_agent:
            query = "What is the weather like in Paris and what is the current time?"
        else:
            query = "What is the weather like in Paris?"

        response = master_agent.run(query)

        # Validate response contains weather information
        if (
            response
            and "Paris" in response
            and ("sunny" in response or "22°C" in response)
        ):
            ok("Sub-agent delegation with tools test successful")
            return True
        else:
            fail("Sub-agent delegation with tools test failed")
            return False

    except Exception as e:
        fail(f"Sub-agent with tools test failed: {e}")
        return False


def main() -> bool:
    """Main function demonstrating comprehensive agent tool integration."""
    try:
        h1("Comprehensive Agent Tool Integration")
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

        # Step 3: Test Native Tools Only
        native_tools_success = test_native_tools_only(client)

        # Step 4: Test Custom Tool Integration
        custom_tools_success = test_custom_tool_integration(client)

        # Step 5: Test Sub-Agent Delegation with Tools
        sub_agent_tools_success = test_sub_agent_with_tools(client)

        # Step 6: Overall Assessment
        h2("Overall Assessment")
        passed_tests = sum(
            [native_tools_success, custom_tools_success, sub_agent_tools_success]
        )
        total_tests = 3

        if passed_tests >= 2:  # Pass if at least 2 out of 3 tests succeeded
            ok(f"✅ Overall test successful: {passed_tests}/{total_tests} tests passed")

            if native_tools_success:
                ok("✅ Native tools integration working")
            if custom_tools_success:
                ok("✅ Custom tool integration working")
            if sub_agent_tools_success:
                ok("✅ Sub-agent delegation with tools working")

            info("All resources will be automatically cleaned up on exit")
            info("This demonstrates comprehensive agent tool integration patterns")

            return True
        else:
            fail(
                f"❌ Overall test failed: only {passed_tests}/{total_tests} tests passed"
            )
            return False

    except Exception as e:
        fail(f"Tool integration demo failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
