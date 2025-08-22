#!/usr/bin/env python3
"""02_resource_management.py - Advanced Resource Management Example

Goal: Demonstrate advanced resource management patterns including unique naming,
      automatic cleanup, and error handling
Estimated time: 4-5 minutes
Prerequisites:
  - Backend services running (docker-compose up)
  - Environment variables set in .env file
  - Python dependencies installed (poetry install)

Run: python examples/advanced/sdk/02_resource_management.py
Cleanup: This example demonstrates automatic cleanup via atexit handlers

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import atexit
import os
import sys
import uuid

from glaip_sdk import Client


def register_cleanup(client, *resources):
    """Register cleanup function to ensure resources are deleted on exit."""

    def _cleanup():
        for resource in resources:
            try:
                if hasattr(resource, "delete"):
                    resource.delete()
                    print(
                        f"🧹 Cleaned up: {resource.name if hasattr(resource, 'name') else resource}"
                    )
            except Exception as e:
                print(f"⚠️  Cleanup warning: {e}")

    atexit.register(_cleanup)


def main():
    """Main function demonstrating advanced resource management."""
    print("🚀 Advanced Resource Management Example")
    print("=" * 50)
    print()

    # Generate unique run ID for resource naming
    RUN_ID = os.getenv("EXAMPLES_RUN_ID", str(uuid.uuid4())[:8])
    print(f"🔑 Using run ID: {RUN_ID}")

    try:
        # Initialize the client
        client = Client()
        print(f"✅ Connected to: {client.api_url}")

        # Create multiple resources with unique names
        agent_name = f"demo-agent-{RUN_ID}"
        tool_name = f"demo-tool-{RUN_ID}"

        print(f"\n🤖 Creating agent: {agent_name}")
        agent = client.create_agent(
            name=agent_name,
            instruction="You are a helpful AI assistant. Keep responses concise.",
            model="gpt-4.1",
            timeout=300,
        )
        print(f"✅ Agent created: {agent.name} (ID: {agent.id})")

        print(f"\n🔧 Creating tool: {tool_name}")
        # Create a simple tool (this would be your actual tool creation logic)
        tool = client.create_tool(
            name=tool_name,
            description="A demonstration tool for resource management",
            # Add other tool parameters as needed
        )
        print(f"✅ Tool created: {tool.name} (ID: {tool.id})")

        # Register cleanup for both resources
        register_cleanup(client, agent, tool)
        print(
            "\n🔒 Cleanup handlers registered - resources will be deleted automatically"
        )

        # Demonstrate resource usage
        print(f"\n💬 Testing agent: {agent.name}")
        response = agent.run("Hello! What's your name?")
        print(f"🤖 Response: {response}")

        # Show that cleanup is automatic
        print("\n📋 Resources created in this session:")
        print(f"  - Agent: {agent.name} ({agent.id})")
        print(f"  - Tool: {tool.name} ({tool.id})")
        print("\n💡 These will be automatically cleaned up when the script exits")

        print("\n🎉 Example completed successfully!")
        print("💭 Check the console output when the script exits to see cleanup")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    # The atexit handlers will run automatically here
    sys.exit(0 if success else 1)
