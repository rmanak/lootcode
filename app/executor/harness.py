"""Sandbox harness — runs INSIDE the isolated subprocess/container.

Trusted code (part of the sandbox boundary). Must not import anything from the
`app` package: it runs with a minimal environment and only the standard library.

Reads  <workdir>/payload.json  and  <workdir>/solution.py
Writes <workdir>/result.json   = {"results": [{name, status, returned?, time_ms,
                                  error?, stdout}]}

Per-test wall-clock limits are enforced with SIGALRM; the parent process applies
CPU/memory/PID/file-size rlimits and an overall kill-timeout as a backstop.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import signal
import sys
import time
import traceback
from collections import deque


class _Timeout(Exception):
    pass


def _on_alarm(signum, frame):  # noqa: ANN001
    raise _Timeout()


def _short_tb(limit: int = 2000) -> str:
    tb = traceback.format_exc()
    return tb[-limit:]


# --- Rich input/return types -------------------------------------------------
# Some problems declare a parameter or return as a custom structure (e.g.
# TreeNode) instead of a plain JSON value. The on-disk and across-the-boundary
# wire format stays a plain JSON value (a binary tree is a LeetCode-style
# level-order array with None holes); these codecs convert array<->object on the
# untrusted side so solvers work with real objects. Comparison in the trusted
# parent still happens on the JSON array, so the judge is unchanged.
#
# SECURITY: this runs in-sandbox alongside hostile code. Keep it stdlib-only,
# iterative (no recursion -> no stack-overflow DoS) and node-capped (a cyclic or
# huge returned object must not hang the harness); the per-test SIGALRM is the
# backstop and stays armed while a return value is encoded.

# Generously above any realistic tree (problems cap nodes in the 10^4 range) but
# low enough that a cyclic/hostile returned object fails fast and cheap.
_MAX_TREE_NODES = 200_000

# Same idea for linked lists: comfortably above any realistic list (problems cap
# node counts in the 10^4-10^5 range) but bounded so a cyclic/hostile returned
# chain fails fast instead of hanging while we walk `.next` forever.
_MAX_LIST_NODES = 1_000_000


class TreeNode:
    """Binary-tree node injected into solutions that declare a TreeNode param/return."""

    __slots__ = ("value", "left", "right")

    def __init__(self, value=None, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def _tree_decode(arr):
    """Level-order array (None marks a missing child) -> TreeNode, or None if empty."""
    if not arr or arr[0] is None:
        return None
    root = TreeNode(arr[0])
    q = deque([root])
    i, n = 1, len(arr)
    while q and i < n:
        cur = q.popleft()
        if i < n:
            v = arr[i]; i += 1
            if v is not None:
                cur.left = TreeNode(v); q.append(cur.left)
        if i < n:
            v = arr[i]; i += 1
            if v is not None:
                cur.right = TreeNode(v); q.append(cur.right)
    return root


def _tree_encode(node):
    """TreeNode -> level-order array with trailing Nones trimmed.

    Duck-typed on .value/.left/.right (so a user-defined equivalent node also
    works) and bounded by _MAX_TREE_NODES against cyclic/huge returns.
    """
    if node is None:
        return []
    out, q, count = [], deque([node]), 0
    while q:
        cur = q.popleft()
        if cur is None:
            out.append(None)
            continue
        count += 1
        if count > _MAX_TREE_NODES:
            raise ValueError("Returned tree is too large or contains a cycle.")
        out.append(cur.value)
        q.append(cur.left)
        q.append(cur.right)
    while out and out[-1] is None:
        out.pop()
    return out


class ListNode:
    """Singly-linked list node injected into solutions that declare a ListNode
    param/return. Matches the LeetCode convention (``val``/``next``)."""

    __slots__ = ("val", "next")

    def __init__(self, val=0, next=None):  # noqa: A002 - `next` mirrors LeetCode
        self.val = val
        self.next = next


def _list_decode(arr):
    """Flat value array -> head ListNode of a singly-linked chain, or None if empty."""
    head = nxt = None
    for v in reversed(arr or []):
        nxt = ListNode(v, head)
        head = nxt
    return head


def _list_encode(node):
    """Head ListNode -> flat value array by walking ``.next``.

    Duck-typed on ``.val``/``.next`` (so a user-defined equivalent node also works)
    and bounded by _MAX_LIST_NODES so a cyclic/huge returned chain fails fast
    instead of hanging the harness.
    """
    out, count = [], 0
    while node is not None:
        count += 1
        if count > _MAX_LIST_NODES:
            raise ValueError("Returned list is too long or contains a cycle.")
        out.append(node.val)
        node = node.next
    return out


class Node:
    """Doubly-linked list node injected into solutions that declare a doubly-linked
    param/return. Matches the LeetCode convention (``val``/``prev``/``next``)."""

    __slots__ = ("val", "prev", "next")

    def __init__(self, val=0, prev=None, next=None):  # noqa: A002 - mirrors LeetCode
        self.val = val
        self.prev = prev
        self.next = next


def _dlist_decode(arr):
    """Flat value array -> head Node of a doubly-linked chain (prev/next both set),
    or None if empty."""
    head = prev = None
    for v in arr or []:
        cur = Node(v, prev, None)
        if prev is None:
            head = cur
        else:
            prev.next = cur
        prev = cur
    return head


def _dlist_encode(node):
    """Head Node -> flat value array by walking ``.next``.

    Duck-typed on ``.val``/``.next`` and bounded by _MAX_LIST_NODES (same
    cyclic/huge-return protection as the singly-linked encoder)."""
    out, count = [], 0
    while node is not None:
        count += 1
        if count > _MAX_LIST_NODES:
            raise ValueError("Returned list is too long or contains a cycle.")
        out.append(node.val)
        node = node.next
    return out


# Bound on the number of nodes materialized from a nested-list input, so a huge
# or deeply-nested hostile payload fails fast instead of exhausting memory.
_MAX_NESTED_NODES = 1_000_000


class Iterator:
    """Read-only forward iterator over a fixed list, injected for class problems
    whose constructor takes an ``Iterator`` (e.g. peeking-iterator). Matches
    LeetCode's integer-iterator interface: ``next()`` advances and returns the
    element; ``hasNext()`` reports whether one remains. Param-only (never a
    return), so there is no encoder."""

    __slots__ = ("_data", "_i")

    def __init__(self, nums=None):
        self._data = list(nums or [])
        self._i = 0

    def hasNext(self):  # noqa: N802 - mirrors LeetCode
        return self._i < len(self._data)

    def next(self):
        v = self._data[self._i]
        self._i += 1
        return v


def _iterator_decode(arr):
    """Flat JSON array -> Iterator over its elements."""
    return Iterator(arr or [])


class NestedInteger:
    """One element of a nested list — either a single integer or a list of
    ``NestedInteger`` — injected for class problems that take a nested list
    (e.g. flatten-nested-list-iterator). Matches LeetCode's read interface."""

    __slots__ = ("_int", "_list")

    def __init__(self, value=None):
        if isinstance(value, list):
            self._int, self._list = None, value
        else:
            self._int, self._list = value, None

    def isInteger(self):  # noqa: N802 - mirrors LeetCode
        return self._list is None

    def getInteger(self):  # noqa: N802
        return self._int

    def getList(self):  # noqa: N802
        return self._list

    def add(self, ni):
        if self._list is None:
            self._list = []
        self._list.append(ni)

    def setInteger(self, value):  # noqa: N802
        self._int, self._list = value, None


