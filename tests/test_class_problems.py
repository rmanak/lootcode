"""Class-based ("design") problem tests: the harness instantiates a class and
replays a sequence of method calls against one instance, collecting one output
per call. These run the real subprocess sandbox, so they only pass on POSIX.

See specs/problem-schema.md (class kind) and docs/design-problems.md.
"""
from types import SimpleNamespace as NS

from app.executor import run_submission


def _class_problem(class_name, ctor_params, methods, *, compare="exact",
                   time_limit_ms=3000):
    """A minimal class-problem stand-in with the attrs run_submission reads."""
    return NS(
        kind="class", function_name="", return_type="",
        params=ctor_params, class_name=class_name, class_methods=methods,
        time_limit_ms=time_limit_ms, memory_limit_mb=512, points=100,
        compare=compare,
    )


def _test(name, operations, args, expected, hidden=False):
    return NS(name=name, input={"operations": operations, "args": args},
              expected=expected, weight=1, hidden=hidden)


# --- Min Stack: constructor + void + value-returning methods ------------------
MIN_STACK = '''
class MinStack:
    def __init__(self):
        self.s = []
        self.m = []
    def push(self, val):
        self.s.append(val)
        self.m.append(val if not self.m else min(val, self.m[-1]))
    def pop(self):
        self.s.pop(); self.m.pop()
    def top(self):
        return self.s[-1]
    def getMin(self):
        return self.m[-1]
'''

MIN_STACK_METHODS = [
    {"name": "push", "params": [{"name": "val", "type": "int"}], "returns": {"type": "void"}},
    {"name": "pop", "params": [], "returns": {"type": "void"}},
    {"name": "top", "params": [], "returns": {"type": "int"}},
    {"name": "getMin", "params": [], "returns": {"type": "int"}},
]


def _min_stack_test():
    return _test(
        "ex",
        ["MinStack", "push", "push", "push", "getMin", "pop", "top", "getMin"],
        [[], [-2], [0], [-3], [], [], [], []],
        [None, None, None, None, -3, None, 0, -2],
    )


def test_class_ctor_void_and_returning_methods():
    prob = _class_problem("MinStack", [], MIN_STACK_METHODS)
    graded = run_submission(MIN_STACK, prob, [_min_stack_test()])
    assert graded.solved
    assert graded.results[0].returned == [None, None, None, None, -3, None, 0, -2]


def test_wrong_class_not_solved():
    # getMin returns the wrong thing (top instead of min).
    bad = MIN_STACK.replace("return self.m[-1]", "return self.s[-1]")
    prob = _class_problem("MinStack", [], MIN_STACK_METHODS)
    graded = run_submission(bad, prob, [_min_stack_test()])
    assert not graded.solved
    assert graded.results[0].status == "wrong"


def test_function_instead_of_class_reports_error():
    code = "def minStack(operations):\n    return []\n"
    prob = _class_problem("MinStack", [], MIN_STACK_METHODS)
    graded = run_submission(code, prob, [_min_stack_test()])
    assert graded.results[0].status == "error"
    assert "must define a class named `MinStack`" in (graded.results[0].error or "")


def test_unknown_method_in_test_is_error():
    # The test calls a method the problem's method list doesn't declare.
    prob = _class_problem("MinStack", [], MIN_STACK_METHODS)
    t = _test("ex", ["MinStack", "peek"], [[], []], [None, 0])
    graded = run_submission(MIN_STACK, prob, [t])
    assert graded.results[0].status == "error"
    assert "unknown method" in (graded.results[0].error or "").lower()


def test_class_method_timeout():
    code = ("class Spin:\n"
            "    def __init__(self):\n        pass\n"
            "    def go(self):\n        \n        while True:\n            pass\n")
    prob = _class_problem(
        "Spin", [],
        [{"name": "go", "params": [], "returns": {"type": "void"}}],
        time_limit_ms=1000)
    t = _test("ex", ["Spin", "go"], [[], []], [None, None])
    graded = run_submission(code, prob, [t])
    assert graded.results[0].status == "timeout"


def test_non_json_serializable_return_is_error():
    code = ("class Box:\n"
            "    def __init__(self):\n        pass\n"
            "    def get(self):\n        return object()\n")
    prob = _class_problem(
        "Box", [],
        [{"name": "get", "params": [], "returns": {"type": "any"}}])
    t = _test("ex", ["Box", "get"], [[], []], [None, None])
    graded = run_submission(code, prob, [t])
    assert graded.results[0].status == "error"


