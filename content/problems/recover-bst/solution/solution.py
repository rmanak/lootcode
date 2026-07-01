def recoverTree(root):
    nodes = []

    def inorder(n):
        if n is None:
            return
        inorder(n.left)
        nodes.append(n)
        inorder(n.right)

    inorder(root)
    first = second = prev = None
    for n in nodes:
        if prev and prev.value > n.value:
            if first is None:
                first = prev
            second = n
        prev = n
    if first and second:
        first.value, second.value = second.value, first.value
    return root