def _nested_list_decode(arr):
    """Nested JSON list -> list[NestedInteger], iteratively (no recursion, so a
    deeply-nested payload can't overflow the stack) and node-capped."""
    root: list = []
    count = 0
    stack = [(arr or [], root)]  # (json list, target list[NestedInteger])
    while stack:
        jlist, target = stack.pop()
        for elem in jlist:
            count += 1
            if count > _MAX_NESTED_NODES:
                raise ValueError("Nested list is too large.")
            if isinstance(elem, list):
                ni = NestedInteger([])
                target.append(ni)
                stack.append((elem, ni._list))  # fill its children later
            else:
                target.append(NestedInteger(elem))
    return root


# type token -> (class to inject, decode JSON->object, encode object->JSON)
# Encoder is None for param-only helper types (Iterator, nested lists), which
# never appear as a declared return.
_CODECS = {
    "TreeNode": (TreeNode, _tree_decode, _tree_encode),
    "ListNode": (ListNode, _list_decode, _list_encode),
    "DoublyLinkedList": (Node, _dlist_decode, _dlist_encode),
    "Iterator": (Iterator, _iterator_decode, None),
    "Iterator<int>": (Iterator, _iterator_decode, None),
    "NestedInteger[]": (NestedInteger, _nested_list_decode, None),
    "List<NestedInteger>": (NestedInteger, _nested_list_decode, None),
}


