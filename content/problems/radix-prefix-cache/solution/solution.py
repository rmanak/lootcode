class _Node:
    __slots__ = ("children", "end")

    def __init__(self):
        self.children = {}        # first token -> [edge tokens (list), child node]
        self.end = False


class RadixCache:
    def __init__(self):
        self.root = _Node()

    def insert(self, sequence):
        node, i = self.root, 0
        while i < len(sequence):
            entry = node.children.get(sequence[i])
            if entry is None:                                  # new leaf edge
                leaf = _Node()
                leaf.end = True
                node.children[sequence[i]] = [list(sequence[i:]), leaf]
                return
            edge, child = entry
            k = 0
            while k < len(edge) and i + k < len(sequence) and edge[k] == sequence[i + k]:
                k += 1
            if k < len(edge):                                  # split the edge after k tokens
                mid = _Node()
                mid.children[edge[k]] = [edge[k:], child]
                entry[0], entry[1] = edge[:k], mid
                child = mid
            node, i = child, i + k
        node.end = True

    def _walk(self, sequence):
        """Yield (tokens consumed, node) for every node whose full path is a prefix of sequence."""
        node, i = self.root, 0
        while True:
            yield i, node
            if i == len(sequence) or sequence[i] not in node.children:
                return
            edge, child = node.children[sequence[i]]
            if sequence[i:i + len(edge)] != edge:
                return
            node, i = child, i + len(edge)

    def search(self, sequence):
        for i, node in self._walk(sequence):
            if i == len(sequence):
                return node.end and i > 0
        return False

    def prefixMatch(self, sequence):
        best = 0
        for i, node in self._walk(sequence):
            if node.end:
                best = i
        return list(sequence[:best])

    def getAllSequences(self):
        out = []

        def dfs(node, path):
            if node.end:
                out.append(list(path))
            for first in sorted(node.children):
                edge, child = node.children[first]
                dfs(child, path + edge)
        dfs(self.root, [])
        return out

    def structure(self):
        out = []

        def dfs(node, depth):
            for first in sorted(node.children):
                edge, child = node.children[first]
                out.append([depth, list(edge)])
                dfs(child, depth + 1)
        dfs(self.root, 1)
        return out
