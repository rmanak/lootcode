#!/usr/bin/env python3
"""Validate the structured problem JSON that an LLM produces from ``app/llm/problem_prompt.txt``.

Usage
-----
    python test_llm_output.py generated_llm_output.json

The companion ``app/llm/problem_prompt.txt`` asks a (generic, unspecified) LLM to turn a fixed
problem statement into a single JSON object containing everything needed to
create a new lootcode problem programmatically: the function contract, the
comparison mode, a starter stub, a canonical reference solution, and a set of
structured test cases with expected outputs.

The slug, title, and problem statement are intentionally NOT part of this output.
They are already known when the LLM is prompted (the statement is the input, and
the slug/title are supplied separately to the problem-creation step), so the LLM
is never asked to echo or re-interpret the statement -- which avoids drift and
mis-interpretation, especially with smaller models. This validator therefore does
not expect those three fields.

This script is the gate between that LLM output and the code that would write a
real problem to ``content/problems/<slug>/``. It answers one question: *is the
JSON well-formed and self-consistent enough to be used without human editing, or
is it corrupted / incomplete?* It checks, in order:

  1. The file exists and parses as JSON (the most common failure: the model
     emitted prose, Markdown fences, or truncated/invalid JSON).
  2. The JSON conforms to the required schema (all required keys present, correct
     types, no unexpected keys) -- enforced with **pydantic v2**, the de-facto
     standard for Python data validation.
  3. Cross-field / semantic invariants that a flat schema cannot express:
       - function_name / parameter names are valid Python identifiers;
       - the canonical solution and the starter both actually parse as Python and
         define the declared top-level function with exactly the declared
         parameters, in order (checked statically with the ``ast`` module);
       - each test's ``input`` keys are exactly the parameter names (the grader
         calls ``function_name(**input)``);
       - there is at least one visible and one hidden test; names are unique;
       - ``expected`` values have the shape the declared ``compare`` mode
         requires (a list for ``unordered``; a list of lists for
         ``set_of_lists``);
       - every value is JSON-serializable.

Security note
-------------
This validator NEVER executes ``canonical_solution`` / ``starter_code``. That
code is untrusted (it came from an LLM) and lootcode is explicit that untrusted
code may only run inside the project's sandbox (``app/executor`` /
``docs/code-execution.md``). We therefore validate the solution *statically* with
``ast`` only. Actually running the solution against the tests to confirm it
*passes* is a separate, deeper step that belongs to the sandboxed executor
(``scripts/seed.py`` / ``app.executor.run_submission``).

Exit codes
----------
    0  valid (no errors; warnings may have been printed)
    1  invalid (one or more schema/semantic errors)
    2  could not even read/parse the input file as a JSON object

With ``--strict``, warnings are promoted to errors (so a "clean but slightly
unusual" output also exits non-zero).
"""
from __future__ import annotations

import argparse
import ast
import json
import keyword
import sys
from pathlib import Path
from typing import Any

# pydantic v2 is the validation engine. It ships with FastAPI (a project
# dependency), so it is available wherever lootcode runs. We import lazily-ish at
# module top and fail with a clear, actionable message if it is somehow missing,
# rather than dying with a raw ImportError.
try:
    from pydantic import (
        BaseModel,
        ConfigDict,
        Field,
        ValidationError,
        field_validator,
        model_validator,
    )
except ImportError:  # pragma: no cover - environment problem, not LLM problem
    sys.stderr.write(
        "This validator needs pydantic v2. Install it with:\n"
        "    pip install 'pydantic>=2'\n"
    )
    raise SystemExit(2)


# ---------------------------------------------------------------------------
# Constants that mirror the rest of the codebase (kept in sync intentionally).
# ---------------------------------------------------------------------------

# The three comparison modes the judge understands. Source of truth:
# app/executor/__init__.py (_normalize/_equal) and specs/problem-schema.md.
COMPARE_MODES = ("exact", "unordered", "set_of_lists")

# Allowed difficulty levels (specs/problem-schema.md / meta.json).
DIFFICULTIES = ("easy", "medium", "hard")

