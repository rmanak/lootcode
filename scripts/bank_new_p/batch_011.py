"""Batch 011 of the new_p.txt import (19 problems).

One entry was dropped as a duplicate under a different slug (see `_skips.py`):
`search-a-2d-matrix` (== `search-sorted-matrix`).
"""
from scripts.build_bank import add, ilist, sstr  # noqa: F401


# --------------------------- brute / reference helpers ---------------------
def _ugly_brute(n):
    def is_ugly(x):
        for p in (2, 3, 5):
            while x % p == 0:
                x //= p
        return x == 1
    count = 0
    x = 0
    while count < n:
        x += 1
        if is_ugly(x):
            count += 1
    return x


def _battle_brute(board):
    m, n = len(board), len(board[0])
    seen = [[False] * n for _ in range(m)]

    def dfs(i, j):
        seen[i][j] = True
        for di, dj in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            ni, nj = i + di, j + dj
            if 0 <= ni < m and 0 <= nj < n and board[ni][nj] == 'X' and not seen[ni][nj]:
                dfs(ni, nj)
    c = 0
    for i in range(m):
        for j in range(n):
            if board[i][j] == 'X' and not seen[i][j]:
                dfs(i, j)
                c += 1
    return c


def _squares_brute(n):
    from collections import deque
    if n == 0:
        return 0
    squares = [i * i for i in range(1, int(n ** 0.5) + 1)]
    seen = {0}
    q = deque([(0, 0)])
    while q:
        v, d = q.popleft()
        for s in squares:
            nv = v + s
            if nv == n:
                return d + 1
            if nv < n and nv not in seen:
                seen.add(nv)
                q.append((nv, d + 1))
    return n


def _delcol3_brute(A):
    from itertools import combinations
    n = len(A[0])
    best = 0
    for size in range(n, 0, -1):
        found = False
        for cols in combinations(range(n), size):
            if all(all(row[cols[k]] <= row[cols[k + 1]] for k in range(len(cols) - 1))
                   for row in A):
                found = True
                break
        if found:
            best = size
            break
    return n - best


def _split_brute(nums, m):
    from functools import lru_cache
    n = len(nums)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + nums[i]

    @lru_cache(None)
    def dp(i, parts):
        if parts == 1:
            return pre[n] - pre[i]
        best = float('inf')
        for j in range(i + 1, n - parts + 2):
            best = min(best, max(pre[j] - pre[i], dp(j, parts - 1)))
        return best
    return dp(0, m)


def _nice_brute(nums, k):
    n = len(nums)
    c = 0
    for i in range(n):
        odd = 0
        for j in range(i, n):
            odd += nums[j] % 2
            if odd == k:
                c += 1
            elif odd > k:
                break
    return c


def _perminstr_brute(s1, s2):
    k = len(s1)
    target = sorted(s1)
    for i in range(len(s2) - k + 1):
        if sorted(s2[i:i + k]) == target:
            return True
    return False


def _maxsumdel_brute(arr):
    def kadane(a):
        if not a:
            return float('-inf')
        best = cur = a[0]
        for x in a[1:]:
            cur = max(x, cur + x)
            best = max(best, cur)
        return best
    res = kadane(arr)
    for i in range(len(arr)):
        res = max(res, kadane(arr[:i] + arr[i + 1:]))
    return res


def _kdistinct_brute(A, K):
    n = len(A)
    c = 0
    for i in range(n):
        s = set()
        for j in range(i, n):
            s.add(A[j])
            if len(s) == K:
                c += 1
            elif len(s) > K:
                break
    return c


def _brokencalc_brute(startValue, target):
    from collections import deque
    if startValue >= target:
        return startValue - target
    seen = {startValue}
    q = deque([(startValue, 0)])
    while q:
        v, d = q.popleft()
        if v == target:
            return d
        for nv in (v * 2, v - 1):
            if nv == target:
                return d + 1
            if 0 < nv < 2 * target and nv not in seen:
                seen.add(nv)
                q.append((nv, d + 1))
    return -1


def _strchain_brute(words):
    from functools import lru_cache
    wset = set(words)

    @lru_cache(None)
    def f(w):
        best = 1
        for i in range(len(w)):
            pred = w[:i] + w[i + 1:]
            if pred in wset:
                best = max(best, f(pred) + 1)
        return best
    return max(f(w) for w in words)


def _numsubseq_brute(nums, target):
    n = len(nums)
    c = 0
    for mask in range(1, 1 << n):
        sub = [nums[i] for i in range(n) if mask & (1 << i)]
        if min(sub) + max(sub) <= target:
            c += 1
    return c % (10 ** 9 + 7)


def _dice_brute(n, rollMax):
    from itertools import product
    c = 0
    for seq in product(range(6), repeat=n):
        ok = True
        run = 1
        for i in range(1, n):
            if seq[i] == seq[i - 1]:
                run += 1
                if run > rollMax[seq[i]]:
                    ok = False
                    break
            else:
                run = 1
        if ok:
            c += 1
    return c % (10 ** 9 + 7)


def _kthlex_brute(n, k):
    return sorted(range(1, n + 1), key=str)[k - 1]


def _seat_brute(seats):
    n = len(seats)
    ones = [i for i in range(n) if seats[i] == 1]
    best = 0
    for i in range(n):
        if seats[i] == 0:
            best = max(best, min(abs(i - o) for o in ones))
    return best


def _findreplace_brute(S, indexes, sources, targets):
    repl = {}
    for idx, src, tgt in zip(indexes, sources, targets):
        if S[idx:idx + len(src)] == src:
            repl[idx] = (src, tgt)
    res = []
    i = 0
    n = len(S)
    while i < n:
        if i in repl:
            src, tgt = repl[i]
            res.append(tgt)
            i += len(src)
        else:
            res.append(S[i])
            i += 1
    return "".join(res)


