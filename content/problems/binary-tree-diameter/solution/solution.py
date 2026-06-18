def diameterOfBinaryTree(root):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        q, i = [head], 1
        while q and i < len(arr):
            cur = q.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); q.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); q.append(cur.right)
        return head

    best = [0]

    def height(n):
        if n is None:
            return 0
        lh = height(n.left)
        rh = height(n.right)
        best[0] = max(best[0], lh + rh)
        return 1 + max(lh, rh)

    height(build(root))
    return best[0]
