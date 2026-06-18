def catMouseGame(graph):
    n = len(graph)
    DRAW, MOUSE, CAT = 0, 1, 2
    color = [[[DRAW] * 2 for _ in range(n)] for _ in range(n)]
    degree = [[[0] * 2 for _ in range(n)] for _ in range(n)]
    for m in range(n):
        for c in range(n):
            degree[m][c][0] = len(graph[m])
            degree[m][c][1] = len(graph[c])
            for x in graph[c]:
                if x == 0:
                    degree[m][c][1] -= 1

    from collections import deque
    q = deque()
    for c in range(n):
        for t in range(2):
            color[0][c][t] = MOUSE
            q.append((0, c, t, MOUSE))
            if c > 0:
                color[c][c][t] = CAT
                q.append((c, c, t, CAT))

    def parents(m, c, t):
        if t == 0:
            for x in graph[c]:
                if x != 0:
                    yield (m, x, 1)
        else:
            for x in graph[m]:
                yield (x, c, 0)

    while q:
        m, c, t, result = q.popleft()
        for pm, pc, pt in parents(m, c, t):
            if color[pm][pc][pt] != DRAW:
                continue
            mover = MOUSE if pt == 0 else CAT
            if result == mover:
                color[pm][pc][pt] = result
                q.append((pm, pc, pt, result))
            else:
                degree[pm][pc][pt] -= 1
                if degree[pm][pc][pt] == 0:
                    color[pm][pc][pt] = result
                    q.append((pm, pc, pt, result))
    return color[1][2][0]