def _ship_brute(weights, days):
    def need(cap):
        d = 1
        cur = 0
        for w in weights:
            if cur + w > cap:
                d += 1
                cur = w
            else:
                cur += w
        return d
    cap = max(weights)
    while need(cap) > days:
        cap += 1
    return cap


def _tiling_brute(n, m):
    grid = [[False] * m for _ in range(n)]
    best = [n * m]

    def find_empty():
        for i in range(n):
            for j in range(m):
                if not grid[i][j]:
                    return (i, j)
        return None

    def dfs(count):
        if count >= best[0]:
            return
        cell = find_empty()
        if cell is None:
            best[0] = min(best[0], count)
            return
        i, j = cell
        max_s = 0
        while i + max_s < n and j + max_s < m:
            ok = True
            for t in range(max_s + 1):
                if grid[i + max_s][j + t] or grid[i + t][j + max_s]:
                    ok = False
                    break
            if not ok:
                break
            max_s += 1
        for s in range(max_s, 0, -1):
            for a in range(s):
                for b in range(s):
                    grid[i + a][j + b] = True
            dfs(count + 1)
            for a in range(s):
                for b in range(s):
                    grid[i + a][j + b] = False
    dfs(0)
    return best[0]


# gen helpers ---------------------------------------------------------------
def _path_gen(r):
    parts = [r.choice([".", "..", "a", "bb", "home", "x"]) for _ in range(r.randint(0, 6))]
    return {"path": "/" + "/".join(parts)}


def _battle_gen(r):
    rows, cols = r.randint(1, 5), r.randint(1, 5)
    grid = [['.'] * cols for _ in range(rows)]

    def can_place(cells):
        for i, j in cells:
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols and grid[ni][nj] == 'X':
                        return False
        return True

    for _ in range(r.randint(0, 4)):
        horiz = r.random() < 0.5
        length = r.randint(1, 3)
        si, sj = r.randint(0, rows - 1), r.randint(0, cols - 1)
        cells = [(si, sj + k) if horiz else (si + k, sj) for k in range(length)]
        if all(0 <= i < rows and 0 <= j < cols for i, j in cells) and can_place(cells):
            for i, j in cells:
                grid[i][j] = 'X'
    return {"board": ["".join(row) for row in grid]}


def _seat_gen(r):
    while True:
        s = [r.randint(0, 1) for _ in range(r.randint(2, 10))]
        if 0 in s and 1 in s:
            return {"seats": s}


def _findreplace_gen(r):
    n = r.randint(1, 8)
    S = "".join(r.choice("ab") for _ in range(n))
    indexes, sources, targets = [], [], []
    i = 0
    while i < n:
        if r.random() < 0.5:
            L = r.randint(1, min(2, n - i))
            indexes.append(i)
            if r.random() < 0.7:
                sources.append(S[i:i + L])
            else:
                sources.append("".join(r.choice("abc") for _ in range(L)))
            targets.append("".join(r.choice("xy") for _ in range(r.randint(1, 3))))
            i += L
        else:
            i += 1
    return {"S": S, "indexes": indexes, "sources": sources, "targets": targets}


# ===========================================================================
# 1. Simplify Path
# ===========================================================================
add("simplify-path", "Simplify Path", "medium",
    ["string", "stack"], "simplifyPath", [("path", "string")], "string",
    """
Given an absolute Unix-style file `path`, **return its simplified canonical path.**
Collapse `.` (current dir), `..` (parent dir), and redundant slashes; the result
starts with a single `/` and has no trailing slash (except the root `/`).

**Examples**
```
"/home/"          ->  "/home"
"/a/./b/../../c/" ->  "/c"
"/../"            ->  "/"
"/home//foo/"     ->  "/home/foo"
```

**Constraints:** `1 <= len(path) <= 3000`, valid absolute path.
""",
    """def simplifyPath(path):
    stack = []
    for part in path.split("/"):
        if part == "" or part == ".":
            continue
        if part == "..":
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return "/" + "/".join(stack)
""",
    visible=[{"path": "/home/"}, {"path": "/a/./b/../../c/"}, {"path": "/../"},
             {"path": "/home//foo/"}],
    hidden=[{"path": "/"}, {"path": "/..."}, {"path": "/a/../../b/../c//.//"},
            {"path": "/a//b////c/d//././/.."}],
    gen=lambda r: [_path_gen(r) for _ in range(8)],
    brute=lambda path: __import__("os").path.normpath(path),
    checks=[({"path": "/home/"}, "/home"), ({"path": "/a/./b/../../c/"}, "/c"),
            ({"path": "/../"}, "/"), ({"path": "/home//foo/"}, "/home/foo")],
    source="new_p")


# ===========================================================================
# 2. Ugly Number II
# ===========================================================================
add("ugly-number-ii", "Ugly Number II", "medium",
    ["math", "dynamic-programming", "heap"], "nthUglyNumber", [("n", "int")], "int",
    """
An *ugly number* is a positive integer whose only prime factors are `2`, `3`, and `5`
(`1` counts as ugly). **Return the `n`-th ugly number** (1-indexed).

**Example**
```
n = 10  ->  12   (1, 2, 3, 4, 5, 6, 8, 9, 10, 12)
```

**Constraints:** `1 <= n <= 1690`.
""",
    """def nthUglyNumber(n):
    ugly = [1] * n
    i2 = i3 = i5 = 0
    for i in range(1, n):
        nxt = min(ugly[i2] * 2, ugly[i3] * 3, ugly[i5] * 5)
        ugly[i] = nxt
        if nxt == ugly[i2] * 2:
            i2 += 1
        if nxt == ugly[i3] * 3:
            i3 += 1
        if nxt == ugly[i5] * 5:
            i5 += 1
    return ugly[-1]
""",
    visible=[{"n": 10}],
    hidden=[{"n": 1}, {"n": 2}, {"n": 5}, {"n": 11}, {"n": 50}],
    gen=lambda r: [{"n": r.randint(1, 40)} for _ in range(8)],
    brute=_ugly_brute,
    checks=[({"n": 10}, 12), ({"n": 1}, 1), ({"n": 2}, 2), ({"n": 7}, 8)],
    source="new_p")


