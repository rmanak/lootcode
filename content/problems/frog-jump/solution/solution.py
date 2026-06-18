def canCross(stones):
    stone_set = set(stones)
    from collections import defaultdict
    dp = defaultdict(set)
    dp[stones[0]].add(0)
    for s in stones:
        for k in dp[s]:
            for step in (k - 1, k, k + 1):
                if step > 0 and s + step in stone_set:
                    dp[s + step].add(step)
    return len(dp[stones[-1]]) > 0
