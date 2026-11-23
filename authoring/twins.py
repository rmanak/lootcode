"""numpy ⇄ PyTorch problem twins: the shared-test machinery.

A *twin* is a deliberate near-duplicate of a numpy ML problem on the PyTorch
runtime, so the same exercise can be practised in both frameworks. The two are
kept **as close as possible**: the same function name, parameter names, shapes,
constraints, statement and return structure (tensors in place of lists), the
same input validator, and **one body of tests** that flows both ways:

* numpy → twin (:func:`port_cases`): every stored numpy case becomes a twin case
  with ``expected: null`` (on the torch runtime the canonical is the oracle);
* one generator, ``<numpy>/tests/generator.json``, drives both sides: the twin
  copies it into its ``torch`` block and draws fresh tests from it on every run,
  and :func:`draw_inputs` + ``scripts/sync_twin_tests.py bake`` turn draws into
  stored hidden numpy cases (expected values from the numpy canonical).

This module is pure (no I/O beyond reading files, no torch, no sandbox) so the
tests can pin it. The CLI is ``scripts/sync_twin_tests.py``; the guide is
``docs/pytorch-twins.md``. Like the rest of ``authoring/``, nothing in ``app/``
imports it.
"""
from __future__ import annotations

import json
import math
import re
import struct
from collections.abc import Mapping
from pathlib import Path

from app.executor.torch_runtime.inputs import (
    TENSOR_LIST_TYPE,
    TENSOR_TYPES,
    generated_inputs,
    is_tensor_value,
    materialize_input,
    to_plain,
)

TWIN_SUFFIX = "-pytorch"
GENERATOR_FILE = Path("tests") / "generator.json"

#: Autograd entry points. A twin of a hand-written-gradient problem forbids
#: them (``torch.forbid``), because the numpy original is about deriving the
#: gradient yourself. See docs/pytorch-twins.md.
AUTOGRAD = [
    "torch.Tensor.backward",
    "torch.autograd.grad",
    "torch.autograd.backward",
    "torch.autograd.functional.jacobian",
    "torch.autograd.functional.vjp",
    "torch.autograd.functional.jvp",
    "torch.autograd.functional.hessian",
    "torch.autograd.functional.vhp",
    "torch.autograd.functional.hvp",
    "torch.func.grad",
    "torch.func.grad_and_value",
    "torch.func.vjp",
    "torch.func.jvp",
    "torch.func.jacrev",
    "torch.func.jacfwd",
    "torch.func.hessian",
    "torch.func.linearize",
    "torch.autograd.forward_ad.make_dual",
    "torch.autograd.forward_ad.unpack_dual",
]

_ARRAY = re.compile(r"(float|int|bool)((?:\[\])*)")


def twin_slug(numpy_slug: str) -> str:
    return numpy_slug + TWIN_SUFFIX


def numpy_slug_of(twin_meta: Mapping) -> str | None:
    """The numpy sibling a twin's meta.json names (``torch.twin``)."""
    return ((twin_meta.get("torch") or {}).get("twin")
            if twin_meta.get("runtime") == "torch" else None)


