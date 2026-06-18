def isSameTree(p, q):
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

    def same(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)

    return same(build(p), build(q))
