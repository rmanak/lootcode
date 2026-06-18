def largestComponentSize(nums):
    from collections import Counter
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    def primes(x):
        ps = []
        d = 2
        while d * d <= x:
            if x % d == 0:
                ps.append(d)
                while x % d == 0:
                    x //= d
            d += 1
        if x > 1:
            ps.append(x)
        return ps

    for v in nums:
        for p in primes(v):
            union(v, ('p', p))
    cnt = Counter(find(v) for v in nums)
    return max(cnt.values()) if cnt else 0
