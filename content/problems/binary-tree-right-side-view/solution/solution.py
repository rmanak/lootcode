class _N:
    __slots__ = ("v", "l", "r")

    def __init__(self, v):
        self.v, self.l, self.r = v, None, None


def _build(arr):
    if not arr or arr[0] is None:
        return None
    root = _N(arr[0])
    q, i = [root], 1
    while q and i < len(arr):
        cur = q.pop(0)
        if i < len(arr):
            x = arr[i]; i += 1
            if x is not None:
                cur.l = _N(x); q.append(cur.l)
        if i < len(arr):
            x = arr[i]; i += 1
            if x is not None:
                cur.r = _N(x); q.append(cur.r)
    return root


def _ser(root):
    out, q = [], [root]
    while q:
        node = q.pop(0)
        if node is None:
            out.append(None)
            continue
        out.append(node.v)
        q.append(node.l)
        q.append(node.r)
    while out and out[-1] is None:
        out.pop()
    return out


def rightSideView(root):
    from collections import deque
    r = _build(root)
    if not r:
        return []
    res = []
    q = deque([r])
    while q:
        n = len(q)
        for i in range(n):
            node = q.popleft()
            if i == n - 1:
                res.append(node.v)
            if node.l:
                q.append(node.l)
            if node.r:
                q.append(node.r)
    return res
