#!/usr/bin/env python3
"""Examples module entry point.

This module allows running examples as a package:
    python -m examples --list
    python -m examples --run-sdk
    aip-examples --help
"""

import argparse
import sys
from pathlib import Path

# Add the parent directory to sys.path to import run_examples
sys.path.insert(0, str(Path(__file__).parent.parent))

from examples.run_examples import ExampleRunner


def main():
    """Main entry point for the examples module."""
    parser = argparse.ArgumentParser(
        prog="aip-examples",
        description="AI Agent Platform Examples Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    aip-examples                              # List all examples
    aip-examples --list                       # List all examples
    aip-examples --run-sdk                    # Run all SDK examples
    aip-examples --run-sdk --dry-run          # Test imports only
    aip-examples --category getting-started   # List examples by category

For more information, see: https://github.com/your-org/ai-agent-platform
        """,
    )

    parser.add_argument(
        "--list", action="store_true", help="List all examples (default action)"
    )

    parser.add_argument("--run-sdk", action="store_true", help="Run all SDK examples")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test imports without execution (use with --run-sdk)",
    )

    parser.add_argument(
        "--category",
        choices=["getting-started", "intermediate", "advanced", "demos"],
        help="Filter examples by category",
    )

    parser.add_argument("--version", action="version", version="aip-examples 1.0.0")

    args = parser.parse_args()

    # Default to list if no action specified
    if not args.list and not args.run_sdk:
        args.list = True

    # Initialize runner
    examples_root = Path(__file__).parent
    runner = ExampleRunner(examples_root)

    try:
        # Execute requested action
        if args.list:
            runner.list_examples(args.category)

        if args.run_sdk:
            runner.run_sdk_examples(args.dry_run)

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
