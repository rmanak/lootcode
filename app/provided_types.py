"""Solver-facing documentation for the rich types the harness injects.

When a problem declares a param or return as `TreeNode`, `ListNode`,
`DoublyLinkedList` — or, for a design problem, takes an `Iterator` or a
`NestedInteger` — the sandbox injects a real class into the solution's module
(see `app/executor/harness.py`). The problem page shows the solver what that
class looks like, next to the signature.

**The snippets are rendered from the real classes, not retyped.** They used to
be hand-written string literals in `routers/pages.py`, one screen away from the
`# Keep the shape in sync with that class` comment that was the only thing
holding the two in step. Nothing enforced it, and the UI is a promise about what
the sandbox will hand you: a drifted parameter name here is a solver writing
against a constructor that does not exist.

The harness cannot import from `app` — it runs stdlib-only inside the sandbox
and `docker_executor.py` copies it into the container as a single file — so the
arrow points this way: this module reads the harness's classes via `inspect`.
What is derived is the shape (class name, constructor parameters and defaults,
method names and arity); what is authored is the prose and the return
annotations, since the harness's own methods carry neither. `tests/
test_provided_types.py` pins the authored half against the real classes.
"""
from __future__ import annotations

import inspect
from dataclasses import dataclass, field

from .executor import harness


@dataclass(frozen=True)
class _Spec:
    """How to document one injected class."""

    cls: type
    #: Trailing comment on the `class X:` line.
    summary: str
    #: For interface types: method name -> (return annotation, trailing comment).
    #: Empty for plain data types, which are documented by their constructor.
    methods: dict[str, tuple[str, str]] = field(default_factory=dict)
    #: Extra type labels a problem may use for this same definition.
    aliases: tuple[str, ...] = ()


# Keyed by the `type` string a problem writes in its contract.
_SPECS: dict[str, _Spec] = {
    "TreeNode": _Spec(harness.TreeNode, "binary tree node"),
    "ListNode": _Spec(harness.ListNode, "singly-linked list node"),
    # The contract calls the type `DoublyLinkedList`; the injected class is `Node`.
    "DoublyLinkedList": _Spec(harness.Node, "doubly-linked list node"),
    "Iterator": _Spec(
        harness.Iterator, "", aliases=("Iterator<int>",),
        methods={
            "hasNext": ("bool", "another element remains?"),
            "next": ("int", "return the next element, advance"),
        },
    ),
    "NestedInteger": _Spec(
        harness.NestedInteger, "",
        aliases=("List<NestedInteger>", "NestedInteger[]"),
        # The read interface only. The harness class also carries `add` /
        # `setInteger`, which its decoder uses to build the structure; solvers
        # are never handed a NestedInteger to write to.
        methods={
            "isInteger": ("bool", "holds a single integer?"),
            "getInteger": ("int", "the integer (else None)"),
            "getList": ("list", "the nested list (else None)"),
        },
    ),
}

_DO_NOT_REDEFINE = "provided, do not redefine"


def _render(spec: _Spec) -> str:
    """One class's documentation snippet, built from the real class."""
    summary = f"{spec.summary} — {_DO_NOT_REDEFINE}" if spec.summary \
        else _DO_NOT_REDEFINE
    head = f"class {spec.cls.__name__}:  # {summary}"

    if not spec.methods:
        # A data type: show the constructor and what it assigns. Parameter names
        # and defaults come straight from the harness's `__init__`.
        # getattr_static: the plain function off the class, not a bound descriptor,
        # so the signature still carries `self` the way the snippet shows it.
        sig = inspect.signature(inspect.getattr_static(spec.cls, "__init__"))
        params = list(sig.parameters)[1:]  # drop `self`
        body = [f"        self.{p} = {p}" for p in params]
        return "\n".join([head, f"    def __init__{sig}:", *body])

    # An interface type: show the methods solvers may call, comments aligned.
    stubs = [
        (f"    def {name}{inspect.signature(getattr(spec.cls, name))} -> {ret}: ...",
         comment)
        for name, (ret, comment) in spec.methods.items()
    ]
    width = max(len(stub) for stub, _ in stubs) + 2
    return "\n".join([head, *(f"{stub:<{width}}# {comment}" for stub, comment in stubs)])


#: Type label -> the snippet shown on the problem page. Aliases share one object,
#: which is what lets `provided_types` de-duplicate by identity below.
PROVIDED_TYPE_DEFS: dict[str, str] = {}
for _label, _spec in _SPECS.items():
    _defn = _render(_spec)
    PROVIDED_TYPE_DEFS[_label] = _defn
    for _alias in _spec.aliases:
        PROVIDED_TYPE_DEFS[_alias] = _defn


def provided_types(prob) -> dict:  # noqa: ANN001
    """Ordered map of declared custom type -> its definition snippet, for the
    rich/helper types this problem actually uses. Covers a function's params and
    return, and (for a class problem) the constructor params plus every method's
    params and return."""
    used: list[str] = [(p.get("type") or "") for p in (prob.params or [])]
    used.append(getattr(prob, "return_type", "") or "")
    for m in (getattr(prob, "class_methods", None) or []):
        used.extend((p.get("type") or "") for p in (m.get("params") or []))
        used.append((m.get("returns") or {}).get("type") or "")
    # De-dup by definition (aliases share one), preserving first-seen order.
    out: dict = {}
    seen: set = set()
    for t in used:
        defn = PROVIDED_TYPE_DEFS.get(t)
        if defn and defn not in seen:
            out[t] = defn
            seen.add(defn)
    return out
