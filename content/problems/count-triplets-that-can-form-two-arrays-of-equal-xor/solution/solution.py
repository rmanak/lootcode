def countTriplets(arr):
    n = len(arr)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] ^ arr[i]
    res = 0
    for l in range(n + 1):
        for r in range(l + 1, n + 1):
            if prefix[l] == prefix[r]:
                res += r - l - 1
    return res
