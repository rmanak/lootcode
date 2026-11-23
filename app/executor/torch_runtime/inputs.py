"""Torch-runtime test inputs: literals and random specs, made concrete.

Runs in the **trusted parent** and imports no torch. Every input is turned into
plain numbers *here*, once, and the same numbers are handed to both sandboxes —
the submission's and the canonical's. Generating them with the standard
library's PRNG rather than ``torch.randn`` is what makes that possible: the
parent has no torch, and a draw no longer depends on the torch version, the
CPU's kernels, or which process made it.

A test input maps each parameter to a value. For a parameter whose declared
type is ``Tensor`` that value may be

* a plain number or rectangular nested list — a float32 tensor of that shape;
* ``{"$tensor": {"data": <nested or flat list>, "shape"?: [...], "dtype"?: "int64",
  "requires_grad"?: true}}`` — a literal with an explicit dtype;
* ``{"$random": {"shape": [8, "D"], "dist": "randn", "std": [0.5, 4.0], ...}}`` —
  a random tensor (see :func:`_sample` for the distributions).

A non-tensor parameter takes a plain JSON value, or a ``$random`` spec without
``shape`` for a random scalar (``{"$random": {"dist": "uniform", "low": 0.01,
"high": 1.0}}``) or with one for a random nested list.

Every concrete tensor is normalised to ``{"$tensor": {"shape", "dtype", "data"}}``
with ``data`` flat — the one form the in-sandbox harness decodes.

Seeds are deterministic: a stored test draws from a seed derived from its own
name and the parameter's (stable across runs and machines, so a stored test is
the same test every time), unless the spec pins ``"seed"``. The problem-level
generator (``meta.json`` → ``torch.inputs``) draws fresh tests per submission
from a seed the grader picks; see :func:`generated_inputs`.
"""
from __future__ import annotations

import math
import random
import zlib
from collections.abc import Mapping

TENSOR_TYPE = "Tensor"
TENSOR_LIST_TYPE = "Tensor[]"
TENSOR_TYPES = (TENSOR_TYPE, TENSOR_LIST_TYPE)

#: dtypes a test may ask for. The harness maps each to ``torch.<name>``, and
#: only these, so a spec can never name an arbitrary torch attribute.
DTYPES = ("float32", "float64", "float16", "bfloat16",
          "int64", "int32", "int16", "int8", "uint8", "bool")
FLOAT_DTYPES = ("float32", "float64", "float16", "bfloat16")
DEFAULT_DTYPE = "float32"

#: Ceiling on the numbers in one test's inputs, all parameters together.
#: Tests are meant to be small (docs/torch-runtime.md): a large input is slow
#: to generate, slow to ship to two sandboxes, and catches nothing a small
#: one would not.
MAX_ELEMENTS = 50_000
MAX_RANK = 6
#: Ceilings for a whole run (all stored + random tests together). The parent
#: builds every input before any sandbox starts, so these bound work done in
#: the *web server's* process, not just in the sandbox.
MAX_RUN_ELEMENTS = 500_000
MAX_RUN_TESTS = 200
MAX_RANDOM_TESTS = 50

DISTRIBUTIONS = ("randn", "normal", "rand", "uniform", "randint", "bernoulli", "choice")


class SpecError(ValueError):
    """A test input that cannot be made concrete (a content bug)."""


def derive_seed(*parts: object) -> int:
    """A stable 32-bit seed from any parts (not ``hash()``, which is salted)."""
    return zlib.crc32("\x1f".join(map(str, parts)).encode("utf-8"))


# --- dims ------------------------------------------------------------------
def draw_dims(spec: Mapping | None, rng: random.Random) -> dict[str, int]:
    """Resolve symbolic dims: an int is fixed, ``[lo, hi]`` is drawn inclusive."""
    out: dict[str, int] = {}
    for name, v in (spec or {}).items():
        if isinstance(v, bool):
            raise SpecError(f"dim {name!r} must be an int or [lo, hi]")
        if isinstance(v, int):
            out[name] = v
        elif (isinstance(v, list) and len(v) == 2
              and all(isinstance(x, int) and not isinstance(x, bool) for x in v)
              and v[0] <= v[1]):
            out[name] = rng.randint(v[0], v[1])
        else:
            raise SpecError(f"dim {name!r} must be an int or [lo, hi], got {v!r}")
        if out[name] < 0:
            raise SpecError(f"dim {name!r} is negative")
    return out


