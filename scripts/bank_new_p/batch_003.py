"""Batch 003 of the new_p.txt import (20 problems)."""
from scripts.build_bank import add, ilist, sstr  # noqa: F401


# --------------------------- brute / reference helpers ---------------------
def _findword_brute(s, d):
    def is_sub(w):
        it = iter(s)
        return all(c in it for c in w)
    best = ""
    for w in d:
        if is_sub(w) and (len(w) > len(best) or (len(w) == len(best) and w < best)):
            best = w
    return best


def _minflips_brute(a, b, c):
    f = 0
    for i in range(32):
        ai, bi, ci = (a >> i) & 1, (b >> i) & 1, (c >> i) & 1
        if ci:
            if not (ai or bi):
                f += 1
        else:
            f += ai + bi
    return f


def _egg_brute(K, N):
    from functools import lru_cache

    @lru_cache(None)
    def f(k, n):
        if n == 0:
            return 0
        if k == 1:
            return n
        lo, hi = 1, n
        while lo < hi:
            mid = (lo + hi) // 2
            broke = f(k - 1, mid - 1)
            ok = f(k, n - mid)
            if broke >= ok:
                hi = mid
            else:
                lo = mid + 1
        return 1 + max(f(k - 1, lo - 1), f(k, n - lo))
    return f(K, N)


def _intbreak_brute(n):
    dp = [0] * (n + 1)
    for i in range(2, n + 1):
        for j in range(1, i):
            dp[i] = max(dp[i], j * (i - j), j * dp[i - j])
    return dp[n]


def _shortsub_brute(arr):
    n = len(arr)

    def ok(a):
        return all(a[i] <= a[i + 1] for i in range(len(a) - 1))
    best = n
    for i in range(n + 1):
        for j in range(i, n + 1):
            if ok(arr[:i] + arr[j:]):
                best = min(best, j - i)
    return best


def _maxdiff_brute(num):
    s = str(num)
    cands = set()
    for x in '0123456789':
        for y in '0123456789':
            t = s.replace(x, y)
            if t[0] != '0' and int(t) != 0:
                cands.add(int(t))
    return max(cands) - min(cands)


def _pairs_brute(arr, k):
    n = len(arr)
    used = [False] * n

    def bt():
        i = next((x for x in range(n) if not used[x]), None)
        if i is None:
            return True
        used[i] = True
        for j in range(n):
            if not used[j] and j != i and (arr[i] + arr[j]) % k == 0:
                used[j] = True
                if bt():
                    return True
                used[j] = False
        used[i] = False
        return False
    return bt()


def _consec_brute(n):
    return sum(1 for x in range(n + 1) if '11' not in bin(x))


def _scramble_brute(s1, s2):
    if len(s1) != len(s2):
        return False
    from functools import lru_cache

    @lru_cache(None)
    def scrambles(s):
        if len(s) == 1:
            return frozenset([s])
        res = set()
        for i in range(1, len(s)):
            for left in scrambles(s[:i]):
                for right in scrambles(s[i:]):
                    res.add(left + right)
                    res.add(right + left)
        return frozenset(res)
    return s2 in scrambles(s1)


def _rle_len(t):
    res = 0
    i = 0
    while i < len(t):
        j = i
        while j < len(t) and t[j] == t[i]:
            j += 1
        cnt = j - i
        res += 1 + (len(str(cnt)) if cnt > 1 else 0)
        i = j
    return res


def _strcomp_brute(s, k):
    from itertools import combinations
    n = len(s)
    best = float('inf')
    for d in range(0, k + 1):
        for dele in combinations(range(n), d):
            ds = set(dele)
            t = "".join(s[i] for i in range(n) if i not in ds)
            best = min(best, _rle_len(t))
    return best


def _refuel_brute(target, startFuel, stations):
    n = len(stations)
    dp = [startFuel] + [0] * n
    for pos, fuel in stations:
        for t in range(n, 0, -1):
            if dp[t - 1] >= pos:
                dp[t] = max(dp[t], dp[t - 1] + fuel)
    for t in range(n + 1):
        if dp[t] >= target:
            return t
    return -1


def _cooldown_brute(prices):
    n = len(prices)
    from functools import lru_cache

    @lru_cache(None)
    def dp(i, holding):
        if i >= n:
            return 0
        best = dp(i + 1, holding)
        if holding:
            best = max(best, prices[i] + dp(i + 2, False))
        else:
            best = max(best, -prices[i] + dp(i + 1, True))
        return best
    return dp(0, False)


def _trap_brute(height):
    n = len(height)
    res = 0
    for i in range(n):
        lm = max(height[:i + 1])
        rm = max(height[i:])
        res += min(lm, rm) - height[i]
    return res


def _dot_brute(nums1, nums2):
    from itertools import combinations
    best = float('-inf')
    m, n = len(nums1), len(nums2)
    for L in range(1, min(m, n) + 1):
        for ci in combinations(range(m), L):
            for cj in combinations(range(n), L):
                best = max(best, sum(nums1[ci[t]] * nums2[cj[t]] for t in range(L)))
    return best


def _swaprep_brute(text):
    n = len(text)

    def longest(t):
        if n == 0:
            return 0
        best = 1
        i = 0
        while i < n:
            j = i
            while j < n and t[j] == t[i]:
                j += 1
            best = max(best, j - i)
            i = j
        return best
    best = longest(text)
    for i in range(n):
        for j in range(n):
            t = list(text)
            t[i], t[j] = t[j], t[i]
            best = max(best, longest("".join(t)))
    return best


def _codes_brute(s, k):
    from itertools import product
    for bits in product('01', repeat=k):
        if "".join(bits) not in s:
            return False
    return True


def _largestnum_brute(cost, target):
    dp = [-1] * (target + 1)
    dp[0] = 0
    for t in range(1, target + 1):
        for c in cost:
            if t >= c and dp[t - c] != -1:
                dp[t] = max(dp[t], dp[t - c] + 1)
    if dp[target] == -1:
        return "0"
    digits = []
    t = target
    while t > 0:
        for d in range(9, 0, -1):
            c = cost[d - 1]
            if t >= c and dp[t - c] == dp[t] - 1:
                digits.append(d)
                t -= c
                break
    return "".join(map(str, digits))


