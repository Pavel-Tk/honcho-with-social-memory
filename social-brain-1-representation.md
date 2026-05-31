# Social Brain 1: Representation

This document defines the hackathon target for the first Social Brain milestone: a representation layer for social memory.

The goal is to extend Honcho-inspired agent memory from “facts about a user” into “structured understanding of a social world.” Agents should remember people, relationships, beliefs, commitments, roles, conflicts, and perspectives with enough fidelity to act appropriately later.

## Product Goal

Build a memory representation that lets an AI agent answer:

- Who matters to this person?
- How are those people related?
- What does this person believe about others?
- What commitments, intentions, or obligations are active?
- What social tensions or trust relationships should the agent respect?
- Which memories are objective facts, and which are only someone’s report or belief?

## Representation Principles

### 1. Preserve perspective

Do not turn a person’s belief into objective truth.

Good:

```text
Alice believes Dana may be upset with her.
```

Bad:

```text
Dana is upset with Alice.
```

Unless Dana directly says she is upset or the system has strong evidence, the memory must remain attributed to Alice’s perspective.

### 2. Model social edges

Social memories often connect two or more entities. The representation should make those edges explicit.

Examples:

```text
Bob is Alice's manager.
Alice trusts Bob with launch planning.
Priya is waiting on Alice for the contract.
Dana owns final approval for the launch.
```

### 3. Track commitments and intentions

Commitments are among the most useful forms of social memory because they become actionable later.

Examples:

```text
Alice intends to send Priya the contract on Friday.
Alice wants to apologize to Dana before the review meeting.
Bob expects Alice to own the launch narrative.
```

### 4. Include confidence

Social memory is often uncertain. The representation should distinguish high-confidence direct facts from low-confidence beliefs, guesses, or reports.

Examples:

```text
High confidence: Bob is Alice's manager.
Low confidence: Alice believes Dana may be upset with her.
```

### 5. Keep evidence available

Every social observation should be traceable to source messages or source conclusions. This supports debugging, user trust, and demo explainability.

## Core Fields

Explicit social observations can use these fields:

| Field             | Purpose                    | Example                                          |
| ----------------- | -------------------------- | ------------------------------------------------ |
| `content`         | Human-readable observation | `Alice trusts Bob with launch planning.`         |
| `social_category` | Type of social memory      | `trust`                                          |
| `subject`         | Primary entity             | `Alice`                                          |
| `object`          | Related entity             | `Bob`                                            |
| `relation_type`   | Edge or action             | `trusts`                                         |
| `confidence`      | Certainty label            | `high`, `medium`, `low`                          |
| `perspective`     | Attribution qualifier      | `Alice stated`, `Alice believes`, `Bob reported` |

## Social Categories

Initial categories:

- `identity`
- `preference`
- `relationship`
- `emotion`
- `intention`
- `belief`
- `commitment`
- `role`
- `trust`
- `conflict`
- `group_context`
- `other`

These are intentionally simple for the hackathon. The priority is consistent extraction and useful recall, not ontology perfection.

## Examples

### Relationship and trust

Message:

```text
Alice: Bob is my manager, and I trust him with launch planning.
```

Expected observations:

```json
[
  {
    "content": "Bob is Alice's manager.",
    "social_category": "relationship",
    "subject": "Alice",
    "object": "Bob",
    "relation_type": "manager",
    "confidence": "high",
    "perspective": "Alice stated"
  },
  {
    "content": "Alice trusts Bob with launch planning.",
    "social_category": "trust",
    "subject": "Alice",
    "object": "Bob",
    "relation_type": "trusts",
    "confidence": "high",
    "perspective": "Alice stated"
  }
]
```

### Belief with uncertainty

Message:

```text
Alice: I think Dana may be upset with me after yesterday's review.
```

Expected observation:

```json
{
  "content": "Alice believes Dana may be upset with her after yesterday's review.",
  "social_category": "belief",
  "subject": "Alice",
  "object": "Dana",
  "relation_type": "believes_upset",
  "confidence": "low",
  "perspective": "Alice believes"
}
```

### Commitment

Message:

```text
Alice: Please remind me to send Priya the contract on Friday.
```

Expected observation:

```json
{
  "content": "Alice intends to send Priya the contract on Friday.",
  "social_category": "commitment",
  "subject": "Alice",
  "object": "Priya",
  "relation_type": "send_contract",
  "confidence": "high",
  "perspective": "Alice requested"
}
```

## Acceptance Criteria

For the first milestone:

- The deriver prompt explicitly asks for social-brain observations.
- Extracted observations can carry social metadata fields.
- Social metadata persists into document metadata.
- Representations hydrate social metadata back into observation objects.
- Markdown representation output surfaces useful social tags.
- The system avoids promoting beliefs and reports into objective facts.
- Tests cover prompt guidance and representation conversion.

## Demo Acceptance Criteria

The demo should show that the agent can:

1. Ingest a conversation with relationships, beliefs, trust, conflict, and commitments.
2. Produce social observations with categories and perspective.
3. Recall those observations later in a helpful answer.
4. Explain why it believes a social fact.
5. Avoid overstating uncertain social information.

## Future Milestones

After representation, the next milestones are:

1. **Social graph view** — visualize entities and relationship edges.
2. **Temporal change** — detect relationship changes and stale commitments.
3. **Conflict reconciliation** — surface contradictions and ask clarifying questions.
4. **Proactive recall** — remind agents of commitments at the right time.
5. **User controls** — let users inspect, edit, or delete social memories.
