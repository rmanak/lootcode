def minCameraCover(root):
    cameras = [0]

    # 0 = not covered, 1 = covered without a camera, 2 = has a camera
    def dfs(node):
        if node is None:
            return 1
        l = dfs(node.left)
        r = dfs(node.right)
        if l == 0 or r == 0:
            cameras[0] += 1
            return 2
        if l == 2 or r == 2:
            return 1
        return 0

    if dfs(root) == 0:
        cameras[0] += 1
    return cameras[0]
