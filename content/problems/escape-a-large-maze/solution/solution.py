def isEscapePossible(blocked, source, target):
    if not blocked:
        return True
    from collections import deque
    block = set(map(tuple, blocked))
    B = len(blocked)
    limit = B * (B - 1) // 2
    M = 10 ** 6

    def bfs(s, t):
        s, t = tuple(s), tuple(t)
        seen = {s}
        q = deque([s])
        while q:
            if len(seen) > limit:
                return True
            x, y = q.popleft()
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < M and 0 <= ny < M and (nx, ny) not in block and (nx, ny) not in seen:
                    if (nx, ny) == t:
                        return True
                    seen.add((nx, ny))
                    q.append((nx, ny))
        return False

    return bfs(source, target) and bfs(target, source)
