"""Input-constraint validator for design problem 'streaming-softmax-entropy'.

Hand-written (structural part in the generate_class_validators.py shape): the
constructor once at the front, every later op `update` (one list of numbers)
or `entropy` (no args); every logit finite with |x| <= 1e16; at most 2000
calls and 20000 logits in total; `entropy` only after at least one logit.
"""
import math

_SIG = {'StreamingEntropy': [], 'update': [('float', 1)], 'entropy': []}
_CTOR = 'StreamingEntropy'


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
    if len(operations) - 1 > 2000:
        return False
    seen = 0
    for op, a in zip(operations[1:], args[1:]):
        if op == "update":
            if not all(math.isfinite(v) and abs(v) <= 1e16 for v in a[0]):
                return False
            seen += len(a[0])
        elif seen == 0:
            return False
    return seen <= 20000
