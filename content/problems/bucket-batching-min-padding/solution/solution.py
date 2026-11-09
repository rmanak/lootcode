def minPaddedTokens(lengths, G):
    L = sorted(lengths)
    K = len(L)
    INF = float("inf")
    # best[i] = min cost of the first i sorted documents in g batches (g grows each round)
    best = [INF] * (K + 1)
    best[0] = 0
    for g in range(1, G + 1):
        nxt = [INF] * (K + 1)
        for i in range(g, K - (G - g) + 1):      # leave at least one document per later batch
            top = L[i - 1]                       # the batch L[j:i] is padded to its last element
            nxt[i] = min(best[j] + (i - j) * top for j in range(g - 1, i))
        best = nxt
    return best[K]