# ===========================================================================
# 3. Battleships in a Board
# ===========================================================================
add("battleships-in-a-board", "Battleships in a Board", "medium",
    ["array", "depth-first-search", "matrix"], "countBattleships",
    [("board", "string[]")], "int",
    """
A board of `'X'` (ship) and `'.'` (empty) holds battleships placed horizontally or
vertically (`1xN` or `Nx1`), each separated from others by at least one cell. **Return
the number of battleships.**

**Example**
```
board = ["X..X","...X","...X"]  ->  2
```

**Constraints:** rows of equal length, only `'X'`/`'.'`, valid (separated) board.
""",
    """def countBattleships(board):
    count = 0
    m, n = len(board), len(board[0])
    for i in range(m):
        for j in range(n):
            if board[i][j] == 'X':
                if i > 0 and board[i - 1][j] == 'X':
                    continue
                if j > 0 and board[i][j - 1] == 'X':
                    continue
                count += 1
    return count
""",
    visible=[{"board": ["X..X", "...X", "...X"]}],
    hidden=[{"board": ["..."]}, {"board": ["X"]}, {"board": ["XXX"]},
            {"board": ["X", "X", "X"]}, {"board": [".X.", ".X.", "..."]}],
    gen=lambda r: [_battle_gen(r) for _ in range(8)],
    brute=_battle_brute,
    checks=[({"board": ["X..X", "...X", "...X"]}, 2), ({"board": ["..."]}, 0),
            ({"board": ["X"]}, 1)],
    source="new_p")


# ===========================================================================
# 4. Perfect Squares
# ===========================================================================
add("perfect-squares", "Perfect Squares", "medium",
    ["math", "dynamic-programming", "breadth-first-search"], "numSquares",
    [("n", "int")], "int",
    """
**Return the least number of perfect squares (`1, 4, 9, 16, ...`) that sum to `n`.**

**Examples**
```
n = 12  ->  3   (4 + 4 + 4)
n = 13  ->  2   (4 + 9)
```

**Constraints:** `1 <= n <= 10^4`.
""",
    """def numSquares(n):
    dp = [0] + [float('inf')] * n
    for i in range(1, n + 1):
        j = 1
        while j * j <= i:
            dp[i] = min(dp[i], dp[i - j * j] + 1)
            j += 1
    return dp[n]
""",
    visible=[{"n": 12}, {"n": 13}],
    hidden=[{"n": 1}, {"n": 2}, {"n": 4}, {"n": 43}, {"n": 100}],
    gen=lambda r: [{"n": r.randint(1, 50)} for _ in range(8)],
    brute=_squares_brute,
    checks=[({"n": 12}, 3), ({"n": 13}, 2), ({"n": 1}, 1), ({"n": 4}, 1)],
    source="new_p")


# ===========================================================================
# 5. Delete Columns to Make Sorted III
# ===========================================================================
add("delete-columns-to-make-sorted-iii", "Delete Columns to Make Sorted III", "hard",
    ["array", "string", "dynamic-programming"], "minDeletionSize",
    [("A", "string[]")], "int",
    """
`A` is a list of equal-length strings. Choosing a set of column indices to delete
from every string, **return the minimum number of columns to delete so that every
remaining row is in non-decreasing order.**

**Examples**
```
A = ["babca","bbazb"]  ->  3
A = ["edcba"]          ->  4
A = ["ghi","def","abc"] ->  0
```

**Constraints:** `1 <= len(A) <= 100`, `1 <= len(A[i]) <= 100`, lowercase letters.
""",
    """def minDeletionSize(A):
    n = len(A[0])
    dp = [1] * n
    for j in range(n):
        for i in range(j):
            if all(row[i] <= row[j] for row in A):
                dp[j] = max(dp[j], dp[i] + 1)
    return n - max(dp)
""",
    visible=[{"A": ["babca", "bbazb"]}, {"A": ["edcba"]}, {"A": ["ghi", "def", "abc"]}],
    hidden=[{"A": ["a"]}, {"A": ["ab"]}, {"A": ["ba"]}, {"A": ["abc", "cba"]}],
    gen=lambda r: [(lambda rows, cols: {"A": [sstr(r, cols, cols, "ab") for _ in range(rows)]})
                   (r.randint(1, 3), r.randint(1, 5)) for _ in range(6)],
    brute=_delcol3_brute,
    checks=[({"A": ["babca", "bbazb"]}, 3), ({"A": ["edcba"]}, 4),
            ({"A": ["ghi", "def", "abc"]}, 0)],
    source="new_p")


