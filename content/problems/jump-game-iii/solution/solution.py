def canReach(arr, start):
    from collections import deque
    n = len(arr)
    seen = {start}
    q = deque([start])
    while q:
        i = q.popleft()
        if arr[i] == 0:
            return True
        for ni in (i + arr[i], i - arr[i]):
            if 0 <= ni < n and ni not in seen:
                seen.add(ni)
                q.append(ni)
    return False
