def validateBinaryTreeNodes(n, leftChild, rightChild):
    indeg = [0] * n
    for i in range(n):
        for c in (leftChild[i], rightChild[i]):
            if c != -1:
                indeg[c] += 1
                if indeg[c] > 1:
                    return False
    roots = [i for i in range(n) if indeg[i] == 0]
    if len(roots) != 1:
        return False
    from collections import deque
    seen = {roots[0]}
    q = deque([roots[0]])
    while q:
        node = q.popleft()
        for c in (leftChild[node], rightChild[node]):
            if c != -1:
                if c in seen:
                    return False
                seen.add(c)
                q.append(c)
    return len(seen) == n
