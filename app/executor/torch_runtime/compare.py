"""``torch.allclose``, without torch, over what the sandboxes returned.

Runs in the **trusted parent**, which has no torch. Both sides arrive as JSON:
every tensor is ``{"$tensor": {"shape", "dtype", "data"}}`` (data flat, row
major), written by the in-sandbox harness. The submission's side is untrusted,
so its structure is checked before a single number is compared.

The rule per element is ``torch.allclose``'s, verbatim::

    |actual - expected| <= atol + rtol * |expected|

plus what ``torch.testing.assert_close`` adds and an interviewer would expect:
shapes must be equal (no broadcasting), dtypes must be equal (a float64 answer
to a float32 question is a different answer), and integer/bool tensors compare
exactly. ``NaN`` matches ``NaN`` — the expected side is the canonical's own
output, so a NaN there is what the problem defines — and an infinity matches
only the same infinity.

Returns ``(ok, reason)``. The reason is written for the solver: the first
point of difference, with the worst element's index and both values.
"""
from __future__ import annotations

import math

from .inputs import FLOAT_DTYPES, MAX_RANK, is_tensor_value, numel

#: ``torch.allclose`` uses rtol=1e-5, atol=1e-8. atol=1e-8 is below float32's
#: resolution for anything that rounds to zero — a correct softmax entry of
#: 3e-9 computed two ways can differ by more than that — so the default atol is
#: raised to 1e-6. A problem's ``torch`` block may set either.
DEFAULT_RTOL = 1e-5
DEFAULT_ATOL = 1e-6


def _fmt_shape(shape: list) -> str:
    return "(" + ", ".join(map(str, shape)) + ("," if len(shape) == 1 else "") + ")"


def _unravel(i: int, shape: list[int]) -> tuple[int, ...]:
    out = []
    for d in reversed(shape):
        out.append(i % d if d else 0)
        i = i // d if d else 0
    return tuple(reversed(out))


def _describe(v: object) -> str:
    if is_tensor_value(v):
        t = v["$tensor"]  # type: ignore[index]
        return f"a {t.get('dtype')} tensor of shape {_fmt_shape(t.get('shape', []))}"
    if isinstance(v, bool):
        return "a bool"
    if isinstance(v, (int, float)):
        return "a Python number"
    if isinstance(v, list):
        return f"a list/tuple of {len(v)}"
    if isinstance(v, dict):
        return "a dict"
    if v is None:
        return "None"
    return type(v).__name__


def _valid_tensor(t: object) -> bool:
    """Structure check for an untrusted ``$tensor`` payload."""
    if not isinstance(t, dict):
        return False
    shape, dtype, data = t.get("shape"), t.get("dtype"), t.get("data")
    if not (isinstance(shape, list)
            and all(isinstance(d, int) and not isinstance(d, bool) and d >= 0 for d in shape)):
        return False
    if not isinstance(dtype, str):
        return False
    return isinstance(data, list) and len(data) == numel(shape)


def _num_close(a: object, e: object, rtol: float, atol: float) -> bool:
    if isinstance(e, bool) or isinstance(a, bool):
        return type(a) is type(e) and a == e
    if not isinstance(a, (int, float)) or not isinstance(e, (int, float)):
        return False
    try:
        af, ef = float(a), float(e)
    except OverflowError:
        return False
    if math.isnan(ef):
        return math.isnan(af)
    if math.isinf(ef) or math.isinf(af):
        return af == ef
    return abs(af - ef) <= atol + rtol * abs(ef)


