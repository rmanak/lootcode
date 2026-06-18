def numsSameConsecDiff(n, k):
    res = []

    def dfs(num, length):
        if length == n:
            res.append(num)
            return
        last = num % 10
        for d in {last + k, last - k}:
            if 0 <= d <= 9:
                dfs(num * 10 + d, length + 1)

    for start in range(1, 10):
        dfs(start, 1)
    return res
