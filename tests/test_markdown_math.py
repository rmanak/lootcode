"""Math in statements: `$…$` / `$$…$$` reach KaTeX intact, and nothing else does.

`app.templating.render_markdown` runs `pymdownx.arithmatex`, which lifts every
formula out *before* Markdown sees it and wraps it for `static/math.js` to hand
to the vendored KaTeX. These pin the two halves of "without causing issues":
the TeX survives Markdown untouched, and text that merely contains a `$` (prices
in prose, JSON paths in code) is never turned into math. See
docs/math-in-statements.md.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

from app.templating import render_markdown

_ROOT = Path(__file__).resolve().parent.parent
_KATEX = _ROOT / "app" / "static" / "vendor" / "katex"

_spec = importlib.util.spec_from_file_location(
    "check_math", _ROOT / "scripts" / "check_math.py")
assert _spec and _spec.loader
check_math = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_math)
extract = check_math.extract


def test_inline_math_is_wrapped_for_katex():
    assert render_markdown("The loss $L$ is small.") == (
        '<p>The loss <span class="arithmatex">\\(L\\)</span> is small.</p>')


def test_display_math_is_its_own_block():
    html = render_markdown("Before.\n\n$$\ny = Wx + b\n$$\n\nAfter.")
    assert '<div class="arithmatex">\\[\ny = Wx + b\n\\]</div>' in html
    assert "<p>Before.</p>" in html and "<p>After.</p>" in html


def test_markdown_does_not_mangle_the_tex():
    """Without arithmatex, `\\{` loses its backslash and `*…*` becomes <em>."""
    tex = r"\{x \mid x > 0\} \cup a * b * c \cup x_i + y_i"
    assert extract(f"Sets: ${tex}$.") == [(tex, False)]


def test_prices_in_prose_are_not_math():
    """smart_dollar: a `$` that does not hug its content cannot close a formula.
    This is the exact shape of best-time-to-buy-and-sell-stock-v's statement."""
    text = "Buy the stock on day 0 for $1 then sell it on day 2 for $9."
    assert render_markdown(text) == f"<p>{text}</p>"


def test_an_escaped_dollar_is_a_literal_dollar():
    assert render_markdown(r"It costs \$5, while $x$ is math.") == (
        '<p>It costs $5, while <span class="arithmatex">\\(x\\)</span> is math.</p>')


def test_code_is_never_math():
    md = 'Root path `"$.city"` and:\n\n```\nbalance = $20 - $10 = $10\n```'
    html = render_markdown(md)
    assert "arithmatex" not in html
    assert '<code>"$.city"</code>' in html and "$20 - $10 = $10" in html


def test_the_tex_is_html_escaped():
    """A formula is text, not markup: it cannot smuggle a tag into the page."""
    html = render_markdown("$<script>alert(1)</script>$")
    assert "<script>" not in html
    assert "\\(&lt;script&gt;alert(1)&lt;/script&gt;\\)" in html


def test_math_inside_a_list_item_and_a_table_cell():
    assert extract("- the mean $\\mu$\n- the spread $\\sigma$") == [
        ("\\mu", False), ("\\sigma", False)]
    assert extract("| f | x |\n|---|---|\n| relu | $\\max(0, x)$ |") == [
        ("\\max(0, x)", False)]


def test_a_display_block_too_shallow_for_its_list_item_is_caught():
    """Python-Markdown needs 4 spaces to keep a block inside a list item. At 3,
    the list ends, the `$$` lines become a plain paragraph, and the page shows
    raw TeX. KaTeX never sees it, so only `stray` can fail on it."""
    shallow = "1. Softmax:\n\n   $$\n   p_i = e^{z_i}\n   $$\n\n2. Rank."
    assert extract(shallow) == []
    assert len(check_math.stray(shallow)) == 2
    deep = shallow.replace("\n   $$", "\n    $$").replace("   p_i", "    p_i")
    assert [(tex.strip(), d) for tex, d in extract(deep)] == [("p_i = e^{z_i}", True)]
    assert check_math.stray(deep) == []


def test_stray_tex_ignores_prices_code_and_wrapped_math():
    md = ("Buy for $1 and sell for $9; $x$ is math.\n\n"
          "Path `\"$.a\"` and `$$` in code.\n\n```\ncost = $\\alpha\n```")
    assert check_math.stray(md) == []
    assert len(check_math.stray("An unpaired $\\alpha in prose.")) == 1


def test_every_font_the_katex_stylesheet_prefers_is_vendored():
    """The CSS lists woff2 first, and every browser we serve takes it, so only
    those files are vendored. A missing one renders that alphabet in a fallback
    font with no error anywhere."""
    css = (_KATEX / "katex.min.css").read_text(encoding="utf-8")
    fonts = set(re.findall(r"url\((fonts/[^)]+\.woff2)\)", css))
    assert len(fonts) > 10
    missing = sorted(f for f in fonts if not (_KATEX / f).is_file())
    assert not missing, f"app/static/vendor/katex/ lacks {missing}"


def test_every_page_loads_katex_before_the_typesetter(client):
    """base.html carries both, so any page that renders Markdown — the problem
    page, ICF's workspace — gets math with no per-template wiring."""
    html = client.get("/").text
    katex = html.index("vendor/katex/katex.min.js")
    typeset = html.index("/static/math.js")
    assert "vendor/katex/katex.min.css" in html
    assert katex < typeset
