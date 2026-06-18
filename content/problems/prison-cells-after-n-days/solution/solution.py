def prisonAfterNDays(cells, N):
    def step(c):
        return [0] + [1 if c[i - 1] == c[i + 1] else 0 for i in range(1, 7)] + [0]

    seen = {}
    cur = cells[:]
    day = 0
    while day < N:
        key = tuple(cur)
        if key in seen:
            cycle = day - seen[key]
            for _ in range((N - day) % cycle):
                cur = step(cur)
            return cur
        seen[key] = day
        cur = step(cur)
        day += 1
    return cur
