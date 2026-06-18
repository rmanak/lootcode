def leastInterval(tasks, n):
    from collections import Counter
    counts = Counter(tasks)
    mx = max(counts.values())
    num_max = sum(1 for v in counts.values() if v == mx)
    return max(len(tasks), (mx - 1) * (n + 1) + num_max)
