"""Input-constraint validator for problem 'lora-forward-and-merge'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X is N x din, W is din x dout, A is din x r, B is
r x dout with 1 <= N, din, dout <= 64 and 1 <= r <= min(16, din, dout); every
entry finite (not a bool) with |v| <= 10; alpha finite in (0, 128];
useRsLora a bool.
"""
import math


def _num(v, bound=10):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= bound


def _dims(M):
    if not isinstance(M, list) or not M or not isinstance(M[0], list) or not M[0]:
        return None
    c = len(M[0])
    if not all(isinstance(r, list) and len(r) == c and all(_num(v) for v in r) for r in M):
        return None
    return len(M), c


def validate_input(X, W, A, B, alpha, useRsLora):
    dx, dw, da, db = _dims(X), _dims(W), _dims(A), _dims(B)
    if None in (dx, dw, da, db):
        return False
    n, din = dx
    if dw[0] != din or da[0] != din or db[0] != da[1] or db[1] != dw[1]:
        return False
    dout, r = dw[1], da[1]
    if not (1 <= n <= 64 and 1 <= din <= 64 and 1 <= dout <= 64 and 1 <= r <= min(16, din, dout)):
        return False
    return _num(alpha, 128) and alpha > 0 and isinstance(useRsLora, bool)