# ===========================================================================
# 1. Longest Word in Dictionary through Deleting
# ===========================================================================
add("longest-word-in-dictionary-through-deleting",
    "Longest Word in Dictionary through Deleting", "medium",
    ["array", "string", "two-pointers", "sorting"], "findLongestWord",
    [("s", "string"), ("d", "string[]")], "string",
    """
Given a string `s` and a list of words `d`, **return the longest word in `d` that
is a subsequence of `s`**. If several share the longest length, return the
lexicographically smallest. If none qualifies, return `""`.

**Examples**
```
s = "abpcplea", d = ["ale","apple","monkey","plea"]  ->  "apple"
s = "abpcplea", d = ["a","b","c"]                     ->  "a"
```

**Constraints:** `1 <= len(s) <= 1000`, `1 <= len(d) <= 1000`, lowercase letters.
""",
    """def findLongestWord(s, d):
    def is_sub(w):
        it = iter(s)
        return all(c in it for c in w)
    best = ""
    for w in d:
        if is_sub(w) and (len(w) > len(best) or (len(w) == len(best) and w < best)):
            best = w
    return best
""",
    visible=[{"s": "abpcplea", "d": ["ale", "apple", "monkey", "plea"]},
             {"s": "abpcplea", "d": ["a", "b", "c"]}],
    hidden=[{"s": "abc", "d": ["d", "e"]}, {"s": "bab", "d": ["ba", "ab", "a"]},
            {"s": "aaa", "d": ["aaa", "aa", "a"]}, {"s": "x", "d": ["x"]}],
    gen=lambda r: [{"s": sstr(r, 1, 10, "abc"),
                    "d": [sstr(r, 1, 4, "abc") for _ in range(r.randint(1, 5))]}
                   for _ in range(6)],
    brute=_findword_brute,
    checks=[({"s": "abpcplea", "d": ["ale", "apple", "monkey", "plea"]}, "apple"),
            ({"s": "abpcplea", "d": ["a", "b", "c"]}, "a")],
    source="new_p")


# ===========================================================================
# 2. Minimum Flips to Make a OR b Equal to c
# ===========================================================================
add("minimum-flips-to-make-a-or-b-equal-to-c",
    "Minimum Flips to Make a OR b Equal to c", "medium",
    ["bit-manipulation"], "minFlips",
    [("a", "int"), ("b", "int"), ("c", "int")], "int",
    """
Given positive integers `a`, `b`, `c`, **return the minimum number of bit flips**
(each flip toggles a single bit of `a` or `b`) needed so that `a OR b == c`.

**Examples**
```
a = 2, b = 6, c = 5  ->  3
a = 4, b = 2, c = 7  ->  1
a = 1, b = 2, c = 3  ->  0
```

**Constraints:** `1 <= a, b, c <= 10^9`.
""",
    """def minFlips(a, b, c):
    flips = 0
    while a or b or c:
        ai, bi, ci = a & 1, b & 1, c & 1
        if ci == 0:
            flips += ai + bi
        elif ai == 0 and bi == 0:
            flips += 1
        a >>= 1
        b >>= 1
        c >>= 1
    return flips
""",
    visible=[{"a": 2, "b": 6, "c": 5}, {"a": 4, "b": 2, "c": 7},
             {"a": 1, "b": 2, "c": 3}],
    hidden=[{"a": 1, "b": 1, "c": 1}, {"a": 8, "b": 3, "c": 5},
            {"a": 1000000000, "b": 1, "c": 1}, {"a": 7, "b": 7, "c": 0}],
    gen=lambda r: [{"a": r.randint(1, 255), "b": r.randint(1, 255),
                    "c": r.randint(1, 255)} for _ in range(6)],
    brute=_minflips_brute,
    checks=[({"a": 2, "b": 6, "c": 5}, 3), ({"a": 4, "b": 2, "c": 7}, 1),
            ({"a": 1, "b": 2, "c": 3}, 0)],
    source="new_p")


# ===========================================================================
# 3. Super Egg Drop
# ===========================================================================
add("super-egg-drop", "Super Egg Drop", "hard",
    ["math", "dynamic-programming", "binary-search"], "superEggDrop",
    [("K", "int"), ("N", "int")], "int",
    """
You have `K` identical eggs and a building with `N` floors. There is a floor `F`
(`0 <= F <= N`) such that an egg breaks if dropped from any floor above `F` and
survives at or below it. Each move you drop one egg from a chosen floor; a broken
egg can't be reused. **Return the minimum number of moves** that guarantees you
determine `F`, in the worst case.

**Examples**
```
K = 1, N = 2   ->  2
K = 2, N = 6   ->  3
K = 3, N = 14  ->  4
```

**Constraints:** `1 <= K <= 100`, `1 <= N <= 10^4`.
""",
    """def superEggDrop(K, N):
    dp = [0] * (K + 1)
    m = 0
    while dp[K] < N:
        m += 1
        for k in range(K, 0, -1):
            dp[k] = dp[k] + dp[k - 1] + 1
    return m
""",
    visible=[{"K": 1, "N": 2}, {"K": 2, "N": 6}, {"K": 3, "N": 14}],
    hidden=[{"K": 1, "N": 1}, {"K": 2, "N": 1}, {"K": 5, "N": 30},
            {"K": 2, "N": 100}],
    gen=lambda r: [{"K": r.randint(1, 4), "N": r.randint(1, 25)} for _ in range(6)],
    brute=_egg_brute,
    checks=[({"K": 1, "N": 2}, 2), ({"K": 2, "N": 6}, 3), ({"K": 3, "N": 14}, 4),
            ({"K": 2, "N": 100}, 14), ({"K": 100, "N": 10000}, 14)],
    source="new_p")