def _load_solution(path: str, budget_s: float, inject: dict | None = None):
    """Import the user's solution.py, guarding against import-time hangs.

    `inject` maps names (e.g. "TreeNode") to objects placed in the solution's
    module globals before its top-level code runs, so user code can reference
    them at import and call time without defining them.
    """
    signal.setitimer(signal.ITIMER_REAL, budget_s)
    try:
        spec = importlib.util.spec_from_file_location("solution", path)
        module = importlib.util.module_from_spec(spec)
        for name, obj in (inject or {}).items():
            setattr(module, name, obj)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module, None
    except _Timeout:
        return None, "Import timed out (module-level code took too long)."
    except BaseException:  # noqa: BLE001 - report anything, incl. SystemExit
        return None, "Error while loading your solution:\n" + _short_tb()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def _run_one(func, params, decoders, encoder, inp, time_limit_s, max_output) -> dict:
    buf = io.StringIO()
    real_stdout = sys.stdout
    start = time.perf_counter()
    try:
        args = {p: inp[p] for p in params}
    except KeyError as exc:
        return {"status": "error", "error": f"Missing input for parameter {exc}.",
                "time_ms": 0, "stdout": ""}
    try:
        for name, decode in decoders.items():
            args[name] = decode(args[name])
    except Exception:  # noqa: BLE001 - malformed test input for a typed parameter
        return {"status": "error", "time_ms": 0,
                "error": "Could not build the typed input for this test:\n" + _short_tb(),
                "stdout": ""}
    try:
        sys.stdout = buf
        signal.setitimer(signal.ITIMER_REAL, time_limit_s)
        returned = func(**args)
        if encoder is not None:
            returned = encoder(returned)  # bounded; stays under the per-test alarm
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout
        elapsed = (time.perf_counter() - start) * 1000
        try:
            json.dumps(returned)
        except (TypeError, ValueError):
            return {"status": "error", "time_ms": elapsed,
                    "error": f"Return value is not JSON-serializable: {type(returned).__name__}",
                    "stdout": buf.getvalue()[:max_output]}
        return {"status": "ok", "returned": returned, "time_ms": elapsed,
                "stdout": buf.getvalue()[:max_output]}
    except _Timeout:
        return {"status": "timeout", "time_ms": time_limit_s * 1000,
                "error": "Time limit exceeded.", "stdout": buf.getvalue()[:max_output]}
    except BaseException:  # noqa: BLE001
        elapsed = (time.perf_counter() - start) * 1000
        return {"status": "error", "time_ms": elapsed, "error": _short_tb(),
                "stdout": buf.getvalue()[:max_output]}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout


