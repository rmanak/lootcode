def qLearning(numStates, numActions, episodes, algorithm, alpha, gamma, epsilon, initialQ):
    Q = [[float(initialQ)] * numActions for _ in range(numStates)]
    tdErrors = []
    for episode in episodes:
        for t, (s, a, r, s2, done) in enumerate(episode):
            # The target is computed from the table as it stands *before* this update.
            if done:
                target = r                                  # no bootstrapping past a terminal step
            elif algorithm == "q-learning":
                target = r + gamma * max(Q[s2])             # off-policy: the greedy next value
            elif algorithm == "sarsa":
                a2 = episode[t + 1][1]                      # the action actually taken next
                target = r + gamma * Q[s2][a2]
            else:                                           # expected-sarsa under epsilon-greedy
                row = Q[s2]
                target = r + gamma * ((1 - epsilon) * max(row) + epsilon * sum(row) / numActions)
            delta = target - Q[s][a]
            Q[s][a] += alpha * delta
            tdErrors.append(delta)
    policy = [row.index(max(row)) for row in Q]             # ties: the lowest action index
    return [Q, tdErrors, policy]
