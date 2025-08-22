#!/usr/bin/env python3
"""Conversation Memory Example - Demonstrating session persistence and memory management.

This example shows how to work with conversation memory, including:
- Session ID management for persistent conversations
- Memory truncation and management
- Validation of recalled facts
- Memory cleanup and optimization

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import sys
import uuid
from typing import Any

from glaip_sdk import Client


def create_memory_agent(client: Client, name: str, instruction: str) -> Any:
    """Create an agent with memory capabilities."""
    return client.create_agent(
        name=name,
        instruction=instruction,
        model="gpt-4o-mini",  # Use a model that supports memory
    )


def run_conversation_with_memory(
    agent, session_id: str, messages: list[str]
) -> list[dict]:
    """Run a conversation and build chat history."""
    print(f"\n🔄 Running conversation with session: {session_id}")

    chat_history = []

    for i, message in enumerate(messages, 1):
        print(f"\n💬 Message {i}: {message}")

        # Run agent with current chat history
        response = agent.run(message, session_id=session_id, chat_history=chat_history)

        # Add user message and agent response to chat history
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": response})

        print(f"🤖 Response {i}: {response[:100]}...")

    return chat_history


def validate_memory_recall(
    agent, session_id: str, question: str, expected_facts: list[str]
) -> bool:
    """Test if agent can recall information from chat history."""
    print("\n🧠 Testing memory recall...")
    print(f"Question: {question}")

    # Get the full chat history for this session
    # Note: In a real implementation, you'd retrieve this from your session storage
    # For this example, we'll simulate it by building the history from our conversation

    # Run the agent with the question
    response = agent.run(question, session_id=session_id)
    print(f"Response: {response}")

    # Check if expected facts are mentioned
    missed_facts = []
    for fact in expected_facts:
        if fact.lower() not in response.lower():
            missed_facts.append(fact)

    if missed_facts:
        for fact in missed_facts:
            print(f"❌ Missed: {fact}")
        print(
            f"📊 Memory Recall Rate: {((len(expected_facts) - len(missed_facts)) / len(expected_facts) * 100):.1f}% ({len(expected_facts) - len(missed_facts)}/{len(expected_facts)})"
        )
        return False
    else:
        print(
            f"📊 Memory Recall Rate: 100.0% ({len(expected_facts)}/{len(expected_facts)})"
        )
        return True


def demonstrate_memory_truncation(agent, session_id: str):
    """Demonstrate how chat history can be managed for long conversations."""
    print("\n📏 Demonstrating memory truncation...")
    print("Running 20 messages to test memory limits...")

    # Build a long conversation to demonstrate memory management
    long_messages = [
        f"This is message number {i} in a long conversation about various topics."
        for i in range(1, 21)
    ]

    chat_history = []

    for i, message in enumerate(long_messages, 1):
        print(f"\n💬 Message {i}: {message}")

        # Run agent with current chat history
        response = agent.run(message, session_id=session_id, chat_history=chat_history)

        # Add to chat history
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": response})

        print(f"🤖 Response {i}: {response[:100]}...")

    # Test memory recall for early and recent messages
    print("\n🔍 Testing memory recall after long conversation...")

    # Test early message recall
    early_response = agent.run(
        "What was the first message about?",
        session_id=session_id,
        chat_history=chat_history[
            -10:
        ],  # Only keep last 10 messages for memory management
    )
    print(f"🔍 Early message recall: {early_response[:100]}...")

    # Test recent message recall
    recent_response = agent.run(
        "What was the last message about?",
        session_id=session_id,
        chat_history=chat_history[
            -10:
        ],  # Only keep last 10 messages for memory management
    )
    print(f"🔍 Recent message recall: {recent_response[:100]}...")

    # Check if memory truncation is working
    if "message number 1" not in early_response.lower():
        print("⚠️  Early memory may have been truncated")
    if "message number 20" in recent_response.lower():
        print("✅ Recent memory retention working")
    else:
        print("❌ Recent memory not working as expected")


def main() -> bool:
    """Main function demonstrating conversation memory patterns."""
    print("🧠 Conversation Memory Example")
    print("=" * 50)

    # Environment variables are loaded automatically by the Client

    try:
        # Initialize the client
        print("🔌 Initializing SDK client...")
        client = Client()
        print(f"✅ Connected to: {client.api_url}")

        # Create a memory-enabled agent
        print("\n🤖 Creating memory-enabled agent...")
        agent = create_memory_agent(
            client,
            name="memory-demo-agent",
            instruction="""You are a helpful assistant with excellent memory.
            Remember details from our conversation and use them to provide contextually relevant responses.
            When asked about previous topics, refer back to what we discussed earlier.""",
        )
        print(f"✅ Agent created: {agent.name} (ID: {agent.id})")

        # Generate a unique session ID for this conversation
        session_id = str(uuid.uuid4())
        print(f"🆔 Session ID: {session_id}")

        # Run a structured conversation to build memory
        print("\n💬 Building conversation memory...")
        conversation_messages = [
            "My name is Alice and I'm a software engineer.",
            "I work at a company called TechCorp.",
            "My favorite programming language is Python.",
            "I'm working on a project involving AI agents.",
            "The project deadline is next Friday.",
        ]

        run_conversation_with_memory(agent, session_id, conversation_messages)

        # Test memory recall
        print("\n🧠 Testing memory recall...")
        test_question = "Tell me everything you know about me and my project."
        expected_facts = [
            "Alice",
            "software engineer",
            "TechCorp",
            "Python",
            "AI agents",
            "next Friday",
        ]

        memory_success = validate_memory_recall(
            agent, session_id, test_question, expected_facts
        )

        # Demonstrate memory truncation
        demonstrate_memory_truncation(agent, session_id)

        # Test cross-session memory isolation
        print("\n🔒 Testing session isolation...")
        new_session_id = str(uuid.uuid4())

        # Test with empty chat history for new session
        isolation_response = agent.run(
            "What do you know about me?",
            session_id=new_session_id,
            chat_history=[],  # Empty chat history for new session
        )

        if "Alice" not in isolation_response and "TechCorp" not in isolation_response:
            print("✅ Session isolation working - new session has no memory")
        else:
            print("⚠️  Session isolation may not be working properly")

        # Cleanup
        print("\n🧹 Cleaning up...")
        agent.delete()
        print("✅ Agent deleted successfully")

        print("\n🎉 Memory example completed successfully!")
        print(f"📊 Memory recall test: {'PASSED' if memory_success else 'FAILED'}")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("  - Make sure backend services are running (docker-compose up)")
        print("  - Verify your API credentials in .env file")
        print("  - Check that the backend supports memory features")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
