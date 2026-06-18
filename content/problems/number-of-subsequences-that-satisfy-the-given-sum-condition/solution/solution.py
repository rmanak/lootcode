def numSubseq(nums, target):
    MOD = 10 ** 9 + 7
    nums.sort()
    n = len(nums)
    pow2 = [1] * n
    for i in range(1, n):
        pow2[i] = pow2[i - 1] * 2 % MOD
    l, r = 0, n - 1
    res = 0
    while l <= r:
        if nums[l] + nums[r] <= target:
            res = (res + pow2[r - l]) % MOD
            l += 1
        else:
            r -= 1
    return res % MOD
