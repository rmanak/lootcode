"""Generate progressive, non-spoiling hints for a coding problem.

This module talks to a *local* LLM exposed over an OpenAI-compatible HTTP API —
the kind llama.cpp's ``llama-server`` serves at ``http://localhost:<PORT>/v1``.
It uses the official ``openai`` Python client pointed at that base URL, so no
cloud calls and no real API key are involved.

The wording of the prompt lives next to this file in ``hint_prompt.txt`` so it can
be tuned without touching code; the problem statement is injected into that
template here (see :func:`_render_prompt`).

Structured output: when the server supports it we pass a JSON-schema
``response_format``, which constrains the model to emit exactly
``{"hints": [...]}``. llama.cpp enforces this via a GBNF grammar, so the reply is
*guaranteed* to be conforming JSON; stricter OpenAI-style servers honour it as
Structured Outputs. We degrade gracefully — ``json_object``, then a plain request
with loose parsing — so the function still works against a bare-bones endpoint.

Example
-------
    from app.llm.hint_generator import generate_hints

    hints = generate_hints("Given an array of integers nums ... return indices ...")
    for i, h in enumerate(hints, 1):
        print(f"Hint {i}: {h}")
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

# --------------------------------------------------------------------------- #
# LLM server location — EDIT THIS (or set the env vars) to point at your server.
#
# llama.cpp's ``llama-server`` listens on http://localhost:8080 by default and
# serves the OpenAI-compatible API under the ``/v1`` path. Set LLM_SERVER_URL to
# ``http://localhost:<PORT>`` for whatever port your server uses.
# --------------------------------------------------------------------------- #
LLM_SERVER_URL = os.environ.get("LLM_SERVER_URL", "http://localhost:8080")

# Model name to request. llama.cpp serves a single model and largely ignores this,
# but the OpenAI client requires *some* value; override if your server is picky.
LLM_MODEL = os.environ.get("LLM_MODEL", "local-model")

# llama.cpp does not check the key, but the OpenAI client insists on a non-empty
# string. Only override if your endpoint actually enforces auth.
LLM_API_KEY = os.environ.get("LLM_API_KEY", "sk-no-key-required")

# Hard cap on hints, matching the app's problem schema (see specs/problem-schema.md).
MAX_HINTS = 3

_PROMPT_TEMPLATE_PATH = Path(__file__).with_name("hint_prompt.txt")
_JUDGE_TEMPLATE_PATH = Path(__file__).with_name("hint_judge_prompt.txt")

# Persona / global instruction. The substantive prompt lives in the template file.
_SYSTEM = (
    "You are a careful programming tutor who gives graded hints that guide a "
    "student toward solving a problem themselves, and who never reveals the full "
    "solution. You always reply with exactly the JSON object you are asked for."
)

# Persona for the critic pass (see hint_judge_prompt.txt for the full rubric).
_JUDGE_SYSTEM = (
    "You are a strict, terse grader of coding-problem hints. You reply with exactly "
    "the JSON object you are asked for and nothing else."
)


def _hints_schema(max_hints: int) -> dict:
    """JSON schema the model's reply must satisfy: ``{"hints": [str, ...]}``.

    ``max_hints`` bounds the array so the model cannot over-produce. llama.cpp
    compiles this into a grammar and guarantees conforming output.
    """
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "hints": {
                "type": "array",
                "minItems": 1,
                "maxItems": max_hints,
                "items": {"type": "string"},
            },
        },
        "required": ["hints"],
    }


def _client(base_url: str, api_key: str):
    """Build an OpenAI client pointed at the local server's ``/v1`` endpoint.

    Imported lazily so ``openai`` stays an optional dependency: modules that never
    call :func:`generate_hints` do not need the package installed.
    """
    from openai import OpenAI

    base = base_url.rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    return OpenAI(base_url=base, api_key=api_key)


def _render_prompt(statement: str, max_hints: int) -> str:
    """Inject the problem statement into the plain-text prompt template.

    Uses literal token replacement rather than ``str.format`` on purpose: problem
    statements routinely contain ``{``/``}`` from code snippets or set notation,
    which would make ``str.format`` raise. The template exposes two tokens,
    ``{{STATEMENT}}`` and ``{{MAX_HINTS}}``.
    """
    template = _PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
    return (
        template
        .replace("{{MAX_HINTS}}", str(max_hints))
        .replace("{{STATEMENT}}", statement.strip())
    )


def _loads_loose(text: str):
    """``json.loads`` that tolerates code fences / stray prose from weaker models."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        i, j = text.find("{"), text.rfind("}")
        if i != -1 and j != -1 and j > i:
            return json.loads(text[i:j + 1])
        raise


