"""Mode A: fill a fixed problem statement in to a complete, verified problem.

Given a statement, ask an LLM for the runnable core — contract, canonical
solution, tests, hints — under a per-kind JSON schema, then verify it statically
and behaviourally with one corrective retry.

**One implementation, two front ends.** ``scripts/generate_problem_from_statement.py``
is the CLI (single file, folder batch, argparse); ``app/llm/generator.py`` is the
admin "Generate with AI" page. The app used to reach this code by inserting
``scripts/`` onto ``sys.path`` and ``__import__``-ing it by name, at request time
— the runtime depending on the tooling directory, and a rename away from an
ImportError deep in a request. It lives in the runtime package now, and the CLI
imports it like anything else.

That the two share the *same function* is load-bearing, not incidental: an
earlier re-implementation of this through the generic JSON helper diverged on
strict mode, thinking, and temperature, and silently dropped the optional hints
the CLI produces.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field

from .. import problem_spec
from ..config import BASE_DIR, settings
from ..executor import run_submission
from ..tags import CANONICAL_TAGS
from . import client as llm_client

PROMPT_PATH = BASE_DIR / "app" / "llm" / "problem_prompt.txt"
PLACEHOLDER = "{{PROBLEM_STATEMENT}}"

# Folder mode: for each <root>/<slug>/STATEMENT_FILENAME the model is asked to
# fill in the problem, and the object is written to <root>/<slug>/GENERATED_FILENAME.
STATEMENT_FILENAME = "problem.md"
GENERATED_FILENAME = "generated_full_problem.json"

# --- Structured-output schema (keep consistent with the data model) ----------
# Mirrors scripts/app/problem_spec.py::ProblemOutput and specs/problem-schema.md.
# `input`/`expected` are carried as NATIVE JSON (not JSON-encoded strings): with a
# llama.cpp grammar the model then physically cannot abbreviate a value with a
# Python expression.
#
# The schema is built per kind by ``problem_schema(kind)``:
#   * "class" / "function" — a *tight* schema for a known kind: it hard-requires
#     that kind's contract fields (class_name/class_methods, or function_name/
#     return_type) and shapes each test accordingly (for a class, input is exactly
#     {operations, args} and expected is the per-call output array).
#   * "auto" — a ``oneOf`` of the two tight branches. This is a valid schema and is
#     still exported (``PROBLEM_SCHEMA``), BUT it is deliberately NOT sent to the
#     model during generation: llama.cpp's grammar converter miscompiles a nested
#     any-JSON subschema inside a oneOf branch (a function's `expected` collapses to
#     an empty-object-only rule -> every expected came back as {}). Instead, auto
#     mode resolves the kind up front with a cheap ``classify_kind`` call and then
#     sends that kind's single tight branch. So the caller still doesn't need to know
#     the kind ahead of time, and each request carries a clean per-kind grammar.
#     Both auto failures a *loose* grammar used to allow are closed by the tight
#     branch: class_name/class_methods can't be omitted, and `expected` can't be a
#     nested test object (class) or an empty {} (function).
_PARAM = {
    "type": "object", "additionalProperties": False,
    "properties": {"name": {"type": "string"}, "type": {"type": "string"}},
    "required": ["name", "type"],
}
_RETURNS = {
    "type": "object", "additionalProperties": False,
    "properties": {"type": {"type": "string"}},
    "required": ["type"],
}
_METHOD = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "name": {"type": "string"},
        "params": {"type": "array", "items": _PARAM},
        "returns": _RETURNS,
    },
    "required": ["name", "params", "returns"],
}
# "Any JSON value" for a function's ``expected`` return. Do NOT use the empty
# schema {} for this: llama.cpp's json-schema->grammar converter compiles a bare
# {} into an empty-object-only rule, so every ``expected`` came back as {} (while
# the canonical produced the real answer). Spell out the union of JSON types
# instead — {"type":"array"} / {"type":"object"} with no further constraints each
# admit arbitrary contents (confirmed: the function ``input`` schema, {"type":
# "object"}, correctly produced {"nums": [...]} rather than {}).
_ANY_JSON_VALUE = {"anyOf": [
    {"type": "integer"}, {"type": "number"}, {"type": "string"},
    {"type": "boolean"}, {"type": "null"}, {"type": "array"}, {"type": "object"},
]}


def _test_schema(kind: str) -> dict:
    """Schema for one test case, tightened when the kind is known to be a class.

    For a class problem a test replays a call sequence against one instance, so
    ``input`` is exactly ``{operations, args}`` and ``expected`` is the *list* of
    per-call outputs. Constraining them (vs. the free-form ``object`` / any-JSON of
    the "auto"/function case) stops the model from, e.g., nesting a whole test
    object inside ``expected``.
    """
    if kind == "class":
        input_schema: dict = {
            "type": "object", "additionalProperties": False,
            "properties": {
                "operations": {"type": "array", "items": {"type": "string"}},
                "args": {"type": "array"},
            },
            "required": ["operations", "args"],
        }
        expected_schema: dict = {"type": "array"}  # one entry per operation
    else:
        input_schema = {"type": "object"}  # keys are the function's param names
        expected_schema = _ANY_JSON_VALUE  # any JSON value (the function's return)
    return {
        "type": "object", "additionalProperties": False,
        "properties": {
            "name": {"type": "string"},
            "input": input_schema,
            "expected": expected_schema,
            "weight": {"type": "integer", "minimum": 1},
            "hidden": {"type": "boolean"},
        },
        "required": ["name", "input", "expected", "weight", "hidden"],
    }


def _tags_schema() -> dict:
    """Schema for the ``tags`` array, constrained to the canonical vocabulary.

    ``tags`` come from a fixed, curated set (``app.tags.CANONICAL_TAGS``), so the
    items are an ``enum``: against a llama.cpp grammar this makes a non-canonical
    tag *physically unemittable* rather than caught downstream (by
    ``app/problem_spec.py`` / ``normalize_tags``), and it steers hosted endpoints
    too. The enum is sourced from ``app.tags`` (not re-hard-coded here) so the
    schema can never drift from the vocabulary — unlike the prose list baked into
    the prompt text, which ``warn_if_tags_drifted`` has to police. Falls back to a
    free-form string array if ``app`` isn't importable (matches the courtesy-skip
    pattern used elsewhere in this script).
    """
    # Constrained to the canonical vocabulary: this module used to live in
    # scripts/ and guard the import in case `app` wasn't importable. It is `app`.
    item: dict = {"type": "string", "enum": sorted(CANONICAL_TAGS)}
    return {"type": "array", "items": item, "minItems": 1, "uniqueItems": True}


def _kind_schema(kind: str) -> dict:
    """Tight object schema for one *known* kind (``"function"`` or ``"class"``).

    Only that kind's contract fields appear, and its kind-specific fields are
    hard-required, so under constrained decoding the model cannot omit them
    (class_name/class_methods, or function_name/return_type). ``tests`` items are
    shaped by the same kind (a class test is exactly {operations, args} -> output
    array). ``kind`` is required and its enum collapses to the single value, which
    is what lets a ``oneOf`` of the two branches discriminate cleanly.
    """
    props: dict = {
        "kind": {"type": "string", "enum": [kind]},
        "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
        "tags": _tags_schema(),
        "hints": {"type": "array", "items": {"type": "string"}},
    }
    if kind == "function":
        props["function_name"] = {"type": "string"}
        props["params"] = {"type": "array", "items": _PARAM}
        props["return_type"] = {"type": "string"}
        extra_required = ["function_name", "return_type"]
    else:  # class — params double as the constructor params.
        props["class_name"] = {"type": "string"}
        props["params"] = {"type": "array", "items": _PARAM}
        props["class_methods"] = {"type": "array", "items": _METHOD}
        extra_required = ["class_name", "class_methods"]
    props["compare"] = {"type": "string", "enum": ["exact", "unordered", "set_of_lists"]}
    props["starter_code"] = {"type": "string"}
    props["canonical_solution"] = {"type": "string"}
    props["tests"] = {"type": "array", "items": _test_schema(kind), "minItems": 1}
    # ``params`` is required so the grammar forces the model to emit the parameter
    # list rather than silently dropping it (a no-arg function or constructor emits
    # []). Leaving it optional lets the model skip it, after which every test
    # ``input`` key looks "unexpected" to app/problem_spec.py — the function-side
    # analog of the omitted class_name/class_methods failure.
    return {
        "type": "object", "additionalProperties": False,
        "properties": props,
        "required": ["kind", "difficulty", "tags", "params", "compare",
                     "starter_code", "canonical_solution", "tests", *extra_required],
    }


def problem_schema(kind: str = "auto") -> dict:
    """Build the structured-output schema, specialized to a declared ``kind``.

    ``kind`` is one of ``"auto"`` (model decides from the statement), ``"function"``,
    or ``"class"``.

    * A pinned ``"function"``/``"class"`` returns that kind's tight branch
      (``_kind_schema``): its contract fields are hard-required so, under
      constrained decoding, a class can't come back without class_name/
      class_methods (nor a function without function_name/return_type).
    * ``"auto"`` returns a ``oneOf`` of BOTH tight branches — a valid schema kept
      for callers/inspection, but NOT what ``generate`` sends to the model: a nested
      any-JSON subschema inside a oneOf branch is miscompiled by llama.cpp's grammar
      converter, so auto mode instead classifies the kind first (``classify_kind``)
      and sends the single tight branch. See the module comment above ``_PARAM``.
    """
    if kind in ("function", "class"):
        return _kind_schema(kind)
    # "auto": union of both tight branches (see docstring — not sent as-is by generate).
    return {"oneOf": [_kind_schema("function"), _kind_schema("class")]}


# Module-level default (auto kind) — kept for back-compat with importers/tests.
PROBLEM_SCHEMA = problem_schema("auto")


def load_prompt(statement: str) -> str:
    """Return the prompt with the statement injected in place of the token.

    Literal token replacement (not ``str.format``) on purpose: the template is full
    of JSON braces that ``str.format`` would choke on — the same convention the hint
    and help prompts use.
    """
    template = PROMPT_PATH.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise SystemExit(
            f"ERROR: prompt template {PROMPT_PATH} is missing the {PLACEHOLDER} token.")
    return template.replace(PLACEHOLDER, statement.strip())


def warn_if_tags_drifted() -> None:
    """Best-effort: warn if the tag list hard-coded in the prompt has drifted from
    ``app.tags.CANONICAL_TAGS``.

    The canonical vocabulary is embedded verbatim in ``problem_prompt.txt`` (the
    prompt is self-contained and sent to a remote endpoint, so it cannot reference
    ``app/tags.py``). That copy must be updated by hand whenever the canonical tags
    change — this check surfaces the mismatch instead of letting it rot silently.
    """
    try:
        from app.tags import CANONICAL_TAGS  # noqa: PLC0415
    except Exception:  # noqa: BLE001 - app not importable: skip the courtesy check
        return
    try:
        prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
    except OSError:
        return
    missing = sorted(t for t in CANONICAL_TAGS if t not in prompt_text)
    if missing:
        sys.stderr.write(
            "WARNING: these canonical tags are missing from "
            f"{PROMPT_PATH.name}: {missing}. The tag list is hard-coded in the "
            "prompt and must be kept in sync with app/tags.py::CANONICAL_TAGS.\n")


def _client(base_url: str, api_key: str):
    """The endpoint this fill-in runs against.

    ``GEN_LLM_TIMEOUT`` (seconds) overrides the read timeout. The default is
    generous on purpose: on a modest GPU throughput can dip to ~10 tok/s, so a
    ``--max-tokens 27000`` generation legitimately needs ~2700s, and a shorter
    cutoff spuriously "times out" a request the server would have completed.
    """
    try:
        return llm_client.openai_client(
            base_url, api_key, max_retries=1,
            timeout=float(os.environ.get("GEN_LLM_TIMEOUT", "3000")))
    except ImportError as exc:
        raise SystemExit(
            "ERROR: the 'openai' package is required. Install it with:\n"
            "    pip install openai") from exc


def classify_kind(statement: str, *, client, model: str) -> str:
    """Resolve a statement to "function" or "class" with one tiny schema call.

    Used by ``auto`` mode so we can then send that kind's *single* tight schema
    instead of a top-level ``oneOf(function, class)``. The oneOf is miscompiled by
    llama.cpp's grammar converter: a nested "any JSON value" subschema inside the
    function branch's ``expected`` collapses to an empty-object-only rule (every
    ``expected`` came back as ``{}`` while the canonical produced the real answer),
    whereas each standalone per-kind schema is clean. Thinking is forced OFF — the
    judgment is easy and we want it fast/cheap. Any failure falls back to
    "function" (the common case); a misclassified design problem is still caught
    downstream by app/problem_spec.py / verify_json.py.
    """
    schema = {
        "type": "object", "additionalProperties": False,
        "properties": {"kind": {"type": "string", "enum": ["function", "class"]}},
        "required": ["kind"],
    }
    system = ("Classify a coding-practice problem. Answer \"class\" if it asks to "
              "IMPLEMENT or DESIGN a data structure / object — a constructor plus "
              "methods that share state across calls (e.g. \"Implement the X "
              "class\", \"Design a ...\"). Otherwise answer \"function\".")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": statement}],
            max_tokens=200,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
            response_format={"type": "json_schema",
                             "json_schema": {"name": "kind_choice", "schema": schema,
                                             "strict": False}},
        )
        k = llm_client.loads_loose(resp.choices[0].message.content or "").get("kind")
        return k if k in ("function", "class") else "function"
    except Exception:  # noqa: BLE001 - classification is best-effort; default to function
        return "function"


def generate(statement: str, *, base_url: str, model: str, api_key: str,
             temperature: float | None, max_tokens: int, reasoning: str,
             kind: str = "auto", verify: bool = True, max_retries: int = 1,
             strict: bool = False) -> GenResult:
    """Generate a problem object, optionally verifying it and retrying on failure.

    ``kind`` is "auto" (default), "function", or "class". In ``auto`` the kind is
    resolved FROM THE STATEMENT by a cheap :func:`classify_kind` call first, then
    that kind's single tight schema is sent — we deliberately never send the
    ``oneOf`` auto schema to the model because llama.cpp miscompiles a nested
    any-JSON subschema inside a oneOf branch (see ``classify_kind``).

    When ``verify`` (default), each completion is checked by :func:`verify_output`
    (static schema/semantic + a behavioral run of the canonical against the tests);
    on failure the model is re-prompted with the concrete errors up to
    ``max_retries`` times. Returns a :class:`GenResult` carrying the final object,
    whether it verified, and any remaining errors. With ``verify=False`` the first
    completion is returned unchecked.
    """
    client = _client(base_url, api_key)
    # Resolve auto -> function/class up front so the request carries a single tight
    # per-kind schema (never the buggy top-level oneOf).
    if kind == "auto":
        kind = classify_kind(statement, client=client, model=model)
        sys.stderr.write(f"     (auto) classified as kind={kind}\n")
    prompt = load_prompt(statement)
    system = ("You are a precise coding-problem author. Output only the single "
              "requested JSON object — no prose, no Markdown, no code fences.")
    if kind == "class":
        # Reinforce the contract the (pinned) schema requires so the model's
        # *content* matches too.
        system += (" This is a CLASS/design problem: set kind=\"class\", include "
                   "class_name and class_methods, and make each test's `expected` "
                   "the LIST of per-call outputs (one entry per operation in "
                   "`input.operations`, with null for the constructor and any "
                   "void method).")
    else:  # function
        system += (" This is a plain FUNCTION problem: set kind=\"function\" and "
                   "include function_name and return_type.")
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    extra_body: dict = {}
    if reasoning in ("off", "on"):
        # llama.cpp/Qwen convention: gate the model's own thinking. `keep` omits the
        # knob entirely for endpoints (e.g. stock OpenAI) that reject unknown params.
        extra_body["chat_template_kwargs"] = {"enable_thinking": reasoning == "on"}

    schema = problem_schema(kind)

    # Generate, then (optionally) verify and retry once on failure. The verify pass
    # is both STATIC (schema/semantic) and BEHAVIORAL (runs the canonical against the
    # tests in the sandbox); on failure the model is re-prompted with the concrete
    # errors and asked to redo. See ``verify_output`` / ``_retry_message``.
    total_tries = 1 + (max_retries if verify else 0)
    data: dict = {}
    errors: list[str] = []
    attempts = 0
    while attempts < total_tries:
        attempts += 1
        data = _complete(client, messages, schema, model=model,
                         temperature=temperature, max_tokens=max_tokens,
                         extra_body=extra_body)
        if not verify:
            return GenResult(data=data, verified=True, errors=[], kind=kind,
                             attempts=attempts)
        ok, errors = verify_output(data, strict=strict)
        if ok:
            return GenResult(data=data, verified=True, errors=[], kind=kind,
                             attempts=attempts)
        if attempts >= total_tries:
            break
        # Correction pass: show the model its own output plus the concrete errors and
        # ask it to think again and fix them, keeping the same conversation/schema.
        sys.stderr.write(
            f"     verification failed ({len(errors)} problem(s)); re-prompting the "
            f"model (attempt {attempts + 1}/{total_tries})...\n")
        messages = [
            *messages,
            {"role": "assistant", "content": json.dumps(data, ensure_ascii=False)},
            {"role": "user", "content": _retry_message(errors)},
        ]
    return GenResult(data=data, verified=False, errors=errors, kind=kind,
                     attempts=attempts)


def _complete(client, messages: list, schema: dict, *, model: str,
              temperature: float | None, max_tokens: int, extra_body: dict) -> dict:
    """Send ONE chat completion and return the parsed object.

    Degrades through laxer response formats if a bare endpoint rejects the JSON
    schema (a network/timeout error is not retried that way — a laxer format won't
    fix it). Raises SystemExit on total failure.
    """
    response_formats = [
        {"type": "json_schema",
         "json_schema": {"name": "lootcode_problem", "schema": schema,
                         "strict": False}},
        {"type": "json_object"},
        None,
    ]
    last_err: Exception | None = None
    for rf in response_formats:
        kwargs = {"model": model, "messages": messages, "max_tokens": max_tokens}
        # Omit temperature entirely unless the caller set it, so the server's own
        # default governs sampling (don't silently impose one here).
        if temperature is not None:
            kwargs["temperature"] = temperature
        if extra_body:
            kwargs["extra_body"] = extra_body
        if rf is not None:
            kwargs["response_format"] = rf
        try:
            resp = client.chat.completions.create(**kwargs)
            return llm_client.loads_loose(resp.choices[0].message.content or "")
        except Exception as e:  # noqa: BLE001
            last_err = e
            if any(k in type(e).__name__ for k in ("Connection", "Timeout", "APIConnection")):
                break  # a transport failure won't be fixed by a laxer format
            continue
    raise SystemExit(f"ERROR: problem generation failed: {last_err}")


@dataclass
class GenResult:
    """Outcome of :func:`generate`: the object plus whether it was verified."""
    data: dict
    verified: bool           # passed verification (or verification was disabled)
    errors: list[str] = field(default_factory=list)  # remaining errors if not
    kind: str = "function"   # the resolved kind ("function"/"class")
    attempts: int = 1        # number of model completions performed


def verify_output(data: dict, *, strict: bool = False) -> tuple[bool, list[str]]:
    """Validate a generated problem object and return ``(ok, errors)``.

    Two layers, run in order; ``errors`` are phrased so they can be fed straight
    back to the model for a correction pass:

      1. STATIC — schema + semantic checks via ``scripts/app/problem_spec.py`` (never
         executes code). If these fail we stop here: the object may be unrunnable, so
         the model must fix its structure before a behavioral run means anything.
      2. BEHAVIORAL — actually run ``canonical_solution`` against every test in the
         sandbox via ``scripts/verify_json.py`` (the same ``run_submission`` path the
         Admin "Verify" button uses), and report each test whose produced output
         disagrees with its declared ``expected``.

    Each layer degrades gracefully (skips with a NOTE) if its dependency (pydantic /
    the app executor) can't be imported, so the script still runs standalone.
    """
    errors: list[str] = []

    # 1) static schema + semantic validation (no code execution)
    rep = problem_spec.validate(data, strict=strict)
    errors.extend(rep.errors)
    if strict:
        errors.extend(rep.warnings)
    if errors:
        return False, errors

    # 2) behavioral run of the canonical against the tests (real sandbox/judge).
    # `run_submission` normalizes the loose dict itself (problem_view/case_views);
    # a class problem's `function_name` is empty and the harness ignores it, but a
    # loose file may omit the limits, so those are supplied.
    try:
        graded = run_submission(data.get("canonical_solution") or "", {
            **data,
            "function_name": (data.get("function_name")
                              or data.get("class_name") or "").strip(),
            "time_limit_ms": settings.EXEC_TIME_LIMIT_MS,
            "memory_limit_mb": settings.EXEC_MEMORY_LIMIT_MB,
        }, data.get("tests") or [])
    except Exception as e:  # noqa: BLE001 - could not even run it
        return False, [f"canonical_solution could not be executed against the tests: {e}"]
    if graded.solved:
        return True, []

    tests = data.get("tests", [])
    for i, r in enumerate(graded.results):
        if r.passed:
            continue
        exp = tests[i].get("expected") if i < len(tests) else None
        if r.status == "wrong":
            errors.append(
                f"test {r.name!r}: your canonical_solution produced "
                f"{json.dumps(r.returned, ensure_ascii=False)} but the test's declared "
                f"expected is {json.dumps(exp, ensure_ascii=False)} — these MUST match "
                "(fix the canonical_solution, or correct the expected value).")
        else:  # timeout | error
            detail = f": {r.error}" if r.error else ""
            errors.append(
                f"test {r.name!r}: your canonical_solution did not run cleanly "
                f"({r.status}{detail}).")
    if not errors:  # not solved, but no per-test reason surfaced
        errors.append(f"canonical_solution passed only {graded.passed_count}/"
                      f"{graded.total_count} tests.")
    return False, errors


def _retry_message(errors: list[str]) -> str:
    """The correction prompt sent to the model after a failed verification."""
    bullets = "\n".join(f"  - {e}" for e in errors)
    return (
        "Your previous JSON output was REJECTED by the automatic checker. "
        "Problems found:\n\n"
        f"{bullets}\n\n"
        "Think again carefully and produce a corrected single JSON object that fixes "
        "ALL of the above. In particular, mentally RUN your canonical_solution on "
        "every test and make sure it returns EXACTLY that test's declared `expected` "
        "value under the declared compare mode. Do not change the problem statement "
        "or the kind. Output only the corrected JSON object — no prose, no Markdown, "
        "no code fences.")
