"""Batch 006 of the new_p.txt import (20 problems)."""
from scripts.build_bank import add, ilist, sstr  # noqa: F401


# --------------------------- brute / reference helpers ---------------------
def _flipmono_brute(S):
    n = len(S)
    best = n
    for split in range(n + 1):
        flips = sum(1 for i in range(split) if S[i] == '1') + \
            sum(1 for i in range(split, n) if S[i] == '0')
        best = min(best, flips)
    return best


def _binsum_brute(A, S):
    n = len(A)
    res = 0
    for i in range(n):
        cur = 0
        for j in range(i, n):
            cur += A[j]
            if cur == S:
                res += 1
    return res


def _stock3_brute(prices):
    n = len(prices)
    if n == 0:
        return 0

    def best_one(a):
        if not a:
            return 0
        mn = a[0]
        best = 0
        for p in a[1:]:
            best = max(best, p - mn)
            mn = min(mn, p)
        return best
    res = 0
    for i in range(n + 1):
        res = max(res, best_one(prices[:i]) + best_one(prices[i:]))
    return res


def _labels_brute(values, labels, numWanted, useLimit):
    from itertools import combinations
    from collections import Counter
    n = len(values)
    best = 0
    for size in range(0, numWanted + 1):
        for combo in combinations(range(n), size):
            c = Counter(labels[i] for i in combo)
            if all(v <= useLimit for v in c.values()):
                best = max(best, sum(values[i] for i in combo))
    return best


def _robot_brute(instructions):
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    x = y = d = 0
    for _ in range(4):
        for c in instructions:
            if c == 'G':
                x += dirs[d][0]
                y += dirs[d][1]
            elif c == 'L':
                d = (d + 3) % 4
            else:
                d = (d + 1) % 4
        if x == 0 and y == 0:
            return True
    return False


def _eqfreq_brute(nums):
    from collections import Counter
    best = 0
    for L in range(1, len(nums) + 1):
        prefix = nums[:L]
        for rem in range(L):
            c = Counter(prefix[:rem] + prefix[rem + 1:])
            if len(set(c.values())) <= 1:
                best = L
                break
    return best


def _flipgame_brute(fronts, backs):
    from itertools import product
    n = len(fronts)
    best = 0
    for flips in product([0, 1], repeat=n):
        f = [backs[i] if flips[i] else fronts[i] for i in range(n)]
        b = [fronts[i] if flips[i] else backs[i] for i in range(n)]
        fset = set(f)
        for i in range(n):
            if b[i] not in fset and (best == 0 or b[i] < best):
                best = b[i]
    return best


def _numsteps_brute(s):
    bits = [int(c) for c in s]
    steps = 0
    while not (len(bits) == 1 and bits[0] == 1):
        if bits[-1] == 0:
            bits.pop()
        else:
            i = len(bits) - 1
            carry = 1
            while i >= 0 and carry:
                if bits[i] == 1:
                    bits[i] = 0
                else:
                    bits[i] = 1
                    carry = 0
                i -= 1
            if carry:
                bits.insert(0, 1)
        while len(bits) > 1 and bits[0] == 0:
            bits.pop(0)
        steps += 1
    return steps


def _replace_brute(dictionary, sentence):
    roots = sorted(dictionary, key=len)
    out = []
    for w in sentence.split():
        rep = w
        for root in roots:
            if w.startswith(root):
                rep = root
                break
        out.append(rep)
    return " ".join(out)


def _twosub_brute(arr, target):
    n = len(arr)
    subs = []
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += arr[j]
            if s == target:
                subs.append((i, j))
            elif s > target:
                break
    best = float('inf')
    for a in subs:
        for b in subs:
            if a[1] < b[0]:
                best = min(best, (a[1] - a[0] + 1) + (b[1] - b[0] + 1))
    return best if best != float('inf') else -1


