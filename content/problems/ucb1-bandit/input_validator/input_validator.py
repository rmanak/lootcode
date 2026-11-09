"""Input-constraint validator for problem 'ucb1-bandit'.

Hand-written. rewards: K lists (2 <= K <= 10) of 0/1 ints, each at least T
long; T an int with K <= T <= 2000. Also replays UCB1 and enforces the stated
promise: whenever two arms with different (pulls, mean) statistics come
within 1e-9 of the best index, the input is rejected.
"""
import math


def validate_input(rewards, T):
    if not isinstance(T, int) or isinstance(T, bool):
        return False
    if not isinstance(rewards, list) or not 2 <= len(rewards) <= 10:
        return False
    K = len(rewards)
    if not K <= T <= 2000:
        return False
    for r in rewards:
        if not isinstance(r, list) or len(r) < T:
            return False
        if not all(isinstance(v, int) and not isinstance(v, bool) and v in (0, 1) for v in r):
            return False
    n, s = [0] * K, [0] * K
    for t in range(1, T + 1):
        if t <= K:
            a = t - 1
        else:
            u = [s[i] / n[i] + math.sqrt(2 * math.log(t) / n[i]) for i in range(K)]
            top = max(u)
            near = [i for i in range(K) if top - u[i] < 1e-9]
            if len({(n[i], s[i]) for i in near}) > 1:
                return False
            a = near[0]
        s[a] += rewards[a][n[a]]
        n[a] += 1
    return True
