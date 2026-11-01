"""Input-constraint validator for problem 'covariance-and-correlation'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X is n x d with 1 <= n <= 1000 and 1 <= d <= 20,
every value finite (not a bool) with |x| <= 10^9; ddof the int 0 or 1 with
n - ddof >= 1.
"""
import math


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= 1e9


def validate_input(X, ddof):
    if not isinstance(X, list) or not 1 <= len(X) <= 1000 or not isinstance(X[0], list):
        return False
    d = len(X[0])
    if not 1 <= d <= 20:
        return False
    if not all(isinstance(r, list) and len(r) == d and all(_num(v) for v in r) for r in X):
        return False
    return isinstance(ddof, int) and not isinstance(ddof, bool) and ddof in (0, 1) and len(X) - ddof >= 1
