"""Input-constraint validator for problem 'max-pool-forward-backward'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: x is C x H x W with 1 <= C <= 8 and
1 <= H, W <= 32, entries |v| <= 100; kernel = [kH, kW] ints with
1 <= kH <= H and 1 <= kW <= W; stride an int in [1, 4]; dout is
C x Hout x Wout for Hout = (H - kH) // stride + 1 (likewise Wout), entries
|v| <= 10. Every number finite and not a bool.
"""
import math


def _num(v, bound):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= bound


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def _shape(a, depth, bound):
    if depth == 0:
        return () if _num(a, bound) else None
    if not isinstance(a, list) or not a:
        return None
    subs = [_shape(t, depth - 1, bound) for t in a]
    if subs[0] is None or any(s != subs[0] for s in subs):
        return None
    return (len(a),) + subs[0]


def validate_input(x, dout, kernel, stride):
    sx = _shape(x, 3, 100)
    if sx is None:
        return False
    c, h, w = sx
    if not (1 <= c <= 8 and 1 <= h <= 32 and 1 <= w <= 32):
        return False
    if not (isinstance(kernel, list) and len(kernel) == 2 and _int(kernel[0], 1, h) and _int(kernel[1], 1, w)):
        return False
    if not _int(stride, 1, 4):
        return False
    ho, wo = (h - kernel[0]) // stride + 1, (w - kernel[1]) // stride + 1
    return _shape(dout, 3, 10) == (c, ho, wo)
