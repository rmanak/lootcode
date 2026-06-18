def minimumSpanningTree(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    for w, u, v in sorted((w, u, v) for u, v, w in edges):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
    return total
