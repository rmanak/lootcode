"""Input-constraint validator for problem 'local-maxima-in-window'.

Hand-written. rawData: 1..1e5 ints (not bools) in [-1e9, 1e9]; localArea an
int in [0, 1e5].
"""


def validate_input(rawData, localArea):
    if not isinstance(rawData, list) or not 1 <= len(rawData) <= 100000:
        return False
    if not all(isinstance(v, int) and not isinstance(v, bool) and -10**9 <= v <= 10**9 for v in rawData):
        return False
    return isinstance(localArea, int) and not isinstance(localArea, bool) and 0 <= localArea <= 100000