def _positional_decoders(raw_params, inject) -> list:
    """For an ordered params list, return a list aligned to the positional args
    where each entry is a decode fn (for a rich/helper type) or None. Records any
    helper class to inject into ``inject`` (mutated in place)."""
    decs: list = []
    for p in raw_params or []:
        ptype = "" if isinstance(p, str) else (p.get("type") or "")
        codec = _CODECS.get(ptype)
        if codec:
            decs.append(codec[1])
            inject[codec[0].__name__] = codec[0]
        else:
            decs.append(None)
    return decs


def _decode_args(args, decoders) -> None:
    """Decode rich/helper-typed positional args in place (args longer or shorter
    than `decoders` is fine — extra args stay raw, missing ones are skipped)."""
    for j, dec in enumerate(decoders):
        if dec is not None and j < len(args):
            args[j] = dec(args[j])


def _run_class(cls, ctor_decoders, method_dispatch, inp, time_limit_s,
               max_output) -> dict:
    """Run one class test: instantiate `cls` then replay a sequence of method
    calls, collecting one output per call (``None`` for the constructor and for
    void methods). `method_dispatch` maps method name -> (arg-decoders, encoder).

    Mirrors `_run_one`'s contract: the whole operation sequence runs under a
    single per-test SIGALRM (LeetCode-style overall time budget), stdout is
    captured, and the collected outputs list is JSON-gated before returning."""
    buf = io.StringIO()
    real_stdout = sys.stdout
    start = time.perf_counter()
    try:
        operations = inp["operations"]
        arglists = inp["args"]
    except (KeyError, TypeError):
        return {"status": "error", "time_ms": 0, "stdout": "",
                "error": "Class test input needs 'operations' and 'args' arrays."}
    if (not isinstance(operations, list) or not isinstance(arglists, list)
            or len(operations) != len(arglists)):
        return {"status": "error", "time_ms": 0, "stdout": "",
                "error": "'operations' and 'args' must be equal-length arrays."}

    outputs: list = []
    try:
        sys.stdout = buf
        signal.setitimer(signal.ITIMER_REAL, time_limit_s)
        instance = None
        for i, (op, raw_args) in enumerate(zip(operations, arglists)):
            call_args = list(raw_args) if isinstance(raw_args, list) else [raw_args]
            if i == 0:
                # First op is the constructor; its name is the class name.
                _decode_args(call_args, ctor_decoders)
                instance = cls(*call_args)
                outputs.append(None)
                continue
            spec = method_dispatch.get(op)
            if spec is None:
                signal.setitimer(signal.ITIMER_REAL, 0)
                sys.stdout = real_stdout
                return {"status": "error",
                        "time_ms": (time.perf_counter() - start) * 1000,
                        "error": f"Test calls unknown method `{op}` on the class.",
                        "stdout": buf.getvalue()[:max_output]}
            decoders, encoder = spec
            _decode_args(call_args, decoders)
            result = getattr(instance, op)(*call_args)
            if encoder is not None:
                result = encoder(result)
            outputs.append(result)
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout
        elapsed = (time.perf_counter() - start) * 1000
        try:
            json.dumps(outputs)
        except (TypeError, ValueError):
            return {"status": "error", "time_ms": elapsed,
                    "error": "An operation returned a value that is not "
                             "JSON-serializable.",
                    "stdout": buf.getvalue()[:max_output]}
        return {"status": "ok", "returned": outputs, "time_ms": elapsed,
                "stdout": buf.getvalue()[:max_output]}
    except _Timeout:
        return {"status": "timeout", "time_ms": time_limit_s * 1000,
                "error": "Time limit exceeded.", "stdout": buf.getvalue()[:max_output]}
    except BaseException:  # noqa: BLE001
        elapsed = (time.perf_counter() - start) * 1000
        return {"status": "error", "time_ms": elapsed, "error": _short_tb(),
                "stdout": buf.getvalue()[:max_output]}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout


