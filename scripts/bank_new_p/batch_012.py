"""Batch 012 of the new_p.txt import (17 problems).

Three entries were dropped as duplicates under a different slug (see `_skips.py`):
`find-the-duplicate-number` (== `find-duplicate-number`),
`largest-component-size-by-common-factor` (== `largest-component-common-factor`),
`regular-expression-matching` (== `regex-full-match`).

`find-the-shortest-superstring` is reframed to return the LENGTH of the shortest
superstring (the string itself is "return any" — not single-answer gradable).
"""
from scripts.build_bank import add, ilist, sstr  # noqa: F401

MOD = 10 ** 9 + 7


# --------------------------- brute / reference helpers ---------------------
def _hats_brute(hats):
    from itertools import product
    c = 0
    for combo in product(*hats):
        if len(set(combo)) == len(combo):
            c += 1
    return c % MOD


def _jug_brute(x, y, z):
    from collections import deque
    start = (0, 0)
    seen = {start}
    q = deque([start])
    while q:
        a, b = q.popleft()
        if a + b == z:
            return True
        nxts = [(x, b), (a, y), (0, b), (a, 0)]
        pour = min(a, y - b)
        nxts.append((a - pour, b + pour))
        pour = min(b, x - a)
        nxts.append((a + pour, b - pour))
        for s in nxts:
            if s not in seen:
                seen.add(s)
                q.append(s)
    return False


def _uniqchar_brute(s):
    from collections import Counter
    res = 0
    n = len(s)
    for i in range(n):
        cnt = Counter()
        for j in range(i, n):
            cnt[s[j]] += 1
            res += sum(1 for v in cnt.values() if v == 1)
    return res % MOD


def _lsk_brute(s, k):
    from collections import Counter
    n = len(s)
    best = 0
    for i in range(n):
        for j in range(i, n):
            c = Counter(s[i:j + 1])
            if all(v >= k for v in c.values()):
                best = max(best, j - i + 1)
    return best


def _dish_brute(satisfaction):
    from itertools import combinations
    n = len(satisfaction)
    best = 0
    for size in range(1, n + 1):
        for comb in combinations(satisfaction, size):
            c = sorted(comb)
            best = max(best, sum((t + 1) * c[t] for t in range(size)))
    return best


