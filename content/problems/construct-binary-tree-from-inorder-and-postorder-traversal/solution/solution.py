def buildTree(inorder, postorder):
    from collections import deque
    idx = {v: i for i, v in enumerate(inorder)}
    post = postorder[:]
    def build(lo, hi):
        if lo > hi:
            return None
        val = post.pop()
        node = {'v': val, 'l': None, 'r': None}
        mid = idx[val]
        node['r'] = build(mid + 1, hi)
        node['l'] = build(lo, mid - 1)
        return node
    root = build(0, len(inorder) - 1)
    res, q = [], deque([root])
    while q:
        node = q.popleft()
        if node is None:
            res.append(None)
            continue
        res.append(node['v'])
        q.append(node['l'])
        q.append(node['r'])
    while res and res[-1] is None:
        res.pop()
    return res
