"""Batch 017 of the new_p.txt import (20 problems).

Three entries from this group were dropped to `_skips.py` before authoring:
  - `minimum-cost-tree-from-leaf-values` (== `min-cost-tree-leaf-values`)
  - `maximum-profit-in-job-scheduling`   (== `maximum-profit-job-scheduling`)
  - `string-without-aaa-or-bbb`          (return-any string; longest length is trivially A+B)

`longest-happy-string` is reframed to return the LENGTH of the longest happy
string (the "return any happy string" form is not single-answer gradable; its
length is a real, unique computation).
"""
from scripts.build_bank import add  # noqa: F401


# --------------------------- brute / reference helpers ---------------------
def _kthbit_brute(n, k):
    s = "0"
    for _ in range(n - 1):
        s = s + "1" + "".join('1' if c == '0' else '0' for c in reversed(s))
    return s[k - 1]


def _kthbit_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(1, 11)
        k = r.randint(1, (1 << n) - 1)
        out.append({"n": n, "k": k})
    return out


def _single2_brute(nums):
    from collections import Counter
    for k, v in Counter(nums).items():
        if v == 1:
            return k


def _single2_gen(r):
    out = []
    for _ in range(8):
        base = r.sample(range(-20, 20), r.randint(1, 5))
        arr = []
        for b in base:
            arr += [b, b, b]
        single = r.randint(-20, 20)
        while single in base:
            single = r.randint(-20, 20)
        arr.append(single)
        r.shuffle(arr)
        out.append({"nums": arr})
    return out


def _brick_brute(wall):
    offsets = set()
    for row in wall:
        p = 0
        for b in row[:-1]:
            p += b
            offsets.add(p)
    if not offsets:
        return len(wall)
    best = len(wall)
    for off in offsets:
        cross = 0
        for row in wall:
            p = 0
            edge = False
            for b in row:
                p += b
                if p == off:
                    edge = True
                    break
                if p > off:
                    break
            if not edge:
                cross += 1
        best = min(best, cross)
    return best


def _brick_gen(r):
    out = []
    for _ in range(6):
        total = r.randint(1, 8)
        rows = r.randint(1, 4)
        wall = []
        for _ in range(rows):
            cuts = sorted(r.sample(range(1, total), r.randint(0, total - 1))) if total > 1 else []
            prev = 0
            row = []
            for c in cuts:
                row.append(c - prev)
                prev = c
            row.append(total - prev)
            wall.append(row)
        out.append({"wall": wall})
    return out


def _numways_brute(steps, arrLen):
    from functools import lru_cache
    MOD = 10 ** 9 + 7

    @lru_cache(None)
    def f(pos, s):
        if pos < 0 or pos >= arrLen:
            return 0
        if s == 0:
            return 1 if pos == 0 else 0
        return f(pos, s - 1) + f(pos - 1, s - 1) + f(pos + 1, s - 1)

    return f(0, steps) % MOD


def _numways_gen(r):
    return [{"steps": r.randint(1, 30), "arrLen": r.randint(1, 30)} for _ in range(8)]


def _3sumclosest_brute(nums, target):
    from itertools import combinations
    best = None
    for a, b, c in combinations(nums, 3):
        s = a + b + c
        if best is None or abs(s - target) < abs(best - target) or \
                (abs(s - target) == abs(best - target) and s < best):
            best = s
    return best


def _3sumclosest_gen(r):
    return [{"nums": [r.randint(-10, 10) for _ in range(r.randint(3, 8))],
             "target": r.randint(-15, 15)} for _ in range(8)]


def _primepal_brute(N):
    def is_prime(x):
        if x < 2:
            return False
        i = 2
        while i * i <= x:
            if x % i == 0:
                return False
            i += 1
        return True

    x = N
    while True:
        if str(x) == str(x)[::-1] and is_prime(x):
            return x
        x += 1


def _primepal_gen(r):
    return [{"N": r.randint(1, 200)} for _ in range(8)]


def _kflip_brute(A, K):
    A = A[:]
    n = len(A)
    res = 0
    for i in range(n):
        if A[i] == 0:
            if i + K > n:
                return -1
            for j in range(i, i + K):
                A[j] ^= 1
            res += 1
    return res


def _kflip_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(1, 15)
        A = [r.randint(0, 1) for _ in range(n)]
        K = r.randint(1, n)
        out.append({"A": A, "K": K})
    return out


def _querystr_brute(S, N):
    return all(bin(i)[2:] in S for i in range(1, N + 1))


def _querystr_gen(r):
    return [{"S": "".join(r.choice("01") for _ in range(r.randint(1, 12))),
             "N": r.randint(1, 20)} for _ in range(8)]


def _happy_brute(a, b, c):
    from functools import lru_cache

    @lru_cache(None)
    def dfs(ca, cb, cc, last, run):
        best = 0
        for ch, cnt in (('a', ca), ('b', cb), ('c', cc)):
            if cnt == 0:
                continue
            if ch == last and run == 2:
                continue
            nrun = run + 1 if ch == last else 1
            if ch == 'a':
                nxt = dfs(ca - 1, cb, cc, 'a', nrun)
            elif ch == 'b':
                nxt = dfs(ca, cb - 1, cc, 'b', nrun)
            else:
                nxt = dfs(ca, cb, cc - 1, 'c', nrun)
            best = max(best, 1 + nxt)
        return best

    return dfs(a, b, c, '', 0)


def _happy_gen(r):
    out = []
    for _ in range(8):
        a, b, c = r.randint(0, 5), r.randint(0, 5), r.randint(0, 5)
        if a + b + c == 0:
            a = 1
        out.append({"a": a, "b": b, "c": c})
    return out


def _kthsmallest_brute(matrix, k):
    return sorted(v for row in matrix for v in row)[k - 1]


def _kthsmallest_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(1, 4)
        vals = sorted(r.randint(-20, 40) for _ in range(n * n))
        matrix = [vals[i * n:(i + 1) * n] for i in range(n)]
        k = r.randint(1, n * n)
        out.append({"matrix": matrix, "k": k})
    return out


