def isSubtree(root, subRoot):
    class N:
        __slots__ = ("v", "l", "r")

        def __init__(self, v):
            self.v, self.l, self.r = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        node = N(arr[0])
        q, i = [node], 1
        while q and i < len(arr):
            cur = q.pop(0)
            if i < len(arr):
                v = arr[i]
                i += 1
                if v is not None:
                    cur.l = N(v)
                    q.append(cur.l)
            if i < len(arr):
                v = arr[i]
                i += 1
                if v is not None:
                    cur.r = N(v)
                    q.append(cur.r)
        return node

    def same(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.v == b.v and same(a.l, b.l) and same(a.r, b.r)

    def dfs(node):
        if node is None:
            return False
        if same(node, sub):
            return True
        return dfs(node.l) or dfs(node.r)

    sub = build(subRoot)
    return dfs(build(root))
