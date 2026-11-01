#!/usr/bin/env python3
"""Check that every formula in the bank's statements typesets in KaTeX.

Statements may carry LaTeX math (`$…$` inline, `$$…$$` display; see
docs/math-in-statements.md). The page renders a formula KaTeX cannot parse as
red source text, which nobody notices until a solver opens the problem. This
script finds every formula the way the page does — through the real Markdown
filter, `app.templating.render_markdown` — and parses each one with the
**vendored** KaTeX (`app/static/vendor/katex/katex.min.js`), so a typo fails
here instead of on screen.

KaTeX is JavaScript, so parsing needs `node`. Without it the parse is skipped
with a notice (it is a lint, not a gate the app depends on); the unwrapped-TeX
check below still runs.

Usage:  python scripts/check_math.py            every problem, both content roots
        python scripts/check_math.py -v         also list each problem's formula count
        python scripts/check_math.py <substr>   only slugs containing <substr>

It also fails on TeX that reached the page **unwrapped** — a `$$` or a
`\begin{` left in the HTML, or a `$` directly before a TeX command — which is
what a display block too shallowly indented inside a list item, or an unpaired
`$`, produces. Those never get as far as KaTeX, so parsing alone misses them.

Exit codes: 0 every formula parses (or node is absent) and none is unwrapped,
1 a formula does not parse, or TeX was left unwrapped (checked with or without
node).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import settings  # noqa: E402
from app.content import load_all_roots  # noqa: E402
from app.templating import render_markdown  # noqa: E402

KATEX = settings.STATIC_DIR / "vendor" / "katex" / "katex.min.js"

# What arithmatex (generic mode) emits around each formula; the text inside is
# HTML-escaped and still carries its \( \) or \[ \] delimiters.
_MATH = re.compile(r'<(span|div) class="arithmatex">(.*?)</\1>', re.DOTALL)

# Code is never math, so it is cut out before looking for stray TeX.
_CODE = re.compile(r"<pre>.*?</pre>|<code>.*?</code>", re.DOTALL)
# Signs of TeX that arithmatex did not wrap: never part of prose like "$5".
_STRAY = re.compile(r"\$\$|\\begin\{|\$\\[A-Za-z]")

# Parse every formula; report errors, and collect KaTeX's "strict" notes
# (e.g. Unicode text in math mode) as warnings rather than failures — the page
# renders those fine.
_NODE = r"""
const katex = require(process.argv[1]);
const items = JSON.parse(require("fs").readFileSync(0, "utf8"));
const out = items.map(({ tex, display }) => {
  const warnings = [];
  try {
    katex.renderToString(tex, {
      displayMode: display, throwOnError: true,
      strict: (code, msg) => { warnings.push(msg); return "ignore"; },
    });
    return { ok: true, warnings };
  } catch (e) {
    return { ok: false, error: String(e.message || e), warnings };
  }
});
process.stdout.write(JSON.stringify(out));
"""


def extract(statement_md: str) -> list[tuple[str, bool]]:
    """Every formula in one statement, as ``(tex, display)``, delimiters removed."""
    found = []
    for _tag, body in _MATH.findall(render_markdown(statement_md)):
        tex = html.unescape(body).strip()
        if tex[:2] in ("\\(", "\\["):
            found.append((tex[2:-2], tex[:2] == "\\["))
    return found


def stray(statement_md: str) -> list[str]:
    """TeX left unwrapped in one rendered statement, each with some context."""
    text = _CODE.sub("", _MATH.sub("", render_markdown(statement_md)))
    return [" ".join(text[max(0, m.start() - 30):m.end() + 30].split())
            for m in _STRAY.finditer(text)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("filter", nargs="?", help="only slugs containing this substring")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="list each problem's formula count")
    args = ap.parse_args(argv)

    items: list[dict] = []
    per_slug: dict[str, int] = {}
    unwrapped = 0
    for prob in load_all_roots():
        if args.filter and args.filter not in prob["slug"]:
            continue
        statement = prob.get("statement_md") or ""
        for tex, display in extract(statement):
            items.append({"slug": prob["slug"], "tex": tex, "display": display})
            per_slug[prob["slug"]] = per_slug.get(prob["slug"], 0) + 1
        for context in stray(statement):
            unwrapped += 1
            print(f"ERROR  {prob['slug']}: TeX left unwrapped (indent a list item's "
                  f"$$ block 4 spaces, or pair the $):\n       …{context}…")

    if not items:
        print("check_math: no formulas in the selected statements."
              + (f" {unwrapped} UNWRAPPED" if unwrapped else ""))
        return 1 if unwrapped else 0
    node = shutil.which("node") or shutil.which("nodejs")
    if node is None:
        print(f"check_math: parse SKIPPED — node not found; {len(items)} formula(s) "
              "in the bank went unchecked."
              + (f" {unwrapped} UNWRAPPED" if unwrapped else ""))
        return 1 if unwrapped else 0

    proc = subprocess.run(
        [node, "-e", _NODE, str(KATEX)],
        input=json.dumps([{"tex": i["tex"], "display": i["display"]} for i in items]),
        capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        print(f"check_math: node failed:\n{proc.stderr}", file=sys.stderr)
        return 1
    results = json.loads(proc.stdout)

    errors = unwrapped
    for item, res in zip(items, results, strict=True):
        where = f"{item['slug']}: {'$$' if item['display'] else '$'}{item['tex']}"
        if not res["ok"]:
            errors += 1
            print(f"ERROR  {where}\n       {res['error']}")
        for w in res["warnings"]:
            print(f"warn   {where}\n       {w}")
    if args.verbose:
        for slug, n in sorted(per_slug.items()):
            print(f"  {slug}: {n} formula(s)")
    status = "OK" if errors == 0 else f"{errors} FAILED"
    print(f"check_math: {len(items)} formula(s) in {len(per_slug)} statement(s): {status}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
