def isSubPath(head, root):
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

    def match(node, k):
        if k == len(head):
            return True
        if node is None or val[node] != head[k]:
            return False
        return match(left.get(node), k + 1) or match(right.get(node), k + 1)

    return any(match(nd, 0) for nd in val)
