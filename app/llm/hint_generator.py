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
from pathlib import Path

# --------------------------------------------------------------------------- #
# LLM server location — EDIT THIS (or set the env vars) to point at your server.
#
# llama.cpp's ``llama-server`` listens on http://localhost:8080 by default and
# serves the OpenAI-compatible API under the ``/v1`` path. Set LLM_SERVER_URL to
# ``http://localhost:<PORT>`` for whatever port your server uses.
# --------------------------------------------------------------------------- #
LLM_SERVER_URL = os.environ.get("LLM_SERVER_URL", "http://localhost:8090")

# Model name to request. llama.cpp serves a single model and largely ignores this,
# but the OpenAI client requires *some* value; override if your server is picky.
LLM_MODEL = os.environ.get("LLM_MODEL", "local-model")

# llama.cpp does not check the key, but the OpenAI client insists on a non-empty
# string. Only override if your endpoint actually enforces auth.
LLM_API_KEY = os.environ.get("LLM_API_KEY", "sk-no-key-required")

# Hard cap on hints, matching the app's problem schema (see specs/problem-schema.md).
MAX_HINTS = 3

_PROMPT_TEMPLATE_PATH = Path(__file__).with_name("hint_prompt.txt")

# Persona / global instruction. The substantive prompt lives in the template file.
_SYSTEM = (
    "You are a careful programming tutor who gives graded hints that guide a "
    "student toward solving a problem themselves, and who never reveals the full "
    "solution. You always reply with exactly the JSON object you are asked for."
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
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": _render_prompt(statement, max_hints)},
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
