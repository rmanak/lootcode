"""Input-constraint validator for problem 'pad-batch-and-attention-mask'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: sequences a list of 1..16 lists, each 1..32 ints
in [0, 50000]; padId an int in [0, 50000]; side "left" or "right";
padToMultipleOf an int in [1, 8]. No bools.
"""


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def validate_input(sequences, padId, side, padToMultipleOf):
    if not isinstance(sequences, list) or not 1 <= len(sequences) <= 16:
        return False
    for s in sequences:
        if not isinstance(s, list) or not 1 <= len(s) <= 32 or not all(_int(t, 0, 50_000) for t in s):
            return False
    return _int(padId, 0, 50_000) and side in ("left", "right") and _int(padToMultipleOf, 1, 8)