def _cycle_brute(grid):
    m = len(grid)
    n = len(grid[0])
    parent = list(range(m * n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return True
        parent[ra] = rb
        return False

    for i in range(m):
        for j in range(n):
            if j + 1 < n and grid[i][j] == grid[i][j + 1]:
                if union(i * n + j, i * n + j + 1):
                    return True
            if i + 1 < m and grid[i][j] == grid[i + 1][j]:
                if union(i * n + j, (i + 1) * n + j):
                    return True
    return False


def _hire_brute(quality, wage, K):
    from itertools import combinations
    n = len(quality)
    best = float('inf')
    for combo in combinations(range(n), K):
        ratio = max(wage[i] / quality[i] for i in combo)
        best = min(best, ratio * sum(quality[i] for i in combo))
    return round(best, 5)


def _clumsy_brute(N):
    if N == 0:
        return 0
    nums = list(range(N, 0, -1))
    vals = [nums[0]]
    opers = []
    for i in range(len(nums) - 1):
        op = '*/+-'[i % 4]
        b = nums[i + 1]
        if op == '*':
            vals[-1] = vals[-1] * b
        elif op == '/':
            vals[-1] = int(vals[-1] / b)
        else:
            opers.append(op)
            vals.append(b)
    res = vals[0]
    for i, op in enumerate(opers):
        res = res + vals[i + 1] if op == '+' else res - vals[i + 1]
    return res


def _taps_brute(n, ranges):
    INF = float('inf')
    intervals = [(max(0, i - r), min(n, i + r)) for i, r in enumerate(ranges)]
    dp = [0] + [INF] * n
    for i in range(1, n + 1):
        for l, rr in intervals:
            if l < i <= rr and dp[l] != INF:
                dp[i] = min(dp[i], dp[l] + 1)
    return dp[n] if dp[n] != INF else -1


def _uniquedigits_brute(n):
    return sum(1 for x in range(10 ** n) if len(set(str(x))) == len(str(x)))


def _jump2_brute(nums):
    n = len(nums)
    INF = float('inf')
    dp = [0] + [INF] * (n - 1)
    for i in range(n):
        if dp[i] == INF:
            continue
        for j in range(1, nums[i] + 1):
            if i + j < n:
                dp[i + j] = min(dp[i + j], dp[i] + 1)
    return dp[n - 1]


# ===========================================================================
# 1. Flip String to Monotone Increasing
# ===========================================================================
add("flip-string-to-monotone-increasing", "Flip String to Monotone Increasing",
    "medium", ["string", "dynamic-programming"], "minFlipsMonoIncr",
    [("S", "string")], "int",
    """
A `0`/`1` string is *monotone increasing* if it is some `0`s followed by some `1`s.
**Return the minimum number of flips** (`0`->`1` or `1`->`0`) to make `S` monotone
increasing.

**Examples**
```
S = "00110"     ->  1
S = "010110"    ->  2
S = "00011000"  ->  2
```

**Constraints:** `1 <= len(S) <= 2*10^4`, characters `0`/`1`.
""",
    """def minFlipsMonoIncr(S):
    ones = 0
    flips = 0
    for c in S:
        if c == '1':
            ones += 1
        else:
            flips = min(flips + 1, ones)
    return flips
""",
    visible=[{"S": "00110"}, {"S": "010110"}, {"S": "00011000"}],
    hidden=[{"S": "0"}, {"S": "1"}, {"S": "10"}, {"S": "111000"},
            {"S": "0101010101"}],
    gen=lambda r: [{"S": "".join(r.choice("01") for _ in range(r.randint(1, 12)))}
                   for _ in range(6)],
    brute=_flipmono_brute,
    checks=[({"S": "00110"}, 1), ({"S": "010110"}, 2), ({"S": "00011000"}, 2)],
    source="new_p")


# ===========================================================================
# 2. Binary Subarrays With Sum
# ===========================================================================
add("binary-subarrays-with-sum", "Binary Subarrays With Sum", "medium",
    ["array", "hash-table", "prefix-sum", "sliding-window"], "numSubarraysWithSum",
    [("A", "int[]"), ("S", "int")], "int",
    """
Given a `0`/`1` array `A` and an integer `S`, **return the number of non-empty
contiguous subarrays whose sum equals `S`.**

**Example**
```
A = [1,0,1,0,1], S = 2  ->  4
```

**Constraints:** `1 <= len(A) <= 3*10^4`, `0 <= S <= len(A)`, `A[i]` in `{0,1}`.
""",
    """def numSubarraysWithSum(A, S):
    from collections import defaultdict
    count = defaultdict(int)
    count[0] = 1
    cur = 0
    res = 0
    for x in A:
        cur += x
        res += count[cur - S]
        count[cur] += 1
    return res
""",
    visible=[{"A": [1, 0, 1, 0, 1], "S": 2}],
    hidden=[{"A": [0, 0, 0, 0, 0], "S": 0}, {"A": [1, 1, 1], "S": 2},
            {"A": [0, 1, 0], "S": 0}, {"A": [1], "S": 1}, {"A": [1], "S": 0}],
    gen=lambda r: [(lambda a: {"A": a, "S": r.randint(0, sum(a) if a else 0)})
                   ([r.randint(0, 1) for _ in range(r.randint(1, 12))]) for _ in range(6)],
    brute=_binsum_brute,
    checks=[({"A": [1, 0, 1, 0, 1], "S": 2}, 4)],
    source="new_p")


# ===========================================================================
# 3. Best Time to Buy and Sell Stock III
# ===========================================================================
add("best-time-to-buy-and-sell-stock-iii", "Best Time to Buy and Sell Stock III",
    "hard", ["array", "dynamic-programming"], "maxProfit", [("prices", "int[]")], "int",
    """
`prices[i]` is the stock price on day `i`. **Return the maximum profit** with at
most **two** transactions (you must sell before buying again).

**Examples**
```
prices = [3,3,5,0,0,3,1,4]  ->  6
prices = [1,2,3,4,5]        ->  4
prices = [7,6,4,3,1]        ->  0
```

**Constraints:** `0 <= len(prices) <= 10^5`, `0 <= prices[i] <= 10^5`.
""",
    """def maxProfit(prices):
    buy1 = float('-inf')
    sell1 = 0
    buy2 = float('-inf')
    sell2 = 0
    for p in prices:
        buy1 = max(buy1, -p)
        sell1 = max(sell1, buy1 + p)
        buy2 = max(buy2, sell1 - p)
        sell2 = max(sell2, buy2 + p)
    return sell2
""",
    visible=[{"prices": [3, 3, 5, 0, 0, 3, 1, 4]}, {"prices": [1, 2, 3, 4, 5]},
             {"prices": [7, 6, 4, 3, 1]}],
    hidden=[{"prices": []}, {"prices": [1]}, {"prices": [2, 1, 4, 5, 2, 9, 7]},
            {"prices": [6, 1, 6, 4, 3, 0, 2]}],
    gen=lambda r: [{"prices": ilist(r, 0, 12, 0, 15)} for _ in range(6)],
    brute=_stock3_brute,
    checks=[({"prices": [3, 3, 5, 0, 0, 3, 1, 4]}, 6), ({"prices": [1, 2, 3, 4, 5]}, 4),
            ({"prices": [7, 6, 4, 3, 1]}, 0)],
    source="new_p")


# ===========================================================================
# 4. Largest Values From Labels
# ===========================================================================
add("largest-values-from-labels", "Largest Values From Labels", "medium",
    ["array", "hash-table", "greedy", "sorting"], "largestValsFromLabels",
    [("values", "int[]"), ("labels", "int[]"), ("numWanted", "int"), ("useLimit", "int")],
    "int",
    """
Item `i` has value `values[i]` and label `labels[i]`. Choose a subset with at most
`numWanted` items and at most `useLimit` items per label, to **maximize the sum of
values.** Return that maximum sum.

**Examples**
```
values=[5,4,3,2,1], labels=[1,1,2,2,3], numWanted=3, useLimit=1  ->  9
values=[5,4,3,2,1], labels=[1,3,3,3,2], numWanted=3, useLimit=2  ->  12
values=[9,8,8,7,6], labels=[0,0,0,1,1], numWanted=3, useLimit=1  ->  16
```

**Constraints:** `1 <= len(values) == len(labels) <= 2*10^4`,
`0 <= values[i], labels[i] <= 2*10^4`, `1 <= numWanted, useLimit <= len(values)`.
""",
    """def largestValsFromLabels(values, labels, numWanted, useLimit):
    from collections import defaultdict
    items = sorted(zip(values, labels), reverse=True)
    used = defaultdict(int)
    total = 0
    count = 0
    for v, l in items:
        if count >= numWanted:
            break
        if used[l] < useLimit:
            total += v
            used[l] += 1
            count += 1
    return total
""",
    visible=[{"values": [5, 4, 3, 2, 1], "labels": [1, 1, 2, 2, 3],
              "numWanted": 3, "useLimit": 1},
             {"values": [5, 4, 3, 2, 1], "labels": [1, 3, 3, 3, 2],
              "numWanted": 3, "useLimit": 2},
             {"values": [9, 8, 8, 7, 6], "labels": [0, 0, 0, 1, 1],
              "numWanted": 3, "useLimit": 1}],
    hidden=[{"values": [9, 8, 8, 7, 6], "labels": [0, 0, 0, 1, 1],
             "numWanted": 3, "useLimit": 2},
            {"values": [5], "labels": [1], "numWanted": 1, "useLimit": 1}],
    gen=lambda r: [(lambda n: {"values": [r.randint(1, 20) for _ in range(n)],
                               "labels": [r.randint(0, 3) for _ in range(n)],
                               "numWanted": r.randint(1, n), "useLimit": r.randint(1, n)})
                   (r.randint(1, 7)) for _ in range(6)],
    brute=_labels_brute,
    checks=[({"values": [5, 4, 3, 2, 1], "labels": [1, 1, 2, 2, 3],
              "numWanted": 3, "useLimit": 1}, 9),
            ({"values": [5, 4, 3, 2, 1], "labels": [1, 3, 3, 3, 2],
              "numWanted": 3, "useLimit": 2}, 12),
            ({"values": [9, 8, 8, 7, 6], "labels": [0, 0, 0, 1, 1],
              "numWanted": 3, "useLimit": 1}, 16),
            ({"values": [9, 8, 8, 7, 6], "labels": [0, 0, 0, 1, 1],
              "numWanted": 3, "useLimit": 2}, 24)],
    source="new_p")


# ===========================================================================
# 5. Sort Characters By Frequency
# ===========================================================================
add("sort-characters-by-frequency", "Sort Characters By Frequency", "medium",
    ["string", "hash-table", "sorting", "heap"], "frequencySort",
    [("s", "string")], "string",
    """
Sort the characters of `s` by **decreasing frequency**; identical characters must be
grouped together. **Break ties by character in ascending (code-point) order** so the
answer is unique. **Return the sorted string.**

**Examples**
```
s = "tree"     ->  "eert"
s = "cccaaa"   ->  "aaaccc"
s = "Aabb"     ->  "bbAa"
```

**Constraints:** `1 <= len(s) <= 5*10^5`, printable ASCII.
""",
    """def frequencySort(s):
    from collections import Counter
    cnt = Counter(s)
    chars = sorted(cnt, key=lambda c: (-cnt[c], c))
    return "".join(c * cnt[c] for c in chars)
""",
    visible=[{"s": "tree"}, {"s": "cccaaa"}, {"s": "Aabb"}],
    hidden=[{"s": "a"}, {"s": "aabbcc"}, {"s": "loveleetcode"}, {"s": "zZzZ"}],
    gen=lambda r: [{"s": sstr(r, 1, 14, "aabbcAB")} for _ in range(6)],
    brute=lambda s: "".join(c * __import__("collections").Counter(s)[c]
                            for c in sorted(__import__("collections").Counter(s),
                                            key=lambda c: (-__import__("collections").Counter(s)[c], c))),
    checks=[({"s": "tree"}, "eert"), ({"s": "cccaaa"}, "aaaccc"),
            ({"s": "Aabb"}, "bbAa")],
    source="new_p")


# ===========================================================================
# 6. Robot Bounded In Circle
# ===========================================================================
add("robot-bounded-in-circle", "Robot Bounded In Circle", "medium",
    ["math", "string", "simulation"], "isRobotBounded",
    [("instructions", "string")], "bool",
    """
A robot starts at `(0,0)` facing north and repeats `instructions` forever: `'G'`
moves forward one unit, `'L'`/`'R'` turn 90 degrees. **Return `true` if the robot
stays within some bounded circle** (it returns to the origin or does not end facing
north after one pass).

**Examples**
```
instructions = "GGLLGG"  ->  true
instructions = "GG"      ->  false
instructions = "GL"      ->  true
```

**Constraints:** `1 <= len(instructions) <= 100`, characters `G`, `L`, `R`.
""",
    """def isRobotBounded(instructions):
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    x = y = d = 0
    for c in instructions:
        if c == 'G':
            x += dirs[d][0]
            y += dirs[d][1]
        elif c == 'L':
            d = (d + 3) % 4
        else:
            d = (d + 1) % 4
    return (x == 0 and y == 0) or d != 0
""",
    visible=[{"instructions": "GGLLGG"}, {"instructions": "GG"},
             {"instructions": "GL"}],
    hidden=[{"instructions": "G"}, {"instructions": "L"}, {"instructions": "GLGLGLG"},
            {"instructions": "GLRLLGGR"}],
    gen=lambda r: [{"instructions": "".join(r.choice("GLR") for _ in range(r.randint(1, 10)))}
                   for _ in range(6)],
    brute=_robot_brute,
    checks=[({"instructions": "GGLLGG"}, True), ({"instructions": "GG"}, False),
            ({"instructions": "GL"}, True)],
    source="new_p")


# ===========================================================================
# 7. Maximum Equal Frequency
# ===========================================================================
add("maximum-equal-frequency", "Maximum Equal Frequency", "hard",
    ["array", "hash-table"], "maxEqualFreq", [("nums", "int[]")], "int",
    """
**Return the longest prefix of `nums`** such that removing exactly one element from
it makes every value that remains appear the same number of times. (Removing the
only element, leaving nothing, also counts.)

**Examples**
```
nums = [2,2,1,1,5,3,3,5]                    ->  7
nums = [1,1,1,2,2,2,3,3,3,4,4,4,5]          ->  13
nums = [1,1,1,2,2,2]                        ->  5
```

**Constraints:** `2 <= len(nums) <= 10^5`, `1 <= nums[i] <= 10^5`.
""",
    """def maxEqualFreq(nums):
    from collections import defaultdict
    count = defaultdict(int)
    freq = defaultdict(int)
    best = 0
    for i, x in enumerate(nums):
        count[x] += 1
        c = count[x]
        if c > 1:
            freq[c - 1] -= 1
            if freq[c - 1] == 0:
                del freq[c - 1]
        freq[c] += 1
        if len(freq) == 1:
            f = next(iter(freq))
            if f == 1 or freq[f] == 1:
                best = i + 1
        elif len(freq) == 2:
            lo, hi = sorted(freq)
            if (lo == 1 and freq[lo] == 1) or (hi == lo + 1 and freq[hi] == 1):
                best = i + 1
    return best
""",
    visible=[{"nums": [2, 2, 1, 1, 5, 3, 3, 5]},
             {"nums": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5]},
             {"nums": [1, 1, 1, 2, 2, 2]}],
    hidden=[{"nums": [10, 2, 8, 9, 3, 8, 1, 5, 2, 3, 7, 6]}, {"nums": [1, 2]},
            {"nums": [1, 1]}, {"nums": [5, 5, 5, 5]}],
    gen=lambda r: [{"nums": [r.randint(1, 4) for _ in range(r.randint(2, 14))]}
                   for _ in range(6)],
    brute=_eqfreq_brute,
    checks=[({"nums": [2, 2, 1, 1, 5, 3, 3, 5]}, 7),
            ({"nums": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5]}, 13),
            ({"nums": [1, 1, 1, 2, 2, 2]}, 5),
            ({"nums": [10, 2, 8, 9, 3, 8, 1, 5, 2, 3, 7, 6]}, 8)],
    source="new_p")


