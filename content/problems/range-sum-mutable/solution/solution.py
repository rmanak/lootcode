def rangeSum(nums, operations):
    arr = list(nums)
    n = len(arr)
    bit = [0] * (n + 1)

    def add(i, delta):
        i += 1
        while i <= n:
            bit[i] += delta
            i += i & (-i)

    def prefix(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    for i, v in enumerate(arr):
        add(i, v)
    out = []
    for op in operations:
        if op[0] == "query":
            _, l, r = op
            out.append(prefix(r + 1) - prefix(l))
        else:
            _, i, val = op
            add(i, val - arr[i])
            arr[i] = val
            out.append(None)
    return out
