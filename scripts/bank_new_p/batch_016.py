"""Batch 016 of the new_p.txt import (19 problems).

One entry was dropped as a duplicate under a different slug (see `_skips.py`):
`palindrome-partitioning-ii` (== `palindrome-partition-min-cuts`).
"""
from scripts.build_bank import add, ilist, sstr  # noqa: F401

MOD = 10 ** 9 + 7


# --------------------------- brute / reference helpers ---------------------
def _painth3_brute(houses, cost, m, n, target):
    from itertools import product
    free = [i for i in range(m) if houses[i] == 0]
    best = float('inf')
    for combo in product(range(1, n + 1), repeat=len(free)):
        coloring = houses[:]
        ci = 0
        total = 0
        for i in free:
            coloring[i] = combo[ci]
            total += cost[i][combo[ci] - 1]
            ci += 1
        groups = 1
        for i in range(1, m):
            if coloring[i] != coloring[i - 1]:
                groups += 1
        if groups == target:
            best = min(best, total)
    return best if best != float('inf') else -1


def _maxswap_brute(num):
    s = list(str(num))
    best = num
    for i in range(len(s)):
        for j in range(i + 1, len(s)):
            t = s[:]
            t[i], t[j] = t[j], t[i]
            best = max(best, int("".join(t)))
    return best


def _printable_brute(targetGrid):
    m, n = len(targetGrid), len(targetGrid[0])
    grid = [row[:] for row in targetGrid]
    colors = set(v for row in targetGrid for v in row)
    removed = set()
    changed = True
    while colors - removed and changed:
        changed = False
        for c in list(colors - removed):
            rows = [i for i in range(m) for j in range(n) if targetGrid[i][j] == c]
            cols = [j for i in range(m) for j in range(n) if targetGrid[i][j] == c]
            r1, r2, c1, c2 = min(rows), max(rows), min(cols), max(cols)
            ok = all(grid[i][j] in (c, 0)
                     for i in range(r1, r2 + 1) for j in range(c1, c2 + 1))
            if ok:
                for i in range(r1, r2 + 1):
                    for j in range(c1, c2 + 1):
                        grid[i][j] = 0
                removed.add(c)
                changed = True
    return len(removed) == len(colors)


def _frog_brute(stones):
    stone_set = set(stones)
    last = stones[-1]
    from functools import lru_cache

    @lru_cache(None)
    def dfs(pos, k):
        if pos == last:
            return True
        for step in (k - 1, k, k + 1):
            if step > 0 and pos + step in stone_set:
                if dfs(pos + step, step):
                    return True
        return False

    return dfs(stones[0], 0)


def _minsub_brute(nums, p):
    total = sum(nums)
    if total % p == 0:
        return 0
    n = len(nums)
    best = n
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if (total - s) % p == 0:
                best = min(best, j - i + 1)
    return best if best < n else -1


def _nesting_brute(A):
    n = len(A)
    best = 0
    for i in range(n):
        s = set()
        j = i
        while j not in s:
            s.add(j)
            j = A[j]
        best = max(best, len(s))
    return best


def _inform_brute(n, headID, manager, informTime):
    from collections import defaultdict
    children = defaultdict(list)
    for i, mgr in enumerate(manager):
        if mgr != -1:
            children[mgr].append(i)

    def dfs(node):
        if not children[node]:
            return 0
        return informTime[node] + max(dfs(c) for c in children[node])

    return dfs(headID)


def _servers_brute(grid):
    m, n = len(grid), len(grid[0])
    res = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                if any(grid[i][k] == 1 for k in range(n) if k != j) or \
                   any(grid[k][j] == 1 for k in range(m) if k != i):
                    res += 1
    return res


def _revsub_brute(nums):
    def value(a):
        return sum(abs(a[i] - a[i + 1]) for i in range(len(a) - 1))
    n = len(nums)
    best = value(nums)
    for i in range(n):
        for j in range(i, n):
            best = max(best, value(nums[:i] + nums[i:j + 1][::-1] + nums[j + 1:]))
    return best


def _minops_brute(n):
    arr = [2 * i + 1 for i in range(n)]
    mean = sum(arr) // n
    return sum(x - mean for x in arr if x > mean)


def _fourdiv_brute(nums):
    total = 0
    for x in nums:
        divs = [d for d in range(1, x + 1) if x % d == 0]
        if len(divs) == 4:
            total += sum(divs)
    return total


