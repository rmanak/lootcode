"""Executor tests: correctness grading plus adversarial inputs (TLE, errors).

These run the real subprocess sandbox, so they only pass on POSIX.
"""
import time
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from app.content import load_problem_dir
from app.executor import run_submission

# Every test here spawns a real sandbox subprocess.
pytestmark = pytest.mark.slow

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


def test_debug_print_is_captured():
    code = CANONICAL.replace("    seen = {}\n",
                             "    print('debug', nums)\n    seen = {}\n")
    graded = run_submission(code, _problem(), _tests())
    assert graded.solved
    assert "debug [2, 7, 11, 15]" in graded.results[0].stdout


def test_module_level_print_is_captured():
    graded = run_submission("print('at import')\n" + CANONICAL, _problem(), _tests())
    assert graded.solved
    assert "at import" in graded.results[0].stdout


def test_closing_stdout_does_not_kill_the_run():
    """Capturing stdout must survive the solution closing it.

    `sys.stdout` is the harness's own capture buffer while user code runs, so a
    `close()` used to make the later read raise, take the harness down, and lose
    every result — both at module level and inside the function.
    """
    at_import = "import sys\nsys.stdout.close()\n" + CANONICAL
    assert run_submission(at_import, _problem(), _tests()).solved

    in_function = CANONICAL.replace(
        "    seen = {}\n", "    import sys\n    sys.stdout.close()\n    seen = {}\n")
    assert run_submission(in_function, _problem(), _tests()).solved


def test_module_level_print_bomb_is_truncated_not_fatal():
    """Printing without bound at import time is truncated, not an OOM kill."""
    code = "for _ in range(100000): print('A' * 100000)\n" + CANONICAL
    graded = run_submission(code, _problem(), _tests())
    assert graded.solved, [r.error for r in graded.results]


def test_oversized_return_reports_a_real_reason():
    """A return too big for result.json must explain itself, not come back as
    the generic "the run was stopped" (which is what unbudgeted `returned`
    values produced before the write path degraded in steps)."""
    code = "def twoSum(nums, target):\n    return ['A' * 1000000] * 20\n"
    graded = run_submission(code, _problem(), _tests())
    assert not graded.solved
    assert "returned too much data" in (graded.results[0].error or "")


def test_heavy_printing_still_grades():
    """A solution that prints in a loop must be graded, not killed.

    Regression: stdout was capped per test but the parent's file-size rlimit
    covered the whole result.json, so N tests' worth of output blew the limit
    mid-write and every test came back "the run was stopped".
    """
    code = CANONICAL.replace(
        "    seen = {}\n",
        "    for _ in range(1000):\n        print('x' * 100)\n    seen = {}\n")
    graded = run_submission(code, _problem(), _tests())
    assert graded.solved, [r.error for r in graded.results]
    assert "truncated" in graded.results[0].stdout
    # The run-wide budget holds: total captured output stays near the cap.
    assert sum(len(r.stdout) for r in graded.results) < 128 * 1024


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


# --- rich types: ListNode (decode flat value array <-> singly-linked chain) ---
def _ll_problem(function_name, params, return_type, time_limit_ms=3000):
    return NS(function_name=function_name, params=params, return_type=return_type,
              time_limit_ms=time_limit_ms, memory_limit_mb=512, points=100, compare="exact")


SUM_LIST = (
    "def listSum(head):\n"
    "    total = 0\n"
    "    while head is not None:\n"
    "        total += head.val\n"
    "        head = head.next\n"
    "    return total\n"
)


def test_listnode_input_is_decoded_to_object():
    prob = _ll_problem("listSum", [{"name": "head", "type": "ListNode"}], "int")
    tests = [
        NS(name="t1", input={"head": [1, 2, 3]}, expected=6, weight=1, hidden=False),
        NS(name="empty", input={"head": []}, expected=0, weight=1, hidden=True),
    ]
    assert run_submission(SUM_LIST, prob, tests).solved


REVERSE_LIST = (
    "def reverseList(head):\n"
    "    prev = None\n"
    "    while head is not None:\n"
    "        head.next, prev, head = prev, head, head.next\n"
    "    return prev\n"
)