def _ramp_brute(A):
    best = 0
    n = len(A)
    for i in range(n):
        for j in range(i + 1, n):
            if A[i] <= A[j]:
                best = max(best, j - i)
    return best


def _ramp_gen(r):
    return [{"A": [r.randint(0, 20) for _ in range(r.randint(2, 12))]} for _ in range(8)]


def _keys_brute(rooms):
    n = len(rooms)
    can = [False] * n
    can[0] = True
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if can[i]:
                for k in rooms[i]:
                    if not can[k]:
                        can[k] = True
                        changed = True
    return all(can)


def _keys_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(1, 6)
        rooms = [[r.randint(0, n - 1) for _ in range(r.randint(0, 3))] for _ in range(n)]
        out.append({"rooms": rooms})
    return out


def _wrap_brute(p):
    def is_wrap(s):
        for i in range(1, len(s)):
            if (ord(s[i]) - ord(s[i - 1])) % 26 != 1:
                return False
        return True

    subs = set()
    n = len(p)
    for i in range(n):
        for j in range(i + 1, n + 1):
            s = p[i:j]
            if is_wrap(s):
                subs.add(s)
    return len(subs)


def _wrap_gen(r):
    return [{"p": "".join(r.choice("abcxyz") for _ in range(r.randint(1, 20)))}
            for _ in range(8)]


def _target_brute(nums, S):
    from itertools import product
    cnt = 0
    for signs in product((1, -1), repeat=len(nums)):
        if sum(s * x for s, x in zip(signs, nums)) == S:
            cnt += 1
    return cnt


def _target_gen(r):
    out = []
    for _ in range(8):
        nums = [r.randint(0, 5) for _ in range(r.randint(1, 10))]
        S = r.randint(-sum(nums), sum(nums)) if sum(nums) else 0
        out.append({"nums": nums, "S": S})
    return out


