"""The canonical tag vocabulary (app/tags.py).

``normalize_tags`` runs on every content write — manual admin form, AI generator,
bulk importers — so it is the last thing standing between an invented tag and the
on-disk bank. It had no test.
"""
from app.tags import (
    CANONICAL_TAGS,
    DROPPED_TAGS,
    TAG_ALIASES,
    is_canonical,
    normalize_tags,
    unknown_tags,
)


def test_vocabulary_is_thirty_nine_tags():
    # Not a tautology: four other files hard-code this list (see
    # test_docs_consistency.py), and the count is quoted in README.md.
    assert len(CANONICAL_TAGS) == 39


def test_aliases_and_dropped_never_overlap_the_vocabulary():
    # An alias that is also canonical would fold a tag onto itself forever; a
    # dropped tag that is canonical could never be stored.
    assert not (set(TAG_ALIASES) & CANONICAL_TAGS)
    assert not (DROPPED_TAGS & CANONICAL_TAGS)
    # Every alias must land somewhere real.
    assert set(TAG_ALIASES.values()) <= CANONICAL_TAGS


def test_aliases_fold_to_canonical():
    assert normalize_tags(["bfs", "dfs"]) == [
        "breadth-first-search", "depth-first-search"]
    assert normalize_tags(["segment-tree"]) == ["binary-indexed-tree"]


def test_dropped_tags_are_removed():
    assert normalize_tags(["array", "enumeration", "queries"]) == ["array"]


def test_case_and_whitespace_are_normalized():
    assert normalize_tags(["  Array ", "STRING"]) == ["array", "string"]


def test_duplicates_collapse_and_order_is_preserved():
    # Order matters: the first tag is the one the list UI shows first.
    assert normalize_tags(["string", "array", "string", "bfs",
                           "breadth-first-search"]) == [
        "string", "array", "breadth-first-search"]


def test_math_is_dropped_when_something_more_specific_applies():
    assert normalize_tags(["math", "dynamic-programming"]) == ["dynamic-programming"]
    # ...but kept when it is all there is.
    assert normalize_tags(["math"]) == ["math"]
    assert normalize_tags(["number-theory", "geometry"]) == ["math"]


def test_a_problem_is_never_left_tagless():
    for empty in (None, [], [""], ["   "], ["enumeration"]):
        assert normalize_tags(empty) == ["math"]


def test_unknown_tags_pass_through_rather_than_vanish():
    # Silently dropping an unknown tag would hide the mistake; the validator
    # surfaces it instead (see test_problem_validation.py).
    assert normalize_tags(["array", "quantum-annealing"]) == [
        "array", "quantum-annealing"]
    assert unknown_tags(["array", "bfs", "enumeration", "quantum-annealing"]) == [
        "quantum-annealing"]


def test_unknown_tags_deduplicates_case_insensitively():
    assert unknown_tags(["Made-Up", "made-up", "MADE-UP"]) == ["made-up"]


def test_is_canonical():
    assert is_canonical("array") and is_canonical("  ARRAY  ")
    assert not is_canonical("bfs")  # an alias is not itself canonical
    assert not is_canonical("")


def test_normalizing_twice_changes_nothing():
    for raw in (["bfs", "math", "array"], ["enumeration"], ["Math"], []):
        once = normalize_tags(raw)
        assert normalize_tags(once) == once


def test_every_canonical_tag_survives_normalization():
    for tag in CANONICAL_TAGS:
        # Paired with a second tag so the `math` umbrella rule doesn't fire.
        assert tag in normalize_tags([tag, "array"]) or tag in ("math", "array")