# ===========================================================================
# 4. Construct K Palindrome Strings
# ===========================================================================
add("construct-k-palindrome-strings", "Construct K Palindrome Strings", "medium",
    ["string", "greedy", "hash-table", "counting"], "canConstruct",
    [("s", "string"), ("k", "int")], "bool",
    """
**Return `true` if all the characters of `s` can be used to build exactly `k`
non-empty palindrome strings**, else `false`. (Possible iff `k <= len(s)` and the
number of characters with odd frequency is at most `k`.)

**Examples**
```
s = "annabelle", k = 2  ->  true
s = "leetcode", k = 3    ->  false
s = "true", k = 4        ->  true
s = "cr", k = 7          ->  false
```

**Constraints:** `1 <= len(s) <= 10^5`, lowercase letters, `1 <= k <= 10^5`.
""",
    """def canConstruct(s, k):
    from collections import Counter
    if len(s) < k:
        return False
    odd = sum(v % 2 for v in Counter(s).values())
    return odd <= k
""",
    visible=[{"s": "annabelle", "k": 2}, {"s": "leetcode", "k": 3},
             {"s": "true", "k": 4}],
    hidden=[{"s": "yzyzyzyzyzyzyzy", "k": 2}, {"s": "cr", "k": 7},
            {"s": "a", "k": 1}, {"s": "aab", "k": 1}, {"s": "aab", "k": 2}],
    gen=lambda r: [{"s": sstr(r, 1, 12, "abc"), "k": r.randint(1, 12)}
                   for _ in range(6)],
    checks=[({"s": "annabelle", "k": 2}, True), ({"s": "leetcode", "k": 3}, False),
            ({"s": "true", "k": 4}, True), ({"s": "yzyzyzyzyzyzyzy", "k": 2}, True),
            ({"s": "cr", "k": 7}, False), ({"s": "aab", "k": 1}, True),
            ({"s": "aabb", "k": 1}, True), ({"s": "abc", "k": 1}, False)],
    source="new_p")


# ===========================================================================
# 5. Integer Break
# ===========================================================================
add("integer-break", "Integer Break", "medium",
    ["math", "dynamic-programming"], "integerBreak", [("n", "int")], "int",
    """
Given an integer `n`, break it into the sum of **at least two** positive integers
and **maximize the product** of those integers. **Return the maximum product.**

**Examples**
```
n = 2   ->  1    (2 = 1 + 1)
n = 10  ->  36   (10 = 3 + 3 + 4)
```

**Constraints:** `2 <= n <= 58`.
""",
    """def integerBreak(n):
    if n <= 3:
        return n - 1
    q, r = divmod(n, 3)
    if r == 0:
        return 3 ** q
    if r == 1:
        return 3 ** (q - 1) * 4
    return 3 ** q * 2
""",
    visible=[{"n": 2}, {"n": 10}],
    hidden=[{"n": 3}, {"n": 4}, {"n": 7}, {"n": 8}, {"n": 58}],
    gen=lambda r: [{"n": r.randint(2, 58)} for _ in range(6)],
    brute=_intbreak_brute,
    checks=[({"n": 2}, 1), ({"n": 10}, 36), ({"n": 3}, 2), ({"n": 8}, 18)],
    source="new_p")


# ===========================================================================
# 6. Shortest Subarray to be Removed to Make Array Sorted
# ===========================================================================
add("shortest-subarray-to-be-removed-to-make-array-sorted",
    "Shortest Subarray to be Removed to Make Array Sorted", "medium",
    ["array", "two-pointers", "binary-search", "stack"],
    "findLengthOfShortestSubarray", [("arr", "int[]")], "int",
    """
Remove one contiguous subarray (possibly empty) from `arr` so the remaining
elements are non-decreasing. **Return the length of the shortest such subarray.**

**Examples**
```
arr = [1,2,3,10,4,2,3,5]  ->  3    (remove [10,4,2])
arr = [5,4,3,2,1]         ->  4
arr = [1,2,3]             ->  0
```

**Constraints:** `1 <= len(arr) <= 10^5`, `0 <= arr[i] <= 10^9`.
""",
    """def findLengthOfShortestSubarray(arr):
    n = len(arr)
    left = 0
    while left + 1 < n and arr[left] <= arr[left + 1]:
        left += 1
    if left == n - 1:
        return 0
    right = n - 1
    while right > 0 and arr[right - 1] <= arr[right]:
        right -= 1
    res = min(n - left - 1, right)
    i, j = 0, right
    while i <= left and j < n:
        if arr[i] <= arr[j]:
            res = min(res, j - i - 1)
            i += 1
        else:
            j += 1
    return res
""",
    visible=[{"arr": [1, 2, 3, 10, 4, 2, 3, 5]}, {"arr": [5, 4, 3, 2, 1]},
             {"arr": [1, 2, 3]}],
    hidden=[{"arr": [1]}, {"arr": [2, 2, 2]}, {"arr": [1, 2, 3, 4, 3, 2, 1]},
            {"arr": [16, 10, 0, 3, 22, 1, 14, 7, 1, 12, 15]}],
    gen=lambda r: [{"arr": ilist(r, 1, 12, 0, 8)} for _ in range(6)],
    brute=_shortsub_brute,
    checks=[({"arr": [1, 2, 3, 10, 4, 2, 3, 5]}, 3), ({"arr": [5, 4, 3, 2, 1]}, 4),
            ({"arr": [1, 2, 3]}, 0), ({"arr": [1]}, 0)],
    source="new_p")


