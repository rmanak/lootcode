"""Batch 004 of the new_p.txt import (20 problems)."""
from scripts.build_bank import add, ilist, sstr  # noqa: F401


# --------------------------- brute / reference helpers ---------------------
def _replen_brute(nums1, nums2):
    m, n = len(nums1), len(nums2)
    best = 0
    for i in range(m):
        for j in range(n):
            k = 0
            while i + k < m and j + k < n and nums1[i + k] == nums2[j + k]:
                k += 1
            best = max(best, k)
    return best


def _atmostn_brute(digits, n):
    ds = set(digits)
    return sum(1 for x in range(1, n + 1) if all(c in ds for c in str(x)))


def _coins_brute(piles):
    piles = sorted(piles)
    n = len(piles) // 3
    res = 0
    i = len(piles) - 2
    for _ in range(n):
        res += piles[i]
        i -= 2
    return res


def _minset_brute(arr):
    from collections import Counter
    counts = sorted(Counter(arr).values())
    removed = 0
    res = 0
    half = len(arr) / 2
    while removed < half:
        removed += counts.pop()
        res += 1
    return res


def _partk_brute(nums, k):
    total = sum(nums)
    if total % k:
        return False
    target = total // k
    n = len(nums)
    from functools import lru_cache

    @lru_cache(None)
    def dp(mask, rem):
        if mask == (1 << n) - 1:
            return True
        for i in range(n):
            if not (mask >> i) & 1 and nums[i] <= rem:
                nr = rem - nums[i]
                if nr == 0:
                    nr = target
                if dp(mask | (1 << i), nr):
                    return True
        return False
    return dp(0, target)


def _triples_brute(A):
    n = len(A)
    res = 0
    for i in range(n):
        for j in range(n):
            aij = A[i] & A[j]
            for k in range(n):
                if aij & A[k] == 0:
                    res += 1
    return res


def _circ_brute(nums):
    n = len(nums)
    best = float('-inf')
    for i in range(n):
        s = 0
        for L in range(1, n + 1):
            s += nums[(i + L - 1) % n]
            best = max(best, s)
    return best


def _validword_brute(s):
    while 'abc' in s:
        s = s.replace('abc', '', 1)
    return s == ''


def _equalsub_brute(s, t, maxCost):
    n = len(s)
    best = 0
    for i in range(n):
        cost = 0
        for j in range(i, n):
            cost += abs(ord(s[j]) - ord(t[j]))
            if cost <= maxCost:
                best = max(best, j - i + 1)
            else:
                break
    return best


def _fib_brute(k):
    fibs = []
    a, b = 1, 1
    while a <= k:
        fibs.append(a)
        a, b = b, a + b
    INF = float('inf')
    dp = [0] + [INF] * k
    for i in range(1, k + 1):
        for f in fibs:
            if f <= i:
                dp[i] = min(dp[i], dp[i - f] + 1)
    return dp[k]


def _numtrees_brute(n):
    from functools import lru_cache

    @lru_cache(None)
    def f(m):
        if m <= 1:
            return 1
        return sum(f(i) * f(m - 1 - i) for i in range(m))
    return f(n)


def _mountain_brute(arr):
    n = len(arr)
    best = 0
    for i in range(1, n - 1):
        if arr[i - 1] < arr[i] > arr[i + 1]:
            l = i
            while l > 0 and arr[l - 1] < arr[l]:
                l -= 1
            r = i
            while r < n - 1 and arr[r] > arr[r + 1]:
                r += 1
            best = max(best, r - l + 1)
    return best


def _searchrot_brute(nums, target):
    return nums.index(target) if target in nums else -1


def _onesz_brute(strs, m, n):
    L = len(strs)
    best = 0
    for mask in range(1 << L):
        z = o = cnt = 0
        for i in range(L):
            if mask >> i & 1:
                z += strs[i].count('0')
                o += strs[i].count('1')
                cnt += 1
        if z <= m and o <= n:
            best = max(best, cnt)
    return best


def _largest_brute(nums):
    from itertools import permutations
    best = 0
    for p in permutations(map(str, nums)):
        best = max(best, int("".join(p)))
    return str(best)


def _cd3_brute(nums, k, t):
    if k <= 0 or t < 0:
        return False
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, min(n, i + k + 1)):
            if abs(nums[i] - nums[j]) <= t:
                return True
    return False


