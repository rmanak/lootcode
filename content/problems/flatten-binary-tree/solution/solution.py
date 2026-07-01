def flatten(root):
    order = []

    def pre(n):
        if n is None:
            return
        order.append(n)
        pre(n.left)
        pre(n.right)

    pre(root)
    for i, n in enumerate(order):
        n.left = None
        n.right = order[i + 1] if i + 1 < len(order) else None
    return root