def _resolve_shape(shape: object, dims: Mapping[str, int]) -> list[int]:
    if not isinstance(shape, list) or len(shape) > MAX_RANK:
        raise SpecError(f"shape must be a list of at most {MAX_RANK} dims, got {shape!r}")
    out = []
    for d in shape:
        if isinstance(d, str):
            if d not in dims:
                raise SpecError(f"shape uses dim {d!r}, which no 'dims' entry defines")
            out.append(dims[d])
        elif isinstance(d, int) and not isinstance(d, bool) and d >= 0:
            out.append(d)
        else:
            raise SpecError(f"bad shape entry {d!r}")
    # Bound the *structure*, not just the element count: a zero-size dim makes
    # numel 0 while [10_000_000, 0] would still build ten million empty lists
    # for a non-tensor parameter. Treat every dim as at least 1.
    span = 1
    for d in out:
        span *= max(d, 1)
        if span > MAX_ELEMENTS:
            raise SpecError(f"shape {out} is too large (limit {MAX_ELEMENTS} elements)")
    return out


def numel(shape: list[int]) -> int:
    n = 1
    for d in shape:
        n *= d
    return n


# --- sampling --------------------------------------------------------------
def _num_param(spec: Mapping, key: str, default: float, rng: random.Random) -> float:
    """A distribution parameter: a number, or ``[lo, hi]`` drawn uniformly once
    per test — so one spec covers features at many scales, not just one."""
    v = spec.get(key, default)
    if isinstance(v, list) and len(v) == 2 and all(_finite_num(x) for x in v):
        return rng.uniform(float(v[0]), float(v[1]))
    if _finite_num(v):
        return float(v)  # type: ignore[arg-type]
    raise SpecError(f"{key!r} must be a finite number or [lo, hi], got {v!r}")


#: Integers a spec may name (randint bounds, choice values): the int64 range, so
#: a 4000-digit literal cannot reach float conversion or a tensor constructor.
INT64_MIN, INT64_MAX = -(2 ** 63), 2 ** 63 - 1
#: Longest string a ``choice`` may draw (an activation name, a mode).
MAX_STRING = 64


def _finite_num(v: object) -> bool:
    if isinstance(v, bool):
        return False
    if isinstance(v, int):
        return INT64_MIN <= v <= INT64_MAX
    return isinstance(v, float) and math.isfinite(v)


def _int_bound(v: object, dims: Mapping[str, int], key: str) -> int:
    """A ``randint`` bound: an int, or the name of a dim (``"high": "C"`` draws
    labels below the class count this test drew)."""
    if isinstance(v, str):
        if v not in dims:
            raise SpecError(f"randint {key} uses dim {v!r}, which no 'dims' entry defines")
        return dims[v]
    if isinstance(v, int) and not isinstance(v, bool) and INT64_MIN <= v <= INT64_MAX:
        return v
    raise SpecError(f"randint {key} must be an int64 or a dim name, got {v!r}")


