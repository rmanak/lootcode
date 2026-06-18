def prevPermOpt1(A):
    A = A[:]
    n = len(A)
    for i in range(n - 2, -1, -1):
        if A[i] > A[i + 1]:
            j = -1
            for k in range(i + 1, n):
                if A[k] < A[i] and (j == -1 or A[k] > A[j]):
                    j = k
            A[i], A[j] = A[j], A[i]
            return A
    return A
