"""The optional PyTorch runtime (docs/torch-runtime.md).

Two tiers. The first needs no torch at all: input materialization, the
allclose comparator, the grading view, and the content round-trip all run in
the web app's own interpreter, which never has torch. The second spawns real
sandboxes under the torch interpreter and is skipped when it isn't installed.

The property that matters most is pinned first: a plain Python problem never
touches any of this.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from app import content
from app.config import settings
from app.executor import problem_view, run_submission, runtime_unavailable
from app.executor.torch_runtime import unavailable_reason
from app.executor.torch_runtime.compare import compare
from app.executor.torch_runtime.inputs import (
    MAX_ELEMENTS,
    SpecError,
    check_config,
    dim_ranges,
    draw_dims,
    generated_inputs,
    materialize_input,
    materialize_value,
    tensor_value,
    to_plain,
)

ROOT = Path(__file__).resolve().parent.parent
PILOT = ROOT / "content" / "problems" / "clip-loss-pytorch"
T = [{"name": "x", "type": "Tensor"}]


# --- the core is untouched ---------------------------------------------------
def test_a_view_defaults_to_the_python_runtime():
    pv = problem_view({"function_name": "f", "params": []})
    assert pv.runtime == "python"
    assert pv.runtime_config is None
    assert runtime_unavailable(pv) is None


def test_grading_a_python_problem_never_imports_the_torch_runtime():
    """Run in a fresh interpreter so other tests' imports cannot hide it."""
    code = (
        f"import sys; sys.path.insert(0, {str(ROOT)!r})\n"
        "from app.executor import run_submission\n"
        "g = run_submission('def f(a):\\n    return a + 1\\n',\n"
        "    {'function_name': 'f', 'params': [{'name': 'a', 'type': 'int'}]},\n"
        "    [{'name': 't', 'input': {'a': 1}, 'expected': 2}])\n"
        "assert g.solved, g\n"
        "assert not [m for m in sys.modules if 'torch' in m], "
        "[m for m in sys.modules if 'torch' in m]\n"
    )
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       cwd=ROOT, check=False)
    assert r.returncode == 0, r.stderr


def test_an_unknown_runtime_is_refused_not_guessed_at():
    g = run_submission("def f():\n    return 1\n",
                       {"function_name": "f", "params": [], "runtime": "jax"},
                       [{"name": "t", "input": {}, "expected": 1}])
    assert not g.solved
    assert "unknown runtime 'jax'" in g.results[0].error


def test_a_plain_problem_writes_no_runtime_keys(tmp_path):
    data = {"slug": "p", "title": "P", "function_name": "f", "params": [],
            "return_type": "int", "runtime": "python", "runtime_config": None,
            "tests": [{"name": "t", "input": {}, "expected": 1}]}
    content.write_problem_files(data, tmp_path)
    meta = json.loads((tmp_path / "p" / "meta.json").read_text())
    assert "runtime" not in meta and "torch" not in meta


def test_a_torch_problem_round_trips_through_content(tmp_path):
    loaded = content.load_problem_dir(PILOT)
    assert loaded["runtime"] == "torch"
    assert loaded["runtime_config"]["random_tests"] == 5
    content.write_problem_files(loaded, tmp_path)
    again = content.load_problem_dir(tmp_path / "clip-loss-pytorch")
    for key in ("runtime", "runtime_config", "params", "tests", "canonical_solution"):
        assert again[key] == loaded[key], key
    assert (json.loads((tmp_path / "clip-loss-pytorch" / "meta.json").read_text())
            == json.loads((PILOT / "meta.json").read_text()))


def test_unavailable_runtime_errors_every_test_with_a_reason(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "EXECUTOR_BACKEND", "subprocess")
    monkeypatch.setattr(settings, "TORCH_PYTHON", str(tmp_path / "no-such-python"))
    prob = {"function_name": "f", "params": T, "runtime": "torch",
            "canonical_solution": "def f(x):\n    return x\n"}
    assert "no torch interpreter" in runtime_unavailable(prob)
    g = run_submission("def f(x):\n    return x\n", prob,
                       [{"name": "a", "input": {"x": [1.0]}},
                        {"name": "b", "input": {"x": [2.0]}, "hidden": True}])
    assert not g.solved and g.passed_count == 0 and g.total_count == 2
    assert all("PyTorch runtime" in r.error for r in g.results)


