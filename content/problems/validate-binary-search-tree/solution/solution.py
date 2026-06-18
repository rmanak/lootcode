def isValidBST(root):
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

    def check(node, lo, hi):
        if node is None:
            return True
        if not (lo < node.val < hi):
            return False
        return check(node.left, lo, node.val) and check(node.right, node.val, hi)

    return check(build(root), float("-inf"), float("inf"))
