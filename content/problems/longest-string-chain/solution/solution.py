def longestStrChain(words):
    words.sort(key=len)
    dp = {}
    best = 1
    for w in words:
        dp[w] = 1
        for i in range(len(w)):
            pred = w[:i] + w[i + 1:]
            if pred in dp:
                dp[w] = max(dp[w], dp[pred] + 1)
        best = max(best, dp[w])
    return best
