def validTree(n, edges):
    # A tree on n nodes has exactly n - 1 edges; combined with "no cycle" this
    # guarantees the graph is also connected.
    if len(edges) != n - 1:
        return False

    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return False  # u and v already connected -> this edge closes a cycle
        parent[ru] = rv
    return True
