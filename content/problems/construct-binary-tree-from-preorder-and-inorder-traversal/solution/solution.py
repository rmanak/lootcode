def buildTree(preorder, inorder):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    index = {v: i for i, v in enumerate(inorder)}
    ptr = [0]

    def construct(lo, hi):
        if lo > hi:
            return None
        val = preorder[ptr[0]]
        ptr[0] += 1
        node = Node(val)
        mid = index[val]
        node.left = construct(lo, mid - 1)
        node.right = construct(mid + 1, hi)
        return node

    def serialize(node):
        out, q = [], [node]
        while q:
            cur = q.pop(0)
            if cur is None:
                out.append(None)
                continue
            out.append(cur.val); q.append(cur.left); q.append(cur.right)
        while out and out[-1] is None:
            out.pop()
        return out

    return serialize(construct(0, len(inorder) - 1))
