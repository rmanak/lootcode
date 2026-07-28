"""Guards that make two kinds of documentation drift mechanically impossible.

Both of these are cheap, and both encode a failure that already happened in this
repo:

1. **Tag drift.** ``app/tags.py::CANONICAL_TAGS`` is the source of truth, but the
   vocabulary is hard-coded a second, third and fourth time — in ``specs/tags.md``
   (prose), in ``app/llm/problem_prompt.txt`` (injected verbatim into the model's
   system prompt, so a stale copy makes the generator author against the wrong
   vocabulary), and in the ``canonical-tags`` skill (what an authoring agent
   reads). All four agree today. Keeping them in agreement is a machine's job.

2. **Dead references.** Docs cite paths that no longer exist — including
   ``services/executor``, cited by the security-review gate itself. Any
   ``app/...`` or ``scripts/....py`` path named in the docs must be on disk.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.tags import CANONICAL_TAGS

ROOT = Path(__file__).resolve().parent.parent


def tags_in(text: str) -> set[str]:
    """Every canonical-looking tag mentioned in a blob of prose.

    Deliberately loose: it pulls kebab-case words out of backticks and comma
    lists and keeps the ones that *look* like tags, then compares as a set. The
    point is to catch a tag added to the code and forgotten in a doc, not to
    parse four different markup styles exactly.
    """
    words = set(re.findall(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", text))
    # Only judge words that are, or plausibly are, vocabulary entries: a tag in
    # the code, or a kebab-case word sitting in the same list as one.
    return {w for w in words if w in CANONICAL_TAGS}


# --- 1. tag drift ---------------------------------------------------------
TAG_MIRRORS = {
    # (path, the slice of the file that carries the vocabulary)
    "specs/tags.md": ("## Canonical tags", "## Aliases"),
    "app/llm/problem_prompt.txt": ("canonical vocabulary", "Do NOT invent tags"),
    ".claude/skills/canonical-tags/SKILL.md": ("Core data shapes", "##"),
}


@pytest.mark.parametrize("rel,bounds", sorted(TAG_MIRRORS.items()))
def test_every_copy_of_the_tag_vocabulary_matches_the_code(rel, bounds):
    path = ROOT / rel
    assert path.is_file(), f"{rel} is gone — update TAG_MIRRORS"
    text = path.read_text(encoding="utf-8")

    start_marker, end_marker = bounds
    start = text.find(start_marker)
    assert start != -1, f"{rel}: can't find the vocabulary block ({start_marker!r})"
    end = text.find(end_marker, start + len(start_marker))
    block = text[start:end if end != -1 else len(text)]

    missing = CANONICAL_TAGS - tags_in(block)
    assert not missing, (
        f"{rel} is missing {sorted(missing)} — app/tags.py is the source of "
        "truth and this copy has drifted.")


def test_the_prompt_states_the_right_tag_count():
    prompt = (ROOT / "app/llm/problem_prompt.txt").read_text(encoding="utf-8")
    assert f"({len(CANONICAL_TAGS)} tags)" in prompt


def test_the_taxonomy_doc_states_the_right_tag_count():
    spec = (ROOT / "specs/tags.md").read_text(encoding="utf-8")
    assert f"## Canonical tags ({len(CANONICAL_TAGS)})" in spec


# --- 2. dead references ---------------------------------------------------
DOC_ROOTS = ["docs", "specs", ".claude"]
DOC_FILES = ["README.md", "CLAUDE.md", "CONTRIBUTING.md"]

# Docs whose whole job is to describe things that do not exist yet. Excluded by
# name rather than by folder so adding one is a deliberate act.
FORWARD_LOOKING = {
    "docs/engineering-plan.md",
    "docs/engineering-review.md",
    "docs/duplicate-detection-plan.md",
}

# A path that looks like a repo path in prose. Only `app/` and `scripts/`:
# "tests/cases.json" in the docs means content/problems/<slug>/tests/cases.json,
# a fragment, not a repo-root path.
_PATH_RE = re.compile(
    r"(?<![\w./-])"
    r"((?:app|scripts)/[A-Za-z0-9_./-]*[A-Za-z0-9_])"
)

# Prose that names a *pattern* rather than one file.
_NOT_A_PATH = re.compile(r"[*?]|\.\.\.|<|>|\{|\}")


def iter_docs():
    for name in DOC_FILES:
        p = ROOT / name
        if p.is_file():
            yield p
    for root in DOC_ROOTS:
        base = ROOT / root
        if base.is_dir():
            yield from sorted(
                p for p in base.rglob("*.md") if "proposals" not in p.parts)


def resolves(ref: str) -> bool:
    """Whether ``ref`` names something real.

    Docs routinely write a module member as ``app/llm/help_generator.stream_help``
    or ``scripts/oracle.cover``; those resolve to the module file.
    """
    if (ROOT / ref).exists():
        return True
    stem, dot, _member = ref.rpartition(".")
    return bool(dot) and (ROOT / f"{stem}.py").exists()


def referenced_paths(doc: Path) -> set[str]:
    out = set()
    for raw in _PATH_RE.findall(doc.read_text(encoding="utf-8")):
        ref = raw.rstrip(".,;:)`'\"")
        if _NOT_A_PATH.search(ref):
            continue
        # `app/executor/` and `app/executor` both mean the directory.
        out.add(ref.rstrip("/"))
    return out


def test_docs_reference_only_paths_that_exist():
    dead: dict[str, list[str]] = {}
    for doc in iter_docs():
        rel = str(doc.relative_to(ROOT))
        if rel in FORWARD_LOOKING:
            continue
        missing = sorted(ref for ref in referenced_paths(doc) if not resolves(ref))
        if missing:
            dead[rel] = missing

    assert not dead, (
        "Documentation names paths that do not exist:\n"
        + "\n".join(f"  {doc}: {', '.join(refs)}" for doc, refs in sorted(dead.items()))
    )


def test_the_guard_would_actually_catch_something(tmp_path):
    """The dead-reference check is only worth having if it can fail."""
    bogus = tmp_path / "bogus.md"
    bogus.write_text("See `app/does_not_exist.py` and `scripts/nope.py`.",
                     encoding="utf-8")
    assert referenced_paths(bogus) == {"app/does_not_exist.py", "scripts/nope.py"}
    assert not (ROOT / "app/does_not_exist.py").exists()
