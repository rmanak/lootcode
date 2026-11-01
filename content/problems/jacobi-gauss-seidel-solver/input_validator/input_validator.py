"""Input-constraint validator for problem 'jacobi-gauss-seidel-solver'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: A is n x n with 1 <= n <= 30, b has n entries,
every number finite (not a bool), |A[i][j]| <= 100 and |b[i]| <= 1000; A strictly diagonally
dominant by rows (|A[i][i]| > sum of |A[i][j]| for j != i, so every diagonal
entry is nonzero); method "jacobi" or "gauss-seidel"; tol finite in
[1e-12, 1]; maxIterations an int in [1, 1000].

Not checked here: the stopping-margin promise (no iteration's change is
within a relative 1e-9 of tol). The case generator vets it.
"""
import math


def _num(v, lim=100):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and abs(v) <= lim


def validate_input(A, b, method, tol, maxIterations):
    if not isinstance(A, list) or not 1 <= len(A) <= 30:
        return False
    n = len(A)
    if not all(isinstance(r, list) and len(r) == n and all(_num(v) for v in r) for r in A):
        return False
    if not (isinstance(b, list) and len(b) == n and all(_num(v, 1000) for v in b)):
        return False
    for i in range(n):
        if not abs(A[i][i]) > math.fsum(abs(A[i][j]) for j in range(n) if j != i):
            return False
    if method not in ("jacobi", "gauss-seidel"):
        return False
    if not (_num(tol, 1) and 1e-12 <= tol <= 1):
        return False
    return isinstance(maxIterations, int) and not isinstance(maxIterations, bool) and 1 <= maxIterations <= 1000
