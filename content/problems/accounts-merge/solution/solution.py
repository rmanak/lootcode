def accountsMerge(accounts):
    from collections import defaultdict
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    owner = {}
    for acc in accounts:
        name = acc[0]
        first = acc[1]
        for e in acc[1:]:
            owner[e] = name
            parent.setdefault(e, e)
            parent[find(e)] = find(first)
    groups = defaultdict(list)
    for e in owner:
        groups[find(e)].append(e)
    return [[owner[root]] + sorted(emails) for root, emails in groups.items()]
