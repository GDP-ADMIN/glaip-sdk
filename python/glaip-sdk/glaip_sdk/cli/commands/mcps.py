"""MCP management commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from glaip_sdk.utils import is_uuid

from ..utils import (
    get_client,
    handle_ambiguous_resource,
    output_flags,
    output_list,
    output_result,
)

console = Console()


@click.group(name="mcps", no_args_is_help=True)
def mcps_group():
    """MCP management operations."""
    pass


def _resolve_mcp(ctx, client, ref, select=None):
    """Resolve MCP reference (ID or name) with ambiguity handling."""
    if is_uuid(ref):
        return client.mcps.get_mcp_by_id(ref)

    # Find MCPs by name
    matches = client.mcps.find_mcps(name=ref)
    if not matches:
        raise click.ClickException(f"MCP '{ref}' not found")

    if len(matches) == 1:
        return matches[0]

    # Multiple matches - handle ambiguity
    if select:
        idx = int(select) - 1
        if not (0 <= idx < len(matches)):
            raise click.ClickException(f"--select must be 1..{len(matches)}")
        return matches[idx]

    return handle_ambiguous_resource(ctx, "MCP", ref, matches)


@mcps_group.command(name="list")
@output_flags()
@click.pass_context
def list_mcps(ctx):
    """List all MCPs."""
    try:
        client = get_client(ctx)
        mcps = client.mcps.list_mcps()

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("id", "ID", "dim", 36),
            ("name", "Name", "cyan", None),
            ("config", "Config", "blue", None),
        ]

        # Transform function for safe dictionary access
        def transform_mcp(mcp):
            # Handle both dict and object formats
            if isinstance(mcp, dict):
                return {
                    "id": str(mcp.get("id", "N/A")),
                    "name": mcp.get("name", "N/A"),
                    "config": str(mcp.get("config", "N/A"))[:50] + "..."
                    if mcp.get("config")
                    else "N/A",
                }
            else:
                # Fallback to attribute access
                return {
                    "id": str(getattr(mcp, "id", "N/A")),
                    "name": getattr(mcp, "name", "N/A"),
                    "config": str(getattr(mcp, "config", "N/A"))[:50] + "..."
                    if getattr(mcp, "config", None)
                    else "N/A",
                }

        output_list(ctx, mcps, "🔌 Available MCPs", columns, transform_mcp)

    except Exception as e:
        raise click.ClickException(str(e))


@mcps_group.command()
@click.option("--name", required=True, help="MCP name")
@click.option("--transport", required=True, help="MCP transport protocol")
@click.option("--description", help="MCP description")
@click.option("--config", help="JSON configuration string")
@output_flags()
@click.pass_context
def create(ctx, name, transport, description, config):
    """Create a new MCP."""
    try:
        client = get_client(ctx)

        # Parse config if provided
        mcp_config = {}
        if config:
            try:
                mcp_config = json.loads(config)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON in --config")

        mcp = client.mcps.create_mcp(
            name=name,
            type="server",  # Always server type
            transport=transport,
            description=description,
            config=mcp_config,
        )

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(mcp.model_dump(), indent=2))
        else:
            # Rich output
            panel = Panel(
                f"[green]✅ MCP '{mcp.name}' created successfully![/green]\n\n"
                f"ID: {mcp.id}\n"
                f"Type: server (default)\n"
                f"Description: {description or 'No description'}",
                title="🔌 MCP Created",
                border_style="green",
            )
            console.print(panel)

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error creating MCP: {e}[/red]")
        raise click.ClickException(str(e))


@mcps_group.command()
@click.argument("mcp_ref")
@output_flags()
@click.pass_context
def get(ctx, mcp_ref):
    """Get MCP details."""
    try:
        client = get_client(ctx)

        # Get MCP by ID or name (shows all matches for names)
        if is_uuid(mcp_ref):
            mcp = client.mcps.get_mcp_by_id(mcp_ref)
        else:
            # Find MCPs by name
            matches = client.mcps.find_mcps(name=mcp_ref)
            if not matches:
                raise click.ClickException(f"MCP '{mcp_ref}' not found")
            elif len(matches) == 1:
                mcp = matches[0]
            else:
                # Show all matches
                console.print(
                    f"[yellow]Multiple MCPs found with name '{mcp_ref}':[/yellow]"
                )
                for i, match in enumerate(matches, 1):
                    console.print(f"  {i}. {match.name} (ID: {match.id})")
                console.print("[yellow]Use the ID for unambiguous operations.[/yellow]")
                return

        # Create result data with actual available fields
        result_data = {
            "id": str(getattr(mcp, "id", "N/A")),
            "name": getattr(mcp, "name", "N/A"),
            "type": getattr(mcp, "type", "N/A"),
            "config": getattr(mcp, "config", "N/A"),
            "status": getattr(mcp, "status", "N/A"),
            "connection_status": getattr(mcp, "connection_status", "N/A"),
        }

        output_result(
            ctx, result_data, title="MCP Details", panel_title=f"🔌 {mcp.name}"
        )

    except Exception as e:
        raise click.ClickException(str(e))


@mcps_group.command("tools")
@click.argument("mcp_ref")
@output_flags()
@click.pass_context
def list_tools(ctx, mcp_ref):
    """List tools from MCP."""
    try:
        client = get_client(ctx)

        # Get MCP by ID or name (shows all matches for names)
        if is_uuid(mcp_ref):
            mcp = client.get_mcp_by_id(mcp_ref)
        else:
            # Find MCPs by name
            matches = client.find_mcps(name=mcp_ref)
            if not matches:
                raise click.ClickException(f"MCP '{mcp_ref}' not found")
            elif len(matches) == 1:
                mcp = matches[0]
            else:
                # Show all matches
                console.print(
                    f"[yellow]Multiple MCPs found with name '{mcp_ref}':[/yellow]"
                )
                for i, match in enumerate(matches, 1):
                    console.print(f"  {i}. {match.name} (ID: {match.id})")
                console.print("[yellow]Use the ID for unambiguous operations.[/yellow]")
                return

        # Get tools from MCP
        tools = client.mcps.get_mcp_tools(mcp.id)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(tools, indent=2))
        else:  # rich output
            if tools:
                table = Table(
                    title=f"🔧 Tools from MCP: {mcp.name}",
                    show_header=True,
                    header_style="bold magenta",
                )
                table.add_column("Name", style="cyan", no_wrap=True)
                table.add_column("Description", style="green")
                table.add_column("Type", style="yellow")

                for tool in tools:
                    table.add_row(
                        tool.get("name", "N/A"),
                        tool.get("description", "N/A")[:50] + "..."
                        if len(tool.get("description", "")) > 50
                        else tool.get("description", "N/A"),
                        tool.get("type", "N/A"),
                    )
                console.print(table)
            else:
                console.print(f"[yellow]No tools found in MCP '{mcp.name}'[/yellow]")

    except Exception as e:
        raise click.ClickException(str(e))


@mcps_group.command("tools-from-config")
@click.option(
    "--from-file",
    "config_file",
    type=click.Path(exists=True),
    required=True,
    help="MCP config JSON file",
)
@output_flags()
@click.pass_context
def tools_from_config(ctx, config_file):
    """Fetch tools from MCP config."""
    try:
        client = get_client(ctx)

        # Load MCP config from file
        with open(config_file) as f:
            config = json.load(f)

        if ctx.obj.get("view") != "json":
            console.print(
                f"[yellow]Fetching tools from MCP config in {config_file}...[/yellow]"
            )

        # Get tools from MCP config
        tools = client.mcps.get_tools_from_mcp_config(config)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(tools, indent=2))
        else:  # rich output
            if tools:
                table = Table(
                    title="🔧 Tools from MCP Config",
                    show_header=True,
                    header_style="bold magenta",
                )
                table.add_column("Name", style="cyan", no_wrap=True)
                table.add_column("Description", style="green")
                table.add_column("Type", style="yellow")

                for tool in tools:
                    table.add_row(
                        tool.get("name", "N/A"),
                        tool.get("description", "N/A")[:50] + "..."
                        if len(tool.get("description", "")) > 50
                        else tool.get("description", "N/A"),
                        tool.get("type", "N/A"),
                    )
                console.print(table)
            else:
                console.print("[yellow]No tools found in MCP config[/yellow]")

    except Exception as e:
        raise click.ClickException(str(e))


@mcps_group.command("test-connection")
@click.option(
    "--from-file",
    "config_file",
    required=True,
    help="MCP config JSON file",
)
@output_flags()
@click.pass_context
def test_connection(ctx, config_file):
    """Test MCP connection using config file."""
    try:
        client = get_client(ctx)

        # Load MCP config from file
        with open(config_file) as f:
            config = json.load(f)

        if ctx.obj.get("view") != "json":
            console.print(
                f"[yellow]Testing MCP connection with config from {config_file}...[/yellow]"
            )

        # Test connection using config
        result = client.mcps.test_mcp_connection_from_config(config)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(result, indent=2))
        else:
            success_panel = Panel(
                f"[green]✓[/green] MCP connection test successful!\n\n"
                f"[bold]Result:[/bold] {result}",
                title="🔌 Connection Test",
                border_style="green",
            )
            console.print(success_panel)

    except Exception as e:
        raise click.ClickException(str(e))


@mcps_group.command()
@click.argument("mcp_ref")
@click.option("--name", help="New MCP name")
@click.option("--description", help="New description")
@click.option("--config", help="JSON configuration string")
@output_flags()
@click.pass_context
def update(ctx, mcp_ref, name, description, config):
    """Update an existing MCP."""
    try:
        client = get_client(ctx)

        # Get MCP by ID or name (shows all matches for names)
        if is_uuid(mcp_ref):
            mcp = client.mcps.get_mcp_by_id(mcp_ref)
        else:
            # Find MCPs by name
            matches = client.mcps.find_mcps(name=mcp_ref)
            if not matches:
                raise click.ClickException(f"MCP '{mcp_ref}' not found")
            elif len(matches) == 1:
                mcp = matches[0]
            else:
                # Show all matches
                console.print(
                    f"[yellow]Multiple MCPs found with name '{mcp_ref}':[/yellow]"
                )
                for i, match in enumerate(matches, 1):
                    console.print(f"  {i}. {match.name} (ID: {match.id})")
                console.print("[yellow]Use the ID for unambiguous operations.[/yellow]")
                return

        # Build update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if config is not None:
            try:
                update_data["config"] = json.loads(config)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON in --config")

        if not update_data:
            raise click.ClickException("No update fields specified")

        # Update MCP
        updated_mcp = client.mcps.update_mcp(mcp.id, update_data)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(updated_mcp.model_dump(), indent=2))
        else:
            console.print(
                f"[green]✅ MCP '{updated_mcp.name}' updated successfully[/green]"
            )

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error updating MCP: {e}[/red]")
        raise click.ClickException(str(e))


@mcps_group.command()
@click.argument("mcp_ref")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
@output_flags()
@click.pass_context
def delete(ctx, mcp_ref, yes):
    """Delete an MCP."""
    try:
        client = get_client(ctx)

        # Get MCP by ID or name (shows all matches for names)
        if is_uuid(mcp_ref):
            mcp = client.mcps.get_mcp_by_id(mcp_ref)
        else:
            # Find MCPs by name
            matches = client.mcps.find_mcps(name=mcp_ref)
            if not matches:
                raise click.ClickException(f"MCP '{mcp_ref}' not found")
            elif len(matches) == 1:
                mcp = matches[0]
            else:
                # Show all matches
                console.print(
                    f"[yellow]Multiple MCPs found with name '{mcp_ref}':[/yellow]"
                )
                for i, match in enumerate(matches, 1):
                    console.print(f"  {i}. {match.name} (ID: {match.id})")
                console.print("[yellow]Use the ID for unambiguous operations.[/yellow]")
                return

        # Confirm deletion
        if not yes and not click.confirm(
            f"Are you sure you want to delete MCP '{mcp.name}'?"
        ):
            if ctx.obj.get("view") != "json":
                console.print("Deletion cancelled.")
            return

        client.mcps.delete_mcp(mcp.id)

        if ctx.obj.get("view") == "json":
            click.echo(
                json.dumps(
                    {"success": True, "message": f"MCP '{mcp.name}' deleted"}, indent=2
                )
            )
        else:
            console.print(f"[green]✅ MCP '{mcp.name}' deleted successfully[/green]")

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error deleting MCP: {e}[/red]")
        raise click.ClickException(str(e))
