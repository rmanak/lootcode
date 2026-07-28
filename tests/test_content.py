"""content/ <-> problem-dict round trip (app/content.py).

``content/problems/`` is the durable, human-editable mirror of the bank, and
``write_problem_files`` is what every admin save writes through. A silent change
in either direction corrupts the source of truth, so the load→write→load identity
is the thing worth pinning.

These write into a tmp root (``tmp_content_dir``), never the real bank.
"""
import json

import pytest

from app.content import (
    MAX_HINTS,
    load_all,
    load_all_roots,
    load_problem_dir,
    normalize_hints,
    write_problem_files,
)


def function_problem(**over) -> dict:
    data = {
        "slug": "add-two", "title": "Add Two", "difficulty": "medium",
        "topics": ["math", "array"], "hints": ["First.", "Second."],
        "statement_md": "Return `a + b`.\n\nWith a second paragraph.\n",
        "kind": "function", "function_name": "addTwo",
        "params": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
        "return_type": "int", "compare": "unordered",
        "starter_code": "def addTwo(a, b):\n    pass\n",
        "canonical_solution": "def addTwo(a, b):\n    return a + b\n",
        "scoring_type": "weighted", "points": 75,
        "time_limit_ms": 3000, "memory_limit_mb": 128,
        "class_name": None, "class_methods": None,
        "tests": [
            {"name": "c1", "input": {"a": 1, "b": 2}, "expected": 3,
             "weight": 2, "hidden": False},
            {"name": "c2", "input": {"a": -5, "b": 5}, "expected": 0,
             "weight": 1, "hidden": True},
        ],
    }
    data.update(over)
    return data


def class_problem() -> dict:
    return {
        "slug": "min-stack", "title": "Min Stack", "difficulty": "medium",
        "topics": ["design", "stack"], "hints": [],
        "statement_md": "Design a stack.", "kind": "class",
        "function_name": "", "return_type": "",
        "params": [], "class_name": "MinStack",
        "class_methods": [
            {"name": "push", "params": [{"name": "val", "type": "int"}],
             "returns": {"type": "void"}},
            {"name": "getMin", "params": [], "returns": {"type": "int"}},
        ],
        "compare": "exact", "starter_code": "class MinStack:\n    pass\n",
        "canonical_solution": "class MinStack:\n    pass\n",
        "scoring_type": "weighted", "points": 100,
        "tests": [{"name": "c1",
                   "input": {"operations": ["MinStack", "push", "getMin"],
                             "args": [[], [3], []]},
                   "expected": [None, None, 3], "weight": 1, "hidden": False}],
    }


# --- the round trip -------------------------------------------------------
def test_function_problem_round_trips(tmp_content_dir):
    original = function_problem()
    write_problem_files(original, tmp_content_dir)
    back = load_problem_dir(tmp_content_dir / "add-two")

    for key in ("slug", "title", "difficulty", "kind", "function_name",
                "params", "return_type", "compare", "starter_code",
                "canonical_solution", "scoring_type", "points",
                "time_limit_ms", "memory_limit_mb", "tests", "hints"):
        assert back[key] == original[key], key
    # `topics` is normalized on write: `math` drops once `array` is present.
    assert back["topics"] == ["array"]


def test_class_problem_round_trips(tmp_content_dir):
    original = class_problem()
    write_problem_files(original, tmp_content_dir)
    back = load_problem_dir(tmp_content_dir / "min-stack")

    assert back["kind"] == "class"
    assert back["class_name"] == "MinStack"
    assert back["class_methods"] == original["class_methods"]
    assert back["params"] == []
    # A class problem must not grow a function contract on the way through.
    assert back["function_name"] == "" and back["return_type"] == ""
    assert back["tests"] == original["tests"]


def test_round_trip_is_idempotent(tmp_content_dir):
    write_problem_files(function_problem(), tmp_content_dir)
    once = load_problem_dir(tmp_content_dir / "add-two")
    write_problem_files(once, tmp_content_dir)
    twice = load_problem_dir(tmp_content_dir / "add-two")
    assert once == twice


