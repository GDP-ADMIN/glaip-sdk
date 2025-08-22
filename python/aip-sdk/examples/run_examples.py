#!/usr/bin/env python3
"""
AI Agent Platform Examples Runner

This script lists all available examples and can optionally run SDK examples.
Use it to discover examples and verify they work correctly.

Usage:
    poetry run python run_examples.py                    # List all examples
    poetry run python run_examples.py --list            # List all examples (same as above)
    poetry run python run_examples.py --run-sdk         # Run all SDK examples
    poetry run python run_examples.py --run-sdk --dry-run  # Test imports without execution
    poetry run python run_examples.py --category getting-started  # List examples by category
    poetry run python run_examples.py --help            # Show this help message

Examples are organized by complexity and interface type:
- getting-started: Basic examples for beginners
- intermediate: Moderate complexity examples
- advanced: Complex scenarios for experienced users
- demos: Complete workflow demonstrations
"""

import argparse
import importlib.util
import os
import sys
from pathlib import Path


class ExampleRunner:
    """Manages and runs AI Agent Platform examples."""

    def __init__(self, examples_root: Path):
        self.examples_root = examples_root
        self.categories = ["getting-started", "intermediate", "advanced", "demos"]
        self.interfaces = ["sdk", "cli"]

    def discover_examples(self) -> dict[str, dict[str, list[Path]]]:
        """Discover all examples organized by category and interface."""
        examples = {}

        for category in self.categories:
            examples[category] = {"sdk": [], "cli": []}
            category_path = self.examples_root / category

            if not category_path.exists():
                continue

            for interface in self.interfaces:
                interface_path = category_path / interface
                if interface_path.exists():
                    # Find Python files for SDK, Markdown for CLI
                    if interface == "sdk":
                        files = [
                            f
                            for f in interface_path.glob("*.py")
                            if f.name != "__init__.py"
                        ]
                    else:  # cli
                        files = [
                            f
                            for f in interface_path.glob("*.md")
                            if f.name != "__init__.py"
                        ]

                    # Sort by filename (numerical order)
                    files.sort(key=lambda x: x.name)
                    examples[category][interface] = files

        return examples

    def list_examples(self, category_filter: str | None = None) -> None:
        """List all examples, optionally filtered by category."""
        examples = self.discover_examples()

        print("🚀 AI Agent Platform Examples")
        print("=" * 50)

        if category_filter and category_filter not in examples:
            print(f"❌ Category '{category_filter}' not found")
            return

        categories_to_show = [category_filter] if category_filter else self.categories

        for category in categories_to_show:
            if category not in examples:
                continue

            print(f"\n📁 {category.replace('-', ' ').title()}")
            print("-" * 30)

            for interface in self.interfaces:
                files = examples[category][interface]
                if not files:
                    continue

                interface_name = "Python SDK" if interface == "sdk" else "CLI"
                print(f"\n  🔧 {interface_name}:")

                for file_path in files:
                    # Extract example info from file
                    example_info = self.get_example_info(file_path, interface)
                    complexity = example_info.get("complexity", "UNKNOWN")
                    description = example_info.get("description", "No description")

                    print(f"    • {file_path.name} [{complexity}] - {description}")

    def get_example_info(self, file_path: Path, interface: str) -> dict[str, str]:
        """Extract example information from file headers."""
        info = {"complexity": "UNKNOWN", "description": "No description"}

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Look for complexity indicator in first few lines
            for line in lines[:10]:
                if "[BASIC]" in line:
                    info["complexity"] = "BASIC"
                    break
                elif "[INTERMEDIATE]" in line:
                    info["complexity"] = "INTERMEDIATE"
                    break
                elif "[ADVANCED]" in line:
                    info["complexity"] = "ADVANCED"
                    break
                elif "[DEMO]" in line:
                    info["complexity"] = "DEMO"
                    break

            # Look for description in docstring or comments
            for line in lines[:20]:
                if "description:" in line.lower() or "description =" in line:
                    desc = line.split(":", 1)[-1].strip()
                    if desc:
                        info["description"] = desc
                        break

        except Exception:
            pass

        return info

    def run_sdk_examples(self, dry_run: bool = False) -> None:
        """Run all SDK examples that have a main() function."""
        examples = self.discover_examples()

        print("🚀 Running SDK Examples")
        print("=" * 50)

        if dry_run:
            print("🧪 DRY RUN MODE - Testing imports only")

        total_examples = 0
        successful_examples = 0
        failed_examples = 0

        for category in self.categories:
            sdk_files = examples[category]["sdk"]
            if not sdk_files:
                continue

            print(f"\n📁 {category.replace('-', ' ').title()}")
            print("-" * 30)

            for file_path in sdk_files:
                total_examples += 1
                print(f"\n🔧 Testing: {file_path.name}")

                try:
                    if dry_run:
                        # Just test import
                        spec = importlib.util.spec_from_file_location(
                            file_path.stem, file_path
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        if hasattr(module, "main"):
                            print("  ✅ Import successful, main() function found")
                            successful_examples += 1
                        else:
                            print("  ⚠️  Import successful, but no main() function")
                            failed_examples += 1
                    else:
                        # Actually run the example
                        print("  🚀 Running example...")

                        # Change to examples directory for relative imports
                        original_cwd = os.getcwd()
                        os.chdir(self.examples_root)

                        try:
                            spec = importlib.util.spec_from_file_location(
                                file_path.stem, file_path
                            )
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)

                            if hasattr(module, "main"):
                                result = module.main()
                                if result:
                                    print("  ✅ Example completed successfully")
                                    successful_examples += 1
                                else:
                                    print("  ❌ Example failed")
                                    failed_examples += 1
                            else:
                                print("  ⚠️  No main() function found")
                                failed_examples += 1

                        finally:
                            os.chdir(original_cwd)

                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    failed_examples += 1

        # Summary
        print("\n📊 Summary")
        print("=" * 30)
        print(f"Total examples: {total_examples}")
        print(f"Successful: {successful_examples}")
        print(f"Failed: {failed_examples}")

        if failed_examples > 0:
            sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Agent Platform Examples Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
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

    args = parser.parse_args()

    # Default to list if no action specified
    if not args.list and not args.run_sdk:
        args.list = True

    # Initialize runner
    examples_root = Path(__file__).parent
    runner = ExampleRunner(examples_root)

    # Execute requested action
    if args.list:
        runner.list_examples(args.category)

    if args.run_sdk:
        runner.run_sdk_examples(args.dry_run)


if __name__ == "__main__":
    main()