# ===========================================================================
# 8. Card Flipping Game
# ===========================================================================
add("card-flipping-game", "Card Flipping Game", "medium",
    ["array", "hash-table"], "flipgame",
    [("fronts", "int[]"), ("backs", "int[]")], "int",
    """
Each card `i` shows `fronts[i]` and `backs[i]`. You may flip any cards, then choose
one card; the number `X` on its back is *good* if `X` appears on no card's front.
**Return the smallest good number**, or `0` if none exists. (A number that is equal
on both sides of some card can never be good.)

**Example**
```
fronts = [1,2,4,4,7], backs = [1,3,4,1,3]  ->  2
```

**Constraints:** `1 <= len(fronts) == len(backs) <= 1000`,
`1 <= fronts[i], backs[i] <= 2000`.
""",
    """def flipgame(fronts, backs):
    same = {f for f, b in zip(fronts, backs) if f == b}
    best = float('inf')
    for x in fronts + backs:
        if x not in same:
            best = min(best, x)
    return best if best != float('inf') else 0
""",
    visible=[{"fronts": [1, 2, 4, 4, 7], "backs": [1, 3, 4, 1, 3]}],
    hidden=[{"fronts": [1], "backs": [1]}, {"fronts": [1, 1], "backs": [2, 2]},
            {"fronts": [1, 2, 3], "backs": [3, 2, 1]},
            {"fronts": [5, 5, 5], "backs": [5, 5, 5]}],
    gen=lambda r: [(lambda n: {"fronts": [r.randint(1, 6) for _ in range(n)],
                               "backs": [r.randint(1, 6) for _ in range(n)]})
                   (r.randint(1, 6)) for _ in range(6)],
    brute=_flipgame_brute,
    checks=[({"fronts": [1, 2, 4, 4, 7], "backs": [1, 3, 4, 1, 3]}, 2),
            ({"fronts": [1], "backs": [1]}, 0)],
    source="new_p")