def test_listnode_return_is_encoded_to_flat_array():
    prob = _ll_problem("reverseList", [{"name": "head", "type": "ListNode"}], "ListNode")
    tests = [
        NS(name="basic", input={"head": [1, 2, 3, 4, 5]}, expected=[5, 4, 3, 2, 1],
           weight=1, hidden=False),
        NS(name="empty", input={"head": []}, expected=[], weight=1, hidden=True),
    ]
    assert run_submission(REVERSE_LIST, prob, tests).solved


def test_listnode_class_is_injected_and_constructible():
    prob = _ll_problem("f", [{"name": "head", "type": "ListNode"}], "ListNode")
    code = "def f(head):\n    return ListNode(7, ListNode(8, ListNode(9)))\n"
    tests = [NS(name="t", input={"head": []}, expected=[7, 8, 9], weight=1, hidden=False)]
    assert run_submission(code, prob, tests).solved


def test_listnode_none_return_is_empty_list():
    prob = _ll_problem("f", [{"name": "head", "type": "ListNode"}], "ListNode")
    code = "def f(head):\n    return None\n"
    tests = [NS(name="t", input={"head": [1]}, expected=[], weight=1, hidden=False)]
    assert run_submission(code, prob, tests).solved


def test_cyclic_list_return_does_not_hang():
    # A returned chain with a cycle must be bounded (node cap) / killed by the
    # per-test alarm — never hang the harness while walking `.next`.
    prob = _ll_problem("f", [{"name": "head", "type": "ListNode"}], "ListNode",
                       time_limit_ms=5000)
    code = ("def f(head):\n"
            "    a = ListNode(1)\n"
            "    a.next = a\n"
            "    return a\n")
    tests = [NS(name="t", input={"head": [1]}, expected=[1], weight=1, hidden=False)]
    graded = run_submission(code, prob, tests)
    assert not graded.solved
    assert graded.results[0].status in ("error", "timeout")


# --- rich types: DoublyLinkedList (Node with val/prev/next) -------------------
def test_doubly_linked_prev_pointers_are_wired():
    # Walk to the tail via .next, then back via .prev summing values: only correct
    # if the harness set both links when decoding the flat array.
    prob = _ll_problem("f", [{"name": "head", "type": "DoublyLinkedList"}], "int")
    code = ("def f(head):\n"
            "    if head is None:\n"
            "        return 0\n"
            "    node = head\n"
            "    while node.next is not None:\n"
            "        node = node.next\n"
            "    total = 0\n"
            "    while node is not None:\n"
            "        total += node.val\n"
            "        node = node.prev\n"
            "    return total\n")
    tests = [NS(name="t", input={"head": [1, 2, 3, 4]}, expected=10, weight=1, hidden=False)]
    assert run_submission(code, prob, tests).solved


def test_doubly_linked_node_class_injected_and_returned():
    prob = _ll_problem("f", [{"name": "head", "type": "DoublyLinkedList"}],
                       "DoublyLinkedList")
    code = ("def f(head):\n"
            "    a = Node(1)\n"
            "    b = Node(2)\n"
            "    a.next = b\n"
            "    b.prev = a\n"
            "    return a\n")
    tests = [NS(name="t", input={"head": []}, expected=[1, 2], weight=1, hidden=False)]
    assert run_submission(code, prob, tests).solved


def _assert_bank_canonical_solved(slug):
    d = load_problem_dir(REPO_ROOT / "content" / "problems" / slug)
    prob = NS(function_name=d["function_name"], params=d["params"],
              return_type=d["return_type"], compare=d["compare"],
              time_limit_ms=d["time_limit_ms"], memory_limit_mb=d["memory_limit_mb"],
              points=d["points"])
    tests = [NS(name=t["name"], input=t["input"], expected=t["expected"],
                weight=t["weight"], hidden=t["hidden"]) for t in d["tests"]]
    assert run_submission(d["canonical_solution"], prob, tests).solved, slug


# --- numpy (machine-learning problems) -------------------------------------
def _np_problem(compare="close", return_type="float[]"):
    return NS(function_name="f", params=[{"name": "x", "type": "float[]"}],
              return_type=return_type, time_limit_ms=3000, memory_limit_mb=512,
              points=100, compare=compare)


def _np_tests(expected):
    return [NS(name="t", input={"x": [1.0, 2.0, 3.0]}, expected=expected,
               weight=1, hidden=False)]


