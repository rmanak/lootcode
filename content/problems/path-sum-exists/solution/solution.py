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


def hasPathSum(root, targetSum):
    r = _build(root)

    def dfs(n, rem):
        if not n:
            return False
        rem -= n.v
        if not n.l and not n.r:
            return rem == 0
        return dfs(n.l, rem) or dfs(n.r, rem)

    return dfs(r, targetSum) if r else False
