# Social Brain Memory

> A hackathon build for agents that remember people socially — not just semantically.

This repo started from **Honcho**, which is the original inspiration and infrastructure base for the project. Honcho showed that agent memory should be peer-centric, reasoning-first, and grounded in long-running representations. This hackathon project pushes that idea toward a more specific goal: a **social brain** for AI agents.

**Honcho is social-memory infrastructure: it helps agents remember people, relationships, beliefs, commitments, preferences, and changing context over time.**

Instead of treating memory as a bag of retrieved chunks, Honcho turns conversations and events into structured social understanding. It tracks who said what, who believes what, how peers relate to one another, what commitments exist, and which facts are self-reported versus perspectival. Query those memories as peer representations, session context, search results, or natural-language insights from any model or framework. Use it managed at [api.honcho.dev](https://api.honcho.dev) or self-host the FastAPI server yourself.

Use Honcho when your product or agent needs durable social context: user preferences, team dynamics, assistant identity, theory-of-mind reasoning, relationship-aware personalization, and memory that becomes more useful as interactions accumulate.

Social Brain Memory turns conversations and events into structured social representations. It should help an agent answer questions like:

- Who is Alice close to, accountable to, avoiding, helping, or worried about?
- What does Alice believe Bob thinks?
- Which commitments did Alice make to Priya, and when should they matter again?
- What changed in a relationship since the last conversation?
- Which facts are objective, and which are only someone’s perspective?
- What context should an assistant remember before speaking to a person again?

- [Start Here](#start-here)
- [Why Social Memory](#why-social-memory)
- [The Social Memory Loop](#the-social-memory-loop)
- [Social Memory Model](#social-memory-model)
- [Quickstart](#quickstart)
- [What Social Memory Gives You](#what-social-memory-gives-you)
- [Integrations](#integrations)
- [Core Concepts](#core-concepts)
- [Benchmarks & Evals](#benchmarks--evals)
- [Self-hosting](#self-hosting)
- [Configuration](#configuration)
- [Architecture](#architecture)
- [SDKs](#sdks)
- [Learn More](#learn-more)
- [Contributing](#contributing)
- [License](#license)

| Memory type      | Example                                                       |
| ---------------- | ------------------------------------------------------------- |
| Identity         | “Alice is a product lead.”                                    |
| Preference       | “Alice prefers concise launch updates.”                       |
| Relationship     | “Bob is Alice’s manager.”                                     |
| Trust / affinity | “Alice trusts Bob with launch planning.”                      |
| Conflict         | “Alice is worried Dana may be upset with her.”                |
| Belief           | “Alice believes Dana may be upset after the review.”          |
| Commitment       | “Alice intends to send Priya the contract on Friday.”         |
| Perspective      | “Alice reported that Sam owns the decision.”                  |
| Group context    | “The launch team is coordinating around the Friday deadline.” |

## Requirements Document

| I want to...                                | Path                                                       | Get started                   |
| ------------------------------------------- | ---------------------------------------------------------- | ----------------------------- |
| Give my coding agent social memory          | Claude Code, OpenCode, OpenClaw, Hermes, or any MCP client | [Integrations](#integrations) |
| Add relationship-aware memory to my product | Python or TypeScript SDK                                   | [Quickstart](#quickstart)     |
| Self-host social-memory infrastructure      | Docker / local development                                 | [Self-hosting](#self-hosting) |

## Why Social Memory

Most agent memory systems remember _content_. Social agents need to remember _context_: who a person is, what they care about, what they promised, who else matters, what they believe about others, and how those facts change over time.

| Social-memory capability       | What it means                                                                                                                     |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| Relationship memory            | Stores relationship facts such as manager, teammate, friend, customer, mentor, trust, affinity, or conflict.                      |
| Perspective tracking           | Separates objective facts from perspectival facts like “Alice believes Bob is upset” or “Sam reported that Dana owns the launch.” |
| Commitments and intentions     | Captures promises, plans, goals, reminders, and obligations so agents can follow up later.                                        |
| Preference and identity memory | Maintains durable facts about how a person works, learns, communicates, decides, and identifies.                                  |
| Multi-peer theory of mind      | Models what one peer knows or believes about another when `observe_others` is configured.                                         |
| Reasoning-first recall         | Extracts conclusions from interactions instead of only retrieving similar text chunks.                                            |

## The Social Memory Loop

1. **Observe** conversations, events, documents, or tool traces as messages on a session.
2. **Extract social facts** — Honcho processes the queue in the background and derives explicit observations, including social-memory metadata such as category, subject, object, relation, confidence, and perspective.
3. **Consolidate** — background reasoning can reinforce, deduplicate, summarize, and generalize memories into peer representations and peer cards.
4. **Recall** — ask for a representation, session context, search results, or a natural-language answer grounded in long-term social context.
5. **Inject** — drop the recalled memory into any LLM call or agent framework.

Concretely: workspaces hold peers, peers participate in sessions, messages live on sessions, and Honcho builds observer/observed peer representations that you query through the [Chat Endpoint](https://honcho.dev/docs/v3/documentation/features/chat) or directly.

## Social Memory Model

Honcho represents social memory as conclusions about **peers**. A peer can be a human, agent, team, project, organization, or other entity your application needs to understand. The important distinction is perspective:

- **Self memory**: `observer == observed`, e.g. Alice’s own representation contains “Alice prefers concise status updates.”
- **Cross-peer memory**: `observer != observed`, e.g. an assistant’s representation of Alice contains “Alice trusts Bob with launch planning.”
- **Theory-of-mind memory**: a peer’s belief about another peer is preserved as a belief, not silently promoted to objective truth, e.g. “Alice believes Dana may be upset with her.”
- **Social metadata**: explicit observations can carry fields such as `social_category`, `subject`, `object`, `relation_type`, `confidence`, and `perspective` so relationship-aware products can filter and explain memory.

Typical social categories include identity, preference, relationship, emotion, intention, belief, commitment, role, trust, conflict, and group context.

A social brain needs to preserve:

1. **Attribution** — who said it, who it is about, and who observed it.
2. **Perspective** — whether something is objective or just someone’s belief/report.
3. **Relationships** — edges between people, agents, teams, projects, and organizations.
4. **Commitments** — promises, intentions, reminders, obligations, and plans.
5. **Change over time** — relationships and beliefs can strengthen, weaken, conflict, or become stale.
6. **Explainability** — conclusions should retain evidence and source messages.

Honcho’s peer model gives us a strong foundation: peers participate in sessions, messages are labeled by peer, and representations can be scoped by `(observer, observed)`. This project extends that foundation with social-memory metadata and social-brain extraction guidance.

```bash
pip install honcho-ai
# or: uv add honcho-ai
# or: poetry add honcho-ai
```

```python
import os
from honcho import Honcho

# Managed service uses api.honcho.dev by default. For self-hosted, pass
# base_url="http://localhost:8000" or set HONCHO_URL.
honcho = Honcho(
    workspace_id="my-app-testing",
    api_key=os.environ["HONCHO_API_KEY"],
)

# 1. Observe: peers and socially meaningful messages on a session
alice = honcho.peer("alice")
assistant = honcho.peer("assistant")
session = honcho.session("session-1")
session.add_messages([
    alice.message("Bob is my manager, and I trust him with launch planning."),
    alice.message("I think Dana may be upset with me after yesterday's review."),
    alice.message("Please remind me to send Priya the contract on Friday."),
])

# 2. Reason: happens asynchronously in the background. Honcho extracts
# relationship, belief, trust, and commitment memory while preserving perspective.

# 3. Recall: ask Honcho what social context matters, or pull prompt-ready context.
answer = alice.chat("What should my assistant remember about my work relationships?")
context = session.context(summary=True, tokens=10_000)

# 4. Inject: hand the context to your model of choice.
from openai import OpenAI
client = OpenAI()
completion = client.chat.completions.create(
    model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    messages=context.to_openai(assistant=assistant),
)
```

### TypeScript

```bash
npm install @honcho-ai/sdk
# or: bun add @honcho-ai/sdk
```

```typescript
import { Honcho } from "@honcho-ai/sdk";
import OpenAI from "openai";

const honcho = new Honcho({
  workspaceId: "my-app-testing",
  apiKey: process.env.HONCHO_API_KEY,
});

const alice = await honcho.peer("alice");
const assistant = await honcho.peer("assistant");
const session = await honcho.session("session-1");
await session.addMessages([
  alice.message("Bob is my manager, and I trust him with launch planning."),
  alice.message("I think Dana may be upset with me after yesterday's review."),
  alice.message("Please remind me to send Priya the contract on Friday."),
]);

const answer = await alice.chat(
  "What should my assistant remember about my work relationships?",
);
const context = await session.context({ summary: true, tokens: 10_000 });

const openai = new OpenAI();
const completion = await openai.chat.completions.create({
  model: process.env.OPENAI_MODEL ?? "gpt-4o-mini",
  messages: context.toOpenAI({ assistant }),
});
```

This branch adds the first implementation slice of the social brain:

## What Social Memory Gives You

| Social-memory need                           | API                                                             |
| -------------------------------------------- | --------------------------------------------------------------- |
| Save conversations and social events         | `session.add_messages(...)`                                     |
| Ask what Honcho knows about someone          | `peer.chat(...)`                                                |
| Retrieve a relationship-aware representation | `peer.representation(...)`, `session.representation(...)`       |
| Get prompt-ready social context              | `session.context(...).to_openai(...)` / `.to_anthropic(...)`    |
| Search memories and source messages          | `peer.search(...)`, `session.search(...)`, `honcho.search(...)` |
| Import docs, notes, or CRM-style records     | `session.upload_file(...)`                                      |
| Inspect background memory processing         | `honcho.queue_status(...)`                                      |

## Demo Story

A strong hackathon demo should make the social layer obvious.

Example interaction stream:

```text
Alice: Bob is my manager, and I trust him with launch planning.
Alice: I think Dana may be upset with me after yesterday's review.
Alice: Please remind me to send Priya the contract on Friday.
Bob: Alice owns the launch narrative, but Dana owns final approval.
Alice: If Dana is still annoyed, I want to apologize before the review meeting.
```

Expected social memory:

```text
- Bob is Alice's manager. [relationship]
- Alice trusts Bob with launch planning. [trust]
- Alice believes Dana may be upset with her after yesterday's review. [belief, low confidence, Alice's perspective]
- Alice intends to send Priya the contract on Friday. [commitment]
- Bob reported that Alice owns the launch narrative. [perspective]
- Bob reported that Dana owns final approval. [role, perspective]
- Alice wants to apologize to Dana before the review meeting if Dana is still annoyed. [intention, conflict repair]
```

The win condition is that an assistant can later respond with the right social context without being explicitly reminded:

```text
User: What should I do before the review meeting?
Assistant: You wanted to repair things with Dana before the review, and you were unsure whether she was upset after yesterday's review. It may be worth checking in or apologizing before the meeting. Also remember that Dana owns final approval, while Bob is your manager and someone you trust with launch planning.
```

Then invoke `/honcho-integration` in Claude Code (or `/honcho-dev:integrate` via the plugin marketplace). Details: [agentic development guide](https://honcho.dev/docs/v3/documentation/introduction/vibecoding).

### Other MCP clients

The same `claude mcp add` form (or its client-specific equivalent) works in any MCP-compatible client. See [MCP guide](https://honcho.dev/docs/v3/guides/integrations/mcp).

## Core Concepts

Honcho organises social memory around **peers** — humans and AI agents alike are first-class entities. The peer model enables:

- Multi-participant sessions with mixed human and AI agents
- Configurable observation settings (which peers observe which others)
- Flexible identity management for all participants
- Support for complex multi-agent interactions

Peers exchange messages within sessions; Honcho reasons over those messages to build a representation of each peer that you can query.

- **Workspace** (formerly App): top-level container; isolates data between use cases.
- **Peer** (formerly User): any participant — human user or AI agent.
- **Session**: a conversation context; many-to-many with peers.
- **Message**: an atomic data unit (peer-to-peer communication or ingested document chunk).

What you query out of Honcho:

- **Conclusions** — what Honcho has extracted about a peer, including social facts, deductive conclusions, and inductive patterns. Exposed via the [conclusions API](https://honcho.dev/docs/v3/api-reference/introduction).
- **Representations** — static, low-latency snapshots of what Honcho knows about a peer, including relationship and perspective-aware social context (optionally session-scoped).
- **Peer Cards** — compact identity summaries.
- **Session context / summaries** — prompt-ready bundles for long-running conversations.

<!-- markdownlint-disable MD033 -->
<details>
<summary>Internal storage (Collections &amp; Documents)</summary>

Internally, Honcho stores peer-related observations in **collections** of vector-embedded **documents**. Collections are keyed by `(observer, observed)` peer pairs — the same mechanism powers self-representation (`observer == observed`) and cross-peer modelling (peer X's understanding of peer Y). These primitives are not exposed directly; the Conclusions API is the public surface.

</details>
<!-- markdownlint-enable MD033 -->

<!-- TODO(vineeth/marketing): write the "Honcho vs RAG / vector DB / memory-only" comparison.
     Audit recommendation referenced; copy intentionally deferred to avoid inventing
     positioning claims unsupported by primary sources. -->

## Benchmarks &amp; Evals

Honcho's evals span LongMemEval, LoCoMo, and other long-conversation benchmarks. See the [evals page](https://honcho.dev/evals/), the [research blog post](https://blog.plasticlabs.ai/research/Benchmarking-Honcho), and the [Pareto-frontier announcement video](https://x.com/honchodotdev/status/2002090546521911703?s=20) for methodology and reproducible results.

## Self-hosting

Honcho is open source under AGPL-3.0. You can run the full server locally with Docker, then point the SDKs at `http://localhost:8000`.

### Quick start (Docker)

```bash
git clone https://github.com/plastic-labs/honcho.git
cd honcho
cp docker-compose.yml.example docker-compose.yml
cp .env.template .env       # fill in LLM_GEMINI_API_KEY / LLM_ANTHROPIC_API_KEY / LLM_OPENAI_API_KEY
docker compose up
```

The important modeling primitive remains the peer pair:

```text
(observer, observed)
```

That lets us represent different kinds of memory:

- `Alice → Alice`: Alice’s self-memory.
- `Assistant → Alice`: the assistant’s model of Alice.
- `Alice → Bob`: Alice’s model of Bob.
- `Bob → Alice`: Bob’s model of Alice.

This is the core of theory-of-mind memory: different observers can carry different representations of the same person.

## Quickstart for Hackathon Development

Install dependencies:

```bash
uv sync
```

Run checks for the social-memory slice:

```bash
.venv/bin/ruff check src/utils/tokens.py src/schemas/api.py src/utils/representation.py src/schemas/internal.py src/crud/representation.py src/deriver/prompts.py tests/deriver/test_representation_crud.py tests/deriver/test_deriver_prompts_social.py
.venv/bin/basedpyright src/utils/tokens.py src/schemas/api.py src/utils/representation.py src/schemas/internal.py src/crud/representation.py src/deriver/prompts.py tests/deriver/test_representation_crud.py tests/deriver/test_deriver_prompts_social.py
```

Run the app locally with the normal Honcho stack:

```bash
cp docker-compose.yml.example docker-compose.yml
cp .env.template .env
docker compose up
```

Or run services manually:

```bash
uv run alembic upgrade head
uv run fastapi dev src/main.py
uv run python -m src.deriver
```

## Build Priorities

To win the hackathon, prioritize visible social intelligence over generic platform polish.

1. **Great demo data** — conversations that clearly contain relationships, beliefs, and commitments.
2. **Social extraction quality** — observations must preserve perspective and avoid overclaiming.
3. **Recall experience** — the assistant should use social context naturally at the right moment.
4. **Explainability** — show source messages or reasoning for why the agent believes something.
5. **Visual social model** — if time permits, show relationship edges and confidence/perspective labels.

## Repository Map

Important files for this project:

| File                                                                                             | Purpose                                               |
| ------------------------------------------------------------------------------------------------ | ----------------------------------------------------- |
| [`social-brain-1-representation.md`](./social-brain-1-representation.md)                         | Hackathon requirements and representation target.     |
| [`src/deriver/prompts.py`](./src/deriver/prompts.py)                                             | Social-brain extraction prompt.                       |
| [`src/utils/representation.py`](./src/utils/representation.py)                                   | Observation and representation models.                |
| [`src/schemas/internal.py`](./src/schemas/internal.py)                                           | Document metadata schema for persisted social fields. |
| [`src/crud/representation.py`](./src/crud/representation.py)                                     | Persistence path for derived observations.            |
| [`tests/deriver/test_deriver_prompts_social.py`](./tests/deriver/test_deriver_prompts_social.py) | Prompt coverage for social-brain guidance.            |
| [`tests/deriver/test_representation_crud.py`](./tests/deriver/test_representation_crud.py)       | Representation conversion and metadata coverage.      |

## Honcho Credit

This project is inspired by and built from Honcho’s open-source memory infrastructure. Honcho’s core ideas — peers, sessions, messages, conclusions, representations, and observer/observed memory — are the reason this hackathon project can focus on the social-brain layer instead of rebuilding memory infrastructure from scratch.

## Hackathon North Star

Build the agent memory layer that makes judges say:

> “It remembered the social situation, not just the words.”

That is the product. That is the demo. That is how we win.
