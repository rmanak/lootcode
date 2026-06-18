def findKthBit(n, k):
    def helper(n, k):
        if n == 1:
            return '0'
        length = (1 << n) - 1
        mid = (length // 2) + 1
        if k == mid:
            return '1'
        if k < mid:
            return helper(n - 1, k)
        return '1' if helper(n - 1, length + 1 - k) == '0' else '0'
    return helper(n, k)