# --- inputs ------------------------------------------------------------------
def test_a_literal_becomes_a_flat_float32_tensor():
    v = materialize_value([[1, 2, 3], [4, 5, 6]], "Tensor", seed=0)
    assert v == tensor_value([2, 3], "float32", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    assert to_plain(v) == [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]


def test_a_scalar_literal_is_a_zero_dim_tensor():
    assert materialize_value(2.5, "Tensor", seed=0) == tensor_value([], "float32", [2.5])


def test_an_explicit_dtype_and_shape_are_honoured():
    v = materialize_value({"$tensor": {"data": [1, 0, 2, 1], "shape": [2, 2],
                                       "dtype": "int64"}}, "Tensor", seed=0)
    assert v == tensor_value([2, 2], "int64", [1, 0, 2, 1])


@pytest.mark.parametrize("bad", [
    [[1, 2], [3]],                          # ragged
    [[1, 2], 3],                            # mixed depth
    {"$tensor": {"data": [1, 2, 3], "shape": [2, 2]}},
    {"$tensor": {"data": [1], "dtype": "complex64"}},
    {"$tensor": {"data": [1], "dtype": "__class__"}},  # never a torch attribute
    {"$random": {"shape": [3], "dist": "poisson"}},
    {"$random": {"shape": ["N"]}},          # undefined dim
    {"$random": {"shape": [MAX_ELEMENTS + 1]}},
    ["a", "b"],
])
def test_a_malformed_tensor_input_is_a_spec_error(bad):
    with pytest.raises(SpecError):
        materialize_value(bad, "Tensor", seed=0)


def test_random_inputs_are_a_function_of_the_test_name():
    spec = {"x": {"$random": {"shape": [4, 3]}}}
    a = materialize_input(spec, T, seed_base="hidden-1")
    assert a == materialize_input(spec, T, seed_base="hidden-1")
    assert a != materialize_input(spec, T, seed_base="hidden-2")
    assert len(a["x"]["$tensor"]["data"]) == 12


def test_a_pinned_seed_gives_two_parameters_the_same_tensor():
    spec = {"$random": {"shape": [3, 2], "seed": 7}}
    a = materialize_input({"x": spec, "y": spec}, [*T, {"name": "y", "type": "Tensor"}],
                          seed_base="t")
    assert a["x"] == a["y"]


def test_distributions_respect_their_bounds_and_default_dtypes():
    u = materialize_value({"$random": {"shape": [500], "dist": "uniform",
                                       "low": -2, "high": 3}}, "Tensor", seed=1)
    assert all(-2 <= x < 3 for x in u["$tensor"]["data"])
    k = materialize_value({"$random": {"shape": [500], "dist": "randint",
                                       "low": 0, "high": 4}}, "Tensor", seed=1)
    assert k["$tensor"]["dtype"] == "int64" and set(k["$tensor"]["data"]) == {0, 1, 2, 3}
    b = materialize_value({"$random": {"shape": [10], "dist": "bernoulli"}}, "Tensor", seed=1)
    assert b["$tensor"]["dtype"] == "bool"
    s = materialize_value({"$random": {"dist": "choice", "values": [0.1, 0.5]}}, "float", seed=1)
    assert s in (0.1, 0.5)


def test_generated_tests_agree_on_their_dims_and_vary_between_draws():
    cfg = {"random_tests": 20, "dims": {"N": [1, 9], "D": [2, 5]},
           "inputs": {"x": {"$random": {"shape": ["N", "D"]}},
                      "y": {"$random": {"shape": ["N"], "dist": "randint", "high": 3}}}}
    params = [*T, {"name": "y", "type": "Tensor"}]
    draws = generated_inputs(cfg, params, seed=3)
    assert len(draws) == 20
    for d in draws:
        n, dd = d["x"]["$tensor"]["shape"]
        assert 1 <= n <= 9 and 2 <= dd <= 5
        assert d["y"]["$tensor"]["shape"] == [n]
    assert len({tuple(d["x"]["$tensor"]["shape"]) for d in draws}) > 1
    assert draws == generated_inputs(cfg, params, seed=3)
    assert draws != generated_inputs(cfg, params, seed=4)


def test_randint_bounds_may_name_a_dim():
    cfg = {"dims": {"N": [1, 30], "C": [2, 5]},
           "inputs": {"x": {"$random": {"shape": ["N", "C"]}},
                      "y": {"$random": {"shape": ["N"], "dist": "randint", "high": "C"}}}}
    params = [{"name": "x", "type": "Tensor"}, {"name": "y", "type": "Tensor"}]
    for inp in generated_inputs(cfg, params, seed=3, count=40):
        c = inp["x"]["$tensor"]["shape"][1]
        assert all(0 <= v < c for v in inp["y"]["$tensor"]["data"])
    with pytest.raises(SpecError, match="dim 'K'"):
        materialize_value({"$random": {"shape": [2], "dist": "randint", "high": "K"}},
                          "Tensor", seed=1)


def test_step_snaps_values_to_multiples():
    v = materialize_value({"$random": {"shape": [200], "dist": "uniform", "low": -10,
                                       "high": 10, "step": 0.0625}}, "float[]", seed=4)
    assert all((x * 16).is_integer() and -10 <= x <= 10 for x in v)
    with pytest.raises(SpecError, match="step"):
        materialize_value({"$random": {"shape": [2], "step": 0}}, "float[]", seed=1)


def test_a_choice_of_strings_stays_a_plain_string():
    vals = {materialize_value({"$random": {"dist": "choice", "values": ["relu", "tanh"]}},
                              "string", seed=s) for s in range(30)}
    assert vals == {"relu", "tanh"}
    with pytest.raises(SpecError, match="non-tensor"):
        materialize_value({"$random": {"dist": "choice", "values": ["a"]}}, "Tensor", seed=1)


def test_min_abs_keeps_values_off_zero():
    v = materialize_value({"$random": {"shape": [500], "dist": "uniform", "low": -1,
                                       "high": 1, "min_abs": 0.1}}, "float[]", seed=5)
    assert all(0.1 <= abs(x) <= 1 for x in v)


def test_at_least_one_per_row_fills_an_empty_row():
    spec = {"$random": {"shape": [50, 3], "dist": "randint", "high": 2,
                        "at_least_one_per_row": True}}
    for seed in range(20):
        rows = materialize_value(spec, "int[][]", seed=seed)
        assert all(any(r) and set(r) <= {0, 1} for r in rows)


@pytest.mark.parametrize("spec", [
    {"shape": [4], "std": 1e9, "step": 1e-300},          # x/step overflows
    {"shape": [4], "std": float("inf")},                  # json.loads accepts Infinity
    {"shape": [4], "dist": "randint", "high": 10 ** 400},
    {"shape": [4], "round": 400},
    {"shape": [4], "min_abs": 1e-50},                     # 0 once it is a float32
    {"shape": [4], "dist": "choice", "values": ["relu", 1.0]},
    {"shape": [4], "dist": "choice", "values": ["relu"]},  # strings: scalar only
    {"dist": "choice", "values": ["x" * 65]},
    {"shape": [4], "min-abs": 0.1},                       # a typo is an error
    {"shape": [4], "dist": "randint", "high": 1000, "dtype": "int8"},
    {"shape": [4], "dist": "randint", "high": 9, "step": 1.5},   # int dtype, fractional step
    {"shape": [4], "dist": "uniform", "low": -1e308, "high": 1e308},  # inf in float32
    {"shape": [4], "min_abs": 1e-9, "dtype": "float16"},  # 0 once it is a float16
])
def test_bad_generator_options_are_spec_errors(spec):
    ptype = "string" if spec.get("dist") == "choice" else "float[]"
    with pytest.raises(SpecError):
        materialize_value({"$random": spec}, ptype, seed=1)


def test_a_tensor_literal_rejects_unknown_keys_and_out_of_range_ints():
    with pytest.raises(SpecError, match="does not take"):
        materialize_value({"$tensor": {"data": [1, 2], "dtpye": "int64"}}, "Tensor", seed=1)
    for data, dtype in (([300], "uint8"), ([1e30], "int64"), ([1.5], "int32"),
                        ([1e10], "float16")):
        with pytest.raises(SpecError):
            materialize_value({"$tensor": {"data": data, "dtype": dtype}}, "Tensor", seed=1)
    # an explicit inf / nan in a literal is allowed (a test of overflow handling)
    materialize_value({"$tensor": {"data": [float("inf"), 2.0]}}, "Tensor", seed=1)
    materialize_value({"$tensor": {"data": [3.0], "dtype": "int64"}}, "Tensor", seed=1)


def test_dims_can_be_expressions_over_earlier_dims():
    spec = {"H": [1, 16], "r": [0, 9999], "hd": "1 + r % (32 // H)", "D": "H*hd",
            "s": [1, 4], "Ho": [1, 7], "k": [1, 5], "W": "(Ho-1)*s + k + r % s"}
    import random
    for i in range(300):
        d = draw_dims(spec, random.Random(i))
        assert d["D"] == d["H"] * d["hd"] <= 32 and d["D"] % d["H"] == 0
        assert (d["W"] - d["k"]) // d["s"] + 1 == d["Ho"]
    assert dim_ranges(spec)["hd"] == (1, 32)


@pytest.mark.parametrize("dims", [
    {"a": "b"},                    # not declared before it
    {"a": [0, 2], "b": "3 // a"},  # may divide by zero
    {"a": [0, 3], "b": "a - 2"},   # may go negative
    {"a": "1 +"}, {"a": "(1"}, {"a": "2 ** 3"}, {"a": "__import__"},
    {"a": "x" * 70}, [1, 2],
])
def test_bad_dim_expressions_fail_before_any_draw(dims):
    with pytest.raises(SpecError):
        dim_ranges(dims)



# --- ragged lists ($list) ------------------------------------------------------
_LOGPS = {"$list": {"count": "BG", "dims": {"L": [1, 9]}, "share": "len",
                    "item": {"$random": {"shape": ["L"], "dist": "uniform",
                                         "low": -5.0, "high": 0.0, "dtype": "float64"}}}}


def test_a_list_spec_draws_ragged_tensors_whose_lengths_can_be_shared():
    cfg = {"dims": {"B": [1, 3], "G": [2, 4], "BG": "B*G"},
           "inputs": {"new": _LOGPS, "old": _LOGPS,
                      "g": {"$list": {"count": [1, 5], "dims": {"n": [1, 4]},
                                      "item": {"$random": {"shape": ["n"]}}}}}}
    params = [{"name": "new", "type": "Tensor[]"}, {"name": "old", "type": "Tensor[]"},
              {"name": "g", "type": "float[][]"}]
    lengths = set()
    for inp in generated_inputs(cfg, params, seed=7, count=40):
        new, old = inp["new"], inp["old"]
        assert len(new) == len(old) in {b * g for b in range(1, 4) for g in range(2, 5)}
        shapes = [t["$tensor"]["shape"] for t in new]
        assert shapes == [t["$tensor"]["shape"] for t in old]   # aligned item by item
        assert [t["$tensor"]["data"] for t in new] != [t["$tensor"]["data"] for t in old]
        assert all(t["$tensor"]["dtype"] == "float64" for t in new)
        lengths |= {s[0] for s in shapes}
        assert 1 <= len(inp["g"]) <= 5 and all(isinstance(r, list) for r in inp["g"])
    assert len(lengths) > 3   # ragged, not one length
    # Deterministic per seed.
    assert generated_inputs(cfg, params, seed=7, count=2) == generated_inputs(
        cfg, params, seed=7, count=2)


@pytest.mark.parametrize(("inputs", "ptype"), [
    ({"x": {"$list": {"count": 2, "item": 1.0}}}, "Tensor"),              # not a list type
    ({"x": {"$list": {"count": 2}}}, "Tensor[]"),                         # no item
    ({"x": {"$list": {"count": 2, "item": 1.0, "size": 3}}}, "Tensor[]"),  # unknown key
    ({"x": {"$list": {"count": -1, "item": 1.0}}}, "Tensor[]"),
    ({"x": {"$list": {"count": "K", "item": 1.0}}}, "Tensor[]"),          # no such dim
    ({"x": {"$list": {"count": True, "item": 1.0}}}, "Tensor[]"),
    ({"x": {"$list": {"count": 2, "item": {"$list": {"count": 2, "item": 1.0}}}}}, "Tensor[]"),
    ({"x": {"$list": {"count": 2, "dims": {"N": 3}, "item": 1.0}}}, "Tensor[]"),  # shadows N
    ({"x": {"$list": {"count": 2, "dims": {"L": [0, 3]},
                      "item": {"$random": {"dist": "randint", "high": "L", "shape": [1]}}}}},
     "Tensor[]"),                                                         # randint high 0
    ({"x": {"$list": {"count": 60_000, "item": {"$random": {"dist": "rand"}}}}}, "Tensor[]"),
    ({"x": {"$list": {"count": 2_000, "item": {"$random": {"shape": [30]}}}}}, "Tensor[]"),
    # Structure costs, not just numbers: 50k empty rows per item, or a literal
    # repeated `count` times, must not be nearly free (security review).
    ({"x": {"$list": {"count": 2, "item": {"$random": {"shape": [50_000, 0]}}}}}, "float[][]"),
    ({"x": {"$list": {"count": 2, "item": {"$random": {"shape": [50_000, 0]}}}}}, "Tensor[]"),
    ({"x": {"$list": {"count": 2, "item": "x" * 1000}}}, ""),
    ({"x": {"$list": {"count": 2, "item": {"a": 1, "b": 2}}}}, ""),
    ({"x": {"$list": {"count": 2, "item": [1.0, 2.0]}}}, "Tensor[]"),
    ({"x": {"$list": {"count": [0, 100_000], "item": 1.0}}}, "Tensor[]"),   # static, every seed
    ({"x": {"$list": {"count": 1, "dims": {f"d{i}": 1 for i in range(40)}, "item": 1.0}}},
     "Tensor[]"),
])
def test_bad_list_specs_are_spec_errors(inputs, ptype):
    cfg = {"dims": {"N": [1, 2]}, "inputs": inputs}
    with pytest.raises(SpecError):
        generated_inputs(cfg, [{"name": "x", "type": ptype}], seed=1, count=2)


@pytest.mark.parametrize("other_dims", [{"L": [1, 8]},
                                        {"M": [1, 9], "L": [1, 9]}])  # same dims, other order
def test_lists_sharing_lengths_must_draw_them_the_same_way(other_dims):
    mine = {"$list": {**_LOGPS["$list"], "dims": {"L": [1, 9], "M": [1, 9]}}}
    other = {"$list": {**_LOGPS["$list"], "dims": other_dims}}
    cfg = {"dims": {"BG": 4}, "inputs": {"a": mine, "b": other}}
    params = [{"name": "a", "type": "Tensor[]"}, {"name": "b", "type": "Tensor[]"}]
    with pytest.raises(SpecError, match="share"):
        generated_inputs(cfg, params, seed=1, count=1)


def test_per_item_dim_draws_are_charged():
    # 32 long expressions per item, ~50k items: refused before the loop.
    local = {"a": [1, 9], **{f"d{i}": "+".join(["a"] * 30) for i in range(31)}}
    spec = {"$list": {"count": 49_990, "dims": local, "item": {"$dim": "a"}}}
    import time
    start = time.monotonic()
    with pytest.raises(SpecError):
        materialize_input({"x": spec}, [{"name": "x", "type": "int[]"}], seed_base="t")
    assert time.monotonic() - start < 1


def test_the_input_budget_is_checked_key_by_key(monkeypatch):
    import app.executor.torch_runtime.inputs as inputs_mod
    built = []
    real = inputs_mod.materialize_value
    monkeypatch.setattr(inputs_mod, "materialize_value",
                        lambda *a, **k: built.append(1) or real(*a, **k))
    full = {"$random": {"shape": [MAX_ELEMENTS]}}
    with pytest.raises(SpecError):
        materialize_input({f"k{i}": full for i in range(10)}, [], seed_base="t")
    assert len(built) == 2


def test_a_malformed_tensor_literal_is_charged_not_a_crash():
    # A plain (undeclared) input passes through as-is; costing it must not
    # raise a KeyError the grader would turn into a 500.
    from app.executor.torch_runtime.inputs import count_elements
    assert count_elements({"x": 1.0, "junk": [{"$tensor": {}}]}) == 2


def test_costing_a_huge_literal_shape_is_cheap():
    import time

    from app.executor.torch_runtime.inputs import count_elements
    start = time.monotonic()
    junk = [{"$tensor": {"shape": [10 ** 18] * 40_000}}]
    assert count_elements({"junk": junk}) > MAX_ELEMENTS
    assert time.monotonic() - start < 0.5


def test_a_literal_tensor_list_is_charged_item_by_item(monkeypatch):
    import app.executor.torch_runtime.inputs as inputs_mod
    built = []
    real = inputs_mod.tensor_value
    monkeypatch.setattr(inputs_mod, "tensor_value",
                        lambda *a, **k: built.append(1) or real(*a, **k))
    with pytest.raises(SpecError):
        materialize_input({"xs": [{"$random": {"shape": [MAX_ELEMENTS]}}] * 40},
                          [{"name": "xs", "type": "Tensor[]"}], seed_base="t")
    assert len(built) == 2


def test_empty_rows_count_against_a_tests_input_budget():
    # Without $list too: an undeclared input key with a zero-size dim builds
    # 50k empty lists; that is not a free test.
    inp = {"junk": {"$random": {"shape": [50_000, 0]}},
           "more": {"$random": {"shape": [50_000, 0]}}}
    with pytest.raises(SpecError):
        materialize_input(inp, [], seed_base="t")

def test_a_scalar_parameter_can_be_a_drawn_dim():
    cfg = {"dims": {"H": [1, 4], "kh": [1, 3], "kw": [1, 3]},
           "inputs": {"n": {"$dim": "H"}, "k": {"$dim": ["kh", "kw"]},
                      "x": {"$random": {"shape": ["H", "kw"]}}}}
    params = [{"name": "n", "type": "int"}, {"name": "k", "type": "int[]"},
              {"name": "x", "type": "Tensor"}]
    for inp in generated_inputs(cfg, params, seed=3, count=20):
        shape = inp["x"]["$tensor"]["shape"]
        assert inp["n"] == shape[0] and inp["k"][1] == shape[1] and len(inp["k"]) == 2
    with pytest.raises(SpecError):
        materialize_value({"$dim": "H"}, "Tensor", seed=1, dims={"H": 2})
    with pytest.raises(SpecError):
        materialize_value({"$dim": "Q"}, "int", seed=1, dims={"H": 2})


@pytest.mark.parametrize("cfg", [
    {"random_test": 5},                       # a typo would silently mean "no random tests"
    {"rtol": float("nan")}, {"atol": -1}, {"rtol": "1e-5"},
    {"random_weight": 0}, {"random_tests": 51},
])
def test_a_bad_torch_block_is_a_spec_error(cfg):
    with pytest.raises(SpecError):
        check_config(cfg, 1e-5, 1e-6)


def test_dim_named_randint_bounds_are_checked_inside_tensor_lists_too():
    cfg = {"dims": {"A": [0, 5], "B": [1, 6]},
           "inputs": {"xs": [{"$random": {"dist": "randint", "low": "A", "high": "B",
                                           "shape": [2]}}]}}
    with pytest.raises(SpecError, match="extremes"):
        generated_inputs(cfg, [{"name": "xs", "type": "Tensor[]"}], seed=1, count=1)


def test_min_abs_survives_step_and_integer_dtypes():
    v = materialize_value({"$random": {"shape": [2000], "dist": "uniform", "low": -1,
                                       "high": 1, "step": 0.0625, "min_abs": 0.01}},
                          "float[]", seed=2)
    assert all(x != 0 and (x * 16).is_integer() for x in v)
    v = materialize_value({"$random": {"shape": [200], "dist": "randint", "low": -2,
                                       "high": 3, "min_abs": 0.5}}, "int[]", seed=3)
    assert 0 not in v


def test_a_randint_dim_bound_must_hold_at_the_dims_extremes():
    cfg = {"dims": {"C": [0, 3]},
           "inputs": {"y": {"$random": {"shape": [2], "dist": "randint", "high": "C"}}}}
    with pytest.raises(SpecError, match="extremes"):
        generated_inputs(cfg, [{"name": "y", "type": "Tensor"}], seed=1, count=1)


def test_the_generator_must_cover_every_parameter():
    with pytest.raises(SpecError, match="no spec"):
        generated_inputs({"random_tests": 1, "inputs": {"z": 1.0}}, T, seed=0)
    assert generated_inputs({"random_tests": 3}, T, seed=0) == []  # no generator, no tests


# --- compare -----------------------------------------------------------------
def _t(data, shape=None, dtype="float32"):
    return tensor_value([len(data)] if shape is None else shape, dtype, data)


def test_allclose_semantics():
    assert compare(_t([1.0, 2.0]), _t([1.0, 2.0])) == (True, None)
    assert compare(_t([1.0 + 5e-6]), _t([1.0]))[0]          # within rtol
    assert not compare(_t([1.0 + 5e-5]), _t([1.0]))[0]      # outside it
    assert compare(_t([5e-7]), _t([0.0]))[0]                 # atol near zero
    assert compare(_t([math.nan]), _t([math.nan]))[0]
    assert not compare(_t([0.0]), _t([math.nan]))[0]
    assert compare(_t([math.inf]), _t([math.inf]))[0]
    assert not compare(_t([-math.inf]), _t([math.inf]))[0]
    assert compare(_t([1.0]), _t([1.1]), rtol=0.2)[0]       # a problem's own tolerance


def test_shape_and_dtype_must_match_exactly():
    ok, why = compare(_t([1.0], [1]), _t([1.0], []))
    assert not ok and "shape (1,), expected ()" in why
    ok, why = compare(_t([1.0], [], "float64"), _t([1.0], []))
    assert not ok and "dtype float64, expected float32" in why
    ok, why = compare(1.0, _t([1.0], []))
    assert not ok and "expected a float32 tensor" in why


def test_integer_tensors_compare_exactly():
    assert compare(_t([3], dtype="int64"), _t([3], dtype="int64"))[0]
    assert not compare(_t([3.0], dtype="int64"), _t([3], dtype="int64"))[0]


def test_containers_of_tensors_and_the_worst_element_is_reported():
    exp = [_t([1.0, 2.0, 3.0, 4.0], [2, 2]), _t([0.5], [])]
    got = [_t([1.0, 2.0, 3.0, 9.0], [2, 2]), _t([0.5], [])]
    ok, why = compare(got, exp)
    assert not ok and "output[0]" in why and "[1, 1]" in why and "got 9.0" in why
    assert compare(exp, exp)[0]
    assert not compare(exp[:1], exp)[0]


@pytest.mark.parametrize("hostile", [
    {"$tensor": {"shape": [2], "dtype": "float32", "data": [1.0]}},      # short
    {"$tensor": {"shape": [-1], "dtype": "float32", "data": []}},
    {"$tensor": {"shape": [1], "dtype": "float32", "data": [[1.0]]}},
    {"$tensor": {"shape": "1", "dtype": "float32", "data": [1.0]}},
    {"$tensor": [1.0]},
    {"$tensor": {"shape": [1], "dtype": "float32", "data": ["1.0"]}},
])
def test_a_malformed_returned_tensor_is_wrong_never_an_exception(hostile):
    ok, _ = compare(hostile, _t([1.0]))
    assert ok is False


def test_absurd_nesting_is_wrong_not_a_crash():
    deep: list = []
    for _ in range(100_000):
        deep = [deep]
    exp: list = []
    for _ in range(100_000):
        exp = [exp]
    assert compare(deep, exp)[0] is False


# --- the real sandbox --------------------------------------------------------
needs_torch = pytest.mark.skipif(
    settings.EXECUTOR_BACKEND == "docker" or unavailable_reason() is not None,
    reason=f"torch runtime not installed ({unavailable_reason()})")

CANON = ("import torch\n\ndef softmax_rows(x):\n"
         "    return torch.softmax(x, dim=-1)\n")
PROB = {"function_name": "softmax_rows", "params": T, "return_type": "Tensor",
        "runtime": "torch", "canonical_solution": CANON, "time_limit_ms": 3000,
        "runtime_config": {"random_tests": 3, "dims": {"N": [1, 6], "D": [1, 6]},
                           "inputs": {"x": {"$random": {"shape": ["N", "D"],
                                                        "std": [0.5, 5]}}}}}
TESTS = [{"name": "ex", "input": {"x": [[1.0, 2.0, 3.0]]}},
         {"name": "hid", "input": {"x": {"$random": {"shape": [4, 5]}}}, "hidden": True}]


@needs_torch
@pytest.mark.slow
def test_a_different_correct_implementation_passes_with_fresh_random_tests():
    code = ("def softmax_rows(x):\n"   # `torch` is injected, as TreeNode is for trees
            "    e = (x - x.max(-1, keepdim=True).values).exp()\n"
            "    return e / e.sum(-1, keepdim=True)\n")
    g = run_submission(code, PROB, TESTS)
    assert g.solved, [(r.name, r.error) for r in g.results]
    assert [r.name for r in g.results] == ["ex", "hid", "random-1", "random-2", "random-3"]
    assert all(r.hidden for r in g.results[1:])
    assert g.score == 100


@needs_torch
@pytest.mark.slow
@pytest.mark.parametrize(("code", "needle"), [
    ("def softmax_rows(x):\n    return torch.softmax(x, dim=0)\n", "values differ"),
    ("def softmax_rows(x):\n    return torch.softmax(x.double(), -1)\n", "dtype float64"),
    ("def softmax_rows(x):\n    return torch.softmax(x, -1).tolist()\n",
     "expected a float32 tensor"),
    ("def softmax_rows(x):\n    return torch.softmax(x, -1).unsqueeze(0)\n", "shape"),
])
def test_wrong_answers_say_why(code, needle):
    g = run_submission(code, PROB, TESTS)
    assert not g.solved
    assert g.results[0].status == "wrong" and needle in g.results[0].error


@needs_torch
@pytest.mark.slow
def test_a_bad_torch_block_is_a_problem_bug_on_every_test():
    prob = {**PROB, "runtime_config": {"rtol": "loose"}}
    g = run_submission(CANON, prob, TESTS)
    assert all(r.status == "error" and "a problem bug" in r.error for r in g.results)


@needs_torch
@pytest.mark.slow
def test_a_generator_that_overflows_is_a_problem_bug_not_a_crash():
    prob = {**PROB, "runtime_config": {**PROB["runtime_config"], "inputs": {
        "x": {"$random": {"shape": [3], "std": 1e9, "step": 1e-300}}}}}
    g = run_submission(CANON, prob, TESTS)
    assert not g.solved
    assert any(r.name == "random" and "generator is invalid" in r.error
               for r in g.results)


@needs_torch
@pytest.mark.slow
def test_a_hang_is_a_per_test_timeout_not_a_dead_run():
    code = ("def softmax_rows(x):\n"
            "    if x.shape[0] == 1:\n        return torch.softmax(x, -1)\n"
            "    while True:\n        pass\n")
    prob = {**PROB, "time_limit_ms": 500, "runtime_config": {}}
    g = run_submission(code, prob, TESTS)
    assert [r.status for r in g.results] == ["passed", "timeout"]


@needs_torch
@pytest.mark.slow
def test_a_broken_reference_is_reported_as_a_problem_bug():
    prob = {**PROB, "runtime_config": {},
            "canonical_solution": "def softmax_rows(x):\n    raise RuntimeError('oops')\n"}
    g = run_submission(CANON, prob, TESTS)
    assert not g.solved
    assert all("reference solution failed" in r.error for r in g.results)
    assert not any("oops" in r.error for r in g.results)  # its traceback stays server-side


@needs_torch
@pytest.mark.slow
def test_the_canonical_is_not_in_the_submissions_process_or_run_dir():
    """The canonical runs in its own sandbox. This pins the run directory and
    the process only: on the subprocess backend the canonical is still
    readable from content/ on disk (docs/torch-runtime.md, "Trust model")."""
    code = ("import os, sys\n"
            "def softmax_rows(x):\n"
            "    here = os.listdir('.')\n"
            "    src = ''.join(open(f).read() for f in here if f.endswith('.py'))\n"
            "    assert 'dim=-1' not in src.replace(open('solution.py').read(), ''), here\n"
            "    assert not any('canon' in m for m in sys.modules)\n"
            "    return torch.softmax(x, dim=-1)\n")
    g = run_submission(code, PROB, TESTS)
    assert g.solved, [(r.name, r.error) for r in g.results]


@needs_torch
@pytest.mark.slow
def test_the_pilot_problem_grades_its_canonical_and_rejects_a_naive_one():
    prob = content.load_problem_dir(PILOT)
    g = run_submission(prob["canonical_solution"], prob, prob["tests"])
    assert g.solved, [(r.name, r.error) for r in g.results if not r.passed]
    assert g.total_count == len(prob["tests"]) + 5
    naive = ("import torch\n\ndef clip_loss(image_feat, text_feat, temperature):\n"
             "    u = image_feat / image_feat.norm(dim=1, keepdim=True)\n"
             "    v = text_feat / text_feat.norm(dim=1, keepdim=True)\n"
             "    e = (u @ v.T / temperature).exp()\n"
             "    d = e.diagonal()\n"
             "    return -((d / e.sum(1)).log().mean() + (d / e.sum(0)).log().mean()) / 2\n")
    g = run_submission(naive, prob, prob["tests"])
    failed = {r.name for r in g.results if not r.passed}
    assert {"aligned-pairs-tiny-temperature", "low-dim-tiny-temperature"} <= failed


@needs_torch
@pytest.mark.slow
def test_admin_verify_reports_a_torch_run_including_its_random_tests():
    """Regression: the admin verify view indexed stored tests by result position,
    and a torch run has more results than stored tests (the random draws) — a
    500 on the edit page's "Run" button, found on the real server."""
    from app.routers.admin_problems import VerifyBody, _run_verify

    prob = content.load_problem_dir(PILOT)
    body = VerifyBody(
        code=prob["canonical_solution"], function_name="clip_loss",
        params="image_feat: Tensor\ntext_feat: Tensor\ntemperature: float",
        return_type="Tensor", compare="close", tests_json=json.dumps(prob["tests"]))
    out = _run_verify(body, ("torch", prob["runtime_config"]))
    assert out["solved"] and out["total_count"] == len(prob["tests"]) + 5
    assert [r["name"] for r in out["results"][-5:]] == [f"random-{i}" for i in range(1, 6)]
    assert all(r["expected"] is None for r in out["results"])


# --- security review (2026-11-20): bounded work in the trusted parent --------
@pytest.mark.parametrize("value", [
    {"$random": {"shape": [10_000_000, 0]}},
    {"$random": {"shape": [100_000, 100_000, 0]}},
    {"$tensor": {"data": [], "shape": [10_000_000, 0]}},
])
@pytest.mark.parametrize("ptype", ["float", "Tensor"])
def test_a_zero_size_dim_cannot_smuggle_a_huge_structure(value, ptype):
    import time
    t = time.perf_counter()
    with pytest.raises(SpecError, match="too large"):
        materialize_value(value, ptype, seed=0)
    assert time.perf_counter() - t < 0.5


def test_random_tests_per_run_are_capped():
    with pytest.raises(SpecError, match="random_tests"):
        generated_inputs({"random_tests": 10_000, "inputs": {"x": 1.0}}, T, seed=0)


@needs_torch
def test_a_run_wide_input_budget_refuses_before_any_sandbox_starts():
    import time
    tests = [{"name": f"t{i}", "input": {"x": {"$random": {"shape": [50_000]}}}}
             for i in range(200)]
    t = time.perf_counter()
    g = run_submission(CANON, PROB, tests)
    assert time.perf_counter() - t < 5
    assert not g.solved and "too large in total" in g.results[0].error


def test_a_huge_untrusted_shape_is_rejected_cheaply():
    import time
    hostile = {"$tensor": {"shape": [2**30 - 1] * 88_000, "dtype": "float32", "data": []}}
    t = time.perf_counter()
    assert compare(hostile, _t([1.0]))[0] is False
    assert time.perf_counter() - t < 0.1


def test_a_result_json_nested_past_the_parser_reads_as_no_result(tmp_path):
    from app.executor import sandbox
    (tmp_path / "result.json").write_text("[" * 200_000)
    assert sandbox.read_results(str(tmp_path)) is None


@needs_torch
@pytest.mark.slow
def test_a_huge_sparse_answer_is_refused_before_it_is_densified():
    code = ("def softmax_rows(x):\n"
            "    i = torch.tensor([[0], [0]])\n"
            "    return torch.sparse_coo_tensor(i, torch.tensor([1.0]), (200000, 200000))\n")
    g = run_submission(code, {**PROB, "runtime_config": {}}, TESTS[:1])
    assert g.results[0].status == "error" and "capped" in g.results[0].error


@needs_torch
@pytest.mark.slow
def test_a_solution_cannot_sabotage_the_decoder_for_later_tests():
    """Test 1 monkey-patches torch.tensor to hang. Once that made test 2's input
    decode hang (bounded only by the per-test alarm, which covers decoding).
    The codec now captures every torch callable it uses before the solution
    loads, and test 2 is decoded and graded normally."""
    import time
    code = ("import time\n"
            "def softmax_rows(x):\n"
            "    torch.tensor = lambda *a, **k: time.sleep(1e6)\n"
            "    torch.Tensor.reshape = lambda *a, **k: time.sleep(1e6)\n"
            "    return torch.softmax(x, -1)\n")
    prob = {**PROB, "time_limit_ms": 1000, "runtime_config": {}}
    t = time.perf_counter()
    g = run_submission(code, prob, TESTS)
    assert [r.status for r in g.results] == ["passed", "passed"]
    assert time.perf_counter() - t < 15


# --- the docker backend -------------------------------------------------------
def _torch_image_ready() -> bool:
    import shutil
    if shutil.which("docker") is None:
        return False
    probe = subprocess.run(["docker", "image", "inspect", settings.TORCH_DOCKER_IMAGE],
                           capture_output=True, check=False)
    return probe.returncode == 0


needs_torch_image = pytest.mark.skipif(
    not _torch_image_ready(),
    reason="needs docker and the lootcode-runner-torch image "
           "(docker build -f infra/runner-torch.Dockerfile -t lootcode-runner-torch .)")


@pytest.fixture
def docker_backend(monkeypatch):
    monkeypatch.setattr(settings, "EXECUTOR_BACKEND", "docker")
    assert unavailable_reason() is None


@needs_torch_image
@pytest.mark.slow
def test_docker_grades_the_pilot_like_the_subprocess_backend(docker_backend):
    prob = content.load_problem_dir(PILOT)
    g = run_submission(prob["canonical_solution"], prob, prob["tests"])
    assert g.solved, [(r.name, r.error) for r in g.results if not r.passed]
    one_way = ("import torch.nn.functional as F\n"
               "def clip_loss(image_feat, text_feat, temperature):\n"
               "    L = F.normalize(image_feat, dim=-1) @ F.normalize(text_feat, dim=-1).T\n"
               "    return F.cross_entropy(L / temperature, torch.arange(L.shape[0]))\n")
    g = run_submission(one_way, prob, prob["tests"])
    first_bad = next(r for r in g.results if not r.passed)
    assert "values differ" in first_bad.error


@needs_torch_image
@pytest.mark.slow
def test_docker_hides_the_canonical_and_the_host(docker_backend):
    """What the subprocess backend cannot promise (docs/torch-runtime.md, "Trust
    model"): the submission's container mounts only its own run directory, has
    its own PID namespace, no network and no GPU, so the canonical is neither on
    its disk nor in its process table."""
    canon_path = str(PILOT / "solution" / "solution.py")
    code = ("import os, socket\n"
            "def softmax_rows(x):\n"
            f"    assert not os.path.exists({canon_path!r})\n"
            f"    assert not os.path.exists({str(ROOT)!r})\n"
            "    assert sorted(os.listdir('/sandbox')) <= ['__pycache__', '_lc_core_harness.py',"
            " 'harness.py', 'payload.json', 'solution.py'], os.listdir('/sandbox')\n"
            "    assert [p for p in os.listdir('/proc') if p.isdigit()] == ['1']\n"
            "    assert not torch.cuda.is_available()\n"
            "    try:\n"
            "        socket.create_connection(('1.1.1.1', 53), timeout=2)\n"
            "        raise AssertionError('network reachable')\n"
            "    except OSError:\n"
            "        pass\n"
            "    return torch.softmax(x, dim=-1)\n")
    g = run_submission(code, PROB, TESTS)
    assert g.solved, [(r.name, r.error) for r in g.results if not r.passed]


@needs_torch_image
@pytest.mark.slow
def test_docker_contains_a_memory_hog_and_a_hang(docker_backend):
    hog = ("def softmax_rows(x):\n"
           "    return torch.empty(2**30, dtype=torch.float32).fill_(1.0).sum()\n")
    g = run_submission(hog, {**PROB, "runtime_config": {}}, TESTS[:1])
    assert not g.solved and g.results[0].status in ("error", "timeout")
    hang = ("def softmax_rows(x):\n"
            "    if x.shape[0] == 1:\n        return torch.softmax(x, -1)\n"
            "    while True:\n        pass\n")
    g = run_submission(hang, {**PROB, "time_limit_ms": 500, "runtime_config": {}}, TESTS)
    assert [r.status for r in g.results] == ["passed", "timeout"]
