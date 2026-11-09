"""Input-constraint validator for problem 'dynamic-request-batching'.

Hand-written. arrivals: 1..3000 ints (not bools) in [0, 1e6], sorted
non-decreasing; maxBatchSize an int in [1, 64]; maxWaitMs and setupMs ints
in [0, 1e4]; perItemMs an int in [0, 1e3].
"""


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def validate_input(arrivals, maxBatchSize, maxWaitMs, setupMs, perItemMs):
    if not isinstance(arrivals, list) or not 1 <= len(arrivals) <= 3000:
        return False
    if not all(_int(a, 0, 10**6) for a in arrivals):
        return False
    if any(a > b for a, b in zip(arrivals, arrivals[1:])):
        return False
    return (_int(maxBatchSize, 1, 64) and _int(maxWaitMs, 0, 10**4) and _int(setupMs, 0, 10**4)
            and _int(perItemMs, 0, 10**3))
