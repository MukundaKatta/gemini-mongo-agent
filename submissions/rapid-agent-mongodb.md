# Google Cloud Rapid Agent — MongoDB Track submission

**Project name**: gemini-mongo-agent

**Tagline**: A Gemini 2.0 Flash agent that grounds every movie recommendation in MongoDB Atlas through the official MongoDB MCP server, with optional agent-safety guardrails.

**Track**: MongoDB

## What it does

The agent is a movie research assistant backed by MongoDB Atlas' `sample_mflix` dataset. Every question the user asks gets answered with real database rows, not invention. The agent decides which MongoDB tools to invoke (find / aggregate / count / list-collections) and Gemini renders the final answer with citations.

A second, optional MCP layer (`agent-safety-mcp`) is attached over Streamable HTTP. When configured, every tool call the agent emits can be validated and policy-checked before it reaches the database.

## How it uses Google Cloud + MongoDB

- **Vertex AI**: Gemini 2.0 Flash is the planner / responder. `GOOGLE_GENAI_USE_VERTEXAI=TRUE` routes through Vertex.
- **Google Cloud Agent Builder (ADK)**: the agent is wired with `google.adk.agents.Agent` + `McpToolset` + `StdioConnectionParams`. `adk deploy cloud_run --with_ui` produces a hosted chat URL judges can open and try.
- **MongoDB Atlas**: live data store. The agent connects through the official `mongodb-mcp-server` (Apache-2.0). `--readOnly` is enforced so the demo cannot accidentally write or drop collections.
- **MongoDB MCP**: 30+ tools — `find`, `aggregate`, `count`, `list-databases`, `list-collections`, `collection-indexes`, etc. Vector search supported via the `$vectorSearch` aggregation stage.

## Why MongoDB

MongoDB's flexible-schema document model maps naturally to messy real-world entities like movies (cast arrays, embedded ratings, denormalized genres). The `sample_mflix` dataset ships with `embedded_movies` for vector demos. The official MCP server means we get production-quality query primitives instead of bolting on a one-off DB adapter.

## What the agent will be asked

In the 3-min demo video:

1. "Recommend three 1970s sci-fi movies with audience scores above 80."
2. "What are the most-rated Hayao Miyazaki films in the dataset?"
3. "Show me the top three comedies from the past decade by IMDB rating."

The judge sees Gemini decide between MCP tools, run real aggregations against Atlas, and ground each recommendation in a returned document.

## Stack

- Google Cloud: **Vertex AI** (Gemini 2.0 Flash) + **Cloud Run** (hosted via `adk deploy cloud_run`)
- MongoDB: **Atlas** + **MongoDB MCP Server** v1+ (Apache-2.0)
- Python 3.12, google-adk 1.33, mcp 1.x
- Optional second MCP: agent-safety-mcp (validate_args / check_egress / diff_snapshot)

## Links

- Repo: https://github.com/MukundaKatta/gemini-mongo-agent
- Hosted demo URL: *<filled after Cloud Run deploy>*
- 3-min demo video: *<filled when recorded>*

## Originality

This project was newly created during the contest period. It does not modify any earlier project. It uses the official MongoDB MCP server (Apache-2.0) as a third-party dependency, and optionally the author's `agent-safety-mcp` HTTP service, also created within the contest period. No code from earlier projects is forked or embedded; both MCP services are accessed only via their public protocol interfaces.
