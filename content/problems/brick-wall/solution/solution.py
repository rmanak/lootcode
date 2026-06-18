def leastBricks(wall):
    from collections import defaultdict
    edges = defaultdict(int)
    for row in wall:
        pos = 0
        for b in row[:-1]:
            pos += b
            edges[pos] += 1
    return len(wall) - (max(edges.values()) if edges else 0)
