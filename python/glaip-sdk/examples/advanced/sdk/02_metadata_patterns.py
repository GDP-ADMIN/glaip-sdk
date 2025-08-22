#!/usr/bin/env python3
"""03_metadata_patterns.py - Metadata and Documentation Patterns Example

---
title: Metadata and Documentation Patterns
level: advanced
interface: sdk
estimated_time: 5m
features: [metadata, documentation, structured_info]
requires: [AIP_API_KEY, AIP_API_URL]
min_sdk: 0.1.0
cost_hint: low
idempotent: true
tags: [documentation, patterns, best_practices]
---

Goal: Demonstrate advanced metadata patterns and structured documentation for examples
Estimated time: 5 minutes
Prerequisites:
  - Backend services running (docker-compose up)
  - Environment variables set in .env file
  - Python dependencies installed (poetry install)

Run: python examples/advanced/sdk/03_metadata_patterns.py
Cleanup: This example demonstrates metadata-driven resource management

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
import sys
from typing import Any

from glaip_sdk import Client


def extract_metadata(docstring: str) -> dict[str, Any]:
    """Extract YAML metadata from docstring."""
    try:
        # Simple YAML-like parsing for demonstration
        lines = docstring.split("\n")
        metadata = {}
        in_metadata = False

        for line in lines:
            line = line.strip()
            if line == "---":
                in_metadata = not in_metadata
                continue
            if in_metadata and ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                # Parse different value types
                if value.startswith("[") and value.endswith("]"):
                    # List
                    value = [item.strip() for item in value[1:-1].split(",")]
                elif value.isdigit():
                    # Integer
                    value = int(value)
                elif value == "true":
                    value = True
                elif value == "false":
                    value = False

                metadata[key] = value

        return metadata
    except Exception as e:
        print(f"Warning: Could not parse metadata: {e}")
        return {}


def main():
    """Main function demonstrating metadata patterns."""
    print("🚀 Metadata and Documentation Patterns Example")
    print("=" * 55)
    print()

    try:
        # Extract metadata from this file's docstring
        current_docstring = main.__doc__
        metadata = extract_metadata(current_docstring)

        print("📋 Extracted Metadata:")
        print(json.dumps(metadata, indent=2))
        print()

        # Demonstrate metadata-driven behavior
        if metadata.get("level") == "advanced":
            print("🔍 This is an advanced example - showing detailed information")

        if "agents" in metadata.get("features", []):
            print("🤖 Agent features detected in metadata")

        if metadata.get("cost_hint") == "low":
            print("💰 Low cost operation - safe to run multiple times")

        if metadata.get("idempotent"):
            print("🔄 Idempotent operation - can be run multiple times safely")

        # Initialize client
        client = Client()
        print(f"\n✅ Connected to: {client.api_url}")

        # Create a simple agent to demonstrate the pattern
        agent_name = "metadata-demo-agent"
        print(f"\n🤖 Creating agent: {agent_name}")

        agent = client.create_agent(
            name=agent_name,
            instruction="You are a helpful AI assistant. Explain metadata patterns.",
            model="gpt-4.1",
        )
        print(f"✅ Agent created: {agent.name}")

        # Use metadata to inform agent behavior
        if metadata.get("estimated_time"):
            print(f"⏱️  Expected completion time: {metadata['estimated_time']}")

        # Cleanup
        agent.delete()
        print("✅ Agent deleted successfully")

        print("\n🎉 Example completed successfully!")
        print("\n💡 Key Benefits of Metadata Patterns:")
        print("  - Machine-readable documentation")
        print("  - Automated example categorization")
        print("  - CI/CD integration support")
        print("  - Documentation generation")
        print("  - Feature discovery and filtering")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