# ===========================================================================
# 7. Max Difference You Can Get From Changing an Integer
# ===========================================================================
add("max-difference-you-can-get-from-changing-an-integer",
    "Max Difference You Can Get From Changing an Integer", "medium",
    ["math", "greedy"], "maxDiff", [("num", "int")], "int",
    """
Apply this operation **twice independently** to `num`: pick a digit `x` and a digit
`y`, and replace every `x` with `y`. The result must have no leading zero and not be
`0`. Let `a` and `b` be the two results. **Return the maximum value of `a - b`.**

**Examples**
```
num = 555     ->  888   (a = 999, b = 111)
num = 9       ->  8
num = 123456  ->  820000
num = 10000   ->  80000
```

**Constraints:** `1 <= num <= 10^8`.
""",
    """def maxDiff(num):
    s = str(num)
    a = s
    for ch in s:
        if ch != '9':
            a = s.replace(ch, '9')
            break
    if s[0] != '1':
        b = s.replace(s[0], '1')
    else:
        b = s
        for ch in s[1:]:
            if ch != '0' and ch != s[0]:
                b = s.replace(ch, '0')
                break
    return int(a) - int(b)
""",
    visible=[{"num": 555}, {"num": 9}, {"num": 123456}],
    hidden=[{"num": 10000}, {"num": 9288}, {"num": 1}, {"num": 100000000},
            {"num": 1101}],
    gen=lambda r: [{"num": r.randint(1, 100000000)} for _ in range(6)],
    brute=_maxdiff_brute,
    checks=[({"num": 555}, 888), ({"num": 9}, 8), ({"num": 123456}, 820000),
            ({"num": 10000}, 80000), ({"num": 9288}, 8700)],
    source="new_p")


# ===========================================================================
# 8. Check If Array Pairs Are Divisible by k
# ===========================================================================
add("check-if-array-pairs-are-divisible-by-k",
    "Check If Array Pairs Are Divisible by k", "medium",
    ["array", "hash-table", "counting"], "canArrange",
    [("arr", "int[]"), ("k", "int")], "bool",
    """
Given an array `arr` of even length, **return `true` if it can be split into
`len(arr)/2` pairs where each pair's sum is divisible by `k`**, else `false`.

**Examples**
```
arr = [1,2,3,4,5,10,6,7,8,9], k = 5  ->  true
arr = [1,2,3,4,5,6], k = 7           ->  true
arr = [1,2,3,4,5,6], k = 10          ->  false
arr = [-10,10], k = 2                ->  true
```

**Constraints:** `len(arr)` is even, `1 <= len(arr) <= 10^5`,
`-10^9 <= arr[i] <= 10^9`, `1 <= k <= 10^5`.
""",
    """def canArrange(arr, k):
    from collections import Counter
    cnt = Counter(x % k for x in arr)
    for r in range(k):
        if r == 0:
            if cnt[0] % 2:
                return False
        elif cnt[r] != cnt[k - r]:
            return False
    return True
""",
    visible=[{"arr": [1, 2, 3, 4, 5, 10, 6, 7, 8, 9], "k": 5},
             {"arr": [1, 2, 3, 4, 5, 6], "k": 7},
             {"arr": [1, 2, 3, 4, 5, 6], "k": 10}],
    hidden=[{"arr": [-10, 10], "k": 2}, {"arr": [-1, 1, -2, 2, -3, 3, -4, 4], "k": 3},
            {"arr": [1, 1], "k": 2}, {"arr": [2, 2], "k": 3}],
    gen=lambda r: [(lambda k: {"arr": [r.randint(-12, 12) for _ in range(2 * r.randint(1, 5))],
                               "k": k})(r.randint(2, 7)) for _ in range(6)],
    brute=_pairs_brute,
    checks=[({"arr": [1, 2, 3, 4, 5, 10, 6, 7, 8, 9], "k": 5}, True),
            ({"arr": [1, 2, 3, 4, 5, 6], "k": 7}, True),
            ({"arr": [1, 2, 3, 4, 5, 6], "k": 10}, False),
            ({"arr": [-10, 10], "k": 2}, True)],
    source="new_p")


# ===========================================================================
# 9. Longest Absolute File Path
# ===========================================================================
add("longest-absolute-file-path", "Longest Absolute File Path", "medium",
    ["string", "stack", "depth-first-search"], "lengthLongestPath",
    [("s", "string")], "int",
    """
A file system is encoded in a single string `s`. Lines are separated by `\\n`; the
number of leading `\\t` (tab) characters on a line is its depth. A name containing a
`.` is a file; otherwise it is a directory. **Return the length of the longest
absolute path to a file** (joining names with `/`), or `0` if there is no file.

**Examples**
```
s = "dir\\n\\tsubdir1\\n\\tsubdir2\\n\\t\\tfile.ext"  ->  20   ("dir/subdir2/file.ext")
s = "dir\\n\\tsubdir1\\n\\t\\tfile1.ext\\n\\t\\tsubsubdir1\\n\\tsubdir2\\n\\t\\tsubsubdir2\\n\\t\\t\\tfile2.ext"
    ->  32   ("dir/subdir2/subsubdir2/file2.ext")
```

**Constraints:** a file name has at least one `.`; directory names have none.
""",
    """def lengthLongestPath(s):
    maxlen = 0
    depth_len = {0: 0}
    for line in s.split('\\n'):
        name = line.lstrip('\\t')
        depth = len(line) - len(name)
        if '.' in name:
            maxlen = max(maxlen, depth_len[depth] + len(name))
        else:
            depth_len[depth + 1] = depth_len[depth] + len(name) + 1
    return maxlen
""",
    visible=[{"s": "dir\n\tsubdir1\n\tsubdir2\n\t\tfile.ext"},
             {"s": "dir\n\tsubdir1\n\t\tfile1.ext\n\t\tsubsubdir1\n\tsubdir2\n\t\tsubsubdir2\n\t\t\tfile2.ext"}],
    hidden=[{"s": "a"}, {"s": "file.txt"}, {"s": "dir\n\tfile.ext"},
            {"s": "a\n\tb\n\t\tc.d"}],
    checks=[({"s": "dir\n\tsubdir1\n\tsubdir2\n\t\tfile.ext"}, 20),
            ({"s": "dir\n\tsubdir1\n\t\tfile1.ext\n\t\tsubsubdir1\n\tsubdir2\n\t\tsubsubdir2\n\t\t\tfile2.ext"}, 32),
            ({"s": "a"}, 0), ({"s": "file.txt"}, 8),
            ({"s": "dir\n\tfile.ext"}, 12)],
    source="new_p")


