def allPathsSourceTarget(graph):
    n = len(graph)
    res = []

    def dfs(node, path):
        if node == n - 1:
            res.append(path[:])
            return
        for nb in graph[node]:
            path.append(nb)
            dfs(nb, path)
            path.pop()

    dfs(0, [0])
    return res
