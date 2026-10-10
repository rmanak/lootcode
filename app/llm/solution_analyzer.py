"""AI "Analysis" of a solver's solution — the LeetCode-style three-pillar report.

The problem page's **✨ Analysis** button sends the editor's code here (via
``POST /api/problems/{slug}/analyze``). The route grades it with the same
``run_submission`` path as Run & Score (without recording a submission), then
asks the optional OpenAI-compatible endpoint — the one "Get More Help with AI"
uses — for a report on three pillars:

* **Approach** — the technique the code uses vs. the best one for the problem,
  the key idea, and one Socratic "consider" question.
* **Efficiency** — current vs. achievable time *and* space complexity, with a
  concrete suggestion for each.
* **Code Style** — readability and structure ratings, with a suggestion.

…plus a one-line encouraging summary keyed to the real verdict.

The answer is **schema-constrained JSON** (``ANALYSIS_SCHEMA``): llama.cpp
compiles a ``json_schema`` into a grammar and guarantees a conforming object, so
the approach labels are drawn from the canonical tag vocabulary
(:mod:`app.tags`), the ratings from a fixed scale, and every prose field has a
length cap. :func:`parse_analysis` still normalises the result, because a server
that ignores ``response_format`` only promises "something JSON-ish".

The model sees the problem's canonical solution as a *private* calibration
reference (so "suggested complexity" is right for custom problems too) and,
for a failing run, the first failing **visible** test. Hidden tests contribute
only counts — never their inputs, expected values or outputs.

The wording lives in ``analysis_prompt.txt`` next to this file.
"""
from __future__ import annotations

import json
import re
import secrets
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from ..config import settings
from ..tags import CANONICAL_TAGS
from . import client as llm_client

_PROMPT_TEMPLATE_PATH = Path(__file__).with_name("analysis_prompt.txt")

_SYSTEM = (
    "You are a senior software engineer and algorithms coach writing the "
    "'Analysis' panel for a student's solution on a coding-practice site. You are "
    "precise about correctness and complexity, specific to the code in front of "
    "you, encouraging in tone, and brief. You never reveal the private reference "
    "solution. You reply with a single JSON object and nothing else."
)

# --- approach labels ---------------------------------------------------------
# The canonical tag slugs, rendered the way a person reads them. The schema's
# enum is these display labels, so what the model emits is what the UI shows.
_LABEL_OVERRIDES = {
    "heap": "Heap (Priority Queue)",
    "breadth-first-search": "Breadth-First Search",
    "depth-first-search": "Depth-First Search",
}


def tag_label(slug: str) -> str:
    """``"two-pointers"`` → ``"Two Pointers"``; a few read better hand-written."""
    if slug in _LABEL_OVERRIDES:
        return _LABEL_OVERRIDES[slug]
    return " ".join(w if w == "and" else w.capitalize() for w in slug.split("-"))


#: Labels that describe a *solution* but are not problem tags, so they live
#: here rather than in the tag vocabulary. Without "Brute Force" the grammar
#: forced a model that had started writing it into the nearest legal label —
#: a nested-loop Two Sum came back as "Breadth-First Search".
ANALYSIS_ONLY_LABELS = ("Brute Force",)

APPROACH_LABELS: list[str] = sorted(
    [tag_label(t) for t in CANONICAL_TAGS] + list(ANALYSIS_ONLY_LABELS))
RATINGS: list[str] = ["Excellent", "Good", "Fair", "Poor"]

# Caps are a backstop for the prompt's word limits (the UI wants a sentence or
# two per field) and bound how much of anything the model can be talked into
# writing — the student's code is untrusted input to this prompt.
_PROSE_MAX = 420
_BIG_O_MAX = 40


def _prose(max_len: int = _PROSE_MAX) -> dict:
    return {"type": "string", "minLength": 1, "maxLength": max_len}


def _labels() -> dict:
    return {"type": "array", "items": {"type": "string", "enum": APPROACH_LABELS},
            "minItems": 1, "maxItems": 3}


def _complexity() -> dict:
    return {"type": "object", "additionalProperties": False,
            "properties": {"current": _prose(_BIG_O_MAX),
                           "suggested": _prose(_BIG_O_MAX),
                           "suggestions": _prose()},
            "required": ["current", "suggested", "suggestions"]}


def _obj(props: dict) -> dict:
    return {"type": "object", "additionalProperties": False,
            "properties": props, "required": list(props)}