# ===========================================================================
# 10. Non-negative Integers without Consecutive Ones
# ===========================================================================
add("non-negative-integers-without-consecutive-ones",
    "Non-negative Integers without Consecutive Ones", "hard",
    ["dynamic-programming", "bit-manipulation"], "findIntegers",
    [("n", "int")], "int",
    """
Given a positive integer `n`, **return how many integers in `[0, n]` have a binary
representation with no two consecutive `1`s**.

**Examples**
```
n = 5  ->  5    (0, 1, 2, 4, 5 qualify; 3 = "11" does not)
n = 1  ->  2    (0, 1)
n = 2  ->  3    (0, 1, 2)
```

**Constraints:** `1 <= n <= 10^9`.
""",
    """def findIntegers(n):
    fib = [1, 2]
    for i in range(2, 32):
        fib.append(fib[-1] + fib[-2])
    res = 0
    prev_bit = 0
    for i in range(30, -1, -1):
        if (n >> i) & 1:
            res += fib[i]
            if prev_bit == 1:
                return res
            prev_bit = 1
        else:
            prev_bit = 0
    return res + 1
""",
    visible=[{"n": 5}, {"n": 1}, {"n": 2}],
    hidden=[{"n": 3}, {"n": 8}, {"n": 100}, {"n": 1000}, {"n": 5000}],
    gen=lambda r: [{"n": r.randint(1, 2000)} for _ in range(6)],
    brute=_consec_brute,
    checks=[({"n": 5}, 5), ({"n": 1}, 2), ({"n": 2}, 3), ({"n": 3}, 3)],
    source="new_p")


# ===========================================================================
# 11. Scramble String
# ===========================================================================
add("scramble-string", "Scramble String", "hard",
    ["string", "dynamic-programming"], "isScramble",
    [("s1", "string"), ("s2", "string")], "bool",
    """
A string can be turned into a *scramble* by recursively splitting it into two
non-empty parts and optionally swapping them, applied at any node. Given `s1` and
`s2` of equal length, **return `true` if `s2` is a scramble of `s1`**.

**Examples**
```
s1 = "great", s2 = "rgeat"  ->  true
s1 = "abcde", s2 = "caebd"  ->  false
s1 = "a",     s2 = "a"      ->  true
```

**Constraints:** `1 <= len(s1) == len(s2) <= 30`, lowercase letters.
""",
    """def isScramble(s1, s2):
    from functools import lru_cache

    @lru_cache(None)
    def helper(a, b):
        if a == b:
            return True
        if sorted(a) != sorted(b):
            return False
        n = len(a)
        for i in range(1, n):
            if helper(a[:i], b[:i]) and helper(a[i:], b[i:]):
                return True
            if helper(a[:i], b[n - i:]) and helper(a[i:], b[:n - i]):
                return True
        return False

    return helper(s1, s2)
""",
    visible=[{"s1": "great", "s2": "rgeat"}, {"s1": "abcde", "s2": "caebd"},
             {"s1": "a", "s2": "a"}],
    hidden=[{"s1": "abc", "s2": "abc"}, {"s1": "ab", "s2": "ba"},
            {"s1": "abcd", "s2": "bdac"}, {"s1": "abb", "s2": "bba"}],
    gen=lambda r: [(lambda n: {"s1": sstr(r, n, n, "ab"), "s2": sstr(r, n, n, "ab")})
                   (r.randint(1, 5)) for _ in range(6)],
    brute=_scramble_brute,
    checks=[({"s1": "great", "s2": "rgeat"}, True),
            ({"s1": "abcde", "s2": "caebd"}, False), ({"s1": "a", "s2": "a"}, True)],
    source="new_p")


# ===========================================================================
# 12. String Compression II
# ===========================================================================
add("string-compression-ii", "String Compression II", "hard",
    ["string", "dynamic-programming"], "getLengthOfOptimalCompression",
    [("s", "string"), ("k", "int")], "int",
    """
Run-length encoding replaces each maximal run of a repeated character with the
character followed by the run length (a single character stays as-is, e.g. `"aabccc"`
-> `"a2bc3"`). Deleting **at most `k`** characters from `s`, **return the minimum
possible length** of the run-length encoding of what remains.

**Examples**
```
s = "aaabcccd", k = 2     ->  4    (delete b,d -> "a3c3")
s = "aabbaa", k = 2        ->  2    (delete the b's -> "a4")
s = "aaaaaaaaaaa", k = 0   ->  3    ("a11")
```

**Constraints:** `1 <= len(s) <= 100`, `0 <= k <= len(s)`, lowercase letters.
""",
    """def getLengthOfOptimalCompression(s, k):
    from functools import lru_cache
    n = len(s)

    @lru_cache(None)
    def dp(i, prev, prev_cnt, k):
        if k < 0:
            return float('inf')
        if i == n:
            return 0
        res = dp(i + 1, prev, prev_cnt, k - 1)
        if s[i] == prev:
            incr = 1 if prev_cnt in (1, 9, 99) else 0
            res = min(res, incr + dp(i + 1, prev, prev_cnt + 1, k))
        else:
            res = min(res, 1 + dp(i + 1, s[i], 1, k))
        return res

    return dp(0, '', 0, k)
""",
    visible=[{"s": "aaabcccd", "k": 2}, {"s": "aabbaa", "k": 2},
             {"s": "aaaaaaaaaaa", "k": 0}],
    hidden=[{"s": "a", "k": 0}, {"s": "abc", "k": 3}, {"s": "aaa", "k": 1},
            {"s": "babbbbb", "k": 1}, {"s": "ababccdeee", "k": 4}],
    gen=lambda r: [(lambda txt: {"s": txt, "k": r.randint(0, len(txt))})
                   (sstr(r, 1, 10, "ab")) for _ in range(6)],
    brute=_strcomp_brute,
    checks=[({"s": "aaabcccd", "k": 2}, 4), ({"s": "aabbaa", "k": 2}, 2),
            ({"s": "aaaaaaaaaaa", "k": 0}, 3)],
    source="new_p")


