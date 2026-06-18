def lowestCommonAncestor(root, p, q):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        qq, i = [head], 1
        while qq and i < len(arr):
            cur = qq.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); qq.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); qq.append(cur.right)
        return head

    def lca(n):
        if n is None or n.val == p or n.val == q:
            return n
        left = lca(n.left)
        right = lca(n.right)
        if left and right:
            return n
        return left or right

    return lca(build(root)).val
