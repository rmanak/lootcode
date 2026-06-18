def maxPathSum(root):
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

    best = [float("-inf")]

    def gain(n):
        if n is None:
            return 0
        left = max(gain(n.left), 0)
        right = max(gain(n.right), 0)
        best[0] = max(best[0], n.val + left + right)
        return n.val + max(left, right)

    gain(build(root))
    return best[0]
