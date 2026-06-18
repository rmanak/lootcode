def countNegatives(grid):
    n = len(grid[0])
    count = 0
    c = n - 1
    for row in grid:
        while c >= 0 and row[c] < 0:
            c -= 1
        count += n - 1 - c
    return count
