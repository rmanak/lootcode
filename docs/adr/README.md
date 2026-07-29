# Architecture Decision Records (ADRs)

Short documents capturing a significant decision, its context, and consequences.

## How to use

- One ADR per decision. Number them sequentially: `NNNN-title.md`.
- Copy `0001-record-architecture-decisions.md` as the template.
- Status: `Proposed` → `Accepted` → (later) `Superseded by NNNN`.
- Don't edit decided ADRs; supersede them with a new one.

## Suggested ADRs to write soon

Numbers are assigned when an ADR is written, not reserved in advance.

- Build vs. buy the code executor (see `docs/code-execution.md`).
- Source of truth for problems: `content/` files vs. database.
- Backend framework & language.
- Scoring model.

## Index

- [0001 — Record architecture decisions](0001-record-architecture-decisions.md)
- [0002 — Sandbox file-size rlimit: bounds `result.json`, not disk usage](0002-sandbox-file-size-limit.md)
