def lowestCommonAncestor(root, p, q):
    node = root
    while node:
        if p < node.value and q < node.value:
            node = node.left
        elif p > node.value and q > node.value:
            node = node.right
        else:
            return node.value
