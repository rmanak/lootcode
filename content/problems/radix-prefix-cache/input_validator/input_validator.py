"""Input-constraint validator for design problem 'radix-prefix-cache'.

Hand-written (structural part in the generate_class_validators.py shape): the
constructor once at the front, every later op a declared method with the
right arity and types. Every sequence argument is a list of ints in
[0, 1e6]; inserted sequences are non-empty and at most 200 long; at most 3000
calls, and at most 2e5 tokens inserted in total.
"""

_SIG = {'RadixCache': [], 'insert': [('int', 1)], 'search': [('int', 1)], 'prefixMatch': [('int', 1)], 'getAllSequences': [], 'structure': []}
_CTOR = 'RadixCache'


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
    if not _structure_ok(operations, args):
        return False
    if len(operations) - 1 > 3000:
        return False
    total = 0
    for op, a in zip(operations[1:], args[1:]):
        if a and not all(0 <= t <= 10**6 for t in a[0]):
            return False
        if op == "insert":
            if not 1 <= len(a[0]) <= 200:
                return False
            total += len(a[0])
        elif a and len(a[0]) > 1000:
            return False
    return total <= 2 * 10**5