def _matflip_brute(mat):
    m, n = len(mat), len(mat[0])
    cells = m * n
    best = -1
    for mask in range(1 << cells):
        g = [row[:] for row in mat]
        cnt = 0
        for k in range(cells):
            if mask >> k & 1:
                cnt += 1
                i, j = divmod(k, n)
                for di, dj in ((0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n:
                        g[ni][nj] ^= 1
        if all(v == 0 for row in g for v in row):
            if best == -1 or cnt < best:
                best = cnt
    return best


def _bus_brute(routes, source, target):
    if source == target:
        return 0
    from collections import deque
    routesets = [set(r) for r in routes]
    n = len(routes)
    start = [i for i in range(n) if source in routesets[i]]
    visited = set(start)
    q = deque((b, 1) for b in start)
    while q:
        bus, d = q.popleft()
        if target in routesets[bus]:
            return d
        for nb in range(n):
            if nb not in visited and routesets[bus] & routesets[nb]:
                visited.add(nb)
                q.append((nb, d + 1))
    return -1


def _stock4_brute(prices, k):
    from functools import lru_cache
    n = len(prices)

    @lru_cache(None)
    def dp(i, trans, holding):
        if i == n:
            return 0
        best = dp(i + 1, trans, holding)
        if holding:
            best = max(best, prices[i] + dp(i + 1, trans, False))
        elif trans > 0:
            best = max(best, -prices[i] + dp(i + 1, trans - 1, True))
        return best

    return dp(0, k, False)


def _superstr_brute(words):
    from itertools import permutations
    words = [w for w in words if not any(w != o and w in o for o in words)]
    if not words:
        return 0

    def merge(a, b):
        m = min(len(a), len(b))
        for k in range(m, 0, -1):
            if a[-k:] == b[:k]:
                return a + b[k:]
        return a + b

    best = None
    for perm in permutations(words):
        cur = perm[0]
        for w in perm[1:]:
            cur = merge(cur, w)
        if best is None or len(cur) < len(best):
            best = cur
    return len(best)


def _triangulation_brute(values):
    n = len(values)

    def rec(i, j):
        if j - i < 2:
            return 0
        best = float('inf')
        for k in range(i + 1, j):
            best = min(best, rec(i, k) + rec(k, j) + values[i] * values[k] * values[j])
        return best

    return rec(0, n - 1)


def _magical_brute(n, a, b):
    nums = sorted(set(range(a, n * a + 1, a)) | set(range(b, n * b + 1, b)))
    return nums[n - 1] % MOD


def _maxscore_brute(nums1, nums2):
    import bisect
    from functools import lru_cache
    common = set(nums1) & set(nums2)

    def nxt(arr, v):
        i = bisect.bisect_right(arr, v)
        return arr[i] if i < len(arr) else None

    @lru_cache(None)
    def best(v, which):
        arr = nums1 if which == 1 else nums2
        opt = 0
        nv = nxt(arr, v)
        if nv is not None:
            opt = max(opt, best(nv, which))
        if v in common:
            other = 2 if which == 1 else 1
            arr2 = nums1 if other == 1 else nums2
            nv2 = nxt(arr2, v)
            if nv2 is not None:
                opt = max(opt, best(nv2, other))
        return v + opt

    res = 0
    if nums1:
        res = max(res, best(nums1[0], 1))
    if nums2:
        res = max(res, best(nums2[0], 2))
    return res % MOD


def _malware_brute(graph, initial):
    n = len(graph)

    def count(removed):
        inf = [False] * n
        for s in initial:
            if s != removed:
                inf[s] = True
        changed = True
        while changed:
            changed = False
            for u in range(n):
                if u == removed or not inf[u]:
                    continue
                for v in range(n):
                    if v == removed:
                        continue
                    if graph[u][v] == 1 and not inf[v]:
                        inf[v] = True
                        changed = True
        return sum(inf)

    best, node = None, min(initial)
    for cand in sorted(initial):
        c = count(cand)
        if best is None or c < best:
            best, node = c, cand
    return node


def _ssw_brute(nums):
    n = len(nums)
    res = 0
    for mask in range(1, 1 << n):
        sub = [nums[i] for i in range(n) if mask >> i & 1]
        res += max(sub) - min(sub)
    return res % MOD


def _kthfac_brute(n, k):
    fs = [i for i in range(1, n + 1) if n % i == 0]
    return fs[k - 1] if k <= len(fs) else -1


def _vowel_brute(n):
    nexts = {'a': 'e', 'e': 'ai', 'i': 'aeou', 'o': 'iu', 'u': 'a'}
    from functools import lru_cache

    @lru_cache(None)
    def cnt(c, rem):
        if rem == 1:
            return 1
        return sum(cnt(nc, rem - 1) for nc in nexts[c])

    return sum(cnt(c, n) for c in 'aeiou') % MOD


# --------------------------- gen helpers -----------------------------------
def _hats_gen(r):
    n = r.randint(1, 4)
    return {"hats": [sorted(r.sample(range(1, 7), r.randint(1, 4))) for _ in range(n)]}


def _matflip_gen(r):
    m, n = r.randint(1, 3), r.randint(1, 3)
    return {"mat": [[r.randint(0, 1) for _ in range(n)] for _ in range(m)]}


def _bus_gen(r):
    n = r.randint(1, 4)
    routes = [sorted(r.sample(range(0, 8), r.randint(1, 4))) for _ in range(n)]
    stops = sorted({s for route in routes for s in route})
    source = r.choice(stops)
    target = r.choice(stops)
    return {"routes": routes, "source": source, "target": target}


def _stock4_gen(r):
    return {"prices": [r.randint(0, 10) for _ in range(r.randint(0, 8))], "k": r.randint(0, 4)}


def _superstr_gen(r):
    words = list({sstr(r, 1, 4, "ab") for _ in range(r.randint(1, 5))})
    return {"words": words}


def _maxscore_gen(r):
    n1 = r.randint(1, 7)
    n2 = r.randint(1, 7)
    pool = list(range(1, 16))
    return {"nums1": sorted(r.sample(pool, n1)), "nums2": sorted(r.sample(pool, n2))}


def _malware_gen(r):
    n = r.randint(2, 6)
    graph = [[0] * n for _ in range(n)]
    for i in range(n):
        graph[i][i] = 1
    for i in range(n):
        for j in range(i + 1, n):
            if r.random() < 0.4:
                graph[i][j] = graph[j][i] = 1
    k = r.randint(1, n - 1)
    initial = sorted(r.sample(range(n), k))
    return {"graph": graph, "initial": initial}


def _ip_gen(r):
    kind = r.randint(0, 2)
    if kind == 0:
        parts = [str(r.randint(0, 300)) for _ in range(r.randint(3, 5))]
        return {"IP": ".".join(parts)}
    if kind == 1:
        hexchars = "0123456789abcdefABCDEF"
        parts = ["".join(r.choice(hexchars) for _ in range(r.randint(1, 5)))
                 for _ in range(r.randint(6, 9))]
        return {"IP": ":".join(parts)}
    return {"IP": "".join(r.choice("0123456789.:abf") for _ in range(r.randint(1, 12)))}


# ===========================================================================
# 1. Number of Ways to Wear Different Hats to Each Other
# ===========================================================================
add("number-of-ways-to-wear-different-hats-to-each-other",
    "Number of Ways to Wear Different Hats to Each Other", "hard",
    ["array", "dynamic-programming", "bitmask"], "numberWays",
    [("hats", "int[][]")], "int",
    """
There are `n` people and `40` types of hats labeled `1` to `40`. `hats[i]` is the
list of hats preferred by the `i`-th person. **Return the number of ways the `n`
people can each wear a hat such that no two people wear the same hat**, modulo
`10^9 + 7`.

**Examples**
```
hats = [[3,4],[4,5],[5]]                          ->  1
hats = [[3,5,1],[3,5]]                            ->  4
hats = [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]  ->  24
```

**Constraints:** `1 <= n <= 10`, `1 <= len(hats[i]) <= 40`,
`1 <= hats[i][j] <= 40`, each `hats[i]` holds distinct integers.
""",
    """def numberWays(hats):
    MOD = 10 ** 9 + 7
    n = len(hats)
    hat_people = [[] for _ in range(41)]
    for i, hs in enumerate(hats):
        for h in hs:
            hat_people[h].append(i)
    full = (1 << n) - 1
    dp = [0] * (1 << n)
    dp[0] = 1
    for hat in range(1, 41):
        ndp = dp[:]
        for mask in range(1 << n):
            if dp[mask] == 0:
                continue
            for p in hat_people[hat]:
                if not (mask >> p) & 1:
                    nm = mask | (1 << p)
                    ndp[nm] = (ndp[nm] + dp[mask]) % MOD
        dp = ndp
    return dp[full] % MOD
""",
    visible=[{"hats": [[3, 4], [4, 5], [5]]}, {"hats": [[3, 5, 1], [3, 5]]},
             {"hats": [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]]}],
    hidden=[{"hats": [[1]]}, {"hats": [[1, 2], [1, 2]]},
            {"hats": [[1, 2, 3], [2, 3, 5, 6], [1, 3, 7, 9], [1, 8, 9], [2, 5, 7]]},
            {"hats": [[5], [5]]}],
    gen=lambda r: [_hats_gen(r) for _ in range(8)],
    brute=_hats_brute,
    checks=[({"hats": [[3, 4], [4, 5], [5]]}, 1), ({"hats": [[3, 5, 1], [3, 5]]}, 4),
            ({"hats": [[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]]}, 24),
            ({"hats": [[1, 2, 3], [2, 3, 5, 6], [1, 3, 7, 9], [1, 8, 9], [2, 5, 7]]}, 111),
            ({"hats": [[5], [5]]}, 0)],
    source="new_p")


# ===========================================================================
# 2. Water and Jug Problem
# ===========================================================================
add("water-and-jug-problem", "Water and Jug Problem", "medium",
    ["math", "depth-first-search", "breadth-first-search"], "canMeasureWater",
    [("x", "int"), ("y", "int"), ("z", "int")], "bool",
    """
You have two jugs with capacities `x` and `y` litres and an infinite water supply.
You may fill a jug, empty a jug, or pour from one jug into the other until the
source is empty or the destination is full. **Return `true` if you can end with
exactly `z` litres of water held in the two jugs together.**

**Examples**
```
x = 3, y = 5, z = 4  ->  true
x = 2, y = 6, z = 5  ->  false
```

**Constraints:** `0 <= x, y, z <= 10^6`.
""",
    """def canMeasureWater(x, y, z):
    from math import gcd
    if z == 0:
        return True
    if x + y < z:
        return False
    g = gcd(x, y)
    return g != 0 and z % g == 0
""",
    visible=[{"x": 3, "y": 5, "z": 4}, {"x": 2, "y": 6, "z": 5}],
    hidden=[{"x": 0, "y": 0, "z": 0}, {"x": 0, "y": 0, "z": 1}, {"x": 0, "y": 5, "z": 5},
            {"x": 1, "y": 1, "z": 2}, {"x": 4, "y": 6, "z": 8}],
    gen=lambda r: [{"x": r.randint(0, 8), "y": r.randint(0, 8), "z": r.randint(0, 16)}
                   for _ in range(8)],
    brute=_jug_brute,
    checks=[({"x": 3, "y": 5, "z": 4}, True), ({"x": 2, "y": 6, "z": 5}, False),
            ({"x": 0, "y": 0, "z": 0}, True), ({"x": 0, "y": 5, "z": 5}, True),
            ({"x": 1, "y": 1, "z": 2}, True)],
    source="new_p")


# ===========================================================================
# 3. Count Unique Characters of All Substrings of a Given String
# ===========================================================================
add("count-unique-characters-of-all-substrings-of-a-given-string",
    "Count Unique Characters of All Substrings of a Given String", "hard",
    ["string", "hash-table", "dynamic-programming"], "uniqueLetterString",
    [("s", "string")], "int",
    """
For a string `t`, `countUniqueChars(t)` is the number of characters that appear
**exactly once** in `t` (e.g. `countUniqueChars("LEETCODE") = 5`: `L, T, C, O, D`).
**Return the sum of `countUniqueChars(t)` over every substring `t` of `s`** (repeated
substrings are counted each time they occur), modulo `10^9 + 7`.

**Examples**
```
s = "ABC"       ->  10
s = "ABA"       ->  8
s = "LEETCODE"  ->  92
```

**Constraints:** `0 <= len(s) <= 10^4`, `s` is upper-case English letters.
""",
    """def uniqueLetterString(s):
    MOD = 10 ** 9 + 7
    from collections import defaultdict
    idx = defaultdict(lambda: [-1, -1])
    res = 0
    for i, c in enumerate(s):
        prev2, prev1 = idx[c]
        res += (prev1 - prev2) * (i - prev1)
        idx[c] = [prev1, i]
    n = len(s)
    for c in idx:
        prev2, prev1 = idx[c]
        res += (prev1 - prev2) * (n - prev1)
    return res % MOD
""",
    visible=[{"s": "ABC"}, {"s": "ABA"}, {"s": "LEETCODE"}],
    hidden=[{"s": ""}, {"s": "A"}, {"s": "AA"}, {"s": "AAAA"}, {"s": "ABCDEF"}],
    gen=lambda r: [{"s": sstr(r, 0, 12, "ABCD")} for _ in range(8)],
    brute=_uniqchar_brute,
    checks=[({"s": "ABC"}, 10), ({"s": "ABA"}, 8), ({"s": "LEETCODE"}, 92),
            ({"s": ""}, 0), ({"s": "A"}, 1)],
    source="new_p")


# ===========================================================================
# 4. Longest Substring with At Least K Repeating Characters
# ===========================================================================
add("longest-substring-with-at-least-k-repeating-characters",
    "Longest Substring with At Least K Repeating Characters", "medium",
    ["string", "hash-table", "divide-and-conquer", "sliding-window"], "longestSubstring",
    [("s", "string"), ("k", "int")], "int",
    """
**Return the length of the longest substring of `s` in which every character appears
at least `k` times.**

**Examples**
```
s = "aaabb", k = 3   ->  3   ("aaa")
s = "ababbc", k = 2  ->  5   ("ababb")
```

**Constraints:** `0 <= len(s) <= 10^4`, lowercase letters, `1 <= k <= 10^5`.
""",
    """def longestSubstring(s, k):
    if not s:
        return 0
    from collections import Counter
    cnt = Counter(s)
    for c in cnt:
        if cnt[c] < k:
            return max(longestSubstring(t, k) for t in s.split(c))
    return len(s)
""",
    visible=[{"s": "aaabb", "k": 3}, {"s": "ababbc", "k": 2}],
    hidden=[{"s": "", "k": 1}, {"s": "a", "k": 1}, {"s": "a", "k": 2},
            {"s": "ababacb", "k": 3}, {"s": "bbaaacbd", "k": 3}],
    gen=lambda r: [{"s": sstr(r, 0, 12, "abc"), "k": r.randint(1, 3)} for _ in range(8)],
    brute=_lsk_brute,
    checks=[({"s": "aaabb", "k": 3}, 3), ({"s": "ababbc", "k": 2}, 5),
            ({"s": "a", "k": 2}, 0), ({"s": "", "k": 1}, 0)],
    source="new_p")


# ===========================================================================
# 5. Reducing Dishes
# ===========================================================================
add("reducing-dishes", "Reducing Dishes", "hard",
    ["array", "greedy", "sorting", "dynamic-programming"], "maxSatisfaction",
    [("satisfaction", "int[]")], "int",
    """
A chef can cook each dish in `1` unit of time. If a dish is the `t`-th cooked
(1-indexed), its *like-time coefficient* is `t * satisfaction[i]`. The chef may
discard some dishes and cook the rest in whatever sequence is best. **Return the
maximum possible sum of like-time coefficients.**

**Examples**
```
satisfaction = [-1,-8,0,5,-9]  ->  14   (keep -1,0,5: 1*-1 + 2*0 + 3*5)
satisfaction = [4,3,2]         ->  20   (2*1 + 3*2 + 4*3)
satisfaction = [-1,-4,-5]      ->  0    (cook nothing)
```

**Constraints:** `1 <= len(satisfaction) <= 500`, `-10^3 <= satisfaction[i] <= 10^3`.
""",
    """def maxSatisfaction(satisfaction):
    satisfaction.sort(reverse=True)
    total = 0
    run = 0
    for x in satisfaction:
        run += x
        if run <= 0:
            break
        total += run
    return total
""",
    visible=[{"satisfaction": [-1, -8, 0, 5, -9]}, {"satisfaction": [4, 3, 2]},
             {"satisfaction": [-1, -4, -5]}],
    hidden=[{"satisfaction": [-2, 5, -1, 0, 3, -3]}, {"satisfaction": [1]},
            {"satisfaction": [-1]}, {"satisfaction": [0]}, {"satisfaction": [5, 5, 5]}],
    gen=lambda r: [{"satisfaction": [r.randint(-5, 5) for _ in range(r.randint(1, 7))]}
                   for _ in range(8)],
    brute=_dish_brute,
    checks=[({"satisfaction": [-1, -8, 0, 5, -9]}, 14), ({"satisfaction": [4, 3, 2]}, 20),
            ({"satisfaction": [-1, -4, -5]}, 0), ({"satisfaction": [-2, 5, -1, 0, 3, -3]}, 35)],
    source="new_p")


# ===========================================================================
# 6. Minimum Number of Flips to Convert Binary Matrix to Zero Matrix
# ===========================================================================
add("minimum-number-of-flips-to-convert-binary-matrix-to-zero-matrix",
    "Minimum Number of Flips to Convert Binary Matrix to Zero Matrix", "hard",
    ["array", "bitmask", "breadth-first-search", "matrix"], "minFlips",
    [("mat", "int[][]")], "int",
    """
In one step you pick a cell and flip it **and its (up to four) edge-adjacent
neighbours** (flip toggles `0`/`1`). **Return the minimum number of steps to make
`mat` all zeros, or `-1` if impossible.**

**Examples**
```
mat = [[0,0],[0,1]]           ->  3
mat = [[0]]                   ->  0
mat = [[1,1,1],[1,0,1],[0,0,0]]  ->  6
mat = [[1,0,0],[1,0,0]]       ->  -1
```

**Constraints:** `1 <= m, n <= 3`, `mat[i][j]` in `{0, 1}`.
""",
    """def minFlips(mat):
    from collections import deque
    m, n = len(mat), len(mat[0])

    def encode(g):
        v = 0
        for i in range(m):
            for j in range(n):
                v = v * 2 + g[i][j]
        return v

    start = encode(mat)
    if start == 0:
        return 0

    masks = []
    for i in range(m):
        for j in range(n):
            bits = 0
            for di, dj in ((0, 0), (0, 1), (0, -1), (1, 0), (-1, 0)):
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n:
                    pos = ni * n + nj
                    bits ^= 1 << (m * n - 1 - pos)
            masks.append(bits)

    seen = {start}
    q = deque([(start, 0)])
    while q:
        s, d = q.popleft()
        for msk in masks:
            ns = s ^ msk
            if ns == 0:
                return d + 1
            if ns not in seen:
                seen.add(ns)
                q.append((ns, d + 1))
    return -1
""",
    visible=[{"mat": [[0, 0], [0, 1]]}, {"mat": [[0]]},
             {"mat": [[1, 1, 1], [1, 0, 1], [0, 0, 0]]}, {"mat": [[1, 0, 0], [1, 0, 0]]}],
    hidden=[{"mat": [[1]]}, {"mat": [[1, 1], [1, 1]]}, {"mat": [[1, 0], [0, 1]]},
            {"mat": [[0, 0, 0]]}, {"mat": [[1, 1, 1]]}],
    gen=lambda r: [_matflip_gen(r) for _ in range(8)],
    brute=_matflip_brute,
    checks=[({"mat": [[0, 0], [0, 1]]}, 3), ({"mat": [[0]]}, 0),
            ({"mat": [[1, 1, 1], [1, 0, 1], [0, 0, 0]]}, 6),
            ({"mat": [[1, 0, 0], [1, 0, 0]]}, -1)],
    source="new_p")


# ===========================================================================
# 7. Bus Routes
# ===========================================================================
add("bus-routes", "Bus Routes", "hard",
    ["array", "hash-table", "breadth-first-search"], "numBusesToDestination",
    [("routes", "int[][]"), ("source", "int"), ("target", "int")], "int",
    """
`routes[i]` is the (cyclic) sequence of stops the `i`-th bus visits forever. You
start at stop `source` (not on a bus) and want to reach stop `target`. **Return the
least number of buses you must take, or `-1` if it is impossible.**

**Example**
```
routes = [[1,2,7],[3,6,7]], source = 1, target = 6  ->  2
```
(Take bus 0 to stop 7, then bus 1 to stop 6.)

**Constraints:** `1 <= len(routes) <= 500`, `0 <= source, target < 10^6`.
""",
    """def numBusesToDestination(routes, source, target):
    from collections import defaultdict, deque
    if source == target:
        return 0
    stop_buses = defaultdict(list)
    for bus, route in enumerate(routes):
        for s in route:
            stop_buses[s].append(bus)
    visited_bus = set()
    visited_stop = {source}
    q = deque([(source, 0)])
    while q:
        stop, d = q.popleft()
        for bus in stop_buses[stop]:
            if bus in visited_bus:
                continue
            visited_bus.add(bus)
            for ns in routes[bus]:
                if ns == target:
                    return d + 1
                if ns not in visited_stop:
                    visited_stop.add(ns)
                    q.append((ns, d + 1))
    return -1
""",
    visible=[{"routes": [[1, 2, 7], [3, 6, 7]], "source": 1, "target": 6}],
    hidden=[{"routes": [[7, 12], [4, 5, 15], [6], [15, 19], [9, 12, 13]],
             "source": 15, "target": 12},
            {"routes": [[1, 2, 7], [3, 6, 7]], "source": 1, "target": 1},
            {"routes": [[1, 2, 7], [3, 6, 7]], "source": 1, "target": 5},
            {"routes": [[1, 7], [3, 5]], "source": 5, "target": 5},
            {"routes": [[0]], "source": 0, "target": 0}],
    gen=lambda r: [_bus_gen(r) for _ in range(8)],
    brute=_bus_brute,
    checks=[({"routes": [[1, 2, 7], [3, 6, 7]], "source": 1, "target": 6}, 2),
            ({"routes": [[1, 2, 7], [3, 6, 7]], "source": 1, "target": 1}, 0),
            ({"routes": [[1, 2, 7], [3, 6, 7]], "source": 1, "target": 5}, -1)],
    source="new_p")


# ===========================================================================
# 8. Best Time to Buy and Sell Stock IV
# ===========================================================================
add("best-time-to-buy-and-sell-stock-iv", "Best Time to Buy and Sell Stock IV", "hard",
    ["array", "dynamic-programming"], "maxProfit",
    [("prices", "int[]"), ("k", "int")], "int",
    """
`prices[i]` is the price of a stock on day `i`. You may complete **at most `k`
transactions** (a buy followed by a later sell), holding at most one share at a
time. **Return the maximum profit.**

**Examples**
```
prices = [2,4,1], k = 2          ->  2
prices = [3,2,6,5,0,3], k = 2    ->  7
```

**Constraints:** `0 <= k <= 100`, `0 <= len(prices) <= 1000`, `0 <= prices[i] <= 1000`.
""",
    """def maxProfit(prices, k):
    n = len(prices)
    if n == 0 or k == 0:
        return 0
    if k >= n // 2:
        return sum(max(0, prices[i + 1] - prices[i]) for i in range(n - 1))
    buy = [float('-inf')] * (k + 1)
    sell = [0] * (k + 1)
    for p in prices:
        for t in range(1, k + 1):
            buy[t] = max(buy[t], sell[t - 1] - p)
            sell[t] = max(sell[t], buy[t] + p)
    return sell[k]
""",
    visible=[{"prices": [2, 4, 1], "k": 2}, {"prices": [3, 2, 6, 5, 0, 3], "k": 2}],
    hidden=[{"prices": [], "k": 2}, {"prices": [5], "k": 3}, {"prices": [1, 2, 3, 4, 5], "k": 0},
            {"prices": [7, 6, 4, 3, 1], "k": 2}, {"prices": [3, 3, 5, 0, 0, 3, 1, 4], "k": 3}],
    gen=lambda r: [_stock4_gen(r) for _ in range(8)],
    brute=_stock4_brute,
    checks=[({"prices": [2, 4, 1], "k": 2}, 2), ({"prices": [3, 2, 6, 5, 0, 3], "k": 2}, 7),
            ({"prices": [], "k": 2}, 0), ({"prices": [1, 2, 3, 4, 5], "k": 0}, 0)],
    source="new_p")


# ===========================================================================
# 9. Find the Shortest Superstring  (reframed: return the LENGTH)
# ===========================================================================
add("find-the-shortest-superstring", "Find the Shortest Superstring", "hard",
    ["array", "string", "dynamic-programming", "bitmask"], "shortestSuperstringLength",
    [("words", "string[]")], "int",
    """
Given a list of strings `words` (no string is a substring of another), a
*superstring* is a string that contains every word as a (contiguous) substring.
**Return the length of the shortest possible superstring.**

**Examples**
```
words = ["alex","loves","leetcode"]              ->  17   ("alexlovesleetcode")
words = ["catg","ctaagt","gcta","ttca","atgcatc"] ->  16   ("gctaagttcatgcatc")
```

**Constraints:** `1 <= len(words) <= 12`, `1 <= len(words[i]) <= 20`, lowercase letters.
""",
    """def shortestSuperstringLength(words):
    words = [w for w in words if not any(w != o and w in o for o in words)]
    n = len(words)
    if n == 0:
        return 0
    if n == 1:
        return len(words[0])
    overlap = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                m = min(len(words[i]), len(words[j]))
                for k in range(m, 0, -1):
                    if words[i][-k:] == words[j][:k]:
                        overlap[i][j] = k
                        break
    dp = [[0] * n for _ in range(1 << n)]
    for mask in range(1 << n):
        for last in range(n):
            if not (mask >> last) & 1:
                continue
            for nxt in range(n):
                if (mask >> nxt) & 1:
                    continue
                val = dp[mask][last] + overlap[last][nxt]
                nm = mask | (1 << nxt)
                if val > dp[nm][nxt]:
                    dp[nm][nxt] = val
    full = (1 << n) - 1
    total = sum(len(w) for w in words)
    return total - max(dp[full])
""",
    visible=[{"words": ["alex", "loves", "leetcode"]},
             {"words": ["catg", "ctaagt", "gcta", "ttca", "atgcatc"]}],
    hidden=[{"words": ["a"]}, {"words": ["ab", "ba"]}, {"words": ["abc", "cde"]},
            {"words": ["ab", "cd", "ef"]}, {"words": ["xyz"]}],
    gen=lambda r: [_superstr_gen(r) for _ in range(6)],
    brute=_superstr_brute,
    checks=[({"words": ["alex", "loves", "leetcode"]}, 17),
            ({"words": ["catg", "ctaagt", "gcta", "ttca", "atgcatc"]}, 16),
            ({"words": ["a"]}, 1), ({"words": ["ab", "ba"]}, 3)],
    source="new_p")


# ===========================================================================
# 10. Minimum Score Triangulation of Polygon
# ===========================================================================
add("minimum-score-triangulation-of-polygon", "Minimum Score Triangulation of Polygon",
    "medium", ["array", "dynamic-programming"], "minScoreTriangulation",
    [("values", "int[]")], "int",
    """
A convex polygon has vertices labelled `values[0..N-1]` in order. Triangulate it
into `N - 2` triangles; each triangle's value is the product of its three vertex
labels, and the total score is the sum over all triangles. **Return the minimum
possible total score.**

**Examples**
```
values = [1,2,3]      ->  6
values = [3,7,4,5]     ->  144
values = [1,3,1,4,1,5] ->  13
```

**Constraints:** `3 <= len(values) <= 50`, `1 <= values[i] <= 100`.
""",
    """def minScoreTriangulation(values):
    from functools import lru_cache
    n = len(values)

    @lru_cache(None)
    def dp(i, j):
        if j - i < 2:
            return 0
        best = float('inf')
        for k in range(i + 1, j):
            best = min(best, dp(i, k) + dp(k, j) + values[i] * values[k] * values[j])
        return best

    return dp(0, n - 1)
""",
    visible=[{"values": [1, 2, 3]}, {"values": [3, 7, 4, 5]}, {"values": [1, 3, 1, 4, 1, 5]}],
    hidden=[{"values": [1, 1, 1]}, {"values": [2, 2, 2, 2]}, {"values": [5, 4, 3, 2, 1]},
            {"values": [1, 2, 3, 4, 5, 6]}],
    gen=lambda r: [{"values": [r.randint(1, 8) for _ in range(r.randint(3, 8))]}
                   for _ in range(6)],
    brute=_triangulation_brute,
    checks=[({"values": [1, 2, 3]}, 6), ({"values": [3, 7, 4, 5]}, 144),
            ({"values": [1, 3, 1, 4, 1, 5]}, 13)],
    source="new_p")


# ===========================================================================
# 11. Nth Magical Number
# ===========================================================================
add("nth-magical-number", "Nth Magical Number", "hard",
    ["math", "binary-search"], "nthMagicalNumber",
    [("n", "int"), ("a", "int"), ("b", "int")], "int",
    """
A positive integer is *magical* if it is divisible by `a` or by `b`. **Return the
`n`-th magical number** (1-indexed), modulo `10^9 + 7`.

**Examples**
```
n = 1, a = 2, b = 3  ->  2
n = 4, a = 2, b = 3  ->  6
n = 5, a = 2, b = 4  ->  10
n = 3, a = 6, b = 4  ->  8
```

**Constraints:** `1 <= n <= 10^9`, `2 <= a, b <= 4*10^4`.
""",
    """def nthMagicalNumber(n, a, b):
    from math import gcd
    MOD = 10 ** 9 + 7
    l = a * b // gcd(a, b)
    lo, hi = 1, n * min(a, b)
    while lo < hi:
        mid = (lo + hi) // 2
        if mid // a + mid // b - mid // l >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo % MOD
""",
    visible=[{"n": 1, "a": 2, "b": 3}, {"n": 4, "a": 2, "b": 3}, {"n": 5, "a": 2, "b": 4}],
    hidden=[{"n": 3, "a": 6, "b": 4}, {"n": 1, "a": 2, "b": 2}, {"n": 10, "a": 5, "b": 3},
            {"n": 7, "a": 4, "b": 4}, {"n": 2, "a": 3, "b": 5}],
    gen=lambda r: [{"n": r.randint(1, 30), "a": r.randint(2, 6), "b": r.randint(2, 6)}
                   for _ in range(8)],
    brute=_magical_brute,
    checks=[({"n": 1, "a": 2, "b": 3}, 2), ({"n": 4, "a": 2, "b": 3}, 6),
            ({"n": 5, "a": 2, "b": 4}, 10), ({"n": 3, "a": 6, "b": 4}, 8)],
    source="new_p")


# ===========================================================================
# 12. Get the Maximum Score
# ===========================================================================
add("get-the-maximum-score", "Get the Maximum Score", "hard",
    ["array", "two-pointers", "greedy"], "maxSum",
    [("nums1", "int[]"), ("nums2", "int[]")], "int",
    """
`nums1` and `nums2` are strictly increasing arrays of distinct integers. A valid
path starts at index 0 of either array, moves left to right, and may switch to the
other array **only at a value common to both** (each common value is visited once).
The score is the sum of unique values along the path. **Return the maximum score**,
modulo `10^9 + 7`.

**Examples**
```
nums1 = [2,4,5,8,10], nums2 = [4,6,8,9]  ->  30   (path [2,4,6,8,10])
nums1 = [1,3,5,7,9], nums2 = [3,5,100]    ->  109  (path [1,3,5,100])
nums1 = [1,2,3,4,5], nums2 = [6,7,8,9,10] ->  40
```

**Constraints:** `1 <= len(nums1), len(nums2) <= 10^5`, `1 <= nums[i] <= 10^7`,
both strictly increasing.
""",
    """def maxSum(nums1, nums2):
    MOD = 10 ** 9 + 7
    i = j = 0
    s1 = s2 = 0
    n, m = len(nums1), len(nums2)
    res = 0
    while i < n or j < m:
        if i < n and (j == m or nums1[i] < nums2[j]):
            s1 += nums1[i]
            i += 1
        elif j < m and (i == n or nums2[j] < nums1[i]):
            s2 += nums2[j]
            j += 1
        else:
            res += max(s1, s2) + nums1[i]
            s1 = s2 = 0
            i += 1
            j += 1
    res += max(s1, s2)
    return res % MOD
""",
    visible=[{"nums1": [2, 4, 5, 8, 10], "nums2": [4, 6, 8, 9]},
             {"nums1": [1, 3, 5, 7, 9], "nums2": [3, 5, 100]},
             {"nums1": [1, 2, 3, 4, 5], "nums2": [6, 7, 8, 9, 10]}],
    hidden=[{"nums1": [1, 4, 5, 8, 9, 11, 19], "nums2": [2, 3, 4, 11, 12]},
            {"nums1": [1], "nums2": [1]}, {"nums1": [1], "nums2": [2]},
            {"nums1": [1, 2, 3], "nums2": [3]}],
    gen=lambda r: [_maxscore_gen(r) for _ in range(8)],
    brute=_maxscore_brute,
    checks=[({"nums1": [2, 4, 5, 8, 10], "nums2": [4, 6, 8, 9]}, 30),
            ({"nums1": [1, 3, 5, 7, 9], "nums2": [3, 5, 100]}, 109),
            ({"nums1": [1, 2, 3, 4, 5], "nums2": [6, 7, 8, 9, 10]}, 40),
            ({"nums1": [1, 4, 5, 8, 9, 11, 19], "nums2": [2, 3, 4, 11, 12]}, 61)],
    source="new_p")


# ===========================================================================
# 13. Validate IP Address
# ===========================================================================
add("validate-ip-address", "Validate IP Address", "medium",
    ["string"], "validIPAddress", [("IP", "string")], "string",
    """
**Return `"IPv4"` if `IP` is a valid IPv4 address, `"IPv6"` if it is a valid IPv6
address, and `"Neither"` otherwise.**

- IPv4: four decimal numbers `0`-`255` separated by dots, with **no leading zeros**
  (`"172.16.254.01"` is invalid).
- IPv6: eight groups of `1`-`4` hexadecimal digits separated by colons. Leading
  zeros within a group are allowed, but `::` (zero compression) and extra leading
  zeros beyond four digits are not.

**Examples**
```
"172.16.254.1"                       ->  "IPv4"
"2001:0db8:85a3:0:0:8A2E:0370:7334"  ->  "IPv6"
"256.256.256.256"                    ->  "Neither"
```

**Constraints:** `IP` has no spaces or special characters.
""",
    """def validIPAddress(IP):
    def is_v4(s):
        parts = s.split(".")
        if len(parts) != 4:
            return False
        for p in parts:
            if not p.isascii() or not p.isdigit():
                return False
            if len(p) > 1 and p[0] == '0':
                return False
            if not 0 <= int(p) <= 255:
                return False
        return True

    def is_v6(s):
        parts = s.split(":")
        if len(parts) != 8:
            return False
        hexd = set("0123456789abcdefABCDEF")
        for p in parts:
            if not 1 <= len(p) <= 4:
                return False
            if any(c not in hexd for c in p):
                return False
        return True

    if is_v4(IP):
        return "IPv4"
    if is_v6(IP):
        return "IPv6"
    return "Neither"
""",
    visible=[{"IP": "172.16.254.1"}, {"IP": "2001:0db8:85a3:0:0:8A2E:0370:7334"},
             {"IP": "256.256.256.256"}],
    hidden=[{"IP": "172.16.254.01"}, {"IP": "02001:0db8:85a3:0000:0000:8a2e:0370:7334"},
            {"IP": "2001:0db8:85a3::8A2E:0370:7334"}, {"IP": "1e1.4.5.6"},
            {"IP": "12..33.4"}, {"IP": "20EE:FGb8:85a3:0:0:8A2E:0370:7334"},
            {"IP": "1.0.1.0"}],
    gen=lambda r: [_ip_gen(r) for _ in range(8)],
    checks=[({"IP": "172.16.254.1"}, "IPv4"),
            ({"IP": "2001:0db8:85a3:0:0:8A2E:0370:7334"}, "IPv6"),
            ({"IP": "256.256.256.256"}, "Neither"), ({"IP": "172.16.254.01"}, "Neither"),
            ({"IP": "2001:0db8:85a3::8A2E:0370:7334"}, "Neither")],
    source="new_p")


# ===========================================================================
# 14. Minimize Malware Spread II
# ===========================================================================
add("minimize-malware-spread-ii", "Minimize Malware Spread II", "hard",
    ["array", "depth-first-search", "breadth-first-search", "union-find", "graph"],
    "minMalwareSpread", [("graph", "int[][]"), ("initial", "int[]")], "int",
    """
`graph[i][j] == 1` means nodes `i` and `j` are directly connected. Some `initial`
nodes are infected; infection spreads through connections until no more nodes can be
infected. You will **completely remove one node** from `initial` (deleting it and
all its connections). **Return the node whose removal minimizes the final number of
infected nodes;** on a tie return the smallest index.

**Examples**
```
graph = [[1,1,0],[1,1,0],[0,0,1]], initial = [0,1]            ->  0
graph = [[1,1,0],[1,1,1],[0,1,1]], initial = [0,1]            ->  1
graph = [[1,1,0,0],[1,1,1,0],[0,1,1,1],[0,0,1,1]], initial = [0,1]  ->  1
```

**Constraints:** `2 <= len(graph) <= 300`, `graph` is symmetric with `graph[i][i] = 1`,
`1 <= len(initial) < len(graph)`.
""",
    """def minMalwareSpread(graph, initial):
    n = len(graph)
    from collections import deque

    def spread(removed):
        infected = set(s for s in initial if s != removed)
        q = deque(infected)
        while q:
            u = q.popleft()
            if u == removed:
                continue
            for v in range(n):
                if v == removed:
                    continue
                if graph[u][v] == 1 and v not in infected:
                    infected.add(v)
                    q.append(v)
        return len(infected)

    best, node = None, min(initial)
    for cand in sorted(initial):
        c = spread(cand)
        if best is None or c < best:
            best, node = c, cand
    return node
""",
    visible=[{"graph": [[1, 1, 0], [1, 1, 0], [0, 0, 1]], "initial": [0, 1]},
             {"graph": [[1, 1, 0], [1, 1, 1], [0, 1, 1]], "initial": [0, 1]},
             {"graph": [[1, 1, 0, 0], [1, 1, 1, 0], [0, 1, 1, 1], [0, 0, 1, 1]],
              "initial": [0, 1]}],
    hidden=[{"graph": [[1, 0], [0, 1]], "initial": [0, 1]},
            {"graph": [[1, 1, 1], [1, 1, 1], [1, 1, 1]], "initial": [0, 1, 2]},
            {"graph": [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "initial": [1, 2]},
            {"graph": [[1, 1, 0], [1, 1, 0], [0, 0, 1]], "initial": [1, 2]}],
    gen=lambda r: [_malware_gen(r) for _ in range(8)],
    brute=_malware_brute,
    checks=[({"graph": [[1, 1, 0], [1, 1, 0], [0, 0, 1]], "initial": [0, 1]}, 0),
            ({"graph": [[1, 1, 0], [1, 1, 1], [0, 1, 1]], "initial": [0, 1]}, 1),
            ({"graph": [[1, 1, 0, 0], [1, 1, 1, 0], [0, 1, 1, 1], [0, 0, 1, 1]],
              "initial": [0, 1]}, 1)],
    source="new_p")


# ===========================================================================
# 15. Sum of Subsequence Widths
# ===========================================================================
add("sum-of-subsequence-widths", "Sum of Subsequence Widths", "hard",
    ["array", "math", "sorting"], "sumSubseqWidths", [("nums", "int[]")], "int",
    """
The *width* of a sequence is `max - min`. **Return the sum of widths over all
non-empty subsequences of `nums`**, modulo `10^9 + 7`.

**Example**
```
nums = [2,1,3]  ->  6
```
(Subsequence widths: `[1],[2],[3] -> 0`; `[2,1],[2,3] -> 1`; `[1,3] -> 2`;
`[2,1,3] -> 2`; total `6`.)

**Constraints:** `1 <= len(nums) <= 10^5`, `1 <= nums[i] <= 10^5`.
""",
    """def sumSubseqWidths(nums):
    MOD = 10 ** 9 + 7
    nums.sort()
    n = len(nums)
    pow2 = [1] * n
    for i in range(1, n):
        pow2[i] = pow2[i - 1] * 2 % MOD
    res = 0
    for i in range(n):
        res = (res + (pow2[i] - pow2[n - 1 - i]) * nums[i]) % MOD
    return res % MOD
""",
    visible=[{"nums": [2, 1, 3]}],
    hidden=[{"nums": [1]}, {"nums": [5, 5]}, {"nums": [1, 2]}, {"nums": [4, 3, 2, 1]},
            {"nums": [10, 1, 5, 7]}],
    gen=lambda r: [{"nums": [r.randint(1, 20) for _ in range(r.randint(1, 12))]}
                   for _ in range(8)],
    brute=_ssw_brute,
    checks=[({"nums": [2, 1, 3]}, 6), ({"nums": [1]}, 0), ({"nums": [5, 5]}, 0),
            ({"nums": [1, 2]}, 1)],
    source="new_p")


# ===========================================================================
# 16. The kth Factor of n
# ===========================================================================
add("the-kth-factor-of-n", "The kth Factor of n", "medium",
    ["math"], "kthFactor", [("n", "int"), ("k", "int")], "int",
    """
A factor of `n` is an integer `i` with `n % i == 0`. List all factors of `n` in
ascending order; **return the `k`-th factor, or `-1` if `n` has fewer than `k`
factors.**

**Examples**
```
n = 12, k = 3  ->  3    (factors 1,2,3,4,6,12)
n = 7, k = 2   ->  7
n = 4, k = 4   ->  -1
```

**Constraints:** `1 <= k <= n <= 1000`.
""",
    """def kthFactor(n, k):
    for i in range(1, n + 1):
        if n % i == 0:
            k -= 1
            if k == 0:
                return i
    return -1
""",
    visible=[{"n": 12, "k": 3}, {"n": 7, "k": 2}, {"n": 4, "k": 4}],
    hidden=[{"n": 1, "k": 1}, {"n": 1000, "k": 3}, {"n": 100, "k": 9}, {"n": 6, "k": 4},
            {"n": 6, "k": 5}],
    gen=lambda r: [{"n": r.randint(1, 200), "k": r.randint(1, 15)} for _ in range(8)],
    brute=_kthfac_brute,
    checks=[({"n": 12, "k": 3}, 3), ({"n": 7, "k": 2}, 7), ({"n": 4, "k": 4}, -1),
            ({"n": 1, "k": 1}, 1), ({"n": 1000, "k": 3}, 4)],
    source="new_p")


# ===========================================================================
# 17. Count Vowels Permutation
# ===========================================================================
add("count-vowels-permutation", "Count Vowels Permutation", "hard",
    ["dynamic-programming"], "countVowelPermutation", [("n", "int")], "int",
    """
Count strings of length `n` made of vowels `a, e, i, o, u` obeying: after `a` comes
`e`; after `e` comes `a` or `i`; after `i` comes anything except `i`; after `o`
comes `i` or `u`; after `u` comes `a`. **Return the count, modulo `10^9 + 7`.**

**Examples**
```
n = 1  ->  5
n = 2  ->  10
n = 5  ->  68
```

**Constraints:** `1 <= n <= 2*10^4`.
""",
    """def countVowelPermutation(n):
    MOD = 10 ** 9 + 7
    a = e = i = o = u = 1
    for _ in range(n - 1):
        a, e, i, o, u = (
            (e + i + u) % MOD,
            (a + i) % MOD,
            (e + o) % MOD,
            i % MOD,
            (i + o) % MOD,
        )
    return (a + e + i + o + u) % MOD
""",
    visible=[{"n": 1}, {"n": 2}, {"n": 5}],
    hidden=[{"n": 3}, {"n": 4}, {"n": 6}, {"n": 10}],
    gen=lambda r: [{"n": r.randint(1, 9)} for _ in range(8)],
    brute=_vowel_brute,
    checks=[({"n": 1}, 5), ({"n": 2}, 10), ({"n": 5}, 68)],
    source="new_p")
