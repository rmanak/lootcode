def queryString(S, N):
    for i in range(N, N // 2, -1):
        if bin(i)[2:] not in S:
            return False
    return True
