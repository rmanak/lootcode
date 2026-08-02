"""Tests for scripts/remove_problem.py — the problem-retirement tool.

The DB half of that script is guarded by its own dry-run/confirm/backup flow and
a post-write `quick_check`. What is tested here is the half that silently
rewrites *curated content*: the collection manifests. A bug there does not raise
— it reorders someone's study list, or names the same problem twice, and nothing
notices.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from app.config import settings

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "remove_problem.py"
_spec = importlib.util.spec_from_file_location("remove_problem", _SCRIPT)
assert _spec and _spec.loader
remove_problem = importlib.util.module_from_spec(_spec)
# Registered before exec: @dataclass resolves annotations via sys.modules[__module__].
sys.modules[_spec.name] = remove_problem
_spec.loader.exec_module(remove_problem)


# --------------------------------------------------------------------------- specs

@pytest.mark.parametrize("spec,expected", [
    ("two-sum", ("two-sum", None)),
    ("two-sum-ii=two-sum", ("two-sum-ii", "two-sum")),
    ("two-sum-ii->two-sum", ("two-sum-ii", "two-sum")),
    ("  two-sum-ii  ->  two-sum  ", ("two-sum-ii", "two-sum")),
])
def test_parse_spec(spec, expected):
    assert remove_problem.parse_spec(spec) == expected


@pytest.mark.parametrize("bad", ["=two-sum", "two-sum=", "->two-sum"])
def test_parse_spec_rejects_half_a_mapping(bad):
    with pytest.raises(ValueError):
        remove_problem.parse_spec(bad)


def test_read_specs_ignores_comments_and_blanks(tmp_path):
    f = tmp_path / "list.txt"
    f.write_text("# retire these\n\ntwo-sum-ii -> two-sum\nfoo=bar  # inline\n")
    assert remove_problem.read_specs(f) == ["two-sum-ii -> two-sum", "foo=bar"]


# ------------------------------------------------------------------ subtitle counts

def test_restate_count_only_touches_the_stated_size():
    """The list's own size is restated; an unrelated number is left alone."""
    out = remove_problem._restate_count(
        "The 435 problems from the full 500-problem list.", 435, 434)
    assert out == "The 434 problems from the full 500-problem list."


def test_restate_count_noop_when_size_unchanged():
    subtitle = "A curated set of 73 problems."
    assert remove_problem._restate_count(subtitle, 73, 73) == subtitle


# ------------------------------------------------------------- collection rewriting

@pytest.fixture
def collections(tmp_path, monkeypatch):
    """Point the script at a throwaway collections dir."""
    monkeypatch.setattr(settings, "COLLECTIONS_DIR", tmp_path)

    def write(slug: str, problems: list[str], subtitle: str = "") -> Path:
        path = tmp_path / f"{slug}.json"
        path.write_text(json.dumps(
            {"slug": slug, "title": slug, "subtitle": subtitle, "problems": problems}))
        return path

    return write


def _problems(path: Path) -> list[str]:
    return json.loads(path.read_text())["problems"]


def test_replacement_inherits_the_removed_slug_position(collections):
    """A dedupe must not reshuffle the curated study order."""
    path = collections("blind", ["a", "gone", "c"])
    remove_problem.rewrite_collections(
        [remove_problem.Removal(slug="gone", replacement="kept")], verbose=False)
    assert _problems(path) == ["a", "kept", "c"]


def test_replacement_already_present_is_dropped_not_duplicated(collections):
    """A curated list must never name the same problem twice."""
    path = collections("blind", ["a", "gone", "kept"])
    remove_problem.rewrite_collections(
        [remove_problem.Removal(slug="gone", replacement="kept")], verbose=False)
    assert _problems(path) == ["a", "kept"]


def test_removal_without_replacement_just_drops(collections):
    path = collections("blind", ["a", "gone", "c"])
    remove_problem.rewrite_collections(
        [remove_problem.Removal(slug="gone")], verbose=False)
    assert _problems(path) == ["a", "c"]


def test_subtitle_count_follows_a_shrinking_list(collections):
    path = collections("blind", ["a", "gone", "c"], subtitle="A set of 3 problems.")
    remove_problem.rewrite_collections(
        [remove_problem.Removal(slug="gone")], verbose=False)
    assert json.loads(path.read_text())["subtitle"] == "A set of 2 problems."


def test_subtitle_untouched_when_a_replacement_keeps_the_size(collections):
    path = collections("blind", ["a", "gone"], subtitle="A set of 2 problems.")
    remove_problem.rewrite_collections(
        [remove_problem.Removal(slug="gone", replacement="kept")], verbose=False)
    assert json.loads(path.read_text())["subtitle"] == "A set of 2 problems."


def test_untouched_manifests_are_not_rewritten(collections):
    """A list that never named the slug keeps its bytes exactly."""
    other = collections("other", ["x", "y"])
    before = other.read_bytes()
    collections("blind", ["gone"])
    remove_problem.rewrite_collections(
        [remove_problem.Removal(slug="gone")], verbose=False)
    assert other.read_bytes() == before


def test_several_removals_in_one_pass(collections):
    path = collections("blind", ["a", "gone1", "b", "gone2", "c"])
    remove_problem.rewrite_collections([
        remove_problem.Removal(slug="gone1", replacement="kept"),
        remove_problem.Removal(slug="gone2"),
    ], verbose=False)
    assert _problems(path) == ["a", "kept", "b", "c"]
