def numMagicSquaresInside(grid):
    m = len(grid)
    n = len(grid[0])

    def is_magic(r, c):
        nums = [grid[r + i][c + j] for i in range(3) for j in range(3)]
        if sorted(nums) != list(range(1, 10)):
            return False
        s = grid[r][c] + grid[r][c + 1] + grid[r][c + 2]
        for i in range(3):
            if sum(grid[r + i][c + j] for j in range(3)) != s:
                return False
            if sum(grid[r + j][c + i] for j in range(3)) != s:
                return False
        if grid[r][c] + grid[r + 1][c + 1] + grid[r + 2][c + 2] != s:
            return False
        if grid[r][c + 2] + grid[r + 1][c + 1] + grid[r + 2][c] != s:
            return False
        return True

    count = 0
    for r in range(m - 2):
        for c in range(n - 2):
            if is_magic(r, c):
                count += 1
    return count
