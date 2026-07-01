def isSubPath(head, root):
    def match(node, k):
        if k == len(head):
            return True
        if node is None or node.value != head[k]:
            return False
        return match(node.left, k + 1) or match(node.right, k + 1)

    def starts(node):
        if node is None:
            return False
        return match(node, 0) or starts(node.left) or starts(node.right)

    return starts(root)
