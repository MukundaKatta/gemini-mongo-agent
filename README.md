# gemini-mongo-agent

A Gemini 2.0 Flash agent on Vertex AI that researches movies grounded in **MongoDB Atlas** via the official MongoDB MCP server, with an optional **agent-safety-mcp** guardrail layer for validation, egress, and trace diffs.

Built for the Google Cloud Rapid Agent Hackathon — MongoDB track.

## Architecture

```
+--------------+          +---------------------+
|   Browser    |  chat    |  ADK web UI on      |
|  (judge)     +--------->|  Cloud Run          |
+--------------+          +----------+----------+
                                     |
                                     | function-calling loop
                                     v
                          +----------+----------+
                          |  Gemini 2.0 Flash   |
                          |  on Vertex AI       |
                          +----------+----------+
                                     |
                  MCP stdio          |        MCP streamable-http
        +------------------+         |         +-----------------------+
        | MongoDB MCP      |<--------+-------->| agent-safety-mcp      |
        | (--readOnly)     |                   | (optional guardrails) |
        +--------+---------+                   +-----------------------+
                 |
                 | Atlas SRV URI
                 v
        +--------+---------+
        | MongoDB Atlas    |
        | sample_mflix     |
        +------------------+
```

- **Read-only** MongoDB access (`--readOnly`) so a misbehaving model can't write or drop collections.
- **Vector search** is available via the `$vectorSearch` aggregation stage if the Atlas index is configured.
- **Safety layer**: validate_args / check_egress / diff_snapshot live in a separate MCP service for layered defense.

## Local dev

Requires Python 3.11+ and Node 22+ (for `npx mongodb-mcp-server`).

```bash
pip install -e .
export MDB_MCP_CONNECTION_STRING='mongodb+srv://<user>:<pw>@<cluster>.mongodb.net/?retryWrites=true&w=majority'
export GOOGLE_GENAI_USE_VERTEXAI=TRUE
export GOOGLE_CLOUD_PROJECT=<your-project>
export GOOGLE_CLOUD_LOCATION=us-central1
# Optional: layer on the safety guardrails
export AGENT_SAFETY_MCP_URL=https://agent-safety-mcp-444075785245.us-central1.run.app/mcp

adk web .
```

Then open http://localhost:8000.

## Deploy to Cloud Run

```bash
adk deploy cloud_run --project="$GOOGLE_CLOUD_PROJECT" \
  --region=us-central1 --service_name=mongo-agent \
  --with_ui --allow_origins='*' .
```

Make sure the Cloud Run service has these env vars set:
- `GOOGLE_GENAI_USE_VERTEXAI=TRUE`
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`
- `MDB_MCP_CONNECTION_STRING`
- `AGENT_SAFETY_MCP_URL` (optional)

## What to ask it

Once deployed against the Atlas `sample_mflix` dataset, try:

- "Recommend three 1970s sci-fi movies with audience scores above 80."
- "What are the most-rated movies directed by Hayao Miyazaki in this dataset?"
- "Show me the top three comedies from the past decade by IMDB rating."

The agent will call `aggregate` / `find` / `count` MCP tools on the `sample_mflix.movies` collection and ground every recommendation in real database rows.

## Why this isn't an extension of pre-existing work

The Rapid Agent rules require projects to be newly created during the contest period, not modifications or extensions of earlier work. The agent in this repo is brand new: every Python file in `agent/` was written from scratch during the contest window, and the git history starts inside that window. The two MCP servers it talks to (`mongodb-mcp-server`, published by MongoDB under Apache-2.0, and `agent-safety-mcp`) are consumed strictly over their public MCP protocol interface. There is no fork, no vendored copy, and no source-level modification of either. They are runtime dependencies, in the same sense a Cloud Run service depends on Vertex AI or the npm registry. The novel contribution is the agent itself: the prompt, the tool wiring, the Cloud Run packaging, and the safety-layer composition.

## Tests

```bash
pip install -e . pytest
pytest
```

The import smoke tests in `tests/test_imports.py` exercise the agent wiring without requiring a real Atlas connection or Vertex AI credentials.

## Atlas setup

See [`scripts/setup-atlas.md`](scripts/setup-atlas.md) for a short click-through to create a free M0 cluster, load the `sample_mflix` sample dataset, and copy the SRV connection string.

## Demo video script

The 3-minute screen-recording walkthrough used for the hackathon submission lives at [`docs/video-script.md`](docs/video-script.md).

## License

Apache 2.0
