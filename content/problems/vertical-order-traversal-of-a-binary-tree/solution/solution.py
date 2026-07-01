def verticalTraversal(root):
    from collections import defaultdict

    nodes = []

    def dfs(node, x, y):
        if node is None:
            return
        nodes.append((x, y, node.value))
        dfs(node.left, x - 1, y + 1)
        dfs(node.right, x + 1, y + 1)

    dfs(root, 0, 0)
    cols = defaultdict(list)
    for x, y, v in nodes:
        cols[x].append((y, v))
    return [[v for _, v in sorted(cols[x])] for x in sorted(cols)]
