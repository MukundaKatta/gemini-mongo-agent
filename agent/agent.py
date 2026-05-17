"""Gemini agent that researches movies grounded in MongoDB Atlas via MCP.

Architecture:
  - Gemini 2.0 Flash on Vertex AI is the planner / responder.
  - MongoDB MCP server (Apache-2.0, official) exposes find / aggregate / vectorSearch
    tools against the user's Atlas cluster.
  - agent-safety MCP server provides validate_args + check_egress + diff_snapshot
    so the agent's tool calls are sanity-checked before they hit the database.

Run locally with `adk web` in the project root.
Deploy with `adk deploy cloud_run --with_ui`.
"""

from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters


def _mongo_toolset() -> McpToolset:
    """Spawn the official MongoDB MCP server as a stdio subprocess."""
    conn = os.environ.get("MDB_MCP_CONNECTION_STRING")
    if not conn:
        raise RuntimeError(
            "MDB_MCP_CONNECTION_STRING is required. Set it to your Atlas SRV URI."
        )
    # --readOnly is critical for a demo agent: it removes insert/update/delete tools
    # from the MongoDB MCP surface so a misbehaving model can't write to your data.
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=["-y", "mongodb-mcp-server@latest", "--readOnly"],
                env={"MDB_MCP_CONNECTION_STRING": conn},
            ),
            timeout=30,
        ),
    )


def _safety_toolset() -> McpToolset | None:
    """Optionally attach the agent-safety-mcp HTTP endpoint for guardrails."""
    url = os.environ.get("AGENT_SAFETY_MCP_URL")
    if not url:
        return None
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=url),
    )


SYSTEM_PROMPT = """\
You are a careful movie research agent backed by the Atlas sample_mflix dataset.

You have read-only access to MongoDB via MCP tools. Before answering any
question, use the MCP tools to ground your response in real data. Cite the
movie title and year for every recommendation.

When you draft a complex aggregation, you may first ask the agent-safety
tools (if available) to validate the shape, then run it through MongoDB.
Never invent movies. If the database returns no results, say so.

Be brief. Pick three concrete recommendations max per question.\
"""


def _build_root_agent() -> Agent:
    tools = [_mongo_toolset()]
    safety = _safety_toolset()
    if safety is not None:
        tools.append(safety)
    return Agent(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-001"),
        name="movie_research_agent",
        instruction=SYSTEM_PROMPT,
        tools=tools,
    )


root_agent = _build_root_agent()