def _frac_brute(numerator, denominator):
    if numerator == 0:
        return "0"
    sign = "-" if (numerator < 0) != (denominator < 0) else ""
    num, den = abs(numerator), abs(denominator)
    intpart, rem = num // den, num % den
    if rem == 0:
        return sign + str(intpart)
    digits = []
    seen = {}
    rep_start = -1
    while rem != 0:
        if rem in seen:
            rep_start = seen[rem]
            break
        seen[rem] = len(digits)
        rem *= 10
        digits.append(str(rem // den))
        rem %= den
    if rep_start == -1:
        return sign + str(intpart) + "." + "".join(digits)
    nonrep = "".join(digits[:rep_start])
    rep = "".join(digits[rep_start:])
    return sign + str(intpart) + "." + nonrep + "(" + rep + ")"


def _validtree_brute(n, leftChild, rightChild):
    indeg = [0] * n
    edges = 0
    for i in range(n):
        for c in (leftChild[i], rightChild[i]):
            if c != -1:
                indeg[c] += 1
                edges += 1
    if any(d > 1 for d in indeg):
        return False
    if edges != n - 1:
        return False
    if sum(1 for d in indeg if d == 0) != 1:
        return False
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for c in (leftChild[i], rightChild[i]):
            if c != -1:
                ra, rb = find(i), find(c)
                if ra == rb:
                    return False
                parent[ra] = rb
    return len(set(find(i) for i in range(n))) == 1


def _3summulti_brute(A, target):
    n = len(A)
    res = 0
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if A[i] + A[j] + A[k] == target:
                    res += 1
    return res % MOD


def _jump3_brute(arr, start):
    n = len(arr)
    seen = set()

    def dfs(i):
        if i < 0 or i >= n or i in seen:
            return False
        if arr[i] == 0:
            return True
        seen.add(i)
        return dfs(i + arr[i]) or dfs(i - arr[i])

    return dfs(start)


def _triplets_brute(arr):
    n = len(arr)
    res = 0
    for i in range(n):
        for j in range(i + 1, n):
            a = 0
            for t in range(i, j):
                a ^= arr[t]
            for k in range(j, n):
                b = 0
                for t in range(j, k + 1):
                    b ^= arr[t]
                if a == b:
                    res += 1
    return res


def _scorewords_brute(words, letters, score):
    from collections import Counter
    avail = Counter(letters)
    n = len(words)
    best = 0
    for mask in range(1 << n):
        need = Counter()
        for i in range(n):
            if mask >> i & 1:
                need += Counter(words[i])
        if all(avail[c] >= cnt for c, cnt in need.items()):
            best = max(best, sum(score[ord(c) - 97] * cnt for c, cnt in need.items()))
    return best


def _rangesum_brute(nums, n, left, right):
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + nums[i]
    sums = sorted(pre[j] - pre[i] for i in range(n) for j in range(i + 1, n + 1))
    return sum(sums[left - 1:right]) % MOD


# --------------------------- gen helpers -----------------------------------
def _painth3_gen(r):
    m, n = r.randint(1, 4), r.randint(1, 3)
    houses = [r.choice([0] + list(range(1, n + 1))) for _ in range(m)]
    cost = [[r.randint(1, 9) for _ in range(n)] for _ in range(m)]
    return {"houses": houses, "cost": cost, "m": m, "n": n, "target": r.randint(1, m)}


def _printable_gen(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    return {"targetGrid": [[r.randint(1, 4) for _ in range(n)] for _ in range(m)]}


def _frog_gen(r):
    pos = 0
    stones = [0]
    for _ in range(r.randint(1, 8)):
        pos += r.randint(1, 4)
        stones.append(pos)
    return {"stones": stones}


def _nesting_gen(r):
    n = r.randint(1, 10)
    a = list(range(n))
    r.shuffle(a)
    return {"A": a}


def _inform_gen(r):
    n = r.randint(1, 8)
    headID = r.randint(0, n - 1)
    manager = [-1] * n
    nodes = [headID]
    for x in range(n):
        if x == headID:
            continue
        p = r.choice(nodes)
        manager[x] = p
        nodes.append(x)
    has_child = set(manager[i] for i in range(n) if manager[i] != -1)
    informTime = [r.randint(0, 10) if i in has_child else 0 for i in range(n)]
    return {"n": n, "headID": headID, "manager": manager, "informTime": informTime}


def _servers_gen(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    return {"grid": [[r.randint(0, 1) for _ in range(n)] for _ in range(m)]}


def _validtree_gen(r):
    n = r.randint(1, 6)
    left = [-1] * n
    right = [-1] * n
    for i in range(n):
        if r.random() < 0.5:
            left[i] = r.randint(-1, n - 1)
        if r.random() < 0.5:
            right[i] = r.randint(-1, n - 1)
    return {"n": n, "leftChild": left, "rightChild": right}


def _scorewords_gen(r):
    nw = r.randint(1, 6)
    words = [sstr(r, 1, 4, "abcd") for _ in range(nw)]
    letters = [r.choice("abcd") for _ in range(r.randint(1, 10))]
    score = [r.randint(0, 5) if i < 4 else 0 for i in range(26)]
    return {"words": words, "letters": letters, "score": score}


def _rangesum_gen(r):
    n = r.randint(1, 8)
    nums = [r.randint(1, 10) for _ in range(n)]
    total = n * (n + 1) // 2
    left = r.randint(1, total)
    right = r.randint(left, total)
    return {"nums": nums, "n": n, "left": left, "right": right}


# ===========================================================================
# 1. Paint House III
# ===========================================================================
add("paint-house-iii", "Paint House III", "hard",
    ["array", "dynamic-programming"], "minCost",
    [("houses", "int[]"), ("cost", "int[][]"), ("m", "int"), ("n", "int"), ("target", "int")],
    "int",
    """
A row of `m` houses each needs one of `n` colors (`1..n`). `houses[i]` is the color of
house `i` (`0` = unpainted, must be painted; non-zero = already painted, keep it).
`cost[i][j]` is the cost to paint house `i` color `j+1`. A *neighborhood* is a maximal
run of equal colors. **Return the minimum total painting cost so there are exactly
`target` neighborhoods, or `-1` if impossible.**

**Examples**
```
houses=[0,0,0,0,0], cost=[[1,10],[10,1],[10,1],[1,10],[5,1]], m=5, n=2, target=3  ->  9
houses=[3,1,2,3], cost=[[1,1,1],[1,1,1],[1,1,1],[1,1,1]], m=4, n=3, target=3      ->  -1
```

**Constraints:** `1 <= m <= 100`, `1 <= n <= 20`, `1 <= target <= m`, `0 <= houses[i] <= n`,
`1 <= cost[i][j] <= 10^4`.
""",
    """def minCost(houses, cost, m, n, target):
    from functools import lru_cache
    INF = float('inf')

    @lru_cache(None)
    def dp(i, prev, groups):
        if groups > target:
            return INF
        if i == m:
            return 0 if groups == target else INF
        if houses[i] != 0:
            c = houses[i]
            return dp(i + 1, c, groups + (1 if c != prev else 0))
        best = INF
        for c in range(1, n + 1):
            best = min(best, cost[i][c - 1] +
                       dp(i + 1, c, groups + (1 if c != prev else 0)))
        return best

    res = dp(0, 0, 0)
    return res if res != INF else -1
""",
    visible=[{"houses": [0, 0, 0, 0, 0], "cost": [[1, 10], [10, 1], [10, 1], [1, 10], [5, 1]],
              "m": 5, "n": 2, "target": 3},
             {"houses": [0, 2, 1, 2, 0], "cost": [[1, 10], [10, 1], [10, 1], [1, 10], [5, 1]],
              "m": 5, "n": 2, "target": 3},
             {"houses": [3, 1, 2, 3], "cost": [[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]],
              "m": 4, "n": 3, "target": 3}],
    hidden=[{"houses": [0, 0, 0, 0, 0], "cost": [[1, 10], [10, 1], [1, 10], [10, 1], [1, 10]],
             "m": 5, "n": 2, "target": 5},
            {"houses": [1], "cost": [[5]], "m": 1, "n": 1, "target": 1},
            {"houses": [0], "cost": [[3, 7]], "m": 1, "n": 2, "target": 1},
            {"houses": [2, 2, 2], "cost": [[1, 1], [1, 1], [1, 1]], "m": 3, "n": 2, "target": 2}],
    gen=lambda r: [_painth3_gen(r) for _ in range(6)],
    brute=_painth3_brute,
    checks=[({"houses": [0, 0, 0, 0, 0], "cost": [[1, 10], [10, 1], [10, 1], [1, 10], [5, 1]],
              "m": 5, "n": 2, "target": 3}, 9),
            ({"houses": [0, 2, 1, 2, 0], "cost": [[1, 10], [10, 1], [10, 1], [1, 10], [5, 1]],
              "m": 5, "n": 2, "target": 3}, 11),
            ({"houses": [0, 0, 0, 0, 0], "cost": [[1, 10], [10, 1], [1, 10], [10, 1], [1, 10]],
              "m": 5, "n": 2, "target": 5}, 5),
            ({"houses": [3, 1, 2, 3], "cost": [[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]],
              "m": 4, "n": 3, "target": 3}, -1)],
    source="new_p")


# ===========================================================================
# 2. Maximum Swap
# ===========================================================================
add("maximum-swap", "Maximum Swap", "medium",
    ["math", "greedy"], "maximumSwap", [("num", "int")], "int",
    """
Given a non-negative integer `num`, swap two of its digits **at most once** to make
the largest possible value. **Return that value.**

**Examples**
```
num = 2736  ->  7236
num = 9973  ->  9973
```

**Constraints:** `0 <= num <= 10^8`.
""",
    """def maximumSwap(num):
    digits = list(str(num))
    last = {int(d): i for i, d in enumerate(digits)}
    for i, d in enumerate(digits):
        for x in range(9, int(d), -1):
            if last.get(x, -1) > i:
                j = last[x]
                digits[i], digits[j] = digits[j], digits[i]
                return int("".join(digits))
    return num
""",
    visible=[{"num": 2736}, {"num": 9973}],
    hidden=[{"num": 0}, {"num": 1993}, {"num": 98368}, {"num": 10}, {"num": 100000}],
    gen=lambda r: [{"num": r.randint(0, 100000)} for _ in range(8)],
    brute=_maxswap_brute,
    checks=[({"num": 2736}, 7236), ({"num": 9973}, 9973), ({"num": 0}, 0),
            ({"num": 1993}, 9913), ({"num": 98368}, 98863)],
    source="new_p")


# ===========================================================================
# 3. Strange Printer II
# ===========================================================================
add("strange-printer-ii", "Strange Printer II", "hard",
    ["array", "graph", "topological-sort", "matrix"], "isPrintable",
    [("targetGrid", "int[][]")], "bool",
    """
A printer prints solid rectangles of a single color (covering whatever was there), and
each color may be used at most once. **Return `true` if `targetGrid` can be produced.**

**Examples**
```
[[1,1,1,1],[1,2,2,1],[1,2,2,1],[1,1,1,1]]  ->  true
[[1,2,1],[2,1,2],[1,2,1]]                   ->  false
```

**Constraints:** `1 <= m, n <= 60`, `1 <= targetGrid[r][c] <= 60`.
""",
    """def isPrintable(targetGrid):
    m, n = len(targetGrid), len(targetGrid[0])
    colors = set(v for row in targetGrid for v in row)
    box = {}
    for c in colors:
        rs = [i for i in range(m) for j in range(n) if targetGrid[i][j] == c]
        cs = [j for i in range(m) for j in range(n) if targetGrid[i][j] == c]
        box[c] = (min(rs), max(rs), min(cs), max(cs))
    graph = {c: set() for c in colors}
    for c in colors:
        r1, r2, c1, c2 = box[c]
        for i in range(r1, r2 + 1):
            for j in range(c1, c2 + 1):
                if targetGrid[i][j] != c:
                    graph[c].add(targetGrid[i][j])
    state = {}

    def dfs(c):
        state[c] = 1
        for nb in graph[c]:
            if state.get(nb, 0) == 1:
                return False
            if state.get(nb, 0) == 0 and not dfs(nb):
                return False
        state[c] = 2
        return True

    return all(dfs(c) for c in colors if state.get(c, 0) == 0)
""",
    visible=[{"targetGrid": [[1, 1, 1, 1], [1, 2, 2, 1], [1, 2, 2, 1], [1, 1, 1, 1]]},
             {"targetGrid": [[1, 2, 1], [2, 1, 2], [1, 2, 1]]}],
    hidden=[{"targetGrid": [[1, 1, 1, 1], [1, 1, 3, 3], [1, 1, 3, 4], [5, 5, 1, 4]]},
            {"targetGrid": [[1, 1, 1], [3, 1, 3]]}, {"targetGrid": [[1]]},
            {"targetGrid": [[1, 2], [2, 1]]}],
    gen=lambda r: [_printable_gen(r) for _ in range(8)],
    brute=_printable_brute,
    checks=[({"targetGrid": [[1, 1, 1, 1], [1, 2, 2, 1], [1, 2, 2, 1], [1, 1, 1, 1]]}, True),
            ({"targetGrid": [[1, 1, 1, 1], [1, 1, 3, 3], [1, 1, 3, 4], [5, 5, 1, 4]]}, True),
            ({"targetGrid": [[1, 2, 1], [2, 1, 2], [1, 2, 1]]}, False),
            ({"targetGrid": [[1, 1, 1], [3, 1, 3]]}, False)],
    source="new_p")


# ===========================================================================
# 4. Frog Jump
# ===========================================================================
add("frog-jump", "Frog Jump", "hard",
    ["array", "dynamic-programming", "hash-table"], "canCross", [("stones", "int[]")], "bool",
    """
A frog crosses a river on stones at the given sorted positions, starting on the first
stone with a mandatory first jump of `1`. If the last jump was `k`, the next must be
`k-1`, `k`, or `k+1` (forward only) and must land on a stone. **Return `true` if the
frog can reach the last stone.**

**Examples**
```
stones = [0,1,3,5,6,8,12,17]  ->  true
stones = [0,1,2,3,4,8,9,11]   ->  false
```

**Constraints:** `2 <= len(stones) <= 2000`, first stone is `0`, strictly increasing.
""",
    """def canCross(stones):
    stone_set = set(stones)
    from collections import defaultdict
    dp = defaultdict(set)
    dp[stones[0]].add(0)
    for s in stones:
        for k in dp[s]:
            for step in (k - 1, k, k + 1):
                if step > 0 and s + step in stone_set:
                    dp[s + step].add(step)
    return len(dp[stones[-1]]) > 0
""",
    visible=[{"stones": [0, 1, 3, 5, 6, 8, 12, 17]}, {"stones": [0, 1, 2, 3, 4, 8, 9, 11]}],
    hidden=[{"stones": [0, 1]}, {"stones": [0, 2]}, {"stones": [0, 1, 3, 6, 10, 13, 14]},
            {"stones": [0, 1, 3, 4, 5, 7, 9, 10, 12]}],
    gen=lambda r: [_frog_gen(r) for _ in range(8)],
    brute=_frog_brute,
    checks=[({"stones": [0, 1, 3, 5, 6, 8, 12, 17]}, True),
            ({"stones": [0, 1, 2, 3, 4, 8, 9, 11]}, False), ({"stones": [0, 1]}, True),
            ({"stones": [0, 2]}, False)],
    source="new_p")


# ===========================================================================
# 5. Make Sum Divisible by P
# ===========================================================================
add("make-sum-divisible-by-p", "Make Sum Divisible by P", "medium",
    ["array", "hash-table", "prefix-sum"], "minSubarray",
    [("nums", "int[]"), ("p", "int")], "int",
    """
Remove the **smallest contiguous subarray** (possibly empty, but not the whole array)
so that the sum of the remaining elements is divisible by `p`. **Return the length of
that subarray, or `-1` if impossible.**

**Examples**
```
nums = [3,1,4,2], p = 6  ->  1
nums = [6,3,5,2], p = 9  ->  2
nums = [1,2,3], p = 3    ->  0
nums = [1,2,3], p = 7    ->  -1
```

**Constraints:** `1 <= len(nums) <= 10^5`, `1 <= nums[i] <= 10^9`, `1 <= p <= 10^9`.
""",
    """def minSubarray(nums, p):
    total = sum(nums) % p
    if total == 0:
        return 0
    n = len(nums)
    pre = 0
    last = {0: -1}
    res = n
    for i, x in enumerate(nums):
        pre = (pre + x) % p
        need = (pre - total) % p
        if need in last:
            res = min(res, i - last[need])
        last[pre] = i
    return res if res < n else -1
""",
    visible=[{"nums": [3, 1, 4, 2], "p": 6}, {"nums": [6, 3, 5, 2], "p": 9},
             {"nums": [1, 2, 3], "p": 3}, {"nums": [1, 2, 3], "p": 7}],
    hidden=[{"nums": [1000000000, 1000000000, 1000000000], "p": 3}, {"nums": [1], "p": 2},
            {"nums": [4, 4, 2], "p": 7}, {"nums": [5, 5, 5, 5], "p": 5}],
    gen=lambda r: [{"nums": [r.randint(1, 10) for _ in range(r.randint(1, 10))],
                    "p": r.randint(1, 6)} for _ in range(8)],
    brute=_minsub_brute,
    checks=[({"nums": [3, 1, 4, 2], "p": 6}, 1), ({"nums": [6, 3, 5, 2], "p": 9}, 2),
            ({"nums": [1, 2, 3], "p": 3}, 0), ({"nums": [1, 2, 3], "p": 7}, -1),
            ({"nums": [1000000000, 1000000000, 1000000000], "p": 3}, 0)],
    source="new_p")


# ===========================================================================
# 6. Array Nesting
# ===========================================================================
add("array-nesting", "Array Nesting", "medium",
    ["array", "depth-first-search"], "arrayNesting", [("A", "int[]")], "int",
    """
`A` is a permutation of `0..N-1`. Starting from index `i`, the set `S` collects
`A[i], A[A[i]], A[A[A[i]]], ...` until a value repeats. **Return the length of the
longest such set over all starting indices.**

**Example**
```
A = [5,4,0,3,1,6,2]  ->  4
```

**Constraints:** `1 <= N <= 2*10^4`, `A` is a permutation of `0..N-1`.
""",
    """def arrayNesting(A):
    seen = [False] * len(A)
    best = 0
    for i in range(len(A)):
        if not seen[i]:
            cnt = 0
            j = i
            while not seen[j]:
                seen[j] = True
                j = A[j]
                cnt += 1
            best = max(best, cnt)
    return best
""",
    visible=[{"A": [5, 4, 0, 3, 1, 6, 2]}],
    hidden=[{"A": [0, 1, 2]}, {"A": [1, 0]}, {"A": [0]}, {"A": [2, 0, 1]},
            {"A": [1, 2, 3, 4, 0]}],
    gen=lambda r: [_nesting_gen(r) for _ in range(8)],
    brute=_nesting_brute,
    checks=[({"A": [5, 4, 0, 3, 1, 6, 2]}, 4), ({"A": [0, 1, 2]}, 1), ({"A": [1, 0]}, 2),
            ({"A": [1, 2, 3, 4, 0]}, 5)],
    source="new_p")


# ===========================================================================
# 7. Time Needed to Inform All Employees
# ===========================================================================
add("time-needed-to-inform-all-employees", "Time Needed to Inform All Employees", "medium",
    ["tree", "depth-first-search", "breadth-first-search"], "numOfMinutes",
    [("n", "int"), ("headID", "int"), ("manager", "int[]"), ("informTime", "int[]")], "int",
    """
A company tree has `n` employees; `manager[i]` is `i`'s manager (`-1` for the head).
Employee `i` takes `informTime[i]` minutes to inform all direct subordinates. **Return
the number of minutes until everyone is informed**, starting from `headID`.

**Examples**
```
n=6, headID=2, manager=[2,2,-1,2,2,2], informTime=[0,0,1,0,0,0]  ->  1
n=7, headID=6, manager=[1,2,3,4,5,6,-1], informTime=[0,6,5,4,3,2,1]  ->  21
```

**Constraints:** `1 <= n <= 10^5`, valid tree, `0 <= informTime[i] <= 1000`.
""",
    """def numOfMinutes(n, headID, manager, informTime):
    from collections import defaultdict, deque
    children = defaultdict(list)
    for i, m in enumerate(manager):
        if m != -1:
            children[m].append(i)
    best = 0
    q = deque([(headID, 0)])
    while q:
        node, t = q.popleft()
        best = max(best, t)
        for c in children[node]:
            q.append((c, t + informTime[node]))
    return best
""",
    visible=[{"n": 6, "headID": 2, "manager": [2, 2, -1, 2, 2, 2],
              "informTime": [0, 0, 1, 0, 0, 0]},
             {"n": 7, "headID": 6, "manager": [1, 2, 3, 4, 5, 6, -1],
              "informTime": [0, 6, 5, 4, 3, 2, 1]}],
    hidden=[{"n": 1, "headID": 0, "manager": [-1], "informTime": [0]},
            {"n": 4, "headID": 2, "manager": [3, 3, -1, 2], "informTime": [0, 0, 162, 914]},
            {"n": 15, "headID": 0, "manager": [-1, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6],
             "informTime": [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]}],
    gen=lambda r: [_inform_gen(r) for _ in range(8)],
    brute=_inform_brute,
    checks=[({"n": 6, "headID": 2, "manager": [2, 2, -1, 2, 2, 2],
              "informTime": [0, 0, 1, 0, 0, 0]}, 1),
            ({"n": 7, "headID": 6, "manager": [1, 2, 3, 4, 5, 6, -1],
              "informTime": [0, 6, 5, 4, 3, 2, 1]}, 21),
            ({"n": 1, "headID": 0, "manager": [-1], "informTime": [0]}, 0),
            ({"n": 4, "headID": 2, "manager": [3, 3, -1, 2], "informTime": [0, 0, 162, 914]}, 1076)],
    source="new_p")


# ===========================================================================
# 8. Count Servers that Communicate
# ===========================================================================
add("count-servers-that-communicate", "Count Servers that Communicate", "medium",
    ["array", "matrix", "counting"], "countServers", [("grid", "int[][]")], "int",
    """
`grid[i][j] == 1` marks a server. Two servers communicate if they share a row or a
column. **Return the number of servers that communicate with at least one other server.**

**Examples**
```
[[1,0],[0,1]]  ->  0
[[1,0],[1,1]]  ->  3
```

**Constraints:** `1 <= m, n <= 250`, `grid[i][j]` is `0` or `1`.
""",
    """def countServers(grid):
    m, n = len(grid), len(grid[0])
    row_count = [sum(r) for r in grid]
    col_count = [sum(grid[i][j] for i in range(m)) for j in range(n)]
    res = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1 and (row_count[i] > 1 or col_count[j] > 1):
                res += 1
    return res
""",
    visible=[{"grid": [[1, 0], [0, 1]]}, {"grid": [[1, 0], [1, 1]]},
             {"grid": [[1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 0, 1]]}],
    hidden=[{"grid": [[1]]}, {"grid": [[0]]}, {"grid": [[1, 1, 1]]}, {"grid": [[1], [1], [1]]},
            {"grid": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}],
    gen=lambda r: [_servers_gen(r) for _ in range(8)],
    brute=_servers_brute,
    checks=[({"grid": [[1, 0], [0, 1]]}, 0), ({"grid": [[1, 0], [1, 1]]}, 3),
            ({"grid": [[1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 0, 1]]}, 4)],
    source="new_p")


# ===========================================================================
# 9. Reverse Subarray To Maximize Array Value
# ===========================================================================
add("reverse-subarray-to-maximize-array-value", "Reverse Subarray to Maximize Array Value",
    "hard", ["array", "math", "greedy"], "maxValueAfterReverse", [("nums", "int[]")], "int",
    """
The value of an array is `sum(|nums[i] - nums[i+1]|)`. You may reverse **one**
subarray at most once. **Return the maximum achievable array value.**

**Examples**
```
nums = [2,3,1,5,4]        ->  10
nums = [2,4,9,24,2,1,10]  ->  68
```

**Constraints:** `1 <= len(nums) <= 3*10^4`, `-10^5 <= nums[i] <= 10^5`.
""",
    """def maxValueAfterReverse(nums):
    n = len(nums)
    total = sum(abs(nums[i] - nums[i + 1]) for i in range(n - 1))
    best = 0
    for j in range(n - 1):
        best = max(best, abs(nums[0] - nums[j + 1]) - abs(nums[j] - nums[j + 1]))
        best = max(best, abs(nums[n - 1] - nums[j]) - abs(nums[j] - nums[j + 1]))
    hi, lo = float('-inf'), float('inf')
    for i in range(n - 1):
        a, b = nums[i], nums[i + 1]
        hi = max(hi, min(a, b))
        lo = min(lo, max(a, b))
    best = max(best, 2 * (hi - lo))
    return total + best
""",
    visible=[{"nums": [2, 3, 1, 5, 4]}, {"nums": [2, 4, 9, 24, 2, 1, 10]}],
    hidden=[{"nums": [1]}, {"nums": [1, 2]}, {"nums": [5, 1, 5]}, {"nums": [3, 1, 4, 1, 5, 9]},
            {"nums": [-1, -5, 3, -2]}],
    gen=lambda r: [{"nums": [r.randint(-10, 10) for _ in range(r.randint(1, 10))]}
                   for _ in range(8)],
    brute=_revsub_brute,
    checks=[({"nums": [2, 3, 1, 5, 4]}, 10), ({"nums": [2, 4, 9, 24, 2, 1, 10]}, 68),
            ({"nums": [1]}, 0), ({"nums": [1, 2]}, 1)],
    source="new_p")


# ===========================================================================
# 10. Minimum Operations to Make Array Equal
# ===========================================================================
add("minimum-operations-to-make-array-equal", "Minimum Operations to Make Array Equal",
    "medium", ["math"], "minOperations", [("n", "int")], "int",
    """
For the array `arr` where `arr[i] = 2*i + 1` (`0 <= i < n`), one operation subtracts
`1` from one element and adds `1` to another. **Return the minimum number of operations
to make all elements equal.**

**Examples**
```
n = 3  ->  2    (arr = [1,3,5] -> [3,3,3])
n = 6  ->  9
```

**Constraints:** `1 <= n <= 10^4`.
""",
    """def minOperations(n):
    res = 0
    for i in range(n // 2):
        res += n - (2 * i + 1)
    return res
""",
    visible=[{"n": 3}, {"n": 6}],
    hidden=[{"n": 1}, {"n": 2}, {"n": 4}, {"n": 5}, {"n": 100}],
    gen=lambda r: [{"n": r.randint(1, 200)} for _ in range(8)],
    brute=_minops_brute,
    checks=[({"n": 3}, 2), ({"n": 6}, 9), ({"n": 1}, 0), ({"n": 4}, 4)],
    source="new_p")


# ===========================================================================
# 11. Masking Personal Information
# ===========================================================================
add("masking-personal-information", "Masking Personal Information", "medium",
    ["string"], "maskPII", [("S", "string")], "string",
    """
Mask a personal-information string. **Email** (`name1@name2.name3`): lowercase
everything and replace the middle of `name1` with exactly `5` asterisks
(`l*****e@...`). **Phone** (digits plus `+ - ( ) ` and spaces, 10-13 digits): keep
only the last `4` digits as `***-***-1111`; if there is a country code of `k` digits,
prefix `+` then `k` stars then `-`. **Return the masked string.**

**Examples**
```
"LeetCode@LeetCode.com"  ->  "l*****e@leetcode.com"
"1(234)567-890"          ->  "***-***-7890"
"86-(10)12345678"        ->  "+**-***-***-5678"
```

**Constraints:** `len(S) <= 40`; a valid email or phone number.
""",
    """def maskPII(S):
    if '@' in S:
        name, domain = S.split('@')
        name = name.lower()
        return name[0] + "*****" + name[-1] + "@" + domain.lower()
    digits = [c for c in S if c.isdigit()]
    local = "".join(digits[-10:])
    country = digits[:-10]
    local_masked = "***-***-" + local[-4:]
    if country:
        return "+" + "*" * len(country) + "-" + local_masked
    return local_masked
""",
    visible=[{"S": "LeetCode@LeetCode.com"}, {"S": "1(234)567-890"}, {"S": "86-(10)12345678"}],
    hidden=[{"S": "AB@qq.com"}, {"S": "Test@Test.com"}, {"S": "123 456 7890"},
            {"S": "+111 111 111 1111"}, {"S": "+1-234-567-8901"}],
    checks=[({"S": "LeetCode@LeetCode.com"}, "l*****e@leetcode.com"),
            ({"S": "AB@qq.com"}, "a*****b@qq.com"),
            ({"S": "1(234)567-890"}, "***-***-7890"),
            ({"S": "86-(10)12345678"}, "+**-***-***-5678"),
            ({"S": "+1-234-567-8901"}, "+*-***-***-8901")],
    source="new_p")


# ===========================================================================
# 12. Four Divisors
# ===========================================================================
add("four-divisors", "Four Divisors", "medium",
    ["array", "math"], "sumFourDivisors", [("nums", "int[]")], "int",
    """
**Return the sum of the divisors of those integers in `nums` that have exactly four
divisors** (sum over all such integers; `0` if none).

**Example**
```
nums = [21,4,7]  ->  32    (21 has divisors 1,3,7,21)
```

**Constraints:** `1 <= len(nums) <= 10^4`, `1 <= nums[i] <= 10^5`.
""",
    """def sumFourDivisors(nums):
    def four_sum(x):
        divs = []
        i = 1
        while i * i <= x:
            if x % i == 0:
                divs.append(i)
                if i != x // i:
                    divs.append(x // i)
                if len(divs) > 4:
                    return 0
            i += 1
        return sum(divs) if len(divs) == 4 else 0
    return sum(four_sum(x) for x in nums)
""",
    visible=[{"nums": [21, 4, 7]}],
    hidden=[{"nums": [6]}, {"nums": [1, 2, 3, 4, 5]}, {"nums": [8]}, {"nums": [10, 15]},
            {"nums": [1]}],
    gen=lambda r: [{"nums": [r.randint(1, 50) for _ in range(r.randint(1, 8))]}
                   for _ in range(8)],
    brute=_fourdiv_brute,
    checks=[({"nums": [21, 4, 7]}, 32), ({"nums": [6]}, 12), ({"nums": [1, 2, 3, 4, 5]}, 0),
            ({"nums": [10, 15]}, 18 + 24)],
    source="new_p")


# ===========================================================================
# 13. Fraction to Recurring Decimal
# ===========================================================================
add("fraction-to-recurring-decimal", "Fraction to Recurring Decimal", "medium",
    ["math", "hash-table", "string"], "fractionToDecimal",
    [("numerator", "int"), ("denominator", "int")], "string",
    """
**Return the decimal representation of `numerator/denominator` as a string**, enclosing
any repeating fractional part in parentheses.

**Examples**
```
numerator = 1, denominator = 2  ->  "0.5"
numerator = 2, denominator = 1  ->  "2"
numerator = 2, denominator = 3  ->  "0.(6)"
```

**Constraints:** both fit in 32-bit signed range, `denominator != 0`.
""",
    """def fractionToDecimal(numerator, denominator):
    if numerator == 0:
        return "0"
    res = []
    if (numerator < 0) != (denominator < 0):
        res.append("-")
    num, den = abs(numerator), abs(denominator)
    res.append(str(num // den))
    rem = num % den
    if rem == 0:
        return "".join(res)
    res.append(".")
    seen = {}
    while rem != 0:
        if rem in seen:
            res.insert(seen[rem], "(")
            res.append(")")
            break
        seen[rem] = len(res)
        rem *= 10
        res.append(str(rem // den))
        rem %= den
    return "".join(res)
""",
    visible=[{"numerator": 1, "denominator": 2}, {"numerator": 2, "denominator": 1},
             {"numerator": 2, "denominator": 3}],
    hidden=[{"numerator": 4, "denominator": 333}, {"numerator": -50, "denominator": 8},
            {"numerator": 7, "denominator": 12}, {"numerator": 0, "denominator": 5},
            {"numerator": 1, "denominator": 6}],
    gen=lambda r: [(lambda d: {"numerator": r.randint(-50, 50), "denominator": d})
                   (r.choice([x for x in range(-12, 13) if x != 0])) for _ in range(8)],
    brute=_frac_brute,
    checks=[({"numerator": 1, "denominator": 2}, "0.5"), ({"numerator": 2, "denominator": 1}, "2"),
            ({"numerator": 2, "denominator": 3}, "0.(6)"),
            ({"numerator": 4, "denominator": 333}, "0.(012)"),
            ({"numerator": -50, "denominator": 8}, "-6.25"),
            ({"numerator": 0, "denominator": 5}, "0")],
    source="new_p")


# ===========================================================================
# 14. Validate Binary Tree Nodes
# ===========================================================================
add("validate-binary-tree-nodes", "Validate Binary Tree Nodes", "medium",
    ["tree", "graph", "union-find", "breadth-first-search"], "validateBinaryTreeNodes",
    [("n", "int"), ("leftChild", "int[]"), ("rightChild", "int[]")], "bool",
    """
There are `n` nodes `0..n-1`; node `i` has children `leftChild[i]` and `rightChild[i]`
(`-1` for none). **Return `true` if and only if the nodes form exactly one valid binary
tree** (one root, every other node has exactly one parent, fully connected, no cycle).

**Examples**
```
n=4, leftChild=[1,-1,3,-1], rightChild=[2,-1,-1,-1]  ->  true
n=2, leftChild=[1,0], rightChild=[-1,-1]             ->  false
```

**Constraints:** `1 <= n <= 10^4`, `-1 <= leftChild[i], rightChild[i] <= n-1`.
""",
    """def validateBinaryTreeNodes(n, leftChild, rightChild):
    indeg = [0] * n
    for i in range(n):
        for c in (leftChild[i], rightChild[i]):
            if c != -1:
                indeg[c] += 1
                if indeg[c] > 1:
                    return False
    roots = [i for i in range(n) if indeg[i] == 0]
    if len(roots) != 1:
        return False
    from collections import deque
    seen = {roots[0]}
    q = deque([roots[0]])
    while q:
        node = q.popleft()
        for c in (leftChild[node], rightChild[node]):
            if c != -1:
                if c in seen:
                    return False
                seen.add(c)
                q.append(c)
    return len(seen) == n
""",
    visible=[{"n": 4, "leftChild": [1, -1, 3, -1], "rightChild": [2, -1, -1, -1]},
             {"n": 4, "leftChild": [1, -1, 3, -1], "rightChild": [2, 3, -1, -1]},
             {"n": 2, "leftChild": [1, 0], "rightChild": [-1, -1]}],
    hidden=[{"n": 6, "leftChild": [1, -1, -1, 4, -1, -1], "rightChild": [2, -1, -1, 5, -1, -1]},
            {"n": 1, "leftChild": [-1], "rightChild": [-1]},
            {"n": 3, "leftChild": [1, -1, -1], "rightChild": [-1, 2, -1]},
            {"n": 2, "leftChild": [-1, -1], "rightChild": [-1, -1]}],
    gen=lambda r: [_validtree_gen(r) for _ in range(8)],
    brute=_validtree_brute,
    checks=[({"n": 4, "leftChild": [1, -1, 3, -1], "rightChild": [2, -1, -1, -1]}, True),
            ({"n": 4, "leftChild": [1, -1, 3, -1], "rightChild": [2, 3, -1, -1]}, False),
            ({"n": 2, "leftChild": [1, 0], "rightChild": [-1, -1]}, False),
            ({"n": 6, "leftChild": [1, -1, -1, 4, -1, -1],
              "rightChild": [2, -1, -1, 5, -1, -1]}, False)],
    source="new_p")


# ===========================================================================
# 15. 3Sum With Multiplicity
# ===========================================================================
add("3sum-with-multiplicity", "3Sum With Multiplicity", "medium",
    ["array", "hash-table", "two-pointers", "counting"], "threeSumMulti",
    [("A", "int[]"), ("target", "int")], "int",
    """
**Return the number of index triples `i < j < k` with `A[i] + A[j] + A[k] == target`**,
modulo `10^9 + 7`.

**Examples**
```
A = [1,1,2,2,3,3,4,4,5,5], target = 8  ->  20
A = [1,1,2,2,2,2], target = 5          ->  12
```

**Constraints:** `3 <= len(A) <= 3000`, `0 <= A[i] <= 100`, `0 <= target <= 300`.
""",
    """def threeSumMulti(A, target):
    MOD = 10 ** 9 + 7
    from collections import Counter
    cnt = Counter(A)
    keys = sorted(cnt)
    res = 0
    nk = len(keys)
    for i in range(nk):
        for j in range(i, nk):
            x, y = keys[i], keys[j]
            z = target - x - y
            if z < y or z not in cnt:
                continue
            cz = cnt[z]
            if x == y == z:
                c = cnt[x]
                res += c * (c - 1) * (c - 2) // 6
            elif x == y != z:
                c = cnt[x]
                res += c * (c - 1) // 2 * cz
            elif x != y == z:
                c = cnt[y]
                res += cnt[x] * (c * (c - 1) // 2)
            else:
                res += cnt[x] * cnt[y] * cz
    return res % MOD
""",
    visible=[{"A": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5], "target": 8},
             {"A": [1, 1, 2, 2, 2, 2], "target": 5}],
    hidden=[{"A": [0, 0, 0], "target": 0}, {"A": [1, 1, 1, 1], "target": 3},
            {"A": [2, 2, 2, 2], "target": 6}, {"A": [0, 1, 2, 3, 4], "target": 5},
            {"A": [5, 5, 5], "target": 100}],
    gen=lambda r: [(lambda a: {"A": a, "target": r.randint(0, 20)})
                   ([r.randint(0, 10) for _ in range(r.randint(3, 18))]) for _ in range(8)],
    brute=_3summulti_brute,
    checks=[({"A": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5], "target": 8}, 20),
            ({"A": [1, 1, 2, 2, 2, 2], "target": 5}, 12),
            ({"A": [0, 0, 0], "target": 0}, 1), ({"A": [1, 1, 1, 1], "target": 3}, 4)],
    source="new_p")


# ===========================================================================
# 16. Jump Game III
# ===========================================================================
add("jump-game-iii", "Jump Game III", "medium",
    ["array", "depth-first-search", "breadth-first-search"], "canReach",
    [("arr", "int[]"), ("start", "int")], "bool",
    """
From index `i` you may jump to `i + arr[i]` or `i - arr[i]` (staying in bounds).
**Return `true` if you can reach any index holding value `0`, starting from `start`.**

**Examples**
```
arr = [4,2,3,0,3,1,2], start = 5  ->  true
arr = [3,0,2,1,2], start = 2      ->  false
```

**Constraints:** `1 <= len(arr) <= 5*10^4`, `0 <= arr[i] < len(arr)`, `0 <= start < len(arr)`.
""",
    """def canReach(arr, start):
    from collections import deque
    n = len(arr)
    seen = {start}
    q = deque([start])
    while q:
        i = q.popleft()
        if arr[i] == 0:
            return True
        for ni in (i + arr[i], i - arr[i]):
            if 0 <= ni < n and ni not in seen:
                seen.add(ni)
                q.append(ni)
    return False
""",
    visible=[{"arr": [4, 2, 3, 0, 3, 1, 2], "start": 5}, {"arr": [4, 2, 3, 0, 3, 1, 2], "start": 0},
             {"arr": [3, 0, 2, 1, 2], "start": 2}],
    hidden=[{"arr": [0], "start": 0}, {"arr": [1, 1, 1], "start": 0}, {"arr": [2, 0, 1], "start": 0},
            {"arr": [1, 1, 2], "start": 2}, {"arr": [58, 47, 5], "start": 0}],
    gen=lambda r: [(lambda a: {"arr": a, "start": r.randint(0, len(a) - 1)})
                   ([r.randint(0, max(1, r.randint(0, 6))) for _ in range(r.randint(1, 12))])
                   for _ in range(8)],
    brute=_jump3_brute,
    checks=[({"arr": [4, 2, 3, 0, 3, 1, 2], "start": 5}, True),
            ({"arr": [4, 2, 3, 0, 3, 1, 2], "start": 0}, True),
            ({"arr": [3, 0, 2, 1, 2], "start": 2}, False), ({"arr": [0], "start": 0}, True)],
    source="new_p")


# ===========================================================================
# 17. Count Triplets That Can Form Two Arrays of Equal XOR
# ===========================================================================
add("count-triplets-that-can-form-two-arrays-of-equal-xor",
    "Count Triplets That Can Form Two Arrays of Equal XOR", "medium",
    ["array", "hash-table", "math", "bit-manipulation", "prefix-sum"], "countTriplets",
    [("arr", "int[]")], "int",
    """
Choose `i < j <= k`. Let `a = arr[i] ^ ... ^ arr[j-1]` and `b = arr[j] ^ ... ^ arr[k]`.
**Return the number of triples `(i, j, k)` with `a == b`.**

**Examples**
```
arr = [2,3,1,6,7]  ->  4
arr = [1,1,1,1,1]  ->  10
```

**Constraints:** `1 <= len(arr) <= 300`, `1 <= arr[i] <= 10^8`.
""",
    """def countTriplets(arr):
    n = len(arr)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] ^ arr[i]
    res = 0
    for l in range(n + 1):
        for r in range(l + 1, n + 1):
            if prefix[l] == prefix[r]:
                res += r - l - 1
    return res
""",
    visible=[{"arr": [2, 3, 1, 6, 7]}, {"arr": [1, 1, 1, 1, 1]}],
    hidden=[{"arr": [2, 3]}, {"arr": [1, 3, 5, 7, 9]}, {"arr": [7, 11, 12, 9, 5, 2, 7, 17, 22]},
            {"arr": [5]}, {"arr": [4, 4]}],
    gen=lambda r: [{"arr": [r.randint(1, 8) for _ in range(r.randint(1, 12))]}
                   for _ in range(8)],
    brute=_triplets_brute,
    checks=[({"arr": [2, 3, 1, 6, 7]}, 4), ({"arr": [1, 1, 1, 1, 1]}, 10), ({"arr": [2, 3]}, 0),
            ({"arr": [1, 3, 5, 7, 9]}, 3),
            ({"arr": [7, 11, 12, 9, 5, 2, 7, 17, 22]}, 8)],
    source="new_p")


# ===========================================================================
# 18. Maximum Score Words Formed by Letters
# ===========================================================================
add("maximum-score-words-formed-by-letters", "Maximum Score Words Formed by Letters", "hard",
    ["array", "string", "dynamic-programming", "bitmask"], "maxScoreWords",
    [("words", "string[]"), ("letters", "string[]"), ("score", "int[]")], "int",
    """
Given `words`, a multiset of available `letters`, and a `score` for each of `a..z`,
**return the maximum total score of a subset of `words`** that can be spelled using the
letters (each letter used at most once; a word used at most once).

**Examples**
```
words=["dog","cat","dad","good"], letters=["a","a","c","d","d","d","g","o","o"], ... -> 23
words=["leetcode"], letters=["l","e","t","c","o","d"], ...                          -> 0
```

**Constraints:** `1 <= len(words) <= 14`, `1 <= len(letters) <= 100`, `score` has 26
entries `0..10`.
""",
    """def maxScoreWords(words, letters, score):
    from collections import Counter
    avail = Counter(letters)
    n = len(words)
    best = [0]

    def bt(i, remaining, cur):
        if i == n:
            best[0] = max(best[0], cur)
            return
        bt(i + 1, remaining, cur)
        wc = Counter(words[i])
        if all(remaining.get(c, 0) >= cnt for c, cnt in wc.items()):
            for c, cnt in wc.items():
                remaining[c] -= cnt
            ws = sum(score[ord(c) - 97] for c in words[i])
            bt(i + 1, remaining, cur + ws)
            for c, cnt in wc.items():
                remaining[c] += cnt

    bt(0, dict(avail), 0)
    return best[0]
""",
    visible=[{"words": ["dog", "cat", "dad", "good"],
              "letters": ["a", "a", "c", "d", "d", "d", "g", "o", "o"],
              "score": [1, 0, 9, 5, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
             {"words": ["leetcode"], "letters": ["l", "e", "t", "c", "o", "d"],
              "score": [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]}],
    hidden=[{"words": ["xxxz", "ax", "bx", "cx"], "letters": ["z", "a", "b", "c", "x", "x", "x"],
             "score": [4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 10]},
            {"words": ["a"], "letters": ["a"], "score": [5] + [0] * 25},
            {"words": ["a"], "letters": ["b"], "score": [5] + [0] * 25}],
    gen=lambda r: [_scorewords_gen(r) for _ in range(6)],
    brute=_scorewords_brute,
    checks=[({"words": ["dog", "cat", "dad", "good"],
              "letters": ["a", "a", "c", "d", "d", "d", "g", "o", "o"],
              "score": [1, 0, 9, 5, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, 23),
            ({"words": ["xxxz", "ax", "bx", "cx"], "letters": ["z", "a", "b", "c", "x", "x", "x"],
              "score": [4, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 10]}, 27),
            ({"words": ["leetcode"], "letters": ["l", "e", "t", "c", "o", "d"],
              "score": [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]}, 0)],
    source="new_p")


# ===========================================================================
# 19. Range Sum of Sorted Subarray Sums
# ===========================================================================
add("range-sum-of-sorted-subarray-sums", "Range Sum of Sorted Subarray Sums", "medium",
    ["array", "sorting", "binary-search"], "rangeSum",
    [("nums", "int[]"), ("n", "int"), ("left", "int"), ("right", "int")], "int",
    """
Compute the sums of all `n*(n+1)/2` non-empty contiguous subarrays of `nums` and sort
them non-decreasingly. **Return the sum of the entries from index `left` to `right`
(1-indexed, inclusive)**, modulo `10^9 + 7`.

**Examples**
```
nums=[1,2,3,4], n=4, left=1, right=5   ->  13
nums=[1,2,3,4], n=4, left=1, right=10  ->  50
```

**Constraints:** `1 <= len(nums) == n <= 10^3`, `1 <= nums[i] <= 100`,
`1 <= left <= right <= n*(n+1)/2`.
""",
    """def rangeSum(nums, n, left, right):
    MOD = 10 ** 9 + 7
    sums = []
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            sums.append(s)
    sums.sort()
    return sum(sums[left - 1:right]) % MOD
""",
    visible=[{"nums": [1, 2, 3, 4], "n": 4, "left": 1, "right": 5},
             {"nums": [1, 2, 3, 4], "n": 4, "left": 3, "right": 4},
             {"nums": [1, 2, 3, 4], "n": 4, "left": 1, "right": 10}],
    hidden=[{"nums": [1], "n": 1, "left": 1, "right": 1},
            {"nums": [5, 5], "n": 2, "left": 1, "right": 3},
            {"nums": [10, 1, 2], "n": 3, "left": 2, "right": 5}],
    gen=lambda r: [_rangesum_gen(r) for _ in range(8)],
    brute=_rangesum_brute,
    checks=[({"nums": [1, 2, 3, 4], "n": 4, "left": 1, "right": 5}, 13),
            ({"nums": [1, 2, 3, 4], "n": 4, "left": 3, "right": 4}, 6),
            ({"nums": [1, 2, 3, 4], "n": 4, "left": 1, "right": 10}, 50),
            ({"nums": [1], "n": 1, "left": 1, "right": 1}, 1)],
    source="new_p")