def _tensors(a: dict, e: dict, rtol: float, atol: float, where: str) -> tuple[bool, str | None]:
    at, et = a["$tensor"], e["$tensor"]
    # Cheap checks first: the shape is untrusted and may be any length, so it is
    # compared with the trusted one before anything multiplies it out.
    shape = at.get("shape") if isinstance(at, dict) else None
    if not isinstance(shape, list) or len(shape) > MAX_RANK:
        return False, f"{where}: returned tensor could not be read back"
    if not _valid_tensor(at):
        return False, f"{where}: returned tensor could not be read back"
    if at["shape"] != et["shape"]:
        return False, (f"{where}: shape {_fmt_shape(at['shape'])}, "
                       f"expected {_fmt_shape(et['shape'])}")
    if at["dtype"] != et["dtype"]:
        return False, f"{where}: dtype {at['dtype']}, expected {et['dtype']}"
    exact = et["dtype"] not in FLOAT_DTYPES
    worst_i, worst = -1, -1.0
    for i, (x, y) in enumerate(zip(at["data"], et["data"], strict=True)):
        ok = (x == y and type(x) is type(y)) if exact else _num_close(x, y, rtol, atol)
        if ok:
            continue
        try:
            gap = abs(float(x) - float(y))
            if math.isnan(gap):
                gap = math.inf
        except (TypeError, ValueError, OverflowError):
            gap = math.inf
        if gap > worst:
            worst_i, worst = i, gap
    if worst_i < 0:
        return True, None
    bad = sum(1 for x, y in zip(at["data"], et["data"], strict=True)
              if not ((x == y and type(x) is type(y)) if exact
                      else _num_close(x, y, rtol, atol)))
    idx = _unravel(worst_i, et["shape"])
    pos = f"[{', '.join(map(str, idx))}]" if idx else ""
    got, want = at["data"][worst_i], et["data"][worst_i]
    tol = "" if exact else f" (rtol={rtol:g}, atol={atol:g})"
    return False, (f"{where}: {bad} of {len(et['data'])} values differ{tol}; worst at "
                   f"{pos or 'the scalar'}: got {got!r}, expected {want!r}")


def compare(actual: object, expected: object, *, rtol: float = DEFAULT_RTOL,
            atol: float = DEFAULT_ATOL, where: str = "output") -> tuple[bool, str | None]:
    """Is ``actual`` allclose to ``expected``, structure and all?"""
    try:
        return _compare(actual, expected, rtol, atol, where)
    except RecursionError:  # a hostile, absurdly nested return value
        return False, f"{where}: the returned value is nested too deeply to compare"


def _compare(a: object, e: object, rtol: float, atol: float,
             where: str) -> tuple[bool, str | None]:
    if is_tensor_value(e):
        if not is_tensor_value(a):
            return False, f"{where}: got {_describe(a)}, expected {_describe(e)}"
        return _tensors(a, e, rtol, atol, where)  # type: ignore[arg-type]
    if is_tensor_value(a):
        return False, f"{where}: got {_describe(a)}, expected {_describe(e)}"
    if isinstance(e, list):
        if not isinstance(a, list) or len(a) != len(e):
            return False, f"{where}: got {_describe(a)}, expected {_describe(e)}"
        for i, (x, y) in enumerate(zip(a, e, strict=True)):
            ok, why = _compare(x, y, rtol, atol, f"{where}[{i}]")
            if not ok:
                return ok, why
        return True, None
    if isinstance(e, dict):
        if not isinstance(a, dict) or a.keys() != e.keys():
            return False, f"{where}: got {_describe(a)}, expected a dict with keys {sorted(e)}"
        for k in e:
            ok, why = _compare(a[k], e[k], rtol, atol, f"{where}[{k!r}]")
            if not ok:
                return ok, why
        return True, None
    if isinstance(e, (int, float)) and not isinstance(e, bool):
        if isinstance(a, (int, float)) and not isinstance(a, bool):
            if _num_close(a, e, rtol, atol):
                return True, None
            return False, f"{where}: got {a!r}, expected {e!r}"
        return False, f"{where}: got {_describe(a)}, expected {_describe(e)}"
    if a == e and type(a) is type(e):
        return True, None
    return False, f"{where}: got {a!r}, expected {e!r}"
