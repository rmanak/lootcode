"""Executor tests: correctness grading plus adversarial inputs (TLE, errors).

These run the real subprocess sandbox, so they only pass on POSIX.
"""
from types import SimpleNamespace as NS

import pytest

from app.executor import run_submission

PARAMS = [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}]

CANONICAL = (
    "def twoSum(nums, target):\n"
    "    seen = {}\n"
    "    for i, n in enumerate(nums):\n"
    "        if target - n in seen:\n"
    "            return [seen[target - n], i]\n"
    "        seen[n] = i\n"
    "    return []\n"
)


def _problem(time_limit_ms=3000):
    return NS(function_name="twoSum", params=PARAMS, time_limit_ms=time_limit_ms,
              memory_limit_mb=512, points=100)


def _tests():
    return [
        NS(name="t1", input={"nums": [2, 7, 11, 15], "target": 9},
           expected=[0, 1], weight=1, hidden=False),
        NS(name="t2", input={"nums": [3, 3], "target": 6},
           expected=[0, 1], weight=1, hidden=True),
    ]


def test_correct_solution_is_solved():
    graded = run_submission(CANONICAL, _problem(), _tests())
    assert graded.solved
    assert graded.passed_count == 2
    assert graded.score == 100


def test_wrong_answer_is_not_solved():
    code = "def twoSum(nums, target):\n    return [0, 0]\n"
    graded = run_submission(code, _problem(), _tests())
    assert not graded.solved
    assert graded.results[0].status == "wrong"


def test_infinite_loop_times_out():
    code = "def twoSum(nums, target):\n    while True:\n        pass\n"
    one = [NS(name="t", input={"nums": [1, 2], "target": 3},
              expected=[0, 1], weight=1, hidden=False)]
    graded = run_submission(code, _problem(time_limit_ms=1000), one)
    assert not graded.solved
    assert graded.results[0].status == "timeout"


def test_runtime_error_is_reported():
    code = "def twoSum(nums, target):\n    raise ValueError('boom')\n"
    graded = run_submission(code, _problem(), _tests())
    assert graded.results[0].status == "error"
    assert "boom" in (graded.results[0].error or "")


def test_missing_function_is_error():
    code = "def somethingElse(nums, target):\n    return []\n"
    graded = run_submission(code, _problem(), _tests())
    assert graded.results[0].status == "error"


# --- comparison modes (statement/judge consistency) ----------------------
def _problem_mode(mode):
    return NS(function_name="twoSum", params=PARAMS, time_limit_ms=3000,
              memory_limit_mb=512, points=100, compare=mode)


# Returns the pair in the OPPOSITE order to the canonical (larger index first).
REVERSED_PAIR = (
    "def twoSum(nums, target):\n"
    "    seen = {}\n"
    "    for i, n in enumerate(nums):\n"
    "        if target - n in seen:\n"
    "            return [i, seen[target - n]]\n"
    "        seen[n] = i\n"
    "    return []\n"
)
ONE = [NS(name="t1", input={"nums": [2, 7, 11, 15], "target": 9},
          expected=[0, 1], weight=1, hidden=False)]


def test_unordered_accepts_reordered_answer():
    assert run_submission(REVERSED_PAIR, _problem_mode("unordered"), ONE).solved


def test_exact_rejects_reordered_answer():
    assert not run_submission(REVERSED_PAIR, _problem_mode("exact"), ONE).solved


def test_set_of_lists_accepts_shuffled_nested():
    prob = NS(function_name="f", params=[{"name": "x", "type": "int[]"}],
              time_limit_ms=3000, memory_limit_mb=512, points=100, compare="set_of_lists")
    tests = [NS(name="t", input={"x": [1]}, expected=[[1, 2], [3, 4]], weight=1, hidden=False)]
    code = "def f(x):\n    return [[4, 3], [2, 1]]\n"  # outer + inner reversed
    assert run_submission(code, prob, tests).solved