# ===========================================================================
# 13. Minimum Number of Refueling Stops
# ===========================================================================
add("minimum-number-of-refueling-stops", "Minimum Number of Refueling Stops",
    "hard", ["array", "dynamic-programming", "greedy", "heap"], "minRefuelStops",
    [("target", "int"), ("startFuel", "int"), ("stations", "int[][]")], "int",
    """
A car must drive `target` miles starting with `startFuel` liters (1 liter per
mile). `stations[i] = [position, fuel]` is a station `position` miles from the
start holding `fuel` liters; stopping there adds all its fuel. **Return the minimum
number of stops** to reach `target`, or `-1` if impossible.

**Examples**
```
target = 1,   startFuel = 1,  stations = []                            ->  0
target = 100, startFuel = 1,  stations = [[10,100]]                    ->  -1
target = 100, startFuel = 10, stations = [[10,60],[20,30],[30,30],[60,40]] ->  2
```

**Constraints:** `1 <= target, startFuel, stations[i][1] <= 10^9`,
`0 <= len(stations) <= 500`, station positions strictly increasing and `< target`.
""",
    """def minRefuelStops(target, startFuel, stations):
    import heapq
    heap = []
    fuel = startFuel
    stops = 0
    i = 0
    n = len(stations)
    while fuel < target:
        while i < n and stations[i][0] <= fuel:
            heapq.heappush(heap, -stations[i][1])
            i += 1
        if not heap:
            return -1
        fuel += -heapq.heappop(heap)
        stops += 1
    return stops
""",
    visible=[{"target": 1, "startFuel": 1, "stations": []},
             {"target": 100, "startFuel": 1, "stations": [[10, 100]]},
             {"target": 100, "startFuel": 10,
              "stations": [[10, 60], [20, 30], [30, 30], [60, 40]]}],
    hidden=[{"target": 1000, "startFuel": 299,
             "stations": [[13, 21], [26, 115], [100, 47], [225, 99], [299, 141],
                          [444, 198], [608, 190], [636, 157], [647, 255], [841, 123]]},
            {"target": 5, "startFuel": 5, "stations": []},
            {"target": 10, "startFuel": 3, "stations": [[4, 3]]}],
    gen=lambda r: [(lambda t: {"target": t, "startFuel": r.randint(1, t),
                               "stations": [[p, r.randint(1, 15)] for p in
                                            sorted(r.sample(range(1, t), r.randint(0, min(5, t - 1))))]})
                   (r.randint(5, 40)) for _ in range(6)],
    brute=_refuel_brute,
    checks=[({"target": 1, "startFuel": 1, "stations": []}, 0),
            ({"target": 100, "startFuel": 1, "stations": [[10, 100]]}, -1),
            ({"target": 100, "startFuel": 10,
              "stations": [[10, 60], [20, 30], [30, 30], [60, 40]]}, 2)],
    source="new_p")


# ===========================================================================
# 14. Best Time to Buy and Sell Stock with Cooldown
# ===========================================================================
add("best-time-to-buy-and-sell-stock-with-cooldown",
    "Best Time to Buy and Sell Stock with Cooldown", "medium",
    ["array", "dynamic-programming"], "maxProfit", [("prices", "int[]")], "int",
    """
`prices[i]` is the stock price on day `i`. You may complete any number of
transactions but must sell before buying again, and after selling you must wait one
day (cooldown) before buying. **Return the maximum profit.**

**Example**
```
prices = [1,2,3,0,2]  ->  3    (buy, sell, cooldown, buy, sell)
```

**Constraints:** `0 <= len(prices) <= 5000`, `0 <= prices[i] <= 1000`.
""",
    """def maxProfit(prices):
    if not prices:
        return 0
    hold = -prices[0]
    sold = 0
    rest = 0
    for p in prices[1:]:
        prev_sold = sold
        sold = hold + p
        hold = max(hold, rest - p)
        rest = max(rest, prev_sold)
    return max(sold, rest)
""",
    visible=[{"prices": [1, 2, 3, 0, 2]}],
    hidden=[{"prices": []}, {"prices": [1]}, {"prices": [2, 1]},
            {"prices": [1, 2, 4]}, {"prices": [6, 1, 3, 2, 4, 7]},
            {"prices": [(i * 7) % 13 for i in range(60)]}],
    gen=lambda r: [{"prices": ilist(r, 0, 12, 0, 10)} for _ in range(6)],
    brute=_cooldown_brute,
    checks=[({"prices": [1, 2, 3, 0, 2]}, 3), ({"prices": []}, 0),
            ({"prices": [1]}, 0), ({"prices": [2, 1]}, 0)],
    source="new_p")


# ===========================================================================
# 15. Trapping Rain Water
# ===========================================================================
add("trapping-rain-water", "Trapping Rain Water", "hard",
    ["array", "two-pointers", "dynamic-programming", "stack"], "trap",
    [("height", "int[]")], "int",
    """
Given `n` non-negative integers `height` representing an elevation map where each
bar has width `1`, **return how many units of water can be trapped** after raining.

**Example**
```
height = [0,1,0,2,1,0,1,3,2,1,2,1]  ->  6
```

**Constraints:** `0 <= n <= 2*10^4`, `0 <= height[i] <= 10^5`.
""",
    """def trap(height):
    if not height:
        return 0
    l, r = 0, len(height) - 1
    lm = rm = 0
    res = 0
    while l < r:
        if height[l] < height[r]:
            lm = max(lm, height[l])
            res += lm - height[l]
            l += 1
        else:
            rm = max(rm, height[r])
            res += rm - height[r]
            r -= 1
    return res
""",
    visible=[{"height": [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]}],
    hidden=[{"height": []}, {"height": [4, 2, 0, 3, 2, 5]}, {"height": [1, 1, 1]},
            {"height": [5, 4, 1, 2]}, {"height": [2, 0, 2]},
            {"height": [(i * 13) % 7 for i in range(500)]}],
    gen=lambda r: [{"height": ilist(r, 0, 15, 0, 6)} for _ in range(6)],
    brute=_trap_brute,
    checks=[({"height": [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]}, 6),
            ({"height": [4, 2, 0, 3, 2, 5]}, 9), ({"height": [2, 0, 2]}, 2)],
    source="new_p")


