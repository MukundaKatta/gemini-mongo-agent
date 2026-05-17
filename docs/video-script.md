# 3-minute demo video script

For Google Cloud Rapid Agent Hackathon, MongoDB track. Target length 2:50 to 3:00.

Screen layout: browser window with the deployed Cloud Run URL on the left, agent trace / function-call panel visible on the right (ADK web UI shows both by default).

---

## 0:00 to 0:20: Open

**Voiceover:**

> "This is gemini-mongo-agent. It's a Gemini 2.0 Flash agent on Vertex AI that answers movie questions by querying a real MongoDB Atlas database through the official MongoDB MCP server. I'm opening the hosted Cloud Run URL right now."

**Action:** click the bookmark for the Cloud Run URL. Wait for the chat UI to load. Point cursor at the URL bar so judges see it's a public hosted endpoint.

---

## 0:20 to 1:10: Question 1: simple find

**Voiceover:**

> "First question. I want three 1970s sci-fi movies with audience scores above 80."

**Action:** type into the chat box:

> Recommend three 1970s sci-fi movies with audience scores above 80.

Hit send. While the agent is thinking, switch to the trace panel.

**Voiceover (over the trace panel):**

> "On the right you can see Gemini decide to call the MongoDB MCP `aggregate` tool against `sample_mflix.movies`. The filter checks `year` between 1970 and 1979, `genres` includes Sci-Fi, `tomatoes.viewer.rating` above 80. That's a real query against my Atlas cluster, not a hallucination."

When the answer renders, read the titles aloud: "Star Wars, 1977. Alien, 1979. Close Encounters, 1977. Each cited with year."

---

## 1:10 to 1:55: Question 2: aggregation

**Voiceover:**

> "Second question, a heavier aggregation. Most-rated Hayao Miyazaki films in the dataset."

**Action:** type:

> What are the most-rated Hayao Miyazaki films in the dataset?

Hit send. Switch to trace panel.

**Voiceover:**

> "Gemini is now building a multi-stage pipeline: match on director equals Miyazaki, sort by `imdb.votes` descending, limit three. The MongoDB MCP server runs it on Atlas and returns the raw documents. Gemini summarizes them with title and year only. No invention. If the database had returned zero rows, the agent is instructed to say so."

---

## 1:55 to 2:35: Question 3: recent comedies + safety layer

**Voiceover:**

> "Third question. Top three comedies from the past decade by IMDB rating."

**Action:** type the question. Hit send.

**Voiceover (over trace panel):**

> "Watch the tool-call list. Notice the `validate_args` call before the `aggregate` call. That's the agent-safety MCP server, a separate Streamable HTTP MCP I attached. It sanity-checks the aggregation pipeline before it touches the database. Two MCPs, layered: MongoDB for data, agent-safety for guardrails. The agent itself doesn't have to trust the model's output blindly."

---

## 2:35 to 3:00: Close

**Voiceover:**

> "Stack recap. Vertex AI Gemini 2.0 Flash as the brain. Google Cloud Agent Development Kit for tool routing. The agent is deployed on Cloud Run with `adk deploy cloud_run`. MongoDB Atlas with the official Apache-licensed MCP server in `--readOnly` mode for data. The agent-safety MCP for an extra validation layer. Code on GitHub, link in the description. Thanks for watching."

**Action:** show the GitHub repo URL on screen for the last three seconds.
