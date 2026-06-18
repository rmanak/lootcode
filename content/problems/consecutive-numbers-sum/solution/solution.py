def consecutiveNumbersSum(N):
    count = 0
    k = 1
    while k * (k + 1) // 2 <= N:
        if (N - k * (k + 1) // 2) % k == 0:
            count += 1
        k += 1
    return count
