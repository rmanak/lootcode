def isSubtree(root, subRoot):
    def same(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.value == b.value and same(a.left, b.left) and same(a.right, b.right)

    def dfs(node):
        if node is None:
            return False
        if same(node, subRoot):
            return True
        return dfs(node.left) or dfs(node.right)

    return dfs(root)