# ===========================================================================
# 16. Max Dot Product of Two Subsequences
# ===========================================================================
add("max-dot-product-of-two-subsequences", "Max Dot Product of Two Subsequences",
    "hard", ["array", "dynamic-programming"], "maxDotProduct",
    [("nums1", "int[]"), ("nums2", "int[]")], "int",
    """
Given arrays `nums1` and `nums2`, **return the maximum dot product** between two
**non-empty** subsequences of equal length, one chosen from each array.

**Examples**
```
nums1 = [2,1,-2,5], nums2 = [3,0,-6]  ->  18   ([2,-2] . [3,-6])
nums1 = [3,-2],     nums2 = [2,-6,7]  ->  21   ([3] . [7])
nums1 = [-1,-1],    nums2 = [1,1]     ->  -1
```

**Constraints:** `1 <= len(nums1), len(nums2) <= 500`,
`-1000 <= nums[i] <= 1000`.
""",
    """def maxDotProduct(nums1, nums2):
    m, n = len(nums1), len(nums2)
    NEG = float('-inf')
    dp = [[NEG] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            prod = nums1[i - 1] * nums2[j - 1]
            dp[i][j] = max(prod, prod + max(dp[i - 1][j - 1], 0),
                           dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
""",
    visible=[{"nums1": [2, 1, -2, 5], "nums2": [3, 0, -6]},
             {"nums1": [3, -2], "nums2": [2, -6, 7]},
             {"nums1": [-1, -1], "nums2": [1, 1]}],
    hidden=[{"nums1": [1], "nums2": [1]}, {"nums1": [-5], "nums2": [-4]},
            {"nums1": [-3, -8, 3, -10, 1, 3, 9], "nums2": [9, 2, 3, 7, -9, 1, -8, 5, -1, -1]},
            {"nums1": [2, -2], "nums2": [-2, 2]}],
    gen=lambda r: [{"nums1": ilist(r, 1, 6, -5, 5), "nums2": ilist(r, 1, 6, -5, 5)}
                   for _ in range(6)],
    brute=_dot_brute,
    checks=[({"nums1": [2, 1, -2, 5], "nums2": [3, 0, -6]}, 18),
            ({"nums1": [3, -2], "nums2": [2, -6, 7]}, 21),
            ({"nums1": [-1, -1], "nums2": [1, 1]}, -1)],
    source="new_p")


# ===========================================================================
# 17. Swap For Longest Repeated Character Substring
# ===========================================================================
add("swap-for-longest-repeated-character-substring",
    "Swap For Longest Repeated Character Substring", "medium",
    ["string", "sliding-window"], "maxRepOpt1", [("text", "string")], "int",
    """
You may swap two characters of `text` at most once (or not at all). **Return the
length of the longest substring of a single repeated character** achievable.

**Examples**
```
text = "ababa"    ->  3
text = "aaabaaa"  ->  6
text = "aaabbaaa" ->  4
text = "aaaaa"    ->  5
```

**Constraints:** `1 <= len(text) <= 2*10^4`, lowercase letters.
""",
    """def maxRepOpt1(text):
    from collections import Counter
    cnt = Counter(text)
    groups = []
    i = 0
    n = len(text)
    while i < n:
        j = i
        while j < n and text[j] == text[i]:
            j += 1
        groups.append((text[i], j - i))
        i = j
    res = 0
    for ch, length in groups:
        res = max(res, min(length + 1, cnt[ch]))
    for i in range(1, len(groups) - 1):
        if groups[i - 1][0] == groups[i + 1][0] and groups[i][1] == 1:
            ch = groups[i - 1][0]
            total = groups[i - 1][1] + groups[i + 1][1]
            res = max(res, min(total + 1, cnt[ch]))
    return res
""",
    visible=[{"text": "ababa"}, {"text": "aaabaaa"}, {"text": "aaabbaaa"}],
    hidden=[{"text": "aaaaa"}, {"text": "abcdef"}, {"text": "a"},
            {"text": "aabaaabaa"}, {"text": "bbababaaaa"}],
    gen=lambda r: [{"text": sstr(r, 1, 15, "ab")} for _ in range(6)],
    brute=_swaprep_brute,
    checks=[({"text": "ababa"}, 3), ({"text": "aaabaaa"}, 6),
            ({"text": "aaabbaaa"}, 4), ({"text": "aaaaa"}, 5),
            ({"text": "abcdef"}, 1)],
    source="new_p")


# ===========================================================================
# 18. Check If a String Contains All Binary Codes of Size K
# ===========================================================================
add("check-if-a-string-contains-all-binary-codes-of-size-k",
    "Check If a String Contains All Binary Codes of Size K", "medium",
    ["string", "hash-table", "bit-manipulation"], "hasAllCodes",
    [("s", "string"), ("k", "int")], "bool",
    """
Given a binary string `s` and an integer `k`, **return `true` if every binary
string of length `k` appears as a substring of `s`**, else `false`.

**Examples**
```
s = "00110110", k = 2  ->  true
s = "0110", k = 1       ->  true
s = "0110", k = 2       ->  false   ("00" is missing)
```

**Constraints:** `1 <= len(s) <= 5*10^5`, `s` is `0`/`1`, `1 <= k <= 20`.
""",
    """def hasAllCodes(s, k):
    if len(s) < k:
        return False
    seen = set()
    for i in range(len(s) - k + 1):
        seen.add(s[i:i + k])
    return len(seen) == (1 << k)
""",
    visible=[{"s": "00110110", "k": 2}, {"s": "0110", "k": 1},
             {"s": "0110", "k": 2}],
    hidden=[{"s": "00110", "k": 2}, {"s": "0000000001011100", "k": 4},
            {"s": "0", "k": 1}, {"s": "1", "k": 2}],
    gen=lambda r: [{"s": "".join(r.choice("01") for _ in range(r.randint(1, 18))),
                    "k": r.randint(1, 4)} for _ in range(6)],
    brute=_codes_brute,
    checks=[({"s": "00110110", "k": 2}, True), ({"s": "0110", "k": 1}, True),
            ({"s": "0110", "k": 2}, False), ({"s": "00110", "k": 2}, True),
            ({"s": "0000000001011100", "k": 4}, False)],
    source="new_p")


