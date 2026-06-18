def unhappyFriends(n, preferences, pairs):
    rank = [[0] * n for _ in range(n)]
    for x in range(n):
        for idx, y in enumerate(preferences[x]):
            rank[x][y] = idx
    partner = [0] * n
    for a, b in pairs:
        partner[a] = b
        partner[b] = a
    unhappy = 0
    for x in range(n):
        y = partner[x]
        for u in preferences[x]:
            if u == y:
                break
            v = partner[u]
            if rank[u][x] < rank[u][v]:
                unhappy += 1
                break
    return unhappy