# The 39 canonical tags. Source of truth is app/tags.py::CANONICAL_TAGS; this is a
# copy so the validator stays standalone (no dependency on the `app` package).
# Non-canonical tags are only WARNED about, because app.tags.normalize_tags folds
# aliases and passes unknown tags through on write -- they are not fatal.
CANONICAL_TAGS = frozenset({
    "array", "backtracking", "binary-indexed-tree", "binary-search",
    "binary-search-tree", "binary-tree", "bit-manipulation", "bitmask",
    "breadth-first-search", "combinatorics", "counting", "depth-first-search",
    "design", "divide-and-conquer", "dynamic-programming", "graph", "greedy",
    "hash-function", "hash-set", "hash-table", "heap", "linked-list", "math",
    "matrix", "memoization", "monotonic-stack", "prefix-sum", "queue",
    "recursion", "simulation",
    "sliding-window", "sorting", "stack", "string", "suffix-array", "tree",
    "trie", "two-pointers", "union-find",
})

# How many tests we expect. The prompt asks for 6-10; fewer than MIN is an error,
# fewer than RECOMMENDED is a warning.
MIN_TESTS = 4
RECOMMENDED_TESTS = 6

# At most this many progressive hints are kept per problem (app/content.py::MAX_HINTS).
# Extras are dropped on write, so >MAX_HINTS is a warning, not an error.
MAX_HINTS = 3


# ---------------------------------------------------------------------------
# Schema layer (pydantic). This catches "missing required field", "wrong type",
# "unexpected extra key", and basic value constraints -- i.e. most of the ways an
# LLM corrupts structured output.
# ---------------------------------------------------------------------------

class Param(BaseModel):
    """One function parameter: a name and a documentation-only type label."""
    # extra="forbid" -> an unexpected key (e.g. the model invents "default") fails.
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    type: str = Field(min_length=1)


class Test(BaseModel):
    """One test case: input kwargs, expected return, weight, and visibility."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    # ``input`` maps each parameter name -> JSON value; the grader does
    # function_name(**input), so it must be an object/dict.
    input: dict[str, Any]
    # ``expected`` is an arbitrary JSON value (scalar, list, list-of-lists, ...);
    # we accept Any here and check its *shape* later against the compare mode.
    expected: Any
    weight: int = Field(ge=1)
    hidden: bool

    @field_validator("expected", mode="before")
    @classmethod
    def _expected_present(cls, v: Any) -> Any:
        # ``expected: null`` is suspicious but technically valid JSON, so we allow
        # it here and let the semantic layer decide (a null expected under
        # unordered/set_of_lists will be flagged there).
        return v


class ReturnSpec(BaseModel):
    """A method's declared return: ``{"type": "int"}`` (``"void"`` for no value)."""
    model_config = ConfigDict(extra="forbid")

    type: str = ""


