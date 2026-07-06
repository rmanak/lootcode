def copyRandomList(head):
    n = len(head)
    if n == 0:
        return []
    nodes = [{"val": v, "next": None, "random": None} for v, _ in head]
    for i in range(n):
        nodes[i]["next"] = nodes[i + 1] if i + 1 < n else None
        ri = head[i][1]
        nodes[i]["random"] = nodes[ri] if ri is not None else None
    index = {id(node): i for i, node in enumerate(nodes)}
    res, cur = [], nodes[0]
    while cur is not None:
        rnd = cur["random"]
        res.append([cur["val"], index[id(rnd)] if rnd is not None else None])
        cur = cur["next"]
    return res
