"""numpy ⇄ PyTorch twins stay twins (docs/pytorch-twins.md).

A twin (``<slug>-pytorch``, ``torch.twin`` in its meta.json) is meant to be the
numpy problem again, in PyTorch: same contract, same constraints, same tests.
Everything that can drift by hand is pinned here, statically (no torch, no
sandbox): the contract, the validator, the tags, the shared generator, the
ported test cases, and the collection. The numerical agreement of the two
canonicals is ``scripts/sync_twin_tests.py check``'s job (it needs torch).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from app.executor.torch_runtime.inputs import generated_inputs
from authoring import twins

ROOT = Path(__file__).resolve().parent.parent
ROOTS = [ROOT / "content" / "problems", ROOT / "content" / "problems-extended"]


def _meta(d: Path) -> dict:
    return json.loads((d / "meta.json").read_text(encoding="utf-8"))


def _cases(d: Path) -> list:
    return json.loads((d / "tests" / "cases.json").read_text(encoding="utf-8"))["cases"]


def _validator(d: Path):
    path = d / "input_validator" / "input_validator.py"
    spec = importlib.util.spec_from_file_location(f"_v_{d.name}", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.validate_input


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
def test_the_generator_is_shared_or_the_twins_own(np_dir, tw_dir):
    # The numpy tests/generator.json, unless the twin has its own in
    # tests/twin.json (float32-scale draws, docs/pytorch-twins.md "dtype").
    gen = twins.twin_generator(np_dir, tw_dir)
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


OWN = [(n, t) for n, t in PAIRS if (t / twins.OVERRIDES_FILE).exists()
       and twins.load_overrides(t)["generator"]]


@pytest.mark.parametrize(("np_dir", "tw_dir"), OWN, ids=[t.name for _, t in OWN])
def test_a_twins_own_generator_stays_inside_the_shared_constraints(np_dir, tw_dir):
    own = twins.load_overrides(tw_dir)["generator"]
    valid = _validator(tw_dir)
    draws = twins.draw_inputs(own, _meta(tw_dir)["function"]["params"], seed=7, count=50)
    assert all(valid(**d) for d in draws)


@pytest.mark.parametrize(("np_dir", "tw_dir"), PAIRS, ids=IDS)
def test_skipped_cases_exist_in_the_numpy_problem(np_dir, tw_dir):
    skip = twins.load_overrides(tw_dir)["skip"]
    assert set(skip) <= {c["name"] for c in _cases(np_dir)}, "a stale skip"


@pytest.mark.parametrize(("np_dir", "tw_dir"), PAIRS, ids=IDS)
def test_the_twin_holds_every_numpy_case(np_dir, tw_dir):
    gen = twins.twin_generator(np_dir, tw_dir)
    want = twins.port_cases(_cases(np_dir), _meta(np_dir)["function"]["params"],
                            _meta(tw_dir)["function"]["params"], gen, _cases(tw_dir),
                            skip=twins.load_overrides(tw_dir)["skip"])
    assert _cases(tw_dir) == want, (
        f"the twin's cases are stale: run scripts/sync_twin_tests.py port "
        f"{np_dir.name} --write")


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


def test_overrides_give_a_twin_its_own_generator_and_skips(tmp_path):
    assert twins.load_overrides(tmp_path) == {"generator": None, "skip": {}}
    (tmp_path / "tests").mkdir()
    own = {"dims": {"n": [1, 3]},
           "inputs": {"x": {"$random": {"shape": ["n"], "low": -1.0, "high": 1.0}}}}
    (tmp_path / "tests" / "twin.json").write_text(json.dumps(
        {"generator": {"why": "float32 scale", **own}, "skip": {"big": "unrepresentable"}}))
    assert twins.load_overrides(tmp_path) == {"generator": own, "skip": {"big": "unrepresentable"}}
    assert twins.twin_generator(tmp_path / "no-numpy-sibling", tmp_path) == own


@pytest.mark.parametrize("bad", [
    {"generator": {"dims": {}, "inputs": {}}},           # no why
    {"generator": {"why": " ", "inputs": {}}},           # empty why
    {"skip": {"case": ""}},                              # skip without a reason
    {"skip": ["case"]},
    {"generatr": {}},                                    # a typo is an error, not a no-op
])
def test_overrides_reject_a_missing_reason_or_an_unknown_key(tmp_path, bad):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "twin.json").write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        twins.load_overrides(tmp_path)


def test_port_leaves_out_skipped_cases_and_keeps_torch_ones():
    params = [{"name": "x", "type": "float[]"}]
    tparams = [{"name": "x", "type": "Tensor"}]
    cases = [{"name": n, "input": {"x": [1.0]}, "expected": [1.0]} for n in ("a", "huge", "b")]
    mine = [{"name": "torch-huge-at-float32-scale", "input": {"x": [1.0]}, "expected": None}]
    out = twins.port_cases(cases, params, tparams, None, mine, skip={"huge": "why"})
    assert [c["name"] for c in out] == ["a", "b", "torch-huge-at-float32-scale"]
