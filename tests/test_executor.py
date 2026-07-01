"""Executor tests: correctness grading plus adversarial inputs (TLE, errors).

These run the real subprocess sandbox, so they only pass on POSIX.
"""
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from app.content import load_problem_dir
from app.executor import run_submission

REPO_ROOT = Path(__file__).resolve().parent.parent

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


# --- rich types: TreeNode (decode level-order array <-> object) -----------
def _tn_problem(function_name, params, return_type, time_limit_ms=3000):
    return NS(function_name=function_name, params=params, return_type=return_type,
              time_limit_ms=time_limit_ms, memory_limit_mb=512, points=100, compare="exact")


SUM_VALUES = (
    "def treeSum(root):\n"
    "    if root is None:\n"
    "        return 0\n"
    "    return root.value + treeSum(root.left) + treeSum(root.right)\n"
)


def test_treenode_input_is_decoded_to_object():
    prob = _tn_problem("treeSum", [{"name": "root", "type": "TreeNode"}], "int")
    tests = [
        NS(name="t1", input={"root": [1, 2, 3]}, expected=6, weight=1, hidden=False),
        NS(name="empty", input={"root": []}, expected=0, weight=1, hidden=True),
    ]
    assert run_submission(SUM_VALUES, prob, tests).solved


INVERT = (
    "def invert(root):\n"
    "    if root is None:\n"
    "        return None\n"
    "    root.left, root.right = invert(root.right), invert(root.left)\n"
    "    return root\n"
)


def test_treenode_return_is_encoded_with_holes_and_trailing_trim():
    prob = _tn_problem("invert", [{"name": "root", "type": "TreeNode"}], "TreeNode")
    tests = [
        NS(name="basic", input={"root": [1, 2, 3]}, expected=[1, 3, 2],
           weight=1, hidden=False),
        # 1->(2->4), 3  inverts to  1->3, (2 with right=4); inner Nones kept,
        # trailing Nones trimmed.
        NS(name="holes", input={"root": [1, 2, 3, 4]},
           expected=[1, 3, 2, None, None, None, 4], weight=1, hidden=True),
        NS(name="empty", input={"root": []}, expected=[], weight=1, hidden=True),
    ]
    assert run_submission(INVERT, prob, tests).solved


def test_treenode_class_is_injected_and_constructible():
    prob = _tn_problem("f", [{"name": "root", "type": "TreeNode"}], "TreeNode")
    code = "def f(root):\n    return TreeNode(7, TreeNode(8), TreeNode(9))\n"
    tests = [NS(name="t", input={"root": []}, expected=[7, 8, 9], weight=1, hidden=False)]
    assert run_submission(code, prob, tests).solved


def test_treenode_none_return_is_empty_list():
    prob = _tn_problem("f", [{"name": "root", "type": "TreeNode"}], "TreeNode")
    code = "def f(root):\n    return None\n"
    tests = [NS(name="t", input={"root": [1]}, expected=[], weight=1, hidden=False)]
    assert run_submission(code, prob, tests).solved


def test_cyclic_tree_return_does_not_hang():
    # A returned node graph with a cycle must be bounded (node cap) / killed by the
    # per-test alarm — never hang the harness.
    prob = _tn_problem("f", [{"name": "root", "type": "TreeNode"}], "TreeNode",
                       time_limit_ms=5000)
    code = "def f(root):\n    a = TreeNode(1)\n    a.left = a\n    return a\n"
    tests = [NS(name="t", input={"root": [1]}, expected=[1], weight=1, hidden=False)]
    graded = run_submission(code, prob, tests)
    assert not graded.solved
    assert graded.results[0].status in ("error", "timeout")


def test_migrated_tree_problems_pass_canonical():
    for slug in ("invert-binary-tree", "maximum-depth-of-binary-tree", "same-tree"):
        d = load_problem_dir(REPO_ROOT / "content" / "problems" / slug)
        prob = NS(function_name=d["function_name"], params=d["params"],
                  return_type=d["return_type"], compare=d["compare"],
                  time_limit_ms=d["time_limit_ms"], memory_limit_mb=d["memory_limit_mb"],
                  points=d["points"])
        tests = [NS(name=t["name"], input=t["input"], expected=t["expected"],
                    weight=t["weight"], hidden=t["hidden"]) for t in d["tests"]]
        assert run_submission(d["canonical_solution"], prob, tests).solved, slug
