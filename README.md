# Social Brain Memory

> A hackathon build for agents that remember people socially — not just semantically.

This repo started from **Honcho**, which is the original inspiration and infrastructure base for the project. Honcho showed that agent memory should be peer-centric, reasoning-first, and grounded in long-running representations. This hackathon project pushes that idea toward a more specific goal: a **social brain** for AI agents.

We are building memory that helps an agent understand people, relationships, beliefs, commitments, emotions, and perspectives over time. The target is not “better vector search.” The target is an agent that can walk into an ongoing social world and remember why people matter to each other.

We want to win the hackathon by demonstrating that social memory is the next frontier of useful agent memory.

## What We Are Building

Social Brain Memory turns conversations and events into structured social representations. It should help an agent answer questions like:

- Who is Alice close to, accountable to, avoiding, helping, or worried about?
- What does Alice believe Bob thinks?
- Which commitments did Alice make to Priya, and when should they matter again?
- What changed in a relationship since the last conversation?
- Which facts are objective, and which are only someone’s perspective?
- What context should an assistant remember before speaking to a person again?

The system is designed around the idea that a memory should carry **social meaning**:

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

The social-brain representation requirements live in:

- [`social-brain-1-representation.md`](./social-brain-1-representation.md)

That document is the product and implementation target for this hackathon branch. The documentation site also references it from:

- [`docs/v3/documentation/core-concepts/social-brain-representation.mdx`](./docs/v3/documentation/core-concepts/social-brain-representation.mdx)

## Why This Is Different From Normal Memory

Most memory systems store text and retrieve similar chunks. That helps with recall, but it does not build a social model.

A social brain needs to preserve:

1. **Attribution** — who said it, who it is about, and who observed it.
2. **Perspective** — whether something is objective or just someone’s belief/report.
3. **Relationships** — edges between people, agents, teams, projects, and organizations.
4. **Commitments** — promises, intentions, reminders, obligations, and plans.
5. **Change over time** — relationships and beliefs can strengthen, weaken, conflict, or become stale.
6. **Explainability** — conclusions should retain evidence and source messages.

Honcho’s peer model gives us a strong foundation: peers participate in sessions, messages are labeled by peer, and representations can be scoped by `(observer, observed)`. This project extends that foundation with social-memory metadata and social-brain extraction guidance.

## Current Implementation

This branch adds the first implementation slice of the social brain:

- Social-memory fields on explicit observations:
  - `social_category`
  - `subject`
  - `object`
  - `relation_type`
  - `confidence`
  - `perspective`
- Deriver prompt guidance for relationship, belief, trust, conflict, commitment, and theory-of-mind extraction.
- Persistence of social metadata into document metadata.
- Hydration of social metadata back into peer representations.
- Markdown rendering that surfaces social tags in representation output.
- Offline-safe token encoding so local demos do not fail when tokenizer assets are unavailable.

This is intentionally the first slice. It creates the representation substrate that future hackathon work can use for UI, demos, graph views, and richer reasoning.

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

## Architecture at a Glance

```text
Messages
  ↓
Deriver extracts explicit social observations
  ↓
Observations are stored as documents with social metadata
  ↓
Representations hydrate those observations by peer and perspective
  ↓
Chat, search, context, and demos recall the social model
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
