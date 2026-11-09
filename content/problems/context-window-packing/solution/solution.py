import numpy as np


def packContext(budget, minTokens, documents):
    NEG = -np.inf
    dp = np.full(budget + 1, NEG)        # dp[c]: best score using exactly c tokens, docs seen so far
    dp[0] = 0.0
    best2 = 0.0
    caps = np.arange(budget + 1)
    for _, score, T in documents:
        # this document as the truncated last one, after any whole subset of the earlier ones
        room = budget - caps                                   # tokens left after a whole subset of size c
        t = np.minimum(room, T)
        ok = (t >= minTokens) & (dp > NEG)
        if ok.any():
            best2 = max(best2, float((dp[ok] + score * t[ok] / T).max()))
        # then as a whole document (0/1 knapsack, using the old dp on the right-hand side)
        if T <= budget:
            new = dp.copy()
            new[T:] = np.maximum(dp[T:], dp[:budget + 1 - T] + score)
            dp = new
    best1 = float(dp.max())
    return [best1, max(best1, best2)]
