#!/usr/bin/env python3
"""Error Handling Patterns Example - Demonstrating robust error handling in production applications.

This example shows how to handle common errors and edge cases when working with the AIP SDK:
- Authentication and connection errors
- Validation and resource errors
- Rate limiting and timeout handling
- Graceful degradation and retry logic
- User-friendly error messages

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import sys
import time
from typing import Any

from glaip_sdk import Client
from glaip_sdk.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class RobustAgentManager:
    """Demonstrates robust error handling patterns for agent operations."""

    def __init__(self, client: Client):
        self.client = client
        self.retry_config = {"max_retries": 3, "base_delay": 1.0, "max_delay": 10.0}

    def create_agent_with_retry(
        self, name: str, instruction: str, **kwargs
    ) -> Any | None:
        """Create an agent with retry logic and comprehensive error handling."""
        print(f"🤖 Creating agent: {name}")

        for attempt in range(self.retry_config["max_retries"]):
            try:
                agent = self.client.create_agent(
                    name=name, instruction=instruction, **kwargs
                )
                print(f"✅ Agent created successfully: {agent.name} (ID: {agent.id})")
                return agent

            except AuthenticationError as e:
                print(f"❌ Authentication failed: {e}")
                print("💡 Check your API key and ensure it's valid")
                return None

            except ValidationError as e:
                print(f"❌ Validation error: {e}")
                print("💡 Check your input parameters")
                return None

            except RateLimitError:
                delay = min(
                    self.retry_config["base_delay"] * (2**attempt),
                    self.retry_config["max_delay"],
                )
                print(
                    f"⏳ Rate limited, retrying in {delay}s... (attempt {attempt + 1})"
                )
                time.sleep(delay)
                continue

            except ServerError as e:
                if attempt < self.retry_config["max_retries"] - 1:
                    delay = self.retry_config["base_delay"] * (2**attempt)
                    print(
                        f"🔄 Server error, retrying in {delay}s... (attempt {attempt + 1})"
                    )
                    time.sleep(delay)
                    continue
                else:
                    print(
                        f"❌ Server error after {self.retry_config['max_retries']} attempts: {e}"
                    )
                    return None

            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("💡 This might be a new error type - check the logs")
                return None

        print(
            f"❌ Failed to create agent after {self.retry_config['max_retries']} attempts"
        )
        return None

    def run_agent_safely(self, agent: Any, message: str) -> str | None:
        """Run an agent with comprehensive error handling."""
        print(f"💬 Running agent with message: {message[:50]}...")

        try:
            response = agent.run(message)
            print(f"✅ Agent response: {response[:100]}...")
            return response

        except NotFoundError as e:
            print(f"❌ Agent not found: {e}")
            print("💡 The agent may have been deleted or moved")
            return None

        except RateLimitError as e:
            print(f"⏳ Rate limited: {e}")
            print("💡 Consider implementing exponential backoff")
            return None

        except ServerError as e:
            print(f"🔄 Server error: {e}")
            print("💡 The backend may be experiencing issues")
            return None

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("💡 Log this error for investigation")
            return None

    def cleanup_agent_safely(self, agent: Any) -> bool:
        """Clean up an agent with error handling."""
        print(f"🧹 Cleaning up agent: {agent.name}")

        try:
            agent.delete()
            print(f"✅ Agent {agent.name} deleted successfully")
            return True

        except NotFoundError:
            print(f"⚠️  Agent {agent.name} already deleted")
            return True

        except Exception as e:
            print(f"❌ Failed to delete agent {agent.name}: {e}")
            print("💡 You may need to clean this up manually")
            return False


def demonstrate_connection_errors() -> None:
    """Demonstrate handling connection and authentication errors."""
    print("\n🔌 Demonstrating connection error handling...")

    try:
        # Try to create client with invalid credentials
        client = Client(api_url="http://invalid-url:9999", api_key="invalid-key")

        # This should fail
        client.list_agents()
        print("❌ Expected failure but got success")

    except AuthenticationError as e:
        print(f"✅ Caught authentication error: {e}")

    except Exception as e:
        print(f"✅ Caught connection error: {e}")

    print("💡 Always validate your connection before proceeding")


def demonstrate_validation_errors() -> None:
    """Demonstrate handling validation errors."""
    print("\n✅ Demonstrating validation error handling...")

    try:
        client = Client()

        # Try to create agent with invalid parameters
        client.create_agent(
            name="",  # Empty name should fail
            instruction="Test",
        )
        print("❌ Expected validation failure but got success")

    except ValidationError as e:
        print(f"✅ Caught validation error: {e}")

    except Exception as e:
        print(f"✅ Caught other error: {e}")

    print("💡 Always validate your input parameters")


def demonstrate_graceful_degradation() -> None:
    """Demonstrate graceful degradation when services are unavailable."""
    print("\n🔄 Demonstrating graceful degradation...")

    try:
        client = Client()

        # Try to list agents
        agents = client.list_agents()
        print(f"✅ Backend is healthy, found {len(agents)} agents")

        # Try to create a test agent
        test_agent = client.create_agent(
            name="test-agent-error-handling",
            instruction="This is a test agent for error handling demonstration",
        )

        if test_agent:
            print("✅ Test agent created successfully")

            # Try to run it
            response = (
                test_agent.run_safely("Hello!")
                if hasattr(test_agent, "run_safely")
                else "Test response"
            )
            print(f"✅ Agent response: {response}")

            # Clean up
            test_agent.delete()
            print("✅ Test agent cleaned up")
        else:
            print("⚠️  Could not create test agent, but application continues")

    except Exception as e:
        print(f"❌ Backend error: {e}")
        print("💡 Application can continue with limited functionality")
        print("💡 Consider implementing fallback behavior")


def main() -> bool:
    """Main function demonstrating error handling patterns."""
    print("🛡️  Error Handling Patterns Example")
    print("=" * 50)
    print("This example demonstrates robust error handling patterns")
    print("for production applications using the AIP SDK.")
    print()

    try:
        # Demonstrate various error scenarios
        demonstrate_connection_errors()
        demonstrate_validation_errors()
        demonstrate_graceful_degradation()

        # Test with actual client if available
        print("\n🧪 Testing with actual client...")

        try:
            client = Client()
            print(f"✅ Connected to: {client.api_url}")

            # Create agent manager
            manager = RobustAgentManager(client)

            # Test agent creation with retry logic
            agent = manager.create_agent_with_retry(
                name="error-handling-demo-agent",
                instruction="You are a helpful assistant for demonstrating error handling patterns.",
            )

            if agent:
                # Test safe agent execution
                response = manager.run_agent_safely(
                    agent, "Explain what error handling means in software development"
                )

                if response:
                    print("✅ All error handling patterns demonstrated successfully")
                else:
                    print("⚠️  Agent execution had issues, but error handling worked")

                # Clean up
                manager.cleanup_agent_safely(agent)
            else:
                print("⚠️  Agent creation failed, but error handling worked")

        except Exception as e:
            print(f"❌ Client test failed: {e}")
            print("💡 This demonstrates error handling in action")

        print("\n🎉 Error handling patterns example completed successfully!")
        print("\n💡 Key Takeaways:")
        print("  • Always handle authentication and connection errors")
        print("  • Implement retry logic for transient failures")
        print("  • Provide user-friendly error messages")
        print("  • Implement graceful degradation when possible")
        print("  • Log unexpected errors for investigation")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("  - Make sure backend services are running (docker-compose up)")
        print("  - Verify your API credentials in .env file")
        print("  - Check that the backend supports the required endpoints")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
