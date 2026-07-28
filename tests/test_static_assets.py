"""Every asset a template asks for must exist, and load in a workable order.

`app/templating.py`'s `static()` falls back to an unversioned URL when it can't
stat the file, so a template pointing at a missing asset renders a perfectly
normal-looking `<script src>` that 404s — a dead button and no error anywhere.
That has already happened once: `llm_refresh.js` was referenced by a tracked
template while the file itself was untracked.

Now that three scripts depend on `sse.js` being loaded first, the same class of
silent breakage covers "the dependency wasn't included on this page".
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
_TEMPLATES = _ROOT / "app" / "templates"
_STATIC = _ROOT / "app" / "static"

#: `{{ static('foo.js') }}` — the only way templates reference an asset.
_STATIC_CALL = re.compile(r"""static\(\s*['"]([^'"]+)['"]\s*\)""")
_SCRIPT_SRC = re.compile(r"""<script[^>]*\bsrc=["']?\{\{\s*static\(\s*['"]([^'"]+)['"]""")

#: Scripts that call into `window.lootcode`, and so need sse.js loaded first.
_NEEDS_SSE = {"app.js", "generate.js", "generate_statement.js"}


def _templates() -> list[Path]:
    return sorted(_TEMPLATES.rglob("*.html"))


def test_there_are_templates_to_check():
    """Guard the guard: a bad glob would make every test below vacuous."""
    assert len(_templates()) > 5


@pytest.mark.parametrize("template", _templates(), ids=lambda p: p.name)
def test_every_referenced_asset_exists(template):
    for asset in _STATIC_CALL.findall(template.read_text(encoding="utf-8")):
        assert (_STATIC / asset).is_file(), (
            f"{template.relative_to(_ROOT)} references app/static/{asset}, "
            "which does not exist — static() would silently emit a 404 URL")


@pytest.mark.parametrize("template", _templates(), ids=lambda p: p.name)
def test_sse_dependents_load_their_dependency_first(template):
    scripts = _SCRIPT_SRC.findall(template.read_text(encoding="utf-8"))
    for i, name in enumerate(scripts):
        if name in _NEEDS_SSE:
            assert "sse.js" in scripts[:i], (
                f"{template.relative_to(_ROOT)} loads {name}, which calls "
                "window.lootcode, without loading sse.js before it")


def test_the_sse_helpers_the_consumers_call_are_the_ones_it_exports():
    """A rename in sse.js has to reach its callers; nothing else would notice."""
    sse = (_STATIC / "sse.js").read_text(encoding="utf-8")
    exported = set(re.findall(r"^\s*ns\.(\w+)\s*=", sse, re.MULTILINE))
    assert exported, "sse.js exports nothing — did the ns.* assignments move?"

    called = set()
    for name in _NEEDS_SSE:
        called |= set(re.findall(r"window\.lootcode\.(\w+)\(",
                                 (_STATIC / name).read_text(encoding="utf-8")))
    assert called, "no consumer calls window.lootcode — check the regex"
    assert called <= exported, f"called but not exported: {sorted(called - exported)}"


@pytest.mark.parametrize("name", sorted(_NEEDS_SSE | {"sse.js", "admin.js"}))
def test_the_server_actually_serves_the_script(client, name):
    r = client.get(f"/static/{name}")
    assert r.status_code == 200
    assert r.text.strip()