# ===========================================================================
# 19. Form Largest Integer With Digits That Add up to Target
# ===========================================================================
add("form-largest-integer-with-digits-that-add-up-to-target",
    "Form Largest Integer With Digits That Add up to Target", "hard",
    ["array", "dynamic-programming"], "largestNumber",
    [("cost", "int[]"), ("target", "int")], "string",
    """
`cost[i]` is the cost to paint the digit `i+1` (digits `1`..`9`, no `0`). Spending
**exactly** `target` total cost, **return the largest integer you can paint** as a
string, or `"0"` if it is impossible.

**Examples**
```
cost = [4,3,2,5,6,7,2,5,5], target = 9   ->  "7772"
cost = [7,6,5,5,5,6,8,7,8], target = 12  ->  "85"
cost = [2,4,6,2,4,6,4,4,4], target = 5   ->  "0"
```

**Constraints:** `len(cost) == 9`, `1 <= cost[i] <= 5000`, `1 <= target <= 5000`.
""",
    """def largestNumber(cost, target):
    dp = [0] + [-1] * target
    for t in range(1, target + 1):
        for c in cost:
            if t - c >= 0 and dp[t - c] != -1:
                dp[t] = max(dp[t], dp[t - c] + 1)
    if dp[target] == -1:
        return "0"
    res = []
    t = target
    for d in range(9, 0, -1):
        c = cost[d - 1]
        while t - c >= 0 and dp[t - c] == dp[t] - 1:
            res.append(str(d))
            t -= c
    return "".join(res)
""",
    visible=[{"cost": [4, 3, 2, 5, 6, 7, 2, 5, 5], "target": 9},
             {"cost": [7, 6, 5, 5, 5, 6, 8, 7, 8], "target": 12},
             {"cost": [2, 4, 6, 2, 4, 6, 4, 4, 4], "target": 5}],
    hidden=[{"cost": [6, 10, 15, 40, 40, 40, 40, 40, 40], "target": 47},
            {"cost": [1, 1, 1, 1, 1, 1, 1, 1, 1], "target": 4},
            {"cost": [5, 5, 5, 5, 5, 5, 5, 5, 5], "target": 7},
            {"cost": [3, 2, 4, 5, 6, 7, 8, 9, 10], "target": 10}],
    gen=lambda r: [{"cost": [r.randint(1, 8) for _ in range(9)],
                    "target": r.randint(1, 25)} for _ in range(6)],
    brute=_largestnum_brute,
    checks=[({"cost": [4, 3, 2, 5, 6, 7, 2, 5, 5], "target": 9}, "7772"),
            ({"cost": [7, 6, 5, 5, 5, 6, 8, 7, 8], "target": 12}, "85"),
            ({"cost": [2, 4, 6, 2, 4, 6, 4, 4, 4], "target": 5}, "0"),
            ({"cost": [6, 10, 15, 40, 40, 40, 40, 40, 40], "target": 47}, "32211")],
    source="new_p")


# ===========================================================================
# 20. Maximum Profit of Operating a Centennial Wheel
# ===========================================================================
add("maximum-profit-of-operating-a-centennial-wheel",
    "Maximum Profit of Operating a Centennial Wheel", "medium",
    ["array", "simulation", "greedy"], "minOperationsMaxProfit",
    [("customers", "int[]"), ("boardingCost", "int"), ("runningCost", "int")], "int",
    """
A wheel has gondolas holding up to 4 people each; each rotation costs `runningCost`
and each boarding customer pays `boardingCost`. `customers[i]` people arrive just
before rotation `i`; waiting customers board (up to 4) at each rotation. **Return
the minimum number of rotations that maximizes profit**, or `-1` if profit is never
positive.

**Examples**
```
customers = [8,3],   boardingCost = 5, runningCost = 6  ->  3
customers = [10,9,6], boardingCost = 6, runningCost = 4 ->  7
customers = [3,4,0,5,1], boardingCost = 1, runningCost = 92 ->  -1
```

**Constraints:** `1 <= len(customers) <= 10^5`, `0 <= customers[i] <= 50`,
`1 <= boardingCost, runningCost <= 100`.
""",
    """def minOperationsMaxProfit(customers, boardingCost, runningCost):
    waiting = 0
    profit = 0
    best_profit = 0
    best_rot = -1
    rot = 0
    i = 0
    n = len(customers)
    while i < n or waiting > 0:
        if i < n:
            waiting += customers[i]
            i += 1
        board = min(4, waiting)
        waiting -= board
        rot += 1
        profit += board * boardingCost - runningCost
        if profit > best_profit:
            best_profit = profit
            best_rot = rot
    return best_rot
""",
    visible=[{"customers": [8, 3], "boardingCost": 5, "runningCost": 6},
             {"customers": [10, 9, 6], "boardingCost": 6, "runningCost": 4},
             {"customers": [3, 4, 0, 5, 1], "boardingCost": 1, "runningCost": 92}],
    hidden=[{"customers": [10, 10, 6, 4, 7], "boardingCost": 3, "runningCost": 8},
            {"customers": [0], "boardingCost": 100, "runningCost": 1},
            {"customers": [4], "boardingCost": 100, "runningCost": 1},
            {"customers": [2], "boardingCost": 2, "runningCost": 4}],
    gen=lambda r: [{"customers": [r.randint(0, 12) for _ in range(r.randint(1, 6))],
                    "boardingCost": r.randint(1, 10), "runningCost": r.randint(1, 10)}
                   for _ in range(6)],
    checks=[({"customers": [8, 3], "boardingCost": 5, "runningCost": 6}, 3),
            ({"customers": [10, 9, 6], "boardingCost": 6, "runningCost": 4}, 7),
            ({"customers": [3, 4, 0, 5, 1], "boardingCost": 1, "runningCost": 92}, -1),
            ({"customers": [10, 10, 6, 4, 7], "boardingCost": 3, "runningCost": 8}, 9)],
    source="new_p")
