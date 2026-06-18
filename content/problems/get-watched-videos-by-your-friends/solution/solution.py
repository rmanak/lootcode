def watchedVideosByFriends(watchedVideos, friends, id, level):
    from collections import deque, Counter
    n = len(friends)
    visited = [False] * n
    visited[id] = True
    q = deque([id])
    for _ in range(level):
        for _ in range(len(q)):
            u = q.popleft()
            for v in friends[u]:
                if not visited[v]:
                    visited[v] = True
                    q.append(v)
    cnt = Counter()
    for u in q:
        for vid in watchedVideos[u]:
            cnt[vid] += 1
    return sorted(cnt, key=lambda x: (cnt[x], x))
