class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def _find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        self.parent[self._find(a)] = self._find(b)

    def connected(self, a, b):
        return self._find(a) == self._find(b)
