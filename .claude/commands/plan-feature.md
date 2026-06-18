---
description: Turn a feature idea into a short implementation plan tied to the PRD
argument-hint: <feature description>
---

Plan this feature for lootcode: $ARGUMENTS

1. Check `docs/PRD.md` and `docs/roadmap.md` — does it fit? Note any gaps.
2. List the components touched: web / api / executor / data model / content.
3. Propose data-model or API changes if needed (cite `docs/data-model.md`,
   `docs/api-design.md`).
4. Give a concise, step-by-step plan with explicit test points.
5. Flag security implications — especially anything touching code execution.

Output the plan for review. Do **not** write code yet.