def _run_class_problem(workdir, payload, tests, max_output) -> None:
    """Load a class solution and dispatch every test through `_run_class`."""
    class_name = payload.get("class_name") or ""
    ctor_params = payload.get("params", []) or []
    methods_spec = payload.get("class_methods", []) or []

    inject: dict = {}
    ctor_decoders = _positional_decoders(ctor_params, inject)
    method_dispatch: dict = {}
    for m in methods_spec:
        decoders = _positional_decoders(m.get("params", []), inject)
        rtype = (m.get("returns") or {}).get("type", "") or ""
        codec = _CODECS.get(rtype)
        encoder = codec[2] if codec else None
        if codec:
            inject[codec[0].__name__] = codec[0]
        method_dispatch[m["name"]] = (decoders, encoder)

    signal.signal(signal.SIGALRM, _on_alarm)
    module, load_err = _load_solution(
        os.path.join(workdir, "solution.py"),
        float(payload.get("import_budget_s", 5.0)),
        inject,
    )
    # A misconfigured class problem (no class name) should report a clean per-test
    # error, not raise out of the harness (getattr(module, None) is a TypeError).
    if not class_name:
        module, load_err = None, "This class problem is misconfigured: no class name."
    cls = getattr(module, class_name, None) if module else None
    if module and cls is None:
        load_err = f"Your solution must define a class named `{class_name}`."

    results = []
    for t in tests:
        if load_err or cls is None:
            results.append({"name": t["name"], "status": "error",
                            "error": load_err or "Class not found.",
                            "time_ms": 0, "stdout": ""})
            continue
        out = _run_class(cls, ctor_decoders, method_dispatch, t["input"],
                         float(t["time_limit_s"]), max_output)
        out["name"] = t["name"]
        results.append(out)

    with open(os.path.join(workdir, "result.json"), "w", encoding="utf-8") as f:
        json.dump({"results": results}, f)


def main() -> None:
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "payload.json"), encoding="utf-8") as f:
        payload = json.load(f)

    max_output = int(payload.get("max_output_bytes", 65536))
    tests = payload["tests"]

    # Class-based "design" problems: instantiate a class and replay a sequence of
    # method calls, instead of calling one top-level function per test.
    if payload.get("kind") == "class":
        _run_class_problem(workdir, payload, tests, max_output)
        return

    fn_name = payload["function_name"]
    raw_params = payload["params"]
    return_type = payload.get("return_type", "") or ""

    # `params` may be a list of names (legacy) or of {name, type} dicts. Build the
    # call order, the per-param decoders, the return encoder, and the classes to
    # inject for any declared custom type.
    params: list = []
    decoders: dict = {}
    inject: dict = {}
    for p in raw_params:
        name = p if isinstance(p, str) else p["name"]
        ptype = "" if isinstance(p, str) else (p.get("type") or "")
        params.append(name)
        codec = _CODECS.get(ptype)
        if codec:
            decoders[name] = codec[1]
            inject[codec[0].__name__] = codec[0]
    encoder = None
    ret_codec = _CODECS.get(return_type)
    if ret_codec:
        encoder = ret_codec[2]
        inject[ret_codec[0].__name__] = ret_codec[0]

    signal.signal(signal.SIGALRM, _on_alarm)

    module, load_err = _load_solution(
        os.path.join(workdir, "solution.py"),
        float(payload.get("import_budget_s", 5.0)),
        inject,
    )
    func = getattr(module, fn_name, None) if module else None
    if module and func is None:
        load_err = f"Your solution must define a function named `{fn_name}`."

    results = []
    for t in tests:
        if load_err or func is None:
            results.append({"name": t["name"], "status": "error",
                            "error": load_err or "Function not found.",
                            "time_ms": 0, "stdout": ""})
            continue
        out = _run_one(func, params, decoders, encoder, t["input"],
                       float(t["time_limit_s"]), max_output)
        out["name"] = t["name"]
        results.append(out)

    with open(os.path.join(workdir, "result.json"), "w", encoding="utf-8") as f:
        json.dump({"results": results}, f)


if __name__ == "__main__":
    main()
