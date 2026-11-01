"""Input-constraint validator for problem 'grouped-query-attention'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X is T x D with 1 <= T, D <= 32; numHeads divides
D and numKvHeads divides numHeads (both >= 1); with dh = D / numHeads, Wq and
Wo are D x D, Wk and Wv are D x (numKvHeads * dh); every entry finite (not a
bool) with |v| <= 10.
"""
import math

MAX_T = MAX_D = 32


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 10


def _matrix(M, rows, cols):
    return (isinstance(M, list) and len(M) == rows
            and all(isinstance(r, list) and len(r) == cols and all(_num(v) for v in r) for r in M))


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_input(X, Wq, Wk, Wv, Wo, numHeads, numKvHeads):
    if not isinstance(X, list) or not 1 <= len(X) <= MAX_T:
        return False
    if not isinstance(X[0], list) or not 1 <= len(X[0]) <= MAX_D:
        return False
    T, D = len(X), len(X[0])
    if not _matrix(X, T, D):
        return False
    if not (_int(numHeads) and _int(numKvHeads) and 1 <= numHeads <= D and D % numHeads == 0
            and 1 <= numKvHeads <= numHeads and numHeads % numKvHeads == 0):
        return False
    kv = numKvHeads * (D // numHeads)
    return _matrix(Wq, D, D) and _matrix(Wo, D, D) and _matrix(Wk, D, kv) and _matrix(Wv, D, kv)
