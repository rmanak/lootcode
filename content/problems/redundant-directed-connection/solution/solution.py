def findRedundantDirectedConnection(edges):
    n = len(edges)
    parent = [0] * (n + 1)
    cand1 = cand2 = None
    for i, (u, v) in enumerate(edges):
        if parent[v] != 0:
            cand1 = [parent[v], v]
            cand2 = [u, v]
            edges[i] = [0, 0]
            break
        parent[v] = u
    uf = list(range(n + 1))

    def find(x):
        while uf[x] != x:
            uf[x] = uf[uf[x]]
            x = uf[x]
        return x

    for u, v in edges:
        if u == 0:
            continue
        ru, rv = find(u), find(v)
        if ru == rv:
            return cand1 if cand1 else [u, v]
        uf[rv] = ru
    return cand2