# ===========================================================================
# 6. Split Array Largest Sum
# ===========================================================================
add("split-array-largest-sum", "Split Array Largest Sum", "hard",
    ["array", "binary-search", "dynamic-programming"], "splitArray",
    [("nums", "int[]"), ("m", "int")], "int",
    """
Split `nums` into `m` non-empty contiguous subarrays. **Return the minimum possible
value of the largest subarray sum** over all such splits.

**Examples**
```
nums = [7,2,5,10,8], m = 2  ->  18
nums = [1,2,3,4,5], m = 2   ->  9
nums = [1,4,4], m = 3       ->  4
```

**Constraints:** `1 <= len(nums) <= 1000`, `1 <= m <= min(50, len(nums))`,
`0 <= nums[i]`.
""",
    """def splitArray(nums, m):
    lo, hi = max(nums), sum(nums)

    def need(cap):
        cnt, cur = 1, 0
        for x in nums:
            if cur + x > cap:
                cnt += 1
                cur = x
            else:
                cur += x
        return cnt

    while lo < hi:
        mid = (lo + hi) // 2
        if need(mid) <= m:
            hi = mid
        else:
            lo = mid + 1
    return lo
""",
    visible=[{"nums": [7, 2, 5, 10, 8], "m": 2}, {"nums": [1, 2, 3, 4, 5], "m": 2},
             {"nums": [1, 4, 4], "m": 3}],
    hidden=[{"nums": [1], "m": 1}, {"nums": [5, 5, 5], "m": 3}, {"nums": [2, 3, 1, 2, 4, 3], "m": 5},
            {"nums": [0, 0, 0], "m": 2}],
    gen=lambda r: [(lambda nums: {"nums": nums, "m": r.randint(1, len(nums))})
                   ([r.randint(0, 10) for _ in range(r.randint(1, 8))]) for _ in range(6)],
    brute=_split_brute,
    checks=[({"nums": [7, 2, 5, 10, 8], "m": 2}, 18), ({"nums": [1, 2, 3, 4, 5], "m": 2}, 9),
            ({"nums": [1, 4, 4], "m": 3}, 4)],
    source="new_p")


# ===========================================================================
# 7. Count Number of Nice Subarrays
# ===========================================================================
add("count-number-of-nice-subarrays", "Count Number of Nice Subarrays", "medium",
    ["array", "hash-table", "math", "sliding-window", "prefix-sum"], "numberOfSubarrays",
    [("nums", "int[]"), ("k", "int")], "int",
    """
A subarray is *nice* if it contains exactly `k` odd numbers. **Return the number of
nice subarrays.**

**Examples**
```
nums = [1,1,2,1,1], k = 3              ->  2
nums = [2,4,6], k = 1                  ->  0
nums = [2,2,2,1,2,2,1,2,2,2], k = 2    ->  16
```

**Constraints:** `1 <= len(nums) <= 5*10^4`, `1 <= nums[i] <= 10^5`,
`1 <= k <= len(nums)`.
""",
    """def numberOfSubarrays(nums, k):
    from collections import defaultdict
    count = defaultdict(int)
    count[0] = 1
    odd = 0
    res = 0
    for x in nums:
        odd += x % 2
        res += count[odd - k]
        count[odd] += 1
    return res
""",
    visible=[{"nums": [1, 1, 2, 1, 1], "k": 3}, {"nums": [2, 4, 6], "k": 1},
             {"nums": [2, 2, 2, 1, 2, 2, 1, 2, 2, 2], "k": 2}],
    hidden=[{"nums": [1], "k": 1}, {"nums": [2], "k": 1}, {"nums": [1, 1, 1], "k": 1},
            {"nums": [1, 1, 2, 1, 1], "k": 1}],
    gen=lambda r: [(lambda nums: {"nums": nums, "k": r.randint(1, len(nums))})
                   ([r.randint(1, 6) for _ in range(r.randint(1, 12))]) for _ in range(6)],
    brute=_nice_brute,
    checks=[({"nums": [1, 1, 2, 1, 1], "k": 3}, 2), ({"nums": [2, 4, 6], "k": 1}, 0),
            ({"nums": [2, 2, 2, 1, 2, 2, 1, 2, 2, 2], "k": 2}, 16)],
    source="new_p")


# ===========================================================================
# 8. Permutation in String
# ===========================================================================
add("permutation-in-string", "Permutation in String", "medium",
    ["string", "hash-table", "sliding-window", "two-pointers"], "checkInclusion",
    [("s1", "string"), ("s2", "string")], "bool",
    """
**Return `true` if `s2` contains a permutation of `s1` as a substring.**

**Examples**
```
s1 = "ab", s2 = "eidbaooo"  ->  true
s1 = "ab", s2 = "eidboaoo"  ->  false
```

**Constraints:** `1 <= len(s1), len(s2) <= 10^4`, lowercase letters.
""",
    """def checkInclusion(s1, s2):
    from collections import Counter
    need = Counter(s1)
    k = len(s1)
    if k > len(s2):
        return False
    window = Counter(s2[:k])
    if window == need:
        return True
    for i in range(k, len(s2)):
        window[s2[i]] += 1
        window[s2[i - k]] -= 1
        if window[s2[i - k]] == 0:
            del window[s2[i - k]]
        if window == need:
            return True
    return False
""",
    visible=[{"s1": "ab", "s2": "eidbaooo"}, {"s1": "ab", "s2": "eidboaoo"}],
    hidden=[{"s1": "a", "s2": "a"}, {"s1": "abc", "s2": "ab"}, {"s1": "adc", "s2": "dcda"},
            {"s1": "hello", "s2": "ooolleoooleh"}],
    gen=lambda r: [{"s1": sstr(r, 1, 4, "ab"), "s2": sstr(r, 1, 10, "ab")} for _ in range(8)],
    brute=_perminstr_brute,
    checks=[({"s1": "ab", "s2": "eidbaooo"}, True), ({"s1": "ab", "s2": "eidboaoo"}, False),
            ({"s1": "a", "s2": "a"}, True)],
    source="new_p")


