def _build_tree(a):
    """LeetCode level-order array -> root node dict {'v','l','r'} (None = empty)."""
    from collections import deque
    if not a or a[0] is None:
        return None
    root = {'v': a[0], 'l': None, 'r': None}
    q, i = deque([root]), 1
    while q and i < len(a):
        cur = q.popleft()
        if i < len(a):
            if a[i] is not None:
                cur['l'] = {'v': a[i], 'l': None, 'r': None}
                q.append(cur['l'])
            i += 1
        if i < len(a):
            if a[i] is not None:
                cur['r'] = {'v': a[i], 'l': None, 'r': None}
                q.append(cur['r'])
            i += 1
    return root

def bstIterator(operations):
    it = {"stack": []}
    def push_left(node):
        while node is not None:
            it["stack"].append(node)
            node = node['l']
    res = []
    for op in operations:
        name = op[0]
        if name == "BSTIterator":
            it["stack"] = []
            push_left(_build_tree(op[1]))
            res.append(None)
        elif name == "hasNext":
            res.append(len(it["stack"]) > 0)
        elif name == "next":
            node = it["stack"].pop()
            push_left(node['r'])
            res.append(node['v'])
        else:
            raise ValueError(name)
    return res
