"""CLI initialization command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import getpass
import os
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.command()
@click.option("--no-scaffold", is_flag=True, help="Skip creating sample agent and tool")
@click.option("--no-demo", is_flag=True, help="Don't launch interactive demo")
def init_command(no_scaffold, no_demo):
    """Initialize AIP project configuration."""

    console.print(
        Panel(
            "[bold cyan]Welcome to AIP![/bold cyan]\nLet's set up your project.",
            title="🚀 AIP Initialization",
            border_style="cyan",
        )
    )

    # Get configuration with better formatting
    console.print("\n[bold]Step 1:[/bold] API Configuration")
    console.print("─" * 50)

    # Use built-in input for better control
    console.print(
        "\n[cyan]AIP API URL[/cyan] (default: https://your-aip-instance.com):"
    )
    api_url = input("> ").strip()
    if not api_url:
        api_url = "https://your-aip-instance.com"

    console.print()  # Add spacing
    console.print("[cyan]AIP API Key[/cyan]:")
    api_key = getpass.getpass("> ")

    # Project configuration removed - not needed for AIP CLI

    # Create config directory
    config_dir = Path.home() / ".aip"
    config_dir.mkdir(exist_ok=True)

    # Save configuration
    config = {"api_url": api_url, "api_key": api_key}

    config_file = config_dir / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    # Set secure file permissions (0600) - best effort on all platforms
    try:
        os.chmod(config_file, 0o600)
    except Exception:
        # Best effort - may fail on Windows or other non-POSIX systems
        pass

    console.print(f"\n✅ Configuration saved to: {config_file}")

    # Create sample agent and tool if requested
    if not no_scaffold:
        console.print("\n[bold]Step 2:[/bold] Sample Resources")
        console.print("─" * 50)

        console.print("\n[cyan]Create sample agent & tool?[/cyan] (Y/n):")
        create_sample_resources = input("> ").strip().lower()
        if create_sample_resources in ["", "y", "yes"]:
            try:
                from glaip_sdk import Client

                # Set environment variables
                os.environ["AIP_API_URL"] = api_url
                os.environ["AIP_API_KEY"] = api_key

                client = Client()

                # Create sample agent
                agent = client.create_agent(
                    name="hello-world",
                    instruction="You are a helpful AI assistant that says hello",
                )
                console.print(f"✅ Created sample agent: {agent.name} (id: {agent.id})")

                # Create sample tool
                tool_content = '''def hello_tool(name="World"):
    """A simple hello tool."""
    return f"Hello, {name}!"
'''
                with open("greeting_tool.py", "w") as f:
                    f.write(tool_content)

                tool = client.create_tool("greeting_tool.py", framework="langchain")
                console.print(f"✅ Created sample tool: {tool.name} (id: {tool.id})")

            except Exception as e:
                console.print(f"⚠️  Warning: Could not create sample resources: {e}")

    # Launch interactive demo if requested
    if not no_demo:
        console.print("\n[bold]Step 3:[/bold] Interactive Demo")
        console.print("─" * 50)

        console.print("\n[cyan]Start an interactive demo now?[/cyan] (Y/n):")
        launch_demo = input("> ").strip().lower()
        if launch_demo in ["", "y", "yes"]:
            launch_interactive_demo()

    console.print("\n🎉 [bold green]AIP initialization complete![/bold green]")
    console.print(f"📁 Configuration: {config_file}")
    console.print("💡 Next steps:")
    console.print("   • Run 'aip agents list' to see your agents")
    console.print("   • Run 'aip tools list' to see your tools")
    console.print("   • Run 'aip status' to check connection")


def launch_interactive_demo():
    """Launch interactive demo with sample agent."""
    try:
        from glaip_sdk import Client

        console.print(
            Panel(
                "[bold green]Interactive Demo[/bold green]\nType to talk to hello-world. Ctrl+C to exit.",
                title="🎮 Demo Mode",
                border_style="green",
            )
        )

        client = Client()
        agents = client.find_agents(name="hello-world")
        if not agents:
            console.print("❌ Sample agent not found")
            return

        agent = agents[0]  # Use the first (and should be only) agent

        while True:
            try:
                console.print("\n> ", end="")
                user_input = input().strip()
                if user_input.lower() in ["exit", "quit", "bye"]:
                    break

                response = agent.run(user_input)
                console.print(f"🤖 {response}")

            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"❌ Error: {e}")

    except Exception as e:
        console.print(f"⚠️  Could not launch demo: {e}")


# Note: The init command should be registered in main.py, not here
# This prevents circular imports