# ===========================================================================
# 9. Maximum Subarray Sum with One Deletion
# ===========================================================================
add("maximum-subarray-sum-with-one-deletion", "Maximum Subarray Sum with One Deletion",
    "medium", ["array", "dynamic-programming"], "maximumSum", [("arr", "int[]")], "int",
    """
**Return the maximum sum of a non-empty contiguous subarray, with at most one element
deletion allowed** (the subarray must remain non-empty after the deletion).

**Examples**
```
arr = [1,-2,0,3]      ->  4
arr = [1,-2,-2,3]     ->  3
arr = [-1,-1,-1,-1]   ->  -1
```

**Constraints:** `1 <= len(arr) <= 10^5`, `-10^4 <= arr[i] <= 10^4`.
""",
    """def maximumSum(arr):
    n = len(arr)
    no_del = arr[0]
    one_del = float('-inf')
    best = arr[0]
    for i in range(1, n):
        one_del = max(no_del, one_del + arr[i])
        no_del = max(arr[i], no_del + arr[i])
        best = max(best, no_del, one_del)
    return best
""",
    visible=[{"arr": [1, -2, 0, 3]}, {"arr": [1, -2, -2, 3]}, {"arr": [-1, -1, -1, -1]}],
    hidden=[{"arr": [1]}, {"arr": [-5]}, {"arr": [2, 1, -2, -5, -2]},
            {"arr": [-2, -2, -3]}],
    gen=lambda r: [{"arr": [r.randint(-5, 5) for _ in range(r.randint(1, 10))]}
                   for _ in range(6)],
    brute=_maxsumdel_brute,
    checks=[({"arr": [1, -2, 0, 3]}, 4), ({"arr": [1, -2, -2, 3]}, 3),
            ({"arr": [-1, -1, -1, -1]}, -1)],
    source="new_p")


# ===========================================================================
# 10. Subarrays with K Different Integers
# ===========================================================================
add("subarrays-with-k-different-integers", "Subarrays with K Different Integers", "hard",
    ["array", "hash-table", "sliding-window", "counting"], "subarraysWithKDistinct",
    [("A", "int[]"), ("K", "int")], "int",
    """
**Return the number of contiguous subarrays of `A` that contain exactly `K` distinct
integers.**

**Examples**
```
A = [1,2,1,2,3], K = 2  ->  7
A = [1,2,1,3,4], K = 3  ->  3
```

**Constraints:** `1 <= len(A) <= 2*10^4`, `1 <= A[i] <= len(A)`, `1 <= K <= len(A)`.
""",
    """def subarraysWithKDistinct(A, K):
    from collections import defaultdict

    def atMost(k):
        count = defaultdict(int)
        res = 0
        l = 0
        for r in range(len(A)):
            count[A[r]] += 1
            while len(count) > k:
                count[A[l]] -= 1
                if count[A[l]] == 0:
                    del count[A[l]]
                l += 1
            res += r - l + 1
        return res

    return atMost(K) - atMost(K - 1)
""",
    visible=[{"A": [1, 2, 1, 2, 3], "K": 2}, {"A": [1, 2, 1, 3, 4], "K": 3}],
    hidden=[{"A": [1], "K": 1}, {"A": [1, 1, 1], "K": 1}, {"A": [1, 2, 3], "K": 3},
            {"A": [2, 2, 1, 2, 2], "K": 2}],
    gen=lambda r: [(lambda nums: {"A": nums, "K": r.randint(1, len(set(nums)))})
                   ([r.randint(1, 5) for _ in range(r.randint(1, 12))]) for _ in range(6)],
    brute=_kdistinct_brute,
    checks=[({"A": [1, 2, 1, 2, 3], "K": 2}, 7), ({"A": [1, 2, 1, 3, 4], "K": 3}, 3)],
    source="new_p")


# ===========================================================================
# 11. Broken Calculator
# ===========================================================================
add("broken-calculator", "Broken Calculator", "medium",
    ["math", "greedy"], "brokenCalc", [("startValue", "int"), ("target", "int")], "int",
    """
A calculator shows `startValue`. Each operation either doubles the display or
subtracts `1`. **Return the minimum number of operations to display `target`.**

**Examples**
```
startValue = 2, target = 3     ->  2
startValue = 5, target = 8     ->  2
startValue = 1024, target = 1  ->  1023
```

**Constraints:** `1 <= startValue, target <= 10^9`.
""",
    """def brokenCalc(startValue, target):
    ops = 0
    while target > startValue:
        if target % 2 == 0:
            target //= 2
        else:
            target += 1
        ops += 1
    return ops + (startValue - target)
""",
    visible=[{"startValue": 2, "target": 3}, {"startValue": 5, "target": 8},
             {"startValue": 3, "target": 10}],
    hidden=[{"startValue": 1024, "target": 1}, {"startValue": 1, "target": 1},
            {"startValue": 10, "target": 5}, {"startValue": 7, "target": 11}],
    gen=lambda r: [{"startValue": r.randint(1, 20), "target": r.randint(1, 30)}
                   for _ in range(8)],
    brute=_brokencalc_brute,
    checks=[({"startValue": 2, "target": 3}, 2), ({"startValue": 5, "target": 8}, 2),
            ({"startValue": 3, "target": 10}, 3), ({"startValue": 1024, "target": 1}, 1023)],
    source="new_p")


