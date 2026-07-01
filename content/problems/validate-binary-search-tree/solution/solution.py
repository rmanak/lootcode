def isValidBST(root):
    def check(node, lo, hi):
        if node is None:
            return True
        if not (lo < node.value < hi):
            return False
        return check(node.left, lo, node.value) and check(node.right, node.value, hi)

    return check(root, float("-inf"), float("inf"))
