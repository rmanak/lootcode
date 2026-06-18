def maximalRectangle(matrix):
    if not matrix or not matrix[0]:
        return 0
    n = len(matrix[0])
    heights = [0] * n
    best = 0
    for row in matrix:
        for c in range(n):
            heights[c] = heights[c] + 1 if row[c] == 1 else 0
        stack = []
        for i in range(n + 1):
            h = heights[i] if i < n else 0
            while stack and heights[stack[-1]] >= h:
                ht = heights[stack.pop()]
                w = i if not stack else i - stack[-1] - 1
                best = max(best, ht * w)
            stack.append(i)
    return best
