"""Input-constraint validator for problem 'dot-product-of-two-sparse-vectors'.

Hand-written. a and b: lists of <= 1e5 [index, value] pairs of ints (not
bools), indices in [0, 1e9) strictly increasing, values non-zero in
[-1e4, 1e4].
"""


def _vec(v):
    if not isinstance(v, list) or len(v) > 100000:
        return False
    last = -1
    for p in v:
        if not isinstance(p, list) or len(p) != 2:
            return False
        i, x = p
        if not all(isinstance(t, int) and not isinstance(t, bool) for t in p):
            return False
        if not (last < i < 10**9) or x == 0 or not -10**4 <= x <= 10**4:
            return False
        last = i
    return True


def validate_input(a, b):
    return _vec(a) and _vec(b)
