"""Input-constraint validator for problem 'hyperparameter-grid'.

Hand-written. values: <= 30 lists of <= 100 options, each an int, finite
float or str (not a bool); the product of their lengths <= 1e18; queries:
<= 1e4 ints (not bools) in [0, product).
"""
import math


def _opt(v):
    if isinstance(v, bool):
        return False
    if isinstance(v, float):
        return math.isfinite(v)
    return isinstance(v, (int, str))


def validate_input(values, queries):
    if not isinstance(values, list) or len(values) > 30:
        return False
    count = 1
    for opts in values:
        if not isinstance(opts, list) or len(opts) > 100 or not all(_opt(v) for v in opts):
            return False
        count *= len(opts)
    if count > 10**18:
        return False
    if not isinstance(queries, list) or len(queries) > 10**4:
        return False
    return all(isinstance(q, int) and not isinstance(q, bool) and 0 <= q < count for q in queries)
