def alienOrder(words):
    import heapq
    from collections import defaultdict
    chars = set("".join(words))
    adj = defaultdict(set)
    indeg = {c: 0 for c in chars}
    for w1, w2 in zip(words, words[1:]):
        found = False
        for k in range(min(len(w1), len(w2))):
            if w1[k] != w2[k]:
                if w2[k] not in adj[w1[k]]:
                    adj[w1[k]].add(w2[k])
                    indeg[w2[k]] += 1
                found = True
                break
        if not found and len(w1) > len(w2):
            return ""
    heap = [c for c in chars if indeg[c] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        c = heapq.heappop(heap)
        order.append(c)
        for nb in sorted(adj[c]):
            indeg[nb] -= 1
            if indeg[nb] == 0:
                heapq.heappush(heap, nb)
    return "".join(order) if len(order) == len(chars) else ""
