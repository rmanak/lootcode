"""Generate coding problems with an LLM, then verify them.

A generated problem is only trustworthy if its reference solution actually
passes its own tests — so every generated problem is run through the sandbox
executor before it is returned.

Two backends, chosen automatically by :func:`active_backend`:

* **anthropic** — the Claude API (preferred when ``ANTHROPIC_API_KEY`` is set);
  model defaults to claude-opus-4-8 (override with ``ANTHROPIC_MODEL``).
* **openai** — any OpenAI-compatible endpoint (llama.cpp's ``llama-server`` or a
  cloud provider), the same one the "Get More Help with AI" button uses
  (``LLM_HELP_URL`` / ``LLM_HELP_API_KEY`` / ``LLM_HELP_MODEL``). Used as a fallback
  when no Claude key is configured but the startup probe found a live endpoint.

Both paths ask for the same JSON schema and run through the same verify step, so
the rest of the app doesn't care which produced a given problem.
"""
from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass

from ..config import BASE_DIR, settings
from ..executor import run_submission

# Authoring guidelines live in specs/ as the single source of truth. The block
# between the AI-GUIDELINES markers is injected into the system prompt at
# generation time, so editing that file changes generated problems with no code
# change or restart. See specs/problem-authoring-guidelines.md.
GUIDELINES_PATH = BASE_DIR / "specs" / "problem-authoring-guidelines.md"
_GUIDELINES_RE = re.compile(
    r"<!--\s*AI-GUIDELINES:START\s*-->(.*?)<!--\s*AI-GUIDELINES:END\s*-->", re.DOTALL
)

# Structured-output schema. `input`/`expected` are carried as *native* JSON values,
# not JSON-encoded strings: with constrained decoding (llama.cpp builds a GBNF grammar
# from this schema, so the emitted tokens are guaranteed schema-valid) the model
# physically cannot produce an invalid inner value — e.g. it can no longer abbreviate a
# large input with a Python expression like `"ab" * 1000`, which is what used to slip
# through a plain string field and then blow up at json.loads() time. `input` is the
# argument object {param_name: value}; `expected` (empty schema) is any JSON value.
PROBLEM_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "slug": {"type": "string"},
        "title": {"type": "string"},
        "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
        "topics": {"type": "array", "items": {"type": "string"}},
        "statement_md": {"type": "string"},
        "function_name": {"type": "string"},
        "params": {
            "type": "array",
            "items": {
                "type": "object", "additionalProperties": False,
                "properties": {"name": {"type": "string"}, "type": {"type": "string"}},
                "required": ["name", "type"],
            },
        },
        "return_type": {"type": "string"},
        "starter_code": {"type": "string"},
        "canonical_solution": {"type": "string"},
        "compare": {"type": "string", "enum": ["exact", "unordered", "set_of_lists"]},
        "tests": {
            "type": "array",
            "items": {
                "type": "object", "additionalProperties": False,
                "properties": {
                    "name": {"type": "string"},
                    # Native JSON, grammar-enforced (see schema note above): `input` is
                    # the argument object; `expected` (empty schema) is any JSON value.
                    "input": {"type": "object"},
                    "expected": {},
                    "weight": {"type": "integer"},
                    "hidden": {"type": "boolean"},
                },
                "required": ["name", "input", "expected", "weight", "hidden"],
            },
        },
    },
    "required": ["slug", "title", "difficulty", "topics", "statement_md",
                 "function_name", "params", "return_type", "starter_code",
                 "canonical_solution", "compare", "tests"],
}

# Schema for the "plan a batch" step of generate_from_text: a list of briefs.
PLAN_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "problems": {
            "type": "array",
            "items": {
                "type": "object", "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "brief": {"type": "string"},
                    "difficulty": {"type": "string", "enum": ["easy", "medium", "hard"]},
                },
                "required": ["title", "brief", "difficulty"],
            },
        },
    },
    "required": ["problems"],
}