# --- types -------------------------------------------------------------------
def _split(t: str) -> tuple[str, int] | None:
    """``"float[][]"`` → ``("float", 2)``; ``None`` for a non-numeric type."""
    m = _ARRAY.fullmatch(t or "")
    return (m.group(1), len(m.group(2)) // 2) if m else None


def twin_param_type(numpy_type: str) -> str:
    """Default twin type for a numpy param: a numeric array is a ``Tensor``;
    scalars (``temperature: float``, ``numHeads: int``) and everything else
    stay plain JSON, exactly as on the numpy side."""
    s = _split(numpy_type)
    return "Tensor" if s and s[1] >= 1 else numpy_type


def allowed_twin_types(numpy_type: str) -> tuple[str, ...]:
    """Every type a twin may give a numpy param: its own, the default, and for
    a list of arrays (``float[][]`` whose rows may differ in length: one
    gradient per parameter, one log-prob list per completion) ``Tensor[]``."""
    s = _split(numpy_type)
    if numpy_type == "any[]":  # an array deeper than the schema names (a 4-D conv weight)
        return (numpy_type, "Tensor")
    ragged = (TENSOR_LIST_TYPE,) if s and s[1] >= 2 else ()
    return (numpy_type, twin_param_type(numpy_type), *ragged)


def twin_return_type(numpy_type: str) -> str:
    """A numeric return (scalar or array) comes back as a tensor (a 0-dim one
    for a scalar); a structured return (``any[]``) holds tensors inside."""
    return "Tensor" if _split(numpy_type) else numpy_type


def _int_dtype(base: str) -> str | None:
    return {"int": "int64", "bool": "bool"}.get(base)


def pinned_dtype(spec: object) -> str | None:
    """The dtype a generator spec pins (``$random``, or a ``$list``'s item)."""
    if not isinstance(spec, Mapping):
        return None
    if isinstance(spec.get("$list"), Mapping):
        spec = spec["$list"].get("item")
        if not isinstance(spec, Mapping):
            return None
    rnd = spec.get("$random")
    return rnd.get("dtype") if isinstance(rnd, Mapping) else None


def literal_dtypes(numpy_params: list, twin_params: list,
                   generator: Mapping | None) -> dict[str, str]:
    """The dtype a *literal* value of each Tensor param must carry on the twin.

    Floats default to float32 and need no wrapper, unless the generator pins
    another float dtype for that param (an iterative problem run in float64).
    Integer and boolean arrays need an explicit ``int64`` / ``bool``.
    """
    np_types = {p["name"]: p.get("type", "") for p in numpy_params}
    gen = (generator or {}).get("inputs") or {}
    out: dict[str, str] = {}
    for p in twin_params:
        if p.get("type") not in TENSOR_TYPES:
            continue
        name = p["name"]
        pinned = pinned_dtype(gen.get(name))
        s = _split(np_types.get(name, ""))
        if pinned:
            out[name] = pinned
        elif s and _int_dtype(s[0]):
            out[name] = _int_dtype(s[0])  # type: ignore[assignment]
    return out


def twin_value(value: object, dtype: str | None, *, many: bool = False) -> object:
    """A numpy literal as the twin stores it. Specs pass through unchanged.
    ``many``: a ``Tensor[]`` param, whose literal is a list of tensors (a
    ragged numpy ``float[][]``), so each entry is wrapped on its own."""
    if dtype is None or not isinstance(value, list):
        return value
    if many:
        return [twin_value(v, dtype) for v in value]
    return {"$tensor": {"data": value, "dtype": dtype}}


# --- generator ---------------------------------------------------------------
def load_generator(problem_dir: Path) -> dict | None:
    path = problem_dir / GENERATOR_FILE
    if not path.exists():
        return None
    gen = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(gen, dict) or not isinstance(gen.get("inputs"), dict):
        raise ValueError(f"{path}: a generator is {{\"dims\": {{...}}, \"inputs\": {{...}}}}")
    return {"dims": gen.get("dims") or {}, "inputs": gen["inputs"]}


def draw_inputs(generator: Mapping, params: list, *, seed: int, count: int) -> list[dict]:
    """``count`` concrete inputs from a generator, as plain JSON (tensors as
    nested lists), floats rounded to what the twin actually sees (float32,
    unless the spec pins float64). The same draw is then the same test on
    both sides, bit for bit."""
    out = []
    for inp in generated_inputs(dict(generator), params, seed=seed, count=count):
        plain = to_plain(inp)
        if not isinstance(plain, dict):
            raise TypeError("a generated input is a mapping of parameters")
        out.append(round_like_torch(plain, generator, params))
    return out


# --- float32 -----------------------------------------------------------------
def f32(x: float) -> float:
    """``x`` rounded to the nearest float32, back as a Python float (exact)."""
    if not math.isfinite(x):
        return x
    try:
        return struct.unpack("f", struct.pack("f", x))[0]
    except OverflowError:
        return math.copysign(math.inf, x)


def _round(v: object) -> object:
    if isinstance(v, (bool, int)):
        return v
    if isinstance(v, float):
        return f32(v)
    if isinstance(v, list):
        return [_round(x) for x in v]
    return v


def round_like_torch(inp: Mapping, generator: Mapping | None, params: list) -> dict:
    """Round each float the twin would hold as float32 (every ``Tensor`` param,
    and every float array the numpy side reads, unless the generator pins a
    wider dtype). Scalars that stay Python floats on the twin are untouched."""
    gen = (generator or {}).get("inputs") or {}
    out = dict(inp)
    for p in params:
        name, typ = p["name"], p.get("type", "")
        if name not in out:
            continue
        pinned = pinned_dtype(gen.get(name))
        s = _split(typ)
        array = typ in TENSOR_TYPES or (s is not None and s[1] >= 1)
        if array and pinned not in ("float64",):
            out[name] = _round(out[name])
    return out


def concrete_twin_input(case_input: Mapping, twin_params: list, name: str) -> dict:
    """A twin test's input with specs drawn, as plain JSON."""
    return to_plain(materialize_input(case_input, twin_params, seed_base=name))  # type: ignore[return-value]


# --- port: numpy cases -> twin cases ------------------------------------------
#: Twin-only stored tests (a dtype or torch-specific trap with no numpy
#: counterpart) are named with this prefix; :func:`port_cases` keeps them.
TWIN_ONLY_PREFIX = "torch-"


def port_cases(numpy_cases: list, numpy_params: list, twin_params: list,
               generator: Mapping | None, existing_twin_cases: list) -> list:
    """The twin's cases: every numpy case in order (same name, weight, hidden
    flag; ``expected: null``), then the twin's own ``torch-*`` cases."""
    dtypes = literal_dtypes(numpy_params, twin_params, generator)
    many = {p["name"] for p in twin_params if p.get("type") == TENSOR_LIST_TYPE}
    out = []
    for c in numpy_cases:
        inp = {k: twin_value(v, dtypes.get(k), many=k in many) for k, v in c["input"].items()}
        out.append({"name": c["name"], "input": inp, "expected": None,
                    "weight": c.get("weight", 1), "hidden": c.get("hidden", False)})
    out += [c for c in existing_twin_cases if c["name"].startswith(TWIN_ONLY_PREFIX)]
    return out


# --- comparing a twin's answer with the numpy one ------------------------------
def numbers(v: object) -> list[float]:
    """Every number in a value, in order (a ``$tensor`` literal's data too,
    with or without a ``shape``)."""
    if isinstance(v, dict) and isinstance(v.get("$tensor"), dict):
        v = v["$tensor"].get("data")
    if isinstance(v, bool):
        return [float(v)]
    if isinstance(v, (int, float)):
        return [float(v)]
    if isinstance(v, list):
        return [x for e in v for x in numbers(e)]
    if isinstance(v, dict):
        return [x for k in sorted(v) for x in numbers(v[k])]
    return []


def _shape(v: object) -> object:
    if isinstance(v, list):
        return [_shape(x) for x in v]
    if isinstance(v, dict):
        return {k: _shape(v[k]) for k in sorted(v)}
    return "#" if isinstance(v, (int, float)) and not isinstance(v, bool) else type(v).__name__


def disagreement(torch_out: object, numpy_out: object, rtol: float,
                 atol: float) -> tuple[float, str]:
    """How far the twin's answer is from the numpy one, in units of the twin's
    tolerance: ``max |t - n| / (atol + rtol·|n|)``. Below 1 the twin would
    accept the numpy answer; the cross-check wants it far below (default 0.5),
    so a correct float32 submission with a different op order is safe too.
    ``inf`` with a reason when the structures differ."""
    t = to_plain(torch_out) if is_tensor_value(torch_out) else torch_out
    t = _deep_plain(t)
    if _shape(t) != _shape(numpy_out):
        return math.inf, "the two answers have different structure"
    worst, where = 0.0, ""
    for i, (a, e) in enumerate(zip(numbers(t), numbers(numpy_out), strict=True)):
        if math.isnan(a) or math.isnan(e) or math.isinf(a) or math.isinf(e):
            if not (a == e or (math.isnan(a) and math.isnan(e))):
                return math.inf, f"element {i}: {a!r} vs {e!r}"
            continue
        score = abs(a - e) / (atol + rtol * abs(e))
        if score > worst:
            worst, where = score, f"element {i}: torch {a!r} vs numpy {e!r}"
    return worst, where


def _deep_plain(v: object) -> object:
    if is_tensor_value(v):
        return to_plain(v)
    if isinstance(v, list):
        return [_deep_plain(x) for x in v]
    if isinstance(v, dict):
        return {k: _deep_plain(x) for k, x in v.items()}
    return v


# --- stratifying draws by their *answers* --------------------------------------
def _features(inp: Mapping, out: object) -> list[float]:
    xs = numbers(out)
    n = len(xs) or 1
    mean = sum(xs) / n if xs else 0.0
    var = sum((x - mean) ** 2 for x in xs) / n if xs else 0.0
    feats = [math.log1p(len(xs)), mean, math.sqrt(var),
             min(xs, default=0.0), max(xs, default=0.0),
             sum(1 for x in xs if x == 0) / n, sum(1 for x in xs if x < 0) / n]
    feats += [math.log1p(len(numbers(v))) for _, v in sorted(inp.items())]
    return [f if math.isfinite(f) else 0.0 for f in feats]


def stratify(draws: list[tuple[Mapping, object]], k: int) -> list[int]:
    """Pick ``k`` draws whose *answers* (and sizes) differ the most, in pick
    order: greedy farthest-first over standardized output features. A uniform draw tends to
    land in one regime; this keeps the odd ones (a saturated softmax, an
    all-masked row, a degenerate size) instead of k look-alikes."""
    k = min(k, len(draws))
    if k <= 1 or len(draws) <= 1:
        return list(range(k))
    feats = [_features(i, o) for i, o in draws]
    dim = len(feats[0])
    feats = [f + [0.0] * (dim - len(f)) for f in feats]
    cols = list(zip(*feats, strict=True))
    norm = []
    for c in cols:
        m = sum(c) / len(c)
        sd = math.sqrt(sum((x - m) ** 2 for x in c) / len(c)) or 1.0
        norm.append([(x - m) / sd for x in c])
    pts = list(zip(*norm, strict=True))

    def dist(a: tuple, b: tuple) -> float:
        return sum((x - y) ** 2 for x, y in zip(a, b, strict=True))

    origin = tuple(0.0 for _ in range(dim))
    chosen = [max(range(len(pts)), key=lambda i: dist(pts[i], origin))]
    best = [dist(p, pts[chosen[0]]) for p in pts]
    best[chosen[0]] = -1.0
    while len(chosen) < k:
        nxt = max(range(len(pts)), key=lambda i: best[i])
        chosen.append(nxt)
        best = [-1.0 if j in (nxt,) or b < 0 else min(b, dist(p, pts[nxt]))
                for j, (b, p) in enumerate(zip(best, pts, strict=True))]
    return chosen


# --- the statement's framework paragraph ----------------------------------------
_NUMPY_PARAGRAPHS = ("You may use **numpy**",
                     "You may use the Python standard library and **numpy**",
                     "Answers are accepted when")
#: The paragraphs :func:`torch_paragraph` writes, so a twin's can be refreshed.
_TWIN_PARAGRAPHS = ("Write it in **PyTorch**", "Your answer is checked against the reference")
_ATEN = "torch.ops.aten."


def torch_paragraph(np_params: list, twin_params: list, return_type: str,
                    torch_cfg: Mapping, *, np_return: str = "",
                    out_dtype: str | None = None) -> str:
    """The twin's replacement for the numpy statement's "You may use numpy…"
    and "Answers are accepted…" paragraphs: what arrives as a tensor, what
    comes back, what is off-limits, and how the answer is judged.

    ``np_return`` (the numpy return type) tells a matrix from a single number;
    ``out_dtype`` names the answer's dtype when the inputs do not (integer
    positions in, float64 encodings out)."""
    dtypes = literal_dtypes(np_params, twin_params, torch_cfg)
    groups: dict[str, list[str]] = {}
    for p in twin_params:
        if p.get("type") == "Tensor":
            groups.setdefault(dtypes.get(p["name"], "float32"), []).append(f"`{p['name']}`")

    def names(xs: list[str]) -> str:
        return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]

    arrive = []
    for i, (dtype, xs) in enumerate(groups.items()):
        verb = (" arrives as " if len(xs) == 1 else " arrive as ") if i == 0 else " as "
        arrive.append(names(xs) + verb + ("a " if len(xs) == 1 and dtype[0] != "i" else
                                          "an " if len(xs) == 1 else "")
                      + f"{dtype} tensor{'' if len(xs) == 1 else 's'}")
    lists: dict[str, list[str]] = {}
    for p in twin_params:
        if p.get("type") == TENSOR_LIST_TYPE:
            lists.setdefault(dtypes.get(p["name"], "float32"), []).append(f"`{p['name']}`")
    for dtype, xs in lists.items():
        verb = (" arrives as " if len(xs) == 1 else " arrive as ") if not arrive else " as "
        arrive.append(names(xs) + verb + ("a list" if len(xs) == 1 else "lists")
                      + f" of {dtype} tensors")
        groups.setdefault(dtype, [])
    others = [f"`{p['name']}`" for p in twin_params if p.get("type") not in TENSOR_TYPES]
    if others:
        arrive.append(f"{names(others)} as "
                      + ("a plain Python value" if len(others) == 1 else "plain Python values"))
    text = ["Write it in **PyTorch** (`torch` is already imported). "
            + (names(arrive) if arrive else "The inputs arrive as described") + "."]
    floats = [dt for dt in groups if dt in ("float64", "float32", "float16", "bfloat16")]
    answer = out_dtype or (floats[0] if len(floats) == 1 else None)
    of = f"a {answer} tensor" if answer else "a tensor of the inputs' dtype"
    if return_type == "Tensor":
        if np_return in ("float", "int"):
            text.append(f"Return {of.replace('a ', 'a 0-dim ', 1)}.")
        elif np_return:
            text.append(f"Return {of}.")
        else:
            text.append(f"Return {of} (a 0-dim one for a single number).")
    else:
        kind = f"{answer}; " if answer else "the inputs' float dtype; "
        text.append("Return the structure described above with a tensor in place of "
                    "each list of numbers and a 0-dim tensor in place of each single "
                    f"number ({kind}int64 for integers).")
    text.append("The examples print tensors as nested lists.")
    forbid = list(torch_cfg.get("forbid") or [])
    autograd = [f for f in forbid if f in AUTOGRAD]
    rest = [f for f in forbid if f not in AUTOGRAD]
    if autograd:
        text.append("**Autograd is off-limits**: derive the gradients by hand "
                    "(`.backward()`, `torch.autograd` and `torch.func` raise).")
    shown = [f for f in rest if not f.startswith(_ATEN)]
    if shown:
        text.append("These built-ins would do the exercise for you and raise if called: "
                    + ", ".join(f"`{f}`" for f in shown)
                    + (" (and their `torch.ops.aten` kernels)" if len(shown) < len(rest)
                       else "") + ".")
    para1 = " ".join(text)
    rtol, atol = torch_cfg.get("rtol", 1e-5), torch_cfg.get("atol", 1e-6)
    k = int(torch_cfg.get("random_tests", 0))
    para2 = ("Your answer is checked against the reference implementation with "
             f"`torch.allclose` semantics (`rtol={_num(rtol)}`, `atol={_num(atol)}`), and every "
             "tensor's shape and dtype must match exactly.")
    if k:
        para2 += (f" Besides the stored tests, every run adds {k} hidden tests drawn "
                  "at random within the constraints.")
    return para1 + "\n\n" + para2


def _num(x: float) -> str:
    """``1e-05`` → ``1e-5``: how the statements write a tolerance."""
    return re.sub(r"e([-+])0*(\d)", r"e\1\2", f"{x:g}").replace("e+", "e")


def twin_statement(numpy_md: str, paragraph: str) -> tuple[str, bool]:
    """The numpy statement with its framework paragraphs replaced by
    ``paragraph`` (re-wrapped at ~80 columns). Returns (text, replaced). Given
    a twin's statement instead, it refreshes the paragraphs written earlier."""
    blocks = numpy_md.split("\n\n")
    hits = [i for i, b in enumerate(blocks)
            if b.lstrip().startswith(_NUMPY_PARAGRAPHS + _TWIN_PARAGRAPHS)]
    if not hits:
        return numpy_md, False
    wrapped = "\n\n".join(_wrap(p) for p in paragraph.split("\n\n"))
    blocks = [b for i, b in enumerate(blocks) if i not in hits[1:]]
    blocks[hits[0]] = wrapped
    return "\n\n".join(blocks), True


def _wrap(text: str, width: int = 80) -> str:
    import textwrap  # noqa: PLC0415
    return textwrap.fill(text, width=width, break_long_words=False,
                         break_on_hyphens=False)
