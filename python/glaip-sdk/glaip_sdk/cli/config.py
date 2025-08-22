"""CLI commands for managing SDK configuration.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
import os
from pathlib import Path

import click

from glaip_sdk import Client


def get_client(ctx) -> Client:
    """Get configured client from context."""
    config = ctx.obj or {}
    return Client(
        api_url=config.get("api_url"),
        api_key=config.get("api_key"),
        timeout=config.get("timeout", 30.0),
    )


@click.group()
def config_group():
    """Manage SDK configuration."""
    pass


@config_group.command()
@click.pass_context
def show(ctx):
    """Show current configuration."""
    try:
        # Get config from context
        context_config = ctx.obj or {}

        # Get config from environment
        env_config = {
            "api_url": os.getenv("AIP_API_URL"),
            "api_key": os.getenv("AIP_API_KEY"),
            "timeout": os.getenv("AIP_TIMEOUT", "30.0"),
        }

        # Get config from file
        config_path = Path.home() / ".aip" / "config.yaml"
        file_config = {}
        if config_path.exists():
            try:
                import yaml

                with open(config_path) as f:
                    file_config = yaml.safe_load(f) or {}
            except Exception:
                file_config = {}

        click.echo("🔧 AIP SDK Configuration")
        click.echo("=" * 50)

        # Show configuration sources
        click.echo("Configuration Sources (in order of precedence):")
        click.echo("  1. Command line arguments")
        click.echo("  2. Environment variables")
        click.echo("  3. Config file (~/.aip/config.yaml)")
        click.echo("  4. Default values")
        click.echo()

        # Show current values
        click.echo("Current Configuration:")
        click.echo(
            f"  API URL: {context_config.get('api_url') or env_config['api_url'] or file_config.get('api_url') or 'Not set'}"
        )

        api_key = (
            context_config.get("api_key")
            or env_config["api_key"]
            or file_config.get("api_key")
        )
        if api_key:
            # Mask API key for security
            masked_key = (
                api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            )
            click.echo(f"  API Key: {masked_key}")
        else:
            click.echo("  API Key: Not set")

        timeout = (
            context_config.get("timeout")
            or env_config["timeout"]
            or file_config.get("timeout")
            or "30.0"
        )
        click.echo(f"  Timeout: {timeout} seconds")

        # Show config file location
        click.echo(f"\nConfig file: {config_path}")
        if config_path.exists():
            click.echo("✅ Config file exists")
        else:
            click.echo("❌ Config file does not exist")

    except Exception as e:
        click.echo(f"❌ Error showing configuration: {e}")


@config_group.command()
@click.option("--api-url", help="Set API URL")
@click.option("--api-key", help="Set API key")
@click.option("--timeout", type=float, help="Set timeout in seconds")
@click.option("--output", "-o", type=click.Path(), help="Output file for configuration")
@click.pass_context
def set(ctx, api_url, api_key, timeout, output):
    """Set configuration values."""
    try:
        # Get current config
        config_path = Path.home() / ".aip" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config
        current_config = {}
        if config_path.exists():
            try:
                import yaml

                with open(config_path) as f:
                    current_config = yaml.safe_load(f) or {}
            except Exception:
                current_config = {}

        # Update config with new values
        updated = False
        if api_url:
            current_config["api_url"] = api_url
            updated = True
            click.echo(f"✅ API URL set to: {api_url}")

        if api_key:
            current_config["api_key"] = api_key
            updated = True
            # Mask API key for display
            masked_key = (
                api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            )
            click.echo(f"✅ API Key set to: {masked_key}")

        if timeout:
            current_config["timeout"] = timeout
            updated = True
            click.echo(f"✅ Timeout set to: {timeout} seconds")

        if not updated:
            click.echo(
                "❌ No configuration values provided. Use --help for available options."
            )
            return

        # Save updated config
        try:
            import yaml

            with open(config_path, "w") as f:
                yaml.dump(current_config, f, default_flow_style=False)
            click.echo(f"📄 Configuration saved to: {config_path}")
        except Exception as e:
            click.echo(f"❌ Error saving configuration: {e}")
            return

        # Save to output file if specified
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(current_config, f, indent=2, default=str)
            click.echo(f"📄 Configuration also saved to: {output_path}")

    except Exception as e:
        click.echo(f"❌ Error setting configuration: {e}")


@config_group.command()
@click.option("--api-url", is_flag=True, help="Remove API URL setting")
@click.option("--api-key", is_flag=True, help="Remove API key setting")
@click.option("--timeout", is_flag=True, help="Remove timeout setting")
@click.option("--all", is_flag=True, help="Remove all configuration")
@click.option(
    "--output", "-o", type=click.Path(), help="Output file for remaining configuration"
)
@click.pass_context
def unset(ctx, api_url, api_key, timeout, all, output):
    """Remove configuration values."""
    try:
        # Get current config
        config_path = Path.home() / ".aip" / "config.yaml"

        if not config_path.exists():
            click.echo("❌ No configuration file found.")
            return

        # Load current config
        try:
            import yaml

            with open(config_path) as f:
                current_config = yaml.safe_load(f) or {}
        except Exception as e:
            click.echo(f"❌ Error loading configuration: {e}")
            return

        # Remove specified values
        removed = False
        if all:
            # Remove all configuration
            current_config = {}
            removed = True
            click.echo("✅ All configuration removed")
        else:
            if api_url and "api_url" in current_config:
                del current_config["api_url"]
                removed = True
                click.echo("✅ API URL removed")

            if api_key and "api_key" in current_config:
                del current_config["api_key"]
                removed = True
                click.echo("✅ API Key removed")

            if timeout and "timeout" in current_config:
                del current_config["timeout"]
                removed = True
                click.echo("✅ Timeout removed")

        if not removed:
            click.echo(
                "❌ No configuration values specified for removal. Use --help for available options."
            )
            return

        # Save updated config
        if current_config:
            try:
                with open(config_path, "w") as f:
                    yaml.dump(current_config, f, default_flow_style=False)
                click.echo(f"📄 Updated configuration saved to: {config_path}")
            except Exception as e:
                click.echo(f"❌ Error saving configuration: {e}")
                return
        else:
            # Remove config file if empty
            try:
                config_path.unlink()
                click.echo(f"📄 Configuration file removed: {config_path}")
            except Exception as e:
                click.echo(f"❌ Error removing configuration file: {e}")
                return

        # Save to output file if specified
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(current_config, f, indent=2, default=str)
            click.echo(f"📄 Remaining configuration saved to: {output_path}")

    except Exception as e:
        click.echo(f"❌ Error removing configuration: {e}")


@config_group.command()
@click.option("--output", "-o", type=click.Path(), help="Output file for configuration")
@click.pass_context
def export(ctx, output):
    """Export current configuration."""
    try:
        # Get config from all sources
        config_path = Path.home() / ".aip" / "config.yaml"

        # Load file config
        file_config = {}
        if config_path.exists():
            try:
                import yaml

                with open(config_path) as f:
                    file_config = yaml.safe_load(f) or {}
            except Exception:
                file_config = {}

        # Get environment config
        env_config = {
            "api_url": os.getenv("AIP_API_URL"),
            "api_key": os.getenv("AIP_API_KEY"),
            "timeout": os.getenv("AIP_TIMEOUT"),
        }

        # Combine configs (environment overrides file)
        combined_config = {**file_config, **env_config}

        # Remove None values
        combined_config = {k: v for k, v in combined_config.items() if v is not None}

        if not combined_config:
            click.echo("❌ No configuration found to export.")
            return

        # Display configuration
        click.echo("📤 Exported Configuration:")
        click.echo("=" * 30)

        for key, value in combined_config.items():
            if key == "api_key" and value:
                # Mask API key for display
                masked_value = (
                    value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                )
                click.echo(f"{key}: {masked_value}")
            else:
                click.echo(f"{key}: {value}")

        # Save to output file if specified
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(combined_config, f, indent=2, default=str)
            click.echo(f"\n📄 Configuration exported to: {output_path}")
        else:
            # Save to default location
            export_path = Path.home() / ".aip" / "config_export.json"
            export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, "w") as f:
                json.dump(combined_config, f, indent=2, default=str)
            click.echo(f"\n📄 Configuration exported to: {export_path}")

    except Exception as e:
        click.echo(f"❌ Error exporting configuration: {e}")


@config_group.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--overwrite", is_flag=True, help="Overwrite existing configuration")
@click.option(
    "--output", "-o", type=click.Path(), help="Output file for imported configuration"
)
@click.pass_context
def import_config(ctx, config_file, overwrite, output):
    """Import configuration from a file."""
    try:
        config_path = Path(config_file)

        # Load configuration from file
        try:
            if config_path.suffix.lower() in [".json", ".js"]:
                with open(config_path) as f:
                    imported_config = json.load(f)
            elif config_path.suffix.lower() in [".yaml", ".yml"]:
                import yaml

                with open(config_path) as f:
                    imported_config = yaml.safe_load(f)
            else:
                click.echo(f"❌ Unsupported file format: {config_path.suffix}")
                click.echo("Supported formats: .json, .yaml, .yml")
                return
        except Exception as e:
            click.echo(f"❌ Error loading configuration file: {e}")
            return

        if not imported_config:
            click.echo("❌ Configuration file is empty or invalid.")
            return

        # Get current config
        current_config_path = Path.home() / ".aip" / "config.yaml"
        current_config = {}

        if current_config_path.exists() and not overwrite:
            try:
                import yaml

                with open(current_config_path) as f:
                    current_config = yaml.safe_load(f) or {}
            except Exception:
                current_config = {}

        # Merge configurations
        merged_config = {**current_config, **imported_config}

        # Save merged configuration
        current_config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            import yaml

            with open(current_config_path, "w") as f:
                yaml.dump(merged_config, f, default_flow_style=False)
            click.echo(f"✅ Configuration imported and saved to: {current_config_path}")
        except Exception as e:
            click.echo(f"❌ Error saving merged configuration: {e}")
            return

        # Display imported configuration
        click.echo("\n📥 Imported Configuration:")
        click.echo("=" * 30)

        for key, value in imported_config.items():
            if key == "api_key" and value:
                # Mask API key for display
                masked_value = (
                    value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                )
                click.echo(f"{key}: {masked_value}")
            else:
                click.echo(f"{key}: {value}")

        # Save to output file if specified
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                json.dump(merged_config, f, indent=2, default=str)
            click.echo(f"\n📄 Merged configuration saved to: {output_path}")

    except Exception as e:
        click.echo(f"❌ Error importing configuration: {e}")


@config_group.command()
@click.pass_context
def validate(ctx):
    """Validate current configuration."""
    try:
        # Get config from all sources
        config_path = Path.home() / ".aip" / "config.yaml"

        # Load file config
        file_config = {}
        if config_path.exists():
            try:
                import yaml

                with open(config_path) as f:
                    file_config = yaml.safe_load(f) or {}
            except Exception as e:
                click.echo(f"❌ Error loading config file: {e}")
                file_config = {}

        # Get environment config
        env_config = {
            "api_url": os.getenv("AIP_API_URL"),
            "api_key": os.getenv("AIP_API_KEY"),
            "timeout": os.getenv("AIP_TIMEOUT"),
        }

        # Combine configs (environment overrides file)
        combined_config = {**file_config, **env_config}

        # Remove None values
        combined_config = {k: v for k, v in combined_config.items() if v is not None}

        click.echo("🔍 Validating Configuration")
        click.echo("=" * 40)

        # Check required fields
        required_fields = ["api_url", "api_key"]
        missing_fields = []

        for field in required_fields:
            if field not in combined_config:
                missing_fields.append(field)
            else:
                click.echo(f"✅ {field}: Set")

        if missing_fields:
            click.echo(f"❌ Missing required fields: {', '.join(missing_fields)}")
            click.echo("\nTo set these values, use:")
            for field in missing_fields:
                if field == "api_url":
                    click.echo(f"  aip config set --{field} <your-api-url>")
                elif field == "api_key":
                    click.echo(f"  aip config set --{field} <your-api-key>")
            return

        # Validate API URL format
        api_url = combined_config["api_url"]
        if not api_url.startswith(("http://", "https://")):
            click.echo("⚠️  Warning: API URL should start with http:// or https://")

        # Validate timeout if present
        if "timeout" in combined_config:
            try:
                timeout = float(combined_config["timeout"])
                if timeout <= 0:
                    click.echo(f"❌ Timeout must be positive, got: {timeout}")
                    return
                click.echo(f"✅ timeout: {timeout} seconds")
            except ValueError:
                click.echo(f"❌ Invalid timeout value: {combined_config['timeout']}")
                return

        # Test connection if possible
        click.echo("\n🔌 Testing Connection...")
        try:
            client = Client(
                api_url=combined_config["api_url"],
                api_key=combined_config["api_key"],
                timeout=float(combined_config.get("timeout", 30.0)),
            )

            # Try to list resources to test connection
            try:
                agents = client.list_agents()
                click.echo(f"✅ Connection successful! Found {len(agents)} agents")
            except Exception as e:
                click.echo(f"⚠️  Connection established but API call failed: {e}")

            client.close()

        except Exception as e:
            click.echo(f"❌ Connection failed: {e}")
            return

        click.echo("\n🎉 Configuration is valid!")

    except Exception as e:
        click.echo(f"❌ Error validating configuration: {e}")


@config_group.command()
@click.pass_context
def init(ctx):
    """Initialize configuration interactively."""
    try:
        click.echo("🚀 AIP SDK Configuration Initialization")
        click.echo("=" * 50)
        click.echo("This will help you set up your AIP SDK configuration.")
        click.echo()

        # Get configuration values interactively
        api_url = click.prompt(
            "Enter your AIP API URL", default="https://api.aiagentplatform.com"
        )

        api_key = click.prompt("Enter your AIP API Key", hide_input=True)

        timeout = click.prompt(
            "Enter request timeout in seconds", default=30.0, type=float
        )

        # Confirm configuration
        click.echo("\n📋 Configuration Summary:")
        click.echo(f"  API URL: {api_url}")
        click.echo(
            f"  API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}"
        )
        click.echo(f"  Timeout: {timeout} seconds")

        if not click.confirm("\nIs this configuration correct?"):
            click.echo("Configuration cancelled.")
            return

        # Save configuration
        config_path = Path.home() / ".aip" / "config.yaml"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {"api_url": api_url, "api_key": api_key, "timeout": timeout}

        try:
            import yaml

            with open(config_path, "w") as f:
                yaml.dump(config_data, f, default_flow_style=False)
            click.echo(f"\n✅ Configuration saved to: {config_path}")
        except Exception as e:
            click.echo(f"❌ Error saving configuration: {e}")
            return

        # Test connection
        click.echo("\n🔌 Testing connection...")
        try:
            client = Client(api_url=api_url, api_key=api_key, timeout=timeout)
            agents = client.list_agents()
            click.echo(f"✅ Connection successful! Found {len(agents)} agents")
            client.close()
        except Exception as e:
            click.echo(f"⚠️  Configuration saved but connection test failed: {e}")
            click.echo(
                "You may need to check your API credentials or network connection."
            )

        click.echo("\n🎉 Configuration initialization complete!")
        click.echo("You can now use the AIP SDK CLI commands.")

    except Exception as e:
        click.echo(f"❌ Error during configuration initialization: {e}")
