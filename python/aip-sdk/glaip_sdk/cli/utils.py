"""CLI utilities for glaip-sdk.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import io
import json
import os
import platform
import shlex
import shutil
import subprocess
import tempfile
from typing import TYPE_CHECKING, Any

import click
from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table
from rich.text import Text

# Optional interactive deps (fuzzy palette)
try:
    from prompt_toolkit.completion import Completion
    from prompt_toolkit.shortcuts import prompt

    _HAS_PTK = True
except Exception:
    _HAS_PTK = False

try:
    import questionary
except Exception:
    questionary = None

if TYPE_CHECKING:
    from glaip_sdk import Client

console = Console()


# ----------------------------- Pager helpers ----------------------------- #


def _prepare_pager_env(clear_on_exit: bool = True) -> None:
    """
    Configure LESS flags for a predictable, high-quality UX:
      -R  : pass ANSI color escapes
      -S  : chop long lines (horizontal scroll with ←/→)
    (No -F, no -X) so we open a full-screen pager and clear on exit.
    Toggle wrapping with AIP_PAGER_WRAP=1 to drop -S.
    Power users can override via AIP_LESS_FLAGS.
    """
    os.environ.pop("LESSSECURE", None)
    if os.getenv("LESS") is None:
        want_wrap = os.getenv("AIP_PAGER_WRAP", "0") == "1"
        base = "-R" if want_wrap else "-RS"
        default_flags = base if clear_on_exit else (base + "FX")
        os.environ["LESS"] = os.getenv("AIP_LESS_FLAGS", default_flags)


def _render_ansi(renderable) -> str:
    """Render a Rich renderable to an ANSI string suitable for piping to 'less'."""
    buf = io.StringIO()
    tmp_console = Console(
        file=buf,
        force_terminal=True,
        color_system=console.color_system or "auto",
        width=console.size.width or 100,
        legacy_windows=False,
        soft_wrap=False,
        record=False,
    )
    tmp_console.print(renderable)
    return buf.getvalue()


def _pager_header() -> str:
    v = (os.getenv("AIP_PAGER_HEADER", "1") or "1").strip().lower()
    if v in {"0", "false", "off"}:
        return ""
    return "\n".join(
        [
            "TABLE VIEW — ↑/↓ PgUp/PgDn, ←/→ horiz scroll (with -S), /search, n/N next/prev, h help, q quit",
            "───────────────────────────────────────────────────────────────────────────────────────────────",
            "",
        ]
    )


def _page_with_system_pager(ansi_text: str) -> bool:
    """Prefer 'less' with a temp file so stdin remains the TTY."""
    if not (console.is_terminal and os.isatty(1)):
        return False
    if (os.getenv("TERM") or "").lower() == "dumb":
        return False

    pager_cmd = None
    pager_env = os.getenv("PAGER")
    if pager_env:
        parts = shlex.split(pager_env)
        if parts and os.path.basename(parts[0]).lower() == "less":
            pager_cmd = parts

    less_path = shutil.which("less")
    if pager_cmd or less_path:
        _prepare_pager_env(clear_on_exit=True)
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
            tmp.write(_pager_header())
            tmp.write(ansi_text)
            tmp_path = tmp.name
        try:
            if pager_cmd:
                subprocess.run([*pager_cmd, tmp_path], check=False)
            else:
                flags = os.getenv("LESS", "-RS").split()
                subprocess.run([less_path, *flags, tmp_path], check=False)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        return True

    # Windows 'more' is poor with ANSI; let Rich fallback handle it
    if platform.system().lower().startswith("win"):
        return False

    # POSIX 'more' fallback (may or may not honor ANSI)
    more_path = shutil.which("more")
    if more_path:
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
            tmp.write(_pager_header())
            tmp.write(ansi_text)
            tmp_path = tmp.name
        try:
            subprocess.run([more_path, tmp_path], check=False)
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        return True

    return False


def _get_view(ctx) -> str:
    obj = ctx.obj or {}
    return obj.get("view") or obj.get("format") or "rich"


# ----------------------------- Client config ----------------------------- #


def get_client(ctx) -> Client:
    """Get configured client from context, env, and config file (ctx > env > file)."""
    from glaip_sdk import Client
    from glaip_sdk.cli.commands.configure import load_config

    file_config = load_config() or {}
    context_config = (ctx.obj or {}) if ctx else {}

    env_config = {
        "api_url": os.getenv("AIP_API_URL"),
        "api_key": os.getenv("AIP_API_KEY"),
        "timeout": float(os.getenv("AIP_TIMEOUT", "0") or 0) or None,
    }
    env_config = {k: v for k, v in env_config.items() if v not in (None, "", 0)}

    config = {
        **file_config,
        **env_config,
        **{k: v for k, v in context_config.items() if v is not None},
    }

    if not config.get("api_url") or not config.get("api_key"):
        raise click.ClickException(
            "Missing api_url/api_key. Run `aip configure` or set AIP_* env vars."
        )

    return Client(
        api_url=config.get("api_url"),
        api_key=config.get("api_key"),
        timeout=float(config.get("timeout") or 30.0),
    )


# ----------------------------- Small helpers ----------------------------- #


def safe_getattr(obj: Any, attr: str, default: Any = None) -> Any:
    try:
        return getattr(obj, attr)
    except Exception:
        return default


# ----------------------------- Secret masking ---------------------------- #

_DEFAULT_MASK_FIELDS = {
    "api_key",
    "apikey",
    "token",
    "access_token",
    "secret",
    "client_secret",
    "password",
    "private_key",
    "bearer",
}


def _mask_value(v: Any) -> str:
    s = str(v)
    if len(s) <= 8:
        return "••••"
    return f"{s[:4]}••••••••{s[-4:]}"


def _mask_any(x: Any, mask_fields: set[str]) -> Any:
    """Recursively mask sensitive fields in any data structure.

    Args:
        x: The data to mask (dict, list, or primitive)
        mask_fields: Set of field names to mask (case-insensitive)

    Returns:
        Masked copy of the data with sensitive values replaced
    """
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if k.lower() in mask_fields and v is not None:
                out[k] = _mask_value(v)
            else:
                out[k] = _mask_any(v, mask_fields)
        return out
    elif isinstance(x, list):
        return [_mask_any(v, mask_fields) for v in x]
    else:
        return x


def _maybe_mask_row(row: dict[str, Any], mask_fields: set[str]) -> dict[str, Any]:
    """Mask a single row (legacy function, now uses _mask_any)."""
    if not mask_fields:
        return row
    return _mask_any(row, mask_fields)


def _resolve_mask_fields() -> set[str]:
    if os.getenv("AIP_MASK_OFF", "0") in ("1", "true", "on", "yes"):
        return set()
    env_fields = (os.getenv("AIP_MASK_FIELDS") or "").strip()
    if env_fields:
        parts = [p.strip().lower() for p in env_fields.split(",") if p.strip()]
        return set(parts)
    return set(_DEFAULT_MASK_FIELDS)


# ----------------------------- Fuzzy palette ----------------------------- #


def _row_display(row: dict[str, Any], columns: list[tuple]) -> str:
    """
    Build a compact text label for the palette.
    Prefers: name • type • framework • [id] (when available)
    Falls back to first 2 columns + [id].
    """
    name = str(row.get("name", "")).strip()
    _id = str(row.get("id", "")).strip()
    type_ = str(row.get("type", "")).strip()
    fw = str(row.get("framework", "")).strip()

    parts = []
    if name:
        parts.append(name)
    if type_:
        parts.append(type_)
    if fw:
        parts.append(fw)
    if not parts:
        # use first two visible columns
        for k, _hdr, _style, _w in columns[:2]:
            if k in ("id", "name", "type", "framework"):
                continue
            val = str(row.get(k, "")).strip()
            if val:
                parts.append(val)
            if len(parts) >= 2:
                break
    if _id:
        parts.append(f"[{_id}]")
    return " • ".join(parts) if parts else (_id or "(row)")


def _fuzzy_pick(
    rows: list[dict[str, Any]], columns: list[tuple], title: str
) -> dict[str, Any] | None:
    """
    Open a minimal fuzzy palette using prompt_toolkit.
    Returns the selected row (dict) or None if cancelled/missing deps.
    """
    if not (_HAS_PTK and console.is_terminal and os.isatty(1)):
        return None

    # Build display corpus and a reverse map
    labels = []
    by_label: dict[str, dict[str, Any]] = {}
    for r in rows:
        label = _row_display(r, columns)
        # Ensure uniqueness: if duplicate, suffix with …#n
        if label in by_label:
            i = 2
            base = label
            while f"{base} #{i}" in by_label:
                i += 1
            label = f"{base} #{i}"
        labels.append(label)
        by_label[label] = r

    # Create a fuzzy completer that searches anywhere in the string
    class FuzzyCompleter:
        def __init__(self, words: list[str]):
            self.words = words

        def get_completions(self, document, complete_event):
            word = document.get_word_before_cursor()
            if not word:
                return

            word_lower = word.lower()
            for label in self.words:
                label_lower = label.lower()
                # Check if all characters in the search word appear in order in the label
                if self._fuzzy_match(word_lower, label_lower):
                    yield Completion(label, start_position=-len(word))

        def _fuzzy_match(self, search: str, target: str) -> bool:
            """
            True fuzzy matching: checks if all characters in search appear in order in target.
            Examples:
            - "aws" matches "aws_calculator_agent" ✓
            - "calc" matches "aws_calculator_agent" ✓
            - "gent" matches "aws_calculator_agent" ✓
            - "agent" matches "aws_calculator_agent" ✓
            - "aws_calc" matches "aws_calculator_agent" ✓
            """
            if not search:
                return True

            search_idx = 0
            for char in target:
                if search_idx < len(search) and search[search_idx] == char:
                    search_idx += 1
                    if search_idx == len(search):
                        return True
            return False

    completer = FuzzyCompleter(labels)

    try:
        answer = prompt(
            message=f"Find {title.rstrip('s')}: ",
            completer=completer,
            complete_in_thread=True,
            complete_while_typing=True,
        )
    except (KeyboardInterrupt, EOFError):
        return None

    if not answer:
        return None

    # Exact label chosen from menu → direct hit
    if answer in by_label:
        return by_label[answer]

    # Fuzzy search fallback: find best fuzzy match
    best_match = None
    best_score = -1

    for label in labels:
        score = _fuzzy_score(answer.lower(), label.lower())
        if score > best_score:
            best_score = score
            best_match = label

    if best_match and best_score > 0:
        return by_label[best_match]

    # No match
    return None


def _fuzzy_score(search: str, target: str) -> int:
    """
    Calculate fuzzy match score.
    Higher score = better match.
    Returns -1 if no match possible.
    """
    if not search:
        return 0

    # Check if it's a fuzzy match first
    search_idx = 0
    for char in target:
        if search_idx < len(search) and search[search_idx] == char:
            search_idx += 1
            if search_idx == len(search):
                break

    if search_idx < len(search):
        return -1  # Not a fuzzy match

    # Calculate score based on:
    # 1. Exact substring match gets bonus points
    # 2. Consecutive character matches get bonus points
    # 3. Shorter search terms get bonus points

    score = 0

    # Exact substring bonus
    if search.lower() in target.lower():
        score += 100

    # Consecutive character bonus
    consecutive = 0
    max_consecutive = 0
    search_idx = 0
    for char in target:
        if search_idx < len(search) and search[search_idx] == char:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
            search_idx += 1
        else:
            consecutive = 0

    score += max_consecutive * 10

    # Length bonus (shorter searches get higher scores)
    score += (len(target) - len(search)) * 2

    return score


# ----------------------------- Pretty outputs ---------------------------- #


def output_result(
    ctx,
    result: Any,
    title: str = "Result",
    panel_title: str | None = None,
    success_message: str | None = None,
):
    fmt = _get_view(ctx)
    data = result.to_dict() if hasattr(result, "to_dict") else result

    # Apply recursive secret masking before any rendering
    mask_fields = _resolve_mask_fields()
    if mask_fields:
        try:
            data = _mask_any(data, mask_fields)
        except Exception:
            pass  # Continue with unmasked data if masking fails

    if fmt == "json":
        click.echo(json.dumps(data, indent=2, default=str))
        return

    if fmt == "plain":
        click.echo(str(data))
        return

    if fmt == "md":
        try:
            from rich.markdown import Markdown

            console.print(Markdown(str(data)))
        except ImportError:
            # Fallback to plain if markdown not available
            click.echo(str(data))
        return

    if success_message:
        console.print(f"[green]✅ {success_message}[/green]")

    if panel_title:
        console.print(Panel(Pretty(data), title=panel_title, border_style="blue"))
    else:
        console.print(f"[cyan]{title}:[/cyan]")
        console.print(Pretty(data))


# ----------------------------- List rendering ---------------------------- #

# Threshold no longer used - fuzzy palette is always default for TTY
# _PICK_THRESHOLD = int(os.getenv("AIP_PICK_THRESHOLD", "5") or "5")


def output_list(
    ctx,
    items: list[Any],
    title: str,
    columns: list[tuple],
    transform_func=None,
):
    """Display a list with fuzzy palette by default on TTY, Rich table as fallback."""
    fmt = _get_view(ctx)

    # Normalize rows
    try:
        rows: list[dict[str, Any]] = []
        for item in items:
            if transform_func:
                rows.append(transform_func(item))
            elif hasattr(item, "to_dict"):
                rows.append(item.to_dict())
            elif hasattr(item, "__dict__"):
                rows.append(vars(item))
            elif isinstance(item, dict):
                rows.append(item)
            else:
                rows.append({"value": item})
    except Exception:
        rows = []

    # JSON view bypasses any UI
    if fmt == "json":
        data = rows or [it.to_dict() if hasattr(it, "to_dict") else it for it in items]
        click.echo(json.dumps(data, indent=2, default=str))
        return

    # Plain view - simple text output
    if fmt == "plain":
        if not rows:
            click.echo(f"No {title.lower()} found.")
            return
        for row in rows:
            row_str = " | ".join(str(row.get(key, "N/A")) for key, _, _, _ in columns)
            click.echo(row_str)
        return

    # Markdown view - table format
    if fmt == "md":
        if not rows:
            click.echo(f"No {title.lower()} found.")
            return
        # Create markdown table
        headers = [header for _, header, _, _ in columns]
        click.echo(f"| {' | '.join(headers)} |")
        click.echo(f"| {' | '.join('---' for _ in headers)} |")
        for row in rows:
            row_str = " | ".join(str(row.get(key, "N/A")) for key, _, _, _ in columns)
            click.echo(f"| {row_str} |")
        return

    if not items:
        console.print(f"[yellow]No {title.lower()} found.[/yellow]")
        return

    # Sort by name by default (unless disabled)
    if (
        os.getenv("AIP_TABLE_NO_SORT", "0") not in ("1", "true", "on")
        and rows
        and isinstance(rows[0], dict)
        and "name" in rows[0]
    ):
        try:
            rows = sorted(rows, key=lambda r: str(r.get("name", "")).lower())
        except Exception:
            pass

    # Mask secrets
    mask_fields = _resolve_mask_fields()
    if mask_fields:
        try:
            rows = [_maybe_mask_row(r, mask_fields) for r in rows]
        except Exception:
            pass

    # === Fuzzy palette is the default for TTY lists ===
    picked: dict[str, Any] | None = None
    if console.is_terminal and os.isatty(1):
        picked = _fuzzy_pick(rows, columns, title)

    if picked:
        # Show a focused, single-row table (easy to copy ID/name)
        table = Table(title=title, box=box.ROUNDED, expand=True)
        for _key, header, style, width in columns:
            table.add_column(header, style=style, width=width)
        table.add_row(*[str(picked.get(key, "N/A")) for key, _, _, _ in columns])

        console.print(table)
        console.print(Text("\n[dim]Tip: use `aip agents get <ID>` for details[/dim]"))
        return

    # Build full table
    table = Table(title=title, box=box.ROUNDED, expand=True)
    for _key, header, style, width in columns:
        table.add_column(header, style=style, width=width)
    for row in rows:
        table.add_row(*[str(row.get(key, "N/A")) for key, _, _, _ in columns])

    footer = Text(f"\n[dim]Total {len(rows)} items[/dim]")
    content = Group(table, footer)

    # Auto paging when long
    is_tty = console.is_terminal and os.isatty(1)
    pager_env = (os.getenv("AIP_PAGER", "auto") or "auto").lower()

    if pager_env in ("0", "off", "false"):
        should_page = False
    elif pager_env in ("1", "on", "true"):
        should_page = is_tty
    else:
        try:
            term_h = console.size.height or 24
            approx_lines = 5 + len(rows)
            should_page = is_tty and (approx_lines >= term_h * 0.5)
        except Exception:
            should_page = is_tty

    if should_page:
        ansi = _render_ansi(content)
        if not _page_with_system_pager(ansi):
            with console.pager(styles=True):
                console.print(content)
        return

    console.print(content)


# ------------------------- Output flags decorator ------------------------ #


def _set_view(ctx, _param, value):
    if not value:
        return
    ctx.ensure_object(dict)
    ctx.obj["view"] = value


def _set_json(ctx, _param, value):
    if not value:
        return
    ctx.ensure_object(dict)
    ctx.obj["view"] = "json"


def output_flags():
    """Decorator to allow output format flags on any subcommand."""

    def decorator(f):
        f = click.option(
            "--json",
            "json_mode",
            is_flag=True,
            expose_value=False,
            help="Shortcut for --view json",
            callback=_set_json,
        )(f)
        f = click.option(
            "-o",
            "--output",
            "--view",
            "view_opt",
            type=click.Choice(["rich", "plain", "json", "md"]),
            expose_value=False,
            help="Output format",
            callback=_set_view,
        )(f)
        return f

    return decorator


# ------------------------- Ambiguity handling --------------------------- #


def handle_ambiguous_resource(
    ctx, resource_type: str, ref: str, matches: list[Any]
) -> Any:
    """Handle multiple resource matches gracefully."""
    if _get_view(ctx) == "json":
        return matches[0]

    if questionary and os.getenv("TERM") and os.isatty(0) and os.isatty(1):
        picked_idx = questionary.select(
            f"Multiple {resource_type.replace('{', '{{').replace('}', '}}')}s match '{ref.replace('{', '{{').replace('}', '}}')}'. Pick one:",
            choices=[
                questionary.Choice(
                    title=f"{getattr(m, 'name', '—').replace('{', '{{').replace('}', '}}')} — {getattr(m, 'id', '').replace('{', '{{').replace('}', '}}')}",
                    value=i,
                )
                for i, m in enumerate(matches)
            ],
            use_indicator=True,
            qmark="🧭",
            instruction="↑/↓ to select • Enter to confirm",
        ).ask()
        if picked_idx is None:
            raise click.ClickException("Selection cancelled")
        return matches[picked_idx]

    # Fallback numeric prompt
    console.print(
        f"[yellow]Multiple {resource_type.replace('{', '{{').replace('}', '}}')}s found matching '{ref.replace('{', '{{').replace('}', '}}')}':[/yellow]"
    )
    table = Table(
        title=f"Select {resource_type.replace('{', '{{').replace('}', '}}').title()}",
        box=box.ROUNDED,
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("ID", style="dim", width=36)
    table.add_column("Name", style="cyan")
    for i, m in enumerate(matches, 1):
        table.add_row(str(i), str(getattr(m, "id", "")), str(getattr(m, "name", "")))
    console.print(table)
    choice = click.prompt(
        f"Select {resource_type.replace('{', '{{').replace('}', '}}')} (1-{len(matches)})",
        type=int,
    )
    if 1 <= choice <= len(matches):
        return matches[choice - 1]
    raise click.ClickException("Invalid selection")