def _sample(spec: Mapping, n: int, rng: random.Random,
            dims: Mapping[str, int] | None = None) -> tuple[list, str]:
    """``n`` draws from ``spec["dist"]`` and the dtype they default to.

    * ``randn`` / ``normal`` — Gaussian, ``mean`` (0) and ``std`` (1)
    * ``rand`` / ``uniform`` — uniform on [``low``, ``high``), defaults [0, 1)
    * ``randint`` — integers in [``low``, ``high``), like ``torch.randint``;
      either bound may name a dim
    * ``bernoulli`` — booleans, True with probability ``p`` (0.5)
    * ``choice`` — uniformly from the list ``values``
    """
    dist = spec.get("dist", "randn")
    if dist in ("randn", "normal"):
        mean = _num_param(spec, "mean", 0.0, rng)
        std = _num_param(spec, "std", 1.0, rng)
        return [rng.gauss(mean, std) for _ in range(n)], DEFAULT_DTYPE
    if dist in ("rand", "uniform"):
        lo = _num_param(spec, "low", 0.0, rng)
        hi = _num_param(spec, "high", 1.0, rng)
        if not lo < hi:
            raise SpecError(f"uniform needs low < high, got {lo}, {hi}")
        return [lo + (hi - lo) * rng.random() for _ in range(n)], DEFAULT_DTYPE
    if dist == "randint":
        if "high" not in spec:
            raise SpecError("randint needs integer low < high")
        ilo = _int_bound(spec.get("low", 0), dims or {}, "low")
        ihi = _int_bound(spec["high"], dims or {}, "high")
        if not ilo < ihi:
            raise SpecError("randint needs integer low < high")
        return [rng.randrange(ilo, ihi) for _ in range(n)], "int64"
    if dist == "bernoulli":
        p = _num_param(spec, "p", 0.5, rng)
        return [rng.random() < p for _ in range(n)], "bool"
    if dist == "choice":
        values = choice_values(spec)
        return [rng.choice(values) for _ in range(n)], DEFAULT_DTYPE
    raise SpecError(f"unknown dist {dist!r} (one of {', '.join(DISTRIBUTIONS)})")


def choice_values(spec: Mapping) -> list:
    """A ``choice`` spec's values, checked before anything is drawn: all finite
    numbers, or all short strings. Never a mix, so whether a draw is valid
    cannot depend on the seed."""
    values = spec.get("values")
    if not isinstance(values, list) or not values:
        raise SpecError("choice needs a non-empty 'values' list")
    if all(isinstance(v, str) for v in values):
        if any(len(v) > MAX_STRING for v in values):
            raise SpecError(f"choice strings are at most {MAX_STRING} characters")
        return values
    if all(_finite_num(v) for v in values):
        return values
    raise SpecError("choice values must be all finite numbers or all strings")


#: Keys a ``$random`` spec may carry: every distribution's own parameters plus
#: the shared options. An unknown key (a typo such as ``"min-abs"``) is an
#: error, not silently ignored.
_COMMON_KEYS = frozenset({"dist", "shape", "dtype", "seed", "round", "step", "min_abs",
                          "at_least_one_per_row", "requires_grad"})
_DIST_KEYS = {
    "randn": {"mean", "std"}, "normal": {"mean", "std"},
    "rand": {"low", "high"}, "uniform": {"low", "high"},
    "randint": {"low", "high"}, "bernoulli": {"p"}, "choice": {"values"},
}


def _check_keys(spec: Mapping) -> None:
    dist = spec.get("dist", "randn")
    allowed = _COMMON_KEYS | _DIST_KEYS.get(dist, set())
    unknown = sorted(set(spec) - allowed)
    if unknown:
        raise SpecError(f"$random ({dist}) does not take {unknown}")


# --- literals --------------------------------------------------------------
def _flatten(value: object) -> tuple[list, list[int]]:
    """A rectangular nested list (or a scalar) as ``(flat data, shape)``."""
    if not isinstance(value, list):
        _check_scalar(value)
        return [value], []
    shape: list[int] = []
    probe: object = value
    while isinstance(probe, list):
        shape.append(len(probe))
        if len(shape) > MAX_RANK:
            raise SpecError(f"tensor literal is nested deeper than {MAX_RANK}")
        probe = probe[0] if probe else None
    flat: list = []
    level: list = [value]
    for depth, size in enumerate(shape):
        nxt: list = []
        for item in level:
            if not isinstance(item, list) or len(item) != size:
                raise SpecError("tensor literal is not rectangular")
            nxt.extend(item)
        level = nxt
        if depth == len(shape) - 1:
            flat = level
    for v in flat:
        _check_scalar(v)
    _resolve_shape(shape, {})  # the same structural bound as a declared shape
    return flat, shape


def _check_scalar(v: object) -> None:
    if not isinstance(v, (int, float, bool)):
        raise SpecError(f"tensor entries must be numbers or booleans, got {type(v).__name__}")


def _dtype(name: object) -> str:
    if name not in DTYPES:
        raise SpecError(f"unknown dtype {name!r} (one of {', '.join(DTYPES)})")
    return str(name)


