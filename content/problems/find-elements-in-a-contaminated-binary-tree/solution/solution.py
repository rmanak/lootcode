def findElements(root, queries):
    from collections import deque
    present = set()
    if root and root[0] is not None:
        assigned = {0: 0}
        present.add(0)
        q = deque([0]); nid, i, n = 1, 1, len(root)
        while q and i < n:
            cur = q.popleft()
            if i < n:
                v = root[i]; i += 1
                if v is not None:
                    cv = 2 * assigned[cur] + 1
                    assigned[nid] = cv; present.add(cv); q.append(nid); nid += 1
            if i < n:
                v = root[i]; i += 1
                if v is not None:
                    cv = 2 * assigned[cur] + 2
                    assigned[nid] = cv; present.add(cv); q.append(nid); nid += 1
    return [qv in present for qv in queries]
