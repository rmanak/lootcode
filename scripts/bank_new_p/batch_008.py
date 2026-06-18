"""Batch 008 of the new_p.txt import (19 problems).

One entry from this slice was dropped as a duplicate under a different slug (see
`_skips.py`): `task-scheduler` (== existing `task-scheduler-cooldown`).
"""
from scripts.build_bank import add, ilist, sstr  # noqa: F401


# --------------------------- brute / reference helpers ---------------------
def _lmt_brute(digits):
    from itertools import combinations
    n = len(digits)
    best = None
    for size in range(n, 0, -1):
        cand = []
        for combo in combinations(range(n), size):
            ds = sorted((digits[i] for i in combo), reverse=True)
            val = int("".join(map(str, ds)))
            if val % 3 == 0:
                cand.append((val, ds))
        if cand:
            best = max(cand)[1]
            break
    if best is None:
        return ""
    if best[0] == 0:
        return "0"
    return "".join(map(str, best))


def _perm_brute(n, k):
    from itertools import permutations
    p = list(permutations(range(1, n + 1)))
    return "".join(map(str, p[k - 1]))


def _palpart_brute(s, k):
    n = len(s)

    def changes(sub):
        return sum(1 for a in range(len(sub) // 2) if sub[a] != sub[-1 - a])

    best = [float('inf')]

    def rec(start, parts, acc):
        if parts == k:
            if start == n:
                best[0] = min(best[0], acc)
            return
        for end in range(start + 1, n - (k - parts - 1) + 1):
            rec(end, parts + 1, acc + changes(s[start:end]))
    rec(0, 0, 0)
    return best[0]


def _convert_brute(s, t, k):
    if len(s) != len(t):
        return False
    reqs = []
    for a, b in zip(s, t):
        d = (ord(b) - ord(a)) % 26
        if d != 0:
            reqs.append(d)
    used = set()
    for d in sorted(reqs):
        m = d
        while m <= k and m in used:
            m += 26
        if m > k:
            return False
        used.add(m)
    return True


def _maxside_brute(mat, threshold):
    m = len(mat)
    n = len(mat[0])
    best = 0
    for k in range(1, min(m, n) + 1):
        for i in range(m - k + 1):
            for j in range(n - k + 1):
                s = sum(mat[i + a][j + b] for a in range(k) for b in range(k))
                if s <= threshold:
                    best = max(best, k)
    return best


def _pairdist_brute(nums, k):
    ds = sorted(abs(nums[i] - nums[j])
                for i in range(len(nums)) for j in range(i + 1, len(nums)))
    return ds[k - 1]


def _bag_brute(tokens, P):
    n = len(tokens)
    best = [0]

    def dfs(used, score, power):
        best[0] = max(best[0], score)
        for i in range(n):
            if not (used >> i) & 1:
                if power >= tokens[i]:
                    dfs(used | (1 << i), score + 1, power - tokens[i])
                if score > 0:
                    dfs(used | (1 << i), score - 1, power + tokens[i])
    dfs(0, 0, P)
    return best[0]


def _srii_brute(A, K):
    n = len(A)
    best = float('inf')
    for mask in range(1 << n):
        B = [A[i] + (K if (mask >> i) & 1 else -K) for i in range(n)]
        best = min(best, max(B) - min(B))
    return best


def _prob_brute(balls):
    from itertools import combinations
    labels = []
    for color, c in enumerate(balls):
        labels += [color] * c
    N = len(labels)
    n = N // 2
    total = 0
    fav = 0
    for combo in combinations(range(N), n):
        chosen = set(combo)
        b1 = set(labels[i] for i in combo)
        b2 = set(labels[i] for i in range(N) if i not in chosen)
        total += 1
        if len(b1) == len(b2):
            fav += 1
    return round(fav / total, 5)


def _beauty_brute(N):
    from itertools import permutations
    c = 0
    for p in permutations(range(1, N + 1)):
        if all((p[i] % (i + 1) == 0 or (i + 1) % p[i] == 0) for i in range(N)):
            c += 1
    return c


def _flip_brute(n, m):
    def affects(b, i):
        if b == 0:
            return True
        if b == 1:
            return i % 2 == 0
        if b == 2:
            return i % 2 == 1
        return i % 3 == 1

    states = set()
    for S in range(16):
        cnt = bin(S).count("1")
        if cnt <= m and (m - cnt) % 2 == 0:
            pat = []
            for i in range(1, n + 1):
                on = True
                for b in range(4):
                    if (S >> b) & 1 and affects(b, i):
                        on = not on
                pat.append(on)
            states.add(tuple(pat))
    return len(states)


def _twosum_brute(A, L, M):
    n = len(A)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + A[i]
    best = 0
    for i in range(n - L + 1):
        for j in range(n - M + 1):
            if i + L <= j or j + M <= i:
                best = max(best, pre[i + L] - pre[i] + pre[j + M] - pre[j])
    return best


def _mincut_brute(n, cuts):
    from itertools import permutations
    import bisect
    best = float('inf')
    for order in permutations(cuts):
        segs = [0, n]
        cost = 0
        for c in order:
            idx = bisect.bisect_left(segs, c)
            cost += segs[idx] - segs[idx - 1]
            segs.insert(idx, c)
        best = min(best, cost)
    return best


def _oddsum_brute(arr):
    n = len(arr)
    c = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += arr[j]
            if s % 2 == 1:
                c += 1
    return c % (10 ** 9 + 7)


def _maxabs_brute(arr1, arr2):
    n = len(arr1)
    best = 0
    for i in range(n):
        for j in range(n):
            best = max(best, abs(arr1[i] - arr1[j]) + abs(arr2[i] - arr2[j]) + abs(i - j))
    return best


def _nqueens_brute(n):
    from itertools import permutations
    if n == 0:
        return 1
    c = 0
    for perm in permutations(range(n)):
        if (len(set(perm[i] - i for i in range(n))) == n and
                len(set(perm[i] + i for i in range(n))) == n):
            c += 1
    return c


def _selfcross_brute(x):
    dirs = [(0, 1), (-1, 0), (0, -1), (1, 0)]
    cx, cy = 0, 0
    pts = [(0, 0)]
    for i, d in enumerate(x):
        dx, dy = dirs[i % 4]
        cx += dx * d
        cy += dy * d
        pts.append((cx, cy))
    segs = [(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]

    def inter(s1, s2):
        (ax, ay), (bx, by) = s1
        (cx2, cy2), (dx2, dy2) = s2
        return (min(ax, bx) <= max(cx2, dx2) and min(cx2, dx2) <= max(ax, bx) and
                min(ay, by) <= max(cy2, dy2) and min(cy2, dy2) <= max(ay, by))

    for i in range(len(segs)):
        for j in range(i + 2, len(segs)):
            if inter(segs[i], segs[j]):
                return True
    return False


def _tile_brute(tiles):
    from itertools import permutations
    seqs = set()
    for length in range(1, len(tiles) + 1):
        for p in permutations(tiles, length):
            seqs.add(p)
    return len(seqs)


# gen helpers ---------------------------------------------------------------
def _maxside_gen(r):
    rows, cols = r.randint(1, 5), r.randint(1, 5)
    return {"mat": [[r.randint(0, 5) for _ in range(cols)] for _ in range(rows)],
            "threshold": r.randint(0, 30)}


def _balls_gen(r):
    while True:
        b = [r.randint(1, 3) for _ in range(r.randint(1, 3))]
        if sum(b) % 2 == 0 and sum(b) <= 8:
            return {"balls": b}


def _twosum_gen(r):
    n = r.randint(2, 10)
    L = r.randint(1, n - 1)
    M = r.randint(1, n - L)
    return {"A": [r.randint(0, 10) for _ in range(n)], "L": L, "M": M}


def _mincut_gen(r):
    n = r.randint(3, 15)
    m = r.randint(1, min(6, n - 1))
    return {"n": n, "cuts": r.sample(range(1, n), m)}


def _rot_gen(r):
    base = sorted(r.randint(0, 5) for _ in range(r.randint(1, 8)))
    k = r.randint(0, len(base) - 1)
    return {"nums": base[k:] + base[:k]}


def _convert_gen(r):
    n = r.randint(1, 6)
    return {"s": "".join(r.choice("abc") for _ in range(n)),
            "t": "".join(r.choice("abc") for _ in range(n)),
            "k": r.randint(0, 30)}


# ===========================================================================
# 1. Largest Multiple of Three
# ===========================================================================
add("largest-multiple-of-three", "Largest Multiple of Three", "hard",
    ["array", "dynamic-programming", "greedy", "math"], "largestMultipleOfThree",
    [("digits", "int[]")], "string",
    """
Choose some of the `digits` and concatenate them (arranged to make the value as
large as possible) to form the **largest multiple of `3`**. Return it as a string
with no unnecessary leading zeros, or `""` if no multiple of `3` can be formed.

**Examples**
```
digits = [8,1,9]          ->  "981"
digits = [8,6,7,1,0]      ->  "8760"
digits = [1]              ->  ""
digits = [0,0,0,0,0,0]    ->  "0"
```

**Constraints:** `1 <= len(digits) <= 10^4`, `0 <= digits[i] <= 9`.
""",
    """def largestMultipleOfThree(digits):
    from collections import Counter
    total = sum(digits)
    r = total % 3
    m1 = sorted(d for d in digits if d % 3 == 1)
    m2 = sorted(d for d in digits if d % 3 == 2)
    remove = []
    if r == 1:
        if m1:
            remove = [m1[0]]
        elif len(m2) >= 2:
            remove = m2[:2]
        else:
            return ""
    elif r == 2:
        if m2:
            remove = [m2[0]]
        elif len(m1) >= 2:
            remove = m1[:2]
        else:
            return ""
    rc = Counter(remove)
    res = []
    for d in sorted(digits, reverse=True):
        if rc[d] > 0:
            rc[d] -= 1
        else:
            res.append(d)
    if not res:
        return ""
    if res[0] == 0:
        return "0"
    return "".join(map(str, res))
""",
    visible=[{"digits": [8, 1, 9]}, {"digits": [8, 6, 7, 1, 0]}, {"digits": [1]},
             {"digits": [0, 0, 0, 0, 0, 0]}],
    hidden=[{"digits": [3, 6, 9]}, {"digits": [5, 8]}, {"digits": [9]},
            {"digits": [0]}, {"digits": [2, 2, 2]}],
    gen=lambda r: [{"digits": [r.randint(0, 9) for _ in range(r.randint(1, 7))]}
                   for _ in range(6)],
    brute=_lmt_brute,
    checks=[({"digits": [8, 1, 9]}, "981"), ({"digits": [8, 6, 7, 1, 0]}, "8760"),
            ({"digits": [1]}, ""), ({"digits": [0, 0, 0, 0, 0, 0]}, "0")],
    source="new_p")


# ===========================================================================
# 2. Permutation Sequence
# ===========================================================================
add("permutation-sequence", "Permutation Sequence", "hard",
    ["math", "recursion"], "getPermutation", [("n", "int"), ("k", "int")], "string",
    """
The numbers `1..n` have `n!` permutations. Listing them in ascending (lexicographic)
order, **return the `k`-th permutation** (1-indexed) as a string.

**Examples**
```
n = 3, k = 3  ->  "213"
n = 4, k = 9  ->  "2314"
```

**Constraints:** `1 <= n <= 9`, `1 <= k <= n!`.
""",
    """def getPermutation(n, k):
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
""",
    visible=[{"n": 3, "k": 3}, {"n": 4, "k": 9}],
    hidden=[{"n": 1, "k": 1}, {"n": 3, "k": 1}, {"n": 3, "k": 6}, {"n": 4, "k": 24}],
    gen=lambda r: [(lambda n: {"n": n, "k": r.randint(1, __import__("math").factorial(n))})
                   (r.randint(1, 6)) for _ in range(6)],
    brute=_perm_brute,
    checks=[({"n": 3, "k": 3}, "213"), ({"n": 4, "k": 9}, "2314"),
            ({"n": 1, "k": 1}, "1"), ({"n": 3, "k": 6}, "321")],
    source="new_p")


# ===========================================================================
# 3. Palindrome Partitioning III
# ===========================================================================
add("palindrome-partitioning-iii", "Palindrome Partitioning III", "hard",
    ["string", "dynamic-programming"], "palindromePartition",
    [("s", "string"), ("k", "int")], "int",
    """
You may change some characters of `s` to other lowercase letters, then split `s`
into `k` non-empty contiguous substrings that are each palindromes. **Return the
minimum number of character changes needed.**

**Examples**
```
s = "abc", k = 2     ->  1
s = "aabbc", k = 3   ->  0
s = "leetcode", k = 8 ->  0
```

**Constraints:** `1 <= k <= len(s) <= 100`, lowercase letters.
""",
    """def palindromePartition(s, k):
    n = len(s)
    cost = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            cost[i][j] = cost[i + 1][j - 1] + (1 if s[i] != s[j] else 0)
    INF = float('inf')
    dp = [[INF] * (k + 1) for _ in range(n + 1)]
    dp[0][0] = 0
    for i in range(1, n + 1):
        for p in range(1, min(i, k) + 1):
            for j in range(p - 1, i):
                if dp[j][p - 1] < INF:
                    dp[i][p] = min(dp[i][p], dp[j][p - 1] + cost[j][i - 1])
    return dp[n][k]
""",
    visible=[{"s": "abc", "k": 2}, {"s": "aabbc", "k": 3}, {"s": "leetcode", "k": 8}],
    hidden=[{"s": "a", "k": 1}, {"s": "ab", "k": 1}, {"s": "abcde", "k": 1},
            {"s": "abcde", "k": 5}, {"s": "aaa", "k": 1}],
    gen=lambda r: [(lambda s: {"s": s, "k": r.randint(1, len(s))})
                   (sstr(r, 2, 8, "abc")) for _ in range(6)],
    brute=_palpart_brute,
    checks=[({"s": "abc", "k": 2}, 1), ({"s": "aabbc", "k": 3}, 0),
            ({"s": "leetcode", "k": 8}, 0), ({"s": "abcde", "k": 1}, 2)],
    source="new_p")


# ===========================================================================
# 4. Can Convert String in K Moves
# ===========================================================================
add("can-convert-string-in-k-moves", "Can Convert String in K Moves", "medium",
    ["string", "hash-table"], "canConvertString",
    [("s", "string"), ("t", "string"), ("k", "int")], "bool",
    """
On move `i` (for `i = 1..k`) you may pick a not-yet-picked index of `s` and shift its
character forward `i` times in the alphabet (wrapping `z -> a`), or do nothing. Each
index can be picked at most once. **Return `true` if `s` can be turned into `t` in at
most `k` moves.**

**Examples**
```
s = "input", t = "ouput", k = 9   ->  true
s = "abc", t = "bcd", k = 10       ->  false
s = "aab", t = "bbb", k = 27       ->  true
```

**Constraints:** `1 <= len(s), len(t) <= 10^5`, `0 <= k <= 10^9`, lowercase letters.
""",
    """def canConvertString(s, t, k):
    if len(s) != len(t):
        return False
    from collections import defaultdict
    cnt = defaultdict(int)
    for a, b in zip(s, t):
        d = (ord(b) - ord(a)) % 26
        if d == 0:
            continue
        need = d + 26 * cnt[d]
        if need > k:
            return False
        cnt[d] += 1
    return True
""",
    visible=[{"s": "input", "t": "ouput", "k": 9}, {"s": "abc", "t": "bcd", "k": 10},
             {"s": "aab", "t": "bbb", "k": 27}],
    hidden=[{"s": "a", "t": "a", "k": 0}, {"s": "ab", "t": "abc", "k": 100},
            {"s": "az", "t": "ba", "k": 2}, {"s": "aaa", "t": "bbb", "k": 1}],
    gen=lambda r: [_convert_gen(r) for _ in range(8)],
    brute=_convert_brute,
    checks=[({"s": "input", "t": "ouput", "k": 9}, True),
            ({"s": "abc", "t": "bcd", "k": 10}, False),
            ({"s": "aab", "t": "bbb", "k": 27}, True)],
    source="new_p")


# ===========================================================================
# 5. Maximum Side Length of a Square With Sum <= Threshold
# ===========================================================================
add("maximum-side-length-of-a-square-with-sum-less-than-or-equal-to-threshold",
    "Maximum Side Length of a Square With Sum Less Than or Equal to Threshold",
    "medium", ["array", "binary-search", "matrix", "prefix-sum"], "maxSideLength",
    [("mat", "int[][]"), ("threshold", "int")], "int",
    """
Given an `m x n` matrix `mat` and an integer `threshold`, **return the maximum
side-length of a square sub-matrix whose sum is `<= threshold`** (or `0` if no such
square exists).

**Examples**
```
mat = [[1,1,3,2,4,3,2],[1,1,3,2,4,3,2],[1,1,3,2,4,3,2]], threshold = 4  ->  2
mat = [[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2]], threshold = 1  ->  0
mat = [[1,1,1,1],[1,0,0,0],[1,0,0,0],[1,0,0,0]], threshold = 6        ->  3
```

**Constraints:** `1 <= m, n <= 300`, `0 <= mat[i][j] <= 10^4`,
`0 <= threshold <= 10^5`.
""",
    """def maxSideLength(mat, threshold):
    m = len(mat)
    n = len(mat[0])
    pre = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            pre[i + 1][j + 1] = mat[i][j] + pre[i][j + 1] + pre[i + 1][j] - pre[i][j]

    def square_sum(r, c, k):
        return pre[r + k][c + k] - pre[r][c + k] - pre[r + k][c] + pre[r][c]

    best = 0
    k = 1
    while k <= min(m, n):
        found = False
        for i in range(m - k + 1):
            for j in range(n - k + 1):
                if square_sum(i, j, k) <= threshold:
                    found = True
                    break
            if found:
                break
        if found:
            best = k
            k += 1
        else:
            break
    return best
""",
    visible=[{"mat": [[1, 1, 3, 2, 4, 3, 2], [1, 1, 3, 2, 4, 3, 2], [1, 1, 3, 2, 4, 3, 2]],
              "threshold": 4},
             {"mat": [[2, 2, 2, 2, 2], [2, 2, 2, 2, 2], [2, 2, 2, 2, 2],
                      [2, 2, 2, 2, 2], [2, 2, 2, 2, 2]], "threshold": 1},
             {"mat": [[1, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]],
              "threshold": 6}],
    hidden=[{"mat": [[18, 70], [61, 1], [25, 85], [14, 40], [11, 96], [97, 96], [63, 45]],
             "threshold": 40184},
            {"mat": [[1]], "threshold": 0}, {"mat": [[1]], "threshold": 5},
            {"mat": [[0, 0], [0, 0]], "threshold": 0}],
    gen=lambda r: [_maxside_gen(r) for _ in range(6)],
    brute=_maxside_brute,
    checks=[({"mat": [[1, 1, 3, 2, 4, 3, 2], [1, 1, 3, 2, 4, 3, 2], [1, 1, 3, 2, 4, 3, 2]],
              "threshold": 4}, 2),
            ({"mat": [[1, 1, 1, 1], [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0]],
              "threshold": 6}, 3),
            ({"mat": [[18, 70], [61, 1], [25, 85], [14, 40], [11, 96], [97, 96], [63, 45]],
              "threshold": 40184}, 2)],
    source="new_p")


# ===========================================================================
# 6. Find K-th Smallest Pair Distance
# ===========================================================================
add("find-k-th-smallest-pair-distance", "Find K-th Smallest Pair Distance", "hard",
    ["array", "binary-search", "sorting"], "smallestDistancePair",
    [("nums", "int[]"), ("k", "int")], "int",
    """
The distance of a pair `(a, b)` is `|a - b|`. Over all pairs of elements of `nums`,
**return the `k`-th smallest distance** (1-indexed).

**Examples**
```
nums = [1,3,1], k = 1   ->  0
nums = [1,1,1], k = 2   ->  0
nums = [1,6,1], k = 3   ->  5
```

**Constraints:** `2 <= len(nums) <= 10^4`, `0 <= nums[i] <= 10^6`,
`1 <= k <= len(nums)*(len(nums)-1)/2`.
""",
    """def smallestDistancePair(nums, k):
    nums = sorted(nums)
    n = len(nums)

    def count(d):
        cnt = 0
        j = 0
        for i in range(n):
            while nums[i] - nums[j] > d:
                j += 1
            cnt += i - j
        return cnt

    lo, hi = 0, nums[-1] - nums[0]
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
""",
    visible=[{"nums": [1, 3, 1], "k": 1}, {"nums": [1, 1, 1], "k": 2},
             {"nums": [1, 6, 1], "k": 3}],
    hidden=[{"nums": [1, 2], "k": 1}, {"nums": [9, 0, 5, 2], "k": 6},
            {"nums": [38, 33, 57, 65, 13], "k": 6}, {"nums": [0, 0], "k": 1}],
    gen=lambda r: [(lambda nums: {"nums": nums, "k": r.randint(1, len(nums) * (len(nums) - 1) // 2)})
                   ([r.randint(0, 15) for _ in range(r.randint(2, 8))]) for _ in range(6)],
    brute=_pairdist_brute,
    checks=[({"nums": [1, 3, 1], "k": 1}, 0), ({"nums": [1, 1, 1], "k": 2}, 0),
            ({"nums": [1, 6, 1], "k": 3}, 5)],
    source="new_p")


# ===========================================================================
# 7. Bag of Tokens
# ===========================================================================
add("bag-of-tokens", "Bag of Tokens", "medium",
    ["array", "greedy", "sorting", "two-pointers"], "bagOfTokensScore",
    [("tokens", "int[]"), ("P", "int")], "int",
    """
You start with power `P` and score `0`. Each token (used at most once) may be played
**face up** (need at least `tokens[i]` power; lose `tokens[i]` power, gain `1` point)
or **face down** (need at least `1` point; gain `tokens[i]` power, lose `1` point).
**Return the largest score reachable.**

**Examples**
```
tokens = [100], P = 50              ->  0
tokens = [100,200], P = 150         ->  1
tokens = [100,200,300,400], P = 200 ->  2
```

**Constraints:** `0 <= len(tokens) <= 1000`, `0 <= tokens[i] < 10^4`,
`0 <= P < 10^4`.
""",
    """def bagOfTokensScore(tokens, P):
    tokens = sorted(tokens)
    lo, hi = 0, len(tokens) - 1
    score = best = 0
    while lo <= hi:
        if P >= tokens[lo]:
            P -= tokens[lo]
            lo += 1
            score += 1
            best = max(best, score)
        elif score > 0:
            P += tokens[hi]
            hi -= 1
            score -= 1
        else:
            break
    return best
""",
    visible=[{"tokens": [100], "P": 50}, {"tokens": [100, 200], "P": 150},
             {"tokens": [100, 200, 300, 400], "P": 200}],
    hidden=[{"tokens": [], "P": 100}, {"tokens": [26], "P": 51},
            {"tokens": [71, 55, 82], "P": 54}, {"tokens": [1, 2, 3, 4, 5], "P": 3}],
    gen=lambda r: [{"tokens": [r.randint(0, 20) for _ in range(r.randint(0, 5))],
                    "P": r.randint(0, 30)} for _ in range(6)],
    brute=_bag_brute,
    checks=[({"tokens": [100], "P": 50}, 0), ({"tokens": [100, 200], "P": 150}, 1),
            ({"tokens": [100, 200, 300, 400], "P": 200}, 2)],
    source="new_p")


# ===========================================================================
# 8. Smallest Range II
# ===========================================================================
add("smallest-range-ii", "Smallest Range II", "medium",
    ["array", "math", "greedy", "sorting"], "smallestRangeII",
    [("A", "int[]"), ("K", "int")], "int",
    """
To every element of `A` you must add either `+K` or `-K` (exactly once each),
producing an array `B`. **Return the smallest possible value of
`max(B) - min(B)`.**

**Examples**
```
A = [1], K = 0       ->  0
A = [0,10], K = 2    ->  6
A = [1,3,6], K = 3   ->  3
```

**Constraints:** `1 <= len(A) <= 10^4`, `0 <= A[i] <= 10^4`, `0 <= K <= 10^4`.
""",
    """def smallestRangeII(A, K):
    A = sorted(A)
    n = len(A)
    res = A[-1] - A[0]
    for i in range(n - 1):
        hi = max(A[-1] - K, A[i] + K)
        lo = min(A[0] + K, A[i + 1] - K)
        res = min(res, hi - lo)
    return res
""",
    visible=[{"A": [1], "K": 0}, {"A": [0, 10], "K": 2}, {"A": [1, 3, 6], "K": 3}],
    hidden=[{"A": [7], "K": 5}, {"A": [3, 1, 10], "K": 4}, {"A": [0, 0, 0], "K": 1},
            {"A": [2, 7, 2], "K": 1}],
    gen=lambda r: [{"A": [r.randint(0, 15) for _ in range(r.randint(1, 8))],
                    "K": r.randint(0, 8)} for _ in range(6)],
    brute=_srii_brute,
    checks=[({"A": [1], "K": 0}, 0), ({"A": [0, 10], "K": 2}, 6),
            ({"A": [1, 3, 6], "K": 3}, 3)],
    source="new_p")


# ===========================================================================
# 9. Probability of Two Boxes Having the Same Number of Distinct Balls
# ===========================================================================
add("probability-of-a-two-boxes-having-the-same-number-of-distinct-balls",
    "Probability of Two Boxes Having the Same Number of Distinct Balls", "hard",
    ["math", "backtracking", "combinatorics", "probability"], "getProbability",
    [("balls", "int[]")], "float",
    """
There are `2n` distinguishable balls in `k` colors; `balls[i]` of them are color `i`
(`sum(balls)` is even). After a uniformly random shuffle, the first `n` balls go to
box 1 and the rest to box 2. **Return the probability that the two boxes contain the
same number of distinct colors** (answers within `1e-5` are accepted; this judge
expects the value rounded to 5 decimals).

**Examples**
```
balls = [1,1]          ->  1.00000
balls = [2,1,1]        ->  0.66667
balls = [1,2,1,2]      ->  0.60000
balls = [3,2,1]        ->  0.30000
balls = [6,6,6,6,6,6]  ->  0.90327
```

**Constraints:** `1 <= len(balls) <= 8`, `1 <= balls[i] <= 6`, `sum(balls)` even.
""",
    """def getProbability(balls):
    from math import comb
    k = len(balls)
    n = sum(balls) // 2
    fav = [0]
    den = [0]

    def rec(i, left, d1, d2, ways):
        if i == k:
            if left == 0:
                den[0] += ways
                if d1 == d2:
                    fav[0] += ways
            return
        for a in range(0, balls[i] + 1):
            if a > left:
                break
            rec(i + 1, left - a, d1 + (1 if a > 0 else 0),
                d2 + (1 if balls[i] - a > 0 else 0), ways * comb(balls[i], a))

    rec(0, n, 0, 0, 1)
    return round(fav[0] / den[0], 5)
""",
    visible=[{"balls": [1, 1]}, {"balls": [2, 1, 1]}, {"balls": [1, 2, 1, 2]}],
    hidden=[{"balls": [3, 2, 1]}, {"balls": [2, 2]}, {"balls": [1, 1, 1, 1]},
            {"balls": [4, 4]}],
    gen=lambda r: [_balls_gen(r) for _ in range(5)],
    brute=_prob_brute,
    checks=[({"balls": [1, 1]}, 1.0), ({"balls": [2, 1, 1]}, 0.66667),
            ({"balls": [1, 2, 1, 2]}, 0.6), ({"balls": [3, 2, 1]}, 0.3),
            ({"balls": [6, 6, 6, 6, 6, 6]}, 0.90327)],
    source="new_p")


# ===========================================================================
# 10. Beautiful Arrangement
# ===========================================================================
add("beautiful-arrangement", "Beautiful Arrangement", "medium",
    ["dynamic-programming", "backtracking", "bit-manipulation"], "countArrangement",
    [("N", "int")], "int",
    """
A *beautiful arrangement* is a permutation `p` of `1..N` such that for every position
`i` (1-indexed) either `p[i]` is divisible by `i` or `i` is divisible by `p[i]`.
**Return how many beautiful arrangements exist.**

**Examples**
```
N = 1  ->  1
N = 2  ->  2
N = 3  ->  3
```

**Constraints:** `1 <= N <= 15`.
""",
    """def countArrangement(N):
    count = [0]
    used = [False] * (N + 1)

    def dfs(pos):
        if pos > N:
            count[0] += 1
            return
        for num in range(1, N + 1):
            if not used[num] and (num % pos == 0 or pos % num == 0):
                used[num] = True
                dfs(pos + 1)
                used[num] = False

    dfs(1)
    return count[0]
""",
    visible=[{"N": 1}, {"N": 2}, {"N": 3}],
    hidden=[{"N": 4}, {"N": 5}, {"N": 6}, {"N": 7}],
    gen=lambda r: [{"N": r.randint(1, 7)} for _ in range(6)],
    brute=_beauty_brute,
    checks=[({"N": 1}, 1), ({"N": 2}, 2), ({"N": 3}, 3), ({"N": 4}, 8)],
    source="new_p")


# ===========================================================================
# 11. Bulb Switcher II
# ===========================================================================
add("bulb-switcher-ii", "Bulb Switcher II", "hard",
    ["math", "bit-manipulation"], "flipLights", [("n", "int"), ("m", "int")], "int",
    """
A row of `n` lights all start on. Four buttons each toggle a fixed set of lights:
(1) all lights, (2) even-numbered lights, (3) odd-numbered lights, (4) lights at
positions `3k + 1` (`1, 4, 7, ...`). After pressing buttons exactly `m` times in
total, **return how many distinct on/off light configurations are reachable.**

**Examples**
```
n = 1, m = 1  ->  2
n = 2, m = 1  ->  3
n = 3, m = 1  ->  4
```

**Constraints:** `0 <= n, m <= 1000`.
""",
    """def flipLights(n, m):
    if n == 0 or m == 0:
        return 1
    if n == 1:
        return 2
    if n == 2:
        return 3 if m == 1 else 4
    if m == 1:
        return 4
    if m == 2:
        return 7
    return 8
""",
    visible=[{"n": 1, "m": 1}, {"n": 2, "m": 1}, {"n": 3, "m": 1}],
    hidden=[{"n": 0, "m": 5}, {"n": 4, "m": 0}, {"n": 2, "m": 2}, {"n": 3, "m": 3},
            {"n": 5, "m": 2}, {"n": 4, "m": 4}],
    gen=lambda r: [{"n": r.randint(0, 6), "m": r.randint(0, 6)} for _ in range(8)],
    brute=_flip_brute,
    checks=[({"n": 1, "m": 1}, 2), ({"n": 2, "m": 1}, 3), ({"n": 3, "m": 1}, 4)],
    source="new_p")


# ===========================================================================
# 12. Maximum Sum of Two Non-Overlapping Subarrays
# ===========================================================================
add("maximum-sum-of-two-non-overlapping-subarrays",
    "Maximum Sum of Two Non-Overlapping Subarrays", "medium",
    ["array", "dynamic-programming", "sliding-window", "prefix-sum"], "maxSumTwoNoOverlap",
    [("A", "int[]"), ("L", "int"), ("M", "int")], "int",
    """
Given non-negative `A`, pick two **non-overlapping** contiguous subarrays of lengths
`L` and `M` (in either relative order) to **maximize their combined sum.** Return
that maximum.

**Examples**
```
A = [0,6,5,2,2,5,1,9,4], L = 1, M = 2     ->  20
A = [3,8,1,3,2,1,8,9,0], L = 3, M = 2     ->  29
A = [2,1,5,6,0,9,5,0,3,8], L = 4, M = 3   ->  31
```

**Constraints:** `1 <= L, M`, `L + M <= len(A) <= 1000`, `0 <= A[i] <= 1000`.
""",
    """def maxSumTwoNoOverlap(A, L, M):
    n = len(A)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + A[i]

    def helper(Lx, Mx):
        res = 0
        max_l = 0
        for j in range(Lx + Mx, n + 1):
            max_l = max(max_l, pre[j - Mx] - pre[j - Mx - Lx])
            res = max(res, max_l + pre[j] - pre[j - Mx])
        return res

    return max(helper(L, M), helper(M, L))
""",
    visible=[{"A": [0, 6, 5, 2, 2, 5, 1, 9, 4], "L": 1, "M": 2},
             {"A": [3, 8, 1, 3, 2, 1, 8, 9, 0], "L": 3, "M": 2},
             {"A": [2, 1, 5, 6, 0, 9, 5, 0, 3, 8], "L": 4, "M": 3}],
    hidden=[{"A": [1, 1], "L": 1, "M": 1}, {"A": [0, 0, 0], "L": 1, "M": 2},
            {"A": [5, 4, 3, 2, 1], "L": 2, "M": 2}, {"A": [1, 2, 3, 4, 5], "L": 1, "M": 4}],
    gen=lambda r: [_twosum_gen(r) for _ in range(6)],
    brute=_twosum_brute,
    checks=[({"A": [0, 6, 5, 2, 2, 5, 1, 9, 4], "L": 1, "M": 2}, 20),
            ({"A": [3, 8, 1, 3, 2, 1, 8, 9, 0], "L": 3, "M": 2}, 29),
            ({"A": [2, 1, 5, 6, 0, 9, 5, 0, 3, 8], "L": 4, "M": 3}, 31)],
    source="new_p")


# ===========================================================================
# 13. Minimum Cost to Cut a Stick
# ===========================================================================
add("minimum-cost-to-cut-a-stick", "Minimum Cost to Cut a Stick", "hard",
    ["array", "dynamic-programming"], "minCost", [("n", "int"), ("cuts", "int[]")], "int",
    """
A stick spans `[0, n]`. You must cut it at each position in `cuts` (in an order you
choose). Each cut costs the current length of the piece being cut, and splits it in
two. **Return the minimum total cost.**

**Examples**
```
n = 7, cuts = [1,3,4,5]    ->  16
n = 9, cuts = [5,6,1,4,2]  ->  22
```

**Constraints:** `2 <= n <= 10^6`, `1 <= len(cuts) <= min(n-1, 100)`,
`1 <= cuts[i] <= n-1`, all distinct.
""",
    """def minCost(n, cuts):
    from functools import lru_cache
    pts = sorted(set(cuts) | {0, n})
    m = len(pts)

    @lru_cache(None)
    def solve(i, j):
        if j - i <= 1:
            return 0
        return min(solve(i, t) + solve(t, j) + pts[j] - pts[i]
                   for t in range(i + 1, j))

    return solve(0, m - 1)
""",
    visible=[{"n": 7, "cuts": [1, 3, 4, 5]}, {"n": 9, "cuts": [5, 6, 1, 4, 2]}],
    hidden=[{"n": 5, "cuts": [2]}, {"n": 10, "cuts": [3, 7]}, {"n": 4, "cuts": [1, 2, 3]},
            {"n": 6, "cuts": [1, 5]}],
    gen=lambda r: [_mincut_gen(r) for _ in range(6)],
    brute=_mincut_brute,
    checks=[({"n": 7, "cuts": [1, 3, 4, 5]}, 16), ({"n": 9, "cuts": [5, 6, 1, 4, 2]}, 22),
            ({"n": 5, "cuts": [2]}, 5)],
    source="new_p")


# ===========================================================================
# 14. Number of Sub-arrays With Odd Sum
# ===========================================================================
add("number-of-sub-arrays-with-odd-sum", "Number of Sub-arrays With Odd Sum", "medium",
    ["array", "math", "dynamic-programming", "prefix-sum"], "numOfSubarrays",
    [("arr", "int[]")], "int",
    """
**Return the number of contiguous sub-arrays of `arr` whose sum is odd**, modulo
`10^9 + 7`.

**Examples**
```
arr = [1,3,5]              ->  4
arr = [2,4,6]              ->  0
arr = [1,2,3,4,5,6,7]      ->  16
arr = [100,100,99,99]      ->  4
```

**Constraints:** `1 <= len(arr) <= 10^5`, `1 <= arr[i] <= 100`.
""",
    """def numOfSubarrays(arr):
    MOD = 10 ** 9 + 7
    odd = 0
    even = 1
    cur = 0
    res = 0
    for x in arr:
        cur += x
        if cur % 2 == 0:
            res = (res + odd) % MOD
            even += 1
        else:
            res = (res + even) % MOD
            odd += 1
    return res % MOD
""",
    visible=[{"arr": [1, 3, 5]}, {"arr": [2, 4, 6]}, {"arr": [1, 2, 3, 4, 5, 6, 7]},
             {"arr": [100, 100, 99, 99]}],
    hidden=[{"arr": [7]}, {"arr": [2]}, {"arr": [1, 1, 1, 1]}, {"arr": [1, 2, 1, 2, 1]}],
    gen=lambda r: [{"arr": [r.randint(1, 10) for _ in range(r.randint(1, 12))]}
                   for _ in range(6)],
    brute=_oddsum_brute,
    checks=[({"arr": [1, 3, 5]}, 4), ({"arr": [2, 4, 6]}, 0),
            ({"arr": [1, 2, 3, 4, 5, 6, 7]}, 16), ({"arr": [100, 100, 99, 99]}, 4),
            ({"arr": [7]}, 1)],
    source="new_p")


# ===========================================================================
# 15. Maximum of Absolute Value Expression
# ===========================================================================
add("maximum-of-absolute-value-expression", "Maximum of Absolute Value Expression",
    "medium", ["array", "math"], "maxAbsValExpr",
    [("arr1", "int[]"), ("arr2", "int[]")], "int",
    """
For two equal-length arrays, **return the maximum over all `i, j` of**
`|arr1[i] - arr1[j]| + |arr2[i] - arr2[j]| + |i - j|`.

**Examples**
```
arr1 = [1,2,3,4], arr2 = [-1,4,5,6]            ->  13
arr1 = [1,-2,-5,0,10], arr2 = [0,-2,-1,-7,-4]  ->  20
```

**Constraints:** `2 <= len(arr1) == len(arr2) <= 4*10^4`,
`-10^6 <= arr1[i], arr2[i] <= 10^6`.
""",
    """def maxAbsValExpr(arr1, arr2):
    n = len(arr1)
    res = 0
    for s1 in (1, -1):
        for s2 in (1, -1):
            mx = float('-inf')
            mn = float('inf')
            for i in range(n):
                val = s1 * arr1[i] + s2 * arr2[i] + i
                mx = max(mx, val)
                mn = min(mn, val)
            res = max(res, mx - mn)
    return res
""",
    visible=[{"arr1": [1, 2, 3, 4], "arr2": [-1, 4, 5, 6]},
             {"arr1": [1, -2, -5, 0, 10], "arr2": [0, -2, -1, -7, -4]}],
    hidden=[{"arr1": [1, 1], "arr2": [1, 1]}, {"arr1": [0, 0, 0], "arr2": [0, 0, 0]},
            {"arr1": [3, -1], "arr2": [-2, 5]}, {"arr1": [1, 2, 3], "arr2": [3, 2, 1]}],
    gen=lambda r: [(lambda n: {"arr1": [r.randint(-10, 10) for _ in range(n)],
                               "arr2": [r.randint(-10, 10) for _ in range(n)]})
                   (r.randint(2, 8)) for _ in range(6)],
    brute=_maxabs_brute,
    checks=[({"arr1": [1, 2, 3, 4], "arr2": [-1, 4, 5, 6]}, 13),
            ({"arr1": [1, -2, -5, 0, 10], "arr2": [0, -2, -1, -7, -4]}, 20)],
    source="new_p")


# ===========================================================================
# 16. N-Queens II
# ===========================================================================
add("n-queens-ii", "N-Queens II", "hard",
    ["backtracking"], "totalNQueens", [("n", "int")], "int",
    """
**Return the number of distinct ways to place `n` queens on an `n x n` board so that
no two attack each other** (no shared row, column, or diagonal).

**Examples**
```
n = 1  ->  1
n = 4  ->  2
n = 8  ->  92
```

**Constraints:** `1 <= n <= 9`.
""",
    """def totalNQueens(n):
    count = [0]
    cols = set()
    diag = set()
    anti = set()

    def dfs(r):
        if r == n:
            count[0] += 1
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue
            cols.add(c)
            diag.add(r - c)
            anti.add(r + c)
            dfs(r + 1)
            cols.discard(c)
            diag.discard(r - c)
            anti.discard(r + c)

    dfs(0)
    return count[0]
""",
    visible=[{"n": 1}, {"n": 4}],
    hidden=[{"n": 2}, {"n": 3}, {"n": 5}, {"n": 6}, {"n": 7}],
    gen=lambda r: [{"n": r.randint(1, 7)} for _ in range(6)],
    brute=_nqueens_brute,
    checks=[({"n": 1}, 1), ({"n": 4}, 2), ({"n": 8}, 92), ({"n": 9}, 352),
            ({"n": 2}, 0)],
    source="new_p")


# ===========================================================================
# 17. Self Crossing
# ===========================================================================
add("self-crossing", "Self Crossing", "hard",
    ["array", "math", "geometry"], "isSelfCrossing", [("x", "int[]")], "bool",
    """
Starting at `(0, 0)` you walk `x[0]` north, `x[1]` west, `x[2]` south, `x[3]` east,
then north again, and so on (turning counter-clockwise each move). **Return `true`
if the path ever crosses or touches itself.**

**Examples**
```
x = [2,1,1,2]  ->  true
x = [1,2,3,4]  ->  false
x = [1,1,1,1]  ->  true
```

**Constraints:** `1 <= len(x) <= 10^5`, `1 <= x[i] <= 10^5`.
""",
    """def isSelfCrossing(x):
    n = len(x)
    for i in range(3, n):
        if x[i] >= x[i - 2] and x[i - 1] <= x[i - 3]:
            return True
        if i >= 4 and x[i - 1] == x[i - 3] and x[i] + x[i - 4] >= x[i - 2]:
            return True
        if (i >= 5 and x[i - 2] >= x[i - 4] and x[i] + x[i - 4] >= x[i - 2] and
                x[i - 1] <= x[i - 3] and x[i - 1] + x[i - 5] >= x[i - 3]):
            return True
    return False
""",
    visible=[{"x": [2, 1, 1, 2]}, {"x": [1, 2, 3, 4]}, {"x": [1, 1, 1, 1]}],
    hidden=[{"x": [1]}, {"x": [1, 1]}, {"x": [3, 3, 4, 2, 2]}, {"x": [1, 1, 2, 1, 1]}],
    gen=lambda r: [{"x": [r.randint(1, 5) for _ in range(r.randint(1, 8))]}
                   for _ in range(8)],
    brute=_selfcross_brute,
    checks=[({"x": [2, 1, 1, 2]}, True), ({"x": [1, 2, 3, 4]}, False),
            ({"x": [1, 1, 1, 1]}, True)],
    source="new_p")


# ===========================================================================
# 18. Find Minimum in Rotated Sorted Array II
# ===========================================================================
add("find-minimum-in-rotated-sorted-array-ii",
    "Find Minimum in Rotated Sorted Array II", "hard",
    ["array", "binary-search"], "findMin", [("nums", "int[]")], "int",
    """
A sorted (ascending) array, **which may contain duplicates**, has been rotated at an
unknown pivot. **Return its minimum element.**

**Examples**
```
nums = [1,3,5]      ->  1
nums = [2,2,2,0,1]  ->  0
```

**Constraints:** `1 <= len(nums) <= 5000`, values may repeat.
""",
    """def findMin(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        elif nums[mid] < nums[hi]:
            hi = mid
        else:
            hi -= 1
    return nums[lo]
""",
    visible=[{"nums": [1, 3, 5]}, {"nums": [2, 2, 2, 0, 1]}],
    hidden=[{"nums": [1]}, {"nums": [3, 1, 3]}, {"nums": [2, 2, 2, 2]},
            {"nums": [10, 1, 10, 10, 10]}, {"nums": [1, 1, 1, 0, 1]}],
    gen=lambda r: [_rot_gen(r) for _ in range(8)],
    brute=lambda nums: min(nums),
    checks=[({"nums": [1, 3, 5]}, 1), ({"nums": [2, 2, 2, 0, 1]}, 0),
            ({"nums": [3, 1, 3]}, 1)],
    source="new_p")


# ===========================================================================
# 19. Letter Tile Possibilities
# ===========================================================================
add("letter-tile-possibilities", "Letter Tile Possibilities", "medium",
    ["string", "backtracking", "hash-table"], "numTilePossibilities",
    [("tiles", "string")], "int",
    """
Each tile shows one uppercase letter. **Return the number of distinct non-empty
sequences of letters that can be formed** using some of the tiles (order matters,
each tile used at most once).

**Examples**
```
tiles = "AAB"     ->  8
tiles = "AAABBC"  ->  188
tiles = "V"       ->  1
```

**Constraints:** `1 <= len(tiles) <= 7`, uppercase letters.
""",
    """def numTilePossibilities(tiles):
    from collections import Counter
    cnt = Counter(tiles)

    def dfs(counter):
        total = 0
        for ch in counter:
            if counter[ch] > 0:
                counter[ch] -= 1
                total += 1 + dfs(counter)
                counter[ch] += 1
        return total

    return dfs(cnt)
""",
    visible=[{"tiles": "AAB"}, {"tiles": "AAABBC"}, {"tiles": "V"}],
    hidden=[{"tiles": "AB"}, {"tiles": "AAA"}, {"tiles": "ABC"}, {"tiles": "AABB"}],
    gen=lambda r: [{"tiles": sstr(r, 1, 6, "ABC")} for _ in range(6)],
    brute=_tile_brute,
    checks=[({"tiles": "AAB"}, 8), ({"tiles": "AAABBC"}, 188), ({"tiles": "V"}, 1)],
    source="new_p")