def _parse_hints(content: str, max_hints: int) -> list[str]:
    """Pull the hint strings out of the model's reply, defensively.

    Accepts the expected ``{"hints": [...]}`` object, but also a bare JSON array,
    and drops blank entries before capping the list at ``max_hints``.
    """
    data = _loads_loose(content)
    if isinstance(data, dict):
        raw = data.get("hints", [])
    elif isinstance(data, list):
        raw = data
    else:
        raw = []
    hints = [str(h).strip() for h in raw if str(h).strip()]
    return hints[:max_hints]


def generate_hints(
    statement: str,
    *,
    max_hints: int = MAX_HINTS,
    base_url: str = LLM_SERVER_URL,
    model: str = LLM_MODEL,
    api_key: str = LLM_API_KEY,
    temperature: float = 0.6,
    thinking: bool = False,
    feedback: str | None = None,
) -> list[str]:
    """Generate up to ``max_hints`` progressive, non-spoiling hints for a problem.

    Parameters
    ----------
    statement:
        The problem's full body/statement/description as a string. This is the
        only required argument; every other parameter has a sensible default.
    max_hints:
        Upper bound on how many hints to return (clamped to ``[1, MAX_HINTS]``,
        default 3). Hints come back ordered least-revealing first.
    base_url:
        Base URL of the OpenAI-compatible server, e.g. ``"http://localhost:8080"``.
        ``"/v1"`` is appended automatically if it is missing.
    model, api_key, temperature:
        Passed through to the chat-completions call. ``api_key`` may be any
        non-empty string for llama.cpp; ``temperature`` is kept low for focused,
        reproducible hints.
    thinking:
        Whether to let a reasoning ("thinking") model deliberate before answering.
        Default ``False``: thinking sharpens the hint progression only marginally
        but is far slower (~20-40s vs ~3s here) and burns many more tokens, so it's
        off for interactive/bulk use. Qwen3-style templates expose this as a
        *binary* switch (there is no graded ``reasoning_effort``); we forward it as
        ``chat_template_kwargs.enable_thinking`` via ``extra_body``. Servers/models
        that don't recognise the flag simply ignore it. To *cap* (rather than
        disable) thinking, launch the server with ``--reasoning-budget N`` instead.
    feedback:
        Optional revision guidance appended to the prompt. When a previous attempt
        was judged to reveal too much or be too vague, pass the critique here to ask
        for a corrected set. Used by :func:`generate_hints_verified`.

    Returns
    -------
    list[str]
        Between 0 and ``max_hints`` hint strings, most general first. Empty only
        if the model returned nothing usable.

    Raises
    ------
    ValueError
        If ``statement`` is empty or whitespace.
    RuntimeError
        If every attempt to reach the LLM fails (e.g. the server is unreachable).
    """
    if not statement or not statement.strip():
        raise ValueError("`statement` must be a non-empty problem description.")
    max_hints = max(1, min(int(max_hints), MAX_HINTS))

    client = _client(base_url, api_key)
    user_content = _render_prompt(statement, max_hints)
    if feedback and feedback.strip():
        user_content += (
            "\n\n# Revision\n"
            "Your previous attempt had problems. Rewrite the FULL set, keeping the "
            "progressive structure but fixing exactly these:\n"
            f"{feedback.strip()}\n"
            "Return the corrected JSON object only."
        )
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user_content},
    ]
    schema = _hints_schema(max_hints)

    # Enforce structure when the server supports it, degrading to laxer modes so a
    # minimal endpoint still works. Ordered most-constrained first.
    response_formats = [
        {"type": "json_schema",
         "json_schema": {"name": "hints", "schema": schema, "strict": True}},
        {"type": "json_object"},
        None,  # plain request; rely on the prompt + loose parsing
    ]

    # Reasoning models default to "thinking on"; disable it explicitly when asked.
    # This is a llama.cpp / Qwen convention passed through the OpenAI client's
    # `extra_body`; unknown to a plain OpenAI server, which ignores it.
    extra_body = {} if thinking else {"chat_template_kwargs": {"enable_thinking": False}}

    last_err: Exception | None = None
    for rf in response_formats:
        kwargs = dict(model=model, messages=messages, temperature=temperature,
                      extra_body=extra_body)
        if rf is not None:
            kwargs["response_format"] = rf
        try:
            resp = client.chat.completions.create(**kwargs)
            return _parse_hints(resp.choices[0].message.content or "", max_hints)
        except Exception as e:  # noqa: BLE001
            last_err = e
            # A network/timeout failure won't be fixed by a laxer response_format;
            # only a rejected/unsupported param is worth retrying with the next mode.
            if any(k in type(e).__name__ for k in ("Connection", "Timeout")):
                break
            continue

    raise RuntimeError(f"LLM hint generation failed: {last_err}") from last_err


