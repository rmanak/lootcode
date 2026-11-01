"""Input-constraint validator for problem 'moe-top-k-gating'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X is T x d with 1 <= T <= 64 and 1 <= d <= 16;
Wg is d x E with 1 <= E <= 16; experts is E x d x d; every entry finite
(not a bool) with |v| <= 10; k an int in [1, E]; capacity an int in [1, T].

Not checked here: the promise that, per token, the k-th and (k+1)-th largest
logits (and any two adjacent ones among the top k) are exactly equal only when
every input is an integer, and otherwise differ by more than 1e-9 relative.
The case generator vets that.
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 10


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def _matrix(M, rows, cols):
    return (isinstance(M, list) and len(M) == rows
            and all(isinstance(r, list) and len(r) == cols and all(_num(v) for v in r) for r in M))


def validate_input(X, Wg, experts, k, capacity):
    if not isinstance(X, list) or not 1 <= len(X) <= 64 or not isinstance(X[0], list):
        return False
    T, d = len(X), len(X[0])
    if not 1 <= d <= 16 or not _matrix(X, T, d):
        return False
    if not isinstance(Wg, list) or len(Wg) != d or not isinstance(Wg[0], list):
        return False
    E = len(Wg[0])
    if not 1 <= E <= 16 or not _matrix(Wg, d, E):
        return False
    if not (isinstance(experts, list) and len(experts) == E and all(_matrix(M, d, d) for M in experts)):
        return False
    return _int(k, 1, E) and _int(capacity, 1, T)
