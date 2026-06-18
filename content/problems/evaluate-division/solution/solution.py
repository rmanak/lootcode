def calcEquation(equations, values, queries):
    from collections import defaultdict
    graph = defaultdict(dict)
    for (a, b), v in zip(equations, values):
        graph[a][b] = v
        graph[b][a] = 1.0 / v

    def query(x, y):
        if x not in graph or y not in graph:
            return -1.0
        seen = {x}
        stack = [(x, 1.0)]
        while stack:
            node, prod = stack.pop()
            if node == y:
                return prod
            for nb, w in graph[node].items():
                if nb not in seen:
                    seen.add(nb)
                    stack.append((nb, prod * w))
        return -1.0

    return [round(query(x, y), 5) for x, y in queries]
