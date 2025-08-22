#!/usr/bin/env python3
"""Generate documentation from example headers.

This script parses example files and generates documentation pages
that can be used with MkDocs or Sphinx.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import argparse
import re
import sys
from pathlib import Path


class ExampleDocGenerator:
    """Generate documentation from example files."""

    def __init__(self, examples_root: Path, output_dir: Path):
        self.examples_root = examples_root
        self.output_dir = output_dir
        self.categories = ["getting-started", "intermediate", "advanced", "demos"]
        self.interfaces = ["sdk", "cli"]

    def parse_example_header(self, file_path: Path, interface: str) -> dict[str, str]:
        """Parse example file header for documentation."""
        info = {
            "title": file_path.stem,
            "goal": "No goal specified",
            "time": "No time estimate",
            "prerequisites": [],
            "run_command": "No run command specified",
            "cleanup": "No cleanup specified",
            "authors": [],
            "complexity": "UNKNOWN",
        }

        try:
            content = file_path.read_text(encoding="utf-8")

            if interface == "sdk":
                # Parse Python file docstring
                docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if not docstring_match:
                    return info

                docstring = docstring_match.group(1)
                lines = docstring.split("\n")

                for line in lines:
                    line = line.strip()
                    if line.startswith("Goal:"):
                        info["goal"] = line[5:].strip()
                    elif line.startswith("Estimated time:"):
                        info["time"] = line[15:].strip()
                    elif line.startswith("Prerequisites:"):
                        # Collect all prerequisite lines
                        info["prerequisites"] = []
                        for prereq_line in lines[lines.index(line) + 1 :]:
                            if prereq_line.strip().startswith("-"):
                                info["prerequisites"].append(
                                    prereq_line.strip()[1:].strip()
                                )
                            elif (
                                prereq_line.strip()
                                and not line.strip().startswith("Run:")
                                and not line.strip().startswith("Cleanup:")
                            ):
                                break
                    elif line.startswith("Run:"):
                        info["run_command"] = line[4:].strip()
                    elif line.startswith("Cleanup:"):
                        info["cleanup"] = line[8:].strip()
                    elif line.startswith("Authors:"):
                        # Collect author lines
                        info["authors"] = []
                        for author_line in lines[lines.index(line) + 1 :]:
                            if author_line.strip().startswith("    "):
                                info["authors"].append(author_line.strip())
                            elif line.strip() and not line.strip().startswith("    "):
                                break
            else:
                # Parse CLI Markdown file
                lines = content.split("\n")

                for i, line in enumerate(lines):
                    line = line.strip()
                    if line.startswith("**Goal**:"):
                        info["goal"] = line[8:].strip()
                    elif line.startswith("**Estimated time**:"):
                        info["time"] = line[19:].strip()
                    elif line.startswith("**Prerequisites**:"):
                        # Collect all prerequisite lines
                        info["prerequisites"] = []
                        for prereq_line in lines[i + 1 :]:
                            if prereq_line.strip().startswith("-"):
                                info["prerequisites"].append(
                                    prereq_line.strip()[1:].strip()
                                )
                            elif (
                                prereq_line.strip()
                                and not prereq_line.strip().startswith("**")
                            ):
                                break
                    elif line.startswith("**Run**:"):
                        info["run_command"] = line[7:].strip()
                    elif line.startswith("**Cleanup**:"):
                        info["cleanup"] = line[11:].strip()
                    elif line.startswith("**Authors**:"):
                        # Collect author lines
                        info["authors"] = []
                        for author_line in lines[i + 1 :]:
                            if author_line.strip().startswith("-"):
                                info["authors"].append(author_line.strip()[1:].strip())
                            elif (
                                author_line.strip()
                                and not author_line.strip().startswith("**")
                            ):
                                break

            # Detect complexity from filename or content
            if "[BASIC]" in content:
                info["complexity"] = "BASIC"
            elif "[INTERMEDIATE]" in content:
                info["complexity"] = "INTERMEDIATE"
            elif "[ADVANCED]" in content:
                info["complexity"] = "ADVANCED"
            elif "[DEMO]" in content:
                info["complexity"] = "DEMO"

        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")

        return info

    def generate_markdown_doc(self, examples: dict[str, dict[str, list[Path]]]) -> str:
        """Generate Markdown documentation."""
        md_content = []

        # Header
        md_content.append("# AI Agent Platform Examples")
        md_content.append("")
        md_content.append("This documentation is auto-generated from example files.")
        md_content.append("")

        # Table of Contents
        md_content.append("## Table of Contents")
        md_content.append("")
        for category in self.categories:
            if category in examples:
                md_content.append(
                    f"- [{category.replace('-', ' ').title()}](#{category.replace('-', '-')})"
                )
        md_content.append("")

        # Generate content for each category
        for category in self.categories:
            if category not in examples:
                continue

            # Check if category has any examples
            has_examples = False
            for interface in self.interfaces:
                if examples[category][interface]:
                    has_examples = True
                    break

            if not has_examples:
                continue

            md_content.append(f"## {category.replace('-', ' ').title()}")
            md_content.append("")

            for interface in self.interfaces:
                files = examples[category][interface]
                if not files:
                    continue

                interface_name = "Python SDK" if interface == "sdk" else "CLI"
                md_content.append(f"### {interface_name}")
                md_content.append("")

                for file_path in files:
                    info = self.parse_example_header(file_path, interface)

                    md_content.append(f"#### {info['title']}")
                    md_content.append("")
                    md_content.append(f"**Goal:** {info['goal']}")
                    md_content.append("")
                    md_content.append(f"**Estimated time:** {info['time']}")
                    md_content.append("")
                    md_content.append(f"**Complexity:** {info['complexity']}")
                    md_content.append("")

                    if info["prerequisites"]:
                        md_content.append("**Prerequisites:**")
                        for prereq in info["prerequisites"]:
                            md_content.append(f"- {prereq}")
                        md_content.append("")

                    md_content.append(f"**Run:** `{info['run_command']}`")
                    md_content.append("")
                    md_content.append(f"**Cleanup:** {info['cleanup']}")
                    md_content.append("")

                    if info["authors"]:
                        md_content.append("**Authors:**")
                        for author in info["authors"]:
                            md_content.append(f"- {author}")
                        md_content.append("")

                    md_content.append("---")
                    md_content.append("")

        return "\n".join(md_content)

    def generate_sphinx_doc(self, examples: dict[str, dict[str, list[Path]]]) -> str:
        """Generate Sphinx documentation."""
        rst_content = []

        # Header
        rst_content.append("AI Agent Platform Examples")
        rst_content.append("=" * 50)
        rst_content.append("")
        rst_content.append("This documentation is auto-generated from example files.")
        rst_content.append("")

        # Generate content for each category
        for category in self.categories:
            if category not in examples:
                continue

            rst_content.append(f"{category.replace('-', ' ').title()}")
            rst_content.append("-" * len(category.replace("-", " ")))
            rst_content.append("")

            for interface in self.interfaces:
                files = examples[category][interface]
                if not files:
                    continue

                interface_name = "Python SDK" if interface == "sdk" else "CLI"
                rst_content.append(f"{interface_name}")
                rst_content.append("^" * len(interface_name))
                rst_content.append("")

                for file_path in files:
                    info = self.parse_example_header(file_path, interface)

                    rst_content.append(f"{info['title']}")
                    rst_content.append("~" * len(info["title"]))
                    rst_content.append("")
                    rst_content.append(f"**Goal:** {info['goal']}")
                    rst_content.append("")
                    rst_content.append(f"**Estimated time:** {info['time']}")
                    rst_content.append("")
                    rst_content.append(f"**Complexity:** {info['complexity']}")
                    rst_content.append("")

                    if info["prerequisites"]:
                        rst_content.append("**Prerequisites:**")
                        for prereq in info["prerequisites"]:
                            rst_content.append(f"- {prereq}")
                        rst_content.append("")

                    rst_content.append(f"**Run:** ``{info['run_command']}``")
                    rst_content.append("")
                    rst_content.append(f"**Cleanup:** {info['cleanup']}")
                    rst_content.append("")

                    if info["authors"]:
                        rst_content.append("**Authors:**")
                        for author in info["authors"]:
                            rst_content.append(f"- {author}")
                        rst_content.append("")

                    rst_content.append("")

        return "\n".join(rst_content)

    def generate_docs(self, format_type: str = "markdown") -> None:
        """Generate documentation in the specified format."""
        # Discover examples
        examples = {}

        for category in self.categories:
            examples[category] = {"sdk": [], "cli": []}
            category_path = self.examples_root / category

            if not category_path.exists():
                continue

            for interface in self.interfaces:
                interface_path = category_path / interface
                if interface_path.exists():
                    if interface == "sdk":
                        files = list(interface_path.glob("*.py"))
                    else:  # cli
                        files = list(interface_path.glob("*.md"))

                    files.sort(key=lambda x: x.name)
                    examples[category][interface] = files

        # Generate documentation
        if format_type == "markdown":
            content = self.generate_markdown_doc(examples)
            output_file = self.output_dir / "examples.md"
        elif format_type == "sphinx":
            content = self.generate_sphinx_doc(examples)
            output_file = self.output_dir / "examples.rst"
        else:
            raise ValueError(f"Unsupported format: {format_type}")

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Write documentation
        output_file.write_text(content, encoding="utf-8")
        print(f"✅ Generated {format_type} documentation: {output_file}")

        # Also generate a simple index
        index_content = """# Examples Index

