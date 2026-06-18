def arrayNesting(A):
    seen = [False] * len(A)
    best = 0
    for i in range(len(A)):
        if not seen[i]:
            cnt = 0
            j = i
            while not seen[j]:
                seen[j] = True
                j = A[j]
                cnt += 1
            best = max(best, cnt)
    return best