# ===========================================================================
# 9. Number of Steps to Reduce a Number in Binary Representation to One
# ===========================================================================
add("number-of-steps-to-reduce-a-number-in-binary-representation-to-one",
    "Number of Steps to Reduce a Number in Binary Representation to One", "medium",
    ["string", "bit-manipulation", "simulation"], "numSteps",
    [("s", "string")], "int",
    """
Given a binary string `s`, repeatedly: if the number is even divide by 2, if odd add
1. **Return the number of steps to reach 1.**

**Examples**
```
s = "1101"  ->  6
s = "10"    ->  1
s = "1"     ->  0
```

**Constraints:** `1 <= len(s) <= 500`, `s` is binary with `s[0] == '1'`.
""",
    """def numSteps(s):
    num = int(s, 2)
    steps = 0
    while num > 1:
        if num % 2 == 0:
            num //= 2
        else:
            num += 1
        steps += 1
    return steps
""",
    visible=[{"s": "1101"}, {"s": "10"}, {"s": "1"}],
    hidden=[{"s": "111"}, {"s": "1000"}, {"s": "100000"}, {"s": "1111111"}],
    gen=lambda r: [{"s": "1" + "".join(r.choice("01") for _ in range(r.randint(0, 9)))}
                   for _ in range(6)],
    brute=_numsteps_brute,
    checks=[({"s": "1101"}, 6), ({"s": "10"}, 1), ({"s": "1"}, 0)],
    source="new_p")


