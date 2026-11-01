"""Input-constraint validator for problem 'gpt2-block-forward'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: x is T x d with 1 <= T <= 16 and 1 <= d <= 16;
numHeads divides d; params has exactly the twelve stated keys with the stated
shapes (ln vectors d; attnW d x 3d, attnB 3d; attnProjW d x d, attnProjB d;
fcW d x 4d, fcB 4d; projW 4d x d, projB d); every number finite (not a bool)
with |v| <= 10.
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 10


def _vec(v, n):
    return isinstance(v, list) and len(v) == n and all(_num(t) for t in v)


def _mat(M, r, c):
    return isinstance(M, list) and len(M) == r and all(_vec(row, c) for row in M)


def validate_input(x, params, numHeads):
    if not isinstance(x, list) or not 1 <= len(x) <= 16 or not isinstance(x[0], list):
        return False
    T, d = len(x), len(x[0])
    if not 1 <= d <= 16 or not _mat(x, T, d):
        return False
    if not (isinstance(numHeads, int) and not isinstance(numHeads, bool) and 1 <= numHeads <= d
            and d % numHeads == 0):
        return False
    shapes = {"ln1Gamma": (d,), "ln1Beta": (d,), "attnW": (d, 3 * d), "attnB": (3 * d,),
              "attnProjW": (d, d), "attnProjB": (d,), "ln2Gamma": (d,), "ln2Beta": (d,),
              "fcW": (d, 4 * d), "fcB": (4 * d,), "projW": (4 * d, d), "projB": (d,)}
    if not isinstance(params, dict) or set(params) != set(shapes):
        return False
    for key, shape in shapes.items():
        ok = _vec(params[key], shape[0]) if len(shape) == 1 else _mat(params[key], *shape)
        if not ok:
            return False
    return True