def test_big_integers_survive_the_file_round_trip(tmp_content_dir):
    # The DB path has its own guard (test_jsontext_bigint.py); the file path
    # must not lose precision either.
    big = 46970481301346070551168882056905936076800000000000000
    data = function_problem(tests=[
        {"name": "c1", "input": {"a": big, "b": 0}, "expected": big,
         "weight": 1, "hidden": False}])
    write_problem_files(data, tmp_content_dir)
    back = load_problem_dir(tmp_content_dir / "add-two")
    assert back["tests"][0]["expected"] == big
    assert isinstance(back["tests"][0]["expected"], int)


# --- what write_problem_files puts on disk -------------------------------
def test_the_on_disk_layout_is_the_documented_one(tmp_content_dir):
    write_problem_files(function_problem(), tmp_content_dir)
    base = tmp_content_dir / "add-two"
    for rel in ("meta.json", "problem.md", "tests/cases.json",
                "starters/python/solution.py", "solution/solution.py"):
        assert (base / rel).is_file(), rel


def test_tags_are_normalized_on_write(tmp_content_dir):
    write_problem_files(function_problem(topics=["bfs", "enumeration"]),
                        tmp_content_dir)
    meta = json.loads((tmp_content_dir / "add-two" / "meta.json").read_text())
    assert meta["tags"] == ["breadth-first-search"]


def test_hintless_problems_omit_the_key_entirely(tmp_content_dir):
    write_problem_files(function_problem(hints=[]), tmp_content_dir)
    meta = json.loads((tmp_content_dir / "add-two" / "meta.json").read_text())
    assert "hints" not in meta


def test_assets_are_written_alongside(tmp_content_dir):
    svg = '<svg xmlns="http://www.w3.org/2000/svg"></svg>'
    write_problem_files(function_problem(assets={"example-1.svg": svg}),
                        tmp_content_dir)
    written = tmp_content_dir / "add-two" / "assets" / "example-1.svg"
    assert written.read_text(encoding="utf-8") == svg


def test_write_returns_the_directory_it_wrote(tmp_content_dir):
    assert write_problem_files(function_problem(),
                               tmp_content_dir) == tmp_content_dir / "add-two"


# --- hints ----------------------------------------------------------------
@pytest.mark.parametrize("raw,expected", [
    (None, []),
    ([], []),
    (["  a  ", "", "   ", "b"], ["a", "b"]),
    (["a"] * (MAX_HINTS + 3), ["a"] * MAX_HINTS),
])
def test_normalize_hints(raw, expected):
    assert normalize_hints(raw) == expected


# --- loading many ---------------------------------------------------------
def test_load_all_reads_every_problem_dir(tmp_content_dir):
    write_problem_files(function_problem(), tmp_content_dir)
    write_problem_files(function_problem(slug="add-three", title="Add Three"),
                        tmp_content_dir)
    assert {p["slug"] for p in load_all(tmp_content_dir)} == {"add-two", "add-three"}


def test_load_all_skips_a_dir_without_meta(tmp_content_dir):
    write_problem_files(function_problem(), tmp_content_dir)
    (tmp_content_dir / "not-a-problem").mkdir()
    assert [p["slug"] for p in load_all(tmp_content_dir)] == ["add-two"]


def test_load_all_of_a_missing_root_is_empty(tmp_path):
    assert load_all(tmp_path / "nope") == []


def test_load_all_roots_reads_both_roots_in_order(tmp_content_dir):
    # The extended root is created next to it by the fixture.
    extended = tmp_content_dir.parent / "problems-extended"
    write_problem_files(function_problem(title="Default Root"), tmp_content_dir)
    write_problem_files(function_problem(slug="only-extended", title="Only Extended"),
                        extended)

    loaded = load_all_roots([tmp_content_dir, extended])
    assert [p["slug"] for p in loaded] == ["add-two", "only-extended"]


def test_a_slug_in_both_roots_is_returned_twice(tmp_content_dir):
    """Pinning the shadowing hazard, not endorsing it.

    ``load_all_roots`` concatenates the roots without de-duplicating, so a slug
    present in both comes back twice and the *extended* copy is the one that
    survives ``upsert_problem`` at seed time. That is why an admin edit must
    write back to the root the problem actually came from rather than always to
    ``content/problems/``.
    """
    extended = tmp_content_dir.parent / "problems-extended"
    write_problem_files(function_problem(title="Default Root"), tmp_content_dir)
    write_problem_files(function_problem(title="Extended Root"), extended)

    loaded = load_all_roots([tmp_content_dir, extended])
    assert [p["title"] for p in loaded] == ["Default Root", "Extended Root"]
