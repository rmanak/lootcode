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


# type token -> (class to inject, decode JSON->object, encode object->JSON)
_CODECS = {
    "TreeNode": (TreeNode, _tree_decode, _tree_encode),
    "ListNode": (ListNode, _list_decode, _list_encode),
    "DoublyLinkedList": (Node, _dlist_decode, _dlist_encode),
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


def main() -> None:
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "payload.json"), encoding="utf-8") as f:
        payload = json.load(f)

    fn_name = payload["function_name"]
    raw_params = payload["params"]
    return_type = payload.get("return_type", "") or ""
    tests = payload["tests"]
    max_output = int(payload.get("max_output_bytes", 65536))

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