# --- TreeNode constructor argument (BST iterator) ----------------------------
BST = '''
class BSTIterator:
    def __init__(self, root):
        self.vals = []
        stack, node = [], root
        while stack or node:
            while node:
                stack.append(node); node = node.left
            node = stack.pop()
            self.vals.append(node.value)
            node = node.right
        self.i = 0
    def next(self):
        v = self.vals[self.i]; self.i += 1; return v
    def hasNext(self):
        return self.i < len(self.vals)
'''


def test_class_with_treenode_constructor_arg():
    prob = _class_problem(
        "BSTIterator", [{"name": "root", "type": "TreeNode"}],
        [{"name": "next", "params": [], "returns": {"type": "int"}},
         {"name": "hasNext", "params": [], "returns": {"type": "bool"}}])
    t = _test(
        "ex",
        ["BSTIterator", "next", "next", "hasNext", "next", "hasNext"],
        [[[7, 3, 15, None, None, 9, 20]], [], [], [], [], []],
        [None, 3, 7, True, 9, True],
    )
    graded = run_submission(BST, prob, [t])
    assert graded.solved


# --- Injected Iterator helper type (peeking iterator) ------------------------
PEEK = '''
class PeekingIterator:
    def __init__(self, iterator):
        self.it = iterator
        self._has = iterator.hasNext()
        self._peek = iterator.next() if self._has else None
    def peek(self):
        return self._peek
    def next(self):
        v = self._peek
        self._has = self.it.hasNext()
        self._peek = self.it.next() if self._has else None
        return v
    def hasNext(self):
        return self._has
'''


def test_injected_iterator_type():
    prob = _class_problem(
        "PeekingIterator", [{"name": "nums", "type": "Iterator"}],
        [{"name": "next", "params": [], "returns": {"type": "int"}},
         {"name": "peek", "params": [], "returns": {"type": "int"}},
         {"name": "hasNext", "params": [], "returns": {"type": "bool"}}])
    t = _test(
        "ex",
        ["PeekingIterator", "next", "peek", "next", "next", "hasNext"],
        [[[1, 2, 3]], [], [], [], [], []],
        [None, 1, 2, 2, 3, False],
    )
    graded = run_submission(PEEK, prob, [t])
    assert graded.solved


# --- Injected NestedInteger helper type (flatten nested list) ----------------
NEST = '''
class NestedIterator:
    def __init__(self, nestedList):
        self.stack = list(reversed(nestedList))
    def _prime(self):
        while self.stack and not self.stack[-1].isInteger():
            for e in reversed(self.stack.pop().getList()):
                self.stack.append(e)
    def next(self):
        self._prime(); return self.stack.pop().getInteger()
    def hasNext(self):
        self._prime(); return len(self.stack) > 0
'''


def test_injected_nested_integer_type():
    prob = _class_problem(
        "NestedIterator", [{"name": "nestedList", "type": "List<NestedInteger>"}],
        [{"name": "next", "params": [], "returns": {"type": "int"}},
         {"name": "hasNext", "params": [], "returns": {"type": "bool"}}])
    # Flatten [[1,1],2,[1,1]] -> 1,1,2,1,1
    t = _test(
        "ex",
        ["NestedIterator", "hasNext", "next", "next", "next", "next", "next", "hasNext"],
        [[[[1, 1], 2, [1, 1]]], [], [], [], [], [], [], []],
        [None, True, 1, 1, 2, 1, 1, False],
    )
    graded = run_submission(NEST, prob, [t])
    assert graded.solved


def test_pilot_problem_seeds_and_grades(tmp_path=None):
    """The on-disk pilot loads as a class problem and its canonical passes."""
    from pathlib import Path

    from app.content import load_problem_dir
    d = Path(__file__).resolve().parent.parent / "content" / "problems" / "design-browser-history"
    if not d.exists():  # pilot not present in this checkout
        return
    data = load_problem_dir(d)
    assert data["kind"] == "class"
    prob = _class_problem(data["class_name"], data["params"], data["class_methods"])
    tests = [_test(t["name"], t["input"]["operations"], t["input"]["args"],
                   t["expected"], t.get("hidden", False)) for t in data["tests"]]
    graded = run_submission(data["canonical_solution"], prob, tests)
    assert graded.solved
