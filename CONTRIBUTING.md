# Contributing to lootcode

## Workflow

1. Branch from `main`: `feat/<short-name>` or `fix/<short-name>`.
2. Keep changes focused. One concern per PR.
3. Make sure `pnpm typecheck`, `pnpm lint`, and `pnpm test` pass.
4. Use [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`…).
5. Open a PR; fill in the description and link the relevant doc/issue.

## Where things go

- Product decisions → `docs/PRD.md` (and an ADR in `docs/adr/` for big ones).
- New problems → `content/problems/`, following `specs/problem-schema.md`.
- Anything that runs user code → must follow `docs/code-execution.md`.

## Security-sensitive areas

Changes to `services/executor/` or any path that runs user-submitted code get an
extra security review. Never weaken the sandbox guarantees in
`docs/code-execution.md` for convenience. If you must, write an ADR first.

## Using Claude Code here

- `CLAUDE.md` holds the working agreements.
- Handy commands: `/add-problem`, `/plan-feature`, `/test-all`.
- Handy subagents: `problem-author`, `executor-security-reviewer`.
