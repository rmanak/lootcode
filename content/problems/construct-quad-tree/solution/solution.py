def construct(grid):
    from collections import deque
    n = len(grid)
    def build(r, c, size):
        first = grid[r][c]
        if all(grid[r + i][c + j] == first
               for i in range(size) for j in range(size)):
            return {"leaf": True, "val": first, "ch": None}
        h = size // 2
        return {"leaf": False, "val": 1, "ch": [
            build(r, c, h), build(r, c + h, h),
            build(r + h, c, h), build(r + h, c + h, h)]}
    root = build(0, 0, n)
    res, q = [], deque([root])
    while q:
        node = q.popleft()
        if node is None:
            res.append(None)
            continue
        res.append([1 if node["leaf"] else 0, 1 if node["val"] else 0])
        if node["leaf"]:
            q.extend([None, None, None, None])
        else:
            q.extend(node["ch"])
    while res and res[-1] is None:
        res.pop()
    return res
