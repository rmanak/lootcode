"""Batch 009 of the new_p.txt import (18 problems).

Two entries from this slice were dropped as duplicates under different slugs (see
`_skips.py`): `partition-array-for-maximum-sum` (== `partition-array-max-sum`) and
`candy` (== `candy-distribution`).
"""
from scripts.build_bank import add, ilist, sstr  # noqa: F401


# --------------------------- brute / reference helpers ---------------------
def _validpath_brute(grid):
    import heapq
    m, n = len(grid), len(grid[0])
    dirs = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}
    dist = [[float('inf')] * n for _ in range(m)]
    dist[0][0] = 0
    pq = [(0, 0, 0)]
    while pq:
        d, i, j = heapq.heappop(pq)
        if d > dist[i][j]:
            continue
        for dr in range(1, 5):
            di, dj = dirs[dr]
            ni, nj = i + di, j + dj
            c = 0 if grid[i][j] == dr else 1
            if 0 <= ni < m and 0 <= nj < n and d + c < dist[ni][nj]:
                dist[ni][nj] = d + c
                heapq.heappush(pq, (d + c, ni, nj))
    return dist[m - 1][n - 1]


def _leastops_brute(x, target):
    import heapq
    powers = []
    a, p = 0, 1
    while p <= 2 * target + x:
        powers.append((p, 2 if a == 0 else a))
        a += 1
        p *= x
        if a > 40:
            break
    LIM = 2 * target + 2 * x
    dist = {0: 0}
    pq = [(0, 0)]
    while pq:
        d, v = heapq.heappop(pq)
        if v == target:
            return d - 1
        if d > dist.get(v, float('inf')):
            continue
        for p, c in powers:
            for sign in (1, -1):
                nv = v + sign * p
                if abs(nv) > LIM:
                    continue
                if d + c < dist.get(nv, float('inf')):
                    dist[nv] = d + c
                    heapq.heappush(pq, (d + c, nv))
    return -1


def _lcs_brute(A, B):
    from functools import lru_cache

    @lru_cache(None)
    def f(i, j):
        if i == len(A) or j == len(B):
            return 0
        if A[i] == B[j]:
            return 1 + f(i + 1, j + 1)
        return max(f(i + 1, j), f(i, j + 1))
    return f(0, 0)


