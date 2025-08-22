"""Tool management commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json

import click
from rich.console import Console
from rich.panel import Panel

from glaip_sdk.utils import is_uuid

from ..utils import (
    get_client,
    handle_ambiguous_resource,
    output_flags,
    output_list,
    output_result,
)

console = Console()


@click.group(name="tools", no_args_is_help=True)
def tools_group():
    """Tool management operations."""
    pass


def _resolve_tool(ctx, client, ref, select=None):
    """Resolve tool reference (ID or name) with ambiguity handling."""
    if is_uuid(ref):
        return client.get_tool(ref)

    # Use find_tools for name-based resolution
    matches = client.find_tools(name=ref)
    if not matches:
        raise click.ClickException(f"Tool not found: {ref}")

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        if select:
            idx = int(select) - 1
            if not (0 <= idx < len(matches)):
                raise click.ClickException(f"--select must be 1..{len(matches)}")
            return matches[idx]
        return handle_ambiguous_resource(ctx, "tool", ref, matches)
    else:
        raise click.ClickException(f"Tool not found: {ref}")


@tools_group.command(name="list")
@output_flags()
@click.pass_context
def list_tools(ctx):
    """List all tools."""
    try:
        client = get_client(ctx)
        tools = client.list_tools()

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("id", "ID", "dim", 36),
            ("name", "Name", "cyan", None),
            ("framework", "Framework", "blue", None),
        ]

        # Transform function for safe dictionary access
        def transform_tool(tool):
            # Handle both dict and object formats
            if isinstance(tool, dict):
                return {
                    "id": str(tool.get("id", "N/A")),
                    "name": tool.get("name", "N/A"),
                    "framework": tool.get("framework", "N/A"),
                }
            else:
                # Fallback to attribute access
                return {
                    "id": str(getattr(tool, "id", "N/A")),
                    "name": getattr(tool, "name", "N/A"),
                    "framework": getattr(tool, "framework", "N/A"),
                }

        output_list(ctx, tools, "🔧 Available Tools", columns, transform_tool)

    except Exception as e:
        raise click.ClickException(str(e))


@tools_group.command()
@click.option(
    "--file",
    type=click.Path(exists=True),
    help="Tool file to upload (optional for metadata-only tools)",
)
@click.option(
    "--name",
    help="Tool name (required for metadata-only tools, extracted from script if file provided)",
)
@click.option(
    "--description",
    help="Tool description (optional - extracted from script if file provided)",
)
@click.option(
    "--tags",
    help="Comma-separated tags for the tool",
)
@output_flags()
@click.pass_context
def create(ctx, file, name, description, tags):
    """Create a new tool."""
    try:
        client = get_client(ctx)

        # Validate required parameters based on creation method
        if not file:
            # Metadata-only tool creation
            if not name:
                raise click.ClickException(
                    "--name is required when creating metadata-only tools"
                )

        # Create tool based on whether file is provided
        if file:
            # File-based tool creation - use create_tool_from_code for proper plugin processing
            with open(file, encoding="utf-8") as f:
                code_content = f.read()

            # Extract name from file if not provided
            if not name:
                import os

                name = os.path.splitext(os.path.basename(file))[0]

            # Create tool plugin using the upload endpoint
            tool = client.create_tool_from_code(name, code_content)
        else:
            # Metadata-only tool creation
            tool_kwargs = {}
            if name:
                tool_kwargs["name"] = name
            if description:
                tool_kwargs["description"] = description
            if tags:
                tool_kwargs["tags"] = [tag.strip() for tag in tags.split(",")]

            tool = client.create_tool(**tool_kwargs)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(tool.model_dump(), indent=2))
        else:
            # Rich output
            creation_method = (
                "file upload (custom)" if file else "metadata only (native)"
            )
            panel = Panel(
                f"[green]✅ Tool '{tool.name}' created successfully via {creation_method}![/green]\n\n"
                f"ID: {tool.id}\n"
                f"Framework: langchain (default)\n"
                f"Type: {'custom' if file else 'native'} (auto-detected)\n"
                f"Description: {getattr(tool, 'description', 'No description')}",
                title="🔧 Tool Created",
                border_style="green",
            )
            console.print(panel)

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error creating tool: {e}[/red]")
        raise click.ClickException(str(e))


@tools_group.command()
@click.argument("tool_ref")
@click.option("--select", type=int, help="Choose among ambiguous matches (1-based)")
@output_flags()
@click.pass_context
def get(ctx, tool_ref, select):
    """Get tool details."""
    try:
        client = get_client(ctx)

        # Resolve tool with ambiguity handling
        tool = _resolve_tool(ctx, client, tool_ref, select)

        # Create result data with all available fields from backend
        result_data = {
            "id": str(getattr(tool, "id", "N/A")),
            "name": getattr(tool, "name", "N/A"),
            "tool_type": getattr(tool, "tool_type", "N/A"),
            "framework": getattr(tool, "framework", "N/A"),
            "version": getattr(tool, "version", "N/A"),
            "description": getattr(tool, "description", "N/A"),
        }

        output_result(
            ctx, result_data, title="Tool Details", panel_title=f"🔧 {tool.name}"
        )

    except Exception as e:
        raise click.ClickException(str(e))


@tools_group.command()
@click.argument("tool_id")
@click.option(
    "--file", type=click.Path(exists=True), help="New tool file for code update"
)
@click.option("--description", help="New description")
@click.option("--tags", help="Comma-separated tags")
@output_flags()
@click.pass_context
def update(ctx, tool_id, file, description, tags):
    """Update a tool (code or metadata)."""
    try:
        client = get_client(ctx)

        # Get tool by ID (no ambiguity handling needed)
        try:
            tool = client.get_tool_by_id(tool_id)
        except Exception as e:
            raise click.ClickException(f"Tool with ID '{tool_id}' not found: {e}")

        update_data = {}

        if description:
            update_data["description"] = description

        if tags:
            update_data["tags"] = [tag.strip() for tag in tags.split(",")]

        if file:
            # Update code
            updated_tool = tool.update(file_path=file)
            if ctx.obj.get("view") != "json":
                console.print(f"[green]✓[/green] Tool code updated from {file}")
        elif update_data:
            # Update metadata
            updated_tool = tool.update(**update_data)
            if ctx.obj.get("view") != "json":
                console.print("[green]✓[/green] Tool metadata updated")
        else:
            if ctx.obj.get("view") != "json":
                console.print("[yellow]No updates specified[/yellow]")
            return

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(updated_tool.model_dump(), indent=2))
        else:
            console.print(
                f"[green]✅ Tool '{updated_tool.name}' updated successfully[/green]"
            )

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error updating tool: {e}[/red]")
        raise click.ClickException(str(e))


@tools_group.command()
@click.argument("tool_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
@output_flags()
@click.pass_context
def delete(ctx, tool_id, yes):
    """Delete a tool."""
    try:
        client = get_client(ctx)

        # Get tool by ID (no ambiguity handling needed)
        try:
            tool = client.get_tool_by_id(tool_id)
        except Exception as e:
            raise click.ClickException(f"Tool with ID '{tool_id}' not found: {e}")

        # Confirm deletion
        if not yes and not click.confirm(
            f"Are you sure you want to delete tool '{tool.name}'?"
        ):
            if ctx.obj.get("view") != "json":
                console.print("Deletion cancelled.")
            return

        tool.delete()

        if ctx.obj.get("view") == "json":
            click.echo(
                json.dumps(
                    {"success": True, "message": f"Tool '{tool.name}' deleted"},
                    indent=2,
                )
            )
        else:
            console.print(f"[green]✅ Tool '{tool.name}' deleted successfully[/green]")

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error deleting tool: {e}[/red]")
        raise click.ClickException(str(e))
