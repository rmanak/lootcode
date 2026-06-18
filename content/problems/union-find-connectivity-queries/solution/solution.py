def connectivity(n, operations):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    out = []
    for op, a, b in operations:
        if op == "union":
            parent[find(a)] = find(b)
        else:
            out.append(find(a) == find(b))
    return out
