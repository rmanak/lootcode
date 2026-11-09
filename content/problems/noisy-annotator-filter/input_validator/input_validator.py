"""Input-constraint validator for problem 'noisy-annotator-filter'.

Hand-written. annotations: N x A ints (1 <= N <= 2000, 1 <= A <= 50), each
-1 or in [0, 100]; threshold a number (not a bool) in [0, 1].
"""
import math


def validate_input(annotations, threshold):
    M = annotations
    if not isinstance(M, list) or not 1 <= len(M) <= 2000 or not isinstance(M[0], list):
        return False
    A = len(M[0])
    if not 1 <= A <= 50:
        return False
    for r in M:
        if not isinstance(r, list) or len(r) != A:
            return False
        if not all(isinstance(v, int) and not isinstance(v, bool) and (v == -1 or 0 <= v <= 100) for v in r):
            return False
    return (isinstance(threshold, (int, float)) and not isinstance(threshold, bool)
            and math.isfinite(threshold) and 0 <= threshold <= 1)
