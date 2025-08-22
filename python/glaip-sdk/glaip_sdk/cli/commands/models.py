"""Language models commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import click
from rich.console import Console

from ..utils import get_client, output_flags, output_list

console = Console()


@click.group(name="models", no_args_is_help=True)
def models_group():
    """Language model operations."""
    pass


@models_group.command(name="list")
@output_flags()
@click.pass_context
def list_models(ctx):
    """List available language models."""
    try:
        client = get_client(ctx)
        models = client.list_language_models()

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("id", "ID", "dim", 36),
            ("provider", "Provider", "cyan", None),
            ("name", "Model", "green", None),
            ("base_url", "Base URL", "yellow", None),
        ]

        # Transform function for safe dictionary access
        def transform_model(model):
            return {
                "id": str(model.get("id", "N/A")),
                "provider": model.get("provider", "N/A"),
                "name": model.get("name", "N/A"),
                "base_url": model.get("base_url", "Default") or "Default",
            }

        output_list(
            ctx, models, "🧠 Available Language Models", columns, transform_model
        )

    except Exception as e:
        raise click.ClickException(str(e))
