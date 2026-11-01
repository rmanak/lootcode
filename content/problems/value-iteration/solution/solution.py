def _q(outcomes, V, gamma):
    return sum(p * (r + gamma * V[s2]) for p, s2, r in outcomes)


def valueIteration(transitions, gamma, theta, maxIterations):
    n = len(transitions)
    V = [0.0] * n
    sweeps = 0
    while sweeps < maxIterations:
        # Synchronous update: every state reads the previous sweep's values.
        new = [max(_q(o, V, gamma) for o in acts) if acts else 0.0 for acts in transitions]
        delta = max(abs(a - b) for a, b in zip(new, V))
        V = new
        sweeps += 1
        if delta < theta:
            break
    policy = []
    for acts in transitions:
        if not acts:
            policy.append(-1)                   # terminal state
            continue
        qs = [_q(o, V, gamma) for o in acts]
        policy.append(qs.index(max(qs)))        # ties: the lowest action index
    return [V, policy, sweeps]