# --------------------------------------------------------------------------- #
# Quality gate: a cheap heuristic pre-filter + an LLM critic ("judge"), wired
# together into a generate -> judge -> regenerate loop. See docs/hint-generation.md.
# --------------------------------------------------------------------------- #

# High-precision "this hint leaks the solution" patterns. Deliberately conservative
# — these fire only on near-certain giveaways (literal pseudocode / transitions), so
# false positives are rare; the LLM judge catches the subtler cases these miss.
_LEAK_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bdp\s*[\[\(]"), "contains a literal dp[...] state expression"),
    (re.compile(r"[A-Za-z_]\w*\s*\[[^\]]+\]\s*="), "writes an indexed-array assignment (pseudocode)"),
    (re.compile(r"=\s*(?:min|max)\s*\("), "states a min/max transition formula"),
    (re.compile(r"[A-Za-z_]\w*\s*\[[^\]]+\]\s*[+\-*]\s*[A-Za-z_]\w*\s*\["), "spells out an index-arithmetic formula"),
    (re.compile(r"```"), "contains a code fence"),
    (re.compile(r"\bstep\s*\d\b", re.I), "gives an enumerated step-by-step recipe"),
]


def leak_flags(hints: list[str]) -> dict[int, str]:
    """Cheap regex pre-filter: which hints obviously give away the solution?

    Returns a mapping of 1-based tier index -> reason for every hint that trips a
    high-precision leak pattern (literal ``dp[...]``, an indexed assignment, a
    ``min(...)``/``max(...)`` transition, index arithmetic, a code fence, or an
    enumerated step recipe). Empty dict means nothing obvious leaked; the LLM judge
    still runs to catch the subtler cases this can't see. Free — no LLM call.
    """
    flags: dict[int, str] = {}
    for i, hint in enumerate(hints, 1):
        for pat, reason in _LEAK_PATTERNS:
            if pat.search(hint or ""):
                flags[i] = reason
                break
    return flags


def _hints_as_numbered_list(hints: list[str]) -> str:
    return "\n".join(f"Hint {i}: {h}" for i, h in enumerate(hints, 1))


def _render_judge_prompt(statement: str, solution: str, hints: list[str],
                         max_hints: int) -> str:
    """Inject the problem, reference solution and candidate hints into the judge
    template. Literal token replacement (statements/solutions contain ``{}``)."""
    template = _JUDGE_TEMPLATE_PATH.read_text(encoding="utf-8")
    return (
        template
        .replace("{{MAX_HINTS}}", str(max_hints))
        .replace("{{STATEMENT}}", statement.strip())
        .replace("{{SOLUTION}}", (solution or "(no reference solution available)").strip())
        .replace("{{HINTS}}", _hints_as_numbered_list(hints))
    )


def _judge_schema(n_hints: int) -> dict:
    """Schema for the critic's reply: one verdict per hint + a regenerate list."""
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "verdicts": {
                "type": "array",
                "minItems": 1,
                "maxItems": n_hints,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "tier": {"type": "integer"},
                        "label": {"type": "string", "enum": ["ok", "reveals", "vague"]},
                        "reason": {"type": "string"},
                    },
                    "required": ["tier", "label"],
                },
            },
            "regenerate": {"type": "array", "items": {"type": "integer"}},
        },
        "required": ["verdicts", "regenerate"],
    }


