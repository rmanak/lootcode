def crawl(startUrl, graph):
    from collections import deque

    def host(u):
        return u[7:].split("/")[0]

    h = host(startUrl)
    seen = {startUrl}
    q = deque([startUrl])
    while q:
        u = q.popleft()
        for v in graph.get(u, []):
            if v not in seen and host(v) == h:
                seen.add(v)
                q.append(v)
    return sorted(seen)
