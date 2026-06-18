def findCircleNum(M):
    n = len(M)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if M[i][j] == 1:
                parent[find(i)] = find(j)
    return len({find(i) for i in range(n)})
