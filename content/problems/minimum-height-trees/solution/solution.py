def findMinHeightTrees(n, edges):
    if n == 1:
        return [0]
    from collections import defaultdict
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    leaves = [x for x in range(n) if len(adj[x]) == 1]
    remaining = n
    while remaining > 2:
        remaining -= len(leaves)
        new_leaves = []
        for leaf in leaves:
            nb = adj[leaf].pop()
            adj[nb].discard(leaf)
            if len(adj[nb]) == 1:
                new_leaves.append(nb)
        leaves = new_leaves
    return sorted(leaves)
