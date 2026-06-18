# 0001 — Record architecture decisions

- **Status:** Accepted
- **Date:** 🔲 fill in (YYYY-MM-DD)

## Context

We will make decisions (stack, executor strategy, scoring, data ownership) whose
rationale is easy to forget. We want a lightweight, durable record so future
contributors (and Claude) understand *why*, not just *what*.

## Decision

We use Architecture Decision Records, stored in `docs/adr/`, one Markdown file
per decision, numbered sequentially. Each ADR has Context, Decision, and
Consequences. Decided ADRs are immutable; we supersede rather than rewrite.

## Consequences

- Cheap to write, easy to review in PRs.
- Newcomers can read the decision history in order.
- Requires the discipline of actually writing one for big choices.

---

### Template (copy this for new ADRs)

```
# NNNN — Title

- Status: Proposed | Accepted | Superseded by NNNN
- Date: YYYY-MM-DD

## Context
What's the situation and the forces at play?

## Decision
What did we decide, stated plainly?

## Consequences
What becomes easier/harder? Trade-offs and follow-ups.
```