SYSTEM = """You are an expert author of coding-practice problems for a LeetCode-style platform.
You write problems solvable in Python 3 with a single top-level function.

Rules:
- The solver implements ONE top-level function named `function_name` taking exactly
  the listed parameters (by name). No class wrapper.
- `starter_code` is a stub of that function with a docstring/comment, no solution.
- `canonical_solution` is a COMPLETE, CORRECT Python solution that defines the same
  top-level function and passes every test.
- Each test's `input` is a JSON object mapping each parameter name to its value (native
  JSON, NOT a string). `expected` is the return value ITSELF, exactly as the function
  returns it — do NOT wrap it in an object or add a key like "result". If the function
  returns the integer 5, `expected` is `5` (never `{"result": 5}`); if it returns a list,
  `expected` is that list. Write every value out in full — no expressions of any kind
  (no arithmetic, no string/list repetition like `"ab" * 1000` or `[0] * 100`, no
  concatenation, no variables).
  Example test object for a function summing two ints (add(a, b) -> int):
  {"name": "basic", "input": {"a": 2, "b": 3}, "expected": 5, "weight": 1, "hidden": false}
- Provide 6-10 tests total: a few visible (hidden=false, used as examples) and several
  hidden (hidden=true), including edge cases and at least one larger input. Write the
  larger input out as a literal of a size you can spell in full (up to a few hundred
  elements/characters is plenty).
- `weight` is a small positive integer (use 1 unless a test deserves more).
- `statement_md` is Markdown: a clear statement, **Constraints**, and 2-3 examples.
- `compare` is how the judge matches the returned value: `exact` (order matters),
  `unordered` (the returned list is a multiset; top-level order ignored), or
  `set_of_lists` (list of groups; outer order AND each inner list's order ignored).
  It MUST agree with the statement — if the statement allows "any order", do NOT
  use `exact`. Every test's expected value must be correct under this mode.
- Keep difficulty honest. Return values must be JSON-serializable.
Output must conform to the requested JSON schema."""


def _authoring_guidelines() -> str:
    """The marked block of the authoring guidelines, or '' if unavailable.

    Read fresh on each call so edits to the guidelines file take effect for the
    next generation without restarting the app.
    """
    try:
        text = GUIDELINES_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""
    m = _GUIDELINES_RE.search(text)
    block = m.group(1) if m else text
    block = re.sub(r"<!--.*?-->", "", block, flags=re.DOTALL)  # drop owner-only comments
    return block.strip()


def _system_prompt() -> str:
    """Base rules plus the project's authoring guidelines (the latter are MANDATORY)."""
    extra = _authoring_guidelines()
    if not extra:
        return SYSTEM
    return (f"{SYSTEM}\n\nPROJECT AUTHORING GUIDELINES (mandatory — follow in "
            f"addition to the rules above):\n\n{extra}")


@dataclass
class _ProblemLike:
    function_name: str
    params: list
    time_limit_ms: int
    memory_limit_mb: int
    compare: str = "exact"
    points: int = 100


@dataclass
class _TestLike:
    name: str
    input: dict
    expected: object
    weight: int
    hidden: bool


def active_backend() -> str:
    """Which LLM backend problem generation will use, or '' if none is available.

    ``LLM_GEN_BACKEND`` picks a preference (``auto`` | ``anthropic`` | ``openai``);
    ``auto`` prefers the Claude API when an ``ANTHROPIC_API_KEY`` is set (far
    stronger at authoring a correct canonical + tests) and otherwise uses the
    OpenAI-compatible endpoint the startup probe found live. A forced-but-
    unavailable preference falls back to whatever is reachable.
    """
    available = []
    if settings.ai_enabled:
        available.append("anthropic")
    if settings.llm_help_available:
        available.append("openai")
    if not available:
        return ""
    pref = settings.LLM_GEN_BACKEND
    if pref in available:
        return pref
    # 'auto', or a forced preference that isn't reachable: take the default order
    # (anthropic first when both are present).
    return available[0]


