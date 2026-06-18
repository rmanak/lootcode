def minJumps(arr):
    from collections import deque, defaultdict
    n = len(arr)
    if n == 1:
        return 0
    idx = defaultdict(list)
    for i, v in enumerate(arr):
        idx[v].append(i)
    visited = [False] * n
    visited[0] = True
    q = deque([(0, 0)])
    while q:
        i, steps = q.popleft()
        if i == n - 1:
            return steps
        nbrs = [i - 1, i + 1] + idx[arr[i]]
        idx[arr[i]] = []
        for j in nbrs:
            if 0 <= j < n and not visited[j]:
                visited[j] = True
                q.append((j, steps + 1))
    return -1