class Method(BaseModel):
    """One method of a class-based ("design") problem: a name, positional params,
    and a declared return. The constructor is described separately (by the class's
    ``params``); this covers every non-constructor method the solver implements."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    params: list[Param] = Field(default_factory=list)
    returns: ReturnSpec = Field(default_factory=ReturnSpec)


class ProblemOutput(BaseModel):
    """The full structured object the LLM must return (see app/llm/problem_prompt.txt).

    Supports two problem kinds. ``kind="function"`` (default, back-compatible) is
    one top-level function graded per test. ``kind="class"`` is a stateful "design"
    problem: the solver implements ``class_name`` with the listed ``class_methods``,
    ``params`` are the constructor params, and each test replays an operation
    sequence (see semantic_checks / specs/problem-schema.md)."""
    # Forbid extra top-level keys: if the model adds a stray field, that's a sign
    # the contract drifted, so we surface it rather than silently ignoring it.
    model_config = ConfigDict(extra="forbid")

    # Note: slug, title, and statement_md are deliberately absent -- they are known
    # at prompt time and supplied separately, not produced by the LLM (see the
    # module docstring). The on-disk problem dir still needs them, but they come
    # from the caller, not from this output.
    kind: str = "function"
    difficulty: str
    tags: list[str] = Field(min_length=1)
    # Up to MAX_HINTS optional progressive hints (see specs/problem-schema.md).
    # Back-compatible: absent / [] means "no hints". Extras are capped on write, so
    # the count/blank-entry checks in the semantic layer only warn, never reject.
    hints: list[str] = Field(default_factory=list)
    # Function contract (kind="function"). Optional at the schema level; the
    # kind-aware model_validator below enforces what each kind actually needs.
    function_name: str = ""
    params: list[Param] = Field(default_factory=list)
    return_type: str = ""
    # Class contract (kind="class").
    class_name: str = ""
    class_methods: list[Method] = Field(default_factory=list)
    compare: str
    starter_code: str = Field(min_length=1)
    canonical_solution: str = Field(min_length=1)
    tests: list[Test] = Field(min_length=1)

    @field_validator("kind")
    @classmethod
    def _kind_in_set(cls, v: str) -> str:
        if v not in ("function", "class"):
            raise ValueError(f"must be 'function' or 'class', got {v!r}")
        return v

    @field_validator("difficulty")
    @classmethod
    def _difficulty_in_set(cls, v: str) -> str:
        if v not in DIFFICULTIES:
            raise ValueError(f"must be one of {DIFFICULTIES}, got {v!r}")
        return v

    @field_validator("compare")
    @classmethod
    def _compare_in_set(cls, v: str) -> str:
        if v not in COMPARE_MODES:
            raise ValueError(f"must be one of {COMPARE_MODES}, got {v!r}")
        return v

    @model_validator(mode="after")
    def _require_kind_fields(self) -> "ProblemOutput":
        if self.kind == "function":
            if not self.function_name:
                raise ValueError("function_name is required for kind='function'")
            if not self.return_type:
                raise ValueError("return_type is required for kind='function'")
        else:  # class
            if not self.class_name:
                raise ValueError("class_name is required for kind='class'")
            if not self.class_methods:
                raise ValueError(
                    "class_methods must list at least one method for kind='class'")
        return self


# ---------------------------------------------------------------------------
# A tiny report accumulator so we can collect ALL problems in one pass and print
# them together, instead of stopping at the first error.
# ---------------------------------------------------------------------------

class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self, strict: bool) -> bool:
        # Valid means: no errors, and (in strict mode) no warnings either.
        return not self.errors and (not self.warnings or not strict)


# ---------------------------------------------------------------------------
# AST helpers: statically inspect Python source WITHOUT importing/executing it.
# ---------------------------------------------------------------------------

def _top_level_function(source: str, name: str) -> ast.FunctionDef | None:
    """Return the top-level ``def <name>`` node in ``source``, or None.

    Parses with ``ast`` (no execution). Only module-level functions count -- a
    function nested inside a class or another function does not satisfy the
    "single top-level function" contract.
    """
    tree = ast.parse(source)  # may raise SyntaxError; caller handles it
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node  # type: ignore[return-value]
    return None


def _positional_param_names(fn: ast.FunctionDef) -> list[str]:
    """The function's positional parameter names, in order.

    The grader calls ``function_name(**input)``, so positional-or-keyword and
    positional-only params are what the test ``input`` keys must line up with.
    """
    a = fn.args
    return [p.arg for p in (a.posonlyargs + a.args)]


def _check_python_function(
    label: str, source: str, fn_name: str, expected_params: list[str], rep: Report
) -> None:
    """Validate that ``source`` parses and defines ``fn_name`` with the right params.

    ``label`` is "canonical_solution" or "starter_code" for messages.
    """
    try:
        fn = _top_level_function(source, fn_name)
    except SyntaxError as exc:
        rep.error(f"{label}: is not valid Python (SyntaxError: {exc.msg} "
                  f"at line {exc.lineno}).")
        return

    if fn is None:
        rep.error(f"{label}: does not define a top-level function named "
                  f"{fn_name!r} (no class wrapper / nested def is allowed).")
        return

    got = _positional_param_names(fn)
    if got != expected_params:
        rep.error(
            f"{label}: function {fn_name!r} has parameters {got}, but meta "
            f"declares {expected_params} (names and order must match exactly)."
        )

    # A function that takes **kwargs / *args instead of the named params would
    # technically accept the call but breaks the contract -- flag it.
    if fn.args.vararg is not None:
        rep.warn(f"{label}: {fn_name!r} declares *{fn.args.vararg.arg}; the "
                 "contract expects exactly the named parameters.")
    if fn.args.kwarg is not None:
        rep.warn(f"{label}: {fn_name!r} declares **{fn.args.kwarg.arg}; the "
                 "contract expects exactly the named parameters.")


def _looks_like_stub(source: str, fn_name: str) -> bool:
    """Heuristic: does ``source`` look like an unimplemented stub (just pass/...)?

    Used to (a) warn if the canonical solution looks empty, and (b) confirm the
    starter looks like a stub. Parses with ast; conservative -- only treats a body
    of pass/Ellipsis/docstring(+pass) as a stub.
    """
    try:
        fn = _top_level_function(source, fn_name)
    except SyntaxError:
        return False
    if fn is None:
        return False
    meaningful = []
    for stmt in fn.body:
        # Skip a leading docstring and bare `...`/`pass` placeholders.
        if isinstance(stmt, ast.Pass):
            continue
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            # docstring or a bare `...`
            continue
        meaningful.append(stmt)
    return not meaningful


# ---------------------------------------------------------------------------
# AST helpers for class-based ("design") problems.
# ---------------------------------------------------------------------------

def _top_level_class(source: str, name: str) -> ast.ClassDef | None:
    """Return the top-level ``class <name>`` node in ``source``, or None.

    Parses with ``ast`` (no execution). Only module-level classes count."""
    tree = ast.parse(source)  # may raise SyntaxError; caller handles it
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    return None


def _class_methods(cls: ast.ClassDef) -> dict[str, ast.FunctionDef]:
    """Map method name -> def node for the class's directly-defined methods."""
    out: dict[str, ast.FunctionDef] = {}
    for node in cls.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = node  # type: ignore[assignment]
    return out


