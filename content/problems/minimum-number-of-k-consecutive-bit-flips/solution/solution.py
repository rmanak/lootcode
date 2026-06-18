def minKBitFlips(A, K):
    n = len(A)
    diff = [0] * (n + 1)
    flip = 0
    res = 0
    for i in range(n):
        flip += diff[i]
        if (A[i] + flip) % 2 == 0:
            if i + K > n:
                return -1
            res += 1
            flip += 1
            diff[i + K] -= 1
    return res