def _gen_friends(r):
    n = 2 * r.randint(1, 3)
    prefs = []
    for i in range(n):
        others = [j for j in range(n) if j != i]
        r.shuffle(others)
        prefs.append(others)
    perm = list(range(n))
    r.shuffle(perm)
    pairs = [[perm[2 * i], perm[2 * i + 1]] for i in range(n // 2)]
    return {"n": n, "preferences": prefs, "pairs": pairs}


def _gen_rotated(r):
    a = sorted(set(r.randint(-20, 20) for _ in range(r.randint(1, 12))))
    p = r.randint(0, len(a) - 1)
    rot = a[p:] + a[:p]
    target = r.randint(-22, 22)
    return {"nums": rot, "target": target}


# ===========================================================================
# 1. Integer to English Words
# ===========================================================================
add("integer-to-english-words", "Integer to English Words", "hard",
    ["math", "string", "recursion"], "numberToWords", [("num", "int")], "string",
    """
**Convert a non-negative integer `num` to its English words representation.**

**Examples**
```
123        ->  "One Hundred Twenty Three"
12345      ->  "Twelve Thousand Three Hundred Forty Five"
1234567    ->  "One Million Two Hundred Thirty Four Thousand Five Hundred Sixty Seven"
```

**Constraints:** `0 <= num <= 2^31 - 1`.
""",
    """def numberToWords(num):
    if num == 0:
        return "Zero"
    below20 = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
               "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
               "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
            "Eighty", "Ninety"]
    thousands = ["", "Thousand", "Million", "Billion"]

    def helper(n):
        if n == 0:
            return ""
        if n < 20:
            return below20[n] + " "
        if n < 100:
            return tens[n // 10] + " " + helper(n % 10)
        return below20[n // 100] + " Hundred " + helper(n % 100)

    res = ""
    i = 0
    while num > 0:
        if num % 1000 != 0:
            res = helper(num % 1000) + thousands[i] + " " + res
        num //= 1000
        i += 1
    return " ".join(res.split())
""",
    visible=[{"num": 123}, {"num": 12345}, {"num": 1234567}],
    hidden=[{"num": 0}, {"num": 1234567891}, {"num": 100}, {"num": 1000000},
            {"num": 20}, {"num": 2147483647}],
    checks=[({"num": 123}, "One Hundred Twenty Three"),
            ({"num": 12345}, "Twelve Thousand Three Hundred Forty Five"),
            ({"num": 0}, "Zero"),
            ({"num": 1234567}, "One Million Two Hundred Thirty Four Thousand Five Hundred Sixty Seven"),
            ({"num": 1234567891}, "One Billion Two Hundred Thirty Four Million Five Hundred Sixty Seven Thousand Eight Hundred Ninety One")],
    source="new_p")


# ===========================================================================
# 2. Count Unhappy Friends
# ===========================================================================
add("count-unhappy-friends", "Count Unhappy Friends", "medium",
    ["array", "simulation", "counting"], "unhappyFriends",
    [("n", "int"), ("preferences", "int[][]"), ("pairs", "int[][]")], "int",
    """
`n` friends (even `n`) are split into `n/2` pairs given by `pairs`.
`preferences[i]` lists the other friends from most to least preferred. Friend `x`
(paired with `y`) is **unhappy** if there is some friend `u` (paired with `v`) such
that `x` prefers `u` over `y` **and** `u` prefers `x` over `v`. **Return the number
of unhappy friends.**

**Examples**
```
n=4, preferences=[[1,2,3],[3,2,0],[3,1,0],[1,2,0]], pairs=[[0,1],[2,3]]  ->  2
n=2, preferences=[[1],[0]], pairs=[[1,0]]                                ->  0
n=4, preferences=[[1,3,2],[2,3,0],[1,3,0],[0,2,1]], pairs=[[1,3],[0,2]]  ->  4
```

**Constraints:** `2 <= n <= 500` (even), `preferences[i]` is a permutation of the
other `n-1` friends, each friend in exactly one pair.
""",
    """def unhappyFriends(n, preferences, pairs):
    rank = [[0] * n for _ in range(n)]
    for x in range(n):
        for idx, y in enumerate(preferences[x]):
            rank[x][y] = idx
    partner = [0] * n
    for a, b in pairs:
        partner[a] = b
        partner[b] = a
    unhappy = 0
    for x in range(n):
        y = partner[x]
        for u in preferences[x]:
            if u == y:
                break
            v = partner[u]
            if rank[u][x] < rank[u][v]:
                unhappy += 1
                break
    return unhappy
""",
    visible=[{"n": 4, "preferences": [[1, 2, 3], [3, 2, 0], [3, 1, 0], [1, 2, 0]],
              "pairs": [[0, 1], [2, 3]]},
             {"n": 2, "preferences": [[1], [0]], "pairs": [[1, 0]]},
             {"n": 4, "preferences": [[1, 3, 2], [2, 3, 0], [1, 3, 0], [0, 2, 1]],
              "pairs": [[1, 3], [0, 2]]}],
    hidden=[{"n": 2, "preferences": [[1], [0]], "pairs": [[0, 1]]}],
    gen=lambda r: [_gen_friends(r) for _ in range(6)],
    checks=[({"n": 4, "preferences": [[1, 2, 3], [3, 2, 0], [3, 1, 0], [1, 2, 0]],
              "pairs": [[0, 1], [2, 3]]}, 2),
            ({"n": 2, "preferences": [[1], [0]], "pairs": [[1, 0]]}, 0),
            ({"n": 4, "preferences": [[1, 3, 2], [2, 3, 0], [1, 3, 0], [0, 2, 1]],
              "pairs": [[1, 3], [0, 2]]}, 4)],
    source="new_p")


# ===========================================================================
# 3. Maximum Length of Repeated Subarray
# ===========================================================================
add("maximum-length-of-repeated-subarray", "Maximum Length of Repeated Subarray",
    "medium", ["array", "dynamic-programming", "binary-search"], "findLength",
    [("nums1", "int[]"), ("nums2", "int[]")], "int",
    """
Given two integer arrays `nums1` and `nums2`, **return the maximum length of a
subarray (contiguous) that appears in both**.

**Example**
```
nums1 = [1,2,3,2,1], nums2 = [3,2,1,4,7]  ->  3    ([3,2,1])
```

**Constraints:** `1 <= len(nums1), len(nums2) <= 1000`, `0 <= nums[i] <= 100`.
""",
    """def findLength(nums1, nums2):
    m, n = len(nums1), len(nums2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    best = 0
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if nums1[i] == nums2[j]:
                dp[i][j] = dp[i + 1][j + 1] + 1
                best = max(best, dp[i][j])
    return best
""",
    visible=[{"nums1": [1, 2, 3, 2, 1], "nums2": [3, 2, 1, 4, 7]}],
    hidden=[{"nums1": [0, 0, 0, 0, 0], "nums2": [0, 0, 0, 0, 0]},
            {"nums1": [1, 2, 3], "nums2": [4, 5, 6]}, {"nums1": [1], "nums2": [1]},
            {"nums1": [1, 2, 3, 4, 5], "nums2": [2, 3, 4]}],
    gen=lambda r: [{"nums1": ilist(r, 1, 10, 0, 4), "nums2": ilist(r, 1, 10, 0, 4)}
                   for _ in range(6)],
    brute=_replen_brute,
    checks=[({"nums1": [1, 2, 3, 2, 1], "nums2": [3, 2, 1, 4, 7]}, 3)],
    source="new_p")


# ===========================================================================
# 4. Numbers At Most N Given Digit Set
# ===========================================================================
add("numbers-at-most-n-given-digit-set", "Numbers At Most N Given Digit Set",
    "hard", ["math", "dynamic-programming", "binary-search"], "atMostNGivenDigitSet",
    [("digits", "string[]"), ("n", "int")], "int",
    """
Using only the given `digits` (each usable any number of times), **return how many
positive integers `<= n` can be written.** `digits` is a sorted list of distinct
characters from `'1'`..`'9'`.

**Examples**
```
digits = ["1","3","5","7"], n = 100         ->  20
digits = ["1","4","9"],     n = 1000000000  ->  29523
digits = ["7"],             n = 8           ->  1
```

**Constraints:** `1 <= len(digits) <= 9`, `1 <= n <= 10^9`.
""",
    """def atMostNGivenDigitSet(digits, n):
    s = str(n)
    L = len(s)
    D = len(digits)
    res = 0
    for i in range(1, L):
        res += D ** i
    ds = digits
    for i, ch in enumerate(s):
        res += sum(1 for d in ds if d < ch) * (D ** (L - i - 1))
        if ch not in ds:
            break
    else:
        res += 1
    return res
""",
    visible=[{"digits": ["1", "3", "5", "7"], "n": 100},
             {"digits": ["1", "4", "9"], "n": 1000000000},
             {"digits": ["7"], "n": 8}],
    hidden=[{"digits": ["3", "4", "8"], "n": 4}, {"digits": ["1"], "n": 1},
            {"digits": ["1", "2", "3", "4", "5", "6", "7", "8", "9"], "n": 1000},
            {"digits": ["5", "6"], "n": 555}],
    gen=lambda r: [(lambda ds: {"digits": ds, "n": r.randint(1, 2000)})
                   (sorted(r.sample("123456789", r.randint(1, 5)))) for _ in range(6)],
    checks=[({"digits": ["1", "3", "5", "7"], "n": 100}, 20),
            ({"digits": ["1", "4", "9"], "n": 1000000000}, 29523),
            ({"digits": ["7"], "n": 8}, 1),
            ({"digits": ["1", "3", "5", "7"], "n": 10}, 4),
            ({"digits": ["7"], "n": 77}, 2),
            ({"digits": ["3", "4", "8"], "n": 4}, 2)],
    source="new_p")


# ===========================================================================
# 5. Maximum Number of Coins You Can Get
# ===========================================================================
add("maximum-number-of-coins-you-can-get", "Maximum Number of Coins You Can Get",
    "medium", ["array", "greedy", "sorting", "math"], "maxCoins",
    [("piles", "int[]")], "int",
    """
There are `3n` piles. Repeatedly: pick any 3 remaining piles; Alice takes the
largest, **you** take the second largest, Bob takes the smallest. **Return the
maximum number of coins you can collect.** (Sort, then take every second pile from
the top, skipping the smallest `n`.)

**Examples**
```
piles = [2,4,1,2,7,8]          ->  9    (you take 7 and 2)
piles = [2,4,5]                ->  4
piles = [9,8,7,6,5,1,2,3,4]    ->  18
```

**Constraints:** `3 <= len(piles) <= 10^5`, `len(piles) % 3 == 0`,
`1 <= piles[i] <= 10^4`.
""",
    """def maxCoins(piles):
    piles = sorted(piles)
    n = len(piles) // 3
    res = 0
    i = len(piles) - 2
    for _ in range(n):
        res += piles[i]
        i -= 2
    return res
""",
    visible=[{"piles": [2, 4, 1, 2, 7, 8]}, {"piles": [2, 4, 5]},
             {"piles": [9, 8, 7, 6, 5, 1, 2, 3, 4]}],
    hidden=[{"piles": [1, 1, 1]}, {"piles": [1, 2, 3, 4, 5, 6]},
            {"piles": [6, 6, 6, 6, 6, 6, 6, 6, 6]}],
    gen=lambda r: [{"piles": [r.randint(1, 20) for _ in range(3 * r.randint(1, 5))]}
                   for _ in range(6)],
    brute=_coins_brute,
    checks=[({"piles": [2, 4, 1, 2, 7, 8]}, 9), ({"piles": [2, 4, 5]}, 4),
            ({"piles": [9, 8, 7, 6, 5, 1, 2, 3, 4]}, 18)],
    source="new_p")


# ===========================================================================
# 6. Reduce Array Size to The Half
# ===========================================================================
add("reduce-array-size-to-the-half", "Reduce Array Size to The Half", "medium",
    ["array", "greedy", "sorting", "heap", "hash-table"], "minSetSize",
    [("arr", "int[]")], "int",
    """
Choose a set of values and remove **all** their occurrences from `arr`. **Return the
minimum size of such a set** so that at least half of `arr`'s elements are removed.

**Examples**
```
arr = [3,3,3,3,5,5,5,2,2,7]   ->  2
arr = [7,7,7,7,7,7]           ->  1
arr = [1,2,3,4,5,6,7,8,9,10]  ->  5
```

**Constraints:** `1 <= len(arr) <= 10^5` (even), `1 <= arr[i] <= 10^5`.
""",
    """def minSetSize(arr):
    from collections import Counter
    counts = sorted(Counter(arr).values(), reverse=True)
    removed = 0
    res = 0
    half = len(arr) / 2
    for c in counts:
        removed += c
        res += 1
        if removed >= half:
            break
    return res
""",
    visible=[{"arr": [3, 3, 3, 3, 5, 5, 5, 2, 2, 7]}, {"arr": [7, 7, 7, 7, 7, 7]},
             {"arr": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}],
    hidden=[{"arr": [1, 9]}, {"arr": [1000, 1000, 3, 7]}, {"arr": [1, 1, 1, 1]},
            {"arr": [2, 2, 2, 3, 3, 4]}],
    gen=lambda r: [{"arr": [r.randint(1, 8) for _ in range(2 * r.randint(1, 8))]}
                   for _ in range(6)],
    brute=_minset_brute,
    checks=[({"arr": [3, 3, 3, 3, 5, 5, 5, 2, 2, 7]}, 2),
            ({"arr": [7, 7, 7, 7, 7, 7]}, 1), ({"arr": [1, 9]}, 1),
            ({"arr": [1000, 1000, 3, 7]}, 1),
            ({"arr": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}, 5)],
    source="new_p")


# ===========================================================================
# 7. Partition to K Equal Sum Subsets
# ===========================================================================
add("partition-to-k-equal-sum-subsets", "Partition to K Equal Sum Subsets", "medium",
    ["array", "dynamic-programming", "backtracking", "bitmask"],
    "canPartitionKSubsets", [("nums", "int[]"), ("k", "int")], "bool",
    """
Given `nums` and a positive integer `k`, **return `true` if `nums` can be split into
`k` non-empty subsets all with equal sum**, else `false`.

**Example**
```
nums = [4,3,2,3,5,2,1], k = 4  ->  true    ((5),(1,4),(2,3),(2,3))
```

**Constraints:** `1 <= k <= len(nums) <= 16`, `1 <= nums[i] < 10^4`.
""",
    """def canPartitionKSubsets(nums, k):
    total = sum(nums)
    if total % k != 0:
        return False
    target = total // k
    nums.sort(reverse=True)
    if nums[0] > target:
        return False
    used = [False] * len(nums)

    def dfs(start, k_left, cur):
        if k_left == 0:
            return True
        if cur == target:
            return dfs(0, k_left - 1, 0)
        for i in range(start, len(nums)):
            if not used[i] and cur + nums[i] <= target:
                used[i] = True
                if dfs(i + 1, k_left, cur + nums[i]):
                    return True
                used[i] = False
                if cur == 0:
                    break
        return False

    return dfs(0, k, 0)
""",
    visible=[{"nums": [4, 3, 2, 3, 5, 2, 1], "k": 4}],
    hidden=[{"nums": [1, 2, 3, 4], "k": 3}, {"nums": [1, 1, 1, 1], "k": 2},
            {"nums": [2, 2, 2, 2, 3, 4, 5], "k": 4}, {"nums": [4], "k": 1},
            {"nums": [1, 1, 1, 1], "k": 4}],
    gen=lambda r: [(lambda a: {"nums": a, "k": r.randint(1, len(a))})
                   (ilist(r, 1, 8, 1, 6)) for _ in range(6)],
    brute=_partk_brute,
    checks=[({"nums": [4, 3, 2, 3, 5, 2, 1], "k": 4}, True),
            ({"nums": [1, 2, 3, 4], "k": 3}, False),
            ({"nums": [1, 1, 1, 1], "k": 4}, True)],
    source="new_p")


# ===========================================================================
# 8. Triples with Bitwise AND Equal To Zero
# ===========================================================================
add("triples-with-bitwise-and-equal-to-zero", "Triples with Bitwise AND Equal To Zero",
    "hard", ["array", "bit-manipulation", "hash-table"], "countTriplets",
    [("A", "int[]")], "int",
    """
Given an array `A`, **return the number of index triples `(i, j, k)`** (each
independently ranging over all indices) such that `A[i] & A[j] & A[k] == 0`, where
`&` is bitwise AND.

**Example**
```
A = [2,1,3]  ->  12
```

**Constraints:** `1 <= len(A) <= 1000`, `0 <= A[i] < 2^16`.
""",
    """def countTriplets(A):
    from collections import Counter
    pair = Counter()
    for x in A:
        for y in A:
            pair[x & y] += 1
    res = 0
    for x in A:
        for v, c in pair.items():
            if x & v == 0:
                res += c
    return res
""",
    visible=[{"A": [2, 1, 3]}],
    hidden=[{"A": [0]}, {"A": [1, 1, 1]}, {"A": [7]}, {"A": [1, 2, 4, 8]},
            {"A": [5, 3, 6, 1, 7, 2]}],
    gen=lambda r: [{"A": [r.randint(0, 15) for _ in range(r.randint(1, 10))]}
                   for _ in range(6)],
    brute=_triples_brute,
    checks=[({"A": [2, 1, 3]}, 12), ({"A": [0]}, 1), ({"A": [7]}, 0)],
    source="new_p")


# ===========================================================================
# 9. Maximum Sum Circular Subarray
# ===========================================================================
add("maximum-sum-circular-subarray", "Maximum Sum Circular Subarray", "medium",
    ["array", "dynamic-programming", "divide-and-conquer", "queue"],
    "maxSubarraySumCircular", [("nums", "int[]")], "int",
    """
Given a **circular** integer array `nums` (the end wraps to the start), **return the
maximum sum of a non-empty subarray.** A subarray may use each element at most once.

**Examples**
```
nums = [1,-2,3,-2]   ->  3
nums = [5,-3,5]      ->  10   (wraps: [5,5])
nums = [-2,-3,-1]    ->  -1
```

**Constraints:** `1 <= len(nums) <= 3*10^4`, `-3*10^4 <= nums[i] <= 3*10^4`.
""",
    """def maxSubarraySumCircular(nums):
    total = sum(nums)
    cur_max = 0
    best_max = float('-inf')
    cur_min = 0
    best_min = float('inf')
    for x in nums:
        cur_max = max(cur_max + x, x)
        best_max = max(best_max, cur_max)
        cur_min = min(cur_min + x, x)
        best_min = min(best_min, cur_min)
    if best_max < 0:
        return best_max
    return max(best_max, total - best_min)
""",
    visible=[{"nums": [1, -2, 3, -2]}, {"nums": [5, -3, 5]}, {"nums": [-2, -3, -1]}],
    hidden=[{"nums": [3, -1, 2, -1]}, {"nums": [3, -2, 2, -3]}, {"nums": [-5]},
            {"nums": [8]}, {"nums": [2, -2, 2, -2, 2]}],
    gen=lambda r: [{"nums": ilist(r, 1, 12, -8, 8)} for _ in range(6)],
    brute=_circ_brute,
    checks=[({"nums": [1, -2, 3, -2]}, 3), ({"nums": [5, -3, 5]}, 10),
            ({"nums": [3, -1, 2, -1]}, 4), ({"nums": [3, -2, 2, -3]}, 3),
            ({"nums": [-2, -3, -1]}, -1)],
    source="new_p")


# ===========================================================================
# 10. Check If Word Is Valid After Substitutions
# ===========================================================================
add("check-if-word-is-valid-after-substitutions",
    "Check If Word Is Valid After Substitutions", "medium",
    ["string", "stack"], "isValid", [("s", "string")], "bool",
    """
Starting from `""`, you may repeatedly insert `"abc"` at any position. **Return
`true` if `s` can be produced** this way, else `false`. (`s` consists of `a`, `b`,
`c` only.)

**Examples**
```
s = "aabcbc"        ->  true
s = "abcabcababcc"  ->  true
s = "abccba"        ->  false
```

**Constraints:** `1 <= len(s) <= 2*10^4`, characters are `a`, `b`, `c`.
""",
    """def isValid(s):
    stack = []
    for c in s:
        if c == 'c':
            if len(stack) < 2 or stack[-1] != 'b' or stack[-2] != 'a':
                return False
            stack.pop()
            stack.pop()
        else:
            stack.append(c)
    return not stack
""",
    visible=[{"s": "aabcbc"}, {"s": "abcabcababcc"}, {"s": "abccba"}],
    hidden=[{"s": "cababc"}, {"s": "abc"}, {"s": "a"}, {"s": "abcabc"},
            {"s": "aabcbcabc"}],
    gen=lambda r: [{"s": "".join(r.choice("abc") for _ in range(r.randint(1, 9)))}
                   for _ in range(6)],
    brute=_validword_brute,
    checks=[({"s": "aabcbc"}, True), ({"s": "abcabcababcc"}, True),
            ({"s": "abccba"}, False), ({"s": "cababc"}, False)],
    source="new_p")


# ===========================================================================
# 11. Get Equal Substrings Within Budget
# ===========================================================================
add("get-equal-substrings-within-budget", "Get Equal Substrings Within Budget",
    "medium", ["string", "sliding-window", "binary-search"], "equalSubstring",
    [("s", "string"), ("t", "string"), ("maxCost", "int")], "int",
    """
Changing `s[i]` to `t[i]` costs `abs(ord(s[i]) - ord(t[i]))`. With a total budget of
`maxCost`, **return the maximum length of a substring of `s` that can be transformed
into the corresponding substring of `t`** within budget.

**Examples**
```
s = "abcd", t = "bcdf", maxCost = 3  ->  3
s = "abcd", t = "cdef", maxCost = 3  ->  1
s = "abcd", t = "acde", maxCost = 0  ->  1
```

**Constraints:** `1 <= len(s) == len(t) <= 10^5`, `0 <= maxCost <= 10^6`,
lowercase letters.
""",
    """def equalSubstring(s, t, maxCost):
    l = 0
    cost = 0
    best = 0
    for r in range(len(s)):
        cost += abs(ord(s[r]) - ord(t[r]))
        while cost > maxCost:
            cost -= abs(ord(s[l]) - ord(t[l]))
            l += 1
        best = max(best, r - l + 1)
    return best
""",
    visible=[{"s": "abcd", "t": "bcdf", "maxCost": 3},
             {"s": "abcd", "t": "cdef", "maxCost": 3},
             {"s": "abcd", "t": "acde", "maxCost": 0}],
    hidden=[{"s": "a", "t": "a", "maxCost": 0}, {"s": "krrgw", "t": "zjxss", "maxCost": 19},
            {"s": "abc", "t": "abc", "maxCost": 100}, {"s": "ab", "t": "ba", "maxCost": 0}],
    gen=lambda r: [(lambda n: {"s": sstr(r, n, n, "abcde"), "t": sstr(r, n, n, "abcde"),
                               "maxCost": r.randint(0, 10)})(r.randint(1, 10))
                   for _ in range(6)],
    brute=_equalsub_brute,
    checks=[({"s": "abcd", "t": "bcdf", "maxCost": 3}, 3),
            ({"s": "abcd", "t": "cdef", "maxCost": 3}, 1),
            ({"s": "abcd", "t": "acde", "maxCost": 0}, 1)],
    source="new_p")


# ===========================================================================
# 12. Find the Minimum Number of Fibonacci Numbers Whose Sum Is K
# ===========================================================================
add("find-the-minimum-number-of-fibonacci-numbers-whose-sum-is-k",
    "Find the Minimum Number of Fibonacci Numbers Whose Sum Is K", "medium",
    ["math", "greedy"], "findMinFibonacciNumbers", [("k", "int")], "int",
    """
**Return the minimum number of Fibonacci numbers that sum to `k`** (the same
Fibonacci number may be reused). Fibonacci numbers: `1, 1, 2, 3, 5, 8, 13, ...`.

**Examples**
```
k = 7   ->  2    (2 + 5)
k = 10  ->  2    (2 + 8)
k = 19  ->  3    (1 + 5 + 13)
```

**Constraints:** `1 <= k <= 10^9`.
""",
    """def findMinFibonacciNumbers(k):
    fibs = [1, 1]
    while fibs[-1] <= k:
        fibs.append(fibs[-1] + fibs[-2])
    count = 0
    i = len(fibs) - 1
    while k > 0:
        if fibs[i] <= k:
            k -= fibs[i]
            count += 1
        else:
            i -= 1
    return count
""",
    visible=[{"k": 7}, {"k": 10}, {"k": 19}],
    hidden=[{"k": 1}, {"k": 2}, {"k": 13}, {"k": 1000}, {"k": 2000}],
    gen=lambda r: [{"k": r.randint(1, 2000)} for _ in range(6)],
    brute=_fib_brute,
    checks=[({"k": 7}, 2), ({"k": 10}, 2), ({"k": 19}, 3), ({"k": 1}, 1)],
    source="new_p")


# ===========================================================================
# 13. Unique Binary Search Trees
# ===========================================================================
add("unique-binary-search-trees", "Unique Binary Search Trees", "medium",
    ["math", "dynamic-programming", "tree"], "numTrees", [("n", "int")], "int",
    """
**Return the number of structurally unique binary search trees** that store the
values `1 .. n` (the `n`-th Catalan number).

**Example**
```
n = 3  ->  5
```

**Constraints:** `1 <= n <= 19`.
""",
    """def numTrees(n):
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for j in range(i):
            dp[i] += dp[j] * dp[i - 1 - j]
    return dp[n]
""",
    visible=[{"n": 3}],
    hidden=[{"n": 1}, {"n": 2}, {"n": 4}, {"n": 5}, {"n": 10}, {"n": 19}],
    gen=lambda r: [{"n": r.randint(1, 12)} for _ in range(6)],
    brute=_numtrees_brute,
    checks=[({"n": 3}, 5), ({"n": 1}, 1), ({"n": 4}, 14), ({"n": 5}, 42)],
    source="new_p")


# ===========================================================================
# 14. Longest Mountain in Array
# ===========================================================================
add("longest-mountain-in-array", "Longest Mountain in Array", "medium",
    ["array", "two-pointers", "dynamic-programming"], "longestMountain",
    [("arr", "int[]")], "int",
    """
A *mountain* is a contiguous subarray of length `>= 3` that strictly increases to a
peak then strictly decreases. **Return the length of the longest mountain** in
`arr`, or `0` if there is none.

**Examples**
```
arr = [2,1,4,7,3,2,5]  ->  5    ([1,4,7,3,2])
arr = [2,2,2]          ->  0
```

**Constraints:** `0 <= len(arr) <= 10^4`, `0 <= arr[i] <= 10^4`.
""",
    """def longestMountain(arr):
    n = len(arr)
    best = 0
    i = 1
    while i < n - 1:
        if arr[i - 1] < arr[i] > arr[i + 1]:
            l = i - 1
            while l > 0 and arr[l - 1] < arr[l]:
                l -= 1
            r = i + 1
            while r < n - 1 and arr[r] > arr[r + 1]:
                r += 1
            best = max(best, r - l + 1)
            i = r + 1
        else:
            i += 1
    return best
""",
    visible=[{"arr": [2, 1, 4, 7, 3, 2, 5]}, {"arr": [2, 2, 2]}],
    hidden=[{"arr": []}, {"arr": [1, 2, 3]}, {"arr": [3, 2, 1]},
            {"arr": [0, 1, 0, 1, 0]}, {"arr": [1, 3, 2, 1, 4, 5, 3]}],
    gen=lambda r: [{"arr": ilist(r, 0, 14, 0, 5)} for _ in range(6)],
    brute=_mountain_brute,
    checks=[({"arr": [2, 1, 4, 7, 3, 2, 5]}, 5), ({"arr": [2, 2, 2]}, 0)],
    source="new_p")


# ===========================================================================
# 15. Search in Rotated Sorted Array
# ===========================================================================
add("search-in-rotated-sorted-array", "Search in Rotated Sorted Array", "medium",
    ["array", "binary-search"], "search",
    [("nums", "int[]"), ("target", "int")], "int",
    """
A strictly ascending array with **no duplicates** is rotated at an unknown pivot
(e.g. `[0,1,2,4,5,6,7]` -> `[4,5,6,7,0,1,2]`). Given the rotated `nums` and a
`target`, **return the index of `target`**, or `-1` if absent. Aim for `O(log n)`.

**Examples**
```
nums = [4,5,6,7,0,1,2], target = 0  ->  4
nums = [4,5,6,7,0,1,2], target = 3  ->  -1
```

**Constraints:** `1 <= len(nums) <= 5000`, values distinct, `-10^4 <= nums[i] <= 10^4`.
""",
    """def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
""",
    visible=[{"nums": [4, 5, 6, 7, 0, 1, 2], "target": 0},
             {"nums": [4, 5, 6, 7, 0, 1, 2], "target": 3}],
    hidden=[{"nums": [1], "target": 1}, {"nums": [1], "target": 0},
            {"nums": [5, 1, 3], "target": 5}, {"nums": [4, 5, 6, 7, 0, 1, 2], "target": 2}],
    gen=lambda r: [_gen_rotated(r) for _ in range(6)],
    brute=_searchrot_brute,
    checks=[({"nums": [4, 5, 6, 7, 0, 1, 2], "target": 0}, 4),
            ({"nums": [4, 5, 6, 7, 0, 1, 2], "target": 3}, -1)],
    source="new_p")


# ===========================================================================
# 16. Ones and Zeroes
# ===========================================================================
add("ones-and-zeroes", "Ones and Zeroes", "medium",
    ["array", "string", "dynamic-programming"], "findMaxForm",
    [("strs", "string[]"), ("m", "int"), ("n", "int")], "int",
    """
Given binary strings `strs` and budgets of `m` zeros and `n` ones, **return the
maximum number of strings you can select** so that the chosen strings together use
at most `m` `0`s and `n` `1`s.

**Examples**
```
strs = ["10","0001","111001","1","0"], m = 5, n = 3  ->  4
strs = ["10","0","1"], m = 1, n = 1                  ->  2
```

**Constraints:** `1 <= len(strs) <= 600`, `1 <= len(strs[i]) <= 100`,
`0 <= m, n <= 100`.
""",
    """def findMaxForm(strs, m, n):
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for s in strs:
        zeros = s.count('0')
        ones = s.count('1')
        for i in range(m, zeros - 1, -1):
            for j in range(n, ones - 1, -1):
                dp[i][j] = max(dp[i][j], dp[i - zeros][j - ones] + 1)
    return dp[m][n]
""",
    visible=[{"strs": ["10", "0001", "111001", "1", "0"], "m": 5, "n": 3},
             {"strs": ["10", "0", "1"], "m": 1, "n": 1}],
    hidden=[{"strs": ["0"], "m": 0, "n": 0}, {"strs": ["1", "1", "1"], "m": 0, "n": 2},
            {"strs": ["00", "11", "01"], "m": 2, "n": 2},
            {"strs": ["111", "1000", "1000", "1000"], "m": 9, "n": 3}],
    gen=lambda r: [{"strs": ["".join(r.choice("01") for _ in range(r.randint(1, 4)))
                             for _ in range(r.randint(1, 6))],
                    "m": r.randint(0, 6), "n": r.randint(0, 6)} for _ in range(6)],
    brute=_onesz_brute,
    checks=[({"strs": ["10", "0001", "111001", "1", "0"], "m": 5, "n": 3}, 4),
            ({"strs": ["10", "0", "1"], "m": 1, "n": 1}, 2)],
    source="new_p")


# ===========================================================================
# 17. Largest Number
# ===========================================================================
add("largest-number", "Largest Number", "medium",
    ["array", "string", "greedy", "sorting"], "largestNumber",
    [("nums", "int[]")], "string",
    """
Given a list of non-negative integers `nums`, arrange them to form the **largest
number** and **return it as a string** (it may be very large). Watch the all-zeros
case (return `"0"`, not `"00"`).

**Examples**
```
nums = [10,2]          ->  "210"
nums = [3,30,34,5,9]   ->  "9534330"
```

**Constraints:** `1 <= len(nums) <= 100`, `0 <= nums[i] <= 10^9`.
""",
    """def largestNumber(nums):
    from functools import cmp_to_key
    arr = list(map(str, nums))
    arr.sort(key=cmp_to_key(lambda a, b: (a + b < b + a) - (a + b > b + a)))
    res = "".join(arr)
    return "0" if res[0] == '0' else res
""",
    visible=[{"nums": [10, 2]}, {"nums": [3, 30, 34, 5, 9]}],
    hidden=[{"nums": [0, 0]}, {"nums": [0]}, {"nums": [1]},
            {"nums": [121, 12]}, {"nums": [432, 43243]}, {"nums": [10, 0, 1]}],
    gen=lambda r: [{"nums": [r.randint(0, 50) for _ in range(r.randint(1, 5))]}
                   for _ in range(6)],
    brute=_largest_brute,
    checks=[({"nums": [10, 2]}, "210"), ({"nums": [3, 30, 34, 5, 9]}, "9534330"),
            ({"nums": [0, 0]}, "0")],
    source="new_p")


# ===========================================================================
# 18. Dota2 Senate
# ===========================================================================
add("dota2-senate", "Dota2 Senate", "medium",
    ["string", "greedy", "queue"], "predictPartyVictory",
    [("senate", "string")], "string",
    """
Senators are `'R'` (Radiant) or `'D'` (Dire), given in round order by the string
`senate`. Each active senator, in order, may ban one opposing senator (removing them
permanently) or, if only their own party remains active, declare victory. With
optimal play, **return `"Radiant"` or `"Dire"` for the winning party.**

**Examples**
```
senate = "RD"   ->  "Radiant"
senate = "RDD"  ->  "Dire"
```

**Constraints:** `1 <= len(senate) <= 10^4`, characters `'R'`/`'D'`.
""",
    """def predictPartyVictory(senate):
    from collections import deque
    n = len(senate)
    R = deque()
    D = deque()
    for i, c in enumerate(senate):
        (R if c == 'R' else D).append(i)
    while R and D:
        r = R.popleft()
        d = D.popleft()
        if r < d:
            R.append(r + n)
        else:
            D.append(d + n)
    return "Radiant" if R else "Dire"
""",
    visible=[{"senate": "RD"}, {"senate": "RDD"}],
    hidden=[{"senate": "R"}, {"senate": "D"}, {"senate": "RRD"},
            {"senate": "DDRRR"}, {"senate": "RDRDRD"}],
    gen=lambda r: [{"senate": "".join(r.choice("RD") for _ in range(r.randint(1, 10)))}
                   for _ in range(6)],
    checks=[({"senate": "RD"}, "Radiant"), ({"senate": "RDD"}, "Dire"),
            ({"senate": "R"}, "Radiant"), ({"senate": "RRD"}, "Radiant")],
    source="new_p")


# ===========================================================================
# 19. Minimum Cost to Merge Stones
# ===========================================================================
add("minimum-cost-to-merge-stones", "Minimum Cost to Merge Stones", "hard",
    ["array", "dynamic-programming", "prefix-sum"], "mergeStones",
    [("stones", "int[]"), ("K", "int")], "int",
    """
There are `N` piles in a row; pile `i` has `stones[i]` stones. A move merges exactly
`K` consecutive piles into one, costing the total number of stones merged. **Return
the minimum total cost to merge all piles into one**, or `-1` if impossible.

**Examples**
```
stones = [3,2,4,1], K = 2     ->  20
stones = [3,2,4,1], K = 3     ->  -1
stones = [3,5,1,2,6], K = 3   ->  25
```

**Constraints:** `1 <= len(stones) <= 30`, `2 <= K <= 30`, `1 <= stones[i] <= 100`.
""",
    """def mergeStones(stones, K):
    n = len(stones)
    if (n - 1) % (K - 1) != 0:
        return -1
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + stones[i]
    from functools import lru_cache
    INF = float('inf')

    @lru_cache(None)
    def dp(i, j):
        if i == j:
            return 0
        res = INF
        for m in range(i, j, K - 1):
            res = min(res, dp(i, m) + dp(m + 1, j))
        if (j - i) % (K - 1) == 0:
            res += prefix[j + 1] - prefix[i]
        return res

    return dp(0, n - 1)
""",
    visible=[{"stones": [3, 2, 4, 1], "K": 2}, {"stones": [3, 2, 4, 1], "K": 3},
             {"stones": [3, 5, 1, 2, 6], "K": 3}],
    hidden=[{"stones": [1], "K": 2}, {"stones": [1, 2], "K": 2},
            {"stones": [6, 4, 4, 6], "K": 2}, {"stones": [3, 5, 1, 2, 6], "K": 4}],
    gen=lambda r: [{"stones": [r.randint(1, 20) for _ in range(r.randint(1, 7))],
                    "K": r.randint(2, 4)} for _ in range(6)],
    checks=[({"stones": [3, 2, 4, 1], "K": 2}, 20),
            ({"stones": [3, 2, 4, 1], "K": 3}, -1),
            ({"stones": [3, 5, 1, 2, 6], "K": 3}, 25), ({"stones": [1], "K": 2}, 0)],
    source="new_p")


# ===========================================================================
# 20. Contains Duplicate III
# ===========================================================================
add("contains-duplicate-iii", "Contains Duplicate III", "hard",
    ["array", "sliding-window", "sorting", "bucket-sort"],
    "containsNearbyAlmostDuplicate",
    [("nums", "int[]"), ("k", "int"), ("t", "int")], "bool",
    """
**Return `true` if there exist two distinct indices `i` and `j`** with
`abs(nums[i] - nums[j]) <= t` and `abs(i - j) <= k`, else `false`.

**Examples**
```
nums = [1,2,3,1], k = 3, t = 0      ->  true
nums = [1,0,1,1], k = 1, t = 2      ->  true
nums = [1,5,9,1,5,9], k = 2, t = 3  ->  false
```

**Constraints:** `1 <= len(nums) <= 2*10^4`, `0 <= k <= 10^4`, `0 <= t <= 2^31 - 1`.
""",
    """def containsNearbyAlmostDuplicate(nums, k, t):
    if k <= 0 or t < 0:
        return False
    w = t + 1
    buckets = {}
    for i, x in enumerate(nums):
        b = x // w
        if b in buckets:
            return True
        if b - 1 in buckets and x - buckets[b - 1] <= t:
            return True
        if b + 1 in buckets and buckets[b + 1] - x <= t:
            return True
        buckets[b] = x
        if i >= k:
            del buckets[nums[i - k] // w]
    return False
""",
    visible=[{"nums": [1, 2, 3, 1], "k": 3, "t": 0},
             {"nums": [1, 0, 1, 1], "k": 1, "t": 2},
             {"nums": [1, 5, 9, 1, 5, 9], "k": 2, "t": 3}],
    hidden=[{"nums": [1], "k": 1, "t": 1}, {"nums": [-1, -1], "k": 1, "t": 0},
            {"nums": [7, 2, 8], "k": 2, "t": 1}, {"nums": [10, 100, 11, 9], "k": 3, "t": 2}],
    gen=lambda r: [{"nums": [r.randint(-15, 15) for _ in range(r.randint(1, 10))],
                    "k": r.randint(0, 5), "t": r.randint(0, 6)} for _ in range(6)],
    brute=_cd3_brute,
    checks=[({"nums": [1, 2, 3, 1], "k": 3, "t": 0}, True),
            ({"nums": [1, 0, 1, 1], "k": 1, "t": 2}, True),
            ({"nums": [1, 5, 9, 1, 5, 9], "k": 2, "t": 3}, False)],
    source="new_p")
