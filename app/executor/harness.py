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


_TRUNCATED = "\n... [output truncated — your solution printed too much]"


class _OutputBudget:
    """A cap on captured stdout for the WHOLE run, not per test.

    The parent sizes its RLIMIT_FSIZE for a single result.json, and result.json
    holds every test's captured stdout. A per-test cap therefore multiplies by
    the number of tests: a solution that prints in a loop blew past the file
    limit, killed the harness mid-write, and lost *every* result. Each test now
    gets whatever is left of one shared budget, and the user sees a truncation
    notice instead of a dead run.
    """

    def __init__(self, total: int) -> None:
        self.total = max(total, 0)
        self.remaining = self.total

    def new_buffer(self):
        """A stdout stand-in for one test (or the import), pre-capped so nothing
        unbounded is ever held in memory."""
        return _CappedBuffer(self.total)

    def take(self, text: str) -> str:
        if len(text) <= self.remaining:
            self.remaining -= len(text)
            return text
        kept = text[:self.remaining]
        self.remaining = 0
        return kept + _TRUNCATED


class _CappedBuffer:
    """A `sys.stdout` replacement that stops storing past `limit` characters.

    Not an io.StringIO, for two reasons, both learned the hard way:

    * StringIO grows without bound, so a print bomb hit the memory cap and killed
      the harness — losing every result — where truncating would have graded the
      run fine.
    * It stands in for `sys.stdout` while *untrusted* code runs. `close()` on a
      StringIO makes the later `getvalue()` raise, so a solution doing
      `sys.stdout.close()` took the whole run down with it. Here close/flush are
      no-ops and reads never raise.
    """

    def __init__(self, limit: int) -> None:
        self._parts: list[str] = []
        self._len = 0
        self._limit = max(limit, 0)
        self._dropped = False
        self.closed = False  # some libraries probe this before writing

    def write(self, s) -> int:
        text = s if isinstance(s, str) else str(s)
        room = self._limit - self._len
        if len(text) > room:
            self._dropped = True
        if room > 0:
            self._parts.append(text[:room])
            self._len += min(len(text), room)
        return len(text)  # claim the whole write; truncation is ours, not an error

    def writelines(self, lines) -> None:
        for line in lines:
            self.write(line)

    def getvalue(self) -> str:
        # The marker belongs here, not in _OutputBudget.take: dropping at write
        # time is invisible to the budget, and a silent cut reads to the solver
        # like their print stopped working.
        return "".join(self._parts) + (_TRUNCATED if self._dropped else "")

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass

    def isatty(self) -> bool:
        return False

    def writable(self) -> bool:
        return True

    def readable(self) -> bool:
        return False

    def seekable(self) -> bool:
        return False


def _value(buf) -> str:
    """Read back a capture buffer without ever raising into the harness.

    `sys.stdout` is under the solution's control while its code runs; it can be
    closed, replaced or swapped for an object whose reads throw. Extraction must
    not be able to kill the run — that failure mode loses every test's result.
    """
    try:
        return buf.getvalue()
    except BaseException:  # noqa: BLE001 - hostile or closed buffer
        return ""


def _attach_import_output(results: list, import_out: str, out_budget) -> None:
    """Show what the solution printed at module level on the first test, so a
    `print` outside the function is not silently dropped."""
    if import_out and results:
        results[0]["stdout"] = out_budget.take(import_out) + results[0].get("stdout", "")


def _write_results(workdir: str, results: list) -> None:
    """Write result.json, degrading rather than dying if it exceeds the parent's
    file-size rlimit — an OSError here would lose every test's result.

    Degradation drops the least valuable fields first and always lands on a
    *failure* for the affected tests, never on a pass: the parent only awards a
    pass for status "ok" whose `returned` equals the (sandbox-invisible)
    expected value, so a result stripped of `returned` grades as wrong.

    CPython ignores SIGXFSZ by default, which is what turns an over-limit write
    into a catchable OSError. Untrusted code runs first and can restore the
    default disposition, in which case the process is killed outright and the
    parent's own "run was stopped" fallback covers it.
    """
    path = os.path.join(workdir, "result.json")

    def _attempt() -> bool:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"results": results}, f)
            return True
        except OSError:
            return False

    if _attempt():
        return
    # 1. Captured output is the biggest and least important field.
    for r in results:
        if r.get("stdout"):
            r["stdout"] = "[output dropped — the results were too large to store]"
    if _attempt():
        return
    # 2. Tracebacks next: bounded per test, but they multiply across tests and
    #    non-ASCII characters cost up to 12 bytes each once JSON-escaped.
    for r in results:
        if r.get("error"):
            r["error"] = r["error"][:200]
    if _attempt():
        return
    # 3. Finally the returned values, which nothing else bounds. Say why, so the
    #    user sees a real explanation rather than a bare wrong answer.
    for r in results:
        r.pop("returned", None)
        if r.get("status") == "ok":
            r["status"] = "error"
            r["error"] = ("Your solution returned too much data for the grader to "
                          "store. Check the size of what you return.")
    _attempt()


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


