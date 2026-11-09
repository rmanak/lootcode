"""Input-constraint validator for problem 'trajectory-speed-reward'.

Hand-written. trajectories is B x W x 2 (1 <= B <= 100, 2 <= W <= 200),
every coordinate finite (not a bool) with |v| <= 1e4; speedLimits has W - 1
numbers in [0, 100]; dt a number in (0, 1].
"""
import math


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def validate_input(trajectories, speedLimits, dt):
    T = trajectories
    if not isinstance(T, list) or not 1 <= len(T) <= 100 or not isinstance(T[0], list):
        return False
    W = len(T[0])
    if not 2 <= W <= 200:
        return False
    for tr in T:
        if not isinstance(tr, list) or len(tr) != W:
            return False
        for p in tr:
            if not isinstance(p, list) or len(p) != 2 or not all(_num(v, -1e4, 1e4) for v in p):
                return False
    if not isinstance(speedLimits, list) or len(speedLimits) != W - 1:
        return False
    if not all(_num(v, 0, 100) for v in speedLimits):
        return False
    return _num(dt, 0, 1) and dt > 0
