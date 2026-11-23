"""Input-constraint validator for problem 'classifier-free-guidance'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: noisePred has an even number 2B of rows,
1 <= B <= 16, each of N numbers with 2 <= N <= 256, every entry finite
(not a bool) with |v| <= 100; guidanceScale finite in [0, 20];
guidanceRescale finite in [0, 1]. When guidanceRescale > 0, every
conditional row and every guided row (uncond + scale * (cond - uncond)) has a
sample standard deviation of at least 1e-3.
"""
import math


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def _std(row):
    m = math.fsum(row) / len(row)
    return math.sqrt(math.fsum((v - m) ** 2 for v in row) / (len(row) - 1))


def validate_input(noisePred, guidanceScale, guidanceRescale):
    if not isinstance(noisePred, list) or len(noisePred) % 2 or not 2 <= len(noisePred) <= 32:
        return False
    if not isinstance(noisePred[0], list):
        return False
    n = len(noisePred[0])
    if not 2 <= n <= 256:
        return False
    if not all(isinstance(r, list) and len(r) == n and all(_num(v, -100, 100) for v in r) for r in noisePred):
        return False
    if not (_num(guidanceScale, 0, 20) and _num(guidanceRescale, 0, 1)):
        return False
    if guidanceRescale > 0:
        b = len(noisePred) // 2
        for u, c in zip(noisePred[:b], noisePred[b:]):
            guided = [a + guidanceScale * (x - a) for a, x in zip(u, c)]
            if _std(c) < 1e-3 or _std(guided) < 1e-3:
                return False
    return True