# ===========================================================================
# 12. Longest String Chain
# ===========================================================================
add("longest-string-chain", "Longest String Chain", "medium",
    ["array", "string", "dynamic-programming", "hash-table"], "longestStrChain",
    [("words", "string[]")], "int",
    """
`word1` is a *predecessor* of `word2` if inserting exactly one letter into `word1`
(anywhere) makes it equal to `word2`. A *chain* is a sequence where each word is a
predecessor of the next. **Return the length of the longest possible word chain.**

**Examples**
```
words = ["a","b","ba","bca","bda","bdca"]      ->  4
words = ["xbc","pcxbcf","xb","cxbc","pcxbc"]    ->  5
words = ["abcd","dbqca"]                        ->  1
```

**Constraints:** `1 <= len(words) <= 1000`, lowercase letters.
""",
    """def longestStrChain(words):
    words.sort(key=len)
    dp = {}
    best = 1
    for w in words:
        dp[w] = 1
        for i in range(len(w)):
            pred = w[:i] + w[i + 1:]
            if pred in dp:
                dp[w] = max(dp[w], dp[pred] + 1)
        best = max(best, dp[w])
    return best
""",
    visible=[{"words": ["a", "b", "ba", "bca", "bda", "bdca"]},
             {"words": ["xbc", "pcxbcf", "xb", "cxbc", "pcxbc"]},
             {"words": ["abcd", "dbqca"]}],
    hidden=[{"words": ["a"]}, {"words": ["a", "ab", "abc"]}, {"words": ["aa", "bb"]},
            {"words": ["ksqvsyq", "ks", "kss", "czvh", "zczpzvdhx"]}],
    gen=lambda r: [{"words": list({sstr(r, 1, 4, "ab") for _ in range(r.randint(1, 6))})}
                   for _ in range(6)],
    brute=_strchain_brute,
    checks=[({"words": ["a", "b", "ba", "bca", "bda", "bdca"]}, 4),
            ({"words": ["xbc", "pcxbcf", "xb", "cxbc", "pcxbc"]}, 5),
            ({"words": ["abcd", "dbqca"]}, 1)],
    source="new_p")


# ===========================================================================
# 13. Number of Subsequences That Satisfy the Given Sum Condition
# ===========================================================================
add("number-of-subsequences-that-satisfy-the-given-sum-condition",
    "Number of Subsequences That Satisfy the Given Sum Condition", "medium",
    ["array", "two-pointers", "sorting"], "numSubseq",
    [("nums", "int[]"), ("target", "int")], "int",
    """
**Return the number of non-empty subsequences of `nums` where the sum of the minimum
and maximum element is `<= target`**, modulo `10^9 + 7`.

**Examples**
```
nums = [3,5,6,7], target = 9          ->  4
nums = [3,3,6,8], target = 10         ->  6
nums = [2,3,3,4,6,7], target = 12     ->  61
```

**Constraints:** `1 <= len(nums) <= 10^5`, `1 <= nums[i] <= 10^6`,
`1 <= target <= 10^6`.
""",
    """def numSubseq(nums, target):
    MOD = 10 ** 9 + 7
    nums.sort()
    n = len(nums)
    pow2 = [1] * n
    for i in range(1, n):
        pow2[i] = pow2[i - 1] * 2 % MOD
    l, r = 0, n - 1
    res = 0
    while l <= r:
        if nums[l] + nums[r] <= target:
            res = (res + pow2[r - l]) % MOD
            l += 1
        else:
            r -= 1
    return res % MOD
""",
    visible=[{"nums": [3, 5, 6, 7], "target": 9}, {"nums": [3, 3, 6, 8], "target": 10},
             {"nums": [2, 3, 3, 4, 6, 7], "target": 12}],
    hidden=[{"nums": [5, 2, 4, 1, 7, 6, 8], "target": 16}, {"nums": [1], "target": 1},
            {"nums": [1], "target": 1}, {"nums": [5, 5], "target": 9}],
    gen=lambda r: [{"nums": [r.randint(1, 10) for _ in range(r.randint(1, 12))],
                    "target": r.randint(1, 20)} for _ in range(6)],
    brute=_numsubseq_brute,
    checks=[({"nums": [3, 5, 6, 7], "target": 9}, 4), ({"nums": [3, 3, 6, 8], "target": 10}, 6),
            ({"nums": [2, 3, 3, 4, 6, 7], "target": 12}, 61),
            ({"nums": [5, 2, 4, 1, 7, 6, 8], "target": 16}, 127)],
    source="new_p")


# ===========================================================================
# 14. Dice Roll Simulation
# ===========================================================================
add("dice-roll-simulation", "Dice Roll Simulation", "hard",
    ["array", "dynamic-programming"], "dieSimulator",
    [("n", "int"), ("rollMax", "int[]")], "int",
    """
A die shows `1`-`6`; face `i` (1-indexed) may not appear more than `rollMax[i-1]`
times **consecutively**. **Return the number of distinct sequences of exactly `n`
rolls**, modulo `10^9 + 7`.

**Examples**
```
n = 2, rollMax = [1,1,2,2,2,3]  ->  34
n = 2, rollMax = [1,1,1,1,1,1]  ->  30
n = 3, rollMax = [1,1,1,2,2,3]  ->  181
```

**Constraints:** `1 <= n <= 5000`, `len(rollMax) == 6`, `1 <= rollMax[i] <= 15`.
""",
    """def dieSimulator(n, rollMax):
    MOD = 10 ** 9 + 7
    dp = [[0] * (rollMax[j] + 1) for j in range(6)]
    for j in range(6):
        dp[j][1] = 1
    for _ in range(n - 1):
        ndp = [[0] * (rollMax[j] + 1) for j in range(6)]
        for j in range(6):
            total_j = sum(dp[j]) % MOD
            for k in range(1, rollMax[j]):
                ndp[j][k + 1] = (ndp[j][k + 1] + dp[j][k]) % MOD
            for x in range(6):
                if x != j:
                    ndp[x][1] = (ndp[x][1] + total_j) % MOD
        dp = ndp
    return sum(sum(row) for row in dp) % MOD
""",
    visible=[{"n": 2, "rollMax": [1, 1, 2, 2, 2, 3]}, {"n": 2, "rollMax": [1, 1, 1, 1, 1, 1]},
             {"n": 3, "rollMax": [1, 1, 1, 2, 2, 3]}],
    hidden=[{"n": 1, "rollMax": [1, 1, 1, 1, 1, 1]}, {"n": 3, "rollMax": [3, 3, 3, 3, 3, 3]},
            {"n": 2, "rollMax": [2, 2, 2, 2, 2, 2]}, {"n": 4, "rollMax": [1, 1, 1, 1, 1, 1]}],
    gen=lambda r: [{"n": r.randint(1, 4), "rollMax": [r.randint(1, 3) for _ in range(6)]}
                   for _ in range(6)],
    brute=_dice_brute,
    checks=[({"n": 2, "rollMax": [1, 1, 2, 2, 2, 3]}, 34),
            ({"n": 2, "rollMax": [1, 1, 1, 1, 1, 1]}, 30),
            ({"n": 3, "rollMax": [1, 1, 1, 2, 2, 3]}, 181)],
    source="new_p")


