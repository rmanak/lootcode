"""Input-constraint validator for problem 'matrix-factorization-gradient-descent'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: U has 1 <= users <= 50 rows and V 1 <= items <= 50
rows, all of the same length k with 1 <= k <= 10, every entry finite with
|v| <= 10; ratings is a list of 1..500 triples [user, item, rating] with int
user in [0, users), int item in [0, items), rating finite with |rating| <= 10,
and no (user, item) pair repeated; lr finite with 0 < lr <= 1; reg finite with
0 <= reg <= 10; steps an int with 1 <= steps <= 500.

Not checked here: the promise that the loss stays bounded (the learning rate
is small enough). The case generator vets that, and a 1e-12 perturbation.
"""
import math


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _num(v, bound):
    return (isinstance(v, (int, float)) and not isinstance(v, bool)
            and math.isfinite(v) and abs(v) <= bound)


def _matrix(M, width):
    return (isinstance(M, list) and 1 <= len(M) <= 50
            and all(isinstance(r, list) and len(r) == width and all(_num(v, 10) for v in r) for r in M))


def validate_input(ratings, U, V, lr, reg, steps):
    if not isinstance(U, list) or not U or not isinstance(U[0], list):
        return False
    k = len(U[0])
    if not (1 <= k <= 10 and _matrix(U, k) and _matrix(V, k)):
        return False
    if not isinstance(ratings, list) or not 1 <= len(ratings) <= 500:
        return False
    seen = set()
    for t in ratings:
        if not (isinstance(t, list) and len(t) == 3):
            return False
        u, i, r = t
        if not (_int(u) and 0 <= u < len(U) and _int(i) and 0 <= i < len(V) and _num(r, 10)):
            return False
        if (u, i) in seen:
            return False
        seen.add((u, i))
    if not (_num(lr, 1) and lr > 0 and _num(reg, 10) and reg >= 0):
        return False
    return _int(steps) and 1 <= steps <= 500
