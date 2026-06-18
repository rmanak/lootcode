def isPrintable(targetGrid):
    m, n = len(targetGrid), len(targetGrid[0])
    colors = set(v for row in targetGrid for v in row)
    box = {}
    for c in colors:
        rs = [i for i in range(m) for j in range(n) if targetGrid[i][j] == c]
        cs = [j for i in range(m) for j in range(n) if targetGrid[i][j] == c]
        box[c] = (min(rs), max(rs), min(cs), max(cs))
    graph = {c: set() for c in colors}
    for c in colors:
        r1, r2, c1, c2 = box[c]
        for i in range(r1, r2 + 1):
            for j in range(c1, c2 + 1):
                if targetGrid[i][j] != c:
                    graph[c].add(targetGrid[i][j])
    state = {}

    def dfs(c):
        state[c] = 1
        for nb in graph[c]:
            if state.get(nb, 0) == 1:
                return False
            if state.get(nb, 0) == 0 and not dfs(nb):
                return False
        state[c] = 2
        return True

    return all(dfs(c) for c in colors if state.get(c, 0) == 0)
