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

def sumNumbers(root):
    r = _build_tree(root)
    total = 0
    def dfs(node, cur):
        nonlocal total
        if node is None:
            return
        cur = cur * 10 + node['v']
        if node['l'] is None and node['r'] is None:
            total += cur
            return
        dfs(node['l'], cur)
        dfs(node['r'], cur)
    dfs(r, 0)
    return total
