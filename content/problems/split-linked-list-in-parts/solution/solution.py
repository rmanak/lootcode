def splitListToParts(root, k):
    n = len(root)
    base, extra = divmod(n, k)
    res = []
    idx = 0
    for i in range(k):
        size = base + (1 if i < extra else 0)
        res.append(root[idx:idx + size])
        idx += size
    return res
