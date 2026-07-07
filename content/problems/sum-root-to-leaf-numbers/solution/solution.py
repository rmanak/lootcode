def sumNumbers(root):
    total = 0
    def dfs(node, cur):
        nonlocal total
        if node is None:
            return
        cur = cur * 10 + node.value
        if node.left is None and node.right is None:
            total += cur
            return
        dfs(node.left, cur)
        dfs(node.right, cur)
    dfs(root, 0)
    return total
