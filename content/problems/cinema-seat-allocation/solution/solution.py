def maxNumberOfFamilies(n, reservedSeats):
    from collections import defaultdict
    rows = defaultdict(set)
    for r, c in reservedSeats:
        rows[r].add(c)
    total = (n - len(rows)) * 2
    for occ in rows.values():
        left = not (occ & {2, 3, 4, 5})
        mid = not (occ & {4, 5, 6, 7})
        right = not (occ & {6, 7, 8, 9})
        if left and right:
            total += 2
        elif left or mid or right:
            total += 1
    return total