This index was auto-generated from example files.

## Quick Links

- [Full Examples Documentation](examples.md)
- [Examples Runner](../examples/run_examples.py)
- [Environment Setup](../examples/env.example)

## Categories

"""

        for category in self.categories:
            if category in examples:
                sdk_count = len(examples[category]["sdk"])
                cli_count = len(examples[category]["cli"])
                total = sdk_count + cli_count

                if total > 0:
                    index_content += f"- **{category.replace('-', ' ').title()}** ({total} examples)\n"
                    if sdk_count > 0:
                        index_content += f"  - {sdk_count} Python SDK examples\n"
                    if cli_count > 0:
                        index_content += f"  - {cli_count} CLI examples\n"
                    index_content += "\n"

        index_file = self.output_dir / "examples_index.md"
        index_file.write_text(index_content, encoding="utf-8")
        print(f"✅ Generated examples index: {index_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate documentation from examples")
    parser.add_argument(
        "--examples-dir",
        type=Path,
        default=Path("examples"),
        help="Path to examples directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/examples"),
        help="Output directory for generated docs",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "sphinx"],
        default="markdown",
        help="Output format for documentation",
    )

    args = parser.parse_args()

    if not args.examples_dir.exists():
        print(f"❌ Examples directory not found: {args.examples_dir}")
        sys.exit(1)

    generator = ExampleDocGenerator(args.examples_dir, args.output_dir)

    try:
        generator.generate_docs(args.format)
        print("🎉 Documentation generation completed successfully!")
    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