# Property order is generation order: the summary comes LAST so the model writes
# it after it has worked through the code, even though the UI shows it first.
ANALYSIS_SCHEMA: dict = _obj({
    "approach": _obj({"current": _labels(), "suggested": _labels(),
                      "key_idea": _prose(), "consider": _prose()}),
    "efficiency": _obj({"time": _complexity(), "space": _complexity()}),
    "code_style": _obj({"readability": {"type": "string", "enum": RATINGS},
                        "structure": {"type": "string", "enum": RATINGS},
                        "suggestions": _prose()}),
    "summary": _prose(),
})

#: The pillars in the order the model writes them — the route reports each as
#: done when the next key appears in the stream (see :func:`pillars_done`).
PILLARS = ("approach", "efficiency", "code_style")
_NEXT_KEY = [re.compile(rf'"{k}"\s*:') for k in ("efficiency", "code_style", "summary")]


def pillars_done(text: str) -> int:
    """How many pillars the partial JSON ``text`` has finished, in order.

    The schema fixes the key order, so the appearance of ``"efficiency":`` means
    the approach object is complete, and so on — enough to tick each pillar off
    in the UI while the rest is still being written.
    """
    n = 0
    while n < len(_NEXT_KEY) and _NEXT_KEY[n].search(text):
        n += 1
    return n


# --- the verdict, as the model sees it --------------------------------------
_STATUS_LABEL = {"wrong": "Wrong Answer", "timeout": "Time Limit Exceeded",
                 "error": "Runtime Error"}
_VALUE_MAX = 600   # chars of one test input / expected / returned value
_ERROR_MAX = 1200  # chars of a traceback


@dataclass(frozen=True)
class Verdict:
    """What grading found, reduced to what the prompt and the UI need."""
    status: str          # "Accepted" | "Wrong Answer" | "Time Limit Exceeded" | ...
    passed: int
    total: int
    detail: str          # prompt text: counts + the first failing visible test

    @property
    def accepted(self) -> bool:
        return self.status == "Accepted"


def _clip(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n] + " …[truncated]"


def _val(v: object) -> str:
    try:
        s = json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        s = repr(v)
    return _clip(s, _VALUE_MAX)


def build_verdict(graded, cases) -> Verdict:
    """Summarise a :class:`~app.executor.GradedRun` for the prompt.

    ``cases`` are the :class:`~app.executor.CaseView`\\ s it was graded against,
    used to show the first failing *visible* test's input and expected value.
    Hidden tests are counted, never shown.
    """
    total, passed = graded.total_count, graded.passed_count
    if total == 0:
        return Verdict("Not tested", 0, 0, "This problem has no tests to run.")
    failures = [r for r in graded.results if not r.passed]
    if not failures:
        return Verdict("Accepted", passed, total,
                       f"Accepted — all {total} tests passed.")

    # Every field of a result is reachable by the student's code (it can rewrite
    # result.json on exit), so a status outside the known set is an error, and
    # nothing reaches the prompt unclipped.
    def kind(r) -> str:
        return r.status if isinstance(r.status, str) and r.status in _STATUS_LABEL \
            else "error"

    status = _STATUS_LABEL[kind(failures[0])]
    kinds: dict[str, int] = {}
    for r in failures:
        k = _STATUS_LABEL[kind(r)].lower()
        kinds[k] = kinds.get(k, 0) + 1
    breakdown = ", ".join(f"{n} {k}" for k, n in kinds.items())
    lines = [f"{status} — {passed} of {total} tests passed "
             f"({len(failures)} failed: {breakdown})."]

    # Visible cases only: should a hidden test ever share a visible one's name,
    # its input and expected value must still never reach the prompt.
    by_name = {c.name: c for c in cases if not c.hidden}
    visible = next((r for r in failures if not r.hidden), None)
    if visible is None:
        lines.append("Every failing test is hidden, so no failing input is "
                     "available; reason about edge cases from the statement.")
    else:
        case = by_name.get(visible.name)
        lines.append("First failing visible test:")
        if case is not None:
            args = ", ".join(f"{k} = {_val(v)}" for k, v in case.input.items())
            lines.append(f"  input: {args}")
            lines.append(f"  expected: {_val(case.expected)}")
        if kind(visible) == "wrong":
            lines.append(f"  returned: {_val(visible.returned)}")
        elif kind(visible) == "timeout":
            lines.append("  result: exceeded the time limit")
        if visible.error and kind(visible) != "wrong":
            lines.append(f"  error: {_clip(str(visible.error).strip(), _ERROR_MAX)}")
    return Verdict(status, passed, total, "\n".join(lines))


