"""Main CLI entry point for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import sys

import click

from glaip_sdk.cli.commands.agents import agents_group
from glaip_sdk.cli.commands.configure import config_group, configure_command
from glaip_sdk.cli.commands.init import init_command
from glaip_sdk.cli.commands.mcps import mcps_group
from glaip_sdk.cli.commands.models import models_group
from glaip_sdk.cli.commands.tools import tools_group


@click.group()
@click.version_option(version="0.1.1", prog_name="aip")
@click.option("--api-url", envvar="AIP_API_URL", help="AIP API URL")
@click.option("--api-key", envvar="AIP_API_KEY", help="AIP API Key")
@click.option("--timeout", default=30.0, help="Request timeout in seconds")
@click.option(
    "--view",
    "view",
    type=click.Choice(["rich", "plain", "json", "md"]),
    default="rich",
    help="Output view format",
)
@click.option("--no-tty", is_flag=True, help="Disable TTY renderer")
@click.pass_context
def main(ctx, api_url, api_key, timeout, view, no_tty):
    """AIP SDK Command Line Interface.

    A comprehensive CLI for managing AI Agent Platform resources including
    agents, tools, MCPs, and more.

    Examples:
        aip configure                   # Configure credentials
        aip agents list                   # List all agents
        aip tools create my_tool.py      # Create a new tool
        aip agents run my-agent "Hello"  # Run an agent
        aip init                         # Initialize configuration
    """

    # Store configuration in context
    ctx.ensure_object(dict)
    ctx.obj["api_url"] = api_url
    ctx.obj["api_key"] = api_key
    ctx.obj["timeout"] = timeout
    ctx.obj["view"] = view

    ctx.obj["tty"] = not no_tty


# Add command groups
main.add_command(agents_group)
main.add_command(config_group)
main.add_command(tools_group)
main.add_command(mcps_group)
main.add_command(models_group)
main.add_command(init_command)

# Add top-level commands
main.add_command(configure_command)


# Tip: `--version` is provided by click.version_option above.


@main.command()
@click.pass_context
def status(ctx):
    """Show connection status and basic info."""
    config = {}
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table

        from glaip_sdk import Client
        from glaip_sdk.cli.commands.configure import load_config

        console = Console()

        # Load config from file and merge with context
        file_config = load_config()
        context_config = ctx.obj or {}

        # Load environment variables (middle priority)
        import os

        env_config = {}
        if os.getenv("AIP_API_URL"):
            env_config["api_url"] = os.getenv("AIP_API_URL")
        if os.getenv("AIP_API_KEY"):
            env_config["api_key"] = os.getenv("AIP_API_KEY")

        # Filter out None values from context config to avoid overriding other configs
        filtered_context = {k: v for k, v in context_config.items() if v is not None}

        # Merge configs: file (low) -> env (mid) -> CLI args (high)
        config = {**file_config, **env_config, **filtered_context}

        if not config.get("api_url") or not config.get("api_key"):
            console.print(
                Panel(
                    "[bold red]❌ Configuration incomplete[/bold red]\n\n"
                    f"🔍 Current config:\n"
                    f"   • API URL: {config.get('api_url', 'Not set')}\n"
                    f"   • API Key: {'***' + config.get('api_key', '')[-4:] if config.get('api_key') else 'Not set'}\n\n"
                    f"💡 To fix this:\n"
                    f"   • Run 'aip configure' to set up credentials\n"
                    f"   • Or run 'aip config list' to see current config",
                    title="❌ Configuration Error",
                    border_style="red",
                )
            )
            sys.exit(1)

        # Try to create client
        client = Client(
            api_url=config["api_url"],
            api_key=config["api_key"],
            timeout=config.get("timeout", 30.0),
        )

        # Test connection by listing resources
        try:
            agents = client.list_agents()
            tools = client.list_tools()
            mcps = client.list_mcps()

            # Create status table
            table = Table(title="🔗 AIP Platform Status")
            table.add_column("Resource", style="cyan", width=15)
            table.add_column("Count", style="green", width=10)
            table.add_column("Status", style="green", width=15)

            table.add_row("Agents", str(len(agents)), "✅ Available")
            table.add_row("Tools", str(len(tools)), "✅ Available")
            table.add_row("MCPs", str(len(mcps)), "✅ Available")

            console.print(
                Panel(
                    f"[bold green]✅ Connected to AIP Platform[/bold green]\n"
                    f"🔗 API URL: {client.api_url}\n"
                    f"⏱️  Timeout: {config.get('timeout', 30.0)}s",
                    title="🚀 Connection Status",
                    border_style="green",
                )
            )

            console.print(table)

        except Exception as e:
            console.print(
                Panel(
                    f"[bold yellow]⚠️  Connection established but API call failed[/bold yellow]\n"
                    f"🔗 API URL: {client.api_url}\n"
                    f"❌ Error: {e}\n\n"
                    f"💡 This usually means:\n"
                    f"   • Network connectivity issues\n"
                    f"   • API permissions problems\n"
                    f"   • Backend service issues",
                    title="⚠️  Partial Connection",
                    border_style="yellow",
                )
            )

        client.close()

    except Exception as e:
        console.print(
            Panel(
                f"[bold red]❌ Connection failed[/bold red]\n\n"
                f"🔍 Error: {e}\n\n"
                f"💡 Troubleshooting steps:\n"
                f"   • Run 'aip config list' to check configuration\n"
                f"   • Run 'aip configure' to update credentials\n"
                f"   • Verify your API URL and key are correct\n"
                f"   • Check network connectivity to {config.get('api_url', 'your API')}",
                title="❌ Connection Error",
                border_style="red",
            )
        )
        sys.exit(1)


@main.command()
def version():
    """Show version information."""
    from glaip_sdk.config.constants import SDK_VERSION

    click.echo(f"aip version {SDK_VERSION}")


@main.command()
@click.option(
    "--check-only", is_flag=True, help="Only check for updates without installing"
)
@click.option(
    "--force", is_flag=True, help="Force update even if no new version available"
)
def update(check_only: bool, force: bool):
    """Update AIP SDK to the latest version from PyPI."""
    try:
        import subprocess
        import sys

        from rich.console import Console
        from rich.panel import Panel

        console = Console()

        if check_only:
            console.print(
                Panel(
                    "[bold blue]🔍 Checking for updates...[/bold blue]\n\n"
                    "💡 To install updates, run: aip update",
                    title="📋 Update Check",
                    border_style="blue",
                )
            )
            return

        console.print(
            Panel(
                "[bold blue]🔄 Updating AIP SDK...[/bold blue]\n\n"
                "📦 This will update the package from PyPI\n"
                "💡 Use --check-only to just check for updates",
                title="🚀 Update Process",
                border_style="blue",
                padding=(0, 1),
            )
        )

        # Update using pip
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "glaip-sdk"],
                capture_output=True,
                text=True,
                check=True,
            )

            console.print(
                Panel(
                    "[bold green]✅ Update successful![/bold green]\n\n"
                    "🔄 AIP SDK has been updated to the latest version\n"
                    "💡 Restart your terminal or run 'aip --version' to verify",
                    title="🎉 Update Complete",
                    border_style="green",
                    padding=(0, 1),
                )
            )

            # Show new version
            version_result = subprocess.run(
                [sys.executable, "-m", "glaip_sdk.cli.main", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            console.print(f"📋 New version: {version_result.stdout.strip()}")

        except subprocess.CalledProcessError as e:
            console.print(
                Panel(
                    f"[bold red]❌ Update failed[/bold red]\n\n"
                    f"🔍 Error: {e.stderr}\n\n"
                    "💡 Troubleshooting:\n"
                    "   • Check your internet connection\n"
                    "   • Try running: pip install --upgrade glaip-sdk\n"
                    "   • Check if you have write permissions",
                    title="❌ Update Error",
                    border_style="red",
                    padding=(0, 1),
                )
            )
            sys.exit(1)

    except ImportError:
        console.print(
            Panel(
                "[bold red]❌ Rich library not available[/bold red]\n\n"
                "💡 Install rich: pip install rich\n"
                "   Then try: aip update",
                title="❌ Missing Dependency",
                border_style="red",
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
