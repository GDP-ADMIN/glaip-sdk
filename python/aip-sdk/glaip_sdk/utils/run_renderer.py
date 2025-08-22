#!/usr/bin/env python3
"""Modern run renderer for agent execution with clean streaming output.

This module provides a modern CLI experience similar to Claude Code and Gemini CLI,
with compact headers, streaming markdown, collapsible tool steps, and clean output.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from time import monotonic
from typing import Any

from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text
from rich.tree import Tree

# Configure logger
logger = logging.getLogger("glaip_sdk.run_renderer")


def _pretty_args(d: dict | None, max_len: int = 80) -> str:
    if not d:
        return ""
    try:
        import json

        s = json.dumps(d, ensure_ascii=False)
    except Exception:
        s = str(d)
    return s if len(s) <= max_len else s[: max_len - 1] + "…"


def _pretty_out(s: str | None, max_len: int = 80) -> str:
    if not s:
        return ""
    s = s.strip().replace("\n", " ")
    # strip common LaTeX markers so collapsed lines are clean
    s = re.sub(r"\\\((.*?)\\\)", r"\1", s)
    s = re.sub(r"\\\[(.*?)\\\]", r"\1", s)
    s = re.sub(r"\\begin\{.*?\}|\\end\{.*?\}", "", s)
    return s if len(s) <= max_len else s[: max_len - 1] + "…"


@dataclass
class Step:
    step_id: str
    kind: str  # "tool" | "delegate" | "agent"
    name: str
    status: str = "running"
    args: dict = field(default_factory=dict)
    output: str = ""
    parent_id: str | None = None
    task_id: str | None = None
    context_id: str | None = None
    started_at: float = field(default_factory=monotonic)
    duration_ms: int | None = None

    def finish(self, duration_raw: float | None):
        if isinstance(duration_raw, int | float):
            self.duration_ms = int(duration_raw * 1000)
        else:
            self.duration_ms = int((monotonic() - self.started_at) * 1000)
        self.status = "finished"


class StepManager:
    def __init__(self, max_steps: int = 200):
        self.by_id: dict[str, Step] = {}
        self.order: list[str] = []  # top-level order
        self.children: dict[str, list[str]] = {}
        self.key_index: dict[
            tuple, str
        ] = {}  # (task_id, context_id, kind, name, slot) -> step_id
        self.slot_counter: dict[tuple, int] = {}
        self.max_steps = max_steps

    def _alloc_slot(self, task_id, context_id, kind, name) -> int:
        k = (task_id, context_id, kind, name)
        self.slot_counter[k] = self.slot_counter.get(k, 0) + 1
        return self.slot_counter[k]

    def _key(self, task_id, context_id, kind, name, slot) -> tuple:
        return (task_id, context_id, kind, name, slot)

    def _make_id(self, task_id, context_id, kind, name, slot) -> str:
        return f"{task_id or 't'}::{context_id or 'c'}::{kind}::{name}::{slot}"

    def start_or_get(
        self, *, task_id, context_id, kind, name, parent_id=None, args=None
    ) -> Step:
        slot = self._alloc_slot(task_id, context_id, kind, name)
        key = self._key(task_id, context_id, kind, name, slot)
        step_id = self._make_id(task_id, context_id, kind, name, slot)
        st = Step(
            step_id=step_id,
            kind=kind,
            name=name,
            parent_id=parent_id,
            task_id=task_id,
            context_id=context_id,
            args=args or {},
        )
        self.by_id[step_id] = st
        if parent_id:
            self.children.setdefault(parent_id, []).append(step_id)
        else:
            self.order.append(step_id)
        self.key_index[key] = step_id

        # Prune old steps if we exceed the limit
        self._prune_steps()

        return st

    def _prune_steps(self):
        """Remove oldest finished steps (and their children) to stay within max_steps limit."""
        # Count total (top-level + children)
        total = len(self.order) + sum(len(v) for v in self.children.values())
        if total <= self.max_steps:
            return

        while self.order and total > self.max_steps:
            oldest = self.order[0]
            st = self.by_id.get(oldest)
            if not st or st.status != "finished":
                # don't remove running/unknown steps
                break

            # remove oldest + its children
            self.order.pop(0)
            kids = self.children.pop(oldest, [])
            total -= 1 + len(kids)
            for cid in kids:
                self.by_id.pop(cid, None)
            self.by_id.pop(oldest, None)

    def get_child_count(self, step_id: str) -> int:
        """Get the number of child steps for a given step."""
        return len(self.children.get(step_id, []))

    def get_step_summary(self, step_id: str, verbose: bool = False) -> str:
        """Get a formatted summary of a step with child count information."""
        step = self.by_id.get(step_id)
        if not step:
            return "Unknown step"

        # Basic step info
        status = step.status
        duration = f"{step.duration_ms}ms" if step.duration_ms else "running"

        if verbose:
            # Verbose view: show full details
            summary = f"{step.name} → {status} [{duration}]"
            if step.args:
                summary += f" | Args: {_pretty_args(step.args)}"
            if step.output:
                summary += f" | Output: {_pretty_out(step.output)}"
        else:
            # Compact view: show child count if applicable
            child_count = self.get_child_count(step_id)
            if child_count > 0:
                summary = (
                    f"{step.name} → {status} [{duration}] ✓ ({child_count} sub-steps)"
                )
            else:
                summary = f"{step.name} → {status} [{duration}]"

        return summary

    def find_running(self, *, task_id, context_id, kind, name) -> Step | None:
        # Find the last started with same (task, context, kind, name) still running
        for sid in reversed(
            self.order + sum([self.children.get(k, []) for k in self.order], [])
        ):
            st = self.by_id[sid]
            if (st.task_id, st.context_id, st.kind, st.name) == (
                task_id,
                context_id,
                kind,
                name,
            ) and st.status != "finished":
                return st
        return None

    def finish(
        self, *, task_id, context_id, kind, name, output=None, duration_raw=None
    ):
        st = self.find_running(
            task_id=task_id, context_id=context_id, kind=kind, name=name
        )
        if not st:
            # if no running step, create and immediately finish
            st = self.start_or_get(
                task_id=task_id, context_id=context_id, kind=kind, name=name
            )
        if output:
            st.output = output
        st.finish(duration_raw)
        return st


@dataclass
class RunStats:
    """Statistics for agent run execution."""

    started_at: float = field(default_factory=monotonic)
    finished_at: float | None = None
    usage: dict[str, Any] = field(default_factory=dict)

    def stop(self) -> None:
        """Stop timing and record finish time."""
        self.finished_at = monotonic()

    @property
    def duration_s(self) -> float | None:
        """Get duration in seconds."""
        return (
            None
            if self.finished_at is None
            else round(self.finished_at - self.started_at, 2)
        )


class RichStreamRenderer:
    """
    Live, modern terminal view:
    - Compact header
    - Streaming Markdown for assistant content
    - Collapsed tool steps unless verbose=True
    """

    def __init__(
        self,
        console: Console,
        verbose: bool = False,
        theme: str | None = None,
        use_emoji: bool | None = None,
    ):
        # Allow environment variable overrides

        # Choose defaults first
        _theme = theme or os.getenv("AIP_THEME", "dark")
        _emoji = (
            use_emoji
            if use_emoji is not None
            else os.getenv("AIP_NO_EMOJI", "").lower() != "true"
        )
        _persist_live = (
            os.getenv("AIP_PERSIST_LIVE", "1") != "0"
        )  # default: keep live as final

        """Initialize the rich stream renderer."""
        self.console = console
        self.verbose = verbose
        self.theme = _theme
        self.use_emoji = _emoji
        self.persist_live = _persist_live
        self.buffer: list[str] = []  # accumulated assistant text chunks
        self.tools: list[dict[str, Any]] = []
        self.header_text = ""
        self.stats = RunStats()
        self._live: Live | None = None
        self.steps = StepManager()
        self.context_parent: dict[str, str] = {}  # child_context_id -> parent step_id
        self.root_context_id: str | None = (
            None  # Track root context for sub-agent routing
        )

        # sub-agent (child context) panels
        self.context_panels: dict[str, list[str]] = {}  # context_id -> list[str] chunks
        self.context_meta: dict[
            str, dict
        ] = {}  # context_id -> {"title","kind","status"}
        self.context_order: list[str] = []  # preserve creation order

        # tool panels keyed by StepManager step_id
        self.tool_panels: dict[
            str, dict
        ] = {}  # step_id -> {"title","status","chunks":[str]}
        self.tool_order: list[str] = []

        # header / status de-dup
        self._last_status: str | None = None
        self._last_header_rule: str | None = None
        self._header_rules_enabled = os.getenv("AIP_HEADER_STATUS_RULES", "0") == "1"
        self.show_delegate_tool_panels = (
            os.getenv("AIP_SHOW_DELEGATE_PANELS", "0") == "1"
        )

    def __del__(self):
        """Destructor to ensure Live is always stopped."""
        try:
            if hasattr(self, "_live") and self._live:
                self._live.stop()
        except Exception:
            pass  # Ignore cleanup errors during destruction

    def _print_header_once(self, text: str, style: str | None = None):
        """Print header only when changed to avoid duplicates."""
        if not self._header_rules_enabled:
            # don't draw rule; store the text so _main_title can still use name
            self._last_header_rule = text
            self.header_text = text
            return
        if text and text != self._last_header_rule:
            try:
                self.console.rule(text, style=style)
            except Exception:
                self.console.print(text)
            self._last_header_rule = text

    def _spinner(self) -> str:
        """Return animated spinner character."""
        frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        import time

        return frames[int(time.time() * 10) % len(frames)]

    def _has_running_steps(self) -> bool:
        """Check if any non-finished step is present."""
        for _sid, st in self.steps.by_id.items():
            if st.status != "finished":
                return True
        return False

    def _is_delegation_tool(self, tool_name: str) -> bool:
        """Check if a tool name indicates delegation functionality."""
        if not tool_name:
            return False
        # common patterns: delegate_to_math_specialist, delegate, spawn_agent, etc.
        return bool(re.search(r"(?:^|_)delegate(?:_|$)|^delegate_to_", tool_name, re.I))

    def _main_title(self) -> str:
        """Generate main panel title with spinner and status chips."""
        # base name
        name = (self.header_text or "").strip() or "Assistant"
        # strip leading rule emojis if present
        name = name.replace("—", " ").strip()
        # spinner if still working
        mark = "✓" if not self._has_running_steps() else self._spinner()
        # show a tiny hint if there's an active delegate
        active_delegates = sum(
            1
            for sid, st in self.steps.by_id.items()
            if st.kind == "delegate" and st.status != "finished"
        )
        chip = f" • delegating ({active_delegates})" if active_delegates else ""
        # show tools count for parity
        active_tools = sum(
            1
            for st in self.steps.by_id.values()
            if st.kind == "tool" and st.status != "finished"
        )
        chip2 = f" • tools ({active_tools})" if active_tools else ""
        return f"{name}  {mark}{chip}{chip2}"

    def _render_main_panel(self):
        """Render the main panel with content or placeholder."""
        body = "".join(self.buffer).strip()
        if body:
            return Panel(
                self._render_stream(),
                title=self._main_title(),
                border_style="green",
            )
        # fallback placeholder if no content yet
        placeholder = Text("working…", style="dim")
        if self._has_running_steps():
            placeholder = Text("working… running steps", style="dim")
        return Panel(
            placeholder,
            title=self._main_title(),
            border_style="green",
        )

    def _norm_markdown(self, s: str) -> str:
        """Reuse LaTeX normalization for panel bodies."""
        s = self._normalize_math(s)
        return s

    def _render_context_panels(self):
        """Render sub-agent panels."""
        panels = []
        for cid in self.context_order:
            chunks = self.context_panels.get(cid) or []
            meta = self.context_meta.get(cid) or {}
            title = meta.get("title") or f"Sub-agent {cid[:6]}…"
            status = meta.get("status") or "running"
            mark = "✓" if status == "finished" else self._spinner()
            body = self._norm_markdown("".join(chunks))
            panels.append(
                Panel(
                    Markdown(
                        body,
                        code_theme=("monokai" if self.theme == "dark" else "github"),
                    ),
                    title=f"{title}  {mark}",
                    border_style="magenta"
                    if meta.get("kind") == "delegate"
                    else "cyan",
                )
            )
        return panels

    def _render_tool_panels(self):
        """Render tool output panels."""
        panels = []
        for sid in self.tool_order:
            meta = self.tool_panels.get(sid) or {}
            title = meta.get("title") or "Tool"
            status = meta.get("status") or "running"
            mark = "✓" if status == "finished" else self._spinner()
            body = self._norm_markdown("".join(meta.get("chunks") or []))
            panels.append(
                Panel(
                    Markdown(
                        body,
                        code_theme=("monokai" if self.theme == "dark" else "github"),
                    ),
                    title=f"{title}  {mark}",
                    border_style="blue",
                )
            )
        return panels

    def _process_tool_output_for_sub_agents(
        self, tool_name: str, output: str, task_id: str, context_id: str
    ) -> bool:
        """Process tool output to extract and create sub-agent panels."""
        if not output:
            return False

        # Check if this is a delegation tool (contains sub-agent responses)
        if "delegate" in (tool_name or "").lower() or "math_specialist" in output:
            # Extract sub-agent name from output (e.g., "[math_specialist] ...")
            import re

            agent_match = re.search(r"^\s*\[([^\]]+)\]\s*(.*)$", output, re.S)
            if agent_match:
                agent_name = agent_match.group(1).strip()
                agent_content = agent_match.group(2).strip()

                # Create a unique context ID for this sub-agent response
                sub_context_id = f"{context_id}_sub_{agent_name}"

                # Create sub-agent panel if it doesn't exist
                if sub_context_id not in self.context_panels:
                    self.context_panels[sub_context_id] = []
                    self.context_meta[sub_context_id] = {
                        "title": f"Sub-Agent: {agent_name}",
                        "kind": "delegate",
                        "status": "finished",  # Already completed
                    }
                    self.context_order.append(sub_context_id)

                # Add the content to the sub-agent panel
                self.context_panels[sub_context_id].append(agent_content)

                # Mark as finished since it's already complete
                self.context_meta[sub_context_id]["status"] = "finished"
                return True
        return False

    def _render_tools(self):
        if not (self.steps.order or self.steps.children):
            return Text("")

        if not self.verbose:
            # collapsed: one line per top-level step (children are summarized)
            lines = []
            # Get terminal width for better spacing
            width = max(40, self.console.size.width - 8)
            args_budget = min(60, width // 3)

            for sid in self.steps.order:
                st = self.steps.by_id[sid]
                icon = (
                    "⚙️ "
                    if (self.use_emoji and st.kind == "tool")
                    else ("🤝 " if (self.use_emoji and st.kind == "delegate") else "")
                )
                dur = f"[{st.duration_ms}ms]" if st.duration_ms is not None else ""

                # Truncate args to fit budget
                args = _pretty_args(st.args, max_len=args_budget)
                rhs = f"({args})" if args else ""

                # Use spinner for running steps, checkmark for finished
                tail = " ✓" if st.status == "finished" else f" {self._spinner()}"
                lines.append(f"{icon}{st.name}{rhs} {dur}{tail}".rstrip())
            return Text("\n".join(lines), style="dim")

        # verbose: full tree
        def add_children(node: Tree, sid: str):
            st = self.steps.by_id[sid]
            dur = f"[{st.duration_ms}ms]" if st.duration_ms is not None else ""
            args_str = _pretty_args(st.args)
            icon = (
                "⚙️" if st.kind == "tool" else ("🤝" if st.kind == "delegate" else "🧠")
            )
            label = f"{icon} {st.name}"
            if args_str:
                label += f"({args_str})"
            label += f" {dur} {'✓' if st.status=='finished' else '…'}"
            node2 = node.add(label)
            for child_id in self.steps.children.get(sid, []):
                add_children(node2, child_id)

        root = Tree("Steps")
        for sid in self.steps.order:
            add_children(root, sid)
        return root

    def _normalize_math(self, md: str) -> str:
        """Robust LaTeX normalization for better display."""
        import re

        # \text{...} → plain
        md = re.sub(r"\\text\{([^}]*)\}", r"\1", md)

        # simple symbols
        md = md.replace(r"\times", "×").replace(r"\cdot", "·")

        # \boxed{...} → **...**
        md = re.sub(r"\\boxed\{([^}]*)\}", r"**\1**", md)

        # \begin{array}{...} ... \end{array} → code block
        def _array_to_block(m):
            body = m.group("body")
            # drop leading alignment spec {c@{}c@{}c} etc at start of body if present
            body = re.sub(r"^\{[^}]*\}\s*", "", body.strip())

            # split on LaTeX row separator \\ and replace alignment & with spacing
            rows = []
            for raw in re.split(r"\\\\", body):
                line = raw.strip()
                if not line:
                    continue
                # remove explicit + / bullets spacing issues and align with double-spaces
                line = line.replace("&", "  ")
                line = re.sub(r"\s{3,}", "  ", line)
                rows.append(line)

            return "```\n" + "\n".join(rows) + "\n```"

        md = re.sub(
            r"\\begin\{array\}\{[^}]*\}(?P<body>.*?)\\end\{array\}",
            _array_to_block,
            md,
            flags=re.S,
        )

        # Block math \[...\] → fenced code
        md = re.sub(r"\\\[(.*?)\\\]", r"```\n\1\n```", md, flags=re.S)

        # Inline math \(...\) → inline code
        md = re.sub(r"\\\((.*?)\\\)", r"`\1`", md, flags=re.S)

        # Strip any remaining begin/end environments harmlessly
        md = re.sub(r"\\begin\{[^}]*\}|\\end\{[^}]*\}", "", md)

        return md

    def _render_stream(self) -> Markdown:
        """Render the streaming markdown content."""
        content = "".join(self.buffer)
        content = self._normalize_math(content)
        code_theme = "monokai" if self.theme == "dark" else "github"
        return Markdown(content, code_theme=code_theme)

    def _ensure_live(self):
        """Ensure live area is started for any first event."""
        if self._live:
            return
        # Start live view without outer panel to fix double boxing
        self._live = Live(
            refresh_per_second=24,
            console=self.console,
            transient=not self.persist_live,  # Respect flag
            auto_refresh=True,
        )
        self._live.start()

    def _refresh(self) -> None:
        """Refresh the live display with stacked panels."""
        if not self._live:
            return

        panels = [self._render_main_panel()]  # Main assistant content

        # Only include Steps panel when there are actual steps
        if self.steps.order or self.steps.children:
            panels.append(
                Panel(
                    self._render_tools(),
                    title="Steps (collapsed)" if not self.verbose else "Steps",
                    border_style="blue",
                )
            )

        context_panels = self._render_context_panels()

        panels.extend(context_panels)  # Sub-agent panels
        panels.extend(self._render_tool_panels())  # tools

        self._live.update(Group(*panels))

    def _refresh_thread_safe(self) -> None:
        """Thread-safe refresh method for use from background threads."""
        if not self._live:
            return

        try:
            # Use console.call_from_thread for thread-safe updates
            self._live.console.call_from_thread(self._refresh)
        except Exception:
            # Fallback to direct call if call_from_thread fails
            try:
                self._refresh()
            except Exception:
                pass  # Ignore refresh errors

    def on_start(self, meta: dict[str, Any]) -> None:
        """Handle agent run start."""
        parts = []

        # Add emoji if enabled
        if self.use_emoji:
            parts.append("🤖")

        # Add agent name
        agent_name = meta.get("agent_name", "agent")
        if agent_name:
            parts.append(agent_name)

        # Add model if available
        model = meta.get("model", "")
        if model:
            parts.append("•")
            parts.append(model)

        # Add run ID if available
        run_id = meta.get("run_id", "")
        if run_id:
            parts.append("•")
            parts.append(run_id)

        self.header_text = " ".join(parts)

        # Show a compact header once (de-duplicated)
        self._print_header_once(self.header_text)

        # Show the original query for context
        query = meta.get("input_message") or meta.get("query") or meta.get("message")
        if query:
            from rich.markdown import Markdown

            self.console.print(
                Panel(
                    Markdown(f"**Query:** {query}"),
                    title="User Request",
                    border_style="yellow",
                    padding=(0, 1),
                )
            )

        # Don't start live display immediately - wait for actual content
        self._live = None

    def on_event(self, ev: dict[str, Any]) -> None:
        """Handle streaming events from the backend."""
        try:
            # Handle different event types based on backend's SSE format
            metadata = ev.get("metadata", {})
            kind = metadata.get("kind", "")

            if kind == "artifact":
                return  # Hidden by default

            # --- tool steps (collapsed) ---
            if kind == "agent_step":
                # Extract task and context IDs from metadata or direct fields
                task_id = ev.get("task_id") or metadata.get("task_id")
                context_id = ev.get("context_id") or metadata.get("context_id")

                status = metadata.get("status", "running")

                # Tool name + args + (optional) output
                tool_name = None
                tool_args = {}
                tool_out = None
                tc = ev.get("tool_calls")
                if isinstance(tc, list) and tc:
                    tool_name = (tc[0] or {}).get("name")
                    tool_args = (tc[0] or {}).get("args") or {}
                elif isinstance(tc, dict):
                    tool_name = tc.get("name")
                    tool_args = tc.get("args") or {}
                    tool_out = tc.get("output")

                # Heuristic: delegation events (sub-agent) signalled by message, or parent/child context ids
                message_en = ev.get("metadata", {}).get("message", {}).get("en", "")
                maybe_delegate = bool(
                    re.search(
                        r"\bdelegat(e|ion|ed)\b|\bspawn(ed)?\b|\bsub[- ]?agent\b",
                        message_en,
                        re.I,
                    )
                )
                child_ctx = ev.get("child_context_id") or ev.get("sub_context_id")

                # Parent mapping: if this step spawns a child context, remember who spawned it
                parent_id = None
                if maybe_delegate and child_ctx:
                    # start a delegate step at current context; child steps will hang under it
                    parent_step = self.steps.start_or_get(
                        task_id=task_id,
                        context_id=context_id,
                        kind="delegate",
                        name=ev.get("delegate_name")
                        or ev.get("agent_name")
                        or "delegate",
                        args={},
                    )
                    self.context_parent[child_ctx] = parent_step.step_id

                    # NEW: reserve a sub-agent panel immediately (spinner until content arrives)
                    title = (
                        ev.get("delegate_name")
                        or ev.get("agent_name")
                        or f"Sub-agent {child_ctx[:6]}…"
                    )
                    if child_ctx not in self.context_panels:
                        self.context_panels[child_ctx] = []
                        self.context_meta[child_ctx] = {
                            "title": f"Sub-Agent: {title}",
                            "kind": "delegate",
                            "status": "running",
                        }
                        self.context_order.append(child_ctx)

                    self._ensure_live()  # Ensure live for step-first runs
                    self._refresh()
                    return

                # Pick kind for this step
                kind_name = (
                    "tool" if tool_name else ("delegate" if maybe_delegate else "agent")
                )
                name = tool_name or (
                    ev.get("delegate_name") or ev.get("agent_name") or "step"
                )

                # Parent: if this event belongs to a child context, attach under its spawner
                parent_id = self.context_parent.get(context_id)

                # Determine if this is a running or finished step
                # If tool_calls is a list, it's starting; if it's a dict with output, it's finishing
                if isinstance(tc, list):
                    status = "running"
                elif isinstance(tc, dict) and tc.get("output"):
                    status = "finished"
                else:
                    status = status or ev.get("status") or "running"
                dur_raw = ev.get("metadata", {}).get("time")

                if status == "running":
                    st = self.steps.find_running(
                        task_id=task_id,
                        context_id=context_id,
                        kind=kind_name,
                        name=name,
                    )
                    if not st:
                        st = self.steps.start_or_get(
                            task_id=task_id,
                            context_id=context_id,
                            kind=kind_name,
                            name=name,
                            parent_id=parent_id,
                            args=tool_args,
                        )

                    # If it's a tool, ensure a tool panel exists and is running
                    if kind_name == "tool":
                        # Suppress tool panel for delegation tools unless explicitly enabled
                        if not (
                            self._is_delegation_tool(name)
                            and not self.show_delegate_tool_panels
                        ):
                            sid = st.step_id
                            if sid not in self.tool_panels:
                                self.tool_panels[sid] = {
                                    "title": f"Tool: {name}",
                                    "status": "running",
                                    "chunks": [],
                                }
                                self.tool_order.append(sid)
                else:
                    st = self.steps.finish(
                        task_id=task_id,
                        context_id=context_id,
                        kind=kind_name,
                        name=name,
                        output=tool_out,
                        duration_raw=dur_raw,
                    )

                    if kind_name == "tool":
                        sid = st.step_id

                        out = tool_out or ""
                        # First, see if this created a sub-agent panel
                        self._process_tool_output_for_sub_agents(
                            name, out, task_id, context_id
                        )

                        # If it's a delegation tool and we don't want its panel, suppress it
                        if (
                            self._is_delegation_tool(name)
                            and not self.show_delegate_tool_panels
                        ):
                            # If a running tool panel was accidentally created, remove it
                            if sid in self.tool_panels:
                                self.tool_panels.pop(sid, None)
                                try:
                                    self.tool_order.remove(sid)
                                except ValueError:
                                    pass
                            self._ensure_live()
                            self._refresh()
                            return

                        # Normal (non-delegation) tool panel behavior
                        panel = self.tool_panels.get(sid)
                        if not panel:
                            panel = {
                                "title": f"Tool: {name}",
                                "status": "running",
                                "chunks": [],
                            }
                            self.tool_panels[sid] = panel
                            self.tool_order.append(sid)

                        if bool(out) and (
                            (out.strip().startswith("{") and out.strip().endswith("}"))
                            or (
                                out.strip().startswith("[")
                                and out.strip().endswith("]")
                            )
                        ):
                            panel["chunks"].append("```json\n" + out + "\n```")
                        else:
                            panel["chunks"].append(out)

                        # trim for memory
                        if sum(len(x) for x in panel["chunks"]) > 20000:
                            joined = "".join(panel["chunks"])[-10000:]
                            panel["chunks"] = [joined]

                        panel["status"] = "finished"

                self._ensure_live()  # Ensure live for step-first runs
                self._refresh()
                return

            # --- status updates (backend sends status: "streaming_started", "execution_started", etc.) ---
            if "status" in ev and ev.get("metadata", {}).get("kind") != "agent_step":
                status_msg = ev.get("status", "")
                if status_msg in ("streaming_started", "execution_started"):
                    # These are informational status updates, no need to display
                    return
                self._last_status = status_msg  # keep it if you want chips later
                # no rule printing here; _main_title() already animates
                return

            # --- content streaming with boundary spacing ---
            if "content" in ev and ev["content"]:
                content = ev["content"]

                if "Artifact received:" in content:
                    return

                cid = ev.get("context_id") or metadata.get("context_id")

                # establish root context on first content
                if self.root_context_id is None and cid:
                    self.root_context_id = cid

                # sub-agent / child context streaming → stream into its own panel
                if cid and self.root_context_id and cid != self.root_context_id:
                    self._ensure_live()
                    if cid not in self.context_panels:
                        # Create the panel the first time we see content
                        title = (
                            ev.get("agent_name")
                            or ev.get("delegate_name")
                            or f"Sub-agent {cid[:6]}…"
                        )
                        self.context_panels[cid] = []
                        self.context_meta[cid] = {
                            "title": f"Sub-Agent: {title}",
                            "kind": "delegate",
                            "status": "running",
                        }
                        self.context_order.append(cid)

                    # append & trim (memory guard)
                    buf = self.context_panels[cid]
                    buf.append(content)
                    if sum(len(x) for x in buf) > 20000:
                        # keep last ~10k chars
                        joined = "".join(buf)[-10000:]
                        self.context_panels[cid] = [joined]

                    self._refresh()
                    return

                # root / unknown context → assistant
                self._ensure_live()  # Ensure live for content-first runs

                # insert a space at boundary when needed
                if (
                    self.buffer
                    and self.buffer[-1]
                    and self.buffer[-1][-1].isalnum()
                    and content
                    and content[0].isalnum()
                ):
                    self.buffer.append(" ")
                self.buffer.append(content)

                # Memory guard: trim main buffer if it gets too large
                joined = "".join(self.buffer)
                if len(joined) > 200_000:  # ~200KB
                    self.buffer = [joined[-100_000:]]  # keep last ~100KB

                self._refresh()
                return

            # final_response handled in on_complete
        except Exception as e:
            # Log the error and ensure Live is stopped to prevent terminal corruption
            logger.error(f"Error in event handler: {e}")
            try:
                if self._live:
                    self._live.stop()
            except Exception:
                pass  # Ignore cleanup errors
            raise  # Re-raise the original exception

    def on_complete(self, final: str, stats: RunStats) -> None:
        """Handle agent run completion."""
        try:
            # ensure final text is in buffer
            if final:
                whole = "".join(self.buffer)
                if not whole or final not in whole:
                    if (
                        self.buffer
                        and self.buffer[-1]
                        and self.buffer[-1][-1].isalnum()
                        and final
                        and final[0].isalnum()
                    ):
                        self.buffer.append(" ")
                    self.buffer.append(final)

            # Mark all sub-agent panels as finished
            for cid in list(self.context_meta.keys()):
                self.context_meta[cid]["status"] = "finished"

            # make sure live exists for a clean last frame
            if self._live is None:
                self._ensure_live()

            # update both panels one last time
            self._refresh()

            # print footer (works with both transient & persistent)
            footer = []
            if stats.duration_s is not None:
                footer.append(f"✓ Done in {stats.duration_s}s")
            u = stats.usage or {}
            if u.get("input_tokens") or u.get("output_tokens"):
                footer.append(
                    f"{u.get('input_tokens',0)} tok in / {u.get('output_tokens',0)} tok out"
                )
            if u.get("cost"):
                footer.append(f"${u['cost']}")
            if footer:
                self.console.print(Text(" • ".join(footer), style="bold green"))
        finally:
            # Always ensure Live is stopped, even if an exception occurs
            try:
                if self._live:
                    self._live.stop()
            except Exception:
                pass  # Ignore errors during cleanup
