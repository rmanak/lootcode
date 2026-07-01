def isSymmetric(root):
    def mirror(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.value == b.value and mirror(a.left, b.right) and mirror(a.right, b.left)

    return mirror(root.left, root.right) if root else True
