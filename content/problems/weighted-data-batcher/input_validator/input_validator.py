"""Input-constraint validator for design problem 'weighted-data-batcher'.

Hand-written (structural part in the generate_class_validators.py shape).
1..10 distinct non-empty names (letters, digits, '_', '-'; <= 20 chars) with
as many weights, each an int in [1, 100]; batchSize an int in [1, 256]; at
most 500 calls. Every loadStateDict argument is a state that stateDict
returned earlier in the same sequence (the statement's promise).
"""
import re

_SIG = {'DataBatcher': [('string', 1), ('int', 1), ('int', 0)], 'nextBatch': [], 'stateDict': [], 'loadStateDict': [('int', 2)]}
_CTOR = 'DataBatcher'


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
    if not _structure_ok(operations, args) or len(operations) - 1 > 500:
        return False
    names, weights, bs = args[0]
    if not 1 <= len(names) <= 10 or len(set(names)) != len(names) or len(weights) != len(names):
        return False
    if not all(re.fullmatch(r"[A-Za-z0-9_-]{1,20}", n) for n in names):
        return False
    if not all(1 <= w <= 100 for w in weights) or not 1 <= bs <= 256:
        return False
    W = sum(weights)
    offsets, current = [0] * len(names), [0] * len(names)
    saved = []
    for op, a in zip(operations[1:], args[1:]):
        if op == "nextBatch":
            for _ in range(bs):
                current = [c + w for c, w in zip(current, weights)]
                d = max(range(len(names)), key=lambda i: (current[i], -i))
                current[d] -= W
                offsets[d] += 1
        elif op == "stateDict":
            saved.append([list(offsets), list(current)])
        else:
            if a[0] not in saved:
                return False
            offsets, current = list(a[0][0]), list(a[0][1])
    return True