# ===========================================================================
# 10. Optimal Division
# ===========================================================================
add("optimal-division", "Optimal Division", "medium",
    ["array", "math", "dynamic-programming"], "optimalDivision",
    [("nums", "int[]")], "string",
    """
The integers `nums` are divided left to right (`a/b/c/...`). By inserting
parentheses you can change the order. **Return the expression (with no redundant
parentheses) that maximizes the result.** The optimal form is unique: with three or
more numbers it is `nums[0]/(nums[1]/nums[2]/.../nums[k])`.

**Example**
```
nums = [1000,100,10,2]  ->  "1000/(100/10/2)"
```

**Constraints:** `1 <= len(nums) <= 10`, `2 <= nums[i] <= 1000`.
""",
    """def optimalDivision(nums):
    if len(nums) == 1:
        return str(nums[0])
    if len(nums) == 2:
        return f"{nums[0]}/{nums[1]}"
    return f"{nums[0]}/(" + "/".join(map(str, nums[1:])) + ")"
""",
    visible=[{"nums": [1000, 100, 10, 2]}, {"nums": [2, 3, 4]}],
    hidden=[{"nums": [2]}, {"nums": [2, 3]}, {"nums": [9, 8, 7, 6, 5]},
            {"nums": [100, 50]}],
    gen=lambda r: [{"nums": [r.randint(2, 100) for _ in range(r.randint(1, 6))]}
                   for _ in range(6)],
    checks=[({"nums": [1000, 100, 10, 2]}, "1000/(100/10/2)"),
            ({"nums": [2, 3, 4]}, "2/(3/4)"), ({"nums": [2]}, "2"),
            ({"nums": [2, 3]}, "2/3")],
    source="new_p")


# ===========================================================================
# 11. Replace Words
# ===========================================================================
add("replace-words", "Replace Words", "medium",
    ["array", "string", "trie", "hash-table"], "replaceWords",
    [("dictionary", "string[]"), ("sentence", "string")], "string",
    """
Given a list of root words `dictionary` and a `sentence`, replace every word that
has a root prefix with the **shortest** such root. **Return the resulting
sentence.**

**Example**
```
dictionary = ["cat","bat","rat"], sentence = "the cattle was rattled by the battery"
  ->  "the cat was rat by the bat"
```

**Constraints:** lowercase words; roots and sentence words are non-empty.
""",
    """def replaceWords(dictionary, sentence):
    roots = set(dictionary)
    out = []
    for w in sentence.split():
        rep = w
        for i in range(1, len(w) + 1):
            if w[:i] in roots:
                rep = w[:i]
                break
        out.append(rep)
    return " ".join(out)
""",
    visible=[{"dictionary": ["cat", "bat", "rat"],
              "sentence": "the cattle was rattled by the battery"}],
    hidden=[{"dictionary": ["a", "b", "c"], "sentence": "aadsfasf absbs bbab cadsfafs"},
            {"dictionary": ["catt", "cat", "bat", "rat"],
             "sentence": "the cattle was rattled by the battery"},
            {"dictionary": ["se", "association"], "sentence": "the search engine"}],
    gen=lambda r: [{"dictionary": [sstr(r, 1, 3, "ab") for _ in range(r.randint(1, 3))],
                    "sentence": " ".join(sstr(r, 1, 5, "ab") for _ in range(r.randint(1, 4)))}
                   for _ in range(6)],
    brute=_replace_brute,
    checks=[({"dictionary": ["cat", "bat", "rat"],
              "sentence": "the cattle was rattled by the battery"},
             "the cat was rat by the bat")],
    source="new_p")


# ===========================================================================
# 12. Find Two Non-overlapping Sub-arrays Each With Target Sum
# ===========================================================================
add("find-two-non-overlapping-sub-arrays-each-with-target-sum",
    "Find Two Non-overlapping Sub-arrays Each With Target Sum", "medium",
    ["array", "dynamic-programming", "sliding-window"], "minSumOfLengths",
    [("arr", "int[]"), ("target", "int")], "int",
    """
Find two **non-overlapping** subarrays of `arr`, each summing to `target`, with the
**minimum total length**. **Return that minimum total length**, or `-1` if it is
impossible.

**Examples**
```
arr = [3,2,2,4,3], target = 3        ->  2
arr = [7,3,4,7], target = 7          ->  2
arr = [4,3,2,6,2,3,4], target = 6    ->  -1
arr = [3,1,1,1,5,1,2,1], target = 3  ->  3
```

**Constraints:** `1 <= len(arr) <= 10^5`, `1 <= arr[i] <= 1000`,
`1 <= target <= 10^8`.
""",
    """def minSumOfLengths(arr, target):
    n = len(arr)
    INF = float('inf')
    pre = [INF] * n
    res = INF
    l = 0
    cur = 0
    best = INF
    for r in range(n):
        cur += arr[r]
        while cur > target:
            cur -= arr[l]
            l += 1
        if cur == target:
            length = r - l + 1
            if l > 0 and pre[l - 1] != INF:
                res = min(res, length + pre[l - 1])
            best = min(best, length)
        pre[r] = best
    return res if res != INF else -1
""",
    visible=[{"arr": [3, 2, 2, 4, 3], "target": 3}, {"arr": [7, 3, 4, 7], "target": 7},
             {"arr": [4, 3, 2, 6, 2, 3, 4], "target": 6},
             {"arr": [3, 1, 1, 1, 5, 1, 2, 1], "target": 3}],
    hidden=[{"arr": [5, 5, 4, 4, 5], "target": 3}, {"arr": [2, 2, 2], "target": 2},
            {"arr": [1, 1, 1, 1], "target": 1}, {"arr": [3], "target": 3}],
    gen=lambda r: [{"arr": [r.randint(1, 5) for _ in range(r.randint(1, 12))],
                    "target": r.randint(1, 8)} for _ in range(6)],
    brute=_twosub_brute,
    checks=[({"arr": [3, 2, 2, 4, 3], "target": 3}, 2),
            ({"arr": [7, 3, 4, 7], "target": 7}, 2),
            ({"arr": [4, 3, 2, 6, 2, 3, 4], "target": 6}, -1),
            ({"arr": [3, 1, 1, 1, 5, 1, 2, 1], "target": 3}, 3)],
    source="new_p")


