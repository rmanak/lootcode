"""Input-constraint validator for problem 'conv2d-stride-padding'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: x is Cin x H x W with 1 <= Cin <= 8 and
1 <= H, W <= 32; weight is Cout x Cin x kH x kW with 1 <= Cout <= 8,
1 <= kH, kW <= 7, kH <= H + 2*padding and kW <= W + 2*padding; bias has Cout
entries; stride an int in [1, 4]; padding an int in [0, 3]; every number finite
(not a bool) with |v| <= 10.
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 10


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def _shape(a, depth):
    """Shape of a rectangular nested list of numbers `depth` deep, else None."""
    if depth == 0:
        return () if _num(a) else None
    if not isinstance(a, list) or not a:
        return None
    subs = [_shape(t, depth - 1) for t in a]
    if subs[0] is None or any(s != subs[0] for s in subs):
        return None
    return (len(a),) + subs[0]


def validate_input(x, weight, bias, stride, padding):
    if not (_int(stride, 1, 4) and _int(padding, 0, 3)):
        return False
    sx = _shape(x, 3)
    sw = _shape(weight, 4)
    if sx is None or sw is None:
        return False
    cin, h, w = sx
    cout, cin_w, kh, kw = sw
    if not (1 <= cin <= 8 and 1 <= h <= 32 and 1 <= w <= 32 and 1 <= cout <= 8 and cin_w == cin):
        return False
    if not (1 <= kh <= 7 and 1 <= kw <= 7 and kh <= h + 2 * padding and kw <= w + 2 * padding):
        return False
    return isinstance(bias, list) and len(bias) == cout and all(_num(v) for v in bias)
