import math


def ucb1(rewards, T):
    K = len(rewards)
    n = [0] * K          # pulls per arm
    s = [0] * K          # total reward per arm
    pulls, total = [], 0
    for t in range(1, T + 1):
        if t <= K:
            a = t - 1
        else:
            log_t = math.log(t)
            a = max(range(K), key=lambda i: (s[i] / n[i] + math.sqrt(2 * log_t / n[i]), -i))
        r = rewards[a][n[a]]
        n[a] += 1
        s[a] += r
        total += r
        pulls.append(a)
    return [total, pulls]
