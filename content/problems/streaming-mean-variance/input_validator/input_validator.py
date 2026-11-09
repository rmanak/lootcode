"""Input-constraint validator for design problem 'streaming-mean-variance'.

Hand-written (structural part in the generate_class_validators.py shape).
Shard ids are ints in [0, 100); added values are finite numbers (not bools)
with |x| <= 1e9; merge takes two different shard ids; at most 20000 calls.
"""
import math

_SIG = {'StreamStats': [], 'add': [('int', 0), ('float', 0)], 'merge': [('int', 0), ('int', 0)], 'stats': [('int', 0)]}
_CTOR = 'StreamStats'


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


def validate_input(operations, args):
    if not _structure_ok(operations, args) or len(operations) - 1 > 20000:
        return False
    for op, a in zip(operations[1:], args[1:]):
        if op in ("add", "stats") and not 0 <= a[0] < 100:
            return False
        if op == "add" and not (math.isfinite(a[1]) and abs(a[1]) <= 1e9):
            return False
        if op == "merge" and not (0 <= a[0] < 100 and 0 <= a[1] < 100 and a[0] != a[1]):
            return False
    return True