def _square_brute(p1, p2, p3, p4):
    from itertools import permutations
    pts = [p1, p2, p3, p4]

    def d2(a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

    for perm in permutations(pts):
        a, b, c, d = perm
        s = [d2(a, b), d2(b, c), d2(c, d), d2(d, a)]
        if s[0] > 0 and len(set(s)) == 1 and d2(a, c) == d2(b, d) and d2(a, c) == 2 * s[0]:
            return True
    return False


def _friends_brute(ages):
    n = len(ages)
    res = 0
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            a, b = ages[i], ages[j]
            if b <= 0.5 * a + 7 or b > a or (b > 100 and a < 100):
                continue
            res += 1
    return res


def _echo_brute(text):
    n = len(text)
    s = set()
    for i in range(n):
        for j in range(i + 2, n + 1, 2):
            sub = text[i:j]
            h = len(sub) // 2
            if sub[:h] == sub[h:]:
                s.add(sub)
    return len(s)


def _cs4_brute(nums, target):
    from functools import lru_cache

    @lru_cache(None)
    def f(t):
        if t == 0:
            return 1
        return sum(f(t - x) for x in nums if x <= t)
    return f(target)


def _monodigit_brute(N):
    for v in range(N, -1, -1):
        s = str(v)
        if all(s[i] <= s[i + 1] for i in range(len(s) - 1)):
            return v
    return 0


def _shortsub_brute(A, K):
    n = len(A)
    best = n + 1
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += A[j]
            if s >= K:
                best = min(best, j - i + 1)
                break
    return best if best <= n else -1


def _bouquet_brute(bloomDay, m, k):
    if m * k > len(bloomDay):
        return -1

    def can(day):
        b = f = 0
        for x in bloomDay:
            if x <= day:
                f += 1
                if f == k:
                    b += 1
                    f = 0
            else:
                f = 0
        return b >= m

    for d in sorted(set(bloomDay)):
        if can(d):
            return d
    return -1


def _numsub_brute(s):
    n = len(s)
    c = 0
    for i in range(n):
        j = i
        while j < n and s[j] == '1':
            c += 1
            j += 1
    return c % (10 ** 9 + 7)


def _swap_brute(s1, s2):
    from collections import deque
    if s1 == s2:
        return 0
    n = len(s1)
    seen = {(s1, s2)}
    q = deque([(s1, s2, 0)])
    while q:
        a, b, d = q.popleft()
        for i in range(n):
            for j in range(n):
                if a[i] != b[j]:
                    na = a[:i] + b[j] + a[i + 1:]
                    nb = b[:j] + a[i] + b[j + 1:]
                    if na == nb:
                        return d + 1
                    st = (na, nb)
                    if st not in seen:
                        seen.add(st)
                        q.append((na, nb, d + 1))
    return -1


def _prefix_brute(s):
    n = len(s)
    for L in range(n - 1, 0, -1):
        if s[:L] == s[n - L:]:
            return s[:L]
    return ""


def _diperms_brute(S):
    from itertools import permutations
    n = len(S)
    cnt = 0
    for p in permutations(range(n + 1)):
        ok = True
        for i, c in enumerate(S):
            if c == 'I' and not p[i] < p[i + 1]:
                ok = False
                break
            if c == 'D' and not p[i] > p[i + 1]:
                ok = False
                break
        if ok:
            cnt += 1
    return cnt % (10 ** 9 + 7)


def _pizza_brute(slices):
    from itertools import combinations
    n = len(slices)
    k = n // 3
    best = 0
    for combo in combinations(range(n), k):
        cs = set(combo)
        if all((c + 1) % n not in cs for c in combo):
            best = max(best, sum(slices[c] for c in combo))
    return best


# gen helpers ---------------------------------------------------------------
def _numstr(r):
    n = r.randint(1, 4)
    first = str(r.randint(1, 9)) if n > 1 else str(r.randint(0, 9))
    return first + "".join(str(r.randint(0, 9)) for _ in range(n - 1))


def _validpath_gen(r):
    rows, cols = r.randint(1, 4), r.randint(1, 4)
    return {"grid": [[r.randint(1, 4) for _ in range(cols)] for _ in range(rows)]}


def _bouquet_gen(r):
    n = r.randint(1, 10)
    k = r.randint(1, n)
    m = r.randint(1, n // k + 1)
    return {"bloomDay": [r.randint(1, 15) for _ in range(n)], "m": m, "k": k}


def _pizza_gen(r):
    nn = r.randint(1, 2) * 3
    return {"slices": [r.randint(1, 10) for _ in range(nn)]}


# ===========================================================================
# 1. Multiply Strings
# ===========================================================================
add("multiply-strings", "Multiply Strings", "medium",
    ["string", "math", "simulation"], "multiply",
    [("num1", "string"), ("num2", "string")], "string",
    """
Given two non-negative integers `num1` and `num2` represented as strings (no leading
zeros except `"0"` itself), **return their product, also as a string.** Do not
convert the inputs to integers directly.

**Examples**
```
num1 = "2", num2 = "3"      ->  "6"
num1 = "123", num2 = "456"  ->  "56088"
```

**Constraints:** `1 <= len(num1), len(num2) < 110`, digits only.
""",
    """def multiply(num1, num2):
    if num1 == "0" or num2 == "0":
        return "0"
    n, m = len(num1), len(num2)
    res = [0] * (n + m)
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            mul = (ord(num1[i]) - 48) * (ord(num2[j]) - 48)
            p1, p2 = i + j, i + j + 1
            total = mul + res[p2]
            res[p2] = total % 10
            res[p1] += total // 10
    s = "".join(map(str, res)).lstrip("0")
    return s if s else "0"
""",
    visible=[{"num1": "2", "num2": "3"}, {"num1": "123", "num2": "456"}],
    hidden=[{"num1": "0", "num2": "52"}, {"num1": "9", "num2": "9"},
            {"num1": "99", "num2": "99"}, {"num1": "100", "num2": "100"},
            {"num1": "1", "num2": "999"}],
    gen=lambda r: [{"num1": _numstr(r), "num2": _numstr(r)} for _ in range(8)],
    brute=lambda num1, num2: str(int(num1) * int(num2)),
    checks=[({"num1": "2", "num2": "3"}, "6"), ({"num1": "123", "num2": "456"}, "56088"),
            ({"num1": "0", "num2": "52"}, "0")],
    source="new_p")


# ===========================================================================
# 2. Minimum Cost to Make at Least One Valid Path in a Grid
# ===========================================================================
add("minimum-cost-to-make-at-least-one-valid-path-in-a-grid",
    "Minimum Cost to Make at Least One Valid Path in a Grid", "hard",
    ["array", "breadth-first-search", "graph", "matrix", "shortest-path"], "minCost",
    [("grid", "int[][]")], "int",
    """
Each cell holds an arrow: `1` right, `2` left, `3` down, `4` up. Starting at `(0,0)`
you follow arrows; you want to reach `(m-1, n-1)`. Changing one cell's arrow costs
`1` (each cell at most once). **Return the minimum total cost to create at least one
valid path** from top-left to bottom-right.

**Examples**
```
grid = [[1,1,1,1],[2,2,2,2],[1,1,1,1],[2,2,2,2]]  ->  3
grid = [[1,1,3],[3,2,2],[1,1,4]]                  ->  0
grid = [[1,2],[4,3]]                              ->  1
```

**Constraints:** `1 <= m, n <= 100`, `grid[i][j]` in `{1,2,3,4}`.
""",
    """def minCost(grid):
    from collections import deque
    m, n = len(grid), len(grid[0])
    dirs = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}
    dist = [[float('inf')] * n for _ in range(m)]
    dist[0][0] = 0
    dq = deque([(0, 0)])
    while dq:
        i, j = dq.popleft()
        for d in range(1, 5):
            di, dj = dirs[d]
            ni, nj = i + di, j + dj
            cost = 0 if grid[i][j] == d else 1
            if 0 <= ni < m and 0 <= nj < n and dist[i][j] + cost < dist[ni][nj]:
                dist[ni][nj] = dist[i][j] + cost
                if cost == 0:
                    dq.appendleft((ni, nj))
                else:
                    dq.append((ni, nj))
    return dist[m - 1][n - 1]
""",
    visible=[{"grid": [[1, 1, 1, 1], [2, 2, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2]]},
             {"grid": [[1, 1, 3], [3, 2, 2], [1, 1, 4]]}, {"grid": [[1, 2], [4, 3]]}],
    hidden=[{"grid": [[2, 2, 2], [2, 2, 2]]}, {"grid": [[4]]}, {"grid": [[1]]},
            {"grid": [[3, 1], [1, 1]]}],
    gen=lambda r: [_validpath_gen(r) for _ in range(6)],
    brute=_validpath_brute,
    checks=[({"grid": [[1, 1, 1, 1], [2, 2, 2, 2], [1, 1, 1, 1], [2, 2, 2, 2]]}, 3),
            ({"grid": [[1, 1, 3], [3, 2, 2], [1, 1, 4]]}, 0),
            ({"grid": [[1, 2], [4, 3]]}, 1), ({"grid": [[2, 2, 2], [2, 2, 2]]}, 3),
            ({"grid": [[4]]}, 0)],
    source="new_p")


# ===========================================================================
# 3. Least Operators to Express Number
# ===========================================================================
add("least-operators-to-express-number", "Least Operators to Express Number", "hard",
    ["math", "dynamic-programming", "memoization"], "leastOpsExpressTarget",
    [("x", "int"), ("target", "int")], "int",
    """
Build an expression `x op x op x ...` using only `+ - * /` (usual precedence, no
parentheses, no unary minus). Division yields rationals. **Return the least number of
operators needed for the expression to equal `target`.**

**Examples**
```
x = 3, target = 19          ->  5    (3*3 + 3*3 + 3/3)
x = 5, target = 501         ->  8
x = 100, target = 100000000 ->  3    (100*100*100*100)
```

**Constraints:** `2 <= x <= 100`, `1 <= target <= 2*10^8`.
""",
    """def leastOpsExpressTarget(x, target):
    from functools import lru_cache

    @lru_cache(None)
    def dp(t):
        if t == 0:
            return 0
        if t < x:
            return min(2 * t - 1, 2 * (x - t))
        k = 0
        p = 1
        while p * x <= t:
            p *= x
            k += 1
        rem = t - p
        cost_under = (k - 1) + (0 if rem == 0 else 1 + dp(rem))
        rem2 = p * x - t
        if rem2 < t:
            return min(cost_under, k + 1 + dp(rem2))
        return cost_under

    return dp(target)
""",
    visible=[{"x": 3, "target": 19}, {"x": 5, "target": 30}],
    hidden=[{"x": 3, "target": 9}, {"x": 2, "target": 1}, {"x": 4, "target": 20},
            {"x": 2, "target": 25}],
    gen=lambda r: [{"x": r.randint(2, 5), "target": r.randint(1, 30)} for _ in range(8)],
    brute=_leastops_brute,
    checks=[({"x": 3, "target": 19}, 5), ({"x": 5, "target": 501}, 8),
            ({"x": 100, "target": 100000000}, 3), ({"x": 3, "target": 9}, 1)],
    source="new_p")


# ===========================================================================
# 4. Uncrossed Lines
# ===========================================================================
add("uncrossed-lines", "Uncrossed Lines", "medium",
    ["array", "dynamic-programming"], "maxUncrossedLines",
    [("A", "int[]"), ("B", "int[]")], "int",
    """
Write `A` and `B` on two rows. You may connect `A[i]` to `B[j]` with a line when
`A[i] == B[j]`, but lines must not cross and each number joins at most one line.
**Return the maximum number of connecting lines** (this equals the length of the
longest common subsequence).

**Examples**
```
A = [1,4,2], B = [1,2,4]                  ->  2
A = [2,5,1,2,5], B = [10,5,2,1,5,2]       ->  3
A = [1,3,7,1,7,5], B = [1,9,2,5,1]        ->  2
```

**Constraints:** `1 <= len(A), len(B) <= 500`, `1 <= A[i], B[i] <= 2000`.
""",
    """def maxUncrossedLines(A, B):
    n, m = len(A), len(B)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if A[i - 1] == B[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]
""",
    visible=[{"A": [1, 4, 2], "B": [1, 2, 4]},
             {"A": [2, 5, 1, 2, 5], "B": [10, 5, 2, 1, 5, 2]},
             {"A": [1, 3, 7, 1, 7, 5], "B": [1, 9, 2, 5, 1]}],
    hidden=[{"A": [1], "B": [1]}, {"A": [1], "B": [2]}, {"A": [1, 2, 3], "B": [3, 2, 1]},
            {"A": [2, 2, 2], "B": [2, 2]}],
    gen=lambda r: [{"A": [r.randint(1, 4) for _ in range(r.randint(1, 7))],
                    "B": [r.randint(1, 4) for _ in range(r.randint(1, 7))]} for _ in range(6)],
    brute=_lcs_brute,
    checks=[({"A": [1, 4, 2], "B": [1, 2, 4]}, 2),
            ({"A": [2, 5, 1, 2, 5], "B": [10, 5, 2, 1, 5, 2]}, 3),
            ({"A": [1, 3, 7, 1, 7, 5], "B": [1, 9, 2, 5, 1]}, 2)],
    source="new_p")


# ===========================================================================
# 5. Valid Square
# ===========================================================================
add("valid-square", "Valid Square", "medium",
    ["math", "geometry"], "validSquare",
    [("p1", "int[]"), ("p2", "int[]"), ("p3", "int[]"), ("p4", "int[]")], "bool",
    """
Given four points in the plane (each `[x, y]`, in no particular order), **return
`true` if they form a square** with positive side length.

**Example**
```
p1 = [0,0], p2 = [1,1], p3 = [1,0], p4 = [0,1]  ->  true
```

**Constraints:** coordinates in `[-10^4, 10^4]`.
""",
    """def validSquare(p1, p2, p3, p4):
    pts = [p1, p2, p3, p4]

    def d2(a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

    dists = sorted(d2(pts[i], pts[j]) for i in range(4) for j in range(i + 1, 4))
    if dists[0] == 0:
        return False
    return (dists[0] == dists[1] == dists[2] == dists[3] and
            dists[4] == dists[5] and dists[4] == 2 * dists[0])
""",
    visible=[{"p1": [0, 0], "p2": [1, 1], "p3": [1, 0], "p4": [0, 1]}],
    hidden=[{"p1": [0, 0], "p2": [1, 1], "p3": [1, 0], "p4": [0, 12]},
            {"p1": [0, 0], "p2": [0, 0], "p3": [0, 0], "p4": [0, 0]},
            {"p1": [1, 0], "p2": [-1, 0], "p3": [0, 1], "p4": [0, -1]},
            {"p1": [0, 0], "p2": [2, 0], "p3": [2, 2], "p4": [0, 2]}],
    gen=lambda r: [(lambda: {"p1": [r.randint(-3, 3), r.randint(-3, 3)],
                             "p2": [r.randint(-3, 3), r.randint(-3, 3)],
                             "p3": [r.randint(-3, 3), r.randint(-3, 3)],
                             "p4": [r.randint(-3, 3), r.randint(-3, 3)]})() for _ in range(8)],
    brute=_square_brute,
    checks=[({"p1": [0, 0], "p2": [1, 1], "p3": [1, 0], "p4": [0, 1]}, True),
            ({"p1": [0, 0], "p2": [1, 1], "p3": [1, 0], "p4": [0, 12]}, False),
            ({"p1": [1, 0], "p2": [-1, 0], "p3": [0, 1], "p4": [0, -1]}, True)],
    source="new_p")


# ===========================================================================
# 6. Friends of Appropriate Ages
# ===========================================================================
add("friends-of-appropriate-ages", "Friends of Appropriate Ages", "medium",
    ["array", "math", "sorting", "binary-search"], "numFriendRequests",
    [("ages", "int[]")], "int",
    """
Person `A` sends a friend request to person `B` (`A != B`) **unless** any of these
hold: `age[B] <= 0.5*age[A] + 7`, or `age[B] > age[A]`, or
`age[B] > 100 and age[A] < 100`. **Return the total number of friend requests
made.**

**Examples**
```
ages = [16,16]              ->  2
ages = [16,17,18]           ->  2
ages = [20,30,100,110,120]  ->  3
```

**Constraints:** `1 <= len(ages) <= 2*10^4`, `1 <= ages[i] <= 120`.
""",
    """def numFriendRequests(ages):
    from collections import Counter
    cnt = Counter(ages)
    res = 0
    for a in cnt:
        for b in cnt:
            if b <= 0.5 * a + 7 or b > a or (b > 100 and a < 100):
                continue
            res += cnt[a] * cnt[b] - (cnt[a] if a == b else 0)
    return res
""",
    visible=[{"ages": [16, 16]}, {"ages": [16, 17, 18]}, {"ages": [20, 30, 100, 110, 120]}],
    hidden=[{"ages": [1]}, {"ages": [120, 120]}, {"ages": [8, 16]},
            {"ages": [73, 106, 39, 6, 26, 15, 30, 100, 71, 35]}],
    gen=lambda r: [{"ages": [r.randint(10, 40) for _ in range(r.randint(1, 12))]}
                   for _ in range(6)],
    brute=_friends_brute,
    checks=[({"ages": [16, 16]}, 2), ({"ages": [16, 17, 18]}, 2),
            ({"ages": [20, 30, 100, 110, 120]}, 3)],
    source="new_p")


# ===========================================================================
# 7. Distinct Echo Substrings
# ===========================================================================
add("distinct-echo-substrings", "Distinct Echo Substrings", "hard",
    ["string", "hash-table", "rolling-hash"], "distinctEchoSubstrings",
    [("text", "string")], "int",
    """
**Return the number of distinct non-empty substrings of `text` that can be written as
`a + a`** (some string concatenated with itself).

**Examples**
```
text = "abcabcabc"        ->  3   ("abcabc", "bcabca", "cabcab")
text = "leetcodeleetcode" ->  2   ("ee", "leetcodeleetcode")
```

**Constraints:** `1 <= len(text) <= 2000`, lowercase letters.
""",
    """def distinctEchoSubstrings(text):
    n = len(text)
    seen = set()
    for i in range(n):
        for length in range(1, (n - i) // 2 + 1):
            half = text[i:i + length]
            if text[i + length:i + 2 * length] == half:
                seen.add(half + half)
    return len(seen)
""",
    visible=[{"text": "abcabcabc"}, {"text": "leetcodeleetcode"}],
    hidden=[{"text": "a"}, {"text": "aaaa"}, {"text": "abab"}, {"text": "abcde"}],
    gen=lambda r: [{"text": sstr(r, 1, 10, "ab")} for _ in range(6)],
    brute=_echo_brute,
    checks=[({"text": "abcabcabc"}, 3), ({"text": "leetcodeleetcode"}, 2),
            ({"text": "aaaa"}, 2)],
    source="new_p")


# ===========================================================================
# 8. Combination Sum IV
# ===========================================================================
add("combination-sum-iv", "Combination Sum IV", "medium",
    ["array", "dynamic-programming"], "combinationSum4",
    [("nums", "int[]"), ("target", "int")], "int",
    """
`nums` has distinct positive integers. **Return the number of ordered combinations
that sum to `target`** (different orderings count as different combinations).

**Example**
```
nums = [1,2,3], target = 4  ->  7
```

**Constraints:** `1 <= len(nums) <= 200`, distinct positive `nums[i]`,
`1 <= target <= 1000`.
""",
    """def combinationSum4(nums, target):
    dp = [0] * (target + 1)
    dp[0] = 1
    for t in range(1, target + 1):
        for x in nums:
            if x <= t:
                dp[t] += dp[t - x]
    return dp[target]
""",
    visible=[{"nums": [1, 2, 3], "target": 4}],
    hidden=[{"nums": [9], "target": 3}, {"nums": [1], "target": 5},
            {"nums": [2, 3], "target": 7}, {"nums": [1, 2, 3], "target": 0},
            {"nums": [4, 2, 1], "target": 6}],
    gen=lambda r: [(lambda nums: {"nums": nums, "target": r.randint(0, 15)})
                   (r.sample(range(1, 8), r.randint(1, 4))) for _ in range(6)],
    brute=_cs4_brute,
    checks=[({"nums": [1, 2, 3], "target": 4}, 7), ({"nums": [9], "target": 3}, 0),
            ({"nums": [1], "target": 5}, 1)],
    source="new_p")


# ===========================================================================
# 9. Soup Servings
# ===========================================================================
add("soup-servings", "Soup Servings", "medium",
    ["math", "dynamic-programming", "probability", "memoization"], "soupServings",
    [("n", "int")], "float",
    """
Two soups A and B start with `n` ml each. Each turn one of four operations is chosen
with probability `0.25`, serving `(A,B)` ml of `(100,0)`, `(75,25)`, `(50,50)`, or
`(25,75)` (serve as much as available if short). Stop when at least one soup is
empty. **Return P(A empties first) + 0.5 * P(both empty together)**, rounded to 5
decimals.

**Example**
```
n = 50  ->  0.62500
```

**Constraints:** `0 <= n <= 10^9` (answers within `1e-6` accepted).
""",
    """def soupServings(n):
    if n >= 4800:
        return 1.0
    from functools import lru_cache
    m = (n + 24) // 25

    @lru_cache(None)
    def dp(a, b):
        if a <= 0 and b <= 0:
            return 0.5
        if a <= 0:
            return 1.0
        if b <= 0:
            return 0.0
        return 0.25 * (dp(a - 4, b) + dp(a - 3, b - 1) +
                       dp(a - 2, b - 2) + dp(a - 1, b - 3))

    return round(dp(m, m), 5)
""",
    visible=[{"n": 50}, {"n": 0}, {"n": 25}],
    hidden=[{"n": 100}, {"n": 200}, {"n": 1}, {"n": 10000}],
    gen=lambda r: [{"n": r.randint(0, 200)} for _ in range(6)],
    checks=[({"n": 50}, 0.625), ({"n": 0}, 0.5), ({"n": 25}, 0.625),
            ({"n": 10000}, 1.0)],
    source="new_p")


# ===========================================================================
# 10. Tag Validator
# ===========================================================================
add("tag-validator", "Tag Validator", "hard",
    ["string", "stack"], "isValid", [("code", "string")], "bool",
    """
Validate a code snippet against these rules: it must be wrapped in one closed tag
`<TAG_NAME>...</TAG_NAME>` (matching names); a valid `TAG_NAME` is 1-9 upper-case
letters; tag content may contain nested valid closed tags, `cdata`, and any
characters except an unmatched `<`, an unmatched tag, or a closed tag with an invalid
name; `<![CDATA[ ... ]]>` content (up to the first `]]>`) is treated as raw text.
**Return `true` if the snippet is valid.**

**Examples**
```
"<DIV>This is the first line <![CDATA[<div>]]></DIV>"  ->  true
"<A>  <B> </A>   </B>"                                 ->  false
"<DIV>  unmatched <  </DIV>"                           ->  false
```

**Constraints:** the snippet uses only letters, digits, and `<>/![] ` (space).
""",
    """def isValid(code):
    if not code:
        return False
    n = len(code)
    i = 0
    stack = []
    while i < n:
        if code[i] == '<':
            if i + 1 < n and code[i + 1] == '!':
                if not stack:
                    return False
                if code[i:i + 9] != "<![CDATA[":
                    return False
                end = code.find("]]>", i + 9)
                if end == -1:
                    return False
                i = end + 3
            elif i + 1 < n and code[i + 1] == '/':
                end = code.find(">", i)
                if end == -1:
                    return False
                name = code[i + 2:end]
                if not (1 <= len(name) <= 9 and name.isalpha() and name.isupper()):
                    return False
                if not stack or stack[-1] != name:
                    return False
                stack.pop()
                i = end + 1
                if not stack and i < n:
                    return False
            else:
                end = code.find(">", i)
                if end == -1:
                    return False
                name = code[i + 1:end]
                if not (1 <= len(name) <= 9 and name.isalpha() and name.isupper()):
                    return False
                stack.append(name)
                i = end + 1
        else:
            if not stack:
                return False
            i += 1
    return len(stack) == 0
""",
    visible=[{"code": "<DIV>This is the first line <![CDATA[<div>]]></DIV>"},
             {"code": "<A>  <B> </A>   </B>"},
             {"code": "<DIV>  unmatched <  </DIV>"}],
    hidden=[{"code": "<DIV>>>  ![cdata[]] <![CDATA[<div>]>]]>]]>>]</DIV>"},
            {"code": "<DIV>  div tag is not closed  <DIV>"},
            {"code": "<DIV> closed tags with invalid tag name  <b>123</b> </DIV>"},
            {"code": "<A></A>"}, {"code": "<A>B</A>C"}, {"code": "abc"}],
    checks=[({"code": "<DIV>This is the first line <![CDATA[<div>]]></DIV>"}, True),
            ({"code": "<DIV>>>  ![cdata[]] <![CDATA[<div>]>]]>]]>>]</DIV>"}, True),
            ({"code": "<A>  <B> </A>   </B>"}, False),
            ({"code": "<DIV>  div tag is not closed  <DIV>"}, False),
            ({"code": "<DIV>  unmatched <  </DIV>"}, False),
            ({"code": "<A></A>"}, True)],
    source="new_p")


# ===========================================================================
# 11. Monotone Increasing Digits
# ===========================================================================
add("monotone-increasing-digits", "Monotone Increasing Digits", "medium",
    ["math", "greedy"], "monotoneIncreasingDigits", [("N", "int")], "int",
    """
An integer has *monotone increasing digits* if each digit is `<=` the digit to its
right. **Return the largest integer `<= N` with monotone increasing digits.**

**Examples**
```
N = 10    ->  9
N = 1234  ->  1234
N = 332   ->  299
```

**Constraints:** `0 <= N <= 10^9`.
""",
    """def monotoneIncreasingDigits(N):
    digits = list(str(N))
    n = len(digits)
    mark = n
    for i in range(n - 1, 0, -1):
        if digits[i - 1] > digits[i]:
            digits[i - 1] = str(int(digits[i - 1]) - 1)
            mark = i
    for i in range(mark, n):
        digits[i] = '9'
    return int("".join(digits))
""",
    visible=[{"N": 10}, {"N": 1234}, {"N": 332}],
    hidden=[{"N": 0}, {"N": 9}, {"N": 100}, {"N": 120}, {"N": 999}],
    gen=lambda r: [{"N": r.randint(0, 300)} for _ in range(8)],
    brute=_monodigit_brute,
    checks=[({"N": 10}, 9), ({"N": 1234}, 1234), ({"N": 332}, 299),
            ({"N": 0}, 0), ({"N": 1000000000}, 999999999)],
    source="new_p")


# ===========================================================================
# 12. Shortest Subarray With Sum at Least K
# ===========================================================================
add("shortest-subarray-with-sum-at-least-k", "Shortest Subarray With Sum at Least K",
    "hard", ["array", "binary-search", "queue", "sliding-window", "prefix-sum"],
    "shortestSubarray", [("A", "int[]"), ("K", "int")], "int",
    """
**Return the length of the shortest non-empty contiguous subarray of `A` with sum at
least `K`**, or `-1` if none exists. `A` may contain negative numbers.

**Examples**
```
A = [1], K = 1        ->  1
A = [1,2], K = 4      ->  -1
A = [2,-1,2], K = 3   ->  3
```

**Constraints:** `1 <= len(A) <= 5*10^4`, `-10^5 <= A[i] <= 10^5`, `1 <= K <= 10^9`.
""",
    """def shortestSubarray(A, K):
    from collections import deque
    n = len(A)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + A[i]
    dq = deque()
    res = n + 1
    for i in range(n + 1):
        while dq and pre[i] - pre[dq[0]] >= K:
            res = min(res, i - dq.popleft())
        while dq and pre[dq[-1]] >= pre[i]:
            dq.pop()
        dq.append(i)
    return res if res <= n else -1
""",
    visible=[{"A": [1], "K": 1}, {"A": [1, 2], "K": 4}, {"A": [2, -1, 2], "K": 3}],
    hidden=[{"A": [-1, -2], "K": 1}, {"A": [5], "K": 5}, {"A": [1, 1, 1, 1], "K": 3},
            {"A": [84, -37, 32, 40, 95], "K": 167}],
    gen=lambda r: [{"A": [r.randint(-5, 5) for _ in range(r.randint(1, 12))],
                    "K": r.randint(1, 15)} for _ in range(6)],
    brute=_shortsub_brute,
    checks=[({"A": [1], "K": 1}, 1), ({"A": [1, 2], "K": 4}, -1),
            ({"A": [2, -1, 2], "K": 3}, 3)],
    source="new_p")


# ===========================================================================
# 13. Minimum Number of Days to Make m Bouquets
# ===========================================================================
add("minimum-number-of-days-to-make-m-bouquets",
    "Minimum Number of Days to Make m Bouquets", "medium",
    ["array", "binary-search"], "minDays",
    [("bloomDay", "int[]"), ("m", "int"), ("k", "int")], "int",
    """
`bloomDay[i]` is the day flower `i` blooms. A bouquet needs `k` adjacent bloomed
flowers; you want `m` bouquets. **Return the minimum number of days to wait**, or
`-1` if it is impossible.

**Examples**
```
bloomDay = [1,10,3,10,2], m = 3, k = 1   ->  3
bloomDay = [1,10,3,10,2], m = 3, k = 2   ->  -1
bloomDay = [7,7,7,7,12,7,7], m = 2, k = 3 ->  12
```

**Constraints:** `1 <= len(bloomDay) <= 10^5`, `1 <= bloomDay[i] <= 10^9`,
`1 <= m <= 10^6`, `1 <= k <= len(bloomDay)`.
""",
    """def minDays(bloomDay, m, k):
    n = len(bloomDay)
    if m * k > n:
        return -1

    def can(day):
        bouquets = flowers = 0
        for b in bloomDay:
            if b <= day:
                flowers += 1
                if flowers == k:
                    bouquets += 1
                    flowers = 0
            else:
                flowers = 0
        return bouquets >= m

    lo, hi = min(bloomDay), max(bloomDay)
    while lo < hi:
        mid = (lo + hi) // 2
        if can(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
""",
    visible=[{"bloomDay": [1, 10, 3, 10, 2], "m": 3, "k": 1},
             {"bloomDay": [1, 10, 3, 10, 2], "m": 3, "k": 2},
             {"bloomDay": [7, 7, 7, 7, 12, 7, 7], "m": 2, "k": 3}],
    hidden=[{"bloomDay": [1000000000, 1000000000], "m": 1, "k": 1},
            {"bloomDay": [1, 10, 2, 9, 3, 8, 4, 7, 5, 6], "m": 4, "k": 2},
            {"bloomDay": [1], "m": 1, "k": 1}, {"bloomDay": [5, 5, 5], "m": 1, "k": 3}],
    gen=lambda r: [_bouquet_gen(r) for _ in range(6)],
    brute=_bouquet_brute,
    checks=[({"bloomDay": [1, 10, 3, 10, 2], "m": 3, "k": 1}, 3),
            ({"bloomDay": [1, 10, 3, 10, 2], "m": 3, "k": 2}, -1),
            ({"bloomDay": [7, 7, 7, 7, 12, 7, 7], "m": 2, "k": 3}, 12),
            ({"bloomDay": [1, 10, 2, 9, 3, 8, 4, 7, 5, 6], "m": 4, "k": 2}, 9)],
    source="new_p")


# ===========================================================================
# 14. Number of Substrings With Only 1s
# ===========================================================================
add("number-of-substrings-with-only-1s", "Number of Substrings With Only 1s", "medium",
    ["string", "math"], "numSub", [("s", "string")], "int",
    """
**Return the number of substrings of the binary string `s` that consist only of
`1`s**, modulo `10^9 + 7`.

**Examples**
```
s = "0110111"  ->  9
s = "101"      ->  2
s = "111111"   ->  21
```

**Constraints:** `1 <= len(s) <= 10^5`, `s[i]` in `{0, 1}`.
""",
    """def numSub(s):
    MOD = 10 ** 9 + 7
    res = 0
    run = 0
    for c in s:
        if c == '1':
            run += 1
            res = (res + run) % MOD
        else:
            run = 0
    return res % MOD
""",
    visible=[{"s": "0110111"}, {"s": "101"}, {"s": "111111"}],
    hidden=[{"s": "0"}, {"s": "1"}, {"s": "000"}, {"s": "1010101"}],
    gen=lambda r: [{"s": "".join(r.choice("01") for _ in range(r.randint(1, 15)))}
                   for _ in range(6)],
    brute=_numsub_brute,
    checks=[({"s": "0110111"}, 9), ({"s": "101"}, 2), ({"s": "111111"}, 21),
            ({"s": "000"}, 0)],
    source="new_p")


# ===========================================================================
# 15. Minimum Swaps to Make Strings Equal
# ===========================================================================
add("minimum-swaps-to-make-strings-equal", "Minimum Swaps to Make Strings Equal",
    "medium", ["string", "math", "greedy"], "minimumSwap",
    [("s1", "string"), ("s2", "string")], "int",
    """
`s1` and `s2` are equal-length strings of `'x'` and `'y'`. In one move you swap some
`s1[i]` with some `s2[j]`. **Return the minimum number of swaps to make `s1 == s2`,
or `-1` if impossible.**

**Examples**
```
s1 = "xx", s2 = "yy"   ->  1
s1 = "xy", s2 = "yx"   ->  2
s1 = "xx", s2 = "xy"   ->  -1
```

**Constraints:** `1 <= len(s1) == len(s2) <= 1000`, characters `'x'`/`'y'`.
""",
    """def minimumSwap(s1, s2):
    xy = yx = 0
    for a, b in zip(s1, s2):
        if a == 'x' and b == 'y':
            xy += 1
        elif a == 'y' and b == 'x':
            yx += 1
    if (xy + yx) % 2 == 1:
        return -1
    return xy // 2 + yx // 2 + (2 if xy % 2 == 1 else 0)
""",
    visible=[{"s1": "xx", "s2": "yy"}, {"s1": "xy", "s2": "yx"}, {"s1": "xx", "s2": "xy"}],
    hidden=[{"s1": "xxyyxyxyxx", "s2": "xyyxyxxxyx"}, {"s1": "x", "s2": "x"},
            {"s1": "xy", "s2": "xy"}, {"s1": "xyx", "s2": "yxy"}],
    gen=lambda r: [(lambda n: {"s1": "".join(r.choice("xy") for _ in range(n)),
                               "s2": "".join(r.choice("xy") for _ in range(n))})
                   (r.randint(1, 4)) for _ in range(8)],
    brute=_swap_brute,
    checks=[({"s1": "xx", "s2": "yy"}, 1), ({"s1": "xy", "s2": "yx"}, 2),
            ({"s1": "xx", "s2": "xy"}, -1),
            ({"s1": "xxyyxyxyxx", "s2": "xyyxyxxxyx"}, 4)],
    source="new_p")


# ===========================================================================
# 16. Longest Happy Prefix
# ===========================================================================
add("longest-happy-prefix", "Longest Happy Prefix", "hard",
    ["string", "rolling-hash", "string-matching"], "longestPrefix",
    [("s", "string")], "string",
    """
A *happy prefix* is a non-empty proper prefix of `s` that is also a suffix.
**Return the longest happy prefix of `s`**, or `""` if none exists.

**Examples**
```
s = "level"         ->  "l"
s = "ababab"        ->  "abab"
s = "leetcodeleet"  ->  "leet"
```

**Constraints:** `1 <= len(s) <= 10^5`, lowercase letters.
""",
    """def longestPrefix(s):
    n = len(s)
    lps = [0] * n
    k = 0
    for i in range(1, n):
        while k > 0 and s[i] != s[k]:
            k = lps[k - 1]
        if s[i] == s[k]:
            k += 1
        lps[i] = k
    return s[:lps[n - 1]]
""",
    visible=[{"s": "level"}, {"s": "ababab"}, {"s": "leetcodeleet"}],
    hidden=[{"s": "a"}, {"s": "aa"}, {"s": "abcabc"}, {"s": "aaaa"}],
    gen=lambda r: [{"s": sstr(r, 1, 12, "ab")} for _ in range(6)],
    brute=_prefix_brute,
    checks=[({"s": "level"}, "l"), ({"s": "ababab"}, "abab"),
            ({"s": "leetcodeleet"}, "leet"), ({"s": "a"}, "")],
    source="new_p")


# ===========================================================================
# 17. Valid Permutations for DI Sequence
# ===========================================================================
add("valid-permutations-for-di-sequence", "Valid Permutations for DI Sequence", "hard",
    ["dynamic-programming"], "numPermsDISequence", [("S", "string")], "int",
    """
`S` is a string of `'D'` (decrease) and `'I'` (increase) of length `n`. A valid
permutation `P` of `{0, 1, ..., n}` satisfies: `P[i] > P[i+1]` where `S[i] == 'D'`
and `P[i] < P[i+1]` where `S[i] == 'I'`. **Return the number of valid permutations,
modulo `10^9 + 7`.**

**Example**
```
S = "DID"  ->  5
```

**Constraints:** `1 <= len(S) <= 200`, characters `'D'`/`'I'`.
""",
    """def numPermsDISequence(S):
    MOD = 10 ** 9 + 7
    n = len(S)
    dp = [1]
    for i in range(n):
        c = S[i]
        L = i + 1
        pre = [0] * (L + 1)
        for j in range(L):
            pre[j + 1] = (pre[j] + dp[j]) % MOD
        ndp = [0] * (L + 1)
        for j in range(L + 1):
            if c == 'I':
                ndp[j] = pre[j]
            else:
                ndp[j] = (pre[L] - pre[j]) % MOD
        dp = ndp
    return sum(dp) % MOD
""",
    visible=[{"S": "DID"}],
    hidden=[{"S": "I"}, {"S": "D"}, {"S": "DD"}, {"S": "II"}, {"S": "IDID"}],
    gen=lambda r: [{"S": "".join(r.choice("DI") for _ in range(r.randint(1, 6)))}
                   for _ in range(8)],
    brute=_diperms_brute,
    checks=[({"S": "DID"}, 5), ({"S": "I"}, 1), ({"S": "D"}, 1), ({"S": "DD"}, 1)],
    source="new_p")


# ===========================================================================
# 18. Pizza With 3n Slices
# ===========================================================================
add("pizza-with-3n-slices", "Pizza With 3n Slices", "hard",
    ["array", "dynamic-programming", "greedy", "heap"], "maxSizeSlices",
    [("slices", "int[]")], "int",
    """
A circular pizza has `3n` slices with sizes `slices` (clockwise). You repeatedly take
a slice, then your friends take the slices immediately counter-clockwise and clockwise
of your pick. **Return the maximum total size of the slices you can take** (you take
exactly `n` slices, no two adjacent on the circle).

**Examples**
```
slices = [1,2,3,4,5,6]            ->  10
slices = [8,9,8,6,1,1]            ->  16
slices = [4,1,2,5,8,3,1,9,7]      ->  21
```

**Constraints:** `len(slices) % 3 == 0`, `1 <= len(slices) <= 500`,
`1 <= slices[i] <= 1000`.
""",
    """def maxSizeSlices(slices):
    n = len(slices)
    k = n // 3
    NEG = float('-inf')

    def solve(arr):
        m = len(arr)
        dp = [[NEG] * (k + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = 0
        for i in range(1, m + 1):
            for j in range(1, k + 1):
                take = arr[i - 1] + (dp[i - 2][j - 1] if i >= 2 else (0 if j == 1 else NEG))
                dp[i][j] = max(dp[i - 1][j], take)
        return dp[m][k]

    return max(solve(slices[1:]), solve(slices[:-1]))
""",
    visible=[{"slices": [1, 2, 3, 4, 5, 6]}, {"slices": [8, 9, 8, 6, 1, 1]}],
    hidden=[{"slices": [3, 1, 2]}, {"slices": [1, 1, 1]}, {"slices": [9, 9, 1, 1, 1, 9]},
            {"slices": [5, 4, 3, 2, 1, 6]}],
    gen=lambda r: [_pizza_gen(r) for _ in range(6)],
    brute=_pizza_brute,
    checks=[({"slices": [1, 2, 3, 4, 5, 6]}, 10), ({"slices": [8, 9, 8, 6, 1, 1]}, 16),
            ({"slices": [4, 1, 2, 5, 8, 3, 1, 9, 7]}, 21), ({"slices": [3, 1, 2]}, 3)],
    source="new_p")
