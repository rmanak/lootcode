"""`ProblemView` / `CaseView`: the one shape the grader reads.

`run_submission` normalizes whatever it is handed, so no caller has to keep its
own field list. Four callers kept one anyway — the run endpoint, admin verify,
the pre-save gate, and the LLM generator — each re-deciding what a missing
`weight` or `kind` meant. One of them got it wrong; see the regression at the
bottom of this file.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.executor import CaseView, case_views, problem_view

# --- case_views ------------------------------------------------------------


def test_case_views_reads_dicts_and_orm_rows_the_same_way():
    as_dict = {"name": "t1", "input": {"a": 1}, "expected": 2,
               "weight": 3, "hidden": True}
    as_row = SimpleNamespace(**as_dict)
    assert case_views([as_dict]) == case_views([as_row])
    assert case_views([as_dict])[0] == CaseView(
        name="t1", input={"a": 1}, expected=2, weight=3, hidden=True)


def test_case_views_defaults_match_what_the_callers_each_used_to_assume():
    (t,) = case_views([{}])
    assert t.name == "test-1"      # positional: results are keyed by name
    assert t.input == {}
    assert t.expected is None
    assert t.weight == 1
    assert t.hidden is False


def test_case_views_names_every_unnamed_test_distinctly():
    """Two blank names would collide in the harness's by-name result map."""
    names = [t.name for t in case_views([{}, {"name": ""}, {}])]
    assert names == ["test-1", "test-2", "test-3"]
    assert len(set(names)) == 3


def test_case_views_keeps_a_zero_weight():
    """`weight or 1` would silently promote a deliberately-zero-weight test."""
    assert case_views([{"name": "t", "weight": 0}])[0].weight == 0


def test_case_views_passes_through_an_existing_view():
    view = CaseView(name="t", input={}, expected=1, weight=1, hidden=False)
    assert case_views([view])[0] is view


def test_case_views_are_frozen_so_they_outlive_their_session():
    (t,) = case_views([{"name": "t"}])
    with pytest.raises(Exception):  # noqa: B017 - dataclasses.FrozenInstanceError
        t.expected = 99


# --- problem_view ----------------------------------------------------------

def test_problem_view_reads_a_dict_and_an_object_the_same_way():
    fields = {"function_name": "solve", "params": [{"name": "a"}],
              "return_type": "int", "kind": "function", "compare": "unordered",
              "time_limit_ms": 1000, "memory_limit_mb": 64, "points": 50,
              "class_name": None, "class_methods": None}
    assert problem_view(fields) == problem_view(SimpleNamespace(**fields))


def test_problem_view_carries_the_class_fields():
    """The generator's hand-rolled shim omitted exactly these three."""
    pv = problem_view({"kind": "class", "class_name": "MinStack",
                       "class_methods": [{"name": "push"}]})
    assert (pv.kind, pv.class_name) == ("class", "MinStack")
    assert pv.class_methods == [{"name": "push"}]


def test_problem_view_defaults_a_bare_dict_to_a_function_problem():
    pv = problem_view({})
    assert pv.kind == "function"
    assert pv.compare == "exact"
    assert pv.points == 100
    # Left as None so run_submission can apply the configured limits.
    assert pv.time_limit_ms is None and pv.memory_limit_mb is None


# --- the regression this consolidation fixes -------------------------------

MIN_STACK = '''
class MinStack:
    def __init__(self):
        self.s = []
    def push(self, val):
        self.s.append(val)
    def top(self):
        return self.s[-1]
'''


@pytest.mark.slow
def test_the_generator_can_grade_a_class_problem():
    """`llm.generator._validate` graded a draft against its own tests through a
    six-field shim that omitted `kind`, `class_name` and `class_methods`. A
    class/design draft was therefore graded as a function problem: every test
    failed with "must define a function named ''", so the generator could never
    produce one. It now hands the problem dict over whole.
    """
    from app.llm.generator import _validate

    data = {
        "kind": "class", "class_name": "MinStack", "function_name": "",
        "return_type": "", "params": [],
        "class_methods": [
            {"name": "push", "params": [{"name": "val", "type": "int"}],
             "returns": {"type": "void"}},
            {"name": "top", "params": [], "returns": {"type": "int"}},
        ],
        "compare": "exact", "time_limit_ms": 3000, "memory_limit_mb": 512,
        "canonical_solution": MIN_STACK,
        "tests": [{
            "name": "ex",
            "input": {"operations": ["MinStack", "push", "top"],
                      "args": [[], [7], []]},
            "expected": [None, None, 7], "weight": 1, "hidden": False,
        }],
    }
    graded = _validate(data)
    assert graded.solved, [(r.name, r.status, r.error) for r in graded.results]
