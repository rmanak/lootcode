"""Input-constraint validator for design problem 'weighted-pick-by-draw'.

Hand-written (structural part in the generate_class_validators.py shape).
1..1e5 initial weights, ints in [0, 1e12]; update takes an index in range and
a weight in [0, 1e12]; pick takes r with 0 <= r < current total (so the total
is positive whenever pick is called); at most 1e5 calls.
"""

_SIG = {'WeightedPicker': [('int', 1)], 'pick': [('int', 0)], 'update': [('int', 0), ('int', 0)], 'total': []}
_CTOR = 'WeightedPicker'


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
    if not _structure_ok(operations, args) or len(operations) - 1 > 100000:
        return False
    w = list(args[0][0])
    if not 1 <= len(w) <= 100000 or not all(0 <= x <= 10**12 for x in w):
        return False
    total = sum(w)
    for op, a in zip(operations[1:], args[1:]):
        if op == "update":
            i, x = a
            if not (0 <= i < len(w) and 0 <= x <= 10**12):
                return False
            total += x - w[i]
            w[i] = x
        elif op == "pick" and not 0 <= a[0] < total:
            return False
    return True
