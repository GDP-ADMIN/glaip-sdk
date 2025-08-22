#!/usr/bin/env python3
"""Streaming execution demonstration.

This example shows how the SDK naturally streams responses from the backend.
Streaming is enabled by default - no special methods needed!

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import sys
from datetime import datetime

from glaip_sdk import Client


def demonstrate_natural_streaming(client, agent_id: str):
    """Demonstrate how streaming works naturally in the SDK."""
    print("🌊 Demonstrating natural streaming behavior...")

    # The SDK automatically streams responses - no special methods needed!
    print("💡 Streaming is enabled by default in the SDK")
    print("💡 The renderer shows real-time streaming output")

    # Test with a simple query that should stream naturally
    simple_query = "Explain the concept of artificial intelligence in simple terms"
    print(f"\n🤖 Running simple query: {simple_query}")

    start_time = datetime.now()
    print(f"🚀 Started at: {start_time.strftime('%H:%M:%S')}")

    # This will automatically stream - the renderer handles it!
    response = client.get_agent(agent_id).run(simple_query)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"✅ Completed in: {duration:.2f}s")
    print(f"📝 Response length: {len(response)} characters")
    print(f"📊 Streaming speed: {len(response) / duration:.1f} chars/sec")

    return response


def demonstrate_streaming_with_tools(client, agent_id: str):
    """Demonstrate streaming with tool usage."""
    print("\n🛠️ Demonstrating streaming with tool usage...")

    tool_query = "What is the current time? Please use your available tools."
    print(f"🤖 Running tool query: {tool_query}")

    start_time = datetime.now()
    print(f"🚀 Started at: {start_time.strftime('%H:%M:%S')}")

    # This will stream and show tool execution in real-time
    response = client.get_agent(agent_id).run(tool_query)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"✅ Completed in: {duration:.2f}s")
    print(f"📝 Response length: {len(response)} characters")

    return response


def demonstrate_streaming_benefits():
    """Explain the benefits of the natural streaming approach."""
    print("\n💡 STREAMING BENEFITS:")
    print("✅ No special methods needed - streaming is automatic")
    print("✅ Real-time feedback as the agent thinks and responds")
    print("✅ Tool execution is visible in real-time")
    print("✅ Better user experience with immediate feedback")
    print("✅ Handles long responses gracefully")
    print("✅ Works with all agent operations")


def main():
    """Demonstrate natural streaming behavior."""
    print("🌊 Natural Streaming Execution Example")
    print("=" * 50)

    try:
        # Initialize client
        print("🔌 Initializing SDK client...")
        client = Client()
        print(f"✅ Connected to: {client.api_url}")

        # Create a simple agent for testing
        print("\n🤖 Creating test agent...")
        agent = client.create_agent(
            name="streaming-demo-agent",
            instruction="You are a helpful assistant that can use tools and provide detailed explanations.",
            tools=[],  # No tools for basic streaming demo
        )
        print(f"✅ Agent created: {agent.name} (ID: {agent.id})")

        try:
            # Demonstrate natural streaming
            demonstrate_natural_streaming(client, agent.id)

            # Show streaming benefits
            demonstrate_streaming_benefits()

            print("\n🎉 Streaming demonstration completed successfully!")
            print(
                "💡 The SDK automatically streams all responses - no configuration needed!"
            )

        finally:
            # Cleanup
            print("\n🧹 Cleaning up...")
            agent.delete()
            print("✅ Agent deleted successfully")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("  - Make sure backend services are running")
        print("  - Verify your API credentials in .env file")
        print("  - Check that the backend supports streaming")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
