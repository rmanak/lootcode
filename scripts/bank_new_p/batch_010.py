"""Batch 010 of the new_p.txt import (19 problems).

One entry was dropped as a duplicate under a different slug (see `_skips.py`):
`longest-substring-without-repeating-characters` (== `longest-substring-without-repeating`).
"""
from scripts.build_bank import add, ilist, sstr  # noqa: F401


# --------------------------- brute / reference helpers ---------------------
def _stone3_brute(stoneValue):
    from functools import lru_cache
    n = len(stoneValue)

    @lru_cache(None)
    def f(i):
        if i >= n:
            return 0
        best = float('-inf')
        s = 0
        for k in range(3):
            if i + k < n:
                s += stoneValue[i + k]
                best = max(best, s - f(i + k + 1))
        return best
    d = f(0)
    return "Alice" if d > 0 else ("Bob" if d < 0 else "Tie")


def _funccalls_brute(nums):
    a = list(nums)
    ops = 0
    while any(a):
        for i in range(len(a)):
            if a[i] % 2 == 1:
                a[i] -= 1
                ops += 1
        if any(a):
            a = [x // 2 for x in a]
            ops += 1
    return ops


def _break_brute(s1, s2):
    from itertools import permutations
    n = len(s1)

    def can(x, y):
        ys = sorted(y)
        for px in set(permutations(x)):
            if all(px[i] >= ys[i] for i in range(n)):
                return True
        return False
    return can(s1, s2) or can(s2, s1)


def _patch_brute(nums, n):
    from itertools import combinations_with_replacement

    def covered(extra):
        s = {0}
        for x in sorted(nums + extra):
            s |= {b + x for b in list(s) if b + x <= n}
        return all(v in s for v in range(1, n + 1))

    if covered([]):
        return 0
    for p in range(1, 15):
        for combo in combinations_with_replacement(range(1, n + 1), p):
            if covered(list(combo)):
                return p
    return -1


def _interleave_brute(s1, s2, s3):
    if len(s1) + len(s2) != len(s3):
        return False
    from functools import lru_cache

    @lru_cache(None)
    def f(i, j):
        if i == len(s1) and j == len(s2):
            return True
        k = i + j
        res = False
        if i < len(s1) and s1[i] == s3[k]:
            res = res or f(i + 1, j)
        if j < len(s2) and s2[j] == s3[k]:
            res = res or f(i, j + 1)
        return res
    return f(0, 0)


def _nextgreat_brute(n):
    from itertools import permutations
    s = str(n)
    best = None
    for p in set(permutations(s)):
        if p[0] == '0':
            continue
        v = int("".join(p))
        if n < v <= 2 ** 31 - 1 and (best is None or v < best):
            best = v
    return best if best is not None else -1


def _farland_brute(grid):
    n, m = len(grid), len(grid[0])
    lands = [(i, j) for i in range(n) for j in range(m) if grid[i][j] == 1]
    waters = [(i, j) for i in range(n) for j in range(m) if grid[i][j] == 0]
    if not lands or not waters:
        return -1
    best = 0
    for wi, wj in waters:
        best = max(best, min(abs(wi - li) + abs(wj - lj) for li, lj in lands))
    return best


def _zigzag_brute(s, numRows):
    if numRows == 1:
        return s
    rows = [[] for _ in range(numRows)]
    n = len(s)
    i = 0
    while i < n:
        r = 0
        while r < numRows and i < n:
            rows[r].append(s[i])
            i += 1
            r += 1
        r = numRows - 2
        while r >= 1 and i < n:
            rows[r].append(s[i])
            i += 1
            r -= 1
    return "".join("".join(row) for row in rows)


def _p132_brute(nums):
    n = len(nums)
    for j in range(n):
        for k in range(j + 1, n):
            for i in range(j):
                if nums[i] < nums[k] < nums[j]:
                    return True
    return False


def _maxprod_brute(grid):
    m, n = len(grid), len(grid[0])
    best = [-1]

    def dfs(i, j, prod):
        prod *= grid[i][j]
        if i == m - 1 and j == n - 1:
            if prod >= 0:
                best[0] = max(best[0], prod)
            return
        if i + 1 < m:
            dfs(i + 1, j, prod)
        if j + 1 < n:
            dfs(i, j + 1, prod)
    dfs(0, 0, 1)
    return best[0] if best[0] < 0 else best[0] % (10 ** 9 + 7)


def _clock_brute(hour, minutes):
    h = (hour % 12 + minutes / 60.0) * 30.0
    m = minutes * 6.0
    d = abs(h - m) % 360
    return round(min(d, 360 - d), 5)


def _jump4_brute(arr):
    from collections import deque, defaultdict
    n = len(arr)
    if n == 1:
        return 0
    idx = defaultdict(list)
    for i, v in enumerate(arr):
        idx[v].append(i)
    visited = {0}
    q = deque([(0, 0)])
    while q:
        i, s = q.popleft()
        if i == n - 1:
            return s
        cand = [i - 1, i + 1] + [j for j in idx[arr[i]] if j != i]
        for j in cand:
            if 0 <= j < n and j not in visited:
                visited.add(j)
                q.append((j, s + 1))
    return -1


def _delcost_brute(s, cost):
    n = len(s)
    best = [float('inf')]

    def dfs(i, last, acc):
        if acc >= best[0]:
            return
        if i == n:
            best[0] = min(best[0], acc)
            return
        dfs(i + 1, last, acc + cost[i])
        if s[i] != last:
            dfs(i + 1, s[i], acc)
    dfs(0, '', 0)
    return best[0]


def _billboard_brute(rods):
    from itertools import product
    best = 0
    for assign in product(range(3), repeat=len(rods)):
        left = sum(rods[i] for i in range(len(rods)) if assign[i] == 1)
        right = sum(rods[i] for i in range(len(rods)) if assign[i] == 2)
        if left == right:
            best = max(best, left)
    return best


def _anagram_brute(s, t):
    from collections import Counter
    cs = Counter(s)
    tt = Counter(t)
    return sum(tt[c] - cs.get(c, 0) for c in tt if tt[c] > cs.get(c, 0))


def _gas_brute(gas, cost):
    n = len(gas)
    for start in range(n):
        tank = 0
        ok = True
        for k in range(n):
            i = (start + k) % n
            tank += gas[i] - cost[i]
            if tank < 0:
                ok = False
                break
        if ok:
            return start
    return -1


def _goodstr_brute(n, s1, s2, evil):
    from itertools import product
    cnt = 0
    for tup in product(range(26), repeat=n):
        t = "".join(chr(c + 97) for c in tup)
        if s1 <= t <= s2 and evil not in t:
            cnt += 1
    return cnt % (10 ** 9 + 7)


def _triplets_brute(nums1, nums2):
    def count(a, b):
        res = 0
        m = len(b)
        for x in a:
            sq = x * x
            for j in range(m):
                for k in range(j + 1, m):
                    if b[j] * b[k] == sq:
                        res += 1
        return res
    return count(nums1, nums2) + count(nums2, nums1)


# gen helpers ---------------------------------------------------------------
def _patch_gen(r):
    n = r.randint(1, 8)
    k = r.randint(0, 3)
    return {"nums": sorted(r.randint(1, n) for _ in range(k)), "n": n}


def _interleave_gen(r):
    s1 = "".join(r.choice("ab") for _ in range(r.randint(0, 4)))
    s2 = "".join(r.choice("ab") for _ in range(r.randint(0, 4)))
    if r.random() < 0.5:
        a, b, out = list(s1), list(s2), []
        while a or b:
            if a and (not b or r.random() < 0.5):
                out.append(a.pop(0))
            else:
                out.append(b.pop(0))
        s3 = "".join(out)
    else:
        s3 = "".join(r.choice("ab") for _ in range(len(s1) + len(s2)))
    return {"s1": s1, "s2": s2, "s3": s3}


def _farland_gen(r):
    rows, cols = r.randint(1, 5), r.randint(1, 5)
    return {"grid": [[r.randint(0, 1) for _ in range(cols)] for _ in range(rows)]}


def _maxprod_gen(r):
    rows, cols = r.randint(1, 4), r.randint(1, 4)
    return {"grid": [[r.randint(-4, 4) for _ in range(cols)] for _ in range(rows)]}


def _goodstr_gen(r):
    n = r.randint(1, 3)
    a = "".join(r.choice("abc") for _ in range(n))
    b = "".join(r.choice("abc") for _ in range(n))
    s1, s2 = min(a, b), max(a, b)
    evil = "".join(r.choice("abc") for _ in range(r.randint(1, 2)))
    return {"n": n, "s1": s1, "s2": s2, "evil": evil}


# ===========================================================================
# 1. Stone Game III
# ===========================================================================
add("stone-game-iii", "Stone Game III", "hard",
    ["array", "math", "dynamic-programming", "game-theory"], "stoneGameIII",
    [("stoneValue", "int[]")], "string",
    """
Alice and Bob alternate (Alice first), each turn taking `1`, `2`, or `3` stones from
the front of the row; a player's score is the sum of values they take. Both play
optimally to maximize their own score. **Return `"Alice"`, `"Bob"`, or `"Tie"`.**

**Examples**
```
stoneValue = [1,2,3,7]   ->  "Bob"
stoneValue = [1,2,3,-9]  ->  "Alice"
stoneValue = [1,2,3,6]   ->  "Tie"
```

**Constraints:** `1 <= len(stoneValue) <= 5*10^4`, `-1000 <= stoneValue[i] <= 1000`.
""",
    """def stoneGameIII(stoneValue):
    n = len(stoneValue)
    dp = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        take = 0
        best = float('-inf')
        for k in range(3):
            if i + k < n:
                take += stoneValue[i + k]
                best = max(best, take - dp[i + k + 1])
        dp[i] = best
    if dp[0] > 0:
        return "Alice"
    if dp[0] < 0:
        return "Bob"
    return "Tie"
""",
    visible=[{"stoneValue": [1, 2, 3, 7]}, {"stoneValue": [1, 2, 3, -9]},
             {"stoneValue": [1, 2, 3, 6]}],
    hidden=[{"stoneValue": [1, 2, 3, -1, -2, -3, 7]}, {"stoneValue": [-1, -2, -3]},
            {"stoneValue": [1]}, {"stoneValue": [0, 0]}],
    gen=lambda r: [{"stoneValue": [r.randint(-5, 5) for _ in range(r.randint(1, 10))]}
                   for _ in range(6)],
    brute=_stone3_brute,
    checks=[({"stoneValue": [1, 2, 3, 7]}, "Bob"), ({"stoneValue": [1, 2, 3, -9]}, "Alice"),
            ({"stoneValue": [1, 2, 3, 6]}, "Tie"), ({"stoneValue": [-1, -2, -3]}, "Tie")],
    source="new_p")


# ===========================================================================
# 2. Minimum Numbers of Function Calls to Make Target Array
# ===========================================================================
add("minimum-numbers-of-function-calls-to-make-target-array",
    "Minimum Numbers of Function Calls to Make Target Array", "hard",
    ["array", "greedy", "bit-manipulation"], "minOperations", [("nums", "int[]")], "int",
    """
Start from an all-zero array the same length as `nums`. Two operations are allowed:
add `1` to any single element, or double **every** element. **Return the minimum
number of operations to turn the zero array into `nums`.**

**Examples**
```
nums = [1,5]       ->  5
nums = [2,2]       ->  3
nums = [4,2,5]     ->  6
nums = [2,4,8,16]  ->  8
```

**Constraints:** `1 <= len(nums) <= 10^5`, `0 <= nums[i] <= 10^9`.
""",
    """def minOperations(nums):
    increments = 0
    max_doublings = 0
    for x in nums:
        increments += bin(x).count("1")
        if x > 0:
            max_doublings = max(max_doublings, x.bit_length() - 1)
    return increments + max_doublings
""",
    visible=[{"nums": [1, 5]}, {"nums": [2, 2]}, {"nums": [4, 2, 5]},
             {"nums": [2, 4, 8, 16]}],
    hidden=[{"nums": [0]}, {"nums": [3, 2, 2, 4]}, {"nums": [0, 0, 0]}, {"nums": [1]}],
    gen=lambda r: [{"nums": [r.randint(0, 20) for _ in range(r.randint(1, 6))]}
                   for _ in range(6)],
    brute=_funccalls_brute,
    checks=[({"nums": [1, 5]}, 5), ({"nums": [2, 2]}, 3), ({"nums": [4, 2, 5]}, 6),
            ({"nums": [3, 2, 2, 4]}, 7), ({"nums": [2, 4, 8, 16]}, 8)],
    source="new_p")


# ===========================================================================
# 3. Check If a String Can Break Another String
# ===========================================================================
add("check-if-a-string-can-break-another-string",
    "Check If a String Can Break Another String", "medium",
    ["string", "greedy", "sorting"], "checkIfCanBreak",
    [("s1", "string"), ("s2", "string")], "bool",
    """
String `x` *breaks* string `y` (same length) if `x[i] >= y[i]` for every `i` after
each is permuted. **Return `true` if some permutation of `s1` can break some
permutation of `s2`, or vice versa.**

**Examples**
```
s1 = "abc", s2 = "xya"        ->  true
s1 = "abe", s2 = "acd"        ->  false
s1 = "leetcodee", s2 = "interview" ->  true
```

**Constraints:** `1 <= len(s1) == len(s2) <= 10^5`, lowercase letters.
""",
    """def checkIfCanBreak(s1, s2):
    a = sorted(s1)
    b = sorted(s2)
    le = all(a[i] <= b[i] for i in range(len(a)))
    ge = all(a[i] >= b[i] for i in range(len(a)))
    return le or ge
""",
    visible=[{"s1": "abc", "s2": "xya"}, {"s1": "abe", "s2": "acd"},
             {"s1": "leetcodee", "s2": "interview"}],
    hidden=[{"s1": "a", "s2": "a"}, {"s1": "ab", "s2": "ba"}, {"s1": "az", "s2": "by"},
            {"s1": "cba", "s2": "abc"}],
    gen=lambda r: [(lambda n: {"s1": sstr(r, n, n, "abc"), "s2": sstr(r, n, n, "abc")})
                   (r.randint(1, 5)) for _ in range(8)],
    brute=_break_brute,
    checks=[({"s1": "abc", "s2": "xya"}, True), ({"s1": "abe", "s2": "acd"}, False),
            ({"s1": "leetcodee", "s2": "interview"}, True)],
    source="new_p")


# ===========================================================================
# 4. Patching Array
# ===========================================================================
add("patching-array", "Patching Array", "hard",
    ["array", "greedy"], "minPatches", [("nums", "int[]"), ("n", "int")], "int",
    """
`nums` is a sorted array of positive integers. **Return the minimum number of
elements to add** so that every integer in `[1, n]` can be formed as a sum of some
subset of the (patched) array.

**Examples**
```
nums = [1,3], n = 6      ->  1
nums = [1,5,10], n = 20  ->  2
nums = [1,2,2], n = 5    ->  0
```

**Constraints:** `0 <= len(nums) <= 1000`, `1 <= n <= 2^31 - 1`.
""",
    """def minPatches(nums, n):
    patches = 0
    miss = 1
    i = 0
    while miss <= n:
        if i < len(nums) and nums[i] <= miss:
            miss += nums[i]
            i += 1
        else:
            miss += miss
            patches += 1
    return patches
""",
    visible=[{"nums": [1, 3], "n": 6}, {"nums": [1, 5, 10], "n": 20},
             {"nums": [1, 2, 2], "n": 5}],
    hidden=[{"nums": [], "n": 5}, {"nums": [1], "n": 1}, {"nums": [2], "n": 5},
            {"nums": [1, 2, 4, 8], "n": 15}],
    gen=lambda r: [_patch_gen(r) for _ in range(6)],
    brute=_patch_brute,
    checks=[({"nums": [1, 3], "n": 6}, 1), ({"nums": [1, 5, 10], "n": 20}, 2),
            ({"nums": [1, 2, 2], "n": 5}, 0), ({"nums": [], "n": 5}, 3),
            ({"nums": [1, 2, 31, 33], "n": 2147483647}, 28)],
    source="new_p")


# ===========================================================================
# 5. Interleaving String
# ===========================================================================
add("interleaving-string", "Interleaving String", "medium",
    ["string", "dynamic-programming"], "isInterleave",
    [("s1", "string"), ("s2", "string"), ("s3", "string")], "bool",
    """
**Return `true` if `s3` is an interleaving of `s1` and `s2`** — that is, `s3` can be
formed by merging `s1` and `s2` while preserving the left-to-right order of each.

**Examples**
```
s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac"  ->  true
s1 = "aabcc", s2 = "dbbca", s3 = "aadbbbaccc"  ->  false
```

**Constraints:** `0 <= len(s1), len(s2) <= 100`, `len(s3) == len(s1)+len(s2)` (else
`false`), lowercase letters.
""",
    """def isInterleave(s1, s2, s3):
    n, m = len(s1), len(s2)
    if n + m != len(s3):
        return False
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    for i in range(n + 1):
        for j in range(m + 1):
            if i > 0 and dp[i - 1][j] and s1[i - 1] == s3[i + j - 1]:
                dp[i][j] = True
            if j > 0 and dp[i][j - 1] and s2[j - 1] == s3[i + j - 1]:
                dp[i][j] = True
    return dp[n][m]
""",
    visible=[{"s1": "aabcc", "s2": "dbbca", "s3": "aadbbcbcac"},
             {"s1": "aabcc", "s2": "dbbca", "s3": "aadbbbaccc"}],
    hidden=[{"s1": "", "s2": "", "s3": ""}, {"s1": "a", "s2": "", "s3": "a"},
            {"s1": "a", "s2": "b", "s3": "ab"}, {"s1": "a", "s2": "b", "s3": "ba"},
            {"s1": "abc", "s2": "abc", "s3": "abcabc"}],
    gen=lambda r: [_interleave_gen(r) for _ in range(8)],
    brute=_interleave_brute,
    checks=[({"s1": "aabcc", "s2": "dbbca", "s3": "aadbbcbcac"}, True),
            ({"s1": "aabcc", "s2": "dbbca", "s3": "aadbbbaccc"}, False),
            ({"s1": "", "s2": "", "s3": ""}, True)],
    source="new_p")


# ===========================================================================
# 6. Next Greater Element III
# ===========================================================================
add("next-greater-element-iii", "Next Greater Element III", "medium",
    ["math", "two-pointers", "string"], "nextGreaterElement", [("n", "int")], "int",
    """
Given a positive 32-bit integer `n`, **return the smallest 32-bit integer that uses
exactly the same digits and is strictly greater than `n`**, or `-1` if none exists
(or it would exceed `2^31 - 1`).

**Examples**
```
n = 12  ->  21
n = 21  ->  -1
```

**Constraints:** `1 <= n <= 2^31 - 1`.
""",
    """def nextGreaterElement(n):
    digits = list(str(n))
    i = len(digits) - 2
    while i >= 0 and digits[i] >= digits[i + 1]:
        i -= 1
    if i < 0:
        return -1
    j = len(digits) - 1
    while digits[j] <= digits[i]:
        j -= 1
    digits[i], digits[j] = digits[j], digits[i]
    digits[i + 1:] = reversed(digits[i + 1:])
    val = int("".join(digits))
    return val if val <= 2 ** 31 - 1 else -1
""",
    visible=[{"n": 12}, {"n": 21}],
    hidden=[{"n": 1}, {"n": 11}, {"n": 230241}, {"n": 1234}, {"n": 12443}],
    gen=lambda r: [{"n": r.randint(1, 9999)} for _ in range(8)],
    brute=_nextgreat_brute,
    checks=[({"n": 12}, 21), ({"n": 21}, -1), ({"n": 1}, -1), ({"n": 230241}, 230412),
            ({"n": 1234}, 1243), ({"n": 1999999999}, -1)],
    source="new_p")


# ===========================================================================
# 7. As Far from Land as Possible
# ===========================================================================
add("as-far-from-land-as-possible", "As Far from Land as Possible", "medium",
    ["array", "breadth-first-search", "matrix"], "maxDistance",
    [("grid", "int[][]")], "int",
    """
In a grid of `0` (water) and `1` (land), **return the largest Manhattan distance from
a water cell to its nearest land cell**, or `-1` if the grid is all water or all
land.

**Examples**
```
grid = [[1,0,1],[0,0,0],[1,0,1]]  ->  2
grid = [[1,0,0],[0,0,0],[0,0,0]]  ->  4
```

**Constraints:** `1 <= len(grid) == len(grid[0]) <= 100`, cells are `0`/`1`.
""",
    """def maxDistance(grid):
    from collections import deque
    n = len(grid)
    m = len(grid[0])
    q = deque()
    seen = [[grid[i][j] == 1 for j in range(m)] for i in range(n)]
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 1:
                q.append((i, j))
    if not q or len(q) == n * m:
        return -1
    dist = -1
    while q:
        dist += 1
        for _ in range(len(q)):
            i, j = q.popleft()
            for di, dj in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                ni, nj = i + di, j + dj
                if 0 <= ni < n and 0 <= nj < m and not seen[ni][nj]:
                    seen[ni][nj] = True
                    q.append((ni, nj))
    return dist
""",
    visible=[{"grid": [[1, 0, 1], [0, 0, 0], [1, 0, 1]]},
             {"grid": [[1, 0, 0], [0, 0, 0], [0, 0, 0]]}],
    hidden=[{"grid": [[1, 1], [1, 1]]}, {"grid": [[0]]}, {"grid": [[1]]},
            {"grid": [[0, 0, 0], [0, 1, 0], [0, 0, 0]]}],
    gen=lambda r: [_farland_gen(r) for _ in range(6)],
    brute=_farland_brute,
    checks=[({"grid": [[1, 0, 1], [0, 0, 0], [1, 0, 1]]}, 2),
            ({"grid": [[1, 0, 0], [0, 0, 0], [0, 0, 0]]}, 4),
            ({"grid": [[1, 1], [1, 1]]}, -1)],
    source="new_p")


# ===========================================================================
# 8. Zigzag Conversion
# ===========================================================================
add("zigzag-conversion", "Zigzag Conversion", "medium",
    ["string"], "convert", [("s", "string"), ("numRows", "int")], "string",
    """
Write `s` in a zigzag pattern down and up across `numRows` rows, then read it off row
by row. **Return the resulting string.**

**Examples**
```
s = "PAYPALISHIRING", numRows = 3  ->  "PAHNAPLSIIGYIR"
s = "PAYPALISHIRING", numRows = 4  ->  "PINALSIGYAHRPI"
```

**Constraints:** `1 <= len(s) <= 1000`, `1 <= numRows <= 1000`.
""",
    """def convert(s, numRows):
    if numRows == 1 or numRows >= len(s):
        return s
    rows = [''] * numRows
    cur = 0
    step = 1
    for c in s:
        rows[cur] += c
        if cur == 0:
            step = 1
        elif cur == numRows - 1:
            step = -1
        cur += step
    return ''.join(rows)
""",
    visible=[{"s": "PAYPALISHIRING", "numRows": 3},
             {"s": "PAYPALISHIRING", "numRows": 4}],
    hidden=[{"s": "A", "numRows": 1}, {"s": "AB", "numRows": 1}, {"s": "ABCD", "numRows": 2},
            {"s": "ABC", "numRows": 5}],
    gen=lambda r: [{"s": sstr(r, 1, 15, "ABCDE"), "numRows": r.randint(1, 5)}
                   for _ in range(6)],
    brute=_zigzag_brute,
    checks=[({"s": "PAYPALISHIRING", "numRows": 3}, "PAHNAPLSIIGYIR"),
            ({"s": "PAYPALISHIRING", "numRows": 4}, "PINALSIGYAHRPI"),
            ({"s": "A", "numRows": 1}, "A")],
    source="new_p")


# ===========================================================================
# 9. 132 Pattern
# ===========================================================================
add("132-pattern", "132 Pattern", "medium",
    ["array", "stack", "monotonic-stack", "binary-search"], "find132pattern",
    [("nums", "int[]")], "bool",
    """
A *132 pattern* is a subsequence `nums[i], nums[j], nums[k]` with `i < j < k` and
`nums[i] < nums[k] < nums[j]`. **Return `true` if such a pattern exists.**

**Examples**
```
nums = [1,2,3,4]    ->  false
nums = [3,1,4,2]    ->  true
nums = [-1,3,2,0]   ->  true
```

**Constraints:** `1 <= len(nums) <= 2*10^4`, integer values.
""",
    """def find132pattern(nums):
    third = float('-inf')
    stack = []
    for x in reversed(nums):
        if x < third:
            return True
        while stack and stack[-1] < x:
            third = stack.pop()
        stack.append(x)
    return False
""",
    visible=[{"nums": [1, 2, 3, 4]}, {"nums": [3, 1, 4, 2]}, {"nums": [-1, 3, 2, 0]}],
    hidden=[{"nums": [1]}, {"nums": [1, 2]}, {"nums": [3, 5, 0, 3, 4]},
            {"nums": [-2, 1, 2, -2, 1, 2]}],
    gen=lambda r: [{"nums": [r.randint(-5, 5) for _ in range(r.randint(1, 10))]}
                   for _ in range(6)],
    brute=_p132_brute,
    checks=[({"nums": [1, 2, 3, 4]}, False), ({"nums": [3, 1, 4, 2]}, True),
            ({"nums": [-1, 3, 2, 0]}, True)],
    source="new_p")


# ===========================================================================
# 10. Maximum Non Negative Product in a Matrix
# ===========================================================================
add("maximum-non-negative-product-in-a-matrix",
    "Maximum Non Negative Product in a Matrix", "medium",
    ["array", "dynamic-programming", "matrix"], "maxProductPath",
    [("grid", "int[][]")], "int",
    """
From the top-left to the bottom-right of `grid`, moving only right or down, **return
the maximum non-negative product** of the visited cells, modulo `10^9 + 7`. If every
path has a negative product, return `-1`. (The modulo is applied after taking the
maximum.)

**Examples**
```
grid = [[1,-2,1],[1,-2,1],[3,-4,1]]  ->  8
grid = [[1,3],[0,-4]]                ->  0
grid = [[-1,-2,-3],[-2,-3,-3],[-3,-3,-2]]  ->  -1
```

**Constraints:** `1 <= rows, cols <= 15`, `-4 <= grid[i][j] <= 4`.
""",
    """def maxProductPath(grid):
    MOD = 10 ** 9 + 7
    m, n = len(grid), len(grid[0])
    mx = [[0] * n for _ in range(m)]
    mn = [[0] * n for _ in range(m)]
    mx[0][0] = mn[0][0] = grid[0][0]
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            g = grid[i][j]
            cand = []
            if i > 0:
                cand += [mx[i - 1][j] * g, mn[i - 1][j] * g]
            if j > 0:
                cand += [mx[i][j - 1] * g, mn[i][j - 1] * g]
            mx[i][j] = max(cand)
            mn[i][j] = min(cand)
    res = mx[m - 1][n - 1]
    return res % MOD if res >= 0 else -1
""",
    visible=[{"grid": [[1, -2, 1], [1, -2, 1], [3, -4, 1]]},
             {"grid": [[1, 3], [0, -4]]},
             {"grid": [[-1, -2, -3], [-2, -3, -3], [-3, -3, -2]]}],
    hidden=[{"grid": [[1, 4, 4, 0], [-2, 0, 0, 1], [1, -1, 1, 1]]}, {"grid": [[2]]},
            {"grid": [[-1]]}, {"grid": [[1, 2], [3, 4]]}],
    gen=lambda r: [_maxprod_gen(r) for _ in range(6)],
    brute=_maxprod_brute,
    checks=[({"grid": [[1, -2, 1], [1, -2, 1], [3, -4, 1]]}, 8),
            ({"grid": [[1, 3], [0, -4]]}, 0),
            ({"grid": [[-1, -2, -3], [-2, -3, -3], [-3, -3, -2]]}, -1),
            ({"grid": [[1, 4, 4, 0], [-2, 0, 0, 1], [1, -1, 1, 1]]}, 2)],
    source="new_p")


# ===========================================================================
# 11. Valid Number
# ===========================================================================
add("valid-number", "Valid Number", "hard",
    ["string"], "isNumber", [("s", "string")], "bool",
    """
**Return `true` if `s` is a valid number.** A valid number may have leading/trailing
spaces, an optional sign, an integer or decimal mantissa (e.g. `"3"`, `"3.5"`,
`".5"`, `"5."`), and an optional exponent `e`/`E` followed by an optional sign and an
integer.

**Examples**
```
"0"     ->  true
" 0.1 " ->  true
"abc"   ->  false
"1 a"   ->  false
"2e10"  ->  true
```

**Constraints:** `1 <= len(s) <= 20`, ASCII characters.
""",
    """def isNumber(s):
    import re
    return re.fullmatch(r'\\s*[+-]?(\\d+\\.?\\d*|\\.\\d+)([eE][+-]?\\d+)?\\s*', s) is not None
""",
    visible=[{"s": "0"}, {"s": " 0.1 "}, {"s": "abc"}, {"s": "1 a"}, {"s": "2e10"}],
    hidden=[{"s": "."}, {"s": " "}, {"s": "e9"}, {"s": "-.8"}, {"s": "+"},
            {"s": "1."}, {"s": ".1"}, {"s": "4e+6"}, {"s": "99e2.5"}, {"s": "53.5e93"}],
    checks=[({"s": "0"}, True), ({"s": " 0.1 "}, True), ({"s": "abc"}, False),
            ({"s": "1 a"}, False), ({"s": "2e10"}, True), ({"s": "."}, False),
            ({"s": "e9"}, False), ({"s": "-.8"}, True), ({"s": "99e2.5"}, False),
            ({"s": "53.5e93"}, True)],
    source="new_p")


# ===========================================================================
# 12. Angle Between Hands of a Clock
# ===========================================================================
add("angle-between-hands-of-a-clock", "Angle Between Hands of a Clock", "medium",
    ["math"], "angleClock", [("hour", "int"), ("minutes", "int")], "float",
    """
**Return the smaller angle, in degrees, between the hour and minute hands** of a clock
showing `hour:minutes` (rounded to 5 decimals).

**Examples**
```
hour = 12, minutes = 30  ->  165.0
hour = 3, minutes = 30   ->  75.0
hour = 3, minutes = 15   ->  7.5
```

**Constraints:** `1 <= hour <= 12`, `0 <= minutes <= 59`.
""",
    """def angleClock(hour, minutes):
    minute_angle = minutes * 6
    hour_angle = (hour % 12) * 30 + minutes * 0.5
    diff = abs(hour_angle - minute_angle)
    return round(min(diff, 360 - diff), 5)
""",
    visible=[{"hour": 12, "minutes": 30}, {"hour": 3, "minutes": 30},
             {"hour": 3, "minutes": 15}],
    hidden=[{"hour": 4, "minutes": 50}, {"hour": 12, "minutes": 0}, {"hour": 1, "minutes": 0},
            {"hour": 6, "minutes": 0}],
    gen=lambda r: [{"hour": r.randint(1, 12), "minutes": r.randint(0, 59)}
                   for _ in range(8)],
    brute=_clock_brute,
    checks=[({"hour": 12, "minutes": 30}, 165.0), ({"hour": 3, "minutes": 30}, 75.0),
            ({"hour": 3, "minutes": 15}, 7.5), ({"hour": 4, "minutes": 50}, 155.0),
            ({"hour": 12, "minutes": 0}, 0.0)],
    source="new_p")


# ===========================================================================
# 13. Jump Game IV
# ===========================================================================
add("jump-game-iv", "Jump Game IV", "hard",
    ["array", "hash-table", "breadth-first-search"], "minJumps",
    [("arr", "int[]")], "int",
    """
Starting at index `0`, in one step you may move to `i+1`, `i-1`, or any index `j`
with `arr[j] == arr[i]`. **Return the minimum number of steps to reach the last
index.**

**Examples**
```
arr = [100,-23,-23,404,100,23,23,23,3,404]  ->  3
arr = [7]                                    ->  0
arr = [7,6,9,6,9,6,9,7]                      ->  1
```

**Constraints:** `1 <= len(arr) <= 5*10^4`, `-10^8 <= arr[i] <= 10^8`.
""",
    """def minJumps(arr):
    from collections import deque, defaultdict
    n = len(arr)
    if n == 1:
        return 0
    idx = defaultdict(list)
    for i, v in enumerate(arr):
        idx[v].append(i)
    visited = [False] * n
    visited[0] = True
    q = deque([(0, 0)])
    while q:
        i, steps = q.popleft()
        if i == n - 1:
            return steps
        nbrs = [i - 1, i + 1] + idx[arr[i]]
        idx[arr[i]] = []
        for j in nbrs:
            if 0 <= j < n and not visited[j]:
                visited[j] = True
                q.append((j, steps + 1))
    return -1
""",
    visible=[{"arr": [100, -23, -23, 404, 100, 23, 23, 23, 3, 404]}, {"arr": [7]},
             {"arr": [7, 6, 9, 6, 9, 6, 9, 7]}],
    hidden=[{"arr": [6, 1, 9]}, {"arr": [11, 22, 7, 7, 7, 7, 7, 7, 7, 22, 13]},
            {"arr": [1, 1, 1, 1]}, {"arr": [1, 2]}],
    gen=lambda r: [{"arr": [r.randint(1, 5) for _ in range(r.randint(1, 12))]}
                   for _ in range(6)],
    brute=_jump4_brute,
    checks=[({"arr": [100, -23, -23, 404, 100, 23, 23, 23, 3, 404]}, 3),
            ({"arr": [7]}, 0), ({"arr": [7, 6, 9, 6, 9, 6, 9, 7]}, 1),
            ({"arr": [6, 1, 9]}, 2)],
    source="new_p")


# ===========================================================================
# 14. Minimum Deletion Cost to Avoid Repeating Letters
# ===========================================================================
add("minimum-deletion-cost-to-avoid-repeating-letters",
    "Minimum Deletion Cost to Avoid Repeating Letters", "medium",
    ["array", "string", "greedy", "dynamic-programming"], "minCost",
    [("s", "string"), ("cost", "int[]")], "int",
    """
`cost[i]` is the cost of deleting `s[i]`. **Return the minimum total cost to delete
characters so that no two equal letters are adjacent.**

**Examples**
```
s = "abaac", cost = [1,2,3,4,5]  ->  3
s = "abc", cost = [1,2,3]        ->  0
s = "aabaa", cost = [1,2,3,4,1]  ->  2
```

**Constraints:** `1 <= len(s) == len(cost) <= 10^5`, `1 <= cost[i] <= 10^4`,
lowercase letters.
""",
    """def minCost(s, cost):
    total = 0
    i = 0
    n = len(s)
    while i < n:
        j = i
        run_sum = 0
        run_max = 0
        while j < n and s[j] == s[i]:
            run_sum += cost[j]
            run_max = max(run_max, cost[j])
            j += 1
        total += run_sum - run_max
        i = j
    return total
""",
    visible=[{"s": "abaac", "cost": [1, 2, 3, 4, 5]}, {"s": "abc", "cost": [1, 2, 3]},
             {"s": "aabaa", "cost": [1, 2, 3, 4, 1]}],
    hidden=[{"s": "a", "cost": [5]}, {"s": "aa", "cost": [3, 4]},
            {"s": "aaa", "cost": [1, 2, 3]}, {"s": "abab", "cost": [1, 1, 1, 1]}],
    gen=lambda r: [(lambda n: {"s": sstr(r, n, n, "ab"), "cost": [r.randint(1, 5) for _ in range(n)]})
                   (r.randint(1, 8)) for _ in range(6)],
    brute=_delcost_brute,
    checks=[({"s": "abaac", "cost": [1, 2, 3, 4, 5]}, 3),
            ({"s": "abc", "cost": [1, 2, 3]}, 0),
            ({"s": "aabaa", "cost": [1, 2, 3, 4, 1]}, 2)],
    source="new_p")


# ===========================================================================
# 15. Tallest Billboard
# ===========================================================================
add("tallest-billboard", "Tallest Billboard", "hard",
    ["array", "dynamic-programming"], "tallestBillboard", [("rods", "int[]")], "int",
    """
Split some of the `rods` into two disjoint groups of **equal sum** (welding the rods
in each group). **Return the largest achievable equal sum** (each group's total
height), or `0` if no nonempty equal split exists.

**Examples**
```
rods = [1,2,3,6]      ->  6
rods = [1,2,3,4,5,6]  ->  10
rods = [1,2]          ->  0
```

**Constraints:** `0 <= len(rods) <= 20`, `1 <= rods[i] <= 1000`, `sum <= 5000`.
""",
    """def tallestBillboard(rods):
    dp = {0: 0}
    for r in rods:
        cur = {}
        for d, t in dp.items():
            cur[d] = max(cur.get(d, 0), t)
            cur[d + r] = max(cur.get(d + r, 0), t + r)
            nd = abs(d - r)
            cur[nd] = max(cur.get(nd, 0), t + max(0, r - d))
        dp = cur
    return dp[0]
""",
    visible=[{"rods": [1, 2, 3, 6]}, {"rods": [1, 2, 3, 4, 5, 6]}, {"rods": [1, 2]}],
    hidden=[{"rods": []}, {"rods": [2, 4, 8, 16]}, {"rods": [3, 3]},
            {"rods": [1, 1, 1, 1, 1]}],
    gen=lambda r: [{"rods": [r.randint(1, 6) for _ in range(r.randint(0, 7))]}
                   for _ in range(6)],
    brute=_billboard_brute,
    checks=[({"rods": [1, 2, 3, 6]}, 6), ({"rods": [1, 2, 3, 4, 5, 6]}, 10),
            ({"rods": [1, 2]}, 0), ({"rods": [3, 3]}, 3)],
    source="new_p")


# ===========================================================================
# 16. Minimum Number of Steps to Make Two Strings Anagram
# ===========================================================================
add("minimum-number-of-steps-to-make-two-strings-anagram",
    "Minimum Number of Steps to Make Two Strings Anagram", "medium",
    ["string", "hash-table", "counting"], "minSteps",
    [("s", "string"), ("t", "string")], "int",
    """
`s` and `t` have equal length. In one step you may replace any character of `t` with
another. **Return the minimum number of steps to make `t` an anagram of `s`.**

**Examples**
```
s = "bab", t = "aba"            ->  1
s = "leetcode", t = "practice"  ->  5
s = "anagram", t = "mangaar"    ->  0
```

**Constraints:** `1 <= len(s) == len(t) <= 5*10^4`, lowercase letters.
""",
    """def minSteps(s, t):
    from collections import Counter
    cs = Counter(s)
    ct = Counter(t)
    return sum((ct - cs).values())
""",
    visible=[{"s": "bab", "t": "aba"}, {"s": "leetcode", "t": "practice"},
             {"s": "anagram", "t": "mangaar"}],
    hidden=[{"s": "a", "t": "a"}, {"s": "ab", "t": "ba"}, {"s": "xxyyzz", "t": "xxyyzz"},
            {"s": "friend", "t": "family"}],
    gen=lambda r: [(lambda n: {"s": sstr(r, n, n, "abc"), "t": sstr(r, n, n, "abc")})
                   (r.randint(1, 8)) for _ in range(6)],
    brute=_anagram_brute,
    checks=[({"s": "bab", "t": "aba"}, 1), ({"s": "leetcode", "t": "practice"}, 5),
            ({"s": "anagram", "t": "mangaar"}, 0), ({"s": "friend", "t": "family"}, 4)],
    source="new_p")


# ===========================================================================
# 17. Gas Station
# ===========================================================================
add("gas-station", "Gas Station", "medium",
    ["array", "greedy"], "canCompleteCircuit",
    [("gas", "int[]"), ("cost", "int[]")], "int",
    """
On a circular route, station `i` has `gas[i]` fuel and it costs `cost[i]` to drive to
station `i+1`. Starting with an empty tank, **return the starting station index from
which you can complete the full circuit**, or `-1` if impossible. (A solution, if it
exists, is unique.)

**Examples**
```
gas = [1,2,3,4,5], cost = [3,4,5,1,2]  ->  3
gas = [2,3,4], cost = [3,4,3]          ->  -1
```

**Constraints:** `1 <= len(gas) == len(cost) <= 10^5`, `0 <= gas[i], cost[i]`.
""",
    """def canCompleteCircuit(gas, cost):
    total = 0
    tank = 0
    start = 0
    for i in range(len(gas)):
        diff = gas[i] - cost[i]
        total += diff
        tank += diff
        if tank < 0:
            start = i + 1
            tank = 0
    return start if total >= 0 else -1
""",
    visible=[{"gas": [1, 2, 3, 4, 5], "cost": [3, 4, 5, 1, 2]},
             {"gas": [2, 3, 4], "cost": [3, 4, 3]}],
    hidden=[{"gas": [5], "cost": [4]}, {"gas": [2], "cost": [2]},
            {"gas": [3, 1, 1], "cost": [1, 2, 2]}, {"gas": [0], "cost": [1]}],
    gen=lambda r: [(lambda n: {"gas": [r.randint(0, 5) for _ in range(n)],
                               "cost": [r.randint(0, 5) for _ in range(n)]})
                   (r.randint(1, 8)) for _ in range(6)],
    brute=_gas_brute,
    checks=[({"gas": [1, 2, 3, 4, 5], "cost": [3, 4, 5, 1, 2]}, 3),
            ({"gas": [2, 3, 4], "cost": [3, 4, 3]}, -1), ({"gas": [5], "cost": [4]}, 0)],
    source="new_p")


# ===========================================================================
# 18. Find All Good Strings
# ===========================================================================
add("find-all-good-strings", "Find All Good Strings", "hard",
    ["string", "dynamic-programming", "string-matching"], "findGoodStrings",
    [("n", "int"), ("s1", "string"), ("s2", "string"), ("evil", "string")], "int",
    """
A *good string* has length `n`, is `>= s1` and `<= s2` lexicographically, and does
**not** contain `evil` as a substring. **Return the number of good strings, modulo
`10^9 + 7`.**

**Examples**
```
n = 2, s1 = "aa", s2 = "da", evil = "b"            ->  51
n = 8, s1 = "leetcode", s2 = "leetgoes", evil = "leet" ->  0
n = 2, s1 = "gx", s2 = "gz", evil = "x"            ->  2
```

**Constraints:** `len(s1) == len(s2) == n`, `s1 <= s2`, `1 <= n <= 500`,
`1 <= len(evil) <= 50`, lowercase letters.
""",
    """def findGoodStrings(n, s1, s2, evil):
    MOD = 10 ** 9 + 7
    m = len(evil)
    fail = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and evil[i] != evil[k]:
            k = fail[k - 1]
        if evil[i] == evil[k]:
            k += 1
        fail[i] = k

    def trans(j, c):
        while j > 0 and c != evil[j]:
            j = fail[j - 1]
        if c == evil[j]:
            j += 1
        return j

    from functools import lru_cache

    @lru_cache(None)
    def dp(pos, matched, lowtight, hightight):
        if matched == m:
            return 0
        if pos == n:
            return 1
        lo = ord(s1[pos]) - 97 if lowtight else 0
        hi = ord(s2[pos]) - 97 if hightight else 25
        total = 0
        for c in range(lo, hi + 1):
            total += dp(pos + 1, trans(matched, chr(c + 97)),
                        lowtight and c == lo, hightight and c == hi)
        return total % MOD

    return dp(0, 0, True, True) % MOD
""",
    visible=[{"n": 2, "s1": "aa", "s2": "da", "evil": "b"},
             {"n": 2, "s1": "gx", "s2": "gz", "evil": "x"}],
    hidden=[{"n": 1, "s1": "a", "s2": "c", "evil": "b"},
            {"n": 2, "s1": "aa", "s2": "bb", "evil": "ab"},
            {"n": 3, "s1": "aaa", "s2": "aaa", "evil": "a"},
            {"n": 2, "s1": "aa", "s2": "zz", "evil": "z"}],
    gen=lambda r: [_goodstr_gen(r) for _ in range(6)],
    brute=_goodstr_brute,
    checks=[({"n": 2, "s1": "aa", "s2": "da", "evil": "b"}, 51),
            ({"n": 8, "s1": "leetcode", "s2": "leetgoes", "evil": "leet"}, 0),
            ({"n": 2, "s1": "gx", "s2": "gz", "evil": "x"}, 2)],
    source="new_p")


# ===========================================================================
# 19. Number of Ways Where Square of Number Equals Product of Two Numbers
# ===========================================================================
add("number-of-ways-where-square-of-number-is-equal-to-product-of-two-numbers",
    "Number of Ways Where Square of Number Equals Product of Two Numbers", "medium",
    ["array", "hash-table", "math", "two-pointers"], "numTriplets",
    [("nums1", "int[]"), ("nums2", "int[]")], "int",
    """
Count triplets of two kinds:
- Type 1: `(i, j, k)` with `nums1[i]^2 == nums2[j] * nums2[k]`, `j < k`.
- Type 2: `(i, j, k)` with `nums2[i]^2 == nums1[j] * nums1[k]`, `j < k`.

**Return the total number of such triplets.**

**Examples**
```
nums1 = [7,4], nums2 = [5,2,8,9]      ->  1
nums1 = [1,1], nums2 = [1,1,1]        ->  9
nums1 = [7,7,8,3], nums2 = [1,2,9,7]  ->  2
```

**Constraints:** `1 <= len(nums1), len(nums2) <= 1000`, `1 <= nums[i] <= 10^5`.
""",
    """def numTriplets(nums1, nums2):
    from collections import Counter

    def count(a, b):
        res = 0
        for x in a:
            sq = x * x
            seen = Counter()
            for v in b:
                if sq % v == 0 and (sq // v) in seen:
                    res += seen[sq // v]
                seen[v] += 1
        return res

    return count(nums1, nums2) + count(nums2, nums1)
""",
    visible=[{"nums1": [7, 4], "nums2": [5, 2, 8, 9]},
             {"nums1": [1, 1], "nums2": [1, 1, 1]},
             {"nums1": [7, 7, 8, 3], "nums2": [1, 2, 9, 7]}],
    hidden=[{"nums1": [4, 7, 9, 11, 23], "nums2": [3, 5, 1024, 12, 18]},
            {"nums1": [1], "nums2": [1]}, {"nums1": [2, 2], "nums2": [4, 1]},
            {"nums1": [3], "nums2": [9, 1, 3]}],
    gen=lambda r: [{"nums1": [r.randint(1, 10) for _ in range(r.randint(1, 6))],
                    "nums2": [r.randint(1, 10) for _ in range(r.randint(1, 6))]}
                   for _ in range(6)],
    brute=_triplets_brute,
    checks=[({"nums1": [7, 4], "nums2": [5, 2, 8, 9]}, 1),
            ({"nums1": [1, 1], "nums2": [1, 1, 1]}, 9),
            ({"nums1": [7, 7, 8, 3], "nums2": [1, 2, 9, 7]}, 2),
            ({"nums1": [4, 7, 9, 11, 23], "nums2": [3, 5, 1024, 12, 18]}, 0)],
    source="new_p")
