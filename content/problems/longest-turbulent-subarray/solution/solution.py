def maxTurbulenceSize(A):
    n = len(A)
    best = 1
    up = down = 1
    for i in range(1, n):
        if A[i] > A[i - 1]:
            up, down = down + 1, 1
        elif A[i] < A[i - 1]:
            down, up = up + 1, 1
        else:
            up = down = 1
        best = max(best, up, down)
    return best