def _decomp_brute(text):
    from functools import lru_cache

    @lru_cache(None)
    def solve(s):
        m = len(s)
        if m == 0:
            return 0
        if m == 1:
            return 1
        best = 1
        for k in range(1, m // 2 + 1):
            if s[:k] == s[-k:]:
                best = max(best, 2 + solve(s[k:m - k]))
        return best

    return solve(text)


def _decomp_gen(r):
    return [{"text": "".join(r.choice("ab") for _ in range(r.randint(1, 14)))}
            for _ in range(8)]


def _stoneii_brute(stones):
    from itertools import product
    best = sum(stones)
    for signs in product((1, -1), repeat=len(stones)):
        best = min(best, abs(sum(s * x for s, x in zip(signs, stones))))
    return best


def _stoneii_gen(r):
    return [{"stones": [r.randint(1, 15) for _ in range(r.randint(1, 12))]} for _ in range(8)]


def _minunique_brute(A):
    if not A:
        return 0
    used = set()
    moves = 0
    for x in sorted(A):
        v = x
        while v in used:
            v += 1
        used.add(v)
        moves += v - x
    return moves


def _minunique_gen(r):
    return [{"A": [r.randint(0, 15) for _ in range(r.randint(0, 10))]} for _ in range(8)]


def _increments_brute(target):
    t = target[:]
    ops = 0
    while any(t):
        i = 0
        n = len(t)
        while i < n:
            if t[i] > 0:
                j = i
                while j < n and t[j] > 0:
                    t[j] -= 1
                    j += 1
                ops += 1
                i = j
            else:
                i += 1
    return ops


def _increments_gen(r):
    return [{"target": [r.randint(1, 6) for _ in range(r.randint(1, 8))]} for _ in range(8)]


def _shortpal_brute(s):
    n = len(s)
    for k in range(n, 0, -1):
        if s[:k] == s[:k][::-1]:
            return s[k:][::-1] + s
    return s


def _shortpal_gen(r):
    return [{"s": "".join(r.choice("ab") for _ in range(r.randint(0, 12)))} for _ in range(8)]


def _malware_brute(graph, initial):
    n = len(graph)

    def spread(seed):
        seen = set(seed)
        stack = list(seed)
        while stack:
            x = stack.pop()
            for y in range(n):
                if graph[x][y] == 1 and y not in seen:
                    seen.add(y)
                    stack.append(y)
        return len(seen)

    best_node = min(initial)
    best_M = None
    for node in sorted(initial):
        rest = [x for x in initial if x != node]
        M = spread(rest) if rest else 0
        if best_M is None or M < best_M:
            best_M = M
            best_node = node
    return best_node


def _malware_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(2, 6)
        g = [[0] * n for _ in range(n)]
        for i in range(n):
            g[i][i] = 1
        for i in range(n):
            for j in range(i + 1, n):
                if r.random() < 0.4:
                    g[i][j] = g[j][i] = 1
        k = r.randint(1, n)
        initial = sorted(r.sample(range(n), k))
        out.append({"graph": g, "initial": initial})
    return out


# ===========================================================================
# 1. Find Kth Bit in Nth Binary String
# ===========================================================================
add("find-kth-bit-in-nth-binary-string", "Find Kth Bit in Nth Binary String", "medium",
    ["string", "recursion", "simulation"], "findKthBit",
    [("n", "int"), ("k", "int")], "str",
    """
The binary string `Sn` is built recursively:

- `S1 = "0"`
- `Si = S(i-1) + "1" + reverse(invert(S(i-1)))` for `i > 1`

where `reverse(x)` reverses `x` and `invert(x)` flips every bit (`0<->1`). The first
few are `S1 = "0"`, `S2 = "011"`, `S3 = "0111001"`, `S4 = "011100110110001"`.

Return the `k`-th bit of `Sn` (1-indexed) as the string `"0"` or `"1"`. It is
guaranteed that `k` is valid for the given `n`.

**Examples**
```
n = 3, k = 1   ->  "0"
n = 4, k = 11  ->  "1"
n = 1, k = 1   ->  "0"
n = 2, k = 3   ->  "1"
```

**Constraints:** `1 <= n <= 20`, `1 <= k <= 2^n - 1`.
""",
    """def findKthBit(n, k):
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
""",
    visible=[{"n": 3, "k": 1}, {"n": 4, "k": 11}, {"n": 2, "k": 3}],
    hidden=[{"n": 1, "k": 1}, {"n": 5, "k": 16}, {"n": 8, "k": 200},
            {"n": 11, "k": 1024}, {"n": 11, "k": 2047}],
    gen=_kthbit_gen,
    brute=_kthbit_brute,
    checks=[({"n": 3, "k": 1}, "0"), ({"n": 4, "k": 11}, "1"), ({"n": 1, "k": 1}, "0"),
            ({"n": 2, "k": 3}, "1"), ({"n": 20, "k": 1}, "0"),
            ({"n": 20, "k": 524288}, "1"), ({"n": 20, "k": 1048575}, "1")],
    source="new_p")


# ===========================================================================
# 2. Single Number II
# ===========================================================================
add("single-number-ii", "Single Number II", "medium",
    ["array", "bit-manipulation", "math"], "singleNumber", [("nums", "int[]")], "int",
    """
Every element of `nums` appears **exactly three times** except for one element,
which appears **exactly once**. Return that single element. Aim for linear time
and constant extra space.

**Examples**
```
nums = [2,2,3,2]          ->  3
nums = [0,1,0,1,0,1,99]   ->  99
```

**Constraints:** `1 <= len(nums)`, every value but one occurs three times, values
may be negative.
""",
    """def singleNumber(nums):
    return (3 * sum(set(nums)) - sum(nums)) // 2
""",
    visible=[{"nums": [2, 2, 3, 2]}, {"nums": [0, 1, 0, 1, 0, 1, 99]}],
    hidden=[{"nums": [7]}, {"nums": [5, 5, 5, -2]}, {"nums": [-4, -4, -4, -7]},
            {"nums": [30000, 500, 100, 30000, 100, 30000, 100]}],
    gen=_single2_gen,
    brute=_single2_brute,
    checks=[({"nums": [2, 2, 3, 2]}, 3), ({"nums": [0, 1, 0, 1, 0, 1, 99]}, 99),
            ({"nums": [5, 5, 5, -2]}, -2), ({"nums": [7]}, 7)],
    source="new_p")


# ===========================================================================
# 3. Brick Wall
# ===========================================================================
add("brick-wall", "Brick Wall", "medium",
    ["array", "hash-table"], "leastBricks", [("wall", "int[][]")], "int",
    """
A brick wall has several rows; `wall[i]` lists the widths of the bricks in row `i`
from left to right. All rows have the **same total width**. Draw one vertical line
from top to bottom; a brick is *crossed* unless the line passes exactly along one
of its edges. The line may not run along the two outer edges of the wall.

Return the **least number of bricks** the line must cross.

**Example**
```
wall = [[1,2,2,1],
        [3,1,2],
        [1,3,2],
        [2,4],
        [3,1,2],
        [1,3,1,1]]   ->  2
```

**Constraints:** `1 <= len(wall) <= 10^4`, each row has `1..10^4` bricks, total
bricks `<= 2*10^4`, row widths are equal.
""",
    """def leastBricks(wall):
    from collections import defaultdict
    edges = defaultdict(int)
    for row in wall:
        pos = 0
        for b in row[:-1]:
            pos += b
            edges[pos] += 1
    return len(wall) - (max(edges.values()) if edges else 0)
""",
    visible=[{"wall": [[1, 2, 2, 1], [3, 1, 2], [1, 3, 2], [2, 4], [3, 1, 2], [1, 3, 1, 1]]}],
    hidden=[{"wall": [[1], [1], [1]]}, {"wall": [[1, 1], [2]]},
            {"wall": [[1, 1], [1, 1]]}, {"wall": [[2, 1, 1], [1, 1, 2], [1, 3]]}],
    gen=_brick_gen,
    brute=_brick_brute,
    checks=[({"wall": [[1, 2, 2, 1], [3, 1, 2], [1, 3, 2], [2, 4], [3, 1, 2], [1, 3, 1, 1]]}, 2),
            ({"wall": [[1], [1], [1]]}, 3), ({"wall": [[1, 1], [2]]}, 1),
            ({"wall": [[1, 1], [1, 1]]}, 0)],
    source="new_p")


# ===========================================================================
# 4. Number of Ways to Stay in the Same Place After Some Steps
# ===========================================================================
add("number-of-ways-to-stay-in-the-same-place-after-some-steps",
    "Number of Ways to Stay in the Same Place After Some Steps", "hard",
    ["dynamic-programming"], "numWays", [("steps", "int"), ("arrLen", "int")], "int",
    """
A pointer starts at index `0` of an array of length `arrLen`. At each step it may
move one position left, one position right, or stay — but it must never leave the
array. Return the number of ways the pointer is back at index `0` after exactly
`steps` steps, modulo `10^9 + 7`.

**Examples**
```
steps = 3, arrLen = 2   ->  4
steps = 2, arrLen = 4   ->  2
steps = 4, arrLen = 2   ->  8
```

**Constraints:** `1 <= steps <= 500`, `1 <= arrLen <= 10^6`.
""",
    """def numWays(steps, arrLen):
    MOD = 10 ** 9 + 7
    maxpos = min(steps // 2 + 1, arrLen)
    dp = [0] * maxpos
    dp[0] = 1
    for _ in range(steps):
        ndp = [0] * maxpos
        for i in range(maxpos):
            v = dp[i]
            if v:
                ndp[i] = (ndp[i] + v) % MOD
                if i > 0:
                    ndp[i - 1] = (ndp[i - 1] + v) % MOD
                if i + 1 < maxpos:
                    ndp[i + 1] = (ndp[i + 1] + v) % MOD
        dp = ndp
    return dp[0] % MOD
""",
    visible=[{"steps": 3, "arrLen": 2}, {"steps": 2, "arrLen": 4}, {"steps": 4, "arrLen": 2}],
    hidden=[{"steps": 1, "arrLen": 1}, {"steps": 4, "arrLen": 1}, {"steps": 10, "arrLen": 3},
            {"steps": 27, "arrLen": 7}, {"steps": 30, "arrLen": 1000000}],
    gen=_numways_gen,
    brute=_numways_brute,
    checks=[({"steps": 3, "arrLen": 2}, 4), ({"steps": 2, "arrLen": 4}, 2),
            ({"steps": 4, "arrLen": 2}, 8), ({"steps": 1, "arrLen": 1}, 1),
            ({"steps": 4, "arrLen": 1}, 1)],
    source="new_p")


# ===========================================================================
# 5. 3Sum Closest
# ===========================================================================
add("3sum-closest", "3Sum Closest", "medium",
    ["array", "two-pointers", "sorting"], "threeSumClosest",
    [("nums", "int[]"), ("target", "int")], "int",
    """
Given an array `nums` of `n` integers and an integer `target`, pick three numbers
whose sum is closest to `target`, and return **that sum**. If two sums are equally
close, return the smaller sum.

**Example**
```
nums = [-1, 2, 1, -4], target = 1   ->  2   (-1 + 2 + 1)
```

**Constraints:** `3 <= len(nums) <= 500`, `-1000 <= nums[i], target <= 1000`.
""",
    """def threeSumClosest(nums, target):
    nums = sorted(nums)
    n = len(nums)
    best = nums[0] + nums[1] + nums[2]
    for i in range(n - 2):
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if abs(s - target) < abs(best - target) or \
                    (abs(s - target) == abs(best - target) and s < best):
                best = s
            if s == target:
                return s
            if s < target:
                lo += 1
            else:
                hi -= 1
    return best
""",
    visible=[{"nums": [-1, 2, 1, -4], "target": 1}],
    hidden=[{"nums": [0, 0, 0], "target": 1}, {"nums": [1, 1, 1, 0], "target": -100},
            {"nums": [-3, -2, -5, 3, -4], "target": -1}, {"nums": [4, 0, 5, -5, 3, 3, 0, -4, -5], "target": -2}],
    gen=_3sumclosest_gen,
    brute=_3sumclosest_brute,
    checks=[({"nums": [-1, 2, 1, -4], "target": 1}, 2), ({"nums": [0, 0, 0], "target": 1}, 0),
            ({"nums": [1, 1, 1], "target": 0}, 3)],
    source="new_p")


# ===========================================================================
# 6. Prime Palindrome
# ===========================================================================
add("prime-palindrome", "Prime Palindrome", "medium",
    ["math", "number-theory"], "primePalindrome", [("N", "int")], "int",
    """
Return the smallest **prime palindrome** greater than or equal to `N`. A number is
prime if it is greater than `1` and divisible only by `1` and itself; it is a
palindrome if it reads the same forwards and backwards.

**Examples**
```
N = 6    ->  7
N = 8    ->  11
N = 13   ->  101
```

**Constraints:** `1 <= N <= 10^8`. The answer exists and is less than `2*10^8`.
""",
    """def primePalindrome(N):
    def is_prime(x):
        if x < 2:
            return False
        if x % 2 == 0:
            return x == 2
        i = 3
        while i * i <= x:
            if x % i == 0:
                return False
            i += 2
        return True
    if 8 <= N <= 11:
        return 11
    length = len(str(N))
    while True:
        if length % 2 == 0:
            length += 1
            continue
        half = length // 2 + 1
        for first in range(10 ** (half - 1), 10 ** half):
            s = str(first)
            pal = int(s + s[-2::-1])
            if pal >= N and is_prime(pal):
                return pal
        length += 1
""",
    visible=[{"N": 6}, {"N": 8}, {"N": 13}],
    hidden=[{"N": 1}, {"N": 2}, {"N": 11}, {"N": 12}, {"N": 100}, {"N": 999}],
    gen=_primepal_gen,
    brute=_primepal_brute,
    checks=[({"N": 6}, 7), ({"N": 8}, 11), ({"N": 13}, 101), ({"N": 1}, 2),
            ({"N": 11}, 11), ({"N": 12}, 101)],
    source="new_p")


# ===========================================================================
# 7. Minimum Number of K Consecutive Bit Flips
# ===========================================================================
add("minimum-number-of-k-consecutive-bit-flips",
    "Minimum Number of K Consecutive Bit Flips", "hard",
    ["array", "greedy", "sliding-window", "prefix-sum"], "minKBitFlips",
    [("A", "int[]"), ("K", "int")], "int",
    """
`A` contains only `0`s and `1`s. A **K-bit flip** chooses a contiguous subarray of
length `K` and flips every bit in it (`0<->1`). Return the minimum number of K-bit
flips so that `A` contains no `0`, or `-1` if it is impossible.

**Examples**
```
A = [0,1,0], K = 1              ->  2
A = [1,1,0], K = 2              ->  -1
A = [0,0,0,1,0,1,1,0], K = 3    ->  3
```

**Constraints:** `1 <= len(A) <= 3*10^4`, `1 <= K <= len(A)`.
""",
    """def minKBitFlips(A, K):
    n = len(A)
    diff = [0] * (n + 1)
    flip = 0
    res = 0
    for i in range(n):
        flip += diff[i]
        if (A[i] + flip) % 2 == 0:
            if i + K > n:
                return -1
            res += 1
            flip += 1
            diff[i + K] -= 1
    return res
""",
    visible=[{"A": [0, 1, 0], "K": 1}, {"A": [1, 1, 0], "K": 2},
             {"A": [0, 0, 0, 1, 0, 1, 1, 0], "K": 3}],
    hidden=[{"A": [1], "K": 1}, {"A": [0], "K": 1}, {"A": [0, 0], "K": 2},
            {"A": [1, 1, 1], "K": 2}, {"A": [0, 1, 1, 0, 1, 0, 1], "K": 3}],
    gen=_kflip_gen,
    brute=_kflip_brute,
    checks=[({"A": [0, 1, 0], "K": 1}, 2), ({"A": [1, 1, 0], "K": 2}, -1),
            ({"A": [0, 0, 0, 1, 0, 1, 1, 0], "K": 3}, 3), ({"A": [1], "K": 1}, 0),
            ({"A": [0], "K": 1}, 1), ({"A": [0, 0], "K": 2}, 1)],
    source="new_p")


# ===========================================================================
# 8. Binary String With Substrings Representing 1 To N
# ===========================================================================
add("binary-string-with-substrings-representing-1-to-n",
    "Binary String With Substrings Representing 1 To N", "medium",
    ["string", "hash-table"], "queryString", [("S", "str"), ("N", "int")], "bool",
    """
Given a binary string `S` (only `'0'` and `'1'`) and a positive integer `N`, return
`True` if and only if, for **every** integer `X` from `1` to `N`, the binary
representation of `X` is a substring of `S`.

**Examples**
```
S = "0110", N = 3   ->  True
S = "0110", N = 4   ->  False
```

**Constraints:** `1 <= len(S) <= 1000`, `1 <= N <= 10^9`.
""",
    """def queryString(S, N):
    for i in range(N, N // 2, -1):
        if bin(i)[2:] not in S:
            return False
    return True
""",
    visible=[{"S": "0110", "N": 3}, {"S": "0110", "N": 4}],
    hidden=[{"S": "1", "N": 1}, {"S": "0", "N": 1}, {"S": "0110", "N": 1},
            {"S": "1011", "N": 5}, {"S": "110101011", "N": 7}],
    gen=_querystr_gen,
    brute=_querystr_brute,
    checks=[({"S": "0110", "N": 3}, True), ({"S": "0110", "N": 4}, False),
            ({"S": "1", "N": 1}, True), ({"S": "0", "N": 1}, False)],
    source="new_p")


# ===========================================================================
# 9. Longest Happy String (reframed -> length)
# ===========================================================================
add("longest-happy-string", "Longest Happy String", "medium",
    ["greedy", "heap", "string"], "longestHappyStringLength",
    [("a", "int"), ("b", "int"), ("c", "int")], "int",
    """
A string is **happy** if it contains none of `"aaa"`, `"bbb"`, or `"ccc"` as a
substring. Using at most `a` copies of `'a'`, `b` of `'b'`, and `c` of `'c'`,
return the **length of the longest possible happy string** (it is `0` if no
non-empty happy string can be built).

**Examples**
```
a = 1, b = 1, c = 7   ->  8     (e.g. "ccaccbcc")
a = 2, b = 2, c = 1   ->  5     (e.g. "aabbc")
a = 7, b = 1, c = 0   ->  5     (e.g. "aabaa")
```

**Constraints:** `0 <= a, b, c <= 100` and `a + b + c > 0`.
""",
    """def longestHappyStringLength(a, b, c):
    import heapq
    heap = []
    if a:
        heapq.heappush(heap, (-a, 'a'))
    if b:
        heapq.heappush(heap, (-b, 'b'))
    if c:
        heapq.heappush(heap, (-c, 'c'))
    res = []
    while heap:
        cnt, ch = heapq.heappop(heap)
        cnt = -cnt
        if len(res) >= 2 and res[-1] == ch and res[-2] == ch:
            if not heap:
                break
            cnt2, ch2 = heapq.heappop(heap)
            cnt2 = -cnt2
            res.append(ch2)
            cnt2 -= 1
            if cnt2:
                heapq.heappush(heap, (-cnt2, ch2))
            heapq.heappush(heap, (-cnt, ch))
        else:
            res.append(ch)
            cnt -= 1
            if cnt:
                heapq.heappush(heap, (-cnt, ch))
    return len(res)
""",
    visible=[{"a": 1, "b": 1, "c": 7}, {"a": 2, "b": 2, "c": 1}, {"a": 7, "b": 1, "c": 0}],
    hidden=[{"a": 0, "b": 0, "c": 1}, {"a": 3, "b": 0, "c": 0}, {"a": 1, "b": 0, "c": 0},
            {"a": 3, "b": 3, "c": 3}, {"a": 5, "b": 5, "c": 1}],
    gen=_happy_gen,
    brute=_happy_brute,
    checks=[({"a": 1, "b": 1, "c": 7}, 8), ({"a": 2, "b": 2, "c": 1}, 5),
            ({"a": 7, "b": 1, "c": 0}, 5), ({"a": 3, "b": 3, "c": 3}, 9),
            ({"a": 3, "b": 0, "c": 0}, 2), ({"a": 1, "b": 0, "c": 0}, 1)],
    source="new_p")


# ===========================================================================
# 10. Kth Smallest Element in a Sorted Matrix
# ===========================================================================
add("kth-smallest-element-in-a-sorted-matrix",
    "Kth Smallest Element in a Sorted Matrix", "medium",
    ["array", "heap", "binary-search", "matrix"], "kthSmallest",
    [("matrix", "int[][]"), ("k", "int")], "int",
    """
Given an `n x n` matrix whose rows and columns are each sorted in ascending order,
return the `k`-th smallest element in the sorted order (counting duplicates, not
distinct values).

**Example**
```
matrix = [[ 1,  5,  9],
          [10, 11, 13],
          [12, 13, 15]], k = 8   ->  13
```

**Constraints:** `1 <= n <= 300`, `1 <= k <= n^2`.
""",
    """def kthSmallest(matrix, k):
    import heapq
    n = len(matrix)
    heap = [(matrix[i][0], i, 0) for i in range(n)]
    heapq.heapify(heap)
    for _ in range(k - 1):
        val, r, c = heapq.heappop(heap)
        if c + 1 < len(matrix[r]):
            heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))
    return heap[0][0]
""",
    visible=[{"matrix": [[1, 5, 9], [10, 11, 13], [12, 13, 15]], "k": 8}],
    hidden=[{"matrix": [[5]], "k": 1}, {"matrix": [[1, 2], [1, 3]], "k": 2},
            {"matrix": [[-5]], "k": 1}, {"matrix": [[1, 3, 5], [6, 7, 12], [11, 14, 14]], "k": 6}],
    gen=_kthsmallest_gen,
    brute=_kthsmallest_brute,
    checks=[({"matrix": [[1, 5, 9], [10, 11, 13], [12, 13, 15]], "k": 8}, 13),
            ({"matrix": [[5]], "k": 1}, 5), ({"matrix": [[1, 2], [1, 3]], "k": 2}, 1),
            ({"matrix": [[-5]], "k": 1}, -5)],
    source="new_p")


# ===========================================================================
# 11. Maximum Width Ramp
# ===========================================================================
add("maximum-width-ramp", "Maximum Width Ramp", "medium",
    ["array", "stack", "monotonic-stack"], "maxWidthRamp", [("A", "int[]")], "int",
    """
A **ramp** is a pair of indices `(i, j)` with `i < j` and `A[i] <= A[j]`; its width
is `j - i`. Return the maximum width over all ramps in `A`, or `0` if none exists.

**Examples**
```
A = [6,0,8,2,1,5]                 ->  4   (i=1, j=5)
A = [9,8,1,0,1,9,4,0,4,1]         ->  7   (i=2, j=9)
```

**Constraints:** `2 <= len(A) <= 5*10^4`, `0 <= A[i] <= 5*10^4`.
""",
    """def maxWidthRamp(A):
    stack = []
    for i, x in enumerate(A):
        if not stack or A[stack[-1]] > x:
            stack.append(i)
    best = 0
    for j in range(len(A) - 1, -1, -1):
        while stack and A[stack[-1]] <= A[j]:
            best = max(best, j - stack.pop())
    return best
""",
    visible=[{"A": [6, 0, 8, 2, 1, 5]}, {"A": [9, 8, 1, 0, 1, 9, 4, 0, 4, 1]}],
    hidden=[{"A": [1, 2]}, {"A": [2, 1]}, {"A": [3, 3, 3]}, {"A": [5, 4, 3, 2, 1]}],
    gen=_ramp_gen,
    brute=_ramp_brute,
    checks=[({"A": [6, 0, 8, 2, 1, 5]}, 4), ({"A": [9, 8, 1, 0, 1, 9, 4, 0, 4, 1]}, 7),
            ({"A": [1, 2]}, 1), ({"A": [2, 1]}, 0), ({"A": list(range(1000))}, 999)],
    source="new_p")


# ===========================================================================
# 12. Keys and Rooms
# ===========================================================================
add("keys-and-rooms", "Keys and Rooms", "medium",
    ["graph", "depth-first-search", "breadth-first-search"], "canVisitAllRooms",
    [("rooms", "int[][]")], "bool",
    """
There are `N` rooms numbered `0..N-1`; you start in room `0`, which is unlocked, and
all others are locked. Room `i` contains the keys `rooms[i]`, and a key with value
`v` unlocks room `v`. You may move freely between unlocked rooms. Return `True` if
you can unlock and enter **every** room.

**Examples**
```
rooms = [[1],[2],[3],[]]          ->  True
rooms = [[1,3],[3,0,1],[2],[0]]   ->  False
```

**Constraints:** `1 <= len(rooms) <= 1000`, `0 <= len(rooms[i]) <= 1000`, total keys
`<= 3000`.
""",
    """def canVisitAllRooms(rooms):
    seen = {0}
    stack = [0]
    while stack:
        r = stack.pop()
        for k in rooms[r]:
            if k not in seen:
                seen.add(k)
                stack.append(k)
    return len(seen) == len(rooms)
""",
    visible=[{"rooms": [[1], [2], [3], []]}, {"rooms": [[1, 3], [3, 0, 1], [2], [0]]}],
    hidden=[{"rooms": [[]]}, {"rooms": [[], [0]]}, {"rooms": [[1], [0]]},
            {"rooms": [[1, 2], [], [3], []]}],
    gen=_keys_gen,
    brute=_keys_brute,
    checks=[({"rooms": [[1], [2], [3], []]}, True),
            ({"rooms": [[1, 3], [3, 0, 1], [2], [0]]}, False),
            ({"rooms": [[]]}, True), ({"rooms": [[], [0]]}, False)],
    source="new_p")


# ===========================================================================
# 13. Unique Substrings in Wraparound String
# ===========================================================================
add("unique-substrings-in-wraparound-string",
    "Unique Substrings in Wraparound String", "medium",
    ["string", "dynamic-programming"], "findSubstringInWraproundString",
    [("p", "str")], "int",
    """
Let `s` be the infinite wraparound string of `"abcdefghijklmnopqrstuvwxyz"`
(`...zabcdefghi...`). Given a string `p`, return how many **distinct non-empty
substrings** of `p` also appear in `s`.

**Examples**
```
p = "a"     ->  1
p = "cac"   ->  2     ("a", "c")
p = "zab"   ->  6     ("z","a","b","za","ab","zab")
```

**Constraints:** `1 <= len(p) <= 10^5`, `p` is lowercase letters.
""",
    """def findSubstringInWraproundString(p):
    count = {}
    cur = 0
    for i, ch in enumerate(p):
        if i > 0 and (ord(ch) - ord(p[i - 1])) % 26 == 1:
            cur += 1
        else:
            cur = 1
        count[ch] = max(count.get(ch, 0), cur)
    return sum(count.values())
""",
    visible=[{"p": "a"}, {"p": "cac"}, {"p": "zab"}],
    hidden=[{"p": "abcd"}, {"p": "zaz"}, {"p": "aaaa"}, {"p": "abcabc"},
            {"p": "yzab"}],
    gen=_wrap_gen,
    brute=_wrap_brute,
    checks=[({"p": "a"}, 1), ({"p": "cac"}, 2), ({"p": "zab"}, 6),
            ({"p": "abcd"}, 10), ({"p": "aaaa"}, 1)],
    source="new_p")


# ===========================================================================
# 14. Target Sum
# ===========================================================================
add("target-sum", "Target Sum", "medium",
    ["array", "dynamic-programming", "backtracking"], "findTargetSumWays",
    [("nums", "int[]"), ("S", "int")], "int",
    """
You are given a list of non-negative integers `nums` and an integer `S`. Put a `+`
or `-` in front of each number, then sum them. Return the number of sign
assignments that make the total equal to `S`.

**Example**
```
nums = [1,1,1,1,1], S = 3   ->  5
```

**Constraints:** `1 <= len(nums) <= 20`, `0 <= nums[i]`, `sum(nums) <= 1000`.
""",
    """def findTargetSumWays(nums, S):
    from collections import defaultdict
    dp = defaultdict(int)
    dp[0] = 1
    for x in nums:
        ndp = defaultdict(int)
        for s, c in dp.items():
            ndp[s + x] += c
            ndp[s - x] += c
        dp = ndp
    return dp[S]
""",
    visible=[{"nums": [1, 1, 1, 1, 1], "S": 3}],
    hidden=[{"nums": [1], "S": 1}, {"nums": [1], "S": 0}, {"nums": [0, 0, 0], "S": 0},
            {"nums": [1, 2, 3, 4, 5], "S": 3}, {"nums": [7, 9, 3, 8, 0, 2, 4, 8, 3, 9], "S": 0}],
    gen=_target_gen,
    brute=_target_brute,
    checks=[({"nums": [1, 1, 1, 1, 1], "S": 3}, 5), ({"nums": [1], "S": 1}, 1),
            ({"nums": [1], "S": 0}, 0), ({"nums": [0, 0, 0], "S": 0}, 8),
            ({"nums": [0 for _ in range(20)], "S": 0}, 1048576)],
    source="new_p")


# ===========================================================================
# 15. Longest Chunked Palindrome Decomposition
# ===========================================================================
add("longest-chunked-palindrome-decomposition",
    "Longest Chunked Palindrome Decomposition", "hard",
    ["string", "greedy", "two-pointers", "hashing"], "longestDecomposition",
    [("text", "str")], "int",
    """
Split `text` into the largest possible number of non-empty parts
`a_1, a_2, ..., a_k` (concatenating back to `text`) such that `a_i = a_{k+1-i}` for
all `i`. Return the maximum `k`.

**Examples**
```
text = "ghiabcdefhelloadamhelloabcdefghi"   ->  7
text = "merchant"                            ->  1
text = "antaprezatepzapreanta"               ->  11
text = "aaa"                                  ->  3
```

**Constraints:** `1 <= len(text) <= 1000`, lowercase letters.
""",
    """def longestDecomposition(text):
    res = 0
    l, r = 0, len(text)
    while l < r:
        for k in range(1, (r - l) // 2 + 1):
            if text[l:l + k] == text[r - k:r]:
                res += 2
                l += k
                r -= k
                break
        else:
            res += 1
            break
    return res
""",
    visible=[{"text": "ghiabcdefhelloadamhelloabcdefghi"}, {"text": "merchant"},
             {"text": "antaprezatepzapreanta"}],
    hidden=[{"text": "aaa"}, {"text": "a"}, {"text": "aa"}, {"text": "aabaa"},
            {"text": "abab"}],
    gen=_decomp_gen,
    brute=_decomp_brute,
    checks=[({"text": "ghiabcdefhelloadamhelloabcdefghi"}, 7), ({"text": "merchant"}, 1),
            ({"text": "antaprezatepzapreanta"}, 11), ({"text": "aaa"}, 3),
            ({"text": "a"}, 1)],
    source="new_p")


# ===========================================================================
# 16. Last Stone Weight II
# ===========================================================================
add("last-stone-weight-ii", "Last Stone Weight II", "medium",
    ["array", "dynamic-programming"], "lastStoneWeightII", [("stones", "int[]")], "int",
    """
You have stones with positive integer weights. Repeatedly pick two stones of
weights `x <= y` and smash them: if `x == y` both are destroyed, otherwise the one
of weight `x` is destroyed and the other becomes `y - x`. At most one stone
remains. Return the smallest possible weight of that stone (`0` if none remain).

**Example**
```
stones = [2,7,4,1,8,1]   ->  1
```

**Constraints:** `1 <= len(stones) <= 30`, `1 <= stones[i] <= 100`.
""",
    """def lastStoneWeightII(stones):
    total = sum(stones)
    half = total // 2
    dp = [False] * (half + 1)
    dp[0] = True
    for s in stones:
        for j in range(half, s - 1, -1):
            if dp[j - s]:
                dp[j] = True
    for j in range(half, -1, -1):
        if dp[j]:
            return total - 2 * j
""",
    visible=[{"stones": [2, 7, 4, 1, 8, 1]}],
    hidden=[{"stones": [1]}, {"stones": [1, 1]}, {"stones": [1, 2]}, {"stones": [2, 2]},
            {"stones": [31, 26, 33, 21, 40]}],
    gen=_stoneii_gen,
    brute=_stoneii_brute,
    checks=[({"stones": [2, 7, 4, 1, 8, 1]}, 1), ({"stones": [1]}, 1),
            ({"stones": [1, 1]}, 0), ({"stones": [1, 2]}, 1), ({"stones": [2, 2]}, 0)],
    source="new_p")


# ===========================================================================
# 17. Minimum Increment to Make Array Unique
# ===========================================================================
add("minimum-increment-to-make-array-unique",
    "Minimum Increment to Make Array Unique", "medium",
    ["array", "greedy", "sorting", "counting"], "minIncrementForUnique",
    [("A", "int[]")], "int",
    """
A move increments any single element of `A` by `1`. Return the least number of
moves needed to make every value in `A` distinct.

**Examples**
```
A = [1,2,2]          ->  1     (-> [1,2,3])
A = [3,2,1,2,1,7]    ->  6     (e.g. -> [3,4,1,2,5,7])
```

**Constraints:** `0 <= len(A) <= 4*10^4`, `0 <= A[i] < 4*10^4`.
""",
    """def minIncrementForUnique(A):
    A = sorted(A)
    moves = 0
    prev = None
    for x in A:
        if prev is not None and x <= prev:
            need = prev + 1
            moves += need - x
            prev = need
        else:
            prev = x
    return moves
""",
    visible=[{"A": [1, 2, 2]}, {"A": [3, 2, 1, 2, 1, 7]}],
    hidden=[{"A": []}, {"A": [5]}, {"A": [1, 1, 1]}, {"A": [0, 0, 0, 0]},
            {"A": [2, 2, 2, 1]}],
    gen=_minunique_gen,
    brute=_minunique_brute,
    checks=[({"A": [1, 2, 2]}, 1), ({"A": [3, 2, 1, 2, 1, 7]}, 6), ({"A": []}, 0),
            ({"A": [5]}, 0), ({"A": [1, 1, 1]}, 3)],
    source="new_p")


# ===========================================================================
# 18. Minimum Number of Increments on Subarrays to Form a Target Array
# ===========================================================================
add("minimum-number-of-increments-on-subarrays-to-form-a-target-array",
    "Minimum Number of Increments on Subarrays to Form a Target Array", "hard",
    ["array", "greedy", "stack"], "minNumberOperations", [("target", "int[]")], "int",
    """
Start with an all-zero array the same length as `target`. One operation chooses any
contiguous subarray and increments each of its values by `1`. Return the minimum
number of operations to turn the array into `target`.

**Examples**
```
target = [1,2,3,2,1]   ->  3
target = [3,1,1,2]     ->  4
target = [3,1,5,4,2]   ->  7
```

**Constraints:** `1 <= len(target) <= 10^5`, `1 <= target[i] <= 10^5`.
""",
    """def minNumberOperations(target):
    res = target[0]
    for i in range(1, len(target)):
        if target[i] > target[i - 1]:
            res += target[i] - target[i - 1]
    return res
""",
    visible=[{"target": [1, 2, 3, 2, 1]}, {"target": [3, 1, 1, 2]}, {"target": [3, 1, 5, 4, 2]}],
    hidden=[{"target": [1, 1, 1, 1]}, {"target": [5]}, {"target": [1, 2, 3, 4, 5]},
            {"target": [5, 4, 3, 2, 1]}, {"target": [2, 1, 2, 1, 2]}],
    gen=_increments_gen,
    brute=_increments_brute,
    checks=[({"target": [1, 2, 3, 2, 1]}, 3), ({"target": [3, 1, 1, 2]}, 4),
            ({"target": [3, 1, 5, 4, 2]}, 7), ({"target": [1, 1, 1, 1]}, 1),
            ({"target": [5]}, 5)],
    source="new_p")


# ===========================================================================
# 19. Shortest Palindrome
# ===========================================================================
add("shortest-palindrome", "Shortest Palindrome", "hard",
    ["string", "hashing"], "shortestPalindrome", [("s", "str")], "str",
    """
By adding characters **only in front** of `s`, convert it into a palindrome. Return
the shortest palindrome obtainable this way. (The answer is unique: prepending
characters fixes both its length and its content.)

**Examples**
```
s = "aacecaaa"   ->  "aaacecaaa"
s = "abcd"       ->  "dcbabcd"
```

**Constraints:** `0 <= len(s) <= 5*10^4`, lowercase letters.
""",
    """def shortestPalindrome(s):
    if not s:
        return s
    rev = s[::-1]
    combined = s + "#" + rev
    n = len(combined)
    lps = [0] * n
    for i in range(1, n):
        j = lps[i - 1]
        while j > 0 and combined[i] != combined[j]:
            j = lps[j - 1]
        if combined[i] == combined[j]:
            j += 1
        lps[i] = j
    overlap = lps[-1]
    return rev[:len(s) - overlap] + s
""",
    visible=[{"s": "aacecaaa"}, {"s": "abcd"}],
    hidden=[{"s": ""}, {"s": "a"}, {"s": "aa"}, {"s": "ab"}, {"s": "abacd"}],
    gen=_shortpal_gen,
    brute=_shortpal_brute,
    checks=[({"s": "aacecaaa"}, "aaacecaaa"), ({"s": "abcd"}, "dcbabcd"), ({"s": ""}, ""),
            ({"s": "a"}, "a"), ({"s": "ab"}, "bab")],
    source="new_p")


# ===========================================================================
# 20. Minimize Malware Spread
# ===========================================================================
add("minimize-malware-spread", "Minimize Malware Spread", "hard",
    ["graph", "union-find", "depth-first-search", "breadth-first-search"],
    "minMalwareSpread", [("graph", "int[][]"), ("initial", "int[]")], "int",
    """
`graph` is the adjacency matrix of a network: node `i` and `j` are directly
connected iff `graph[i][j] == 1`. The nodes in `initial` are infected; infection
spreads through connections until no more nodes become infected. Let `M(initial)`
be the final number of infected nodes.

Remove exactly one node from `initial` so that `M(initial)` is minimized, and return
that node (the smallest index if several tie). A removed node may still be reinfected
through the network.

**Examples**
```
graph = [[1,1,0],[1,1,0],[0,0,1]], initial = [0,1]   ->  0
graph = [[1,0,0],[0,1,0],[0,0,1]], initial = [0,2]   ->  0
graph = [[1,1,1],[1,1,1],[1,1,1]], initial = [1,2]   ->  1
```

**Constraints:** `2 <= len(graph) <= 300`, `graph` is symmetric with `graph[i][i] == 1`,
`1 <= len(initial) <= len(graph)`.
""",
    """def minMalwareSpread(graph, initial):
    n = len(graph)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if graph[i][j] == 1:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[ri] = rj
    from collections import Counter, defaultdict
    size = Counter(find(i) for i in range(n))
    infected = defaultdict(int)
    for node in initial:
        infected[find(node)] += 1
    best = min(initial)
    best_saved = -1
    for node in sorted(initial):
        root = find(node)
        if infected[root] == 1 and size[root] > best_saved:
            best_saved = size[root]
            best = node
    return best
""",
    visible=[{"graph": [[1, 1, 0], [1, 1, 0], [0, 0, 1]], "initial": [0, 1]},
             {"graph": [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "initial": [0, 2]},
             {"graph": [[1, 1, 1], [1, 1, 1], [1, 1, 1]], "initial": [1, 2]}],
    hidden=[{"graph": [[1, 0], [0, 1]], "initial": [0]},
            {"graph": [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]], "initial": [0, 2]},
            {"graph": [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], "initial": [0, 1, 2]}],
    gen=_malware_gen,
    brute=_malware_brute,
    checks=[({"graph": [[1, 1, 0], [1, 1, 0], [0, 0, 1]], "initial": [0, 1]}, 0),
            ({"graph": [[1, 0, 0], [0, 1, 0], [0, 0, 1]], "initial": [0, 2]}, 0),
            ({"graph": [[1, 1, 1], [1, 1, 1], [1, 1, 1]], "initial": [1, 2]}, 1)],
    source="new_p")
