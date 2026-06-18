def getPermutation(n, k):
    import math
    nums = list(range(1, n + 1))
    k -= 1
    res = []
    for i in range(n, 0, -1):
        f = math.factorial(i - 1)
        idx = k // f
        res.append(str(nums.pop(idx)))
        k %= f
    return "".join(res)