def _method_positional_params(fn: ast.FunctionDef) -> list[str]:
    """Positional parameter names of a method, with a leading ``self`` dropped."""
    a = fn.args
    names = [p.arg for p in (a.posonlyargs + a.args)]
    if names and names[0] == "self":
        names = names[1:]
    return names


def _check_python_class(
    label: str, source: str, class_name: str, ctor_params: list[str],
    methods: list["Method"], rep: Report,
) -> None:
    """Validate that ``source`` parses and defines ``class_name`` with an
    ``__init__`` matching the declared constructor params and every declared
    method matching its declared params. ``label`` is "canonical_solution" or
    "starter_code" for messages."""
    try:
        cls = _top_level_class(source, class_name)
    except SyntaxError as exc:
        rep.error(f"{label}: is not valid Python (SyntaxError: {exc.msg} "
                  f"at line {exc.lineno}).")
        return
    if cls is None:
        rep.error(f"{label}: does not define a top-level class named "
                  f"{class_name!r}.")
        return

    defined = _class_methods(cls)
    if "__init__" not in defined:
        rep.error(f"{label}: class {class_name!r} defines no __init__ constructor "
                  f"(it must accept the constructor params {ctor_params}).")
    else:
        got = _method_positional_params(defined["__init__"])
        if got != ctor_params:
            rep.error(f"{label}: __init__ has params {got}, but meta declares "
                      f"constructor params {ctor_params} (names and order must match).")

    for m in methods:
        want = [p.name for p in m.params]
        if m.name not in defined:
            rep.error(f"{label}: class {class_name!r} does not define method "
                      f"{m.name!r}.")
            continue
        got = _method_positional_params(defined[m.name])
        if got != want:
            rep.error(f"{label}: method {m.name!r} has params {got}, but meta "
                      f"declares {want} (names and order must match).")


def _class_looks_like_stub(source: str, class_name: str) -> bool:
    """Heuristic: does every method body look unimplemented (just pass/.../docstring)?
    Used to confirm the starter is a stub and warn if the canonical looks empty."""
    try:
        cls = _top_level_class(source, class_name)
    except SyntaxError:
        return False
    if cls is None:
        return False
    for node in cls.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for stmt in node.body:
            if isinstance(stmt, ast.Pass):
                continue
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue
            return False  # a meaningful statement -> not a stub
    return True


# ---------------------------------------------------------------------------
# Semantic layer: cross-field invariants the schema can't express.
# ---------------------------------------------------------------------------

