def minCameraCover(root):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
    while q and i < n:
        cur = q.popleft()
        if i < n:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; left[cur] = nid; q.append(nid); nid += 1
        if i < n:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; right[cur] = nid; q.append(nid); nid += 1
    cameras = [0]

    def dfs(node):
        if node is None:
            return 1  # covered, no camera
        l = dfs(left.get(node))
        r = dfs(right.get(node))
        if l == 0 or r == 0:
            cameras[0] += 1
            return 2  # has camera
        if l == 2 or r == 2:
            return 1  # covered by a child's camera
        return 0      # not covered

    if dfs(0) == 0:
        cameras[0] += 1
    return cameras[0]
