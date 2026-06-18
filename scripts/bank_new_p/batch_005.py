"""Batch 005 of the new_p.txt import (20 problems)."""
from scripts.build_bank import add, ilist, sstr  # noqa: F401

MOD = 10 ** 9 + 7


# --------------------------- brute / reference helpers ---------------------
def _factortrees_brute(arr):
    s = set(arr)
    from functools import lru_cache

    @lru_cache(None)
    def count(root):
        total = 1
        for a in arr:
            if root % a == 0 and root // a in s:
                total += count(a) * count(root // a)
        return total
    return sum(count(x) for x in arr) % MOD


def _pow_brute(x, n):
    return round(x ** n, 5)


def _zigzag_brute(nums):
    n = len(nums)

    def cost(start):
        res = 0
        for i in range(start, n, 2):
            left = nums[i - 1] if i > 0 else float('inf')
            right = nums[i + 1] if i + 1 < n else float('inf')
            target = min(left, right) - 1
            if nums[i] > target:
                res += nums[i] - target
        return res
    return min(cost(0), cost(1))


def _orsub_brute(arr):
    res = set()
    n = len(arr)
    for i in range(n):
        cur = 0
        for j in range(i, n):
            cur |= arr[j]
            res.add(cur)
    return len(res)


def _queue_brute(s, k):
    from collections import deque
    seen = {s}
    best = s
    dq = deque([s])
    while dq:
        cur = dq.popleft()
        if cur < best:
            best = cur
        for i in range(k):
            nxt = cur[:i] + cur[i + 1:] + cur[i]
            if nxt not in seen:
                seen.add(nxt)
                dq.append(nxt)
    return best


def _wpi_brute(hours):
    n = len(hours)
    best = 0
    for i in range(n):
        t = 0
        for j in range(i, n):
            t += 1 if hours[j] > 8 else -1
            if t > 0:
                best = max(best, j - i + 1)
    return best


def _grumpy_brute(customers, grumpy, X):
    n = len(customers)
    base = sum(c for c, g in zip(customers, grumpy) if g == 0)
    best = 0
    for start in range(0, max(1, n - X + 1)):
        extra = sum(customers[i] for i in range(start, min(start + X, n)) if grumpy[i] == 1)
        best = max(best, extra)
    return base + best


def _dupsub_brute(s):
    n = len(s)
    best = 0
    for i in range(n):
        for j in range(i + 1, n):
            L = 0
            while j + L < n and s[i + L] == s[j + L]:
                L += 1
            best = max(best, L)
    return best


def _fibsub_brute(arr):
    s = set(arr)
    n = len(arr)
    best = 0
    for i in range(n):
        for j in range(i + 1, n):
            a, b = arr[i], arr[j]
            length = 2
            while a + b in s:
                a, b = b, a + b
                length += 1
            if length >= 3:
                best = max(best, length)
    return best


def _hindex_brute(citations):
    n = len(citations)
    best = 0
    for h in range(n + 1):
        if sum(1 for c in citations if c >= h) >= h:
            best = max(best, h)
    return best


def _dominoes_brute(dominoes):
    state = dominoes
    while True:
        n = len(state)
        new = []
        for i in range(n):
            c = state[i]
            if c == '.':
                left = state[i - 1] if i > 0 else '.'
                right = state[i + 1] if i + 1 < n else '.'
                pr = left == 'R'
                pl = right == 'L'
                if pr and not pl:
                    new.append('R')
                elif pl and not pr:
                    new.append('L')
                else:
                    new.append('.')
            else:
                new.append(c)
        new = "".join(new)
        if new == state:
            return state
        state = new


def _squareful_brute(nums):
    from itertools import permutations
    from math import isqrt

    def is_sq(x):
        r = isqrt(x)
        return r * r == x
    count = 0
    for p in set(permutations(nums)):
        if all(is_sq(p[i] + p[i + 1]) for i in range(len(p) - 1)):
            count += 1
    return count


def _doubled_brute(arr):
    n = len(arr)
    if n % 2:
        return False
    arr = sorted(arr)
    used = [False] * n

    def bt():
        i = next((k for k in range(n) if not used[k]), None)
        if i is None:
            return True
        used[i] = True
        for j in range(n):
            if not used[j] and j != i and (arr[j] == 2 * arr[i] or arr[i] == 2 * arr[j]):
                used[j] = True
                if bt():
                    return True
                used[j] = False
        used[i] = False
        return False
    return bt()


def _teemo_brute(timeSeries, duration):
    intervals = sorted((t, t + duration) for t in timeSeries)
    if not intervals:
        return 0
    total = 0
    cs, ce = intervals[0]
    for s, e in intervals[1:]:
        if s <= ce:
            ce = max(ce, e)
        else:
            total += ce - cs
            cs, ce = s, e
    return total + ce - cs


def _minadd_brute(s):
    while '()' in s:
        s = s.replace('()', '')
    return len(s)


def _arith_brute(nums):
    n = len(nums)
    total = 0
    for i in range(n):
        for j in range(i + 2, n):
            d = nums[i + 1] - nums[i]
            if all(nums[k + 1] - nums[k] == d for k in range(i, j)):
                total += 1
    return total


def _gen_croak(r):
    nf = r.randint(1, 3)
    streams = [list("croak" * r.randint(1, 2)) for _ in range(nf)]
    res = []
    while any(streams):
        i = r.randrange(nf)
        if streams[i]:
            res.append(streams[i].pop(0))
    s = "".join(res)
    if r.random() < 0.3 and len(s) > 1:
        s = s[:-1]
    return {"croakOfFrogs": s if s else "c"}


# ===========================================================================
# 1. Split a String Into the Max Number of Unique Substrings
# ===========================================================================
add("split-a-string-into-the-max-number-of-unique-substrings",
    "Split a String Into the Max Number of Unique Substrings", "medium",
    ["string", "backtracking", "hash-table"], "maxUniqueSplit",
    [("s", "string")], "int",
    """
Split `s` into non-empty substrings whose concatenation is `s` and which are all
**distinct**. **Return the maximum number of substrings** such a split can have.

**Examples**
```
s = "ababccc"  ->  5    (e.g. ['a','b','ab','c','cc'])
s = "aba"      ->  2
s = "aa"       ->  1
```

**Constraints:** `1 <= len(s) <= 16`, lowercase letters.
""",
    """def maxUniqueSplit(s):
    n = len(s)
    best = [0]

    def bt(start, seen):
        if start == n:
            best[0] = max(best[0], len(seen))
            return
        if len(seen) + (n - start) <= best[0]:
            return
        for end in range(start + 1, n + 1):
            sub = s[start:end]
            if sub not in seen:
                seen.add(sub)
                bt(end, seen)
                seen.remove(sub)

    bt(0, set())
    return best[0]
""",
    visible=[{"s": "ababccc"}, {"s": "aba"}, {"s": "aa"}],
    hidden=[{"s": "a"}, {"s": "aaaaaaaaaa"}, {"s": "abcdefgh"}, {"s": "wwwzfvedwfvhsh"}],
    gen=lambda r: [{"s": sstr(r, 1, 10, "ab")} for _ in range(6)],
    checks=[({"s": "ababccc"}, 5), ({"s": "aba"}, 2), ({"s": "aa"}, 1),
            ({"s": "a"}, 1)],
    source="new_p")


# ===========================================================================
# 2. Binary Trees With Factors
# ===========================================================================
add("binary-trees-with-factors", "Binary Trees With Factors", "medium",
    ["array", "dynamic-programming", "hash-table"], "numFactoredBinaryTrees",
    [("arr", "int[]")], "int",
    """
Given distinct integers `arr` (each `> 1`), build binary trees where every non-leaf
node's value equals the **product of its two children** (values may be reused).
**Return the number of such trees**, modulo `10^9 + 7`.

**Examples**
```
arr = [2,4]        ->  3    ([2], [4], [4 -> 2,2])
arr = [2,4,5,10]   ->  7
```

**Constraints:** `1 <= len(arr) <= 1000`, `2 <= arr[i] <= 10^9`, all distinct.
""",
    """def numFactoredBinaryTrees(arr):
    MOD = 10 ** 9 + 7
    arr.sort()
    dp = {}
    for i, x in enumerate(arr):
        dp[x] = 1
        for j in range(i):
            y = arr[j]
            if x % y == 0 and x // y in dp:
                dp[x] = (dp[x] + dp[y] * dp[x // y]) % MOD
    return sum(dp.values()) % MOD
""",
    visible=[{"arr": [2, 4]}, {"arr": [2, 4, 5, 10]}],
    hidden=[{"arr": [2]}, {"arr": [2, 3, 5, 7]}, {"arr": [18, 3, 6, 2]},
            {"arr": [2, 4, 8, 16]}],
    gen=lambda r: [{"arr": r.sample(range(2, 40), r.randint(1, 7))} for _ in range(6)],
    brute=_factortrees_brute,
    checks=[({"arr": [2, 4]}, 3), ({"arr": [2, 4, 5, 10]}, 7), ({"arr": [2]}, 1)],
    source="new_p")


# ===========================================================================
# 3. Pow(x, n)
# ===========================================================================
add("powx-n", "Pow(x, n)", "medium", ["math", "recursion"], "myPow",
    [("x", "float"), ("n", "int")], "float",
    """
Implement `pow(x, n)` — `x` raised to the integer power `n`. **Return the result**
(rounded to 5 decimal places).

**Examples**
```
x = 2.0, n = 10  ->  1024.0
x = 2.1, n = 3   ->  9.261
x = 2.0, n = -2  ->  0.25
```

**Constraints:** `-100 < x < 100`, `n` is a 32-bit signed integer.
""",
    """def myPow(x, n):
    if n < 0:
        x = 1 / x
        n = -n
    result = 1.0
    while n:
        if n & 1:
            result *= x
        x *= x
        n >>= 1
    return round(result, 5)
""",
    visible=[{"x": 2.0, "n": 10}, {"x": 2.1, "n": 3}, {"x": 2.0, "n": -2}],
    hidden=[{"x": 1.0, "n": 2147483647}, {"x": 3.0, "n": 0}, {"x": 0.5, "n": 4},
            {"x": -2.0, "n": 3}, {"x": 2.0, "n": 1}],
    gen=lambda r: [{"x": round(r.uniform(0.5, 3.0), 2) * r.choice([-1, 1]),
                    "n": r.randint(-5, 6)} for _ in range(6)],
    brute=_pow_brute,
    checks=[({"x": 2.0, "n": 10}, 1024.0), ({"x": 2.1, "n": 3}, 9.261),
            ({"x": 2.0, "n": -2}, 0.25), ({"x": 3.0, "n": 0}, 1.0)],
    source="new_p")


# ===========================================================================
# 4. Decrease Elements To Make Array Zigzag
# ===========================================================================
add("decrease-elements-to-make-array-zigzag",
    "Decrease Elements To Make Array Zigzag", "medium",
    ["array", "greedy"], "movesToMakeZigzag", [("nums", "int[]")], "int",
    """
A move decreases any element by 1. The array is *zigzag* if either every
even-indexed element is greater than its neighbors, or every odd-indexed element is.
**Return the minimum number of moves** to make `nums` zigzag.

**Examples**
```
nums = [1,2,3]      ->  2
nums = [9,6,1,6,2]  ->  4
```

**Constraints:** `1 <= len(nums) <= 1000`, `1 <= nums[i] <= 1000`.
""",
    """def movesToMakeZigzag(nums):
    n = len(nums)

    def cost(start):
        res = 0
        for i in range(start, n, 2):
            left = nums[i - 1] if i > 0 else float('inf')
            right = nums[i + 1] if i + 1 < n else float('inf')
            target = min(left, right) - 1
            if nums[i] > target:
                res += nums[i] - target
        return res

    return min(cost(0), cost(1))
""",
    visible=[{"nums": [1, 2, 3]}, {"nums": [9, 6, 1, 6, 2]}],
    hidden=[{"nums": [1]}, {"nums": [2, 1]}, {"nums": [1, 1, 1, 1]},
            {"nums": [7, 4, 8, 9, 7, 7, 5]}],
    gen=lambda r: [{"nums": ilist(r, 1, 12, 1, 10)} for _ in range(6)],
    brute=_zigzag_brute,
    checks=[({"nums": [1, 2, 3]}, 2), ({"nums": [9, 6, 1, 6, 2]}, 4)],
    source="new_p")


# ===========================================================================
# 5. Check If It Is a Good Array
# ===========================================================================
add("check-if-it-is-a-good-array", "Check If It Is a Good Array", "hard",
    ["array", "math", "number-theory"], "isGoodArray", [("nums", "int[]")], "bool",
    """
You may pick a subset of `nums`, multiply each chosen value by any integer, and sum
them. The array is *good* if some such combination equals `1`. **Return `true` if
the array is good**, else `false`. (True iff `gcd` of all elements is `1`.)

**Examples**
```
nums = [12,5,7,23]  ->  true
nums = [29,6,10]    ->  true
nums = [3,6]        ->  false
```

**Constraints:** `1 <= len(nums) <= 10^5`, `1 <= nums[i] <= 10^9`.
""",
    """def isGoodArray(nums):
    from math import gcd
    from functools import reduce
    return reduce(gcd, nums) == 1
""",
    visible=[{"nums": [12, 5, 7, 23]}, {"nums": [29, 6, 10]}, {"nums": [3, 6]}],
    hidden=[{"nums": [1]}, {"nums": [2]}, {"nums": [6, 10, 15]}, {"nums": [4, 6, 8]}],
    gen=lambda r: [{"nums": [r.randint(1, 30) for _ in range(r.randint(1, 6))]}
                   for _ in range(6)],
    brute=lambda nums: __import__("math").gcd(*nums) == 1 if len(nums) > 1 else nums[0] == 1,
    checks=[({"nums": [12, 5, 7, 23]}, True), ({"nums": [29, 6, 10]}, True),
            ({"nums": [3, 6]}, False), ({"nums": [1]}, True)],
    source="new_p")


# ===========================================================================
# 6. Minimum Number of Frogs Croaking
# ===========================================================================
add("minimum-number-of-frogs-croaking", "Minimum Number of Frogs Croaking",
    "medium", ["string", "counting", "simulation"], "minNumberOfFrogs",
    [("croakOfFrogs", "string")], "int",
    """
`croakOfFrogs` is several `"croak"` strings interleaved (frogs croak concurrently).
Each frog prints `c, r, o, a, k` in order. **Return the minimum number of frogs**
needed to produce the string, or `-1` if it is not a valid interleaving of complete
`"croak"`s.

**Examples**
```
croakOfFrogs = "croakcroak"  ->  1
croakOfFrogs = "crcoakroak"  ->  2
croakOfFrogs = "croakcrook"  ->  -1
croakOfFrogs = "croakcroa"   ->  -1
```

**Constraints:** `1 <= len(croakOfFrogs) <= 10^5`, characters from `croak`.
""",
    """def minNumberOfFrogs(croakOfFrogs):
    if len(croakOfFrogs) % 5 != 0:
        return -1
    c = r = o = a = k = 0
    max_frogs = 0
    for ch in croakOfFrogs:
        if ch == 'c':
            c += 1
            max_frogs = max(max_frogs, c - k)
        elif ch == 'r':
            r += 1
            if r > c:
                return -1
        elif ch == 'o':
            o += 1
            if o > r:
                return -1
        elif ch == 'a':
            a += 1
            if a > o:
                return -1
        elif ch == 'k':
            k += 1
            if k > a:
                return -1
    if c == r == o == a == k:
        return max_frogs
    return -1
""",
    visible=[{"croakOfFrogs": "croakcroak"}, {"croakOfFrogs": "crcoakroak"},
             {"croakOfFrogs": "croakcrook"}],
    hidden=[{"croakOfFrogs": "croakcroa"}, {"croakOfFrogs": "croak"},
            {"croakOfFrogs": "ccrroakk"}, {"croakOfFrogs": "ccroakroakk"}],
    gen=lambda r: [_gen_croak(r) for _ in range(6)],
    checks=[({"croakOfFrogs": "croakcroak"}, 1), ({"croakOfFrogs": "crcoakroak"}, 2),
            ({"croakOfFrogs": "croakcrook"}, -1), ({"croakOfFrogs": "croakcroa"}, -1),
            ({"croakOfFrogs": "croak"}, 1)],
    source="new_p")


# ===========================================================================
# 7. Bitwise ORs of Subarrays
# ===========================================================================
add("bitwise-ors-of-subarrays", "Bitwise ORs of Subarrays", "medium",
    ["array", "bit-manipulation", "hash-table", "dynamic-programming"],
    "subarrayBitwiseORs", [("arr", "int[]")], "int",
    """
For every contiguous subarray of `arr`, take the bitwise OR of its elements.
**Return the number of distinct values** obtained.

**Examples**
```
arr = [0]      ->  1
arr = [1,1,2]  ->  3
arr = [1,2,4]  ->  6
```

**Constraints:** `1 <= len(arr) <= 5*10^4`, `0 <= arr[i] <= 10^9`.
""",
    """def subarrayBitwiseORs(arr):
    result = set()
    cur = set()
    for x in arr:
        cur = {x | y for y in cur} | {x}
        result |= cur
    return len(result)
""",
    visible=[{"arr": [0]}, {"arr": [1, 1, 2]}, {"arr": [1, 2, 4]}],
    hidden=[{"arr": [1]}, {"arr": [0, 0, 0]}, {"arr": [3, 1, 4, 1, 5, 9, 2]},
            {"arr": [(i * 7) % 16 for i in range(200)]}],
    gen=lambda r: [{"arr": ilist(r, 1, 12, 0, 15)} for _ in range(6)],
    brute=_orsub_brute,
    checks=[({"arr": [0]}, 1), ({"arr": [1, 1, 2]}, 3), ({"arr": [1, 2, 4]}, 6)],
    source="new_p")


# ===========================================================================
# 8. Orderly Queue
# ===========================================================================
add("orderly-queue", "Orderly Queue", "hard", ["string", "math", "sorting"],
    "orderlyQueue", [("s", "string"), ("k", "int")], "string",
    """
You may repeatedly take one of the first `k` characters of `s` and move it to the
end. **Return the lexicographically smallest string** obtainable.

**Examples**
```
s = "cba", k = 1    ->  "acb"
s = "baaca", k = 3  ->  "aaabc"
```

**Constraints:** `1 <= k <= len(s) <= 1000`, lowercase letters.
""",
    """def orderlyQueue(s, k):
    if k == 1:
        return min(s[i:] + s[:i] for i in range(len(s)))
    return "".join(sorted(s))
""",
    visible=[{"s": "cba", "k": 1}, {"s": "baaca", "k": 3}],
    hidden=[{"s": "a", "k": 1}, {"s": "ba", "k": 1}, {"s": "ba", "k": 2},
            {"s": "nhtq", "k": 1}, {"s": "tryhard", "k": 4}],
    gen=lambda r: [(lambda txt: {"s": txt, "k": r.randint(1, len(txt))})
                   (sstr(r, 1, 6, "abc")) for _ in range(6)],
    brute=_queue_brute,
    checks=[({"s": "cba", "k": 1}, "acb"), ({"s": "baaca", "k": 3}, "aaabc")],
    source="new_p")


# ===========================================================================
# 9. Longest Well-Performing Interval
# ===========================================================================
add("longest-well-performing-interval", "Longest Well-Performing Interval",
    "medium", ["array", "hash-table", "prefix-sum", "stack"], "longestWPI",
    [("hours", "int[]")], "int",
    """
A day is *tiring* if `hours[i] > 8`. A *well-performing interval* has strictly more
tiring days than non-tiring days. **Return the length of the longest
well-performing interval.**

**Example**
```
hours = [9,9,6,0,6,6,9]  ->  3
```

**Constraints:** `1 <= len(hours) <= 10^4`, `0 <= hours[i] <= 16`.
""",
    """def longestWPI(hours):
    score = 0
    best = 0
    seen = {}
    for i, h in enumerate(hours):
        score += 1 if h > 8 else -1
        if score > 0:
            best = i + 1
        elif score - 1 in seen:
            best = max(best, i - seen[score - 1])
        if score not in seen:
            seen[score] = i
    return best
""",
    visible=[{"hours": [9, 9, 6, 0, 6, 6, 9]}],
    hidden=[{"hours": [6]}, {"hours": [9]}, {"hours": [6, 6, 9]},
            {"hours": [9, 9, 9]}, {"hours": [9, 6, 9, 6, 9, 6, 9]}],
    gen=lambda r: [{"hours": [r.randint(0, 16) for _ in range(r.randint(1, 14))]}
                   for _ in range(6)],
    brute=_wpi_brute,
    checks=[({"hours": [9, 9, 6, 0, 6, 6, 9]}, 3)],
    source="new_p")


# ===========================================================================
# 10. Grumpy Bookstore Owner
# ===========================================================================
add("grumpy-bookstore-owner", "Grumpy Bookstore Owner", "medium",
    ["array", "sliding-window"], "maxSatisfied",
    [("customers", "int[]"), ("grumpy", "int[]"), ("X", "int")], "int",
    """
Over `n` minutes, `customers[i]` customers arrive in minute `i` and leave at its
end. If `grumpy[i] == 1` they are unsatisfied that minute. The owner can suppress
grumpiness for one window of `X` consecutive minutes. **Return the maximum number of
satisfied customers.**

**Example**
```
customers = [1,0,1,2,1,1,7,5], grumpy = [0,1,0,1,0,1,0,1], X = 3  ->  16
```

**Constraints:** `1 <= X <= len(customers) <= 2*10^4`, `0 <= customers[i] <= 1000`,
`grumpy[i]` in `{0,1}`.
""",
    """def maxSatisfied(customers, grumpy, X):
    n = len(customers)
    base = sum(customers[i] for i in range(n) if grumpy[i] == 0)
    extra = 0
    best = 0
    for i in range(n):
        if grumpy[i] == 1:
            extra += customers[i]
        if i >= X and grumpy[i - X] == 1:
            extra -= customers[i - X]
        best = max(best, extra)
    return base + best
""",
    visible=[{"customers": [1, 0, 1, 2, 1, 1, 7, 5],
              "grumpy": [0, 1, 0, 1, 0, 1, 0, 1], "X": 3}],
    hidden=[{"customers": [1], "grumpy": [0], "X": 1},
            {"customers": [1], "grumpy": [1], "X": 1},
            {"customers": [4, 10, 10], "grumpy": [1, 1, 0], "X": 2},
            {"customers": [2, 6, 6, 9], "grumpy": [0, 0, 1, 1], "X": 1}],
    gen=lambda r: [(lambda n: {"customers": [r.randint(0, 10) for _ in range(n)],
                               "grumpy": [r.randint(0, 1) for _ in range(n)],
                               "X": r.randint(1, n)})(r.randint(1, 10)) for _ in range(6)],
    brute=_grumpy_brute,
    checks=[({"customers": [1, 0, 1, 2, 1, 1, 7, 5],
              "grumpy": [0, 1, 0, 1, 0, 1, 0, 1], "X": 3}, 16)],
    source="new_p")


# ===========================================================================
# 11. Longest Duplicate Substring (length variant)
# ===========================================================================
add("longest-duplicate-substring", "Longest Duplicate Substring", "hard",
    ["string", "binary-search", "suffix-array", "hash-function"],
    "longestDupSubstring", [("s", "string")], "int",
    """
A *duplicated substring* is a contiguous substring that occurs at least twice
(occurrences may overlap). **Return the length of the longest duplicated
substring** (`0` if there is none).

**Examples**
```
s = "banana"  ->  3    ("ana")
s = "abcd"    ->  0
```

**Constraints:** `2 <= len(s) <= 10^5`, lowercase letters.
""",
    """def longestDupSubstring(s):
    n = len(s)
    lo, hi = 1, n - 1
    res = 0

    def has_dup(L):
        seen = set()
        for i in range(n - L + 1):
            sub = s[i:i + L]
            if sub in seen:
                return True
            seen.add(sub)
        return False

    while lo <= hi:
        mid = (lo + hi) // 2
        if has_dup(mid):
            res = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return res
""",
    visible=[{"s": "banana"}, {"s": "abcd"}],
    hidden=[{"s": "aa"}, {"s": "aaaaa"}, {"s": "abcabc"}, {"s": "mississippi"}],
    gen=lambda r: [{"s": sstr(r, 2, 20, "abc")} for _ in range(6)],
    brute=_dupsub_brute,
    checks=[({"s": "banana"}, 3), ({"s": "abcd"}, 0), ({"s": "aaaaa"}, 4),
            ({"s": "mississippi"}, 4)],
    source="new_p")


# ===========================================================================
# 12. Length of Longest Fibonacci Subsequence
# ===========================================================================
add("length-of-longest-fibonacci-subsequence",
    "Length of Longest Fibonacci Subsequence", "medium",
    ["array", "dynamic-programming", "hash-table"], "lenLongestFibSubseq",
    [("arr", "int[]")], "int",
    """
Given a strictly increasing array `arr`, **return the length of the longest
subsequence that is Fibonacci-like** (`X[i] + X[i+1] = X[i+2]`, length `>= 3`), or
`0` if none exists.

**Examples**
```
arr = [1,2,3,4,5,6,7,8]      ->  5    ([1,2,3,5,8])
arr = [1,3,7,11,12,14,18]    ->  3
```

**Constraints:** `3 <= len(arr) <= 1000`, strictly increasing positive integers.
""",
    """def lenLongestFibSubseq(arr):
    idx = {x: i for i, x in enumerate(arr)}
    n = len(arr)
    dp = {}
    best = 0
    for j in range(n):
        for i in range(j):
            prev = arr[j] - arr[i]
            if prev < arr[i] and prev in idx:
                k = idx[prev]
                dp[(i, j)] = dp.get((k, i), 2) + 1
                best = max(best, dp[(i, j)])
    return best
""",
    visible=[{"arr": [1, 2, 3, 4, 5, 6, 7, 8]}, {"arr": [1, 3, 7, 11, 12, 14, 18]}],
    hidden=[{"arr": [1, 2, 3]}, {"arr": [2, 4, 7, 8, 9, 10, 14, 15, 18, 23, 32, 50]},
            {"arr": [1, 5, 10, 20]}, {"arr": [1, 2, 4, 8, 16]}],
    gen=lambda r: [{"arr": sorted(r.sample(range(1, 60), r.randint(3, 10)))}
                   for _ in range(6)],
    brute=_fibsub_brute,
    checks=[({"arr": [1, 2, 3, 4, 5, 6, 7, 8]}, 5),
            ({"arr": [1, 3, 7, 11, 12, 14, 18]}, 3)],
    source="new_p")


# ===========================================================================
# 13. H-Index II
# ===========================================================================
add("h-index-ii", "H-Index II", "medium", ["array", "binary-search"], "hIndex",
    [("citations", "int[]")], "int",
    """
`citations` is sorted ascending; `citations[i]` is the citation count of a paper.
The **h-index** is the largest `h` such that `h` papers have at least `h` citations
each. **Return the h-index.** Aim for `O(log n)`.

**Example**
```
citations = [0,1,3,5,6]  ->  3
```

**Constraints:** `0 <= len(citations) <= 10^5`, sorted ascending,
`0 <= citations[i] <= 1000`.
""",
    """def hIndex(citations):
    n = len(citations)
    lo, hi = 0, n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if citations[mid] >= n - mid:
            hi = mid - 1
        else:
            lo = mid + 1
    return n - lo
""",
    visible=[{"citations": [0, 1, 3, 5, 6]}],
    hidden=[{"citations": []}, {"citations": [0]}, {"citations": [100]},
            {"citations": [0, 0]}, {"citations": [1, 2, 3, 4, 5]},
            {"citations": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}],
    gen=lambda r: [{"citations": sorted(r.randint(0, 12) for _ in range(r.randint(0, 10)))}
                   for _ in range(6)],
    brute=_hindex_brute,
    checks=[({"citations": [0, 1, 3, 5, 6]}, 3), ({"citations": []}, 0),
            ({"citations": [100]}, 1)],
    source="new_p")


# ===========================================================================
# 14. Push Dominoes
# ===========================================================================
add("push-dominoes", "Push Dominoes", "medium",
    ["string", "two-pointers", "dynamic-programming"], "pushDominoes",
    [("dominoes", "string")], "string",
    """
A row of dominoes is given as a string: `'L'` pushed left, `'R'` pushed right, `'.'`
upright. Each second, a falling domino pushes the adjacent upright one in its
direction; a domino pushed from both sides stays upright. **Return the final
state.**

**Examples**
```
".L.R...LR..L.."  ->  "LL.RR.LLRRLL.."
"RR.L"            ->  "RR.L"
```

**Constraints:** `0 <= len(dominoes) <= 10^5`, characters `L`, `R`, `.`.
""",
    """def pushDominoes(dominoes):
    n = len(dominoes)
    force = [0] * n
    f = 0
    for i in range(n):
        if dominoes[i] == 'R':
            f = n
        elif dominoes[i] == 'L':
            f = 0
        else:
            f = max(f - 1, 0)
        force[i] += f
    f = 0
    for i in range(n - 1, -1, -1):
        if dominoes[i] == 'L':
            f = n
        elif dominoes[i] == 'R':
            f = 0
        else:
            f = max(f - 1, 0)
        force[i] -= f
    return "".join('.' if x == 0 else ('R' if x > 0 else 'L') for x in force)
""",
    visible=[{"dominoes": ".L.R...LR..L.."}, {"dominoes": "RR.L"}],
    hidden=[{"dominoes": ""}, {"dominoes": "."}, {"dominoes": "R."},
            {"dominoes": ".L"}, {"dominoes": "R.R.L.L"}, {"dominoes": "RRR.LLL"}],
    gen=lambda r: [{"dominoes": "".join(r.choice("LR.") for _ in range(r.randint(0, 14)))}
                   for _ in range(6)],
    brute=_dominoes_brute,
    checks=[({"dominoes": ".L.R...LR..L.."}, "LL.RR.LLRRLL.."),
            ({"dominoes": "RR.L"}, "RR.L")],
    source="new_p")


# ===========================================================================
# 15. Number of Squareful Arrays
# ===========================================================================
add("number-of-squareful-arrays", "Number of Squareful Arrays", "hard",
    ["array", "backtracking", "bitmask", "math"], "numSquarefulPerms",
    [("nums", "int[]")], "int",
    """
An array is *squareful* if every pair of adjacent elements sums to a perfect square.
**Return the number of permutations of `nums` that are squareful.** Permutations
that are identical as sequences count once.

**Examples**
```
nums = [1,17,8]  ->  2    ([1,8,17] and [17,8,1])
nums = [2,2,2]   ->  1
```

**Constraints:** `1 <= len(nums) <= 12`, `0 <= nums[i] <= 10^9`.
""",
    """def numSquarefulPerms(nums):
    from math import isqrt
    from collections import Counter

    def is_sq(x):
        r = isqrt(x)
        return r * r == x

    cnt = Counter(nums)
    total = [0]

    def dfs(prev, remaining):
        if remaining == 0:
            total[0] += 1
            return
        for x in list(cnt):
            if cnt[x] > 0 and (prev is None or is_sq(prev + x)):
                cnt[x] -= 1
                dfs(x, remaining - 1)
                cnt[x] += 1

    dfs(None, len(nums))
    return total[0]
""",
    visible=[{"nums": [1, 17, 8]}, {"nums": [2, 2, 2]}],
    hidden=[{"nums": [0]}, {"nums": [1, 3]}, {"nums": [0, 0, 0]},
            {"nums": [2, 2, 2, 2, 2]}, {"nums": [1, 8, 17, 8]}],
    gen=lambda r: [{"nums": [r.choice([0, 1, 2, 3, 6, 8, 17]) for _ in range(r.randint(1, 6))]}
                   for _ in range(6)],
    brute=_squareful_brute,
    checks=[({"nums": [1, 17, 8]}, 2), ({"nums": [2, 2, 2]}, 1), ({"nums": [0]}, 1)],
    source="new_p")


# ===========================================================================
# 16. Maximum Number of Vowels in a Substring of Given Length
# ===========================================================================
add("maximum-number-of-vowels-in-a-substring-of-given-length",
    "Maximum Number of Vowels in a Substring of Given Length", "medium",
    ["string", "sliding-window"], "maxVowels",
    [("s", "string"), ("k", "int")], "int",
    """
**Return the maximum number of vowels (`a, e, i, o, u`) in any length-`k` substring
of `s`.**

**Examples**
```
s = "abciiidef", k = 3  ->  3
s = "aeiou", k = 2       ->  2
s = "leetcode", k = 3    ->  2
```

**Constraints:** `1 <= k <= len(s) <= 10^5`, lowercase letters.
""",
    """def maxVowels(s, k):
    vowels = set('aeiou')
    cur = sum(1 for c in s[:k] if c in vowels)
    best = cur
    for i in range(k, len(s)):
        cur += (s[i] in vowels) - (s[i - k] in vowels)
        best = max(best, cur)
    return best
""",
    visible=[{"s": "abciiidef", "k": 3}, {"s": "aeiou", "k": 2},
             {"s": "leetcode", "k": 3}],
    hidden=[{"s": "rhythms", "k": 4}, {"s": "tryhard", "k": 4}, {"s": "a", "k": 1},
            {"s": "b", "k": 1}, {"s": "aeiouaeiou", "k": 5}],
    gen=lambda r: [(lambda txt: {"s": txt, "k": r.randint(1, len(txt))})
                   (sstr(r, 1, 14, "abeiouxyz")) for _ in range(6)],
    brute=lambda s, k: max(sum(1 for c in s[i:i + k] if c in 'aeiou')
                           for i in range(len(s) - k + 1)),
    checks=[({"s": "abciiidef", "k": 3}, 3), ({"s": "aeiou", "k": 2}, 2),
            ({"s": "leetcode", "k": 3}, 2), ({"s": "rhythms", "k": 4}, 0)],
    source="new_p")


# ===========================================================================
# 17. Array of Doubled Pairs
# ===========================================================================
add("array-of-doubled-pairs", "Array of Doubled Pairs", "medium",
    ["array", "hash-table", "greedy", "sorting"], "canReorderDoubled",
    [("arr", "int[]")], "bool",
    """
**Return `true` if `arr` (even length) can be reordered so that
`arr[2*i+1] == 2 * arr[2*i]` for every `i`**, else `false`.

**Examples**
```
arr = [3,1,3,6]        ->  false
arr = [4,-2,2,-4]      ->  true
arr = [1,2,4,16,8,4]   ->  false
```

**Constraints:** `0 <= len(arr) <= 3*10^4` (even), `-10^5 <= arr[i] <= 10^5`.
""",
    """def canReorderDoubled(arr):
    from collections import Counter
    cnt = Counter(arr)
    for x in sorted(arr, key=abs):
        if cnt[x] == 0:
            continue
        if cnt[2 * x] == 0:
            return False
        cnt[x] -= 1
        cnt[2 * x] -= 1
    return True
""",
    visible=[{"arr": [3, 1, 3, 6]}, {"arr": [4, -2, 2, -4]}, {"arr": [1, 2, 4, 16, 8, 4]}],
    hidden=[{"arr": []}, {"arr": [2, 1, 2, 6]}, {"arr": [0, 0]},
            {"arr": [1, 2, 2, 4]}, {"arr": [2, 4, 0, 0, 8, 4]}],
    gen=lambda r: [{"arr": [r.randint(-6, 6) for _ in range(2 * r.randint(0, 4))]}
                   for _ in range(6)],
    brute=_doubled_brute,
    checks=[({"arr": [3, 1, 3, 6]}, False), ({"arr": [4, -2, 2, -4]}, True),
            ({"arr": [1, 2, 4, 16, 8, 4]}, False), ({"arr": []}, True)],
    source="new_p")


# ===========================================================================
# 18. Teemo Attacking
# ===========================================================================
add("teemo-attacking", "Teemo Attacking", "easy", ["array", "simulation"],
    "findPoisonedDuration", [("timeSeries", "int[]"), ("duration", "int")], "int",
    """
Each attack at time `timeSeries[i]` poisons for `duration` seconds (overlaps do not
stack). Given the strictly increasing `timeSeries` and `duration`, **return the
total time spent poisoned.**

**Examples**
```
timeSeries = [1,4], duration = 2  ->  4
timeSeries = [1,2], duration = 2  ->  3
```

**Constraints:** `0 <= len(timeSeries) <= 10^4`, strictly increasing,
`0 <= duration <= 10^7`.
""",
    """def findPoisonedDuration(timeSeries, duration):
    if not timeSeries:
        return 0
    total = 0
    for i in range(1, len(timeSeries)):
        total += min(duration, timeSeries[i] - timeSeries[i - 1])
    return total + duration
""",
    visible=[{"timeSeries": [1, 4], "duration": 2}, {"timeSeries": [1, 2], "duration": 2}],
    hidden=[{"timeSeries": [], "duration": 2}, {"timeSeries": [5], "duration": 3},
            {"timeSeries": [1, 2, 3, 4, 5], "duration": 1},
            {"timeSeries": [1, 10, 20], "duration": 5}],
    gen=lambda r: [(lambda ts: {"timeSeries": ts, "duration": r.randint(0, 8)})
                   (sorted(r.sample(range(0, 40), r.randint(0, 8)))) for _ in range(6)],
    brute=_teemo_brute,
    checks=[({"timeSeries": [1, 4], "duration": 2}, 4),
            ({"timeSeries": [1, 2], "duration": 2}, 3),
            ({"timeSeries": [], "duration": 2}, 0)],
    source="new_p")


# ===========================================================================
# 19. Minimum Add to Make Parentheses Valid
# ===========================================================================
add("minimum-add-to-make-parentheses-valid",
    "Minimum Add to Make Parentheses Valid", "medium",
    ["string", "stack", "greedy"], "minAddToMakeValid", [("s", "string")], "int",
    """
**Return the minimum number of parentheses to insert** (anywhere) so that the
string `s` of `'('` and `')'` becomes valid.

**Examples**
```
s = "())"     ->  1
s = "((("     ->  3
s = "()"      ->  0
s = "()))(("  ->  4
```

**Constraints:** `0 <= len(s) <= 1000`, characters `(` and `)`.
""",
    """def minAddToMakeValid(s):
    open_ = 0
    add = 0
    for c in s:
        if c == '(':
            open_ += 1
        elif open_ > 0:
            open_ -= 1
        else:
            add += 1
    return add + open_
""",
    visible=[{"s": "())"}, {"s": "((("}, {"s": "()"}, {"s": "()))(("}],
    hidden=[{"s": ""}, {"s": ")"}, {"s": "("}, {"s": "()()"}, {"s": "))(("}],
    gen=lambda r: [{"s": "".join(r.choice("()") for _ in range(r.randint(0, 12)))}
                   for _ in range(6)],
    brute=_minadd_brute,
    checks=[({"s": "())"}, 1), ({"s": "((("}, 3), ({"s": "()"}, 0),
            ({"s": "()))(("}, 4)],
    source="new_p")


# ===========================================================================
# 20. Arithmetic Slices
# ===========================================================================
add("arithmetic-slices", "Arithmetic Slices", "medium",
    ["array", "dynamic-programming"], "numberOfArithmeticSlices",
    [("nums", "int[]")], "int",
    """
An *arithmetic slice* is a contiguous subarray of length `>= 3` with a constant
difference between consecutive elements. **Return the number of arithmetic slices**
in `nums`.

**Example**
```
nums = [1,2,3,4]  ->  3    ([1,2,3], [2,3,4], [1,2,3,4])
```

**Constraints:** `1 <= len(nums) <= 5000`, `-1000 <= nums[i] <= 1000`.
""",
    """def numberOfArithmeticSlices(nums):
    n = len(nums)
    total = 0
    cur = 0
    for i in range(2, n):
        if nums[i] - nums[i - 1] == nums[i - 1] - nums[i - 2]:
            cur += 1
            total += cur
        else:
            cur = 0
    return total
""",
    visible=[{"nums": [1, 2, 3, 4]}],
    hidden=[{"nums": [1, 2, 3, 4, 5]}, {"nums": [7, 7, 7, 7]}, {"nums": [1, 3, 5, 7, 9]},
            {"nums": [1, 1, 2, 5, 7]}, {"nums": [1]}, {"nums": [3, -1, -5, -9]}],
    gen=lambda r: [{"nums": ilist(r, 1, 14, -5, 5)} for _ in range(6)],
    brute=_arith_brute,
    checks=[({"nums": [1, 2, 3, 4]}, 3), ({"nums": [1, 2, 3, 4, 5]}, 6),
            ({"nums": [7, 7, 7, 7]}, 3), ({"nums": [1, 3, 5, 7, 9]}, 6)],
    source="new_p")
