def findFrequentTreeSum(root):
    from collections import Counter

    if root is None:
        return []
    counts = Counter()

    def dfs(node):
        if node is None:
            return 0
        s = node.value + dfs(node.left) + dfs(node.right)
        counts[s] += 1
        return s

    dfs(root)
    mx = max(counts.values())
    return [s for s, c in counts.items() if c == mx]