# ===========================================================================
# 15. K-th Smallest in Lexicographical Order
# ===========================================================================
add("k-th-smallest-in-lexicographical-order", "K-th Smallest in Lexicographical Order",
    "hard", ["math"], "findKthNumber", [("n", "int"), ("k", "int")], "int",
    """
**Return the lexicographically `k`-th smallest integer in `[1, n]`.**

**Example**
```
n = 13, k = 2  ->  10
```
(Lexicographic order: `1, 10, 11, 12, 13, 2, 3, 4, 5, 6, 7, 8, 9`.)

**Constraints:** `1 <= k <= n <= 10^9`.
""",
    """def findKthNumber(n, k):
    def count(prefix):
        cnt = 0
        cur, nxt = prefix, prefix + 1
        while cur <= n:
            cnt += min(n + 1, nxt) - cur
            cur *= 10
            nxt *= 10
        return cnt

    cur = 1
    k -= 1
    while k > 0:
        c = count(cur)
        if c <= k:
            k -= c
            cur += 1
        else:
            cur *= 10
            k -= 1
    return cur
""",
    visible=[{"n": 13, "k": 2}],
    hidden=[{"n": 1, "k": 1}, {"n": 13, "k": 1}, {"n": 100, "k": 10}, {"n": 10, "k": 3},
            {"n": 200, "k": 100}],
    gen=lambda r: [(lambda n: {"n": n, "k": r.randint(1, n)})(r.randint(1, 200))
                   for _ in range(8)],
    brute=_kthlex_brute,
    checks=[({"n": 13, "k": 2}, 10), ({"n": 1, "k": 1}, 1), ({"n": 100, "k": 10}, 17)],
    source="new_p")


# ===========================================================================
# 16. Maximize Distance to Closest Person
# ===========================================================================
add("maximize-distance-to-closest-person", "Maximize Distance to Closest Person",
    "medium", ["array"], "maxDistToClosest", [("seats", "int[]")], "int",
    """
`seats[i]` is `1` if occupied, `0` if empty (there is at least one of each). You sit
in an empty seat to **maximize the distance to the nearest occupied seat**; return
that maximum distance.

**Examples**
```
seats = [1,0,0,0,1,0,1]  ->  2
seats = [1,0,0,0]        ->  3
seats = [0,1]            ->  1
```

**Constraints:** `2 <= len(seats) <= 2*10^4`, `seats[i]` in `{0,1}`.
""",
    """def maxDistToClosest(seats):
    n = len(seats)
    prev = -1
    best = 0
    for i in range(n):
        if seats[i] == 1:
            if prev == -1:
                best = i
            else:
                best = max(best, (i - prev) // 2)
            prev = i
    best = max(best, n - 1 - prev)
    return best
""",
    visible=[{"seats": [1, 0, 0, 0, 1, 0, 1]}, {"seats": [1, 0, 0, 0]}, {"seats": [0, 1]}],
    hidden=[{"seats": [0, 0, 1]}, {"seats": [1, 0, 1]}, {"seats": [0, 0, 1, 0, 0]},
            {"seats": [1, 0, 0, 0, 0, 0, 1]}],
    gen=lambda r: [_seat_gen(r) for _ in range(8)],
    brute=_seat_brute,
    checks=[({"seats": [1, 0, 0, 0, 1, 0, 1]}, 2), ({"seats": [1, 0, 0, 0]}, 3),
            ({"seats": [0, 1]}, 1)],
    source="new_p")


