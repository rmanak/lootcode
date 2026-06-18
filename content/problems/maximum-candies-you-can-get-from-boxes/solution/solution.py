def maxCandies(status, candies, keys, containedBoxes, initialBoxes):
    from collections import deque
    n = len(status)
    have_box = [False] * n
    have_key = [False] * n
    opened = [False] * n
    queue = deque()

    def try_open(b):
        if have_box[b] and not opened[b] and (status[b] == 1 or have_key[b]):
            opened[b] = True
            queue.append(b)

    for b in initialBoxes:
        have_box[b] = True
    for b in initialBoxes:
        try_open(b)
    total = 0
    while queue:
        b = queue.popleft()
        total += candies[b]
        for k in keys[b]:
            if not have_key[k]:
                have_key[k] = True
                try_open(k)
        for nb in containedBoxes[b]:
            if not have_box[nb]:
                have_box[nb] = True
                try_open(nb)
    return total