def tensor_value(shape: list[int], dtype: str, data: list, *,
                 requires_grad: bool = False) -> dict:
    t: dict = {"shape": shape, "dtype": dtype, "data": data}
    if requires_grad:
        t["requires_grad"] = True
    return {"$tensor": t}


def is_tensor_value(v: object) -> bool:
    return isinstance(v, dict) and set(v) == {"$tensor"} and isinstance(v["$tensor"], dict)


def _literal_tensor(spec: Mapping) -> dict:
    if "data" not in spec:
        raise SpecError("$tensor needs 'data'")
    flat, inferred = _flatten(spec["data"])
    dtype = _dtype(spec.get("dtype", DEFAULT_DTYPE))
    shape = inferred
    if "shape" in spec:
        shape = _resolve_shape(spec["shape"], {})
        if numel(shape) != len(flat):
            raise SpecError(f"$tensor shape {shape} does not fit {len(flat)} values")
    return tensor_value(shape, dtype, flat, requires_grad=bool(spec.get("requires_grad")))


def _unflatten(flat: list, shape: list[int]) -> object:
    """Flat row-major data back to nested lists (zero-size dims included).
    Recursion is bounded by MAX_RANK, which every shape here has passed."""
    if not shape:
        return flat[0]

    def build(off: int, dims: list[int]) -> list:
        if len(dims) == 1:
            return flat[off:off + dims[0]]
        step = numel(dims[1:])
        return [build(off + i * step, dims[1:]) for i in range(dims[0])]

    return build(0, shape)


# --- one value -------------------------------------------------------------
def materialize_value(value: object, ptype: str, *, seed: int,
                      dims: Mapping[str, int] | None = None) -> object:
    """One parameter's test value, concrete. ``seed`` is used only when the
    value is a ``$random`` spec that does not pin its own."""
    dims = dims or {}
    if ptype == TENSOR_LIST_TYPE:
        if not isinstance(value, list):
            raise SpecError("a Tensor[] parameter takes a list of tensor values")
        return [materialize_value(v, TENSOR_TYPE, seed=derive_seed(seed, i), dims=dims)
                for i, v in enumerate(value)]

    is_tensor = ptype == TENSOR_TYPE
    if isinstance(value, dict) and set(value) == {"$random"}:
        spec = value["$random"]
        if not isinstance(spec, dict):
            raise SpecError("$random must be an object")
        _check_keys(spec)
        rng = random.Random(spec.get("seed", seed))
        shape = _resolve_shape(spec["shape"], dims) if "shape" in spec else None
        n = numel(shape) if shape is not None else 1
        if n > MAX_ELEMENTS:
            raise SpecError(f"random input of shape {shape} exceeds {MAX_ELEMENTS} elements")
        data, default_dtype = _sample(spec, n, rng, dims)
        if any(isinstance(x, str) for x in data):
            # `choice` over strings (an activation name, a mode): one plain
            # value for a non-tensor parameter. No shape — a string counts as
            # one element in the budgets, so an array of them must not exist —
            # and none of the numeric options below apply.
            if is_tensor or shape is not None or set(spec) - {"dist", "values", "seed"}:
                raise SpecError("a choice of strings is one plain value: a non-tensor "
                                "parameter, no shape, no numeric options")
            return data[0]
        dtype = _dtype(spec.get("dtype", default_dtype))
        data = _coerce(data, dtype)
        if "round" in spec:  # e.g. a temperature that reads well in a statement
            digits = spec["round"]
            if not (isinstance(digits, int) and not isinstance(digits, bool)
                    and 0 <= digits <= 15):
                raise SpecError(f"round must be an int from 0 to 15, got {digits!r}")
            data = [round(x, digits) for x in data]
        step = spec.get("step")
        if step is not None:  # e.g. multiples of 1/16, so sums are exact in float32
            data = _quantize(data, step)
        if "min_abs" in spec:  # keep values off zero (e.g. "row norm >= 0.1")
            data = _off_zero(data, spec["min_abs"], step, dtype)
        if spec.get("at_least_one_per_row"):
            _ensure_each_row(data, shape, rng)
        if is_tensor:
            return tensor_value(shape or [], dtype, data,
                                requires_grad=bool(spec.get("requires_grad")))
        return data[0] if shape is None else _unflatten(data, shape)

    if isinstance(value, dict) and set(value) == {"$tensor"}:
        if not isinstance(value["$tensor"], dict):
            raise SpecError("$tensor must be an object")
        lit = _literal_tensor(value["$tensor"])
        return lit if is_tensor else to_plain(lit)

    if is_tensor:
        flat, shape = _flatten(value)
        return tensor_value(shape, DEFAULT_DTYPE, _coerce(flat, DEFAULT_DTYPE))
    return value


