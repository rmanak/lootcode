"""Input-constraint validator for problem 'debug-broken-training-loop'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: X is N x d with 1 <= N <= 200 and 1 <= d <= 10,
entries finite with |v| <= 10; y has N entries, each 0 or 1; epochs an int in
[1, 20]; batchSize an int in [1, 256]; lr finite in (0, 5]; lrDecay finite in
(0, 1]; l2 finite in [0, 1]; permutations has `epochs` rows, each a
permutation of 0..N-1. No bools.
"""
import math


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def validate_input(X, y, epochs, batchSize, lr, lrDecay, l2, permutations):
    if not isinstance(X, list) or not 1 <= len(X) <= 200 or not isinstance(X[0], list):
        return False
    n, d = len(X), len(X[0])
    if not 1 <= d <= 10:
        return False
    if not all(isinstance(r, list) and len(r) == d and all(_num(v, -10, 10) for v in r) for r in X):
        return False
    if not (isinstance(y, list) and len(y) == n and all(_int(v, 0, 1) for v in y)):
        return False
    if not (_int(epochs, 1, 20) and _int(batchSize, 1, 256)):
        return False
    if not (_num(lr, 0, 5) and lr > 0 and _num(lrDecay, 0, 1) and lrDecay > 0 and _num(l2, 0, 1)):
        return False
    if not (isinstance(permutations, list) and len(permutations) == epochs):
        return False
    want = list(range(n))
    return all(isinstance(p, list) and all(_int(v, 0, n - 1) for v in p) and sorted(p) == want
               for p in permutations)