def _parse_verdict(content: str, n_hints: int) -> dict:
    """Pull ``{"verdicts": [...], "regenerate": [...]}`` out of the critic reply.

    Defensive against fences / stray prose (reuses :func:`_loads_loose`). Always
    returns a dict with ``verdicts`` (list) and ``regenerate`` (sorted unique
    1-based tiers); ``regenerate`` is reconciled with the labels so a model that
    forgets to fill it, or fills it inconsistently, still yields the right set.
    """
    data = _loads_loose(content)
    verdicts = data.get("verdicts", []) if isinstance(data, dict) else []
    clean: list[dict] = []
    for v in verdicts:
        if not isinstance(v, dict):
            continue
        tier = v.get("tier")
        label = v.get("label")
        if not isinstance(tier, int) or label not in ("ok", "reveals", "vague"):
            continue
        if 1 <= tier <= n_hints:
            clean.append({"tier": tier, "label": label, "reason": str(v.get("reason", "")).strip()})
    # Trust the labels for the regenerate set (union with any explicit list).
    regen = {v["tier"] for v in clean if v["label"] != "ok"}
    explicit = data.get("regenerate", []) if isinstance(data, dict) else []
    for t in explicit:
        if isinstance(t, int) and 1 <= t <= n_hints:
            regen.add(t)
    return {"verdicts": clean, "regenerate": sorted(regen)}


def judge_hints(
    statement: str,
    solution: str,
    hints: list[str],
    *,
    base_url: str = LLM_SERVER_URL,
    model: str = LLM_MODEL,
    api_key: str = LLM_API_KEY,
    temperature: float = 0.0,
    thinking: bool = True,
) -> dict:
    """Grade a hint set against the reference solution with the LLM critic.

    The judge is a grader, so it decodes greedily (``temperature=0.0``) for
    run-to-run determinism: at 0.2 the same borderline leak was caught on one call
    and missed on the next, which is unacceptable for a gate.

    Given the problem ``statement``, its canonical ``solution`` (used only as a
    yardstick for how close a hint comes to the answer), and the candidate
    ``hints``, returns ``{"verdicts": [{tier, label, reason}, ...],
    "regenerate": [tiers]}`` where ``label`` is ``ok`` / ``reveals`` / ``vague``.

    Thinking is ON by default: the judge is not in any interactive hot path (it only
    runs over problems being (re)hardened), and deliberation markedly improves the
    reveals-vs-ok calibration. Same structured-output fallback chain as
    :func:`generate_hints`.

    Raises
    ------
    RuntimeError
        If every attempt to reach the LLM fails.
    """
    if not hints:
        return {"verdicts": [], "regenerate": []}
    client = _client(base_url, api_key)
    messages = [
        {"role": "system", "content": _JUDGE_SYSTEM},
        {"role": "user", "content": _render_judge_prompt(statement, solution, hints, len(hints))},
    ]
    schema = _judge_schema(len(hints))
    response_formats = [
        {"type": "json_schema",
         "json_schema": {"name": "verdict", "schema": schema, "strict": True}},
        {"type": "json_object"},
        None,
    ]
    extra_body = {} if thinking else {"chat_template_kwargs": {"enable_thinking": False}}

    last_err: Exception | None = None
    for rf in response_formats:
        kwargs = dict(model=model, messages=messages, temperature=temperature,
                      extra_body=extra_body)
        if rf is not None:
            kwargs["response_format"] = rf
        try:
            resp = client.chat.completions.create(**kwargs)
            return _parse_verdict(resp.choices[0].message.content or "", len(hints))
        except Exception as e:  # noqa: BLE001
            last_err = e
            if any(k in type(e).__name__ for k in ("Connection", "Timeout")):
                break
            continue

    raise RuntimeError(f"LLM hint judging failed: {last_err}") from last_err


