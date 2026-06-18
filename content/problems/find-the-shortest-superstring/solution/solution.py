def shortestSuperstringLength(words):
    words = [w for w in words if not any(w != o and w in o for o in words)]
    n = len(words)
    if n == 0:
        return 0
    if n == 1:
        return len(words[0])
    overlap = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                m = min(len(words[i]), len(words[j]))
                for k in range(m, 0, -1):
                    if words[i][-k:] == words[j][:k]:
                        overlap[i][j] = k
                        break
    dp = [[0] * n for _ in range(1 << n)]
    for mask in range(1 << n):
        for last in range(n):
            if not (mask >> last) & 1:
                continue
            for nxt in range(n):
                if (mask >> nxt) & 1:
                    continue
                val = dp[mask][last] + overlap[last][nxt]
                nm = mask | (1 << nxt)
                if val > dp[nm][nxt]:
                    dp[nm][nxt] = val
    full = (1 << n) - 1
    total = sum(len(w) for w in words)
    return total - max(dp[full])
