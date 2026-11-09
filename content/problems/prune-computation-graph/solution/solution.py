import heapq


def pruneGraph(nodes, output):
    index = {}
    for i, (name, op, inputs) in enumerate(nodes):
        if name in index:
            return [False, []]
        index[name] = i
    for name, op, inputs in nodes:
        if any(src not in index for src in inputs):
            return [False, []]
        if (op == "input") != (len(inputs) == 0):
            return [False, []]
    if output not in index:
        return [False, []]

    # Cycle check over the whole graph (Kahn's algorithm).
    n = len(nodes)
    consumers = [[] for _ in range(n)]
    indeg = [0] * n
    for i, (_, _, inputs) in enumerate(nodes):
        for src in set(inputs):
            consumers[index[src]].append(i)
            indeg[i] += 1
    remaining = list(indeg)
    stack = [i for i in range(n) if indeg[i] == 0]
    seen = 0
    while stack:
        u = stack.pop()
        seen += 1
        for v in consumers[u]:
            remaining[v] -= 1
            if remaining[v] == 0:
                stack.append(v)
    if seen < n:
        return [False, []]

    # Reverse reachability from the output.
    needed = {index[output]}
    todo = [index[output]]
    while todo:
        u = todo.pop()
        for src in nodes[u][2]:
            j = index[src]
            if j not in needed:
                needed.add(j)
                todo.append(j)

    # Kahn on the needed subgraph, earliest-listed node first.
    indeg = {i: len(set(nodes[i][2])) for i in needed}
    heap = [i for i in needed if indeg[i] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        u = heapq.heappop(heap)
        order.append(nodes[u][0])
        for v in consumers[u]:
            if v in needed:
                indeg[v] -= 1
                if indeg[v] == 0:
                    heapq.heappush(heap, v)
    return [True, order]