# ===========================================================================
# 13. Detect Cycles in 2D Grid
# ===========================================================================
add("detect-cycles-in-2d-grid", "Detect Cycles in 2D Grid", "medium",
    ["array", "depth-first-search", "breadth-first-search", "union-find", "matrix"],
    "containsCycle", [("grid", "string[]")], "bool",
    """
`grid` is given as a list of equal-length strings (each character a cell value).
**Return `true` if there is a cycle of length `>= 4`** made of one repeated value,
moving between 4-directionally adjacent equal cells without immediately revisiting
the previous cell.

**Examples**
```
grid = ["aaaa","abba","abba","aaaa"]  ->  true
grid = ["abb","bzb","bba"]            ->  false
```

**Constraints:** `1 <= len(grid)`, all rows equal length, lowercase letters.
""",
    """def containsCycle(grid):
    import sys
    sys.setrecursionlimit(10000)
    m = len(grid)
    n = len(grid[0])
    visited = [[False] * n for _ in range(m)]

    def dfs(r, c, pr, pc, val):
        visited[r][c] = True
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == val and not (nr == pr and nc == pc):
                if visited[nr][nc]:
                    return True
                if dfs(nr, nc, r, c, val):
                    return True
        return False

    for i in range(m):
        for j in range(n):
            if not visited[i][j] and dfs(i, j, -1, -1, grid[i][j]):
                return True
    return False
""",
    visible=[{"grid": ["aaaa", "abba", "abba", "aaaa"]},
             {"grid": ["abb", "bzb", "bba"]}],
    hidden=[{"grid": ["aa", "aa"]}, {"grid": ["a"]}, {"grid": ["ab", "ba"]},
            {"grid": ["ccca", "cdcc", "ccec", "fccc"]}],
    gen=lambda r: [(lambda rows, cols: {"grid": ["".join(r.choice("ab") for _ in range(cols))
                                                 for _ in range(rows)]})
                   (r.randint(1, 5), r.randint(1, 5)) for _ in range(6)],
    brute=_cycle_brute,
    checks=[({"grid": ["aaaa", "abba", "abba", "aaaa"]}, True),
            ({"grid": ["abb", "bzb", "bba"]}, False),
            ({"grid": ["aa", "aa"]}, True)],
    source="new_p")


# ===========================================================================
# 14. Magic Squares In Grid
# ===========================================================================
add("magic-squares-in-grid", "Magic Squares In Grid", "medium",
    ["array", "math", "matrix"], "numMagicSquaresInside",
    [("grid", "int[][]")], "int",
    """
A `3x3` magic square uses the distinct numbers `1..9` so every row, column, and both
diagonals sum to the same value. **Return how many `3x3` contiguous subgrids of
`grid` are magic squares.**

**Examples**
```
grid = [[4,3,8,4],[9,5,1,9],[2,7,6,2]]  ->  1
grid = [[8]]                            ->  0
```

**Constraints:** `1 <= rows, cols <= 10`, `0 <= grid[i][j] <= 15`.
""",
    """def numMagicSquaresInside(grid):
    m = len(grid)
    n = len(grid[0])

    def is_magic(r, c):
        nums = [grid[r + i][c + j] for i in range(3) for j in range(3)]
        if sorted(nums) != list(range(1, 10)):
            return False
        s = grid[r][c] + grid[r][c + 1] + grid[r][c + 2]
        for i in range(3):
            if sum(grid[r + i][c + j] for j in range(3)) != s:
                return False
            if sum(grid[r + j][c + i] for j in range(3)) != s:
                return False
        if grid[r][c] + grid[r + 1][c + 1] + grid[r + 2][c + 2] != s:
            return False
        if grid[r][c + 2] + grid[r + 1][c + 1] + grid[r + 2][c] != s:
            return False
        return True

    count = 0
    for r in range(m - 2):
        for c in range(n - 2):
            if is_magic(r, c):
                count += 1
    return count
""",
    visible=[{"grid": [[4, 3, 8, 4], [9, 5, 1, 9], [2, 7, 6, 2]]}, {"grid": [[8]]}],
    hidden=[{"grid": [[4, 4], [3, 3]]}, {"grid": [[4, 7, 8], [9, 5, 1], [2, 3, 6]]},
            {"grid": [[8, 1, 6], [3, 5, 7], [4, 9, 2]]},
            {"grid": [[2, 7, 6], [9, 5, 1], [4, 3, 8]]}],
    gen=lambda r: [(lambda rows, cols: {"grid": [[r.randint(1, 9) for _ in range(cols)]
                                                 for _ in range(rows)]})
                   (r.randint(1, 4), r.randint(1, 4)) for _ in range(6)],
    checks=[({"grid": [[4, 3, 8, 4], [9, 5, 1, 9], [2, 7, 6, 2]]}, 1),
            ({"grid": [[8]]}, 0), ({"grid": [[4, 4], [3, 3]]}, 0),
            ({"grid": [[8, 1, 6], [3, 5, 7], [4, 9, 2]]}, 1)],
    source="new_p")


