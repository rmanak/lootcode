def insertIntoMaxTree(root, val):
    from collections import deque

    def arr_to_nested(arr):
        if not arr or arr[0] is None:
            return None
        node0 = [arr[0], None, None]
        q = deque([node0]); i, n = 1, len(arr)
        while q and i < n:
            nd = q.popleft()
            if i < n:
                v = arr[i]; i += 1
                if v is not None:
                    nd[1] = [v, None, None]; q.append(nd[1])
            if i < n:
                v = arr[i]; i += 1
                if v is not None:
                    nd[2] = [v, None, None]; q.append(nd[2])
        return node0

    def insert(nd):
        if nd is None or val > nd[0]:
            return [val, nd, None]
        nd[2] = insert(nd[2])
        return nd

    troot = insert(arr_to_nested(root))
    if troot is None:
        return []
    out = [troot[0]]; q = deque([troot])
    while q:
        nd = q.popleft()
        for ch in (nd[1], nd[2]):
            if ch is None:
                out.append(None)
            else:
                out.append(ch[0]); q.append(ch)
    while out and out[-1] is None:
        out.pop()
    return out