def _check_identifier(kind: str, name: str, rep: Report) -> bool:
    """A name must be a valid, non-keyword Python identifier."""
    if not name.isidentifier():
        rep.error(f"{kind} {name!r} is not a valid Python identifier.")
        return False
    if keyword.iskeyword(name):
        rep.error(f"{kind} {name!r} is a reserved Python keyword.")
        return False
    return True


def _check_json_serializable(label: str, value: Any, rep: Report) -> None:
    """Returned/expected/input values must round-trip through JSON (the harness
    enforces the same for return values)."""
    try:
        json.dumps(value)
    except (TypeError, ValueError) as exc:
        rep.error(f"{label}: value is not JSON-serializable ({exc}).")


def _check_tags(tags: list[str], rep: Report) -> None:
    noncanon = sorted({t for t in tags if t not in CANONICAL_TAGS})
    if noncanon:
        rep.warn(f"tags: not in the canonical vocabulary: {noncanon} "
                 "(allowed but will be normalized/folded on write).")


def _check_hints(hints: list[str], rep: Report) -> None:
    """Hints are optional; at most MAX_HINTS are kept and blanks are dropped on
    write, so anything unusual here is a warning rather than a hard error."""
    if len(hints) > MAX_HINTS:
        rep.warn(f"hints: {len(hints)} provided; only the first {MAX_HINTS} are kept "
                 "(extras are dropped on write).")
    if any(not (h or "").strip() for h in hints):
        rep.warn("hints: contains a blank entry (blank hints are dropped on write).")


def _check_test_meta(tests: list[Test], rep: Report) -> None:
    """Count, name-uniqueness, and visibility checks shared by both kinds."""
    n = len(tests)
    if n < MIN_TESTS:
        rep.error(f"tests: only {n} provided; need at least {MIN_TESTS}.")
    elif n < RECOMMENDED_TESTS:
        rep.warn(f"tests: only {n} provided; {RECOMMENDED_TESTS}-10 recommended "
                 "(cover edge and larger inputs).")

    names = [t.name for t in tests]
    dupes = sorted({x for x in names if names.count(x) > 1})
    if dupes:
        rep.error(f"tests: duplicate test names: {dupes} (names must be unique).")

    if not any(not t.hidden for t in tests):
        rep.error("tests: at least one visible case (hidden=false) is required.")
    if not any(t.hidden for t in tests):
        rep.warn("tests: no hidden cases (hidden=true) -- hidden cases are "
                 "expected for fair scoring.")


def semantic_checks(model: ProblemOutput, rep: Report) -> None:
    """All the validation that needs more than one field at a time."""
    _check_tags(model.tags, rep)
    _check_hints(model.hints, rep)
    _check_test_meta(model.tests, rep)
    if model.kind == "class":
        _semantic_checks_class(model, rep)
    else:
        _semantic_checks_function(model, rep)