def test_numpy_imports_and_computes_under_the_default_limits():
    # Without SINGLE_THREAD_ENV, OpenBLAS sizes a buffer per core at import and
    # blows through RLIMIT_AS on a many-core machine: the run dies before the
    # solution's first line, with every test reported as an error.
    code = ("import numpy as np\n"
            "def f(x):\n"
            "    a = np.outer(x, x) + np.eye(len(x))\n"
            "    return float(np.linalg.solve(a @ a, np.ones(len(x))).sum())\n")
    graded = run_submission(code, _np_problem(return_type="float"),
                            _np_tests(0.44))
    assert graded.solved, [(r.status, r.error) for r in graded.results]


def test_numpy_arrays_and_scalars_may_be_returned_as_is():
    # `return w` is the natural ML answer; the harness converts anything with a
    # .tolist() (array, np.float32, np.int64, a tuple holding them) to JSON data.
    code = ("import numpy as np\n"
            "def f(x):\n"
            "    v = np.asarray(x)\n"
            "    return np.float32(v.mean()), v * 2, np.int64(len(x))\n")
    graded = run_submission(code, _np_problem(), _np_tests([2.0, [2.0, 4.0, 6.0], 3]))
    assert graded.solved, [(r.status, r.error) for r in graded.results]


def test_close_grades_float_noise_as_correct_end_to_end():
    # Summing in a different order than whoever computed `expected` is correct
    # code; `exact` fails it, `close` doesn't.
    code = "def f(x):\n    return [0.1 + 0.2, sum(x) / 3]\n"
    assert run_submission(code, _np_problem("close"), _np_tests([0.3, 2.0])).solved
    assert not run_submission(code, _np_problem("exact"), _np_tests([0.3, 2.0])).solved


def test_an_unconvertible_return_still_reports_why():
    code = "def f(x):\n    return object()\n"
    graded = run_submission(code, _np_problem(), _np_tests([1.0]))
    assert graded.results[0].status == "error"
    assert "not JSON-serializable: object" in graded.results[0].error


def test_a_hanging_tolist_times_out_instead_of_stalling_the_run():
    # tolist() is the solution's own code, so it runs under the per-test alarm.
    code = ("class Evil:\n"
            "    def tolist(self):\n"
            "        while True:\n"
            "            pass\n"
            "def f(x):\n"
            "    return Evil()\n")
    started = time.monotonic()
    graded = run_submission(code, _np_problem(), _np_tests([1.0]))
    assert graded.results[0].status == "timeout"
    assert time.monotonic() - started < 20


def test_numpy_returns_from_a_class_problem_are_converted():
    prob = NS(kind="class", function_name="", return_type="", params=[],
              class_name="Acc", time_limit_ms=3000, memory_limit_mb=512, points=100,
              compare="close",
              class_methods=[{"name": "add", "params": [{"name": "v", "type": "float"}],
                              "returns": {"type": "float[]"}}])
    code = ("import numpy as np\n"
            "class Acc:\n"
            "    def __init__(self):\n"
            "        self.s = np.zeros(2)\n"
            "    def add(self, v):\n"
            "        self.s += v\n"
            "        return self.s.copy()\n")
    tests = [NS(name="t", input={"operations": ["Acc", "add", "add"],
                                 "args": [[], [0.5], [0.25]]},
                expected=[None, [0.5, 0.5], [0.75, 0.75]], weight=1, hidden=False)]
    graded = run_submission(code, prob, tests)
    assert graded.solved, [(r.status, r.error) for r in graded.results]


def test_class_outputs_are_recorded_when_each_call_returns():
    # A method that returns its internal list / array and mutates it on a later
    # call must still be graded on what it returned at the time (LeetCode
    # semantics), not on the object's final state.
    prob = NS(kind="class", function_name="", return_type="", params=[],
              class_name="Acc", time_limit_ms=3000, memory_limit_mb=512, points=100,
              compare="close",
              class_methods=[{"name": "add", "params": [{"name": "v", "type": "float"}],
                              "returns": {"type": "float[]"}},
                             {"name": "hist", "params": [], "returns": {"type": "float[]"}}])
    code = ("import numpy as np\n"
            "class Acc:\n"
            "    def __init__(self):\n"
            "        self.s = np.zeros(2)\n"
            "        self.h = []\n"
            "    def add(self, v):\n"
            "        self.s += v\n"
            "        self.h.append(v)\n"
            "        return self.s\n"            # the same array, mutated in place next call
            "    def hist(self):\n"
            "        return self.h\n")           # the same list, appended to next call
    tests = [NS(name="t", input={"operations": ["Acc", "add", "hist", "add", "hist"],
                                 "args": [[], [0.5], [], [0.25], []]},
                expected=[None, [0.5, 0.5], [0.5], [0.75, 0.75], [0.5, 0.25]],
                weight=1, hidden=False)]
    graded = run_submission(code, prob, tests)
    assert graded.solved, [(r.status, r.error, r.returned) for r in graded.results]


