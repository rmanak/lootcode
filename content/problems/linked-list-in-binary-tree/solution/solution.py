def isSubPath(head, root):
    def match(tree_node, list_node):
        if list_node is None:
            return True
        if tree_node is None or tree_node.value != list_node.val:
            return False
        return (match(tree_node.left, list_node.next)
                or match(tree_node.right, list_node.next))

    def starts(tree_node):
        if tree_node is None:
            return False
        return (match(tree_node, head)
                or starts(tree_node.left)
                or starts(tree_node.right))

    return starts(root)