def _quantize(data: list, step: object) -> list:
    """Snap every value to a multiple of ``step`` (a positive number). With a
    power-of-two step, products and sums of the inputs stay exact in float32,
    which is how a problem keeps a promise like "no pre-activation is within
    1e-9 of 0 unless it is exactly 0" on random inputs."""
    if not _finite_num(step) or step <= 0:  # type: ignore[operator]
        raise SpecError(f"step must be a positive number, got {step!r}")
    out = []
    for x in data:
        if isinstance(x, bool):
            out.append(x)
            continue
        q = x / step  # type: ignore[operator]
        if not math.isfinite(q) or abs(q) > 2 ** 53:
            raise SpecError(f"step {step!r} is too fine for the value {x!r}")
        out.append(type(x)(round(q) * step))  # type: ignore[operator]
    return out


#: Below this a ``min_abs`` would underflow to 0 in a float32 tensor.
_FLOAT32_TINY = 1.1754943508222875e-38


def _off_zero(data: list, a: object, step: object, dtype: str) -> list:
    """Push every value with ``|x| < a`` out to ``±a`` (keeping its sign).

    Applied after ``step``, with ``a`` raised to a multiple of the step (and to
    an integer for an integer dtype), so neither option can undo the other."""
    if not _finite_num(a) or a < 0:  # type: ignore[operator]
        raise SpecError(f"min_abs must be a non-negative number, got {a!r}")
    if 0 < a < _FLOAT32_TINY:  # type: ignore[operator]
        raise SpecError(f"min_abs {a!r} would underflow to 0 in a float32 tensor")
    bound = float(a)  # type: ignore[arg-type]
    if step is not None:
        bound = math.ceil(bound / step) * step  # type: ignore[operator]
    if dtype not in FLOAT_DTYPES:
        bound = math.ceil(bound)
    out = []
    for x in data:
        if isinstance(x, bool) or abs(x) >= bound:
            out.append(x)
        else:
            out.append(type(x)(math.copysign(bound, x) if x else bound))
    return out


def _ensure_each_row(data: list, shape: list[int] | None, rng: random.Random) -> None:
    """Make every row (the last dim) hold at least one nonzero entry, by setting
    one random entry of an all-zero row to 1 (``True``). For masks whose
    statement promises "every row contains at least one 1"."""
    if not shape:
        raise SpecError("at_least_one_per_row needs a shape")
    width = shape[-1]
    if width == 0:
        return
    for start in range(0, len(data), width):
        if not any(data[start:start + width]):
            data[start + rng.randrange(width)] = type(data[start])(1)


def _coerce(data: list, dtype: str) -> list:
    if dtype in FLOAT_DTYPES:
        return [float(x) for x in data]
    if dtype == "bool":
        return [bool(x) for x in data]
    return [int(x) for x in data]


def _count(value: object) -> int:
    if is_tensor_value(value):
        return len(value["$tensor"]["data"])  # type: ignore[index]
    if isinstance(value, list):
        return sum(_count(v) for v in value)
    return 1


def count_elements(inp: Mapping) -> int:
    """Numbers held by a materialized test input (all parameters)."""
    return sum(_count(v) for v in inp.values())


# --- a whole test ----------------------------------------------------------
def _param_types(params: list) -> list[tuple[str, str]]:
    out = []
    for p in params or []:
        if isinstance(p, str):
            out.append((p, ""))
        else:
            out.append((p.get("name", ""), p.get("type") or ""))
    return out


