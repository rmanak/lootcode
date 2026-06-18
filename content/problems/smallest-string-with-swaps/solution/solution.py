def smallestStringWithSwaps(s, pairs):
    n = len(s)
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for a, b in pairs:
        par[find(a)] = find(b)
    from collections import defaultdict
    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)
    res = list(s)
    for idxs in groups.values():
        chars = sorted(res[i] for i in idxs)
        for i, ch in zip(idxs, chars):
            res[i] = ch
    return "".join(res)
