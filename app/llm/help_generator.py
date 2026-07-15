"""On-the-fly "Get More Help with AI" hint for a stuck solver.

This is the *interactive* cousin of :mod:`app.llm.hint_generator`. When a user has
read all of a problem's stored hints and is still stuck, the problem page asks this
module for ONE extra, more-concrete hint — generated live from the problem title,
statement and existing hints so it doesn't repeat what they've already seen and
takes a genuine step further.

Like the bulk hint generator it talks to a local, OpenAI-compatible endpoint (the
kind llama.cpp's ``llama-server`` serves at ``http://localhost:<PORT>/v1``) via the
official ``openai`` client. The endpoint, key and model come from
``settings.LLM_HELP_*`` (see :mod:`app.config`), so a cloud OpenAI-compatible
provider works too.

Two entry points:

* :func:`probe_endpoint` — a fast, cheap health check run once at startup to decide
  whether the button is shown enabled (see ``app/main.py`` lifespan).
* :func:`stream_help` — a generator yielding the hint text in chunks as the model
  produces it, so the UI can render it live and show progress.

The wording lives next to this file in ``help_prompt.txt`` so it can be tuned
without touching code.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from ..config import settings

_PROMPT_TEMPLATE_PATH = Path(__file__).with_name("help_prompt.txt")

# Persona / global instruction; the substantive prompt lives in the template file.
_SYSTEM = (
    "You are a patient, insightful programming mentor. You give one focused hint "
    "that nudges a stuck student toward the next step without ever dumping the full "
    "solution. You write in plain prose and reply with the hint text only."
)


def _client(base_url: str, api_key: str, *, timeout: float, max_retries: int = 0):
    """Build an OpenAI client pointed at the endpoint's ``/v1`` path.

    Imported lazily so ``openai`` stays an optional dependency. ``max_retries`` is 0
    by default because both callers want to fail fast rather than stall the UI.
    """
    from openai import OpenAI

    base = base_url.rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    return OpenAI(base_url=base, api_key=api_key, timeout=timeout,
                  max_retries=max_retries)


def probe_endpoint(
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    timeout: float = 2.5,
) -> bool:
    """Return ``True`` if the configured LLM endpoint answers a model listing.

    A cheap ``GET /v1/models`` — the canonical OpenAI-compatible health check, which
    llama.cpp serves without auth. Any failure (server down, ``openai`` not
    installed, auth rejected, timeout) is swallowed and reported as unavailable, so
    the caller can simply disable the feature. Never raises.
    """
    base_url = base_url or settings.LLM_HELP_URL
    api_key = api_key or settings.LLM_HELP_API_KEY
    try:
        client = _client(base_url, api_key, timeout=timeout)
        client.models.list()
        return True
    except Exception:  # noqa: BLE001 - availability probe: any failure => "off"
        return False


def _format_hints(hints: list[str]) -> str:
    hints = [h.strip() for h in (hints or []) if h and h.strip()]
    if not hints:
        return "(This problem has no stored hints, so the student is starting cold.)"
    return "\n".join(f"Hint {i}: {h}" for i, h in enumerate(hints, 1))


def _render_prompt(title: str, statement: str, hints: list[str]) -> str:
    """Inject the problem into the plain-text template.

    Uses literal token replacement rather than ``str.format`` on purpose: problem
    statements routinely contain ``{``/``}`` from code or set notation, which would
    make ``str.format`` raise. Tokens: ``{{TITLE}}``, ``{{STATEMENT}}`` and
    ``{{EXISTING_HINTS}}``.
    """
    template = _PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
    return (
        template
        .replace("{{TITLE}}", (title or "(untitled)").strip())
        .replace("{{STATEMENT}}", (statement or "").strip())
        .replace("{{EXISTING_HINTS}}", _format_hints(hints))
    )


def stream_help(
    title: str,
    statement: str,
    hints: list[str],
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    temperature: float = 0.6,
    max_tokens: int = 400,
    thinking: bool = False,
    timeout: float = 60.0,
) -> Iterator[str]:
    """Stream one extra, more-revealing hint as the model produces it.

    Yields text chunks (``delta.content``) in order; join them for the full hint.
    A synchronous generator, suitable for FastAPI's ``StreamingResponse``.

    Parameters mirror :func:`app.llm.hint_generator.generate_hints`. ``thinking`` is
    off by default: this is an interactive hot path, and deliberation would add tens
    of seconds. The flag is forwarded as ``chat_template_kwargs.enable_thinking``
    (a llama.cpp / Qwen convention); plain OpenAI servers ignore it.

    Raises
    ------
    RuntimeError
        If ``statement`` is empty, or the endpoint cannot be reached / errors before
        producing output.
    """
    if not statement or not statement.strip():
        raise RuntimeError("This problem has no statement to build a hint from.")

    base_url = base_url or settings.LLM_HELP_URL
    api_key = api_key or settings.LLM_HELP_API_KEY
    model = model or settings.LLM_HELP_MODEL

    client = _client(base_url, api_key, timeout=timeout)
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": _render_prompt(title, statement, hints)},
    ]
    # Reasoning models default to "thinking on"; disable it for speed unless asked.
    extra_body = {} if thinking else {"chat_template_kwargs": {"enable_thinking": False}}

    try:
        stream = client.chat.completions.create(
            model=model, messages=messages, temperature=temperature,
            max_tokens=max_tokens, stream=True, extra_body=extra_body,
        )
    except Exception as exc:  # noqa: BLE001 - surface a clean message to the UI
        raise RuntimeError(f"Could not reach the AI endpoint: {exc}") from exc

    for chunk in stream:
        choices = getattr(chunk, "choices", None)
        if not choices:
            continue
        delta = getattr(choices[0], "delta", None)
        piece = getattr(delta, "content", None) if delta is not None else None
        if piece:
            yield piece