# --- the prompt -------------------------------------------------------------
def signature(prob) -> str:
    """The required function or class shape, as one short Python-ish block."""
    def plist(params, *, method: bool = False) -> str:
        args = ["self"] if method else []
        args += [f"{p.get('name')}: {p.get('type')}" if p.get("type")
                 else str(p.get("name")) for p in (params or [])]
        return ", ".join(args)

    if getattr(prob, "kind", "function") == "class":
        lines = [f"class {prob.class_name}:",
                 f"    def __init__({plist(prob.params, method=True)})"]
        for m in prob.class_methods or []:
            ret = (m.get("returns") or {}).get("type") or "None"
            lines.append(f"    def {m.get('name')}"
                         f"({plist(m.get('params'), method=True)}) -> {ret}")
        return "\n".join(lines)
    ret = getattr(prob, "return_type", "") or "None"
    return f"def {prob.function_name}({plist(prob.params)}) -> {ret}"


#: Hard ceiling on a rendered prompt. A real one is well under half of this —
#: statement + reference + a 20,000-char solution + the verdict + the template.
MAX_PROMPT_CHARS = 60_000

_TOKEN = re.compile(
    r"\{\{(TITLE|STATEMENT|SIGNATURE|REFERENCE|VERDICT|APPROACH_LABELS|CODE|FENCE)\}\}")


def render_prompt(*, title: str, statement: str, signature: str, reference: str,
                  code: str, verdict: Verdict) -> str:
    """Fill ``analysis_prompt.txt``.

    One pass over the *template* only, so a token inside a substituted value is
    never expanded. Chained ``.replace`` calls did expand them: ``{{CODE}}`` in
    an exception message (which reaches the verdict) became a full copy of the
    submission each time — a 20 KB request rendered a 3 MB prompt. Not
    ``str.format`` either; statements and code are full of ``{``/``}``.

    The code fence is random per request, so the code cannot close it early.
    """
    values = {
        "TITLE": (title or "(untitled)").strip(),
        "STATEMENT": (statement or "").strip(),
        "SIGNATURE": signature,
        "REFERENCE": (reference or "(not available)").strip(),
        "VERDICT": verdict.detail,
        "APPROACH_LABELS": ", ".join(APPROACH_LABELS),
        "CODE": code.rstrip(),
        "FENCE": f"STUDENT_CODE_{secrets.token_hex(6)}",
    }
    template = _PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")
    return _TOKEN.sub(lambda m: values[m[1]], template)


# --- the call ---------------------------------------------------------------
def stream_analysis(
    prompt: str,
    *,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1500,
    thinking: bool = False,
    timeout: float = 120.0,
) -> Iterator[str]:
    """Stream the model's JSON answer, chunk by chunk.

    Streaming (rather than one blocking call) is what lets the page show real
    progress and tick off each pillar as the model finishes it. Join the chunks
    and hand them to :func:`parse_analysis`.

    ``response_format`` degrades the way :func:`app.llm.client.chat_json` does —
    ``json_schema`` → ``json_object`` → prompt-only — when the endpoint rejects
    the request outright; a connection failure stops immediately. Thinking is
    off by default: someone is waiting, and with the schema enforcing the shape
    the non-thinking answer is good (see ``docs/ai-analysis.md``).
    """
    base_url = base_url or settings.LLM_HELP_URL
    api_key = api_key or settings.LLM_HELP_API_KEY
    model = model or settings.LLM_HELP_MODEL

    client = llm_client.openai_client(base_url, api_key, timeout=timeout,
                                      connect_timeout=llm_client.CONNECT_TIMEOUT_S)
    messages = [{"role": "system", "content": _SYSTEM},
                {"role": "user", "content": prompt}]
    extra_body = {} if thinking else {"chat_template_kwargs": {"enable_thinking": False}}

    stream, last_err = None, None
    for rf in llm_client.response_formats(ANALYSIS_SCHEMA, "solution_analysis"):
        kwargs: dict = {"model": model, "messages": messages, "stream": True,
                        "temperature": temperature, "max_tokens": max_tokens,
                        "extra_body": extra_body}
        if rf is not None:
            kwargs["response_format"] = rf
        try:
            stream = client.chat.completions.create(**kwargs)
            break
        except Exception as exc:  # noqa: BLE001 - try a laxer mode, or give up below
            last_err = exc
            if any(k in type(exc).__name__ for k in ("Connection", "Timeout")):
                break
    if stream is None:
        raise RuntimeError(f"Could not reach the AI endpoint: {last_err}")

    for chunk in stream:
        choices = getattr(chunk, "choices", None)
        if not choices:
            continue
        delta = getattr(choices[0], "delta", None)
        piece = getattr(delta, "content", None) if delta is not None else None
        if piece:
            yield piece