def test_class_output_that_is_not_json_names_the_method():
    prob = NS(kind="class", function_name="", return_type="", params=[],
              class_name="Box", time_limit_ms=3000, memory_limit_mb=512, points=100,
              compare="exact",
              class_methods=[{"name": "get", "params": [], "returns": {"type": "int"}}])
    code = ("class Box:\n"
            "    def __init__(self):\n"
            "        pass\n"
            "    def get(self):\n"
            "        return object()\n")
    tests = [NS(name="t", input={"operations": ["Box", "get"], "args": [[], []]},
                expected=[None, 1], weight=1, hidden=False)]
    graded = run_submission(code, prob, tests)
    assert graded.results[0].status == "error"
    assert "`get`" in graded.results[0].error


def test_a_class_return_that_hangs_while_encoding_times_out_alone():
    # Copying a class method's return runs the solution's own __iter__, so it
    # must happen under that test's alarm. Before the per-call copy it ran after
    # the alarm was disarmed, and the whole run was killed with every test lost.
    prob = NS(kind="class", function_name="", return_type="", params=[],
              class_name="Box", time_limit_ms=1000, memory_limit_mb=512, points=100,
              compare="exact",
              class_methods=[{"name": "get", "params": [{"name": "x", "type": "int"}],
                              "returns": {"type": "int[]"}}])
    code = ("class L(list):\n"
            "    def __iter__(self):\n"
            "        while True:\n"
            "            pass\n"
            "class Box:\n"
            "    def __init__(self):\n"
            "        pass\n"
            "    def get(self, x):\n"
            "        return L([x]) if x < 0 else [x]\n")
    tests = [NS(name=f"t{x}", input={"operations": ["Box", "get"], "args": [[], [x]]},
                expected=[None, [x]], weight=1, hidden=False) for x in (-1, 2)]
    started = time.monotonic()
    graded = run_submission(code, prob, tests)
    assert graded.results[0].status == "timeout"
    # The per-test alarm, not the whole-run kill (which also reports "timeout").
    assert graded.results[0].error == "Time limit exceeded."
    assert graded.results[1].passed
    assert time.monotonic() - started < 8


def test_migrated_tree_problems_pass_canonical():
    for slug in ("invert-binary-tree", "maximum-depth-of-binary-tree", "same-tree"):
        _assert_bank_canonical_solved(slug)


def test_migrated_listnode_problems_pass_canonical():
    # Singly-linked problems migrated from int[] to the ListNode rich type: the
    # canonical works with real nodes and the codec de/serializes at the boundary.
    for slug in ("reverse-linked-list", "merge-two-sorted-lists", "add-two-numbers",
                 "reverse-nodes-in-k-group", "linked-list-in-binary-tree"):
        _assert_bank_canonical_solved(slug)


@pytest.mark.slow
@pytest.mark.parametrize("plant,what", [
    ('os.symlink("/dev/zero", "result.json")', "symlink"),
    ('os.mkfifo("result.json")', "fifo"),
])
def test_a_submission_cannot_booby_trap_the_results_file(plant, what):
    """The run directory belongs to the submission by the time it runs.

    Planting a `result.json` that is not a regular file used to reach the
    *host*: a symlink to /dev/zero was read until the server process was
    OOM-killed, and a fifo blocked — first the harness writing it, then the
    server reading it — for the whole run budget. Both must now cost nothing.
    """
    code = f"import os\n{plant}\n" + CANONICAL
    started = time.monotonic()
    graded = run_submission(code, _problem(), _tests())
    assert time.monotonic() - started < 20, f"the {what} stalled the run"
    # The harness replaces what it finds, so a correct solution still grades.
    assert graded.solved, [r.status for r in graded.results]
