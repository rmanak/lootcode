def getKth(lo, hi, k):
    memo = {1: 0}

    def power(x):
        path = []
        cur = x
        while cur not in memo:
            path.append(cur)
            cur = cur // 2 if cur % 2 == 0 else 3 * cur + 1
        base = memo[cur]
        for i, v in enumerate(reversed(path)):
            memo[v] = base + i + 1
        return memo[x]

    return sorted(range(lo, hi + 1), key=lambda x: (power(x), x))[k - 1]
