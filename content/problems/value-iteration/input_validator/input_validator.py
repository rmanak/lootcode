"""Input-constraint validator for problem 'value-iteration'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: 1..100 states; each state has 0..10 actions; each
action is a list of 1..10 outcomes [p, nextState, reward] with p finite in
(0, 1], nextState an int in [0, S), |reward| <= 100, and the action's
probabilities summing to 1 within 1e-9; gamma finite in [0, 0.99]; theta
finite in [1e-10, 1]; maxIterations an int in [1, 10^4]. No bools.

Not checked here: the margin promises (no sweep's largest change within
1e-9 relative of theta; a state's best two actions differ by more than 1e-9
relative or have identical outcome lists). The case generator vets those.
"""
import math


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def validate_input(transitions, gamma, theta, maxIterations):
    if not isinstance(transitions, list) or not 1 <= len(transitions) <= 100:
        return False
    n = len(transitions)
    for acts in transitions:
        if not isinstance(acts, list) or len(acts) > 10:
            return False
        for outs in acts:
            if not isinstance(outs, list) or not 1 <= len(outs) <= 10:
                return False
            for o in outs:
                if not (isinstance(o, list) and len(o) == 3 and _num(o[0], 0, 1) and o[0] > 0
                        and isinstance(o[1], int) and not isinstance(o[1], bool) and 0 <= o[1] < n
                        and _num(o[2], -100, 100)):
                    return False
            if abs(math.fsum(o[0] for o in outs) - 1) > 1e-9:
                return False
    return (_num(gamma, 0, 0.99) and _num(theta, 1e-10, 1) and isinstance(maxIterations, int)
            and not isinstance(maxIterations, bool) and 1 <= maxIterations <= 10_000)
