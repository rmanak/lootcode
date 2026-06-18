def eventualSafeNodes(graph):
    n = len(graph)
    color = [0] * n

    def dfs(u):
        if color[u] != 0:
            return color[u] == 2
        color[u] = 1
        for v in graph[u]:
            if not dfs(v):
                return False
        color[u] = 2
        return True

    return [i for i in range(n) if dfs(i)]
