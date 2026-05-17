"""Import-time smoke tests.

These run without a real MongoDB cluster, without Vertex AI credentials, and
without spawning the `npx mongodb-mcp-server` subprocess. We patch the two
toolset factories so `_build_root_agent` returns a real ADK `Agent` whose
`tools` list is wired to harmless fakes.
"""

from __future__ import annotations

import os
import sys
from unittest import mock


def _reset_agent_module() -> None:
    """Drop cached imports so each test gets a fresh module state."""
    for mod in ("agent", "agent.agent"):
        sys.modules.pop(mod, None)


def test_import_does_not_require_connection_string(monkeypatch):
    """Importing the package must not raise even with no env vars set."""
    monkeypatch.delenv("MDB_MCP_CONNECTION_STRING", raising=False)
    monkeypatch.delenv("AGENT_SAFETY_MCP_URL", raising=False)
    _reset_agent_module()

    import agent  # noqa: F401

    # root_agent is lazy: the attribute exists on the package but isn't built yet.
    assert "root_agent" not in vars(agent)


def test_root_agent_shape_with_stubbed_env(monkeypatch):
    """`agent.root_agent` returns an ADK Agent with the expected wiring."""
    monkeypatch.setenv(
        "MDB_MCP_CONNECTION_STRING",
        "mongodb+srv://fake:fake@example.mongodb.net/?retryWrites=true",
    )
    monkeypatch.delenv("AGENT_SAFETY_MCP_URL", raising=False)
    _reset_agent_module()

    import agent.agent as agent_mod
    from google.adk.agents import Agent

    fake_mongo_toolset = mock.MagicMock(name="mongo_toolset")
    with mock.patch.object(agent_mod, "_mongo_toolset", return_value=fake_mongo_toolset):
        root = agent_mod.root_agent  # triggers lazy build via __getattr__

    assert isinstance(root, Agent)
    assert root.name == "movie_research_agent"
    assert root.model == os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-001")
    # Safety toolset not configured -> only the Mongo toolset is wired.
    assert list(root.tools) == [fake_mongo_toolset]
    # System prompt is non-trivial and grounded in our movie-research rules.
    assert "movie research agent" in root.instruction.lower()
    assert "sample_mflix" in root.instruction


def test_root_agent_attaches_safety_toolset_when_url_set(monkeypatch):
    """When AGENT_SAFETY_MCP_URL is set, both toolsets are wired in."""
    monkeypatch.setenv(
        "MDB_MCP_CONNECTION_STRING",
        "mongodb+srv://fake:fake@example.mongodb.net/?retryWrites=true",
    )
    monkeypatch.setenv("AGENT_SAFETY_MCP_URL", "https://example.invalid/mcp")
    _reset_agent_module()

    import agent.agent as agent_mod

    fake_mongo = mock.MagicMock(name="mongo_toolset")
    fake_safety = mock.MagicMock(name="safety_toolset")
    with mock.patch.object(agent_mod, "_mongo_toolset", return_value=fake_mongo), \
         mock.patch.object(agent_mod, "_safety_toolset", return_value=fake_safety):
        root = agent_mod.root_agent

    assert list(root.tools) == [fake_mongo, fake_safety]


def test_missing_connection_string_raises_at_build_time(monkeypatch):
    """Without MDB_MCP_CONNECTION_STRING, `_mongo_toolset` raises a clear error."""
    monkeypatch.delenv("MDB_MCP_CONNECTION_STRING", raising=False)
    _reset_agent_module()

    import agent.agent as agent_mod
    import pytest

    with pytest.raises(RuntimeError, match="MDB_MCP_CONNECTION_STRING"):
        agent_mod._mongo_toolset()