def _load_solution(path: str, budget_s: float, inject: dict | None, out_budget):
    """Import the user's solution.py, guarding against import-time hangs.

    `inject` maps names (e.g. "TreeNode") to objects placed in the solution's
    module globals before its top-level code runs, so user code can reference
    them at import and call time without defining them.

    Returns (module, error, captured_stdout). Module-level prints are captured
    like per-test ones — otherwise a `print` outside the function vanishes into
    the parent's pipe and the solver sees nothing.
    """
    buf = out_budget.new_buffer()
    real_stdout = sys.stdout
    signal.setitimer(signal.ITIMER_REAL, budget_s)
    try:
        sys.stdout = buf
        spec = importlib.util.spec_from_file_location("solution", path)
        module = importlib.util.module_from_spec(spec)
        for name, obj in (inject or {}).items():
            setattr(module, name, obj)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module, None, _value(buf)
    except _Timeout:
        return None, "Import timed out (module-level code took too long).", _value(buf)
    except BaseException:  # noqa: BLE001 - report anything, incl. SystemExit
        return (None, "Error while loading your solution:\n" + _short_tb(),
                _value(buf))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout


def _run_one(func, params, decoders, encoder, inp, time_limit_s, out_budget) -> dict:
    buf = out_budget.new_buffer()
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
                    "stdout": out_budget.take(_value(buf))}
        return {"status": "ok", "returned": returned, "time_ms": elapsed,
                "stdout": out_budget.take(_value(buf))}
    except _Timeout:
        return {"status": "timeout", "time_ms": time_limit_s * 1000,
                "error": "Time limit exceeded.", "stdout": out_budget.take(_value(buf))}
    except BaseException:  # noqa: BLE001
        elapsed = (time.perf_counter() - start) * 1000
        return {"status": "error", "time_ms": elapsed, "error": _short_tb(),
                "stdout": out_budget.take(_value(buf))}
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
               out_budget) -> dict:
    """Run one class test: instantiate `cls` then replay a sequence of method
    calls, collecting one output per call (``None`` for the constructor and for
    void methods). `method_dispatch` maps method name -> (arg-decoders, encoder).

    Mirrors `_run_one`'s contract: the whole operation sequence runs under a
    single per-test SIGALRM (LeetCode-style overall time budget), stdout is
    captured, and the collected outputs list is JSON-gated before returning."""
    buf = out_budget.new_buffer()
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
                        "stdout": out_budget.take(_value(buf))}
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
                    "stdout": out_budget.take(_value(buf))}
        return {"status": "ok", "returned": outputs, "time_ms": elapsed,
                "stdout": out_budget.take(_value(buf))}
    except _Timeout:
        return {"status": "timeout", "time_ms": time_limit_s * 1000,
                "error": "Time limit exceeded.", "stdout": out_budget.take(_value(buf))}
    except BaseException:  # noqa: BLE001
        elapsed = (time.perf_counter() - start) * 1000
        return {"status": "error", "time_ms": elapsed, "error": _short_tb(),
                "stdout": out_budget.take(_value(buf))}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout


def _run_class_problem(workdir, payload, tests, out_budget) -> None:
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
    module, load_err, import_out = _load_solution(
        os.path.join(workdir, "solution.py"),
        float(payload.get("import_budget_s", 5.0)),
        inject,
        out_budget,
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
                         float(t["time_limit_s"]), out_budget)
        out["name"] = t["name"]
        results.append(out)

    _attach_import_output(results, import_out, out_budget)
    _write_results(workdir, results)


def main() -> None:
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "payload.json"), encoding="utf-8") as f:
        payload = json.load(f)

    out_budget = _OutputBudget(int(payload.get("max_output_bytes", 65536)))
    tests = payload["tests"]

    # Class-based "design" problems: instantiate a class and replay a sequence of
    # method calls, instead of calling one top-level function per test.
    if payload.get("kind") == "class":
        _run_class_problem(workdir, payload, tests, out_budget)
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

    module, load_err, import_out = _load_solution(
        os.path.join(workdir, "solution.py"),
        float(payload.get("import_budget_s", 5.0)),
        inject,
        out_budget,
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
                       float(t["time_limit_s"]), out_budget)
        out["name"] = t["name"]
        results.append(out)

    _attach_import_output(results, import_out, out_budget)
    _write_results(workdir, results)


if __name__ == "__main__":
    main()