def _loads_loose(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        i, j = text.find("{"), text.rfind("}")
        if i == -1 or j == -1:
            raise
        return json.loads(text[i:j + 1])


# --- Anthropic backend ----------------------------------------------------
def _anthropic_client():
    import anthropic

    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _extract_text(resp) -> str:
    return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")


def _anthropic_json(system: str, user: str, schema: dict, max_tokens: int) -> dict:
    client = _anthropic_client()
    common = dict(model=settings.ANTHROPIC_MODEL, max_tokens=max_tokens,
                  system=system, messages=[{"role": "user", "content": user}])
    try:
        resp = client.messages.create(
            output_config={"format": {"type": "json_schema", "schema": schema}},
            **common,
        )
    except Exception:  # noqa: BLE001 - older SDK / unsupported param: plain JSON ask
        resp = client.messages.create(**common)
    return _loads_loose(_extract_text(resp))


# --- OpenAI-compatible backend --------------------------------------------
def _openai_client():
    from openai import OpenAI

    base = settings.LLM_HELP_URL.rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    # Generation is heavy (a full problem + canonical + tests), so allow plenty of
    # time and one retry; unlike the interactive hint path this isn't latency-bound.
    return OpenAI(base_url=base, api_key=settings.LLM_HELP_API_KEY,
                  timeout=300.0, max_retries=1)


def _openai_json(system: str, user: str, schema: dict, max_tokens: int) -> dict:
    client = _openai_client()
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": user}]
    # Reasoning off: keeps generation from stalling and its tokens from crowding out
    # the JSON (a llama.cpp/Qwen convention; plain OpenAI servers ignore it). The
    # canonical is verified afterwards, with one corrective retry, either way.
    extra_body = {"chat_template_kwargs": {"enable_thinking": False}}
    # Enforce structure when supported, degrading to laxer modes for bare endpoints.
    response_formats = [
        {"type": "json_schema",
         "json_schema": {"name": "problem", "schema": schema, "strict": True}},
        {"type": "json_object"},
        None,
    ]
    last_err: Exception | None = None
    for rf in response_formats:
        kwargs = dict(model=settings.LLM_HELP_MODEL, messages=messages,
                      max_tokens=max_tokens, temperature=0.3, extra_body=extra_body)
        if rf is not None:
            kwargs["response_format"] = rf
        try:
            resp = client.chat.completions.create(**kwargs)
            return _loads_loose(resp.choices[0].message.content or "")
        except Exception as e:  # noqa: BLE001
            last_err = e
            # A network failure won't be fixed by a laxer response_format; only a
            # rejected/unsupported param is worth retrying with the next mode.
            if any(k in type(e).__name__ for k in ("Connection", "Timeout")):
                break
            continue
    raise RuntimeError(f"LLM problem generation failed: {last_err}") from last_err


def _llm_json(system: str, user: str, schema: dict, max_tokens: int) -> dict:
    """Route a JSON-returning completion to whichever backend is configured."""
    backend = active_backend()
    if backend == "anthropic":
        return _anthropic_json(system, user, schema, max_tokens)
    if backend == "openai":
        return _openai_json(system, user, schema, max_tokens)
    raise RuntimeError(
        "No LLM backend configured: set ANTHROPIC_API_KEY, or point LLM_HELP_URL at "
        "a reachable OpenAI-compatible endpoint and restart.")


def _complete_json(user: str) -> dict:
    return _llm_json(_system_prompt(), user, PROBLEM_SCHEMA, max_tokens=16000)


def _test_io(t: dict) -> tuple:
    """(input, expected) for one test, native-JSON first.

    Constrained decoding gives us native `input`/`expected` values already. We still
    accept the legacy JSON-string form (`input_json`/`expected_json`) as a fallback so an
    unconstrained or degraded backend — a bare `json_object` response, a plain Claude
    prompt — keeps working; those strings are re-parsed (and may raise, which the caller
    treats as a malformed test to skip).
    """
    inp = t["input"] if "input" in t else json.loads(t["input_json"])
    exp = t["expected"] if "expected" in t else json.loads(t["expected_json"])
    return inp, exp


def _to_internal(raw: dict) -> dict:
    # With constrained decoding `input`/`expected` are already valid native JSON. The
    # skip-on-error path only fires for an unconstrained/degraded backend that hand-rolled
    # a malformed JSON string; skip just that test rather than aborting the whole run.
    tests, dropped = [], []
    for t in raw["tests"]:
        try:
            inp, exp = _test_io(t)
        except (json.JSONDecodeError, KeyError, TypeError):
            dropped.append(t.get("name", "?"))
            continue
        tests.append({
            "name": t["name"], "input": inp, "expected": exp,
            "weight": max(1, min(int(t.get("weight", 1) or 1), 1000)),
            "hidden": bool(t.get("hidden", False)),
        })
    if not tests:
        raise ValueError(
            f"model produced {len(raw['tests'])} test(s) but none had usable "
            "input/expected values. Try generating again.")
    return {
        "_dropped_tests": dropped,
        "slug": raw["slug"], "title": raw["title"],
        "difficulty": raw.get("difficulty", "easy"), "topics": raw.get("topics", []),
        "statement_md": raw["statement_md"], "function_name": raw["function_name"],
        "params": raw.get("params", []), "return_type": raw.get("return_type", ""),
        "starter_code": raw.get("starter_code", ""),
        "canonical_solution": raw.get("canonical_solution", ""),
        "compare": raw.get("compare", "exact"),
        "scoring_type": "weighted", "points": 100, "source": "ai",
        "time_limit_ms": settings.EXEC_TIME_LIMIT_MS,
        "memory_limit_mb": settings.EXEC_MEMORY_LIMIT_MB, "tests": tests,
    }


def _validate(data: dict):
    prob = _ProblemLike(
        function_name=data["function_name"], params=data["params"],
        time_limit_ms=data["time_limit_ms"], memory_limit_mb=data["memory_limit_mb"],
        compare=data.get("compare", "exact"),
    )
    tcs = [_TestLike(t["name"], t["input"], t["expected"], t["weight"], t["hidden"])
           for t in data["tests"]]
    return run_submission(data.get("canonical_solution") or "", prob, tcs)


def _sync_expected_to_canonical(data: dict) -> dict:
    """Overwrite each test's `expected` with what the canonical solution actually returns.

    The canonical is this project's sole oracle (see docs/test-strengthening.md). A weaker
    model reliably mis-formats or mis-computes `expected` — even under constrained decoding
    it wraps a scalar as ``{"result": 5}`` because the field is an untyped ("any") slot —
    so rather than trust it, we run the canonical over the model's (grammar-valid) `input`s
    and adopt its output as ground truth. This collapses the whole class of wrong/ill-typed
    expected values into "correct by construction". Tests where the canonical raises or
    times out are left untouched — the canonical is genuinely broken on that input, so the
    caller retries or drops them. Returns ``{"failing": [...names], "agree": n, "ran": m}``
    where agree/ran is how often the model's own `expected` already matched the canonical
    (a soft trust signal for the canonical when they agree).
    """
    graded = _validate(data)
    failing, agree, ran = [], 0, 0
    for test, res in zip(data["tests"], graded.results):
        if res.status in ("passed", "wrong"):
            ran += 1
            if res.status == "passed":  # model's expected already matched the oracle
                agree += 1
            test["expected"] = res.returned
        else:  # error | timeout: the canonical itself fails on this input
            failing.append(res.name)
    return {"failing": failing, "agree": agree, "ran": ran}


Progress = Callable[[str], None] | None


def _emit(on_progress: Progress, message: str) -> None:
    """Report a coarse progress step (for the streaming admin UI); no-op if unset."""
    if on_progress:
        on_progress(message)


def generate_problem(brief: str, difficulty: str | None = None,
                     on_progress: Progress = None) -> dict:
    """Generate one verified problem dict (ready for store.upsert_problem).

    ``on_progress(message)`` — if given — is called at each coarse stage so a caller
    (the admin streaming endpoint) can show live progress during the slow model calls.
    """
    user = (f"Create ONE Python coding problem.\nIdea / topic: {brief}\n"
            f"Difficulty: {difficulty or 'you choose'}\n"
            "Make the slug short, kebab-case, and descriptive.")
    def build(prompt: str) -> dict:
        d = _to_internal(_complete_json(prompt))
        if difficulty:
            d["difficulty"] = difficulty
        return d

    # Ground-truth the expected values against the canonical (the oracle). The only thing
    # left to fix afterwards is a canonical that errors/times out on some input.
    _emit(on_progress, "Drafting the problem with the model…")
    data = build(user)
    _emit(on_progress, f"Verifying the reference solution against {len(data['tests'])} tests…")
    sync = _sync_expected_to_canonical(data)
    if sync["failing"]:  # one corrective retry, targeted at the actual failure
        _emit(on_progress,
              f"Reference solution failed on {len(sync['failing'])} input(s); regenerating…")
        retry = user + (
            f"\n\nA previous canonical_solution raised an error or timed out on "
            f"{len(sync['failing'])} of {len(data['tests'])} test input(s). Return a "
            "canonical_solution that runs correctly — no exceptions, within the time "
            "limit — on every input.")
        data = build(retry)
        _emit(on_progress, f"Re-verifying against {len(data['tests'])} tests…")
        sync = _sync_expected_to_canonical(data)

    # Drop any inputs the canonical still can't run, so the stored suite is self-consistent.
    if sync["failing"]:
        drop = set(sync["failing"])
        data["_dropped_tests"] = data.get("_dropped_tests", []) + [
            t["name"] for t in data["tests"] if t["name"] in drop]
        data["tests"] = [t for t in data["tests"] if t["name"] not in drop]
    if not data["tests"]:
        raise ValueError("canonical_solution failed on every test input; try again.")

    _emit(on_progress, "Finalizing…")
    graded = _validate(data)  # confirm the synced, on-disk suite is coherent
    data["_validation"] = {"solved": graded.solved, "passed": graded.passed_count,
                           "total": graded.total_count,
                           "dropped": data.get("_dropped_tests", []),
                           "oracle_agreement": [sync["agree"], sync["ran"]]}
    return data


def generate_from_text(text: str, count: int = 3, on_progress: Progress = None,
                       on_problem: Callable[[dict], None] | None = None) -> list[dict]:
    """Derive up to `count` problems from a blob of text (e.g. a list of ideas).

    ``on_progress(message)`` reports coarse stages; ``on_problem(data)`` — if given — is
    called with each verified problem as soon as it is ready, so a streaming caller can
    save + surface results incrementally rather than only at the end.
    """
    count = max(1, min(int(count or 1), 5))
    brief_prompt = (
        f"From the material below, propose {count} distinct coding problems (you may "
        "reuse the same techniques with different framing). Return ONLY a JSON object "
        '{"problems":[{"title":...,"brief":...,"difficulty":"easy|medium|hard"}]}.\n\n'
        f"MATERIAL:\n{text[:8000]}"
    )
    _emit(on_progress, f"Planning up to {count} problems…")
    planned = _llm_json(
        "You plan coding-practice problem sets. Output only the requested JSON.",
        brief_prompt, PLAN_SCHEMA, max_tokens=4000)
    briefs = [b for b in planned.get("problems", [])[:count]
              if (b.get("brief") or b.get("title"))]

    out = []
    for i, b in enumerate(briefs, 1):
        idea = b.get("brief") or b.get("title") or ""
        title = b.get("title") or idea[:48]
        _emit(on_progress, f"Problem {i}/{len(briefs)}: {title}")
        step = (lambda m, i=i, n=len(briefs): _emit(on_progress, f"[{i}/{n}] {m}"))
        data = generate_problem(idea, b.get("difficulty"), on_progress=step)
        out.append(data)
        if on_problem:
            on_problem(data)
    return out