def _semantic_checks_function(model: ProblemOutput, rep: Report) -> None:
    # --- function name + parameter names are valid, unique identifiers --------
    fn_ok = _check_identifier("function_name", model.function_name, rep)

    param_names: list[str] = []
    for p in model.params:
        if _check_identifier("parameter name", p.name, rep):
            param_names.append(p.name)
    if len(param_names) != len(set(param_names)):
        rep.error("params: parameter names must be unique.")
    # Note: zero parameters is allowed (a no-arg function is legal), but unusual.
    if not model.params:
        rep.warn("params: the function takes no parameters -- double check that "
                 "is intended.")

    # --- canonical solution + starter are real Python with the right signature -
    # Only meaningful if we actually have a usable function name.
    if fn_ok:
        _check_python_function(
            "canonical_solution", model.canonical_solution,
            model.function_name, param_names, rep,
        )
        _check_python_function(
            "starter_code", model.starter_code,
            model.function_name, param_names, rep,
        )

        # The canonical solution should NOT be an empty stub.
        if _looks_like_stub(model.canonical_solution, model.function_name):
            rep.error("canonical_solution: looks like an empty stub (only "
                      "pass/.../docstring) -- it must be a complete solution.")
        # The starter SHOULD be a stub (no leaked solution); warn if it isn't.
        if not _looks_like_stub(model.starter_code, model.function_name):
            rep.warn("starter_code: does not look like an empty stub -- make "
                     "sure it does not leak the solution.")

    # --- per-test checks: input keys, JSON-serializability, expected shape -----
    param_set = set(param_names)
    for t in model.tests:
        # The grader does function_name(**input): keys must be exactly the params.
        input_keys = set(t.input.keys())
        missing = param_set - input_keys
        extra = input_keys - param_set
        if missing:
            rep.error(f"tests[{t.name!r}].input is missing keys for parameters "
                      f"{sorted(missing)}.")
        if extra:
            rep.error(f"tests[{t.name!r}].input has unexpected keys "
                      f"{sorted(extra)} (not function parameters).")

        _check_json_serializable(f"tests[{t.name!r}].input", t.input, rep)
        _check_json_serializable(f"tests[{t.name!r}].expected", t.expected, rep)

        # ``expected`` shape must match the declared compare mode, otherwise the
        # mode is meaningless and the statement<->judge agreement is broken.
        if model.compare == "unordered":
            if not isinstance(t.expected, list):
                rep.error(f"tests[{t.name!r}].expected must be a list when "
                          "compare='unordered'.")
        elif model.compare == "set_of_lists":
            if not isinstance(t.expected, list):
                rep.error(f"tests[{t.name!r}].expected must be a list of lists "
                          "when compare='set_of_lists'.")
            elif not all(isinstance(e, list) for e in t.expected):
                rep.warn(f"tests[{t.name!r}].expected: compare='set_of_lists' "
                         "usually expects every element to itself be a list.")


def _semantic_checks_class(model: ProblemOutput, rep: Report) -> None:
    """Semantic checks for a class-based ("design") problem: the canonical/starter
    must define the class with a matching constructor + methods, and each test
    replays an operation sequence (``operations``/``args``) whose length matches
    its ``expected`` outputs list."""
    # --- class name + constructor/method param names are valid identifiers ----
    cls_ok = _check_identifier("class_name", model.class_name, rep)

    ctor_params: list[str] = []
    for p in model.params:
        if _check_identifier("constructor parameter name", p.name, rep):
            ctor_params.append(p.name)
    if len(ctor_params) != len(set(ctor_params)):
        rep.error("params: constructor parameter names must be unique.")

    method_names: list[str] = []
    for m in model.class_methods:
        if _check_identifier("method name", m.name, rep):
            method_names.append(m.name)
        mparams = [p.name for p in m.params]
        if len(mparams) != len(set(mparams)):
            rep.error(f"method {m.name!r}: parameter names must be unique.")
    if len(method_names) != len(set(method_names)):
        rep.error("class_methods: method names must be unique.")

    # --- canonical + starter define the class with the right shape ------------
    if cls_ok:
        _check_python_class(
            "canonical_solution", model.canonical_solution,
            model.class_name, ctor_params, model.class_methods, rep)
        _check_python_class(
            "starter_code", model.starter_code,
            model.class_name, ctor_params, model.class_methods, rep)

        if _class_looks_like_stub(model.canonical_solution, model.class_name):
            rep.error("canonical_solution: every method looks like an empty stub "
                      "(only pass/.../docstring) -- it must be a complete solution.")
        if not _class_looks_like_stub(model.starter_code, model.class_name):
            rep.warn("starter_code: does not look like an empty class stub -- make "
                     "sure it does not leak the solution.")

    # --- per-test checks: operation-sequence shape ----------------------------
    method_set = set(method_names)
    for t in model.tests:
        keys = set(t.input.keys())
        if keys != {"operations", "args"}:
            rep.error(f"tests[{t.name!r}].input keys must be exactly "
                      "{{'operations', 'args'}} for a class problem, got "
                      f"{sorted(keys)}.")
            continue
        ops = t.input.get("operations")
        args = t.input.get("args")
        if not isinstance(ops, list) or not isinstance(args, list):
            rep.error(f"tests[{t.name!r}].input: 'operations' and 'args' must "
                      "both be arrays.")
            continue
        if len(ops) != len(args):
            rep.error(f"tests[{t.name!r}]: 'operations' ({len(ops)}) and 'args' "
                      f"({len(args)}) must have equal length.")
        if not isinstance(t.expected, list):
            rep.error(f"tests[{t.name!r}].expected must be a list of per-operation "
                      "outputs (null for the constructor and void methods).")
        elif len(t.expected) != len(ops):
            rep.error(f"tests[{t.name!r}]: expected has {len(t.expected)} outputs "
                      f"but there are {len(ops)} operations.")
        if ops:
            if ops[0] != model.class_name:
                rep.error(f"tests[{t.name!r}]: the first operation must be the "
                          f"constructor {model.class_name!r}, got {ops[0]!r}.")
            unknown = sorted({op for op in ops[1:] if op not in method_set})
            if unknown:
                rep.error(f"tests[{t.name!r}]: operations reference unknown "
                          f"method(s) {unknown} (declared: {sorted(method_set)}).")
        if not all(isinstance(a, list) for a in args):
            rep.error(f"tests[{t.name!r}].args: every element must be a list of "
                      "arguments for the corresponding operation.")

        _check_json_serializable(f"tests[{t.name!r}].input", t.input, rep)
        _check_json_serializable(f"tests[{t.name!r}].expected", t.expected, rep)


