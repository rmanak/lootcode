def countSmaller(nums):
    srt = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(srt)}
    m = len(srt)
    bit = [0] * (m + 1)

    def update(i):
        while i <= m:
            bit[i] += 1
            i += i & (-i)

    def query(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    res = [0] * len(nums)
    for idx in range(len(nums) - 1, -1, -1):
        r = rank[nums[idx]]
        res[idx] = query(r - 1)
        update(r)
    return res
