"""Input-constraint validator for problem 'dense-layer-backward'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X is N x Din, W is Din x Dout, b has Dout entries
and dY is N x Dout, with 1 <= N <= 100 and 1 <= Din, Dout <= 32; every entry
finite with |v| <= 10; activation one of "linear", "relu", "tanh", "sigmoid".

Not checked here: the promise that no relu pre-activation is within 1e-9 of 0
unless it is exactly 0 in exact arithmetic with all inputs multiples of 1/16.
The case generator vets that.
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 10


def _mat(M, rows, cols=None):
    if not isinstance(M, list) or not M or (rows is not None and len(M) != rows):
        return None
    if not isinstance(M[0], list):
        return None
    c = len(M[0]) if cols is None else cols
    if not all(isinstance(r, list) and len(r) == c and all(_num(v) for v in r) for r in M):
        return None
    return len(M), c


def validate_input(X, W, b, dY, activation):
    sx = _mat(X, None)
    if sx is None or not (1 <= sx[0] <= 100 and 1 <= sx[1] <= 32):
        return False
    sw = _mat(W, sx[1])
    if sw is None or not 1 <= sw[1] <= 32:
        return False
    if not (isinstance(b, list) and len(b) == sw[1] and all(_num(v) for v in b)):
        return False
    if _mat(dY, sx[0], sw[1]) is None:
        return False
    return activation in ("linear", "relu", "tanh", "sigmoid")