# ---------------------------------------------------------------------------
# Pretty-printing pydantic errors into something a human (or a calling pipeline)
# can act on, instead of a wall of internal detail.
# ---------------------------------------------------------------------------

def _format_pydantic_errors(exc: ValidationError) -> list[str]:
    out = []
    for err in exc.errors():
        # loc is a tuple path like ("tests", 2, "weight"); render it as a dotted
        # path so the offending field is obvious.
        loc = ".".join(str(p) for p in err["loc"]) or "<root>"
        out.append(f"{loc}: {err['msg']} (type={err['type']})")
    return out


# ---------------------------------------------------------------------------
# Top-level driver.
# ---------------------------------------------------------------------------

def load_json_object(path: Path) -> dict:
    """Read ``path`` and return a JSON object, or raise SystemExit(2) with a clear
    message. This is where we catch the single most common LLM failure: output
    that is not valid JSON at all (prose, code fences, truncation)."""
    if not path.exists():
        sys.stderr.write(f"ERROR: file not found: {path}\n")
        raise SystemExit(2)
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        sys.stderr.write(f"ERROR: file is empty: {path}\n")
        raise SystemExit(2)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.stderr.write(
            f"ERROR: {path} is not valid JSON: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno}).\n"
            "       The LLM likely wrapped the JSON in prose or ``` fences, or "
            "truncated it. The output must be a single bare JSON object.\n"
        )
        raise SystemExit(2)
    if not isinstance(data, dict):
        sys.stderr.write(
            f"ERROR: top-level JSON value is a {type(data).__name__}, expected an "
            "object (a single {...} mapping).\n"
        )
        raise SystemExit(2)
    return data


def validate(data: dict, strict: bool) -> Report:
    """Run the schema layer then the semantic layer, returning a Report."""
    rep = Report()

    # ---- schema layer (pydantic) ----
    try:
        model = ProblemOutput.model_validate(data)
    except ValidationError as exc:
        for msg in _format_pydantic_errors(exc):
            rep.error(f"schema: {msg}")
        # Without a valid model we cannot run the semantic checks meaningfully.
        return rep

    # ---- semantic layer ----
    semantic_checks(model, rep)
    return rep


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate LLM-generated problem JSON for lootcode "
                    "(see app/llm/problem_prompt.txt).",
    )
    parser.add_argument(
        "json_file",
        help="Path to the JSON file containing the LLM's structured output.",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat warnings as errors (exit non-zero if any warning).",
    )
    args = parser.parse_args(argv)

    path = Path(args.json_file)
    data = load_json_object(path)          # exits 2 on unreadable/non-object JSON
    rep = validate(data, strict=args.strict)

    # ---- print the report ----
    for w in rep.warnings:
        print(f"WARN:  {w}")
    for e in rep.errors:
        print(f"ERROR: {e}")

    if rep.ok(strict=args.strict):
        suffix = "" if not rep.warnings else f" ({len(rep.warnings)} warning(s))"
        print(f"OK: {path} is a valid problem-generation output{suffix}.")
        return 0

    print(
        f"INVALID: {path} has {len(rep.errors)} error(s) and "
        f"{len(rep.warnings)} warning(s)."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
