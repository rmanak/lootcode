def maxWidthRamp(A):
    stack = []
    for i, x in enumerate(A):
        if not stack or A[stack[-1]] > x:
            stack.append(i)
    best = 0
    for j in range(len(A) - 1, -1, -1):
        while stack and A[stack[-1]] <= A[j]:
            best = max(best, j - stack.pop())
    return best
