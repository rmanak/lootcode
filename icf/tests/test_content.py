"""Loading and validating problem definitions — all static, nothing executed."""
from __future__ import annotations

import json

import pytest

from icf import content
from icf.content import ContentError, parse_cases


def test_cases_are_found_in_source_order():
    source = (
        "from icf_testkit import case\n"
        '@case("first thing")\n'
        "def a(Cls):\n    pass\n"
        '@case("second thing")\n'
        "def b(Cls):\n    pass\n"
        "def not_a_case(Cls):\n    pass\n"
    )
    cases = parse_cases(source, level=2, hidden=True, where="x")
    assert [c.func for c in cases] == ["a", "b"]
    assert [c.label for c in cases] == ["first thing", "second thing"]
    assert cases[0].id == "L2:hidden:a"
    assert cases[0].module == "icf_tests_l2_hidden"


def test_a_case_without_a_label_is_a_content_error():
    with pytest.raises(ContentError):
        parse_cases('from icf_testkit import case\n@case\ndef a(Cls):\n    pass\n',
                    level=1, hidden=False, where="x")


def test_a_test_module_that_does_not_parse_is_a_content_error():
    with pytest.raises(ContentError):
        parse_cases("def oops(:\n", level=1, hidden=False, where="x")


def test_the_toy_problem_loads_and_validates(toy):
    assert toy.class_name == "Counter"
    assert [lv.number for lv in toy.levels] == [1, 2, 3, 4]
    assert toy.case_count == 8
    assert content.validate(toy) == []


def test_unknown_slug_loads_as_none(toy_root):
    assert content.load("no-such-problem") is None
    assert content.load("../etc") is None, "a traversal-shaped slug is not a slug"


def test_load_all_lists_what_is_there(toy_root):
    assert [p.slug for p in content.load_all()] == ["toy-counter"]


def test_validate_rejects_a_reserved_slug(toy_root):
    directory = toy_root / "toy-counter"
    meta = json.loads((directory / "meta.json").read_text())
    meta["slug"] = "static"
    (directory / "meta.json").write_text(json.dumps(meta))
    content.clear_cache()
    problem = content.load("toy-counter")
    assert any("reserved" in e for e in content.validate(problem))


def test_validate_notices_a_method_missing_from_the_starter(toy_root):
    directory = toy_root / "toy-counter"
    starter = (directory / "starter" / "solution.py").read_text()
    (directory / "starter" / "solution.py").write_text(
        starter.replace("    def undo(self):\n        pass\n", ""))
    content.clear_cache()
    errors = content.validate(content.load("toy-counter"))
    assert any("undo" in e for e in errors), errors


def test_validate_wants_four_levels(toy_root):
    directory = toy_root / "toy-counter"
    meta = json.loads((directory / "meta.json").read_text())
    meta["levels"] = meta["levels"][:3]
    (directory / "meta.json").write_text(json.dumps(meta))
    content.clear_cache()
    errors = content.validate(content.load("toy-counter"))
    assert any("levels must be exactly" in e for e in errors), errors


def test_the_cache_is_keyed_by_root_as_well_as_slug(tmp_path, toy_root):
    """Two roots, one slug: the second must not be served the first's parse."""
    from icf.tests.conftest import write_toy_problem

    other = tmp_path / "other"
    other.mkdir()
    write_toy_problem(other)
    (other / "toy-counter" / "problem.md").write_text("A different intro.\n")

    first = content.load("toy-counter", toy_root)
    second = content.load("toy-counter", other)
    assert first.intro_md != second.intro_md
