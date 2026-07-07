"""Canonical *execution-coverage* tokens (the semantic half of the model).

Where features.py describes an input's static shape, this module runs the
**trusted canonical** on an input and records which behaviors the run exercised —
a solution-independent notion of "novel behavior" that no wrong solution defines.
An input earns selection if the canonical, on it, enters a (line, local-state,
output) regime the current suite never entered.

This is what closes the gap the adversary/mutant model left open. Example
(basic-calculator, sign-stack canonical): every stored case already kills every
canonical-mutant, and the input ``1-(2-(3-4))`` kills none — so mutation-guided
selection discarded it, even though it crashes a whole class of "evaluate the
inner group and splice the result back as a string" wrong parsers. But on that
input the canonical is the *only* case that reaches a ``)`` while its running
``result`` is negative **and** the paren stack is ≥2 deep — a joint value regime
no stored case covers. The joint per-line ``val:`` signature below captures
exactly that, so coverage keeps the input on its own merits.

Three token families, all prefixed and all derived only from the canonical:
  * ``line:<lineno>``            — statement/branch coverage of the canonical.
  * ``val:<lineno>:<sig>``       — a coarse *joint* signature of the numeric &
                                   container locals live at that line (int sign,
                                   list/str length bucket). The joint is the
                                   point: it separates value regimes single-var
                                   buckets miss.
  * ``out:<bucket>``             — the class of the returned value.

Everything is bucketed coarsely so the token universe stays finite and a handful
of cases can cover it. Tracing is bounded (event cap + size skip) so it never
dominates the offline authoring run; the canonical is trusted (same footing as
the mutation grader already exec'ing it in-process).
"""
from __future__ import annotations

import sys
from typing import Any, Callable

from .features import _sign, _size_bucket

_CANON_FILE = "<canon-trace>"          # filename the canonical is compiled under
_MAX_EVENTS = 40_000                    # per-input trace-event ceiling
_MAX_VAL_TOKENS = 600                   # per-input cap on distinct val: tokens
_TRACE_SIZE_LIMIT = 4_000               # skip tracing inputs whose JSON is bigger


def _local_bucket(v: Any) -> str | None:
    """Coarse bucket for one local, or None to ignore it in the signature."""
    if isinstance(v, bool):
        return f"b{int(v)}"
    if isinstance(v, int):
        return _sign(v)
    if isinstance(v, (list, str, tuple, dict, set, bytes)):
        try:
            return _size_bucket(len(v))
        except TypeError:
            return None
    return None


def output_tokens(value: Any) -> set[str]:
    """The class of a returned value (the ``out:`` universe)."""
    if value is None:
        return {"out:none"}
    if isinstance(value, bool):
        return {f"out:bool:{int(value)}"}
    if isinstance(value, int):
        from .features import _mag
        return {f"out:int:{_sign(value)}:{_mag(value)}"}
    if isinstance(value, float):
        return {f"out:float:{_sign(int(value)) if value == value else 'nan'}"}
    if isinstance(value, str):
        return {f"out:str:{_size_bucket(len(value))}"}
    if isinstance(value, (list, tuple)):
        toks = {f"out:list:{_size_bucket(len(value))}"}
        if not value:
            toks.add("out:list:empty")
        elif all(isinstance(x, int) and not isinstance(x, bool) for x in value):
            toks.add(f"out:list:sum{_sign(sum(value))}")
        return toks
    if isinstance(value, dict):
        return {f"out:dict:{_size_bucket(len(value))}"}
    return {"out:other"}


class CanonicalTracer:
    """Compile a canonical once; emit coverage tokens for each input.

    ``decoders`` maps rich-typed param names to their array->object decoder and
    ``encoder`` encodes a rich-typed return — the same harness codecs the judge
    uses — so tracing invokes the canonical exactly as the real run does.
    """

    def __init__(self, source: str, function_name: str,
                 inject: dict | None = None,
                 decoders: dict | None = None, encoder=None) -> None:
        g: dict = dict(inject or {})
        exec(compile(source, _CANON_FILE, "exec"), g)  # noqa: S102 - trusted canonical
        self.func: Callable = g[function_name]
        self.decoders = decoders or {}
        self.encoder = encoder

    def _invoke(self, inp: dict):
        if self.decoders:
            args = dict(inp)
            for name, dec in self.decoders.items():
                if name in args:
                    args[name] = dec(args[name])
        else:
            args = inp
        val = self.func(**args)
        return self.encoder(val) if self.encoder is not None else val

    def tokens(self, inp: dict) -> set[str]:
        """Coverage tokens for running the canonical on ``inp`` (best-effort).

        Never raises: a canonical that errors on the input still yields the tokens
        seen up to the failure plus ``out:error``. Oversized inputs skip the
        (expensive) line/val trace and contribute only their output class."""
        import json
        toks: set[str] = set()
        big = len(json.dumps(inp, default=str)) > _TRACE_SIZE_LIMIT

        events = [0]
        val_count = [0]

        def _trace(frame, event, arg):
            if frame.f_code.co_filename != _CANON_FILE:
                return None
            return _line

        def _line(frame, event, arg):
            if event != "line":
                return _line
            events[0] += 1
            if events[0] > _MAX_EVENTS:
                toks.add("line:truncated")
                return None
            lineno = frame.f_lineno
            toks.add(f"line:{lineno}")
            if val_count[0] < _MAX_VAL_TOKENS:
                sig_items = []
                for name, v in frame.f_locals.items():
                    b = _local_bucket(v)
                    if b is not None:
                        sig_items.append(f"{name}={b}")
                if sig_items:
                    tok = f"val:{lineno}:{','.join(sorted(sig_items))}"
                    if tok not in toks:
                        val_count[0] += 1
                        toks.add(tok)
            return _line

        prev = sys.gettrace()
        try:
            if not big:
                sys.settrace(_trace)
            ret = self._invoke(inp)
            toks |= output_tokens(ret)
        except Exception:  # noqa: BLE001 - a crash is still coverage information
            toks.add("out:error")
        finally:
            if not big:
                sys.settrace(prev)
        return toks
