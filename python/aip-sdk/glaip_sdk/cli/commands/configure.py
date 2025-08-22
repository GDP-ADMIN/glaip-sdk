"""Configuration management commands.

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
from rich.table import Table

console = Console()

CONFIG_DIR = Path.home() / ".aip"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def load_config():
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {}

    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f) or {}


def save_config(config):
    """Save configuration to file."""
    CONFIG_DIR.mkdir(exist_ok=True)

    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    # Set secure file permissions
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:
        pass  # Best effort


@click.group()
def config_group():
    """Configuration management operations."""
    pass


@config_group.command()
def configure():
    """Configure AIP CLI credentials and settings interactively."""

    console.print(
        Panel(
            "[bold cyan]AIP Configuration[/bold cyan]\nConfigure your AIP CLI settings.",
            title="🔧 Configuration Setup",
            border_style="cyan",
        )
    )

    # Load existing config
    config = load_config()

    console.print("\n[bold]Enter your AIP configuration:[/bold]")
    console.print("(Leave blank to keep current values)")
    console.print("─" * 50)

    # API URL
    current_url = config.get("api_url", "")
    console.print(
        f"\n[cyan]AIP API URL[/cyan] {f'(current: {current_url})' if current_url else ''}:"
    )
    new_url = input("> ").strip()
    if new_url:
        config["api_url"] = new_url
    elif not current_url:
        config["api_url"] = "https://your-aip-instance.com"

    # API Key
    current_key_masked = (
        "***" + config.get("api_key", "")[-4:] if config.get("api_key") else ""
    )
    console.print(
        f"\n[cyan]AIP API Key[/cyan] {f'(current: {current_key_masked})' if current_key_masked else ''}:"
    )
    new_key = getpass.getpass("> ")
    if new_key:
        config["api_key"] = new_key

    # Save configuration
    save_config(config)

    console.print(f"\n✅ Configuration saved to: {CONFIG_FILE}")

    # Test the new configuration
    console.print("\n🔌 Testing connection...")
    try:
        from glaip_sdk import Client

        # Create client with new config
        client = Client(api_url=config["api_url"], api_key=config["api_key"])

        # Try to list resources to test connection
        try:
            agents = client.list_agents()
            console.print(f"✅ Connection successful! Found {len(agents)} agents")
        except Exception as e:
            console.print(f"⚠️  Connection established but API call failed: {e}")
            console.print(
                "   You may need to check your API permissions or network access"
            )

        client.close()

    except Exception as e:
        console.print(f"❌ Connection failed: {e}")
        console.print("   Please check your API URL and key")
        console.print("   You can run 'aip status' later to test again")

    console.print("\n💡 You can now use AIP CLI commands!")
    console.print("   • Run 'aip status' to check connection")
    console.print("   • Run 'aip agents list' to see your agents")


@config_group.command("list")
def list_config():
    """List current configuration."""

    config = load_config()

    if not config:
        console.print(
            "[yellow]No configuration found. Run 'aip config configure' to set up.[/yellow]"
        )
        return

    table = Table(title="🔧 AIP Configuration")
    table.add_column("Setting", style="cyan", width=20)
    table.add_column("Value", style="green")

    for key, value in config.items():
        if key == "api_key" and value:
            # Mask the API key
            masked_value = "***" + value[-4:] if len(value) > 4 else "***"
            table.add_row(key, masked_value)
        else:
            table.add_row(key, str(value))

    console.print(table)
    console.print(f"\n📁 Config file: {CONFIG_FILE}")


@config_group.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    """Set a configuration value."""

    valid_keys = ["api_url", "api_key"]

    if key not in valid_keys:
        console.print(
            f"[red]Error: Invalid key '{key}'. Valid keys are: {', '.join(valid_keys)}[/red]"
        )
        raise click.ClickException(f"Invalid configuration key: {key}")

    config = load_config()
    config[key] = value
    save_config(config)

    if key == "api_key":
        masked_value = "***" + value[-4:] if len(value) > 4 else "***"
        console.print(f"✅ Set {key} = {masked_value}")
    else:
        console.print(f"✅ Set {key} = {value}")


@config_group.command("get")
@click.argument("key")
def get_config(key):
    """Get a configuration value."""

    config = load_config()

    if key not in config:
        console.print(f"[yellow]Configuration key '{key}' not found.[/yellow]")
        raise click.ClickException(f"Configuration key not found: {key}")

    value = config[key]

    if key == "api_key":
        # Mask the API key for display
        masked_value = "***" + value[-4:] if len(value) > 4 else "***"
        console.print(masked_value)
    else:
        console.print(value)


@config_group.command("unset")
@click.argument("key")
def unset_config(key):
    """Remove a configuration value."""

    config = load_config()

    if key not in config:
        console.print(f"[yellow]Configuration key '{key}' not found.[/yellow]")
        return

    del config[key]
    save_config(config)

    console.print(f"✅ Removed {key} from configuration")


@config_group.command("reset")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def reset_config(force):
    """Reset all configuration to defaults."""

    if not force:
        console.print("[yellow]This will remove all AIP configuration.[/yellow]")
        confirm = input("Are you sure? (y/N): ").strip().lower()
        if confirm not in ["y", "yes"]:
            console.print("Cancelled.")
            return

    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        console.print(
            "✅ Configuration reset. Run 'aip config configure' to set up again."
        )
    else:
        console.print("[yellow]No configuration found to reset.[/yellow]")


# Note: The config command group should be registered in main.py


@click.command()
def configure_command():
    """Configure AIP CLI credentials and settings interactively."""

    console.print(
        Panel(
            "[bold cyan]AIP Configuration[/bold cyan]\nConfigure your AIP CLI settings.",
            title="🔧 Configuration Setup",
            border_style="cyan",
        )
    )

    # Load existing config
    config = load_config()

    console.print("\n[bold]Enter your AIP configuration:[/bold]")
    console.print("(Leave blank to keep current values)")
    console.print("─" * 50)

    # API URL
    current_url = config.get("api_url", "")
    console.print(
        f"\n[cyan]AIP API URL[/cyan] {f'(current: {current_url})' if current_url else ''}:"
    )
    new_url = input("> ").strip()
    if new_url:
        config["api_url"] = new_url
    elif not current_url:
        config["api_url"] = "https://your-aip-instance.com"

    # API Key
    current_key_masked = (
        "***" + config.get("api_key", "")[-4:] if config.get("api_key") else ""
    )
    console.print(
        f"\n[cyan]AIP API Key[/cyan] {f'(current: {current_key_masked})' if current_key_masked else ''}:"
    )
    new_key = getpass.getpass("> ")
    if new_key:
        config["api_key"] = new_key

    # Save configuration
    save_config(config)

    console.print(f"\n✅ Configuration saved to: {CONFIG_FILE}")

    # Test the new configuration
    console.print("\n🔌 Testing connection...")
    try:
        from glaip_sdk import Client

        # Create client with new config
        client = Client(api_url=config["api_url"], api_key=config["api_key"])

        # Try to list resources to test connection
        try:
            agents = client.list_agents()
            console.print(f"✅ Connection successful! Found {len(agents)} agents")
        except Exception as e:
            console.print(f"⚠️  Connection established but API call failed: {e}")
            console.print(
                "   You may need to check your API permissions or network access"
            )

        client.close()

    except Exception as e:
        console.print(f"❌ Connection failed: {e}")
        console.print("   Please check your API URL and key")
        console.print("   You can run 'aip status' later to test again")

    console.print("\n💡 You can now use AIP CLI commands!")
    console.print("   • Run 'aip status' to check connection")
    console.print("   • Run 'aip agents list' to see your agents")
