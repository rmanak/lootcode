# Problem figures (images)

How figures attach to a problem: **when** to add one, **how** to make it, and the
**storage + serving API** that puts it on the problem page. This is the single
source of truth for images; the `bulk-import` skill and the authoring specs defer
to it.

## When a figure is warranted (decision rubric)

A figure earns its place only when it makes the problem *faster to understand* —
not as decoration. Add one when **both** hold:

1. **The data is structural or spatial** — a 2D grid/matrix, a tree or graph, a
   linked list with structure (e.g. a cycle), geometry, intervals on a number
   line, or a **multi-step transformation** (before → after).
2. **A first-time reader gets the mapping faster from a picture** than from the
   worked examples alone.

**Strong signal:** the original source had a figure here (when importing pasted
text, the tell-tale is a blank gap right before `Input:` where an `<img>` used to
be). If a figure was there, one almost certainly belongs.

**Skip it** when the input/output is a scalar or a flat list whose examples are
self-explanatory (Two Sum, Maximum Subarray, Jump Game, Number of 1 Bits), or when
a tiny inline code block / text table already conveys it (e.g. Reverse Bits' binary
table). When unsure, lean toward *no* image — a redundant picture is clutter.

Typical **yes**: rotate/spiral/traverse a matrix, grid paths, binary-tree
relationships, graph problems, interval merging on a number line.

## How to generate one

Use **hand-written SVG**. It is crisp at any zoom, tiny, text-based (diffs cleanly,
no binary blobs), and needs **no dependencies** — you author it as text, so it
works in the authoring environment with nothing installed.

Conventions:

- **One file per example**, named `example-1.svg`, `example-2.svg`, … (or a short
  descriptive name). Keep the `viewBox` tight and the file self-contained — no
  external fonts, scripts, or `<image href>` references.
- Use a system font stack (`font-family="system-ui, sans-serif"`), high-contrast
  strokes, and a **light/transparent background** that stays legible on the page
  (the page styles `.md img` with a light card background).
- Show the **transformation**, not just the input: input grid → arrow → output
  grid; the spiral path with arrowheads; `root` and `subRoot` side by side with the
  matching subtree highlighted; a grid with the robot and target marked.
- Keep them small (a few hundred bytes to a few KB). Accessibility: include a
  `<title>` and meaningful `alt` text in the markdown.

## Storage + serving API

```
content/problems/<slug>/
└── assets/
    ├── example-1.svg
    └── example-2.svg
```

- **Store** figures in the problem's own `assets/` dir so they live alongside the
  durable mirror. When authoring via `scripts/build_bank.py`, pass an `assets`
  map (`filename → svg-text`) and the builder writes them; `write_problem_files`
  also accepts an optional `assets` map. `load_problem_dir` ignores `assets/`
  (statements carry the URLs — no DB column is needed).
- **Reference** from `problem.md` with ordinary markdown, which already renders via
  the `markdown | safe` filter:
  ```markdown
  ![Example 1: rotate the 3×3 matrix 90° clockwise](/problems/<slug>/assets/example-1.svg)
  ```
- **Serve** via the route `GET /problems/{slug}/assets/{filename}` (in
  `app/routers/pages.py`). It is deliberately narrow:
  - reads only from `CONTENT_DIR/<slug>/assets/`;
  - rejects any `filename` with `/`, `\`, or `..`, and asserts the resolved path
    stays inside that `assets/` dir (no traversal);
  - allows only image extensions (`.svg .png .jpg .jpeg .gif .webp`), serving SVG
    as `image/svg+xml`; `404` otherwise.

  **Never** mount `content/problems/` wholesale — that would expose
  `solution/solution.py` and hidden `tests/cases.json`. Only `assets/` is public.
  This is a file-serving path: review changes to it per `docs/security.md`.

## Why this isn't in the AI-generator guidelines

Figure generation is an **authoring-time** step done by Claude Code / the
problem-author path, not by the in-app AI generator (it can't emit SVG assets), so
it lives here and in the `bulk-import` skill rather than inside the AI-GUIDELINES
block of `specs/problem-authoring-guidelines.md`.