# ===========================================================================
# 15. Minimum Cost to Hire K Workers
# ===========================================================================
add("minimum-cost-to-hire-k-workers", "Minimum Cost to Hire K Workers", "hard",
    ["array", "greedy", "heap", "sorting"], "mincostToHireWorkers",
    [("quality", "int[]"), ("wage", "int[]"), ("K", "int")], "float",
    """
Hire exactly `K` of the `N` workers. Worker `i` has `quality[i]` and minimum wage
`wage[i]`. Everyone in the group is paid in proportion to their quality, and each at
least their minimum wage. **Return the least total cost** (rounded to 5 decimals).

**Examples**
```
quality = [10,20,5], wage = [70,50,30], K = 2          ->  105.0
quality = [3,1,10,10,1], wage = [4,8,2,2,7], K = 3     ->  30.66667
```

**Constraints:** `1 <= K <= N <= 10^4`, `1 <= quality[i], wage[i] <= 10^4`.
""",
    """def mincostToHireWorkers(quality, wage, K):
    import heapq
    workers = sorted((w / q, q) for w, q in zip(wage, quality))
    heap = []
    sumq = 0
    best = float('inf')
    for ratio, q in workers:
        heapq.heappush(heap, -q)
        sumq += q
        if len(heap) > K:
            sumq += heapq.heappop(heap)
        if len(heap) == K:
            best = min(best, ratio * sumq)
    return round(best, 5)
""",
    visible=[{"quality": [10, 20, 5], "wage": [70, 50, 30], "K": 2},
             {"quality": [3, 1, 10, 10, 1], "wage": [4, 8, 2, 2, 7], "K": 3}],
    hidden=[{"quality": [1], "wage": [5], "K": 1},
            {"quality": [2, 2], "wage": [3, 3], "K": 2},
            {"quality": [4, 3, 2, 1], "wage": [10, 20, 5, 8], "K": 2}],
    gen=lambda r: [(lambda n: {"quality": [r.randint(1, 10) for _ in range(n)],
                               "wage": [r.randint(1, 20) for _ in range(n)],
                               "K": r.randint(1, n)})(r.randint(1, 7)) for _ in range(6)],
    brute=_hire_brute,
    checks=[({"quality": [10, 20, 5], "wage": [70, 50, 30], "K": 2}, 105.0),
            ({"quality": [3, 1, 10, 10, 1], "wage": [4, 8, 2, 2, 7], "K": 3}, 30.66667)],
    source="new_p")


# ===========================================================================
# 16. Clumsy Factorial
# ===========================================================================
add("clumsy-factorial", "Clumsy Factorial", "medium",
    ["math", "stack", "simulation"], "clumsy", [("N", "int")], "int",
    """
The *clumsy factorial* of `N` takes `N, N-1, ..., 1` and cycles the operators
`* / + -` between them (e.g. `clumsy(10) = 10*9/8+7-6*5/4+3-2*1`), using normal
operator precedence and **floor-toward-zero division**. **Return `clumsy(N)`.**

**Examples**
```
N = 4   ->  7    (4*3/2 + 1)
N = 10  ->  12
```

**Constraints:** `1 <= N <= 10^4`.
""",
    """def clumsy(N):
    stack = [N]
    num = N - 1
    op = 0
    while num > 0:
        if op == 0:
            stack.append(stack.pop() * num)
        elif op == 1:
            top = stack.pop()
            stack.append(int(top / num))
        elif op == 2:
            stack.append(num)
        else:
            stack.append(-num)
        op = (op + 1) % 4
        num -= 1
    return sum(stack)
""",
    visible=[{"N": 4}, {"N": 10}],
    hidden=[{"N": 1}, {"N": 2}, {"N": 3}, {"N": 5}, {"N": 100}],
    gen=lambda r: [{"N": r.randint(1, 30)} for _ in range(6)],
    brute=_clumsy_brute,
    checks=[({"N": 4}, 7), ({"N": 10}, 12), ({"N": 1}, 1), ({"N": 3}, 6)],
    source="new_p")


