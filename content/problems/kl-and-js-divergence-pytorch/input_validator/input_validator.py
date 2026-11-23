"""Input-constraint validator for problem 'kl-and-js-divergence'.

Hand-written. p and q are equal-length lists (1..1e4) of numbers (not
bools), each 0 or in [1e-12, 1e6]; each has a positive entry; p[i] == 0
exactly when q[i] == 0 (the statement's promise that both KLs are finite).
"""
import math


def _w(v):
    return (isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
            and (v == 0 or 1e-12 <= v <= 1e6))


def validate_input(p, q):
    if not isinstance(p, list) or not isinstance(q, list) or len(p) != len(q) or not 1 <= len(p) <= 10**4:
        return False
    if not all(_w(v) for v in p) or not all(_w(v) for v in q):
        return False
    if not any(v > 0 for v in p):
        return False
    return all((a == 0) == (b == 0) for a, b in zip(p, q))
