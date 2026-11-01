# Math in statements

Problem statements (and ICF statements) may contain LaTeX math, written the way
Jupyter and most Markdown editors take it:

| You write | You get |
|-----------|---------|
| `$\sigma(z)$` | inline math |
| `$$` on its own line, the formula, `$$` on its own line | a centred display block |
| `\(…\)` / `\[…\]` | the same two, LaTeX-style |
| `\$5` | a literal dollar sign |

It is rendered by **KaTeX**, which covers what statements need (fractions, sums,
hats, norms, `aligned`, `cases`, matrices, `\texttt`, `\text`) but not every
LaTeX package. `python scripts/check_math.py` (also run by `make check`) tells
you whether every formula in the bank parses, and whether any TeX reached the
page without being recognized as math (a stray `$$`, `\begin{` or `$\cmd`).

## How it works

Two halves, and both are needed.

1. **Server: `pymdownx.arithmatex`** (`app/templating.py::render_markdown`).
   Python-Markdown would otherwise eat the TeX before any browser saw it:
   `\{` loses its backslash, `*…*` and `_…_` become emphasis, `\\` collapses.
   arithmatex lifts every formula out *before* Markdown runs, HTML-escapes it,
   and emits `<span class="arithmatex">\(…\)</span>` (inline) or
   `<div class="arithmatex">\[…\]</div>` (display).
2. **Browser: KaTeX** (`app/static/vendor/katex/`, vendored, so a LAN install
   needs no CDN) plus `app/static/math.js`, which typesets exactly those
   elements. `base.html` loads both on every page, so any template that renders
   Markdown gets math with no wiring. If KaTeX fails to load, or a formula does
   not parse, the TeX source stays on the page, readable; a bad formula shows as
   red source with the parse error as its tooltip.

Because only arithmatex's wrapped elements are typeset, a bare `$` in prose is
never treated as math. Its `smart_dollar` rule (on by default) only pairs a `$`
that hugs its content, so "buy for $1 then sell for $9" stays text. When math
was switched on, all 1,251 statements in the bank rendered byte-identically
except the ones deliberately converted, including every statement that uses `$`
for money or JSON paths. Code (fenced or inline) is never touched.

## Writing it well

- **Tie every symbol to its argument.** The solver reads the formula but
  writes code: "where $\theta$ is `params` and $\eta$ is `lr`". `\texttt{name}`
  inside math works for names that appear in the formula itself
  (`\texttt{dgamma}_j = …`).
- **Keep display math narrow.** At a common laptop width the statement panel is
  about 460 px. Put one relation per line (`\begin{aligned}…\end{aligned}`,
  `\\` between lines) instead of setting two equations side by side with
  `\qquad`, and put notes such as "(biased: divide by N)" in the prose, not in a
  `\text{…}` beside the formula. A formula that is still too wide scrolls
  sideways inside its own box rather than breaking the layout, but its end is
  hidden until the reader scrolls.
- **Display math goes at the top level**, with blank lines around the `$$`
  block. Inside a list item, Python-Markdown needs the block indented **4
  spaces**: at the usual 3 the list ends, the `$$` lines become a plain
  paragraph, and the page shows raw TeX (`check_math.py` fails on that). Even at
  4 spaces the list turns "loose", with paragraph spacing between its items, so
  prefer an inline formula in the item, or a display block after the list.
- **Constraints and examples stay in code.** The `## Constraints` bullets
  (`1 <= n <= 10⁴`) and the `Input:`/`Output:` blocks keep their bank-wide
  format; math is for the formulas and the prose around them.
- **A `|` inside math breaks a Markdown table row.** Use `\lvert x \rvert` or
  `\mid` in table cells.
- **The LLM features read the raw Markdown**, LaTeX included (hints, "Get More
  Help", Analysis). Models read LaTeX fine.

## Updating KaTeX

`app/static/vendor/katex/` holds `katex.min.js`, `katex.min.css`, the `woff2`
fonts and the MIT `LICENSE`, copied unmodified from the npm tarball (currently
**0.18.11**). Every browser we serve takes the stylesheet's first choice, woff2,
so the `woff`/`ttf` files it also lists are not vendored and are never
requested; `tests/test_markdown_math.py` fails if a woff2 file the CSS names is
missing. To upgrade: download `katex-<ver>.tgz` from the npm registry, check its
`shasum` against the registry's, copy the same files over, then run
`make check` and open a converted problem (e.g. `/problems/dpo-loss`) in a
browser.