# ===========================================================================
# 17. Minimum Number of Taps to Open to Water a Garden
# ===========================================================================
add("minimum-number-of-taps-to-open-to-water-a-garden",
    "Minimum Number of Taps to Open to Water a Garden", "hard",
    ["array", "dynamic-programming", "greedy"], "minTaps",
    [("n", "int"), ("ranges", "int[]")], "int",
    """
A garden spans `[0, n]` with a tap at each integer point `0..n`. Tap `i` waters
`[i - ranges[i], i + ranges[i]]`. **Return the minimum number of taps to water the
whole garden**, or `-1` if impossible.

**Examples**
```
n = 5, ranges = [3,4,1,1,0,0]      ->  1
n = 3, ranges = [0,0,0,0]          ->  -1
n = 7, ranges = [1,2,1,0,2,1,0,1]  ->  3
```

**Constraints:** `1 <= n <= 10^4`, `len(ranges) == n+1`, `0 <= ranges[i] <= 100`.
""",
    """def minTaps(n, ranges):
    max_reach = [0] * (n + 1)
    for i, r in enumerate(ranges):
        left = max(0, i - r)
        right = min(n, i + r)
        max_reach[left] = max(max_reach[left], right)
    taps = 0
    cur_end = 0
    next_end = 0
    i = 0
    while cur_end < n:
        while i <= cur_end:
            next_end = max(next_end, max_reach[i])
            i += 1
        if next_end <= cur_end:
            return -1
        cur_end = next_end
        taps += 1
    return taps
""",
    visible=[{"n": 5, "ranges": [3, 4, 1, 1, 0, 0]}, {"n": 3, "ranges": [0, 0, 0, 0]},
             {"n": 7, "ranges": [1, 2, 1, 0, 2, 1, 0, 1]}],
    hidden=[{"n": 8, "ranges": [4, 0, 0, 0, 0, 0, 0, 0, 4]},
            {"n": 8, "ranges": [4, 0, 0, 0, 4, 0, 0, 0, 4]},
            {"n": 1, "ranges": [1, 0]}, {"n": 2, "ranges": [0, 0, 0]}],
    gen=lambda r: [(lambda n: {"n": n, "ranges": [r.randint(0, 3) for _ in range(n + 1)]})
                   (r.randint(1, 10)) for _ in range(6)],
    brute=_taps_brute,
    checks=[({"n": 5, "ranges": [3, 4, 1, 1, 0, 0]}, 1),
            ({"n": 3, "ranges": [0, 0, 0, 0]}, -1),
            ({"n": 7, "ranges": [1, 2, 1, 0, 2, 1, 0, 1]}, 3),
            ({"n": 8, "ranges": [4, 0, 0, 0, 0, 0, 0, 0, 4]}, 2)],
    source="new_p")


# ===========================================================================
# 18. Super Washing Machines
# ===========================================================================
add("super-washing-machines", "Super Washing Machines", "hard",
    ["array", "greedy", "prefix-sum"], "findMinMoves", [("machines", "int[]")], "int",
    """
`machines[i]` dresses sit in machine `i` in a row. Each move, you may move one dress
from any number of machines to an adjacent machine (simultaneously). **Return the
minimum number of moves to equalize all machines**, or `-1` if impossible.

**Examples**
```
machines = [1,0,5]  ->  3
machines = [0,3,0]  ->  2
machines = [0,2,0]  ->  -1
```

**Constraints:** `1 <= len(machines) <= 10^4`, `0 <= machines[i] <= 10^5`.
""",
    """def findMinMoves(machines):
    total = sum(machines)
    n = len(machines)
    if total % n != 0:
        return -1
    avg = total // n
    res = 0
    running = 0
    for m in machines:
        diff = m - avg
        running += diff
        res = max(res, abs(running), diff)
    return res
""",
    visible=[{"machines": [1, 0, 5]}, {"machines": [0, 3, 0]}, {"machines": [0, 2, 0]}],
    hidden=[{"machines": [0, 0, 0]}, {"machines": [4]}, {"machines": [1, 1, 1]},
            {"machines": [9, 1, 8, 8, 9]}],
    gen=lambda r: [{"machines": [r.randint(0, 8) for _ in range(r.randint(1, 8))]}
                   for _ in range(6)],
    checks=[({"machines": [1, 0, 5]}, 3), ({"machines": [0, 3, 0]}, 2),
            ({"machines": [0, 2, 0]}, -1), ({"machines": [0, 0, 0]}, 0)],
    source="new_p")


# ===========================================================================
# 19. Count Numbers with Unique Digits
# ===========================================================================
add("count-numbers-with-unique-digits", "Count Numbers with Unique Digits", "medium",
    ["math", "dynamic-programming", "backtracking"], "countNumbersWithUniqueDigits",
    [("n", "int")], "int",
    """
**Return how many numbers `x` with `0 <= x < 10^n` have all distinct digits.**

**Example**
```
n = 2  ->  91    (everything in [0,100) except 11,22,...,99)
```

**Constraints:** `0 <= n <= 8`.
""",
    """def countNumbersWithUniqueDigits(n):
    if n == 0:
        return 1
    res = 10
    unique = 9
    available = 9
    for _ in range(2, n + 1):
        unique *= available
        res += unique
        available -= 1
    return res
""",
    visible=[{"n": 2}],
    hidden=[{"n": 0}, {"n": 1}, {"n": 3}, {"n": 4}, {"n": 5}],
    gen=lambda r: [{"n": r.randint(0, 5)} for _ in range(6)],
    brute=_uniquedigits_brute,
    checks=[({"n": 2}, 91), ({"n": 0}, 1), ({"n": 1}, 10), ({"n": 3}, 739)],
    source="new_p")


# ===========================================================================
# 20. Jump Game II
# ===========================================================================
add("jump-game-ii", "Jump Game II", "medium", ["array", "greedy", "dynamic-programming"],
    "jump", [("nums", "int[]")], "int",
    """
`nums[i]` is the maximum jump length from index `i`. Starting at index `0`, **return
the minimum number of jumps to reach the last index** (you can always reach it).

**Example**
```
nums = [2,3,1,1,4]  ->  2
```

**Constraints:** `1 <= len(nums) <= 10^4`, `0 <= nums[i] <= 1000`.
""",
    """def jump(nums):
    n = len(nums)
    jumps = 0
    cur_end = 0
    farthest = 0
    for i in range(n - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
    return jumps
""",
    visible=[{"nums": [2, 3, 1, 1, 4]}],
    hidden=[{"nums": [0]}, {"nums": [2, 1]}, {"nums": [1, 1, 1, 1]},
            {"nums": [3, 3, 4, 1, 1, 1]}, {"nums": [5, 1, 1, 1, 1]}],
    gen=lambda r: [{"nums": [r.randint(1, 4) for _ in range(r.randint(1, 12))]}
                   for _ in range(6)],
    brute=_jump2_brute,
    checks=[({"nums": [2, 3, 1, 1, 4]}, 2), ({"nums": [0]}, 0), ({"nums": [2, 1]}, 1)],
    source="new_p")
