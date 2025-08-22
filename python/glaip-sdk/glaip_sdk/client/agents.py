#!/usr/bin/env python3
"""Agent client for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
import logging
import sys
from typing import Any, BinaryIO

import httpx
from rich.console import Console

from glaip_sdk.client.base import BaseClient
from glaip_sdk.models import Agent
from glaip_sdk.utils.run_renderer import (
    RichStreamRenderer,
)

# Set up module-level logger
logger = logging.getLogger("glaip_sdk.agents")


def _select_renderer(
    renderer: RichStreamRenderer | str | None, *, verbose: bool = False
) -> RichStreamRenderer:
    """Select the appropriate renderer based on input."""
    if isinstance(renderer, RichStreamRenderer):
        return renderer

    console = Console(file=sys.stdout, force_terminal=sys.stdout.isatty())

    if renderer in (None, "auto"):
        return RichStreamRenderer(console=console, verbose=verbose)
    if renderer == "json":
        # JSON output is handled by the renderer itself
        return RichStreamRenderer(console=console, verbose=verbose)
    if renderer == "markdown":
        # Markdown output is handled by the renderer itself
        return RichStreamRenderer(console=console, verbose=verbose)
    if renderer == "plain":
        # Plain output is handled by the renderer itself
        return RichStreamRenderer(console=console, verbose=verbose)

    raise ValueError(f"Unknown renderer: {renderer}")


class AgentClient(BaseClient):
    """Client for agent operations."""

    def __init__(self, *, parent_client: BaseClient | None = None, **kwargs):
        """Initialize the agent client.

        Args:
            parent_client: Parent client to adopt session/config from
            **kwargs: Additional arguments for standalone initialization
        """
        super().__init__(parent_client=parent_client, **kwargs)

    def _extract_ids(self, items: list[str | Any] | None) -> list[str] | None:
        """Extract IDs from a list of objects or strings."""
        if not items:
            return None

        ids = []
        for item in items:
            if isinstance(item, str):
                ids.append(item)
            elif hasattr(item, "id"):
                ids.append(item.id)
            else:
                # Fallback: convert to string
                ids.append(str(item))

        return ids

    def list_agents(self) -> list[Agent]:
        """List all agents."""
        data = self._request("GET", "/agents/")
        return [Agent(**agent_data)._set_client(self) for agent_data in (data or [])]

    def get_agent_by_id(self, agent_id: str) -> Agent:
        """Get agent by ID."""
        data = self._request("GET", f"/agents/{agent_id}")
        return Agent(**data)._set_client(self)

    def find_agents(self, name: str | None = None) -> list[Agent]:
        """Find agents by name."""
        params = {}
        if name:
            params["name"] = name

        data = self._request("GET", "/agents/", params=params)
        return [Agent(**agent_data)._set_client(self) for agent_data in (data or [])]

    def create_agent(
        self,
        name: str,
        instruction: str,
        model: str = "gpt-4.1",
        tools: list[str | Any] | None = None,
        agents: list[str | Any] | None = None,
        timeout: int = 300,
        **kwargs,
    ) -> "Agent":
        """Create a new agent."""
        # Client-side validation
        if not name or not name.strip():
            raise ValueError("Agent name cannot be empty or whitespace")

        if not instruction or not instruction.strip():
            raise ValueError("Agent instruction cannot be empty or whitespace")

        if len(instruction.strip()) < 10:
            raise ValueError("Agent instruction must be at least 10 characters long")

        # Prepare the creation payload
        payload = {
            "name": name.strip(),
            "instruction": instruction.strip(),
            "type": "config",
            "framework": "langchain",
            "version": "1.0",
            "provider": "openai",
            "model_name": model or "gpt-4.1",  # Ensure model_name is never None
        }

        # Extract IDs from tool and agent objects
        tool_ids = self._extract_ids(tools)
        agent_ids = self._extract_ids(agents)

        # Add tools and agents if provided
        if tool_ids:
            payload["tools"] = tool_ids
        if agent_ids:
            payload["agents"] = agent_ids

        # Add any additional kwargs
        payload.update(kwargs)

        # Create the agent
        data = self._request("POST", "/agents/", json=payload)

        # The backend only returns the ID, so we need to fetch the full agent details
        agent_id = data.get("id")
        if not agent_id:
            raise ValueError("Backend did not return agent ID")

        # Fetch the full agent details
        full_agent_data = self._request("GET", f"/agents/{agent_id}")
        return Agent(**full_agent_data)._set_client(self)

    def update_agent(
        self,
        agent_id: str,
        name: str | None = None,
        instruction: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> "Agent":
        """Update an existing agent."""
        # First, get the current agent data
        current_agent = self.get_agent_by_id(agent_id)

        # Prepare the update payload with current values as defaults
        update_data = {
            "name": name if name is not None else current_agent.name,
            "instruction": instruction
            if instruction is not None
            else current_agent.instruction,
            "type": "config",  # Required by backend
            "framework": "langchain",  # Required by backend
            "version": "1.0",  # Required by backend
        }

        # Handle model specification
        if model is not None:
            update_data["provider"] = "openai"  # Default provider
            update_data["model_name"] = model
        else:
            # Use current model if available
            if hasattr(current_agent, "agent_config") and current_agent.agent_config:
                if "lm_provider" in current_agent.agent_config:
                    update_data["provider"] = current_agent.agent_config["lm_provider"]
                if "lm_name" in current_agent.agent_config:
                    update_data["model_name"] = current_agent.agent_config["lm_name"]
            else:
                # Default values
                update_data["provider"] = "openai"
                update_data["model_name"] = "gpt-4.1"

        # Handle tools and agents
        if "tools" in kwargs:
            tool_ids = self._extract_ids(kwargs["tools"])
            if tool_ids:
                update_data["tools"] = tool_ids
        elif current_agent.tools:
            update_data["tools"] = [
                tool["id"] if isinstance(tool, dict) else tool
                for tool in current_agent.tools
            ]

        if "agents" in kwargs:
            agent_ids = self._extract_ids(kwargs["agents"])
            if agent_ids:
                update_data["agents"] = agent_ids
        elif current_agent.agents:
            update_data["agents"] = [
                agent["id"] if isinstance(agent, dict) else agent
                for agent in current_agent.agents
            ]

        # Add any other kwargs
        for key, value in kwargs.items():
            if key not in ["tools", "agents"]:
                update_data[key] = value

        # Send the complete payload
        data = self._request("PUT", f"/agents/{agent_id}", json=update_data)
        return Agent(**data)._set_client(self)

    def delete_agent(self, agent_id: str) -> None:
        """Delete an agent."""
        self._request("DELETE", f"/agents/{agent_id}")

    def run_agent(
        self,
        agent_id: str,
        message: str,
        files: list[str | BinaryIO] | None = None,
        tty: bool = False,
        stream: bool = True,
        *,
        renderer: RichStreamRenderer | str | None = "auto",
        verbose: bool = False,
        **kwargs,
    ) -> str:
        """Run an agent with a message, streaming via a renderer."""
        # Prepare multipart data if files are provided
        form_data = None
        headers = {}

        if files:
            form_data = self._prepare_multipart_data(message, files)
            headers["Content-Type"] = "multipart/form-data"
            payload = None
        else:
            payload = {"input": message, **kwargs}
            if tty:
                payload["tty"] = True
            if not stream:
                payload["stream"] = False

        # Choose renderer (even if stream=False, we can still format final)
        r = _select_renderer(renderer, verbose=verbose)

        # Try to set some meta early; refine as we receive events
        meta = {
            "agent_name": kwargs.get("agent_name", agent_id),
            "model": kwargs.get("model"),
            "run_id": None,
            "input_message": message,  # Add the original query for context
        }
        r.on_start(meta)

        final_text = ""
        stats_usage = {}
        started_monotonic = None
        finished_monotonic = None

        with self.http_client.stream(
            "POST",
            f"/agents/{agent_id}/run",
            json=payload if not files else None,
            data=form_data.get("data") if files else None,
            files=form_data.get("files") if files else None,
            headers=headers,
        ) as response:
            response.raise_for_status()

            # capture request id if provided
            req_id = response.headers.get("x-request-id") or response.headers.get(
                "x-run-id"
            )
            if req_id:
                meta["run_id"] = req_id
                r.on_start(meta)  # refresh header with run_id

            for event in self._iter_sse_events(response):
                try:
                    ev = json.loads(event["data"])
                except json.JSONDecodeError:
                    logger.debug("Non-JSON SSE fragment skipped")
                    continue

                # Start timer at first meaningful event
                if started_monotonic is None and (
                    "content" in ev or "status" in ev or ev.get("metadata")
                ):
                    from time import monotonic

                    started_monotonic = monotonic()

                kind = (ev.get("metadata") or {}).get("kind")

                # Hide "artifact" chatter
                if kind == "artifact":
                    continue

                # Accumulate assistant content, but do not print here
                if "content" in ev and ev["content"]:
                    # Filter weird backend text like "Artifact received: ..."
                    if not ev["content"].startswith("Artifact received:"):
                        final_text = ev["content"]  # replace with latest
                    r.on_event(ev)
                    continue

                # Step / tool events
                if kind == "agent_step":
                    r.on_event(ev)
                    continue

                # Statuses: forward to renderer (it decides to collapse)
                if "status" in ev:
                    r.on_event(ev)
                    continue

                # Usage/cost event (if your backend emits it)
                if kind == "usage":
                    stats_usage.update(ev.get("usage") or {})
                    continue

                # Model/run info (if emitted mid-stream)
                if kind == "run_info":
                    if ev.get("model"):
                        meta["model"] = ev["model"]
                        r.on_start(meta)
                    if ev.get("run_id"):
                        meta["run_id"] = ev["run_id"]
                        r.on_start(meta)

            from time import monotonic

            finished_monotonic = monotonic()

        # Finalize stats
        from glaip_sdk.utils.run_renderer import RunStats

        st = RunStats()
        st.started_at = started_monotonic or st.started_at
        st.finished_at = finished_monotonic or st.started_at
        st.usage = stats_usage

        r.on_complete(final_text or "No response content received.", st)
        return final_text or "No response content received."

    def _iter_sse_events(self, response: httpx.Response):
        """Iterate over Server-Sent Events with proper parsing."""
        buf = []
        event_type = None
        event_id = None

        for raw in response.iter_lines():
            line = raw.decode("utf-8") if isinstance(raw, bytes) else raw

            if line == "":
                if buf:
                    data = "\n".join(buf)
                    yield {
                        "event": event_type or "message",
                        "id": event_id,
                        "data": data,
                    }
                    buf, event_type, event_id = [], None, None
                continue

            if line.startswith(":"):  # comment
                continue
            if line.startswith("data:"):
                buf.append(line[5:].lstrip())
            elif line.startswith("event:"):
                event_type = line[6:].strip() or None
            elif line.startswith("id:"):
                event_id = line[3:].strip() or None

        # Flush any remaining data
        if buf:
            yield {
                "event": event_type or "message",
                "id": event_id,
                "data": "\n".join(buf),
            }

    def _prepare_multipart_data(
        self, message: str, files: list[str | BinaryIO]
    ) -> dict[str, Any]:
        """Prepare multipart form data for file uploads."""
        from pathlib import Path

        form_data = {"data": {"message": message}}
        file_list = []

        for file_item in files:
            if isinstance(file_item, str):
                # File path - let httpx stream the file handle
                file_path = Path(file_item)
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {file_item}")

                file_list.append(
                    (
                        "files",
                        (
                            file_path.name,
                            open(file_path, "rb"),
                            "application/octet-stream",
                        ),
                    )
                )
            else:
                # File-like object
                if hasattr(file_item, "name"):
                    filename = getattr(file_item, "name", "file")
                else:
                    filename = "file"

                if hasattr(file_item, "read"):
                    # For file-like objects, we need to read them since httpx expects bytes
                    file_content = file_item.read()
                    file_list.append(
                        ("files", (filename, file_content, "application/octet-stream"))
                    )
                else:
                    raise ValueError(f"Invalid file object: {file_item}")

        if file_list:
            form_data["files"] = file_list

        return form_data
