def spiralOrder(matrix):
    res = []
    if not matrix or not matrix[0]:
        return res
    top, bot = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bot and left <= right:
        for c in range(left, right + 1):
            res.append(matrix[top][c])
        top += 1
        for r in range(top, bot + 1):
            res.append(matrix[r][right])
        right -= 1
        if top <= bot:
            for c in range(right, left - 1, -1):
                res.append(matrix[bot][c])
            bot -= 1
        if left <= right:
            for r in range(bot, top - 1, -1):
                res.append(matrix[r][left])
            left += 1
    return res
