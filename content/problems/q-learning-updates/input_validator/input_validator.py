"""Input-constraint validator for problem 'q-learning-updates'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound: numStates in [1, 50], numActions in [1, 10];
1..300 episodes, each non-empty, 5000 steps in total; every step is
[s, a, r, s2, done] with s, s2 in [0, numStates), a in [0, numActions),
|r| <= 100 finite, done a bool; done only on an episode's last step; each
step's s2 equals the next step's s; with algorithm "sarsa" every episode ends
with done = true; algorithm one of the three names; alpha in (0, 1], gamma
and epsilon in [0, 1], |initialQ| <= 100. No bools where numbers belong.

Not checked here: the near-tie promise about the final table (only
never-updated actions may tie within 1e-9 of a state's best value). The case
generator vets it.
"""
import math


def _int(v, lo, hi):
    return isinstance(v, int) and not isinstance(v, bool) and lo <= v <= hi


def _num(v, lo, hi):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) and lo <= v <= hi


def validate_input(numStates, numActions, episodes, algorithm, alpha, gamma, epsilon, initialQ):
    if not (_int(numStates, 1, 50) and _int(numActions, 1, 10)):
        return False
    if algorithm not in ("q-learning", "sarsa", "expected-sarsa"):
        return False
    if not (_num(alpha, 0, 1) and alpha > 0 and _num(gamma, 0, 1) and _num(epsilon, 0, 1)
            and _num(initialQ, -100, 100)):
        return False
    if not isinstance(episodes, list) or not 1 <= len(episodes) <= 300:
        return False
    total = 0
    for ep in episodes:
        if not isinstance(ep, list) or not ep:
            return False
        total += len(ep)
        for t, step in enumerate(ep):
            if not (isinstance(step, list) and len(step) == 5):
                return False
            s, a, r, s2, done = step
            if not (_int(s, 0, numStates - 1) and _int(a, 0, numActions - 1) and _num(r, -100, 100)
                    and _int(s2, 0, numStates - 1) and isinstance(done, bool)):
                return False
            last = t == len(ep) - 1
            if done and not last:
                return False
            if not last and ep[t + 1][0] != s2:
                return False
        if algorithm == "sarsa" and ep[-1][4] is not True:
            return False
    return total <= 5000