# ===========================================================================
# 17. Find And Replace in String
# ===========================================================================
add("find-and-replace-in-string", "Find And Replace in String", "medium",
    ["array", "string", "sorting"], "findReplaceString",
    [("S", "string"), ("indexes", "int[]"), ("sources", "string[]"), ("targets", "string[]")],
    "string",
    """
Apply replacement operations to `S`, all relative to the **original** string and
**simultaneously**. Operation `(indexes[i], sources[i], targets[i])` replaces
`sources[i]` with `targets[i]` only if `sources[i]` occurs at index `indexes[i]` in
the original `S`. Operations do not overlap. **Return the resulting string.**

**Examples**
```
S = "abcd", indexes = [0,2], sources = ["a","cd"], targets = ["eee","ffff"]  ->  "eeebffff"
S = "abcd", indexes = [0,2], sources = ["ab","ec"], targets = ["eee","ffff"] ->  "eeecd"
```

**Constraints:** `0 <= len(indexes) <= 100`, indices in range, lowercase letters.
""",
    """def findReplaceString(S, indexes, sources, targets):
    ops = sorted(zip(indexes, sources, targets), reverse=True)
    s = S
    for i, src, tgt in ops:
        if s[i:i + len(src)] == src:
            s = s[:i] + tgt + s[i + len(src):]
    return s
""",
    visible=[{"S": "abcd", "indexes": [0, 2], "sources": ["a", "cd"], "targets": ["eee", "ffff"]},
             {"S": "abcd", "indexes": [0, 2], "sources": ["ab", "ec"], "targets": ["eee", "ffff"]}],
    hidden=[{"S": "abc", "indexes": [], "sources": [], "targets": []},
            {"S": "vmokgggqzp", "indexes": [3, 5, 1], "sources": ["kg", "ggq", "mo"],
             "targets": ["s", "so", "bfr"]},
            {"S": "aaa", "indexes": [0], "sources": ["b"], "targets": ["z"]}],
    gen=lambda r: [_findreplace_gen(r) for _ in range(8)],
    brute=_findreplace_brute,
    checks=[({"S": "abcd", "indexes": [0, 2], "sources": ["a", "cd"], "targets": ["eee", "ffff"]},
             "eeebffff"),
            ({"S": "abcd", "indexes": [0, 2], "sources": ["ab", "ec"], "targets": ["eee", "ffff"]},
             "eeecd")],
    source="new_p")


# ===========================================================================
# 18. Capacity to Ship Packages Within D Days
# ===========================================================================
add("capacity-to-ship-packages-within-d-days", "Capacity to Ship Packages Within D Days",
    "medium", ["array", "binary-search"], "shipWithinDays",
    [("weights", "int[]"), ("days", "int")], "int",
    """
Packages with `weights` must ship in order within `days` days; each day's load can't
exceed the ship's capacity. **Return the least capacity that ships everything within
`days` days.**

**Examples**
```
weights = [1,2,3,4,5,6,7,8,9,10], days = 5  ->  15
weights = [3,2,2,4,1,4], days = 3           ->  6
weights = [1,2,3,1,1], days = 4             ->  3
```

**Constraints:** `1 <= days <= len(weights) <= 5*10^4`, `1 <= weights[i] <= 500`.
""",
    """def shipWithinDays(weights, days):
    lo, hi = max(weights), sum(weights)

    def need(cap):
        d, cur = 1, 0
        for w in weights:
            if cur + w > cap:
                d += 1
                cur = w
            else:
                cur += w
        return d

    while lo < hi:
        mid = (lo + hi) // 2
        if need(mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo
""",
    visible=[{"weights": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "days": 5},
             {"weights": [3, 2, 2, 4, 1, 4], "days": 3},
             {"weights": [1, 2, 3, 1, 1], "days": 4}],
    hidden=[{"weights": [5], "days": 1}, {"weights": [1, 1, 1], "days": 3},
            {"weights": [10, 5, 5], "days": 1}, {"weights": [3, 2, 2, 4, 1, 4], "days": 6}],
    gen=lambda r: [(lambda w: {"weights": w, "days": r.randint(1, len(w))})
                   ([r.randint(1, 10) for _ in range(r.randint(1, 8))]) for _ in range(6)],
    brute=_ship_brute,
    checks=[({"weights": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "days": 5}, 15),
            ({"weights": [3, 2, 2, 4, 1, 4], "days": 3}, 6),
            ({"weights": [1, 2, 3, 1, 1], "days": 4}, 3)],
    source="new_p")


# ===========================================================================
# 19. Tiling a Rectangle with the Fewest Squares
# ===========================================================================
add("tiling-a-rectangle-with-the-fewest-squares",
    "Tiling a Rectangle with the Fewest Squares", "hard",
    ["dynamic-programming", "backtracking"], "tilingRectangle",
    [("n", "int"), ("m", "int")], "int",
    """
**Return the minimum number of integer-sided squares that exactly tile an `n x m`
rectangle.**

**Examples**
```
n = 2, m = 3   ->  3
n = 5, m = 8   ->  5
n = 11, m = 13 ->  6
```

**Constraints:** `1 <= n, m <= 13`.
""",
    """def tilingRectangle(n, m):
    best = [n * m]
    heights = [0] * m

    def dfs(count):
        if count >= best[0]:
            return
        min_h = min(heights)
        if min_h == n:
            best[0] = min(best[0], count)
            return
        start = heights.index(min_h)
        max_possible = min(m - start, n - min_h)
        for s in range(max_possible, 0, -1):
            if all(heights[start + t] == min_h for t in range(s)):
                for t in range(s):
                    heights[start + t] += s
                dfs(count + 1)
                for t in range(s):
                    heights[start + t] -= s

    dfs(0)
    return best[0]
""",
    visible=[{"n": 2, "m": 3}, {"n": 2, "m": 4}, {"n": 3, "m": 3}],
    hidden=[{"n": 1, "m": 1}, {"n": 3, "m": 6}, {"n": 4, "m": 4}, {"n": 5, "m": 5}],
    gen=lambda r: [(lambda: {"n": r.randint(1, 5), "m": r.randint(1, 5)})() for _ in range(6)],
    brute=_tiling_brute,
    checks=[({"n": 2, "m": 3}, 3), ({"n": 5, "m": 8}, 5), ({"n": 11, "m": 13}, 6),
            ({"n": 1, "m": 1}, 1), ({"n": 3, "m": 3}, 1), ({"n": 2, "m": 4}, 2)],
    source="new_p")