# --- normalising the answer -------------------------------------------------
_LABEL_BY_FOLD = {re.sub(r"[^a-z]", "", lab.lower()): lab for lab in APPROACH_LABELS}
_LABEL_BY_FOLD.update({re.sub(r"[^a-z]", "", t): tag_label(t) for t in CANONICAL_TAGS})
_LABEL_BY_FOLD.update({"heap": "Heap (Priority Queue)",
                       "priorityqueue": "Heap (Priority Queue)",
                       "bfs": "Breadth-First Search", "dfs": "Depth-First Search",
                       "hashmap": "Hash Table", "dp": "Dynamic Programming"})


def _norm_labels(raw: object) -> list[str]:
    out: list[str] = []
    for item in raw if isinstance(raw, list) else []:
        lab = _LABEL_BY_FOLD.get(re.sub(r"[^a-z]", "", str(item).lower()))
        if lab and lab not in out:
            out.append(lab)
    return out[:3]


def _norm_big_o(raw: object) -> str:
    """Strip stray LaTeX from a complexity and make sure it reads ``O(...)``."""
    s = str(raw or "").strip().strip("$").strip()
    s = (s.replace("\\mathcal{O}", "O").replace("\\log", "log")
          .replace("\\sqrt", "sqrt").replace("\\cdot", "·").replace("\\times", "·")
          .replace("\\left", "").replace("\\right", "").replace("\\", ""))
    s = re.sub(r"\s+", " ", s)
    if s and not re.match(r"^[OΘΩ]\s*\(", s):
        s = f"O({s})"
    return s[:_BIG_O_MAX] or "—"


def _text(raw: object) -> str:
    return re.sub(r"\s+", " ", str(raw or "")).strip()[:_PROSE_MAX]


def _rating(raw: object) -> str:
    s = str(raw or "").strip().capitalize()
    return s if s in RATINGS else "Good"


def parse_analysis(text: str) -> dict:
    """Parse and normalise the model's answer into the shape the page renders.

    Tolerant of a server that ignored the schema: labels are folded onto the
    canonical set, ratings onto the scale, complexities into ``O(...)`` form,
    prose whitespace collapsed and capped. Raises ``RuntimeError`` if the answer
    is not JSON or lacks the approach and efficiency pillars entirely.
    """
    try:
        data = llm_client.loads_loose(text or "")
    except (ValueError, IndexError) as exc:
        raise RuntimeError("The AI's answer was not valid JSON.") from exc
    if not isinstance(data, dict) or not isinstance(data.get("approach"), dict) \
            or not isinstance(data.get("efficiency"), dict):
        raise RuntimeError("The AI's answer was missing parts of the analysis.")

    ap = data["approach"]
    eff = data["efficiency"]
    cs = data.get("code_style")
    if not isinstance(cs, dict):
        cs = {}

    def cx(part: object) -> dict:
        part = part if isinstance(part, dict) else {}
        return {"current": _norm_big_o(part.get("current")),
                "suggested": _norm_big_o(part.get("suggested")),
                "suggestions": _text(part.get("suggestions"))}

    current = _norm_labels(ap.get("current"))
    return {
        "summary": _text(data.get("summary")),
        "approach": {
            "current": current,
            "suggested": _norm_labels(ap.get("suggested")) or current,
            "key_idea": _text(ap.get("key_idea")),
            "consider": _text(ap.get("consider")),
        },
        "efficiency": {"time": cx(eff.get("time")), "space": cx(eff.get("space"))},
        "code_style": {
            "readability": _rating(cs.get("readability")),
            "structure": _rating(cs.get("structure")),
            "suggestions": _text(cs.get("suggestions")),
        },
    }
