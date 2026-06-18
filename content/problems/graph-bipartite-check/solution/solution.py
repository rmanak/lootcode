def isBipartite(graph):
    color = [0] * len(graph)
    for start in range(len(graph)):
        if color[start] != 0:
            continue
        color[start] = 1
        stack = [start]
        while stack:
            u = stack.pop()
            for v in graph[u]:
                if color[v] == 0:
                    color[v] = -color[u]
                    stack.append(v)
                elif color[v] == color[u]:
                    return False
    return True
