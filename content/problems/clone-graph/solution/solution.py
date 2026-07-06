def cloneGraph(adjList):
    n = len(adjList)
    if n == 0:
        return []
    clone = {i: {"val": i, "nb": []} for i in range(1, n + 1)}
    for i in range(1, n + 1):
        for nb in adjList[i - 1]:
            clone[i]["nb"].append(clone[nb])
    return [[node["val"] for node in clone[i]["nb"]] for i in range(1, n + 1)]
