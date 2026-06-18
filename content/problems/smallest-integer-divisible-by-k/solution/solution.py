def smallestRepunitDivByK(K):
    if K % 2 == 0 or K % 5 == 0:
        return -1
    rem = 0
    for length in range(1, K + 1):
        rem = (rem * 10 + 1) % K
        if rem == 0:
            return length
    return -1