def _feedback_from(flags: dict[int, str], verdicts: list[dict]) -> str:
    """Build the revision guidance handed back to the generator for a retry.

    Merges the heuristic flags and the judge's per-tier verdicts into one short,
    per-hint instruction list, e.g. "Hint 3 reveals too much (states a min/max
    transition formula): rewrite it to hint at the insight without the transition."
    """
    by_tier: dict[int, list[str]] = {}
    for tier, reason in flags.items():
        by_tier.setdefault(tier, []).append(f"reveals too much ({reason})")
    for v in verdicts:
        if v["label"] == "reveals":
            by_tier.setdefault(v["tier"], []).append(
                f"reveals too much{(' (' + v['reason'] + ')') if v.get('reason') else ''}")
        elif v["label"] == "vague":
            by_tier.setdefault(v["tier"], []).append(
                f"is too vague{(' (' + v['reason'] + ')') if v.get('reason') else ''}")
    fix = {
        "reveals": ("rewrite it to point at the insight WITHOUT the mechanics — say what the "
                    "state/array represents and its base or edge cases, but never how one state "
                    "is computed from others, and no formula, code, or step list"),
        "vague": "make it concrete and specific to this problem — name the actual handle, not generic advice",
    }
    lines: list[str] = []
    for tier in sorted(by_tier):
        joined = "; ".join(by_tier[tier])
        kind = "vague" if "vague" in joined and "reveals" not in joined else "reveals"
        lines.append(f"- Hint {tier} {joined}: {fix[kind]}.")
    return "\n".join(lines)


def generate_hints_verified(
    statement: str,
    solution: str,
    *,
    max_hints: int = MAX_HINTS,
    base_url: str = LLM_SERVER_URL,
    model: str = LLM_MODEL,
    api_key: str = LLM_API_KEY,
    gen_temperature: float = 0.6,
    gen_thinking: bool = False,
    use_judge: bool = True,
    tries: int = 3,
) -> tuple[list[str], dict]:
    """Generate hints, then gate them: heuristic pre-filter + LLM judge, with up to
    ``tries`` regeneration rounds fed the critique. Returns ``(hints, record)``.

    Each round: generate (statement only — the solution is deliberately withheld
    from the *generator* to avoid transcription), run :func:`leak_flags`, then (if
    ``use_judge``) :func:`judge_hints` against the reference ``solution``. Any tier
    flagged by either gate is regenerated next round with targeted feedback. The
    first clean set wins; otherwise the least-flagged set across rounds is returned.

    ``record`` captures the audit trail: ``accepted`` (bool — a fully clean set was
    reached), ``tries_used``, ``flagged`` (final unresolved tiers), and ``attempts``
    (per-round hints + heuristic flags + judge verdicts), suitable for a report.
    """
    record: dict = {"accepted": False, "tries_used": 0, "flagged": [], "attempts": []}
    best_hints: list[str] = []
    best_flagged: list[int] = []
    best_score = 10 ** 9
    feedback: str | None = None

    for attempt in range(1, max(1, tries) + 1):
        record["tries_used"] = attempt
        hints = generate_hints(
            statement, max_hints=max_hints, base_url=base_url, model=model,
            api_key=api_key, temperature=gen_temperature, thinking=gen_thinking,
            feedback=feedback,
        )
        flags = leak_flags(hints)
        verdicts: list[dict] = []
        judge_err: str | None = None
        if use_judge and hints:
            try:
                verdict = judge_hints(statement, solution, hints, base_url=base_url,
                                      model=model, api_key=api_key)
                verdicts = verdict["verdicts"]
            except Exception as e:  # noqa: BLE001 - judge down => fall back to heuristic only
                judge_err = f"{type(e).__name__}: {e}"

        flagged = sorted(set(flags) | {v["tier"] for v in verdicts if v["label"] != "ok"})
        record["attempts"].append({
            "hints": hints, "heuristic": flags, "verdicts": verdicts,
            "flagged": flagged, "judge_error": judge_err,
        })

        if len(flagged) < best_score:
            best_score, best_hints, best_flagged = len(flagged), hints, flagged

        if not flagged:
            record["accepted"] = True
            record["flagged"] = []
            return hints, record

        feedback = _feedback_from(flags, verdicts)

    # Not fully clean: return the least-flagged set found, and report ITS flags
    # (not merely the last attempt's) so the record matches the hints returned.
    record["flagged"] = best_flagged
    return best_hints, record
