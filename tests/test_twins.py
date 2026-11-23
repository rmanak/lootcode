"""numpy ⇄ PyTorch twins stay twins (docs/pytorch-twins.md).

A twin (``<slug>-pytorch``, ``torch.twin`` in its meta.json) is meant to be the
numpy problem again, in PyTorch: same contract, same constraints, same tests.
Everything that can drift by hand is pinned here, statically (no torch, no
sandbox): the contract, the validator, the tags, the shared generator, the
ported test cases, and the collection. The numerical agreement of the two
canonicals is ``scripts/sync_twin_tests.py check``'s job (it needs torch).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from app import content
from app.config import settings
from app.executor import run_submission
from app.executor.torch_runtime import unavailable_reason
from app.executor.torch_runtime.inputs import generated_inputs
from authoring import twins

ROOT = Path(__file__).resolve().parent.parent
ROOTS = [ROOT / "content" / "problems", ROOT / "content" / "problems-extended"]


def _meta(d: Path) -> dict:
    return json.loads((d / "meta.json").read_text(encoding="utf-8"))


def _cases(d: Path) -> list:
    return json.loads((d / "tests" / "cases.json").read_text(encoding="utf-8"))["cases"]


def _pairs() -> list[tuple[Path, Path]]:
    out = []
    for root in ROOTS:
        for m in sorted(root.glob("*/meta.json")):
            meta = json.loads(m.read_text(encoding="utf-8"))
            sibling = twins.numpy_slug_of(meta)
            if sibling:
                out.append((root / sibling, m.parent))
    return out


PAIRS = _pairs()
IDS = [tw.name for _, tw in PAIRS]


def test_there_are_twins_to_check():
    assert PAIRS, "no twins found: did torch.twin move?"


@pytest.mark.parametrize(("np_dir", "tw_dir"), PAIRS, ids=IDS)
def test_the_twin_is_named_after_its_sibling_in_the_same_root(np_dir, tw_dir):
    assert (np_dir / "meta.json").exists(), f"{tw_dir.name}: no sibling {np_dir.name}"
    assert tw_dir.name == twins.twin_slug(np_dir.name)
    assert _meta(np_dir).get("runtime", "python") == "python"


@pytest.mark.parametrize(("np_dir", "tw_dir"), PAIRS, ids=IDS)
def test_the_contract_is_the_same(np_dir, tw_dir):
    npm, twm = _meta(np_dir), _meta(tw_dir)
    nf, tf = npm["function"], twm["function"]
    assert tf["name"] == nf["name"]
    assert [p["name"] for p in tf["params"]] == [p["name"] for p in nf["params"]]
    for n, t in zip(nf["params"], tf["params"], strict=True):
        # An array may become a Tensor (a ragged one a Tensor[]); anything
        # else keeps its numpy type.
        assert t["type"] in twins.allowed_twin_types(n["type"]), t
    assert twm["difficulty"] == npm["difficulty"]
    assert twm["tags"] == [*npm["tags"], "pytorch"]


@pytest.mark.parametrize(("np_dir", "tw_dir"), PAIRS, ids=IDS)
def test_the_validator_is_the_numpy_one(np_dir, tw_dir):
    rel = Path("input_validator") / "input_validator.py"
    assert (tw_dir / rel).read_bytes() == (np_dir / rel).read_bytes(), (
        "the twin's constraints are the numpy problem's: copy its validator")


@pytest.mark.parametrize(("np_dir", "tw_dir"), PAIRS, ids=IDS)
def test_the_generator_is_shared(np_dir, tw_dir):
    gen = twins.load_generator(np_dir)
    cfg = _meta(tw_dir)["torch"]
    if gen is None:
        assert not cfg.get("inputs") and not cfg.get("random_tests"), (
            "the twin draws from a generator the numpy problem does not have")
        return
    assert cfg.get("dims") == gen["dims"] and cfg.get("inputs") == gen["inputs"], (
        f"run: scripts/sync_twin_tests.py port {np_dir.name} --write")
    assert cfg.get("random_tests", 0) > 0
    # Both sides can actually draw from it.
    np_params = _meta(np_dir)["function"]["params"]
    tw_params = _meta(tw_dir)["function"]["params"]
    assert generated_inputs(gen, np_params, seed=1, count=3)
    assert generated_inputs(gen, tw_params, seed=1, count=3)


@pytest.mark.parametrize(("np_dir", "tw_dir"), PAIRS, ids=IDS)
def test_the_twin_holds_every_numpy_case(np_dir, tw_dir):
    gen = twins.load_generator(np_dir)
    want = twins.port_cases(_cases(np_dir), _meta(np_dir)["function"]["params"],
                            _meta(tw_dir)["function"]["params"], gen, _cases(tw_dir))
    assert _cases(tw_dir) == want, (
        f"the twin's cases are stale: run scripts/sync_twin_tests.py port "
        f"{np_dir.name} --write")


@pytest.mark.parametrize(("np_dir", "tw_dir"), PAIRS, ids=IDS)
def test_forbid_names_are_well_formed(np_dir, tw_dir):
    forbid = _meta(tw_dir)["torch"].get("forbid") or []
    assert isinstance(forbid, list)
    for name in forbid:
        assert re.fullmatch(r"torch(\.[A-Za-z][A-Za-z0-9_]*)*\._?[A-Za-z][A-Za-z0-9_]*", name), name


@pytest.mark.slow
@pytest.mark.skipif(settings.EXECUTOR_BACKEND == "docker" or unavailable_reason() is not None,
                    reason="torch runtime not installed")
@pytest.mark.parametrize(("np_dir", "tw_dir"), PAIRS, ids=IDS)
def test_a_wrong_submission_is_wrong_not_broken_under_the_forbid_list(np_dir, tw_dir):
    # verify_bank grades the canonical, which is never patched, so a forbid
    # list that breaks the harness would stay invisible there. Grade a
    # non-canonical answer instead: it must be judged, not crash.
    prob = content.load_problem_dir(tw_dir)
    prob["runtime_config"] = {**prob["runtime_config"], "random_tests": 1}
    sig = ", ".join(p["name"] for p in prob["params"])
    g = run_submission(f"def {prob['function_name']}({sig}):\n    return 0\n",
                       prob, prob["tests"][:1])
    assert [r.status for r in g.results] == ["wrong", "wrong"], g.results


def test_the_pytorch_collection_follows_the_numpy_study_order():
    coll = json.loads((ROOT / "content/collections/ml-coding-pytorch.json")
                      .read_text(encoding="utf-8"))["problems"]
    order = json.loads((ROOT / "content/collections/ml-coding.json")
                       .read_text(encoding="utf-8"))["problems"]
    rank = {twins.twin_slug(s): i for i, s in enumerate(order)}
    twin_items = [s for s in coll if s in rank]
    assert twin_items == sorted(twin_items, key=rank.__getitem__)
    assert {tw.name for _, tw in PAIRS} <= set(coll)


# --- the pure helpers -------------------------------------------------------------
def test_types_map_arrays_to_tensors_and_leave_the_rest():
    assert twins.twin_param_type("float[][]") == "Tensor"
    assert twins.twin_param_type("int[]") == "Tensor"
    assert twins.twin_param_type("float") == "float"
    assert twins.twin_param_type("string") == "string"
    assert twins.twin_param_type("any[]") == "any[]"
    assert twins.twin_return_type("float") == "Tensor"
    assert twins.twin_return_type("any[]") == "any[]"


def test_a_ragged_array_may_become_a_list_of_tensors():
    assert twins.allowed_twin_types("float[][]") == ("float[][]", "Tensor", "Tensor[]")
    assert twins.allowed_twin_types("float[]") == ("float[]", "Tensor")
    np_params = [{"name": "g", "type": "float[][]"}]
    tw_params = [{"name": "g", "type": "Tensor[]"}]
    gen = {"inputs": {"g": {"$list": {"count": 2, "dims": {"L": [1, 3]},
                                      "item": {"$random": {"shape": ["L"],
                                                           "dtype": "float64"}}}}}}
    cases = [{"name": "a", "input": {"g": [[1.0, 2.0], [3.0]]}, "expected": [0]}]
    out = twins.port_cases(cases, np_params, tw_params, gen, [])
    assert out[0]["input"]["g"] == [{"$tensor": {"data": [1.0, 2.0], "dtype": "float64"}},
                                    {"$tensor": {"data": [3.0], "dtype": "float64"}}]
    # float64 is pinned, so neither side rounds to float32.
    assert twins.round_like_torch({"g": [[0.1]]}, gen, tw_params) == {"g": [[0.1]]}
    para = twins.torch_paragraph(np_params, tw_params, "any[]", gen)
    assert "`g` arrives as a list of float64 tensors" in para


def test_port_wraps_integer_and_pinned_float_literals():
    np_params = [{"name": "x", "type": "float[][]"}, {"name": "y", "type": "int[]"},
                 {"name": "z", "type": "float[]"}, {"name": "t", "type": "float"}]
    tw_params = [{"name": "x", "type": "Tensor"}, {"name": "y", "type": "Tensor"},
                 {"name": "z", "type": "Tensor"}, {"name": "t", "type": "float"}]
    gen = {"inputs": {"z": {"$random": {"shape": [2], "dtype": "float64"}}}}
    cases = [{"name": "a", "input": {"x": [[1.0]], "y": [0, 1], "z": [0.5, 1.5], "t": 0.1},
              "expected": [1], "hidden": True, "weight": 2}]
    keep = [{"name": "torch-extra", "input": {}, "expected": None}]
    out = twins.port_cases(cases, np_params, tw_params, gen, [*keep, {"name": "stale"}])
    assert out[0] == {"name": "a", "expected": None, "weight": 2, "hidden": True,
                      "input": {"x": [[1.0]], "t": 0.1,
                                "y": {"$tensor": {"data": [0, 1], "dtype": "int64"}},
                                "z": {"$tensor": {"data": [0.5, 1.5], "dtype": "float64"}}}}
    assert [c["name"] for c in out] == ["a", "torch-extra"]


def test_float32_rounding_matches_what_torch_holds():
    assert twins.f32(0.1) == 0.10000000149011612
    assert twins.f32(1e39) == float("inf")
    params = [{"name": "x", "type": "float[]"}, {"name": "t", "type": "float"}]
    out = twins.round_like_torch({"x": [0.1, 2], "t": 0.1}, None, params)
    assert out == {"x": [0.10000000149011612, 2], "t": 0.1}
    pinned = {"inputs": {"x": {"$random": {"dtype": "float64"}}}}
    assert twins.round_like_torch({"x": [0.1]}, pinned, params) == {"x": [0.1]}


def test_disagreement_is_in_units_of_the_tolerance():
    t = [{"$tensor": {"shape": [], "dtype": "float32", "data": [1.00001]}},
         {"$tensor": {"shape": [2], "dtype": "float32", "data": [0.0, 2.0]}}]
    score, _ = twins.disagreement(t, [1.0, [0.0, 2.0]], rtol=1e-5, atol=1e-6)
    assert score == pytest.approx(1e-5 / (1e-6 + 1e-5), rel=1e-3)
    assert twins.disagreement(t, [1.0, [0.0]], 1e-5, 1e-6)[0] == float("inf")


def test_stratify_spreads_over_the_answers():
    draws = [({"x": [1]}, [0.0])] * 20 + [({"x": [1]}, [100.0]), ({"x": [1]}, [-50.0])]
    picks = twins.stratify(draws, 3)
    assert {20, 21} <= set(picks) and len(set(picks)) == 3
