"""Input-constraint validator for problem 'run-length-encoded-dot-product'.

Hand-written. a and b: 1..1e5 [value, count] pairs of ints (not bools),
value in [-1e4, 1e4], count in [1, 1e9]; the two count sums are equal.
"""


def _rle(v):
    if not isinstance(v, list) or not 1 <= len(v) <= 100000:
        return None
    s = 0
    for p in v:
        if not isinstance(p, list) or len(p) != 2:
            return None
        if not all(isinstance(t, int) and not isinstance(t, bool) for t in p):
            return None
        if not -10**4 <= p[0] <= 10**4 or not 1 <= p[1] <= 10**9:
            return None
        s += p[1]
    return s


def validate_input(a, b):
    sa, sb = _rle(a), _rle(b)
    return sa is not None and sa == sb