def materialize_input(inp: Mapping, params: list, *, seed_base: object,
                      dims: Mapping[str, int] | None = None) -> dict:
    """A stored test's input with every spec replaced by concrete values.

    Keys that are not parameters are passed through untouched, so the core
    harness still reports a missing/extra parameter the way it always does.
    """
    if not isinstance(inp, Mapping):
        raise SpecError("a test input must be an object")
    types = dict(_param_types(params))
    out = {}
    for name, value in inp.items():
        out[name] = materialize_value(value, types.get(name, ""),
                                      seed=derive_seed(seed_base, name), dims=dims)
    total = sum(_count(v) for v in out.values())
    if total > MAX_ELEMENTS:
        raise SpecError(f"test inputs hold {total} numbers (limit {MAX_ELEMENTS})")
    return out


def _dim_range(dims: Mapping | None, name: str) -> tuple[int, int]:
    v = (dims or {}).get(name)
    if isinstance(v, list) and len(v) == 2:
        return int(v[0]), int(v[1])
    if isinstance(v, int) and not isinstance(v, bool):
        return v, v
    raise SpecError(f"randint bound names dim {name!r}, which no 'dims' entry defines")


def _check_dim_bounds(dims: Mapping | None, inputs: Mapping) -> None:
    """A ``randint`` bound that names a dim must keep ``low < high`` for EVERY
    value the dim can take — otherwise the generator fails on some seeds only,
    which shows up as an intermittent broken run instead of a content error."""
    for name, value in inputs.items():
        spec = value.get("$random") if isinstance(value, Mapping) else None
        if not isinstance(spec, Mapping) or spec.get("dist") != "randint":
            continue
        lo, hi = spec.get("low", 0), spec.get("high")
        lo_max = _dim_range(dims, lo)[1] if isinstance(lo, str) else lo
        hi_min = _dim_range(dims, hi)[0] if isinstance(hi, str) else hi
        if isinstance(lo_max, int) and isinstance(hi_min, int) and not lo_max < hi_min:
            raise SpecError(f"{name}: randint low < high fails when the dims are at "
                            f"their extremes (low up to {lo_max}, high down to {hi_min})")


def generated_inputs(config: Mapping | None, params: list, *, seed: int,
                     count: int | None = None) -> list[dict]:
    """Fresh random inputs from the problem-level generator.

    ``config`` is the problem's ``torch`` block: ``inputs`` maps every parameter
    to a value spec (usually ``$random``), ``dims`` holds the symbolic sizes
    (``{"N": [1, 32]}``) that are drawn once per test so every parameter of one
    test agrees on them, and ``random_tests`` is how many to draw.
    """
    config = config or {}
    spec = config.get("inputs")
    if not spec:
        return []
    if not isinstance(spec, Mapping):
        raise SpecError("torch.inputs must map parameter names to value specs")
    n = int(config.get("random_tests", 0) if count is None else count)
    if count is None and not 0 <= n <= MAX_RANDOM_TESTS:
        raise SpecError(f"random_tests must be between 0 and {MAX_RANDOM_TESTS}, got {n}")
    _check_dim_bounds(config.get("dims"), spec)
    names = [name for name, _ in _param_types(params)]
    missing = [p for p in names if p not in spec]
    if missing:
        raise SpecError(f"torch.inputs has no spec for parameter(s) {missing}")
    out = []
    for i in range(n):
        dims = draw_dims(config.get("dims"), random.Random(derive_seed(seed, i, "$dims")))
        out.append(materialize_input({p: spec[p] for p in names}, params,
                                     seed_base=derive_seed(seed, i), dims=dims))
    return out


# --- plain views -----------------------------------------------------------
def to_plain(value: object) -> object:
    """``$tensor`` values as nested lists (for input validators and display)."""
    if is_tensor_value(value):
        t = value["$tensor"]  # type: ignore[index]
        return _unflatten(list(t["data"]), list(t["shape"]))
    if isinstance(value, list):
        return [to_plain(v) for v in value]
    if isinstance(value, dict):
        return {k: to_plain(v) for k, v in value.items()}
    return value


def finite(value: object) -> bool:
    """Every number in a (materialized) value is finite."""
    if is_tensor_value(value):
        return all(not isinstance(x, float) or math.isfinite(x)
                   for x in value["$tensor"]["data"])  # type: ignore[index]
    if isinstance(value, list):
        return all(finite(v) for v in value)
    if isinstance(value, float):
        return math.isfinite(value)
    return True
