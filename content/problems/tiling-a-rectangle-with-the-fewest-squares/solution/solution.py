def tilingRectangle(n, m):
    best = [n * m]
    heights = [0] * m

    def dfs(count):
        if count >= best[0]:
            return
        min_h = min(heights)
        if min_h == n:
            best[0] = min(best[0], count)
            return
        start = heights.index(min_h)
        max_possible = min(m - start, n - min_h)
        for s in range(max_possible, 0, -1):
            if all(heights[start + t] == min_h for t in range(s)):
                for t in range(s):
                    heights[start + t] += s
                dfs(count + 1)
                for t in range(s):
                    heights[start + t] -= s

    dfs(0)
    return best[0]
