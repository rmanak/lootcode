"""Generate a *population* of candidate solutions per problem with the local LLM.

This is the source material for the population-differential test selector (plan
§11.3): mutation-of-the-canonical only models *local* edits, so it is blind to
from-scratch wrong solutions with distributed bugs (the median ``sol.py`` class).
A diverse population of independent attempts — some correct, some subtly wrong —
covers that space. The wrong ones are realistic stand-ins for the bugs future
users will write; an input on which a candidate *disagrees with the canonical
oracle* becomes a discriminating hidden test.

Trust model: the LLM is **never** an oracle here. The canonical computes every
``expected``; a candidate is only ever a *foil*. A correct candidate simply agrees
with the canonical everywhere and contributes no discriminators; a wrong one points
at an input we should bake. So the model stays entirely out of the trust path — the
same footing as a mutant.

We reuse the existing local-server convention (llama.cpp ``llama-server`` on
:8090, model id ``qwen36``), mirroring ``app/llm/hint_generator.py``.
"""
from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from typing import Optional

LLM_SERVER_URL = os.environ.get("LLM_SERVER_URL", "http://localhost:8090")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen36")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "sk-no-key-required")

_SYSTEM = (
    "You are a competitive programmer. You read a problem and write a correct, "
    "efficient Python 3 solution. Reply with ONE fenced ```python code block "
    "containing a single top-level function with the exact required signature and "
    "nothing else — no explanation, no tests, no example calls."
)


@dataclass(frozen=True)
class CandidateConfig:
    """One knob-setting for a generation attempt.

    ``thinking`` lets the reasoning model deliberate (slower, ~30s, tends toward
    *subtle* bugs when wrong — the high-value kind); off is ~2s and tends toward
    obvious bugs. ``style`` picks the prompt: ``full`` shows the whole statement
    (realistic), ``minimal`` shows only the signature + a one-line gist (induces
    the misunderstandings that expose edge-case bugs). Varying ``temperature``
    spreads the population."""
    label: str
    temperature: float
    thinking: bool = False
    style: str = "full"   # "full" | "minimal"


# Default population: fast (non-thinking, ~3s) attempts across a temperature spread
# plus two signature-only ("minimal") attempts that induce edge-case misreadings.
# Thinking is deliberately excluded here: with the server's --reasoning-budget it is
# ~30-70s *and* frequently spends the whole token budget on reasoning without ever
# emitting code (see the smoke test). Use THINKING_CONFIGS via the collector's
# --think flag for a slower, higher-token-budget top-up on problems that come up
# short on discriminators.
DEFAULT_CONFIGS: list[CandidateConfig] = [
    CandidateConfig("t05", 0.5, thinking=False, style="full"),
    CandidateConfig("t07", 0.7, thinking=False, style="full"),
    CandidateConfig("t09", 0.9, thinking=False, style="full"),
    CandidateConfig("t11", 1.1, thinking=False, style="full"),
    CandidateConfig("min08", 0.8, thinking=False, style="minimal"),
    CandidateConfig("min11", 1.1, thinking=False, style="minimal"),
]

# Opt-in careful attempts (reasoning on). Needs a larger max_tokens so the code
# block survives the reasoning budget — the collector bumps it for thinking configs.
THINKING_CONFIGS: list[CandidateConfig] = [
    CandidateConfig("care06", 0.6, thinking=True, style="full"),
    CandidateConfig("care09", 0.9, thinking=True, style="full"),
]


@dataclass
class Candidate:
    label: str
    temperature: float
    thinking: bool
    style: str
    code: str                 # extracted function source ("" if none found)
    parse_ok: bool            # code compiles AND defines the required function
    error: Optional[str] = None
    elapsed_s: float = 0.0
    completion_tokens: int = 0

    def to_dict(self) -> dict:
        return {
            "label": self.label, "temperature": self.temperature,
            "thinking": self.thinking, "style": self.style, "code": self.code,
            "parse_ok": self.parse_ok, "error": self.error,
            "elapsed_s": round(self.elapsed_s, 2),
            "completion_tokens": self.completion_tokens,
        }


def client(base_url: str = LLM_SERVER_URL, api_key: str = LLM_API_KEY):
    from openai import OpenAI
    base = base_url.rstrip("/")
    if not base.endswith("/v1"):
        base = f"{base}/v1"
    return OpenAI(base_url=base, api_key=api_key)


def _signature_line(prob: dict) -> str:
    params = ", ".join(p["name"] for p in prob.get("params", []))
    ptypes = ", ".join(f"{p['name']}: {p['type']}" for p in prob.get("params", []))
    return (f"def {prob['function_name']}({params}):  "
            f"# params: {ptypes} -> {prob.get('return_type','')}")


def build_messages(prob: dict, style: str) -> list[dict]:
    starter = (prob.get("starter_code") or "").strip()
    if style == "minimal":
        title = prob.get("title", prob["slug"])
        user = (f"Problem: {title}\n\n"
                f"Implement this function:\n\n{starter or _signature_line(prob)}\n\n"
                "Return only the completed function in one ```python block.")
    else:
        stmt = (prob.get("statement_md") or "").strip()
        user = (f"{stmt}\n\n"
                f"Implement the solution as this exact function (Python 3, standard "
                f"library only):\n\n{starter or _signature_line(prob)}\n\n"
                "Return only the completed function in one ```python block.")
    return [{"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user}]


_FENCE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_code(text: str) -> str:
    """Pull the Python from the first code fence; fall back to the raw text.

    Weaker/looser samples sometimes omit the fence or add prose; we take the first
    fenced block if present, else the whole reply, and let the compile-check below
    decide whether it is usable."""
    if not text:
        return ""
    m = _FENCE.search(text)
    body = m.group(1) if m else text
    return body.strip()


def _validates(code: str, function_name: str) -> bool:
    if not code:
        return False
    try:
        compile(code, "<candidate>", "exec")
    except (SyntaxError, ValueError):
        return False
    return bool(re.search(rf"^\s*def\s+{re.escape(function_name)}\s*\(", code, re.M))


def generate_candidate(cli, prob: dict, cfg: CandidateConfig,
                       timeout: float = 120.0, max_tokens: int = 2048) -> Candidate:
    """One generation attempt. Never raises for model/HTTP errors — records them."""
    messages = build_messages(prob, cfg.style)
    extra_body = ({} if cfg.thinking
                  else {"chat_template_kwargs": {"enable_thinking": False}})
    # Thinking spends up to the server's reasoning budget (~2048 tok) *before* the
    # answer, so the code block needs headroom on top or it gets truncated away.
    mt = max_tokens if not cfg.thinking else max(max_tokens, 4096)
    t0 = time.time()
    try:
        resp = cli.chat.completions.create(
            model=LLM_MODEL, messages=messages, temperature=cfg.temperature,
            max_tokens=mt, timeout=timeout, extra_body=extra_body,
        )
        body = resp.choices[0].message.content or ""
        code = extract_code(body)
        return Candidate(
            label=cfg.label, temperature=cfg.temperature, thinking=cfg.thinking,
            style=cfg.style, code=code,
            parse_ok=_validates(code, prob["function_name"]),
            elapsed_s=time.time() - t0,
            completion_tokens=getattr(resp.usage, "completion_tokens", 0) or 0,
        )
    except Exception as e:  # noqa: BLE001 - network/timeout/etc: record, keep going
        return Candidate(
            label=cfg.label, temperature=cfg.temperature, thinking=cfg.thinking,
            style=cfg.style, code="", parse_ok=False,
            error=f"{type(e).__name__}: {e}", elapsed_s=time.time() - t0,
        )
