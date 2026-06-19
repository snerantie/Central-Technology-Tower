# Architecture Decision Records (ADRs)

This folder captures significant architectural decisions made for the
**Central Technology Tower – AI Agent Programme**. Each ADR documents
*what* was decided, *why*, the alternatives considered, and the
consequences accepted.

## Why ADRs?

- Decisions are easy to make, hard to remember six months later.
- New team members can read the *reasoning*, not just inherit the result.
- A decision's *trade-offs* are made explicit, so we know **when** to revisit.

## How to add a new ADR

1. Copy the most recent ADR file (or use the template below).
2. Number it sequentially (`0002-...`, `0003-...`).
3. Use a short, imperative title (`Use X for Y`).
4. Set status to **Proposed** while drafting; flip to **Accepted** when the
   programme team agrees.
5. Commit on a feature branch; merge after review. The ADR itself is the
   review artifact.

## Status meanings

| Status | Meaning |
|--------|---------|
| Proposed | Drafted, not yet agreed |
| Accepted | Active decision, currently in effect |
| Deprecated | No longer in effect, but kept for history |
| Superseded by ADR-XXXX | Replaced by a newer decision (link forward) |

## Index

| # | Title | Status |
|---|-------|--------|
| [0001](0001-bedrock-model-selection.md) | Use Amazon Nova Lite as default Bedrock LLM | Accepted |

## Template (Nygard style)

```markdown
# ADR-XXXX: <Short imperative title>

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-YYYY (YYYY-MM-DD)

## Context
What problem are we solving? What constraints apply?

## Decision
What did we decide? Be specific.

## Consequences
### Positive / Negative / Neutral
What changes as a result of this decision?

## Alternatives considered
What else did we look at? Why did we reject it?

## Review trigger
Under what conditions should we revisit this decision?

## Related decisions
Links to dependent ADRs.
```
