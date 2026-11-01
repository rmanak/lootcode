"""Input-constraint validator for problem 'k-means-from-given-centroids'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1 <= N <= 200 points and 1 <= K <= 10 initial
centroids, all vectors the same length d with 1 <= d <= 10, every coordinate a
finite number with |value| <= 100, and maxIters an integer (not a bool) with
1 <= maxIters <= 100. The statement pins the tie-break and the empty-cluster
rule, so it makes no promise about the answer that needs enforcing here.

Not a statement promise, so not checked here: test inputs must also avoid
near-ties (two centroids within float noise of equally close to a point in some
iteration), where correct implementations could disagree. The case generator
vets that with an exact rational re-run.
"""
import math

MAX_N = 200
MAX_K = 10
MAX_DIM = 10
MAX_ABS = 100
MAX_ITERS = 100


def _number(x):
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x) and abs(x) <= MAX_ABS)


def _vectors(vs, max_count, d):
    return (isinstance(vs, list) and 1 <= len(vs) <= max_count
            and all(isinstance(v, list) and len(v) == d and all(_number(x) for x in v)
                    for v in vs))


def validate_input(points, initialCentroids, maxIters):
    if not isinstance(points, list) or not points or not isinstance(points[0], list):
        return False
    d = len(points[0])
    if not 1 <= d <= MAX_DIM:
        return False
    if not (_vectors(points, MAX_N, d) and _vectors(initialCentroids, MAX_K, d)):
        return False
    return (isinstance(maxIters, int) and not isinstance(maxIters, bool)
            and 1 <= maxIters <= MAX_ITERS)
