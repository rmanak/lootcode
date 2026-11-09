"""Input-constraint validator for design problem 'storage-full-forecast'.

Hand-written (structural part in the generate_class_validators.py shape).
windowSize an int in [2, 500]; timestamps ints in [0, 4e9], strictly
increasing across recordUsage calls; usedBytes and totalBytes ints in
[0, 1e13]; at most 3000 calls. Also enforces the statement's promise that
whenever a forecast or rate is asked for, the windowed least-squares slope is
either exactly 0 or clearly non-zero: |slope| * (time span) >= 1e-6 *
(1 + byte range), checked in exact rational arithmetic.
"""
from collections import deque
from fractions import Fraction

_SIG = {'StorageForecaster': [('int', 0)], 'recordUsage': [('int', 0), ('int', 0)], 'forecastFull': [('int', 0)], 'getGrowthRatePerDay': []}
_CTOR = 'StorageForecaster'


def _scalar_ok(v, base):
    if base == "int":
        return isinstance(v, int) and not isinstance(v, bool)
    if base in ("float", "num"):
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if base == "bool":
        return isinstance(v, bool)
    if base in ("string", "str", "char"):
        return isinstance(v, str)
    return True


def _type_ok(v, base, dims):
    if dims == 0:
        return _scalar_ok(v, base)
    if not isinstance(v, list):
        return False
    return all(_type_ok(e, base, dims - 1) for e in v)


def _structure_ok(operations, args):
    if not isinstance(operations, list) or not isinstance(args, list):
        return False
    if len(operations) != len(args) or not operations or operations[0] != _CTOR:
        return False
    for i, (op, a) in enumerate(zip(operations, args)):
        if op not in _SIG or (op == _CTOR) != (i == 0):
            return False
        if not isinstance(a, list) or len(a) != len(_SIG[op]):
            return False
        if not all(_type_ok(v, b, d) for v, (b, d) in zip(a, _SIG[op])):
            return False
    return True


def _slope(pts):
    n = len(pts)
    mt = Fraction(sum(t for t, _ in pts), n)
    my = Fraction(sum(y for _, y in pts), n)
    num = sum((t - mt) * (y - my) for t, y in pts)
    den = sum((t - mt) ** 2 for t, _ in pts)
    return num / den


def validate_input(operations, args):
    if not _structure_ok(operations, args) or len(operations) - 1 > 3000:
        return False
    w = args[0][0]
    if not 2 <= w <= 500:
        return False
    pts = deque(maxlen=w)
    last = -1
    for op, a in zip(operations[1:], args[1:]):
        if op == "recordUsage":
            t, y = a
            if not (0 <= t <= 4 * 10**9 and t > last and 0 <= y <= 10**13):
                return False
            last = t
            pts.append((t, y))
        else:
            if op == "forecastFull" and not 0 <= a[0] <= 10**13:
                return False
            if len(pts) >= 2:
                b = _slope(list(pts))
                span = pts[-1][0] - pts[0][0]
                yr = max(y for _, y in pts) - min(y for _, y in pts)
                if b != 0 and abs(b) * span < Fraction(1, 10**6) * (1 + yr):
                    return False
    return True
