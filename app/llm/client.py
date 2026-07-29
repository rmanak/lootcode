"""One transport for every LLM call in the project.

Four modules each built their own client — the AI-help endpoint, the hint
generator and the problem generator
generator — with four different timeout policies and four copies of the "append
/v1 if it isn't there" fixup. Two carried their own `_loads_loose`, and three
carried the same `response_format` degradation ladder, comment for comment.

The timeout differences were the only real ones, and they are real: a startup
probe must fail in seconds, an interactive hint must not stall the page, and a
local reasoning model writing a whole problem can legitimately take minutes. So
timeouts stay a per-caller argument; everything else is here.

`openai` and `anthropic` are optional dependencies — imported inside the
functions so a checkout without them still runs everything that isn't AI.
"""
from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

#: Connect timeouts stay short even when the read timeout is long: a *down*
#: server should fail fast, while a live one thinking hard should not be cut off.
CONNECT_TIMEOUT_S = 10.0


def api_base(base_url: str) -> str:
    """The endpoint's OpenAI-compatible `/v1` base, appended if it isn't there."""
    base = base_url.rstrip("/")
    return base if base.endswith("/v1") else f"{base}/v1"


def openai_client(base_url: str, api_key: str, *, timeout: float,
                  connect_timeout: float | None = None, max_retries: int = 0):
    """An OpenAI client pointed at `base_url`'s `/v1` path.

    `timeout` is the read timeout and has no default on purpose — the right
    value differs by an order of magnitude between callers, and picking one
    here is how a 2.5s health probe or a 900s generation would silently get the
    wrong one. Pass `connect_timeout` to keep connection setup short while
    allowing a long read.
    """
    from openai import OpenAI

    if connect_timeout is not None:
        from httpx import Timeout

        timeout_arg: Any = Timeout(timeout, connect=connect_timeout)
    else:
        timeout_arg = timeout
    return OpenAI(base_url=api_base(base_url), api_key=api_key,
                  timeout=timeout_arg, max_retries=max_retries)


def anthropic_client(api_key: str):
    """An Anthropic client for the Claude API backend."""
    import anthropic

    return anthropic.Anthropic(api_key=api_key)


def loads_loose(text: str) -> Any:
    """`json.loads` that tolerates code fences and stray prose from weaker models.

    Strips a leading ```/```json fence, and failing that falls back to the
    outermost `{...}` span — which is what a model that prefixed its answer with
    a sentence leaves behind.
    """
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        i, j = text.find("{"), text.rfind("}")
        if i == -1 or j == -1:
            raise
        return json.loads(text[i:j + 1])


def _response_formats(schema: dict | None, schema_name: str) -> list[dict | None]:
    """Structured-output modes, most-constrained first.

    llama.cpp compiles a `json_schema` into a GBNF grammar and *guarantees* a
    conforming answer; stricter OpenAI-style servers honour it as a contract; a
    minimal endpoint rejects it, and we degrade rather than fail.
    """
    formats: list[dict | None] = []
    if schema is not None:
        formats.append({"type": "json_schema", "json_schema": {
            "name": schema_name, "schema": schema, "strict": True}})
    formats += [{"type": "json_object"}, None]  # laxer, then prompt-only
    return formats


def chat_json(client, *, model: str, messages: list[dict], what: str,
              schema: dict | None = None, schema_name: str = "result",
              parse: Callable[[str], Any] = loads_loose,
              temperature: float | None = None, max_tokens: int | None = None,
              thinking: bool = False, extra_body: dict | None = None) -> Any:
    """A chat completion parsed into JSON, degrading through the structured-output
    modes until one is accepted.

    `parse` runs *inside* the attempt, so a response that arrives but doesn't
    parse also falls through to the next (laxer) mode — a server that ignored
    `json_schema` rather than rejecting it is indistinguishable from one that
    honoured it until you try to read the answer.

    A connection or timeout failure breaks out immediately: a laxer
    `response_format` will not fix an unreachable server, and retrying the ladder
    would triple the wait before the caller hears about it.

    `what` names the operation for the error message ("hint generation").
    """
    # Reasoning models default to thinking on; disabling it keeps the tokens from
    # crowding out the JSON. A llama.cpp / Qwen convention passed through
    # `extra_body`; a plain OpenAI server ignores the unknown key.
    body = dict(extra_body or {})
    if not thinking:
        body.setdefault("chat_template_kwargs", {"enable_thinking": False})

    last_err: Exception | None = None
    for rf in _response_formats(schema, schema_name):
        kwargs: dict[str, Any] = {"model": model, "messages": messages}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if body:
            kwargs["extra_body"] = body
        if rf is not None:
            kwargs["response_format"] = rf
        try:
            resp = client.chat.completions.create(**kwargs)
            return parse(resp.choices[0].message.content or "")
        except Exception as e:  # noqa: BLE001 - try the next mode, or give up below
            last_err = e
            if any(k in type(e).__name__ for k in ("Connection", "Timeout")):
                break
    raise RuntimeError(f"LLM {what} failed: {last_err}") from last_err
