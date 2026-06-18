"""Batch 015 of the new_p.txt import (19 problems).

One entry was dropped as a duplicate under a different slug (see `_skips.py`):
`find-minimum-in-rotated-sorted-array` (== `find-minimum-rotated-sorted`).
"""
from scripts.build_bank import add, ilist, sstr  # noqa: F401

MOD = 10 ** 9 + 7


# --------------------------- brute / reference helpers ---------------------
def _numsub_brute(arr, k, threshold):
    return sum(1 for i in range(len(arr) - k + 1)
               if sum(arr[i:i + k]) >= k * threshold)


def _longsub_brute(nums):
    n = len(nums)
    best = 0
    for d in range(n):
        arr = nums[:d] + nums[d + 1:]
        cur = 0
        for x in arr:
            cur = cur + 1 if x == 1 else 0
            best = max(best, cur)
    return best


def _divk_brute(A, K):
    n = len(A)
    res = 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += A[j]
            if s % K == 0:
                res += 1
    return res


def _oranges_brute(n):
    from collections import deque
    if n == 0:
        return 0
    seen = {n}
    q = deque([(n, 0)])
    while q:
        v, d = q.popleft()
        if v == 0:
            return d
        nxts = [v - 1]
        if v % 2 == 0:
            nxts.append(v // 2)
        if v % 3 == 0:
            nxts.append(v // 3)
        for nv in nxts:
            if nv not in seen:
                seen.add(nv)
                q.append((nv, d + 1))
    return -1


def _decode_brute(S, K):
    tape = []
    for c in S:
        if c.isdigit():
            tape = tape * int(c)
        else:
            tape.append(c)
    return tape[K - 1]


def _latest_brute(arr, m):
    n = len(arr)
    bits = [0] * (n + 2)
    res = -1
    for step, pos in enumerate(arr, 1):
        bits[pos] = 1
        i, ok = 1, False
        while i <= n:
            if bits[i] == 1:
                j = i
                while j <= n and bits[j] == 1:
                    j += 1
                if j - i == m:
                    ok = True
                i = j
            else:
                i += 1
        if ok:
            res = step
    return res


def _turb_brute(A):
    n = len(A)
    best = 1
    for i in range(n):
        for j in range(i + 1, n):
            ok = True
            for k in range(i, j):
                d = A[k + 1] - A[k]
                if d == 0:
                    ok = False
                    break
                if k > i and (d > 0) == (A[k] - A[k - 1] > 0):
                    ok = False
                    break
            if ok:
                best = max(best, j - i + 1)
            else:
                break
    return best


def _mirror_brute(p, q):
    from math import gcd
    g = gcd(p, q)
    pp, qq = p // g, q // g
    right, top = pp % 2 == 1, qq % 2 == 1
    if right and top:
        return 1
    if right and not top:
        return 0
    return 2


def _consec_brute(N):
    # a = starting value of the consecutive run
    count = 0
    a = 1
    while a <= N:
        s, x = 0, a
        while s < N:
            s += x
            x += 1
        if s == N:
            count += 1
        a += 1
    return count


def _minswapgrid_brute(grid):
    from collections import deque
    n = len(grid)
    z = []
    for row in grid:
        c = 0
        for x in reversed(row):
            if x == 0:
                c += 1
            else:
                break
        z.append(c)

    def valid(order):
        return all(z[order[i]] >= n - 1 - i for i in range(n))

    start = tuple(range(n))
    if valid(start):
        return 0
    seen = {start}
    q = deque([(start, 0)])
    while q:
        order, d = q.popleft()
        for i in range(n - 1):
            no = list(order)
            no[i], no[i + 1] = no[i + 1], no[i]
            no = tuple(no)
            if no not in seen:
                if valid(no):
                    return d + 1
                seen.add(no)
                q.append((no, d + 1))
    return -1


def _teams_brute(rating):
    n = len(rating)
    res = 0
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if rating[i] < rating[j] < rating[k] or rating[i] > rating[j] > rating[k]:
                    res += 1
    return res


def _mindiff_brute(nums):
    from itertools import combinations
    n = len(nums)
    if n <= 1:
        return 0
    best = float('inf')
    for rem in range(0, 4):
        for comb in combinations(range(n), rem):
            cset = set(comb)
            remaining = [nums[i] for i in range(n) if i not in cset]
            if remaining:
                best = min(best, max(remaining) - min(remaining))
    return best


def _leastuniq_brute(arr, k):
    from collections import Counter
    counts = sorted(Counter(arr).values())
    removed, i = 0, 0
    while i < len(counts) and removed + counts[i] <= k:
        removed += counts[i]
        i += 1
    return len(counts) - i


def _removedup_brute(s):
    from itertools import permutations
    distinct = sorted(set(s))

    def is_subseq(t):
        it = iter(s)
        return all(ch in it for ch in t)

    for perm in permutations(distinct):
        if is_subseq(perm):
            return "".join(perm)
    return ""


def _conssum_brute(nums, k):
    n = len(nums)
    for i in range(n):
        s = nums[i]
        for j in range(i + 1, n):
            s += nums[j]
            if (k == 0 and s == 0) or (k != 0 and s % k == 0):
                return True
    return False


def _utf8_brute(data):
    bits = [format(num & 0xFF, '08b') for num in data]
    i, n = 0, len(bits)
    while i < n:
        b = bits[i]
        if b[0] == '0':
            i += 1
            continue
        if b[:3] == '110':
            cnt = 1
        elif b[:4] == '1110':
            cnt = 2
        elif b[:5] == '11110':
            cnt = 3
        else:
            return False
        for j in range(1, cnt + 1):
            if i + j >= n or bits[i + j][:2] != '10':
                return False
        i += cnt + 1
    return True


def _jobdiff_brute(jobDifficulty, d):
    from itertools import combinations
    n = len(jobDifficulty)
    if n < d:
        return -1
    best = float('inf')
    for cuts in combinations(range(1, n), d - 1):
        idx = [0] + list(cuts) + [n]
        total = sum(max(jobDifficulty[idx[g]:idx[g + 1]]) for g in range(d))
        best = min(best, total)
    return best


# --------------------------- gen helpers -----------------------------------
def _decode_gen(r):
    S = r.choice("abc")
    size = 1
    for _ in range(r.randint(1, 5)):
        if r.random() < 0.5:
            S += r.choice("abc")
            size += 1
        else:
            d = r.randint(2, 3)
            if size * d <= 2000:
                S += str(d)
                size *= d
            else:
                S += r.choice("abc")
                size += 1
    return {"S": S, "K": r.randint(1, size)}


def _latest_gen(r):
    n = r.randint(1, 10)
    arr = list(range(1, n + 1))
    r.shuffle(arr)
    return {"arr": arr, "m": r.randint(1, n)}


def _grid_gen(r):
    n = r.randint(1, 4)
    return {"grid": [[r.randint(0, 1) for _ in range(n)] for _ in range(n)]}


# ===========================================================================
# 1. Number of Sub-arrays of Size K and Average >= Threshold
# ===========================================================================
add("number-of-sub-arrays-of-size-k-and-average-greater-than-or-equal-to-threshold",
    "Number of Sub-arrays of Size K and Average At Least Threshold", "medium",
    ["array", "sliding-window"], "numOfSubarrays",
    [("arr", "int[]"), ("k", "int"), ("threshold", "int")], "int",
    """
**Return the number of contiguous subarrays of length exactly `k` whose average is
`>= threshold`.**

**Examples**
```
arr = [2,2,2,2,5,5,5,8], k = 3, threshold = 4              ->  3
arr = [1,1,1,1,1], k = 1, threshold = 0                    ->  5
arr = [11,13,17,23,29,31,7,5,2,3], k = 3, threshold = 5    ->  6
```

**Constraints:** `1 <= len(arr) <= 10^5`, `1 <= arr[i] <= 10^4`, `1 <= k <= len(arr)`,
`0 <= threshold <= 10^4`.
""",
    """def numOfSubarrays(arr, k, threshold):
    target = k * threshold
    s = sum(arr[:k])
    cnt = 1 if s >= target else 0
    for i in range(k, len(arr)):
        s += arr[i] - arr[i - k]
        if s >= target:
            cnt += 1
    return cnt
""",
    visible=[{"arr": [2, 2, 2, 2, 5, 5, 5, 8], "k": 3, "threshold": 4},
             {"arr": [1, 1, 1, 1, 1], "k": 1, "threshold": 0},
             {"arr": [11, 13, 17, 23, 29, 31, 7, 5, 2, 3], "k": 3, "threshold": 5}],
    hidden=[{"arr": [7, 7, 7, 7, 7, 7, 7], "k": 7, "threshold": 7},
            {"arr": [4, 4, 4, 4], "k": 4, "threshold": 1}, {"arr": [1], "k": 1, "threshold": 5},
            {"arr": [5, 1, 5, 1], "k": 2, "threshold": 3}],
    gen=lambda r: [(lambda a: {"arr": a, "k": r.randint(1, len(a)), "threshold": r.randint(0, 10)})
                   ([r.randint(1, 10) for _ in range(r.randint(1, 10))]) for _ in range(8)],
    brute=_numsub_brute,
    checks=[({"arr": [2, 2, 2, 2, 5, 5, 5, 8], "k": 3, "threshold": 4}, 3),
            ({"arr": [1, 1, 1, 1, 1], "k": 1, "threshold": 0}, 5),
            ({"arr": [11, 13, 17, 23, 29, 31, 7, 5, 2, 3], "k": 3, "threshold": 5}, 6),
            ({"arr": [7, 7, 7, 7, 7, 7, 7], "k": 7, "threshold": 7}, 1)],
    source="new_p")


# ===========================================================================
# 2. Longest Subarray of 1's After Deleting One Element
# ===========================================================================
add("longest-subarray-of-1s-after-deleting-one-element",
    "Longest Subarray of 1's After Deleting One Element", "medium",
    ["array", "sliding-window", "dynamic-programming"], "longestSubarray",
    [("nums", "int[]")], "int",
    """
Delete exactly one element from the binary array `nums`. **Return the length of the
longest run of `1`s in the resulting array** (return `0` if none).

**Examples**
```
nums = [1,1,0,1]              ->  3
nums = [0,1,1,1,0,1,1,0,1]    ->  5
nums = [1,1,1]                ->  2
```

**Constraints:** `1 <= len(nums) <= 10^5`, `nums[i]` is `0` or `1`.
""",
    """def longestSubarray(nums):
    left = 0
    zeros = 0
    best = 0
    for right in range(len(nums)):
        if nums[right] == 0:
            zeros += 1
        while zeros > 1:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left)
    return best
""",
    visible=[{"nums": [1, 1, 0, 1]}, {"nums": [0, 1, 1, 1, 0, 1, 1, 0, 1]}, {"nums": [1, 1, 1]}],
    hidden=[{"nums": [1, 1, 0, 0, 1, 1, 1, 0, 1]}, {"nums": [0, 0, 0]}, {"nums": [1]},
            {"nums": [0]}, {"nums": [1, 0, 1]}],
    gen=lambda r: [{"nums": [r.randint(0, 1) for _ in range(r.randint(1, 15))]}
                   for _ in range(8)],
    brute=_longsub_brute,
    checks=[({"nums": [1, 1, 0, 1]}, 3), ({"nums": [0, 1, 1, 1, 0, 1, 1, 0, 1]}, 5),
            ({"nums": [1, 1, 1]}, 2), ({"nums": [0, 0, 0]}, 0)],
    source="new_p")


# ===========================================================================
# 3. Subarray Sums Divisible by K
# ===========================================================================
add("subarray-sums-divisible-by-k", "Subarray Sums Divisible by K", "medium",
    ["array", "hash-table", "prefix-sum"], "subarraysDivByK",
    [("A", "int[]"), ("K", "int")], "int",
    """
**Return the number of contiguous non-empty subarrays of `A` whose sum is divisible by
`K`.**

**Example**
```
A = [4,5,0,-2,-3,1], K = 5  ->  7
```

**Constraints:** `1 <= len(A) <= 3*10^4`, `-10^4 <= A[i] <= 10^4`, `2 <= K <= 10^4`.
""",
    """def subarraysDivByK(A, K):
    from collections import defaultdict
    cnt = defaultdict(int)
    cnt[0] = 1
    pre = 0
    res = 0
    for x in A:
        pre = (pre + x) % K
        res += cnt[pre]
        cnt[pre] += 1
    return res
""",
    visible=[{"A": [4, 5, 0, -2, -3, 1], "K": 5}],
    hidden=[{"A": [5], "K": 5}, {"A": [1, 2, 3], "K": 3}, {"A": [-1, -2, -3], "K": 3},
            {"A": [0, 0, 0], "K": 2}, {"A": [2, 2, 2, 2], "K": 4}],
    gen=lambda r: [{"A": [r.randint(-10, 10) for _ in range(r.randint(1, 12))],
                    "K": r.randint(2, 6)} for _ in range(8)],
    brute=_divk_brute,
    checks=[({"A": [4, 5, 0, -2, -3, 1], "K": 5}, 7), ({"A": [5], "K": 5}, 1),
            ({"A": [1, 2, 3], "K": 3}, 3)],
    source="new_p")


# ===========================================================================
# 4. Minimum Number of Days to Eat N Oranges
# ===========================================================================
add("minimum-number-of-days-to-eat-n-oranges", "Minimum Number of Days to Eat N Oranges",
    "hard", ["dynamic-programming", "breadth-first-search", "memoization"], "minDays",
    [("n", "int")], "int",
    """
With `n` oranges, each day you may eat one orange, or (if divisible) eat `n/2`
oranges when `n` is even, or eat `2*(n/3)` oranges when `n` is divisible by `3`. One
action per day. **Return the minimum number of days to eat all `n` oranges.**

**Examples**
```
n = 10  ->  4
n = 6   ->  3
n = 56  ->  6
```

**Constraints:** `1 <= n <= 2*10^9`.
""",
    """def minDays(n):
    from functools import lru_cache

    @lru_cache(None)
    def f(x):
        if x <= 1:
            return x
        return 1 + min(x % 2 + f(x // 2), x % 3 + f(x // 3))

    return f(n)
""",
    visible=[{"n": 10}, {"n": 6}, {"n": 56}],
    hidden=[{"n": 1}, {"n": 2}, {"n": 3}, {"n": 100}, {"n": 7}],
    gen=lambda r: [{"n": r.randint(1, 200)} for _ in range(8)],
    brute=_oranges_brute,
    checks=[({"n": 10}, 4), ({"n": 6}, 3), ({"n": 1}, 1), ({"n": 56}, 6)],
    source="new_p")


# ===========================================================================
# 5. Decoded String at Index
# ===========================================================================
add("decoded-string-at-index", "Decoded String at Index", "medium",
    ["string", "stack"], "decodeAtIndex", [("S", "string"), ("K", "int")], "string",
    """
Read encoded string `S` left to right onto a tape: a letter is appended; a digit `d`
repeats the entire current tape `d` times. **Return the `K`-th letter (1-indexed) of
the decoded string.**

**Examples**
```
S = "leet2code3", K = 10  ->  "o"
S = "ha22", K = 5         ->  "h"
```

**Constraints:** `2 <= len(S) <= 100`, digits are `2..9`, `S` starts with a letter,
`1 <= K <=` decoded length (`< 2^63`).
""",
    """def decodeAtIndex(S, K):
    size = 0
    for c in S:
        if c.isdigit():
            size *= int(c)
        else:
            size += 1
    for c in reversed(S):
        K %= size
        if K == 0 and c.isalpha():
            return c
        if c.isdigit():
            size //= int(c)
        else:
            size -= 1
    return ""
""",
    visible=[{"S": "leet2code3", "K": 10}, {"S": "ha22", "K": 5}],
    hidden=[{"S": "a2", "K": 2}, {"S": "abc", "K": 3}, {"S": "x2y3", "K": 7},
            {"S": "leet2code3", "K": 1}, {"S": "a2b3", "K": 5}],
    gen=lambda r: [_decode_gen(r) for _ in range(8)],
    brute=_decode_brute,
    checks=[({"S": "leet2code3", "K": 10}, "o"), ({"S": "ha22", "K": 5}, "h"),
            ({"S": "a2345678999999999999999", "K": 1}, "a"), ({"S": "abc", "K": 3}, "c")],
    source="new_p")


# ===========================================================================
# 6. Find Latest Group of Size M
# ===========================================================================
add("find-latest-group-of-size-m", "Find Latest Group of Size M", "medium",
    ["array", "hash-table", "simulation"], "findLatestStep",
    [("arr", "int[]"), ("m", "int")], "int",
    """
`arr` is a permutation of `1..n`. Start with `n` zero bits; at step `i` set bit
`arr[i]` to `1`. A *group* is a maximal run of `1`s. **Return the latest step at which
some group has length exactly `m`, or `-1` if none ever does.**

**Examples**
```
arr = [3,5,1,2,4], m = 1  ->  4
arr = [3,1,5,4,2], m = 2  ->  -1
arr = [1], m = 1          ->  1
```

**Constraints:** `1 <= len(arr) == n <= 10^5`, `arr` permutes `1..n`, `1 <= m <= n`.
""",
    """def findLatestStep(arr, m):
    n = len(arr)
    length = [0] * (n + 2)
    count = [0] * (n + 1)
    res = -1
    for step, pos in enumerate(arr, 1):
        left = length[pos - 1]
        right = length[pos + 1]
        new_len = left + right + 1
        length[pos - left] = new_len
        length[pos + right] = new_len
        if left > 0:
            count[left] -= 1
        if right > 0:
            count[right] -= 1
        count[new_len] += 1
        if count[m] > 0:
            res = step
    return res
""",
    visible=[{"arr": [3, 5, 1, 2, 4], "m": 1}, {"arr": [3, 1, 5, 4, 2], "m": 2},
             {"arr": [1], "m": 1}],
    hidden=[{"arr": [2, 1], "m": 2}, {"arr": [2, 1], "m": 1}, {"arr": [1, 2, 3], "m": 3},
            {"arr": [1, 2, 3], "m": 1}, {"arr": [4, 3, 2, 1, 5], "m": 2}],
    gen=lambda r: [_latest_gen(r) for _ in range(8)],
    brute=_latest_brute,
    checks=[({"arr": [3, 5, 1, 2, 4], "m": 1}, 4), ({"arr": [3, 1, 5, 4, 2], "m": 2}, -1),
            ({"arr": [1], "m": 1}, 1), ({"arr": [2, 1], "m": 2}, 2)],
    source="new_p")


# ===========================================================================
# 7. Longest Turbulent Subarray
# ===========================================================================
add("longest-turbulent-subarray", "Longest Turbulent Subarray", "medium",
    ["array", "dynamic-programming", "sliding-window"], "maxTurbulenceSize",
    [("A", "int[]")], "int",
    """
A subarray is *turbulent* if the comparison sign strictly flips between each adjacent
pair (up, down, up, ... or down, up, down, ...). **Return the length of the longest
turbulent subarray of `A`.**

**Examples**
```
A = [9,4,2,10,7,8,8,1,9]  ->  5
A = [4,8,12,16]           ->  2
A = [100]                 ->  1
```

**Constraints:** `1 <= len(A) <= 4*10^4`, `0 <= A[i] <= 10^9`.
""",
    """def maxTurbulenceSize(A):
    n = len(A)
    best = 1
    up = down = 1
    for i in range(1, n):
        if A[i] > A[i - 1]:
            up, down = down + 1, 1
        elif A[i] < A[i - 1]:
            down, up = up + 1, 1
        else:
            up = down = 1
        best = max(best, up, down)
    return best
""",
    visible=[{"A": [9, 4, 2, 10, 7, 8, 8, 1, 9]}, {"A": [4, 8, 12, 16]}, {"A": [100]}],
    hidden=[{"A": [9, 9]}, {"A": [1, 2]}, {"A": [2, 1]}, {"A": [0, 1, 0, 1, 0]},
            {"A": [3, 3, 3, 3]}],
    gen=lambda r: [{"A": [r.randint(0, 5) for _ in range(r.randint(1, 12))]}
                   for _ in range(8)],
    brute=_turb_brute,
    checks=[({"A": [9, 4, 2, 10, 7, 8, 8, 1, 9]}, 5), ({"A": [4, 8, 12, 16]}, 2),
            ({"A": [100]}, 1), ({"A": [0, 1, 0, 1, 0]}, 5)],
    source="new_p")


# ===========================================================================
# 8. Mirror Reflection
# ===========================================================================
add("mirror-reflection", "Mirror Reflection", "medium",
    ["math", "geometry", "number-theory"], "mirrorReflection",
    [("p", "int"), ("q", "int")], "int",
    """
A square room of side `p` has mirrored walls and receptors `0`, `1`, `2` at three
corners (the southwest corner, the laser's origin, has none). The laser leaves the
southwest corner and first meets the east wall at height `q`. **Return the index of the
first receptor the ray reaches.**

**Example**
```
p = 2, q = 1  ->  2
```

**Constraints:** `1 <= p <= 1000`, `0 <= q <= p`.
""",
    """def mirrorReflection(p, q):
    from math import gcd
    g = gcd(p, q)
    p //= g
    q //= g
    if p % 2 == 0:
        return 2
    if q % 2 == 0:
        return 0
    return 1
""",
    visible=[{"p": 2, "q": 1}],
    hidden=[{"p": 3, "q": 1}, {"p": 1, "q": 1}, {"p": 4, "q": 3}, {"p": 3, "q": 2},
            {"p": 2, "q": 0}],
    gen=lambda r: [(lambda p: {"p": p, "q": r.randint(0, p)})(r.randint(1, 20))
                   for _ in range(8)],
    brute=_mirror_brute,
    checks=[({"p": 2, "q": 1}, 2), ({"p": 3, "q": 1}, 1), ({"p": 1, "q": 1}, 1),
            ({"p": 4, "q": 3}, 2), ({"p": 3, "q": 2}, 0), ({"p": 2, "q": 0}, 0)],
    source="new_p")


# ===========================================================================
# 9. Consecutive Numbers Sum
# ===========================================================================
add("consecutive-numbers-sum", "Consecutive Numbers Sum", "hard",
    ["math"], "consecutiveNumbersSum", [("N", "int")], "int",
    """
**Return the number of ways to write `N` as a sum of one or more consecutive positive
integers.**

**Examples**
```
N = 5   ->  2    (5; 2+3)
N = 9   ->  3    (9; 4+5; 2+3+4)
N = 15  ->  4
```

**Constraints:** `1 <= N <= 10^9`.
""",
    """def consecutiveNumbersSum(N):
    count = 0
    k = 1
    while k * (k + 1) // 2 <= N:
        if (N - k * (k + 1) // 2) % k == 0:
            count += 1
        k += 1
    return count
""",
    visible=[{"N": 5}, {"N": 9}, {"N": 15}],
    hidden=[{"N": 1}, {"N": 2}, {"N": 3}, {"N": 100}, {"N": 6}],
    gen=lambda r: [{"N": r.randint(1, 500)} for _ in range(8)],
    brute=_consec_brute,
    checks=[({"N": 5}, 2), ({"N": 9}, 3), ({"N": 15}, 4), ({"N": 1}, 1)],
    source="new_p")


# ===========================================================================
# 10. Minimum Swaps to Arrange a Binary Grid
# ===========================================================================
add("minimum-swaps-to-arrange-a-binary-grid", "Minimum Swaps to Arrange a Binary Grid",
    "medium", ["array", "greedy", "matrix"], "minSwaps", [("grid", "int[][]")], "int",
    """
You may swap two **adjacent rows** of an `n x n` binary grid in one step. The grid is
*valid* when every cell above the main diagonal is `0`. **Return the minimum number of
swaps to make it valid, or `-1` if impossible.**

**Examples**
```
grid = [[0,0,1],[1,1,0],[1,0,0]]  ->  3
grid = [[0,1,1,0],[0,1,1,0],[0,1,1,0],[0,1,1,0]]  ->  -1
grid = [[1,0,0],[1,1,0],[1,1,1]]  ->  0
```

**Constraints:** `1 <= n <= 200`, `grid[i][j]` is `0` or `1`.
""",
    """def minSwaps(grid):
    n = len(grid)
    zeros = []
    for row in grid:
        c = 0
        for x in reversed(row):
            if x == 0:
                c += 1
            else:
                break
        zeros.append(c)
    res = 0
    for i in range(n):
        need = n - 1 - i
        j = i
        while j < n and zeros[j] < need:
            j += 1
        if j == n:
            return -1
        while j > i:
            zeros[j], zeros[j - 1] = zeros[j - 1], zeros[j]
            res += 1
            j -= 1
    return res
""",
    visible=[{"grid": [[0, 0, 1], [1, 1, 0], [1, 0, 0]]},
             {"grid": [[0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 0]]},
             {"grid": [[1, 0, 0], [1, 1, 0], [1, 1, 1]]}],
    hidden=[{"grid": [[1]]}, {"grid": [[0]]}, {"grid": [[1, 1], [1, 0]]},
            {"grid": [[0, 0], [0, 0]]}, {"grid": [[1, 0, 1], [0, 1, 0], [1, 0, 0]]}],
    gen=lambda r: [_grid_gen(r) for _ in range(8)],
    brute=_minswapgrid_brute,
    checks=[({"grid": [[0, 0, 1], [1, 1, 0], [1, 0, 0]]}, 3),
            ({"grid": [[0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 1, 1, 0]]}, -1),
            ({"grid": [[1, 0, 0], [1, 1, 0], [1, 1, 1]]}, 0)],
    source="new_p")


# ===========================================================================
# 11. Count Number of Teams
# ===========================================================================
add("count-number-of-teams", "Count Number of Teams", "medium",
    ["array", "dynamic-programming", "binary-indexed-tree"], "numTeams",
    [("rating", "int[]")], "int",
    """
From `n` soldiers with distinct ratings, count triples of indices `i < j < k` whose
ratings are strictly increasing or strictly decreasing. **Return the number of such
teams.**

**Examples**
```
rating = [2,5,3,4,1]  ->  3
rating = [2,1,3]      ->  0
rating = [1,2,3,4]    ->  4
```

**Constraints:** `1 <= n <= 1000`, distinct `1 <= rating[i] <= 10^5`.
""",
    """def numTeams(rating):
    n = len(rating)
    res = 0
    for j in range(n):
        less_left = sum(1 for i in range(j) if rating[i] < rating[j])
        great_left = j - less_left
        less_right = sum(1 for k in range(j + 1, n) if rating[k] < rating[j])
        great_right = (n - 1 - j) - less_right
        res += less_left * great_right + great_left * less_right
    return res
""",
    visible=[{"rating": [2, 5, 3, 4, 1]}, {"rating": [2, 1, 3]}, {"rating": [1, 2, 3, 4]}],
    hidden=[{"rating": [1]}, {"rating": [5, 4, 3, 2, 1]}, {"rating": [1, 2]},
            {"rating": [3, 1, 2]}, {"rating": [10, 20, 5, 15, 25]}],
    gen=lambda r: [{"rating": r.sample(range(1, 50), r.randint(1, 10))} for _ in range(8)],
    brute=_teams_brute,
    checks=[({"rating": [2, 5, 3, 4, 1]}, 3), ({"rating": [2, 1, 3]}, 0),
            ({"rating": [1, 2, 3, 4]}, 4), ({"rating": [5, 4, 3, 2, 1]}, 10)],
    source="new_p")


# ===========================================================================
# 12. Airplane Seat Assignment Probability
# ===========================================================================
add("airplane-seat-assignment-probability", "Airplane Seat Assignment Probability",
    "medium", ["math", "dynamic-programming", "probability"], "nthPersonGetsNthSeat",
    [("n", "int")], "float",
    """
`n` passengers board a plane with `n` assigned seats. The first passenger lost their
ticket and sits randomly; each later passenger takes their own seat if free, else a
random free seat. **Return the probability that the `n`-th passenger gets their own
seat.**

**Examples**
```
n = 1  ->  1.0
n = 2  ->  0.5
```

**Constraints:** `1 <= n <= 10^5`.
""",
    """def nthPersonGetsNthSeat(n):
    return 1.0 if n == 1 else 0.5
""",
    visible=[{"n": 1}, {"n": 2}],
    hidden=[{"n": 3}, {"n": 5}, {"n": 100}, {"n": 10}],
    gen=lambda r: [{"n": r.randint(1, 50)} for _ in range(6)],
    checks=[({"n": 1}, 1.0), ({"n": 2}, 0.5), ({"n": 3}, 0.5), ({"n": 100}, 0.5)],
    source="new_p")


# ===========================================================================
# 13. Minimum Difference Between Largest and Smallest Value in Three Moves
# ===========================================================================
add("minimum-difference-between-largest-and-smallest-value-in-three-moves",
    "Minimum Difference Between Largest and Smallest Value in Three Moves", "medium",
    ["array", "greedy", "sorting"], "minDifference", [("nums", "int[]")], "int",
    """
In one move you may change any single element of `nums` to any value. Using **at most
3 moves**, **return the minimum possible difference between the largest and smallest
element.**

**Examples**
```
nums = [5,3,2,4]       ->  0
nums = [1,5,0,10,14]   ->  1
nums = [6,6,0,1,1,4,6] ->  2
```

**Constraints:** `1 <= len(nums) <= 10^5`, `-10^9 <= nums[i] <= 10^9`.
""",
    """def minDifference(nums):
    n = len(nums)
    if n <= 4:
        return 0
    nums.sort()
    return min(nums[n - 4 + i] - nums[i] for i in range(4))
""",
    visible=[{"nums": [5, 3, 2, 4]}, {"nums": [1, 5, 0, 10, 14]}, {"nums": [6, 6, 0, 1, 1, 4, 6]}],
    hidden=[{"nums": [1, 5, 6, 14, 15]}, {"nums": [1]}, {"nums": [1, 2, 3, 4, 5]},
            {"nums": [4, 4, 4, 4, 4, 4]}, {"nums": [-1, -5, -10, 5, 10, 20]}],
    gen=lambda r: [{"nums": [r.randint(-20, 20) for _ in range(r.randint(1, 8))]}
                   for _ in range(8)],
    brute=_mindiff_brute,
    checks=[({"nums": [5, 3, 2, 4]}, 0), ({"nums": [1, 5, 0, 10, 14]}, 1),
            ({"nums": [6, 6, 0, 1, 1, 4, 6]}, 2), ({"nums": [1, 5, 6, 14, 15]}, 1)],
    source="new_p")


# ===========================================================================
# 14. Least Number of Unique Integers After K Removals
# ===========================================================================
add("least-number-of-unique-integers-after-k-removals",
    "Least Number of Unique Integers After K Removals", "medium",
    ["array", "hash-table", "greedy", "sorting", "counting"], "findLeastNumOfUniqueInts",
    [("arr", "int[]"), ("k", "int")], "int",
    """
**Return the least number of distinct integers remaining after removing exactly `k`
elements from `arr`.**

**Examples**
```
arr = [5,5,4], k = 1            ->  1
arr = [4,3,1,1,3,3,2], k = 3    ->  2
```

**Constraints:** `1 <= len(arr) <= 10^5`, `0 <= k <= len(arr)`.
""",
    """def findLeastNumOfUniqueInts(arr, k):
    from collections import Counter
    counts = sorted(Counter(arr).values())
    for i, c in enumerate(counts):
        if k >= c:
            k -= c
        else:
            return len(counts) - i
    return 0
""",
    visible=[{"arr": [5, 5, 4], "k": 1}, {"arr": [4, 3, 1, 1, 3, 3, 2], "k": 3}],
    hidden=[{"arr": [1], "k": 0}, {"arr": [1], "k": 1}, {"arr": [1, 2, 3], "k": 3},
            {"arr": [2, 1, 1, 3, 3, 3], "k": 3}, {"arr": [5, 5, 5, 5], "k": 2}],
    gen=lambda r: [(lambda a: {"arr": a, "k": r.randint(0, len(a))})
                   ([r.randint(1, 6) for _ in range(r.randint(1, 12))]) for _ in range(8)],
    brute=_leastuniq_brute,
    checks=[({"arr": [5, 5, 4], "k": 1}, 1), ({"arr": [4, 3, 1, 1, 3, 3, 2], "k": 3}, 2),
            ({"arr": [1], "k": 0}, 1), ({"arr": [1, 2, 3], "k": 3}, 0)],
    source="new_p")


# ===========================================================================
# 15. Remove Duplicate Letters
# ===========================================================================
add("remove-duplicate-letters", "Remove Duplicate Letters", "medium",
    ["string", "stack", "greedy", "monotonic-stack"], "removeDuplicateLetters",
    [("s", "string")], "string",
    """
**Remove duplicate letters so that every letter appears exactly once, and the result
is the lexicographically smallest such string.** Return that string.

**Examples**
```
s = "bcabc"     ->  "abc"
s = "cbacdcbc"  ->  "acdb"
```

**Constraints:** `1 <= len(s) <= 10^4`, lowercase letters.
""",
    """def removeDuplicateLetters(s):
    from collections import Counter
    remaining = Counter(s)
    stack = []
    seen = set()
    for c in s:
        remaining[c] -= 1
        if c in seen:
            continue
        while stack and stack[-1] > c and remaining[stack[-1]] > 0:
            seen.discard(stack.pop())
        stack.append(c)
        seen.add(c)
    return "".join(stack)
""",
    visible=[{"s": "bcabc"}, {"s": "cbacdcbc"}],
    hidden=[{"s": "a"}, {"s": "aaa"}, {"s": "abacb"}, {"s": "bbcaac"}, {"s": "edcba"}],
    gen=lambda r: [{"s": sstr(r, 1, 10, "abcd")} for _ in range(8)],
    brute=_removedup_brute,
    checks=[({"s": "bcabc"}, "abc"), ({"s": "cbacdcbc"}, "acdb"), ({"s": "a"}, "a"),
            ({"s": "aaa"}, "a")],
    source="new_p")


# ===========================================================================
# 16. Continuous Subarray Sum
# ===========================================================================
add("continuous-subarray-sum", "Continuous Subarray Sum", "medium",
    ["array", "hash-table", "math", "prefix-sum"], "checkSubarraySum",
    [("nums", "int[]"), ("k", "int")], "bool",
    """
**Return `true` if `nums` has a contiguous subarray of length at least `2` whose sum
is a multiple of `k`** (including `0`).

**Examples**
```
nums = [23,2,4,6,7], k = 6  ->  true   ([2,4] sums to 6)
nums = [23,2,6,4,7], k = 6  ->  true
```

**Constraints:** `1 <= len(nums) <= 10^4`, `0 <= nums[i]`, `0 <= k`.
""",
    """def checkSubarraySum(nums, k):
    seen = {0: -1}
    pre = 0
    for i, x in enumerate(nums):
        pre += x
        r = pre % k if k != 0 else pre
        if r in seen:
            if i - seen[r] >= 2:
                return True
        else:
            seen[r] = i
    return False
""",
    visible=[{"nums": [23, 2, 4, 6, 7], "k": 6}, {"nums": [23, 2, 6, 4, 7], "k": 6}],
    hidden=[{"nums": [1, 2, 3], "k": 5}, {"nums": [1, 2, 3], "k": 7},
            {"nums": [0, 0], "k": 0}, {"nums": [1, 0], "k": 2}, {"nums": [5, 0, 0], "k": 3}],
    gen=lambda r: [{"nums": [r.randint(0, 10) for _ in range(r.randint(1, 10))],
                    "k": r.randint(0, 6)} for _ in range(8)],
    brute=_conssum_brute,
    checks=[({"nums": [23, 2, 4, 6, 7], "k": 6}, True), ({"nums": [23, 2, 6, 4, 7], "k": 6}, True),
            ({"nums": [1, 2, 3], "k": 5}, True), ({"nums": [1, 2, 3], "k": 7}, False),
            ({"nums": [0, 0], "k": 0}, True)],
    source="new_p")


# ===========================================================================
# 17. UTF-8 Validation
# ===========================================================================
add("utf-8-validation", "UTF-8 Validation", "medium",
    ["array", "bit-manipulation"], "validUtf8", [("data", "int[]")], "bool",
    """
Each integer in `data` contributes its low 8 bits as one byte. **Return `true` if the
bytes form a valid UTF-8 encoding**, where a character is 1-4 bytes: a 1-byte char is
`0xxxxxxx`; an `n`-byte char (n>1) starts with `n` ones then a `0`, followed by `n-1`
continuation bytes `10xxxxxx`.

**Examples**
```
data = [197,130,1]  ->  true
data = [235,140,4]  ->  false
```

**Constraints:** `1 <= len(data) <= 2*10^4`, `0 <= data[i] <= 255` (low 8 bits used).
""",
    """def validUtf8(data):
    n_bytes = 0
    for num in data:
        b = num & 0xFF
        if n_bytes == 0:
            if b >> 7 == 0:
                n_bytes = 0
            elif b >> 5 == 0b110:
                n_bytes = 1
            elif b >> 4 == 0b1110:
                n_bytes = 2
            elif b >> 3 == 0b11110:
                n_bytes = 3
            else:
                return False
        else:
            if b >> 6 != 0b10:
                return False
            n_bytes -= 1
    return n_bytes == 0
""",
    visible=[{"data": [197, 130, 1]}, {"data": [235, 140, 4]}],
    hidden=[{"data": [240, 162, 138, 147]}, {"data": [255]}, {"data": [0]},
            {"data": [197, 130]}, {"data": [145]}],
    gen=lambda r: [{"data": [r.randint(0, 255) for _ in range(r.randint(1, 6))]}
                   for _ in range(8)],
    brute=_utf8_brute,
    checks=[({"data": [197, 130, 1]}, True), ({"data": [235, 140, 4]}, False),
            ({"data": [240, 162, 138, 147]}, True), ({"data": [255]}, False),
            ({"data": [0]}, True)],
    source="new_p")


# ===========================================================================
# 18. Equal Rational Numbers
# ===========================================================================
add("equal-rational-numbers", "Equal Rational Numbers", "hard",
    ["math", "string"], "isRationalEqual", [("S", "string"), ("T", "string")], "bool",
    """
`S` and `T` are non-negative rationals written as `<int>`, `<int>.<frac>`, or
`<int>.<frac>(<repeat>)`, where `(<repeat>)` is the repeating part of the decimal
expansion. **Return `true` if they represent the same number.**

**Examples**
```
S = "0.(52)", T = "0.5(25)"      ->  true
S = "0.1666(6)", T = "0.166(66)" ->  true
S = "0.9(9)", T = "1."           ->  true
```

**Constraints:** parts are digit strings; `IntegerPart` length `1..4`, `NonRepeating`
`0..4`, `Repeating` `1..4`.
""",
    """def isRationalEqual(S, T):
    from fractions import Fraction

    def parse(s):
        rep = ''
        if '(' in s:
            base, rep = s.split('(')
            rep = rep[:-1]
        else:
            base = s
        if '.' in base:
            intpart, frac = base.split('.')
        else:
            intpart, frac = base, ''
        intpart = intpart or '0'
        val = Fraction(int(intpart))
        if frac:
            val += Fraction(int(frac), 10 ** len(frac))
        if rep:
            denom = (10 ** len(rep) - 1) * (10 ** len(frac))
            val += Fraction(int(rep), denom)
        return val

    return parse(S) == parse(T)
""",
    visible=[{"S": "0.(52)", "T": "0.5(25)"}, {"S": "0.1666(6)", "T": "0.166(66)"},
             {"S": "0.9(9)", "T": "1."}],
    hidden=[{"S": "1", "T": "1"}, {"S": "0.5", "T": "0.5000"}, {"S": "0.(9)", "T": "1"},
            {"S": "0.5", "T": "0.6"}, {"S": "1.0", "T": "1"}, {"S": "0.00(1212)", "T": "0.(0012)"}],
    checks=[({"S": "0.(52)", "T": "0.5(25)"}, True),
            ({"S": "0.1666(6)", "T": "0.166(66)"}, True),
            ({"S": "0.9(9)", "T": "1."}, True), ({"S": "0.5", "T": "0.6"}, False),
            ({"S": "1", "T": "1"}, True)],
    source="new_p")


# ===========================================================================
# 19. Minimum Difficulty of a Job Schedule
# ===========================================================================
add("minimum-difficulty-of-a-job-schedule", "Minimum Difficulty of a Job Schedule",
    "hard", ["array", "dynamic-programming"], "minDifficulty",
    [("jobDifficulty", "int[]"), ("d", "int")], "int",
    """
Schedule jobs (which must be done in order) over `d` days, at least one job per day.
A day's difficulty is the maximum difficulty among its jobs; the schedule's difficulty
is the sum over days. **Return the minimum possible schedule difficulty, or `-1` if it
is impossible.**

**Examples**
```
jobDifficulty = [6,5,4,3,2,1], d = 2  ->  7
jobDifficulty = [9,9,9], d = 4        ->  -1
jobDifficulty = [1,1,1], d = 3        ->  3
```

**Constraints:** `1 <= len(jobDifficulty) <= 300`, `0 <= jobDifficulty[i] <= 1000`,
`1 <= d <= 10`.
""",
    """def minDifficulty(jobDifficulty, d):
    n = len(jobDifficulty)
    if n < d:
        return -1
    from functools import lru_cache
    INF = float('inf')

    @lru_cache(None)
    def dp(i, days):
        if days == 1:
            return max(jobDifficulty[i:])
        best, mx = INF, 0
        for j in range(i, n - days + 1):
            mx = max(mx, jobDifficulty[j])
            best = min(best, mx + dp(j + 1, days - 1))
        return best

    return dp(0, d)
""",
    visible=[{"jobDifficulty": [6, 5, 4, 3, 2, 1], "d": 2}, {"jobDifficulty": [9, 9, 9], "d": 4},
             {"jobDifficulty": [1, 1, 1], "d": 3}],
    hidden=[{"jobDifficulty": [7, 1, 7, 1, 7, 1], "d": 3},
            {"jobDifficulty": [11, 111, 22, 222, 33, 333, 44, 444], "d": 6},
            {"jobDifficulty": [5], "d": 1}, {"jobDifficulty": [1, 2], "d": 3},
            {"jobDifficulty": [4, 3, 2, 1], "d": 2}],
    gen=lambda r: [(lambda a: {"jobDifficulty": a, "d": r.randint(1, len(a))})
                   ([r.randint(0, 20) for _ in range(r.randint(1, 8))]) for _ in range(8)],
    brute=_jobdiff_brute,
    checks=[({"jobDifficulty": [6, 5, 4, 3, 2, 1], "d": 2}, 7),
            ({"jobDifficulty": [9, 9, 9], "d": 4}, -1), ({"jobDifficulty": [1, 1, 1], "d": 3}, 3),
            ({"jobDifficulty": [7, 1, 7, 1, 7, 1], "d": 3}, 15),
            ({"jobDifficulty": [11, 111, 22, 222, 33, 333, 44, 444], "d": 6}, 843)],
    source="new_p")
