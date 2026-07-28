"""Pin the solver-facing type docs to the classes the sandbox actually injects.

`app/provided_types.py` renders each snippet from the real harness class, so the
*shape* cannot drift. What it cannot derive is the authored half — which methods
make up the solver-facing read interface, and their return annotations, neither
of which the harness's own definitions carry. This is the guard for that half,
and for the wiring in between.
"""
from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from app.executor import harness
from app.provided_types import _SPECS, PROVIDED_TYPE_DEFS, provided_types


@pytest.mark.parametrize("label", sorted(_SPECS))
def test_documented_class_is_the_one_the_harness_injects(label):
    """The class named in the snippet must exist in the harness under that name."""
    spec = _SPECS[label]
    assert getattr(harness, spec.cls.__name__) is spec.cls
    assert f"class {spec.cls.__name__}:" in PROVIDED_TYPE_DEFS[label]


@pytest.mark.parametrize("label", sorted(_SPECS))
def test_documented_methods_exist_with_the_documented_arity(label):
    """Every method shown to solvers must be callable on the injected class.

    Extras are allowed and deliberate: `NestedInteger` also has `add` /
    `setInteger`, which the decoder uses to build the structure. Solvers are only
    ever handed one to read, so the docs show the read interface.
    """
    spec = _SPECS[label]
    for name in spec.methods:
        method = getattr(spec.cls, name, None)
        assert callable(method), f"{spec.cls.__name__}.{name} is not a method"
        params = list(inspect.signature(method).parameters)
        assert params == ["self"], f"{name} takes arguments the docs don't show"


@pytest.mark.parametrize("label", sorted(_SPECS))
def test_data_types_document_every_attribute_they_set(label):
    """A data type's snippet must show each attribute the constructor assigns."""
    spec = _SPECS[label]
    if spec.methods:  # an interface type, documented by its methods instead
        return
    snippet = PROVIDED_TYPE_DEFS[label]
    for attr in spec.cls.__slots__:
        assert f"self.{attr}" in snippet, f"{spec.cls.__name__}.{attr} undocumented"
    # ...and the constructor line is the real signature, defaults included.
    sig = inspect.signature(inspect.getattr_static(spec.cls, "__init__"))
    assert f"def __init__{sig}:" in snippet


def test_every_snippet_warns_against_redefining_the_class():
    for label, defn in PROVIDED_TYPE_DEFS.items():
        assert "provided, do not redefine" in defn.splitlines()[0], label


def test_aliases_share_one_definition_object():
    """De-duplication in `provided_types` is by identity, so aliases must not be
    separately rendered copies."""
    for spec in _SPECS.values():
        for alias in spec.aliases:
            assert PROVIDED_TYPE_DEFS[alias] is PROVIDED_TYPE_DEFS[
                next(k for k, v in _SPECS.items() if v is spec)]


# --- the selector ----------------------------------------------------------

def _problem(**kw):
    return SimpleNamespace(
        **{"params": [], "return_type": "", "class_methods": None, **kw})


def test_provided_types_picks_up_params_and_return():
    prob = _problem(params=[{"name": "root", "type": "TreeNode"}],
                    return_type="ListNode")
    assert list(provided_types(prob)) == ["TreeNode", "ListNode"]


def test_provided_types_covers_class_method_signatures():
    """For a design problem the rich type can appear only on a method."""
    prob = _problem(class_methods=[
        {"name": "push", "params": [{"name": "node", "type": "ListNode"}],
         "returns": {"type": "void"}},
        {"name": "peek", "params": [], "returns": {"type": "NestedInteger"}},
    ])
    assert list(provided_types(prob)) == ["ListNode", "NestedInteger"]


def test_provided_types_reports_an_alias_under_the_label_the_problem_used():
    prob = _problem(params=[{"name": "it", "type": "Iterator<int>"}])
    out = provided_types(prob)
    assert list(out) == ["Iterator<int>"]
    assert out["Iterator<int>"] == PROVIDED_TYPE_DEFS["Iterator"]


def test_provided_types_shows_a_shared_definition_once():
    prob = _problem(params=[{"name": "a", "type": "NestedInteger"},
                            {"name": "b", "type": "NestedInteger[]"}],
                    return_type="List<NestedInteger>")
    assert list(provided_types(prob)) == ["NestedInteger"]


def test_provided_types_ignores_plain_and_unknown_types():
    prob = _problem(params=[{"name": "n", "type": "int"}, {"name": "x"}],
                    return_type="Widget")
    assert provided_types(prob) == {}
