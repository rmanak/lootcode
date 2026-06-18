"""Generate coding problems with the Claude API, then verify them.

A generated problem is only trustworthy if its reference solution actually
passes its own tests — so every generated problem is run through the sandbox
executor before it is returned. Uses the Anthropic Python SDK; the model
defaults to claude-opus-4-8 (override with ANTHROPIC_MODEL).
"""
from __future__ import annotations

import json
import re
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

# Structured-output schema. Test input/expected are JSON-encoded *strings* so the
# schema stays strict-validation friendly while still carrying arbitrary values.
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
                    "input_json": {"type": "string"},
                    "expected_json": {"type": "string"},
                    "weight": {"type": "integer"},
                    "hidden": {"type": "boolean"},
                },
                "required": ["name", "input_json", "expected_json", "weight", "hidden"],
            },
        },
    },
    "required": ["slug", "title", "difficulty", "topics", "statement_md",
                 "function_name", "params", "return_type", "starter_code",
                 "canonical_solution", "compare", "tests"],
}

SYSTEM = """You are an expert author of coding-practice problems for a LeetCode-style platform.
You write problems solvable in Python 3 with a single top-level function.

Rules:
- The solver implements ONE top-level function named `function_name` taking exactly
  the listed parameters (by name). No class wrapper.
- `starter_code` is a stub of that function with a docstring/comment, no solution.
- `canonical_solution` is a COMPLETE, CORRECT Python solution that defines the same
  top-level function and passes every test.
- Each test's `input_json` is a JSON object mapping each parameter name to its value;
  `expected_json` is the JSON-encoded expected return value. Both must be valid JSON.
- Provide 6-10 tests total: a few visible (hidden=false, used as examples) and several
  hidden (hidden=true), including edge cases and at least one larger input.
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


def _client():
    import anthropic

    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _extract_text(resp) -> str:
    return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")


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


def _complete_json(user: str) -> dict:
    client = _client()
    common = dict(model=settings.ANTHROPIC_MODEL, max_tokens=16000,
                  system=_system_prompt(), messages=[{"role": "user", "content": user}])
    try:
        resp = client.messages.create(
            output_config={"format": {"type": "json_schema", "schema": PROBLEM_SCHEMA}},
            **common,
        )
    except Exception:  # noqa: BLE001 - older SDK / unsupported param: plain JSON ask
        resp = client.messages.create(**common)
    return _loads_loose(_extract_text(resp))


def _to_internal(raw: dict) -> dict:
    tests = [{
        "name": t["name"],
        "input": json.loads(t["input_json"]),
        "expected": json.loads(t["expected_json"]),
        "weight": int(t.get("weight", 1)),
        "hidden": bool(t.get("hidden", False)),
    } for t in raw["tests"]]
    return {
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


def generate_problem(brief: str, difficulty: str | None = None) -> dict:
    """Generate one verified problem dict (ready for store.upsert_problem)."""
    user = (f"Create ONE Python coding problem.\nIdea / topic: {brief}\n"
            f"Difficulty: {difficulty or 'you choose'}\n"
            "Make the slug short, kebab-case, and descriptive.")
    raw = _complete_json(user)
    data = _to_internal(raw)
    if difficulty:
        data["difficulty"] = difficulty

    graded = _validate(data)
    if not graded.solved:  # one corrective retry
        retry = user + (f"\n\nA previous attempt's reference solution failed "
                        f"{graded.total_count - graded.passed_count} of "
                        f"{graded.total_count} tests. Make sure canonical_solution "
                        "passes ALL tests and every expected_json is correct.")
        data = _to_internal(_complete_json(retry))
        if difficulty:
            data["difficulty"] = difficulty
        graded = _validate(data)

    data["_validation"] = {"solved": graded.solved, "passed": graded.passed_count,
                           "total": graded.total_count}
    return data


def generate_from_text(text: str, count: int = 3) -> list[dict]:
    """Derive up to `count` problems from a blob of text (e.g. a list of ideas)."""
    count = max(1, min(int(count or 1), 5))
    brief_prompt = (
        f"From the material below, propose {count} distinct coding problems (you may "
        "reuse the same techniques with different framing). Return ONLY a JSON object "
        '{"problems":[{"title":...,"brief":...,"difficulty":"easy|medium|hard"}]}.\n\n'
        f"MATERIAL:\n{text[:8000]}"
    )
    client = _client()
    resp = client.messages.create(
        model=settings.ANTHROPIC_MODEL, max_tokens=4000,
        system="You plan coding-practice problem sets. Output only the requested JSON.",
        messages=[{"role": "user", "content": brief_prompt}],
    )
    briefs = _loads_loose(_extract_text(resp)).get("problems", [])[:count]

    out = []
    for b in briefs:
        idea = b.get("brief") or b.get("title") or ""
        if not idea:
            continue
        out.append(generate_problem(idea, b.get("difficulty")))
    return out
