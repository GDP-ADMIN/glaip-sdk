"""Agent management commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from glaip_sdk.utils import is_uuid

from ..utils import (
    get_client,
    handle_ambiguous_resource,
    output_flags,
    output_list,
    output_result,
    safe_getattr,
)

console = Console()


@click.group(name="agents", no_args_is_help=True)
def agents_group():
    """Agent management operations."""
    pass


def _resolve_agent(ctx, client, ref, select=None):
    """Resolve agent reference (ID or name) with ambiguity handling."""
    if is_uuid(ref):
        return client.agents.get_agent_by_id(ref)

    # Find agents by name
    matches = client.agents.find_agents(name=ref)
    if not matches:
        raise click.ClickException(f"Agent '{ref}' not found")

    if len(matches) == 1:
        return matches[0]

    # Multiple matches - handle ambiguity
    if select:
        idx = int(select) - 1
        if not (0 <= idx < len(matches)):
            raise click.ClickException(f"--select must be 1..{len(matches)}")
        return matches[idx]

    return handle_ambiguous_resource(ctx, "agent", ref, matches)


@agents_group.command(name="list")
@output_flags()
@click.pass_context
def list_agents(ctx):
    """List all agents."""
    try:
        client = get_client(ctx)
        agents = client.agents.list_agents()

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("id", "ID", "dim", 36),
            ("name", "Name", "cyan", None),
            ("type", "Type", "yellow", None),
            ("framework", "Framework", "blue", None),
            ("version", "Version", "green", None),
        ]

        # Transform function for safe attribute access
        def transform_agent(agent):
            return {
                "id": str(agent.id),
                "name": agent.name,
                "type": safe_getattr(agent, "type") or "N/A",
                "framework": safe_getattr(agent, "framework") or "N/A",
                "version": safe_getattr(agent, "version") or "N/A",
            }

        output_list(ctx, agents, "🤖 Available Agents", columns, transform_agent)

    except Exception as e:
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_ref")
@click.option("--select", type=int, help="Choose among ambiguous matches (1-based)")
@output_flags()
@click.pass_context
def get(ctx, agent_ref, select):
    """Get agent details."""
    try:
        client = get_client(ctx)

        # Resolve agent with ambiguity handling
        agent = _resolve_agent(ctx, client, agent_ref, select)

        # Create result data with all available fields from backend
        result_data = {
            "id": str(getattr(agent, "id", "N/A")),
            "name": getattr(agent, "name", "N/A"),
            "type": getattr(agent, "type", "N/A"),
            "framework": getattr(agent, "framework", "N/A"),
            "version": getattr(agent, "version", "N/A"),
            "description": getattr(agent, "description", "N/A"),
            "instruction": getattr(agent, "instruction", "") or "-",
            "metadata": getattr(agent, "metadata", "N/A"),
            "language_model_id": getattr(agent, "language_model_id", "N/A"),
            "agent_config": getattr(agent, "agent_config", "N/A"),
            "tools": getattr(agent, "tools", []),
            "agents": getattr(agent, "agents", []),
            "mcps": getattr(agent, "mcps", []),
            "a2a_profile": getattr(agent, "a2a_profile", "N/A"),
        }

        output_result(
            ctx, result_data, title="Agent Details", panel_title=f"🤖 {agent.name}"
        )

    except Exception as e:
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_id")
@click.option("--input", "input_text", required=True, help="Input text for the agent")
@click.option("--chat-history", help="JSON string of chat history")
@click.option("--timeout", default=600, type=int, help="Request timeout in seconds")
@click.option(
    "--view",
    type=click.Choice(["rich", "plain", "json", "md"]),
    default="rich",
    help="Output view format",
)
@click.option(
    "--compact/--verbose", default=True, help="Collapse tool steps (default: compact)"
)
@click.option(
    "--save",
    type=click.Path(dir_okay=False, writable=True),
    help="Save transcript to file (md or json)",
)
@click.option(
    "--theme", type=click.Choice(["dark", "light"]), default="dark", help="Color theme"
)
@click.option(
    "--file",
    "files",
    multiple=True,
    type=click.Path(exists=True),
    help="Attach file(s)",
)
@click.pass_context
def run(
    ctx,
    agent_id,
    input_text,
    chat_history,
    timeout,
    view,
    compact,
    save,
    theme,
    files,
):
    """Run an agent with input text (ID required)."""
    try:
        client = get_client(ctx)

        # Get agent by ID (no ambiguity handling needed)
        try:
            agent = client.agents.get_agent_by_id(agent_id)
        except Exception as e:
            raise click.ClickException(f"Agent with ID '{agent_id}' not found: {e}")

        # Parse chat history if provided
        parsed_chat_history = None
        if chat_history:
            try:
                parsed_chat_history = json.loads(chat_history)
            except json.JSONDecodeError:
                raise click.ClickException("Invalid JSON in chat history")

        # Always stream (no --no-stream option)
        stream = ctx.obj.get("tty", True)

        # Create appropriate renderer based on view
        renderer = None
        if stream:
            from ...utils.run_renderer import RichStreamRenderer

            # Use RichStreamRenderer for all streaming output
            # Different view formats are handled in the output logic below
            renderer = RichStreamRenderer(
                console, verbose=not compact, theme=theme, use_emoji=True
            )

        # Run agent
        result = client.agents.run_agent(
            agent_id=agent.id,
            message=input_text,
            files=list(files),
            stream=stream,
            agent_name=agent.name,  # Pass agent name for better display
            **({"chat_history": parsed_chat_history} if parsed_chat_history else {}),
            **({"timeout": timeout} if timeout else {}),
        )

        # Check if renderer already printed output (for streaming renderers)
        printed_by_renderer = bool(renderer and stream)

        # Handle output format for non-streaming or fallback
        # Only print here if nothing was printed by the renderer
        if not printed_by_renderer:
            if (ctx.obj.get("view") == "json") or (view == "json"):
                click.echo(json.dumps({"output": result}, indent=2))
            elif view == "md":
                click.echo(f"# Assistant\n\n{result}")
            elif view == "plain":
                click.echo(result)
            elif not stream:
                # Rich output for non-streaming
                panel = Panel(
                    Text(result, style="green"),
                    title="Agent Output",
                    border_style="green",
                )
                console.print(panel)

        # Save transcript if requested
        if save and result:
            ext = (save.rsplit(".", 1)[-1] or "").lower()
            if ext == "json":
                content = json.dumps({"output": result}, indent=2)
                with open(save, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                content = f"# Assistant\n\n{result}\n"
                with open(save, "w", encoding="utf-8") as f:
                    f.write(content)
            console.print(f"[green]Transcript saved to: {save}[/green]")

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error running agent: {e}[/red]")
        raise click.ClickException(str(e))


@agents_group.command()
@click.option("--name", required=True, help="Agent name")
@click.option("--instruction", required=True, help="Agent instruction (prompt)")
@click.option("--tools", multiple=True, help="Tool names or IDs to attach")
@click.option("--agents", multiple=True, help="Sub-agent names to attach")
@click.option("--timeout", default=300, type=int, help="Execution timeout in seconds")
@output_flags()
@click.pass_context
def create(
    ctx,
    name,
    instruction,
    tools,
    agents,
    timeout,
):
    """Create a new agent."""
    try:
        client = get_client(ctx)
        # Create agent (uses backend default model)
        agent = client.agents.create_agent(
            name=name,
            instruction=instruction,
            tools=list(tools),
            agents=list(agents),
            timeout=timeout,
        )

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(agent.model_dump(), indent=2))
        else:
            # Rich output
            lm = getattr(agent, "model", None)
            if not lm:
                cfg = getattr(agent, "agent_config", {}) or {}
                lm = (
                    cfg.get("lm_name")
                    or cfg.get("model")
                    or "gpt-4.1 (backend default)"
                )

            panel = Panel(
                f"[green]✅ Agent '{agent.name}' created successfully![/green]\n\n"
                f"ID: {agent.id}\n"
                f"Model: {lm}\n"
                f"Type: {getattr(agent, 'type', 'config')}\n"
                f"Framework: {getattr(agent, 'framework', 'langchain')}\n"
                f"Version: {getattr(agent, 'version', '1.0')}",
                title="🤖 Agent Created",
                border_style="green",
            )
            console.print(panel)

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error creating agent: {e}[/red]")
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_id")
@click.option("--name", help="New agent name")
@click.option("--instruction", help="New instruction")
@click.option("--tools", multiple=True, help="New tool names or IDs")
@click.option("--agents", multiple=True, help="New sub-agent names")
@click.option("--timeout", type=int, help="New timeout value")
@output_flags()
@click.pass_context
def update(ctx, agent_id, name, instruction, tools, agents, timeout):
    """Update an existing agent."""
    try:
        client = get_client(ctx)

        # Get agent by ID (no ambiguity handling needed)
        try:
            agent = client.agents.get_agent_by_id(agent_id)
        except Exception as e:
            raise click.ClickException(f"Agent with ID '{agent_id}' not found: {e}")

        # Build update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if instruction is not None:
            update_data["instruction"] = instruction
        if tools:
            update_data["tools"] = list(tools)
        if agents:
            update_data["agents"] = list(agents)
        if timeout is not None:
            update_data["timeout"] = timeout

        if not update_data:
            raise click.ClickException("No update fields specified")

        # Update agent
        updated_agent = client.agents.update_agent(agent.id, update_data)

        if ctx.obj.get("view") == "json":
            click.echo(json.dumps(updated_agent.model_dump(), indent=2))
        else:
            console.print(
                f"[green]✅ Agent '{updated_agent.name}' updated successfully[/green]"
            )

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error updating agent: {e}[/red]")
        raise click.ClickException(str(e))


@agents_group.command()
@click.argument("agent_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
@output_flags()
@click.pass_context
def delete(ctx, agent_id, yes):
    """Delete an agent."""
    try:
        client = get_client(ctx)

        # Get agent by ID (no ambiguity handling needed)
        try:
            agent = client.agents.get_agent_by_id(agent_id)
        except Exception as e:
            raise click.ClickException(f"Agent with ID '{agent_id}' not found: {e}")

        # Confirm deletion
        if not yes and not click.confirm(
            f"Are you sure you want to delete agent '{agent.name}'?"
        ):
            if ctx.obj.get("view") != "json":
                console.print("Deletion cancelled.")
            return

        client.agents.delete_agent(agent.id)

        if ctx.obj.get("view") == "json":
            click.echo(
                json.dumps(
                    {"success": True, "message": f"Agent '{agent.name}' deleted"},
                    indent=2,
                )
            )
        else:
            console.print(
                f"[green]✅ Agent '{agent.name}' deleted successfully[/green]"
            )

    except Exception as e:
        if ctx.obj.get("view") == "json":
            click.echo(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error deleting agent: {e}[/red]")
        raise click.ClickException(str(e))
