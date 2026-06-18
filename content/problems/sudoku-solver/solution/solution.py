def solveSudoku(board):
    grid = [list(row) for row in board]
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empties = []
    for i in range(9):
        for j in range(9):
            c = grid[i][j]
            if c == '.':
                empties.append((i, j))
            else:
                rows[i].add(c); cols[j].add(c); boxes[(i // 3) * 3 + j // 3].add(c)

    def bt(k):
        if k == len(empties):
            return True
        i, j = empties[k]
        b = (i // 3) * 3 + j // 3
        for d in "123456789":
            if d not in rows[i] and d not in cols[j] and d not in boxes[b]:
                grid[i][j] = d
                rows[i].add(d); cols[j].add(d); boxes[b].add(d)
                if bt(k + 1):
                    return True
                grid[i][j] = '.'
                rows[i].discard(d); cols[j].discard(d); boxes[b].discard(d)
        return False

    bt(0)
    return ["".join(row) for row in grid]
