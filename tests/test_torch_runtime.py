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
def test_a_sabotaged_decoder_times_out_per_test_not_per_run():
    """Test 1 monkey-patches torch.tensor; test 2's input decode then hangs.
    The per-test alarm now covers decoding, so it is a 1 s timeout rather than
    a stall until the overall kill (~40 s)."""
    import time
    code = ("import time\n"
            "def softmax_rows(x):\n"
            "    torch.tensor = lambda *a, **k: time.sleep(1e6)\n"
            "    return torch.softmax(x, -1)\n")
    prob = {**PROB, "time_limit_ms": 1000, "runtime_config": {}}
    t = time.perf_counter()
    g = run_submission(code, prob, TESTS)
    assert [r.status for r in g.results] == ["passed", "timeout"]
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
