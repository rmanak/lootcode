def kthSmallest(root, k):
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

    stack, node = [], build(root)
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val
        node = node.right
