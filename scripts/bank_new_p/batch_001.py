"""Batch 001 of the new_p.txt import (20 problems).

Each problem registers itself with scripts.build_bank.add at import time. Expected
outputs are computed by build_bank by running the canonical; brute-force references
and known answers below cross-check the canonical before anything is written.
"""
from scripts.build_bank import add, COMPARE, ilist, sstr  # noqa: F401

MOD = 10 ** 9 + 7


# ---------------------------------------------------------------------------
# Brute / reference helpers (independent of the canonicals where practical)
# ---------------------------------------------------------------------------
def _maxScore_brute(cardPoints, k):
    n = len(cardPoints)
    best = 0
    for l in range(k + 1):
        r = k - l
        s = sum(cardPoints[:l]) + (sum(cardPoints[n - r:]) if r else 0)
        best = max(best, s)
    return best


def _playlist_brute(n, goal, k):
    from itertools import product
    c = 0
    for seq in product(range(n), repeat=goal):
        last, ok = {}, True
        for idx, x in enumerate(seq):
            if x in last and idx - last[x] <= k:
                ok = False
                break
            last[x] = idx
        if ok and len(set(seq)) == n:
            c += 1
    return c % MOD


def _superpow_brute(a, b):
    e = int("".join(map(str, b)))
    return pow(a, e, 1337)


def _maxfreq_brute(s, maxLetters, minSize, maxSize):
    from collections import Counter
    cnt = Counter()
    n = len(s)
    for size in range(minSize, maxSize + 1):
        for i in range(n - size + 1):
            sub = s[i:i + size]
            if len(set(sub)) <= maxLetters:
                cnt[sub] += 1
    return max(cnt.values()) if cnt else 0


def _schemes_brute(n, minProfit, group, profit):
    m = len(group)
    c = 0
    for mask in range(1 << m):
        mem = pr = 0
        for i in range(m):
            if mask >> i & 1:
                mem += group[i]
                pr += profit[i]
        if mem <= n and pr >= minProfit:
            c += 1
    return c % MOD


def _sightseeing_brute(values):
    best = float("-inf")
    n = len(values)
    for i in range(n):
        for j in range(i + 1, n):
            best = max(best, values[i] + values[j] + i - j)
    return best


def _restore_brute(s, k):
    n = len(s)
    count = 0
    for mask in range(1 << (n - 1)):
        parts, start = [], 0
        for i in range(n - 1):
            if mask >> i & 1:
                parts.append(s[start:i + 1])
                start = i + 1
        parts.append(s[start:])
        ok = True
        for p in parts:
            if (len(p) > 1 and p[0] == "0") or not (1 <= int(p) <= k):
                ok = False
                break
        if ok:
            count += 1
    return count % MOD


def _tickets_brute(days, costs):
    # Independent backward DP (the canonical scans forward).
    dayset = set(days)
    last = days[-1]
    dp = [0] * (last + 2)
    for d in range(last, 0, -1):
        if d not in dayset:
            dp[d] = dp[d + 1]
        else:
            dp[d] = min(
                costs[0] + dp[d + 1],
                costs[1] + dp[min(d + 7, last + 1)],
                costs[2] + dp[min(d + 30, last + 1)],
            )
    return dp[1]


def _balanced_brute(s):
    from collections import Counter
    n = len(s)
    need = n // 4
    best = n
    for i in range(n + 1):
        for j in range(i, n + 1):
            out = Counter(s[:i] + s[j:])
            if all(out[c] <= need for c in "QWER"):
                best = min(best, j - i)
    return best


def _ndup_brute(n):
    return sum(1 for x in range(1, n + 1) if len(set(str(x))) < len(str(x)))


def _validate_brute(pushed, popped):
    n = len(pushed)
    seen = set()
    stack = [(0, (), 0)]
    while stack:
        i, st, j = stack.pop()
        if j == n:
            return True
        if (i, st, j) in seen:
            continue
        seen.add((i, st, j))
        if st and j < n and st[-1] == popped[j]:
            stack.append((i, st[:-1], j + 1))
        if i < n:
            stack.append((i + 1, st + (pushed[i],), j))
    return False


def _onebit_neighbors(x):
    res = [x ^ 1]
    for i in range(1, x.bit_length() + 1):
        if (x >> (i - 1)) & 1 and (x & ((1 << (i - 1)) - 1)) == 0:
            res.append(x ^ (1 << i))
    return res


def _onebit_brute(n):
    from collections import deque
    if n == 0:
        return 0
    seen = {n: 0}
    dq = deque([n])
    while dq:
        x = dq.popleft()
        if x == 0:
            return seen[x]
        for y in _onebit_neighbors(x):
            if y not in seen:
                seen[y] = seen[x] + 1
                dq.append(y)
    return seen.get(0, 0)


def _maxlen_brute(nums):
    n = len(nums)
    best = 0
    for i in range(n):
        sign = 1
        for j in range(i, n):
            if nums[j] == 0:
                break
            if nums[j] < 0:
                sign = -sign
            if sign > 0:
                best = max(best, j - i + 1)
    return best


def _delcols_brute(strs):
    from itertools import combinations
    n, m = len(strs), len(strs[0])

    def sorted_after(keep):
        rows = ["".join(s[c] for c in keep) for s in strs]
        return all(rows[i] <= rows[i + 1] for i in range(n - 1))

    for d in range(m + 1):
        for dele in combinations(range(m), d):
            keep = [c for c in range(m) if c not in dele]
            if sorted_after(keep):
                return d
    return m


def _maxxor_brute(nums):
    best = 0
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            best = max(best, nums[i] ^ nums[j])
    return best


def _boats_brute(people, limit):
    n = len(people)
    people = sorted(people)
    used = [False] * n
    best = [n]

    def bt(count):
        if count >= best[0]:
            return
        i = next((k for k in range(n) if not used[k]), None)
        if i is None:
            best[0] = min(best[0], count)
            return
        used[i] = True
        bt(count + 1)
        for j in range(i + 1, n):
            if not used[j] and people[i] + people[j] <= limit:
                used[j] = True
                bt(count + 1)
                used[j] = False
        used[i] = False

    bt(0)
    return best[0]


def _lus_brute(strs):
    def is_sub(a, b):
        it = iter(b)
        return all(c in it for c in a)
    res = -1
    for i, s in enumerate(strs):
        if all(i == j or not is_sub(s, t) for j, t in enumerate(strs)):
            res = max(res, len(s))
    return res


# ===========================================================================
# 1. Maximum Points You Can Obtain From Cards
# ===========================================================================
add("maximum-points-you-can-obtain-from-cards",
    "Maximum Points You Can Obtain From Cards", "medium",
    ["array", "sliding-window", "prefix-sum"], "maxScore",
    [("cardPoints", "int[]"), ("k", "int")], "int",
    """
There are several cards in a row; card `i` is worth `cardPoints[i]` points. In one
step you take a card from the **beginning or the end** of the row, and you take
exactly `k` cards. **Return the maximum total points** you can obtain.

The `k` cards you take are some prefix and some suffix; equivalently the cards you
leave behind form one contiguous window of length `len(cardPoints) - k`, so the
score equals the total minus the minimum such window.

**Examples**
```
cardPoints = [1,2,3,4,5,6,1], k = 3  ->  12   (take 1 + 6 + 5 from the right)
cardPoints = [2,2,2], k = 2          ->  4
cardPoints = [9,7,7,9,7,7,9], k = 7  ->  55   (take every card)
```

**Constraints:** `1 <= len(cardPoints) <= 10^5`, `1 <= cardPoints[i] <= 10^4`,
`1 <= k <= len(cardPoints)`.
""",
    """def maxScore(cardPoints, k):
    n = len(cardPoints)
    w = n - k
    if w == 0:
        return sum(cardPoints)
    cur = sum(cardPoints[:w])
    min_win = cur
    for i in range(w, n):
        cur += cardPoints[i] - cardPoints[i - w]
        min_win = min(min_win, cur)
    return sum(cardPoints) - min_win
""",
    visible=[{"cardPoints": [1, 2, 3, 4, 5, 6, 1], "k": 3},
             {"cardPoints": [2, 2, 2], "k": 2},
             {"cardPoints": [9, 7, 7, 9, 7, 7, 9], "k": 7}],
    hidden=[{"cardPoints": [1, 1000, 1], "k": 1},
            {"cardPoints": [1, 79, 80, 1, 1, 1, 200, 1], "k": 3},
            {"cardPoints": [5], "k": 1},
            {"cardPoints": list(range(1, 2001)), "k": 1000}],
    gen=lambda r: [(lambda a: {"cardPoints": a, "k": r.randint(1, len(a))})
                   (ilist(r, 1, 25, 1, 50)) for _ in range(4)],
    brute=_maxScore_brute,
    checks=[({"cardPoints": [1, 2, 3, 4, 5, 6, 1], "k": 3}, 12),
            ({"cardPoints": [2, 2, 2], "k": 2}, 4),
            ({"cardPoints": [9, 7, 7, 9, 7, 7, 9], "k": 7}, 55),
            ({"cardPoints": [1, 1000, 1], "k": 1}, 1),
            ({"cardPoints": [1, 79, 80, 1, 1, 1, 200, 1], "k": 3}, 202)],
    source="new_p")


# ===========================================================================
# 2. Number of Music Playlists
# ===========================================================================
add("number-of-music-playlists", "Number of Music Playlists", "hard",
    ["math", "dynamic-programming", "combinatorics"], "numMusicPlaylists",
    [("n", "int"), ("goal", "int"), ("k", "int")], "int",
    """
Your music player has `n` different songs and you want to listen to `goal` songs
(repeats allowed) during a trip. Build a playlist so that:

- every one of the `n` songs is played **at least once**, and
- a song can be replayed only after at least `k` **other** songs have been played
  since its previous play.

**Return the number of possible playlists**, modulo `10^9 + 7`.

**Examples**
```
n = 3, goal = 3, k = 1  ->  6
n = 2, goal = 3, k = 0  ->  6
n = 2, goal = 3, k = 1  ->  2   (only [1,2,1] and [2,1,2])
```

**Constraints:** `0 <= k < n <= goal <= 100`.
""",
    """def numMusicPlaylists(n, goal, k):
    MOD = 10 ** 9 + 7
    dp = [[0] * (n + 1) for _ in range(goal + 1)]
    dp[0][0] = 1
    for i in range(1, goal + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i - 1][j - 1] * (n - j + 1)
            dp[i][j] += dp[i - 1][j] * max(j - k, 0)
            dp[i][j] %= MOD
    return dp[goal][n] % MOD
""",
    visible=[{"n": 3, "goal": 3, "k": 1}, {"n": 2, "goal": 3, "k": 0},
             {"n": 2, "goal": 3, "k": 1}],
    hidden=[{"n": 1, "goal": 1, "k": 0}, {"n": 2, "goal": 2, "k": 1},
            {"n": 4, "goal": 6, "k": 2}, {"n": 3, "goal": 5, "k": 1}],
    gen=lambda r: [(lambda n: {"n": n, "goal": r.randint(n, 6),
                               "k": r.randint(0, n - 1)})
                   (r.randint(1, 4)) for _ in range(4)],
    brute=_playlist_brute,
    checks=[({"n": 3, "goal": 3, "k": 1}, 6), ({"n": 2, "goal": 3, "k": 0}, 6),
            ({"n": 2, "goal": 3, "k": 1}, 2)],
    source="new_p")


# ===========================================================================
# 3. Search in Rotated Sorted Array II
# ===========================================================================
add("search-in-rotated-sorted-array-ii", "Search in Rotated Sorted Array II",
    "medium", ["array", "binary-search"], "search",
    [("nums", "int[]"), ("target", "int")], "bool",
    """
An array sorted in ascending order is rotated at some unknown pivot (for example
`[0,0,1,2,2,5,6]` might become `[2,5,6,0,0,1,2]`). The array **may contain
duplicates**. Given the rotated array `nums` and a `target`, **return `true` if
`target` is present**, otherwise `false`.

**Examples**
```
nums = [2,5,6,0,0,1,2], target = 0  ->  true
nums = [2,5,6,0,0,1,2], target = 3  ->  false
```

**Constraints:** `1 <= len(nums) <= 5000`, `-10^4 <= nums[i], target <= 10^4`.
""",
    """def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return True
        if nums[lo] == nums[mid] == nums[hi]:
            lo += 1
            hi -= 1
        elif nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return False
""",
    visible=[{"nums": [2, 5, 6, 0, 0, 1, 2], "target": 0},
             {"nums": [2, 5, 6, 0, 0, 1, 2], "target": 3},
             {"nums": [1, 0, 1, 1, 1], "target": 0}],
    hidden=[{"nums": [1], "target": 1}, {"nums": [1], "target": 0},
            {"nums": [3, 1], "target": 1},
            {"nums": [2, 2, 2, 2, 2, 2, 0, 2, 2], "target": 0}],
    gen=lambda r: [(lambda a, t: {"nums": a, "target": t})
                   ((lambda s, p: s[p:] + s[:p])(
                       sorted(ilist(r, 1, 14, 0, 6)), r.randint(0, 13)),
                    r.randint(0, 7)) for _ in range(5)],
    brute=lambda nums, target: target in nums,
    checks=[({"nums": [2, 5, 6, 0, 0, 1, 2], "target": 0}, True),
            ({"nums": [2, 5, 6, 0, 0, 1, 2], "target": 3}, False)],
    source="new_p")


# ===========================================================================
# 4. Super Pow
# ===========================================================================
add("super-pow", "Super Pow", "medium", ["math", "divide-and-conquer"],
    "superPow", [("a", "int"), ("b", "int[]")], "int",
    """
Calculate `a^b mod 1337`, where `a` is a positive integer and `b` is an extremely
large positive integer given as an **array of its decimal digits** (most
significant first). **Return the result.**

**Examples**
```
a = 2, b = [3]    ->  8       (2^3 = 8)
a = 2, b = [1,0]  ->  1024    (2^10 = 1024)
```

**Constraints:** `1 <= a <= 2^31 - 1`, `1 <= len(b) <= 2000`, each `b[i]` is a
digit `0..9` with no leading zero.
""",
    """def superPow(a, b):
    MOD = 1337
    res = 1
    a %= MOD
    for d in b:
        res = pow(res, 10, MOD) * pow(a, d, MOD) % MOD
    return res
""",
    visible=[{"a": 2, "b": [3]}, {"a": 2, "b": [1, 0]}],
    hidden=[{"a": 1, "b": [9, 9]}, {"a": 2147483647, "b": [2, 0, 0]},
            {"a": 7, "b": [1, 2, 3]}, {"a": 1337, "b": [5]}],
    gen=lambda r: [{"a": r.randint(1, 5000),
                    "b": [r.randint(1, 9)] + [r.randint(0, 9) for _ in range(r.randint(0, 3))]}
                   for _ in range(5)],
    brute=_superpow_brute,
    checks=[({"a": 2, "b": [3]}, 8), ({"a": 2, "b": [1, 0]}, 1024)],
    source="new_p")


# ===========================================================================
# 5. Maximum Number of Occurrences of a Substring
# ===========================================================================
add("maximum-number-of-occurrences-of-a-substring",
    "Maximum Number of Occurrences of a Substring", "medium",
    ["string", "hash-table", "sliding-window"], "maxFreq",
    [("s", "string"), ("maxLetters", "int"), ("minSize", "int"), ("maxSize", "int")],
    "int",
    """
Given a string `s`, **return the maximum number of occurrences** of any substring
that satisfies both rules:

- it contains at most `maxLetters` distinct characters, and
- its length is between `minSize` and `maxSize` inclusive.

(Occurrences may overlap. Only the size-`minSize` substrings ever need to be
counted, since any qualifying longer substring occurs no more often than its
prefix.)

**Examples**
```
s = "aababcaab", maxLetters = 2, minSize = 3, maxSize = 4  ->  2   ("aab" twice)
s = "aaaa",      maxLetters = 1, minSize = 3, maxSize = 3  ->  2   ("aaa" twice)
s = "abcde",     maxLetters = 2, minSize = 3, maxSize = 3  ->  0
```

**Constraints:** `1 <= len(s) <= 10^5`, `1 <= maxLetters <= 26`,
`1 <= minSize <= maxSize <= min(26, len(s))`, lowercase letters only.
""",
    """def maxFreq(s, maxLetters, minSize, maxSize):
    from collections import Counter
    cnt = Counter()
    n = len(s)
    for i in range(n - minSize + 1):
        sub = s[i:i + minSize]
        if len(set(sub)) <= maxLetters:
            cnt[sub] += 1
    return max(cnt.values()) if cnt else 0
""",
    visible=[{"s": "aababcaab", "maxLetters": 2, "minSize": 3, "maxSize": 4},
             {"s": "aaaa", "maxLetters": 1, "minSize": 3, "maxSize": 3},
             {"s": "abcde", "maxLetters": 2, "minSize": 3, "maxSize": 3}],
    hidden=[{"s": "aabcabcab", "maxLetters": 2, "minSize": 2, "maxSize": 3},
            {"s": "a", "maxLetters": 1, "minSize": 1, "maxSize": 1},
            {"s": "abababab", "maxLetters": 2, "minSize": 2, "maxSize": 4},
            {"s": "z" * 200, "maxLetters": 1, "minSize": 3, "maxSize": 5}],
    gen=lambda r: [(lambda txt, mn: {"s": txt, "maxLetters": r.randint(1, 3),
                                     "minSize": mn,
                                     "maxSize": r.randint(mn, min(6, len(txt)))})
                   (sstr(r, 4, 14, "abc"), r.randint(1, 4)) for _ in range(5)],
    brute=_maxfreq_brute,
    checks=[({"s": "aababcaab", "maxLetters": 2, "minSize": 3, "maxSize": 4}, 2),
            ({"s": "aaaa", "maxLetters": 1, "minSize": 3, "maxSize": 3}, 2),
            ({"s": "aabcabcab", "maxLetters": 2, "minSize": 2, "maxSize": 3}, 3),
            ({"s": "abcde", "maxLetters": 2, "minSize": 3, "maxSize": 3}, 0)],
    source="new_p")


# ===========================================================================
# 6. Profitable Schemes
# ===========================================================================
add("profitable-schemes", "Profitable Schemes", "hard",
    ["dynamic-programming"], "profitableSchemes",
    [("n", "int"), ("minProfit", "int"), ("group", "int[]"), ("profit", "int[]")],
    "int",
    """
A gang of `n` members can commit a list of crimes. Crime `i` needs `group[i]`
members and yields `profit[i]`. A member who joins one crime cannot join another,
so a chosen subset of crimes uses `sum(group[i])` members in total.

A subset is **profitable** if it earns at least `minProfit` profit using at most
`n` members. **Return the number of profitable subsets**, modulo `10^9 + 7`.

**Examples**
```
n = 5,  minProfit = 3, group = [2,2],   profit = [2,3]  ->  2
n = 10, minProfit = 5, group = [2,3,5], profit = [6,7,8] ->  7
```

**Constraints:** `1 <= n <= 100`, `0 <= minProfit <= 100`,
`1 <= len(group) == len(profit) <= 100`, `1 <= group[i] <= 100`,
`0 <= profit[i] <= 100`.
""",
    """def profitableSchemes(n, minProfit, group, profit):
    MOD = 10 ** 9 + 7
    dp = [[0] * (minProfit + 1) for _ in range(n + 1)]
    for g in range(n + 1):
        dp[g][0] = 1
    for k in range(len(group)):
        gk, pk = group[k], profit[k]
        for g in range(n, gk - 1, -1):
            for p in range(minProfit, -1, -1):
                np = min(minProfit, p + pk)
                dp[g][np] = (dp[g][np] + dp[g - gk][p]) % MOD
    return dp[n][minProfit] % MOD
""",
    visible=[{"n": 5, "minProfit": 3, "group": [2, 2], "profit": [2, 3]},
             {"n": 10, "minProfit": 5, "group": [2, 3, 5], "profit": [6, 7, 8]}],
    hidden=[{"n": 1, "minProfit": 0, "group": [1], "profit": [0]},
            {"n": 1, "minProfit": 1, "group": [1], "profit": [0]},
            {"n": 12, "minProfit": 10, "group": [1, 2, 3, 4, 5, 6],
             "profit": [3, 1, 4, 1, 5, 9]}],
    gen=lambda r: [(lambda m: {"n": r.randint(1, 12),
                               "minProfit": r.randint(0, 8),
                               "group": [r.randint(1, 6) for _ in range(m)],
                               "profit": [r.randint(0, 6) for _ in range(m)]})
                   (r.randint(1, 8)) for _ in range(5)],
    brute=_schemes_brute,
    checks=[({"n": 5, "minProfit": 3, "group": [2, 2], "profit": [2, 3]}, 2),
            ({"n": 10, "minProfit": 5, "group": [2, 3, 5], "profit": [6, 7, 8]}, 7)],
    source="new_p")


# ===========================================================================
# 7. Best Sightseeing Pair
# ===========================================================================
add("best-sightseeing-pair", "Best Sightseeing Pair", "medium",
    ["array", "dynamic-programming"], "maxScoreSightseeing",
    [("values", "int[]")], "int",
    """
`values[i]` is the value of sightseeing spot `i`. The score of a pair `i < j` is
`values[i] + values[j] + i - j` (the two values, minus the distance between them).
**Return the maximum score** over all pairs.

**Example**
```
values = [8,1,5,2,6]  ->  11   (i = 0, j = 2: 8 + 5 + 0 - 2 = 11)
```

**Constraints:** `2 <= len(values) <= 5*10^4`, `1 <= values[i] <= 1000`.
""",
    """def maxScoreSightseeing(values):
    best = values[0]
    ans = float('-inf')
    for j in range(1, len(values)):
        ans = max(ans, best + values[j] - j)
        best = max(best, values[j] + j)
    return ans
""",
    visible=[{"values": [8, 1, 5, 2, 6]}, {"values": [1, 2]}],
    hidden=[{"values": [1, 1]}, {"values": [2, 2, 2, 2]},
            {"values": [10, 1, 1, 1, 10]},
            {"values": [(i * 37) % 1000 + 1 for i in range(2000)]}],
    gen=lambda r: [{"values": ilist(r, 2, 20, 1, 50)} for _ in range(5)],
    brute=_sightseeing_brute,
    checks=[({"values": [8, 1, 5, 2, 6]}, 11)],
    source="new_p")


# ===========================================================================
# 8. Restore the Array
# ===========================================================================
add("restore-the-array", "Restore the Array", "hard",
    ["string", "dynamic-programming"], "numberOfArrays",
    [("s", "string"), ("k", "int")], "int",
    """
A program printed an array of integers but forgot the separators, leaving the
digit string `s`. Every original integer was in the range `[1, k]` and had no
leading zero. **Return the number of arrays** that could print as `s`, modulo
`10^9 + 7`.

**Examples**
```
s = "1000", k = 10000  ->  1    (only [1000])
s = "1000", k = 10      ->  0
s = "1317", k = 2000    ->  8
s = "2020", k = 30      ->  1    (only [20,20])
```

**Constraints:** `1 <= len(s) <= 10^5`, `s` is digits with no leading zero,
`1 <= k <= 10^9`.
""",
    """def numberOfArrays(s, k):
    MOD = 10 ** 9 + 7
    n = len(s)
    dp = [0] * (n + 1)
    dp[n] = 1
    for i in range(n - 1, -1, -1):
        if s[i] == '0':
            dp[i] = 0
            continue
        num = 0
        for j in range(i, n):
            num = num * 10 + int(s[j])
            if num > k:
                break
            dp[i] = (dp[i] + dp[j + 1]) % MOD
    return dp[0] % MOD
""",
    visible=[{"s": "1000", "k": 10000}, {"s": "1317", "k": 2000},
             {"s": "2020", "k": 30}],
    hidden=[{"s": "1000", "k": 10}, {"s": "1234567890", "k": 90},
            {"s": "7", "k": 7}, {"s": "7", "k": 6},
            {"s": "9" * 16, "k": 1000000000}],
    gen=lambda r: [{"s": "".join(str(r.randint(1, 9)) if i == 0
                                 else str(r.randint(0, 9))
                                 for i in range(r.randint(1, 11))),
                    "k": r.randint(1, 5000)} for _ in range(5)],
    brute=_restore_brute,
    checks=[({"s": "1000", "k": 10000}, 1), ({"s": "1000", "k": 10}, 0),
            ({"s": "1317", "k": 2000}, 8), ({"s": "2020", "k": 30}, 1),
            ({"s": "1234567890", "k": 90}, 34)],
    source="new_p")


# ===========================================================================
# 9. Parse Lisp Expression
# ===========================================================================
add("parse-lisp-expression", "Parse Lisp Expression", "hard",
    ["string", "stack", "recursion", "hash-table"], "evaluate",
    [("expression", "string")], "int",
    """
Evaluate a Lisp-like `expression` and **return its integer value**. An expression
is one of:

- an integer (possibly negative), or a variable name;
- `(add e1 e2)` -> `eval(e1) + eval(e2)`;
- `(mult e1 e2)` -> `eval(e1) * eval(e2)`;
- `(let v1 e1 v2 e2 ... vn en expr)` -> assign each `vi` the value of `ei`
  **sequentially**, then evaluate `expr`.

Variables use lexical scope: a name resolves to the value bound in the innermost
enclosing `let`. Names `add`, `let`, `mult` are reserved.

**Examples**
```
(add 1 2)                                   ->  3
(mult 3 (add 2 3))                          ->  15
(let x 2 (mult x (let x 3 y 4 (add x y))))  ->  14
(let x 3 x 2 x)                             ->  2
```

**Constraints:** `1 <= len(expression) <= 2000`; the expression is well-formed and
every value fits in a 32-bit signed integer.
""",
    """def evaluate(expression):
    def tokenize(s):
        res, bal, cur = [], 0, ''
        for ch in s:
            if ch == '(':
                bal += 1
            elif ch == ')':
                bal -= 1
            if ch == ' ' and bal == 0:
                res.append(cur)
                cur = ''
            else:
                cur += ch
        if cur:
            res.append(cur)
        return res

    def ev(expr, scope):
        if expr[0] != '(':
            if expr[0] == '-' or expr[0].isdigit():
                return int(expr)
            return scope[expr][-1]
        toks = tokenize(expr[1:-1])
        op = toks[0]
        if op == 'add':
            return ev(toks[1], scope) + ev(toks[2], scope)
        if op == 'mult':
            return ev(toks[1], scope) * ev(toks[2], scope)
        params = toks[1:]
        assigned = []
        for i in range(0, len(params) - 1, 2):
            scope.setdefault(params[i], []).append(ev(params[i + 1], scope))
            assigned.append(params[i])
        res = ev(params[-1], scope)
        for v in assigned:
            scope[v].pop()
        return res

    return ev(expression, {})
""",
    visible=[{"expression": "(add 1 2)"}, {"expression": "(mult 3 (add 2 3))"},
             {"expression": "(let x 2 (mult x 5))"}],
    hidden=[{"expression": "(let x 2 (mult x (let x 3 y 4 (add x y))))"},
            {"expression": "(let x 3 x 2 x)"},
            {"expression": "(let x 1 y 2 x (add x y) (add x y))"},
            {"expression": "(let x 2 (add (let x 3 (let x 4 x)) x))"},
            {"expression": "(let a1 3 b2 (add a1 1) b2)"},
            {"expression": "(add -5 (mult 2 3))"}],
    checks=[({"expression": "(add 1 2)"}, 3),
            ({"expression": "(mult 3 (add 2 3))"}, 15),
            ({"expression": "(let x 2 (mult x 5))"}, 10),
            ({"expression": "(let x 2 (mult x (let x 3 y 4 (add x y))))"}, 14),
            ({"expression": "(let x 3 x 2 x)"}, 2),
            ({"expression": "(let x 1 y 2 x (add x y) (add x y))"}, 5),
            ({"expression": "(let x 2 (add (let x 3 (let x 4 x)) x))"}, 6),
            ({"expression": "(let a1 3 b2 (add a1 1) b2)"}, 4),
            ({"expression": "(add -5 (mult 2 3))"}, 1)],
    source="new_p")


# ===========================================================================
# 10. Minimum Cost For Tickets
# ===========================================================================
add("minimum-cost-for-tickets", "Minimum Cost For Tickets", "medium",
    ["array", "dynamic-programming"], "mincostTickets",
    [("days", "int[]"), ("costs", "int[]")], "int",
    """
You planned train trips on the given `days` of the year (each `1..365`). Tickets:
a 1-day pass for `costs[0]`, a 7-day pass for `costs[1]`, a 30-day pass for
`costs[2]`. A pass bought on day `d` covers that many **consecutive** days from
`d`. **Return the minimum cost** to cover every travel day.

**Examples**
```
days = [1,4,6,7,8,20], costs = [2,7,15]                  ->  11
days = [1,2,3,4,5,6,7,8,9,10,30,31], costs = [2,7,15]    ->  17
```

**Constraints:** `1 <= len(days) <= 365`, `1 <= days[i] <= 365` strictly
increasing, `len(costs) == 3`, `1 <= costs[i] <= 1000`.
""",
    """def mincostTickets(days, costs):
    dayset = set(days)
    last = days[-1]
    dp = [0] * (last + 1)
    for d in range(1, last + 1):
        if d not in dayset:
            dp[d] = dp[d - 1]
        else:
            dp[d] = min(dp[d - 1] + costs[0],
                        dp[max(0, d - 7)] + costs[1],
                        dp[max(0, d - 30)] + costs[2])
    return dp[last]
""",
    visible=[{"days": [1, 4, 6, 7, 8, 20], "costs": [2, 7, 15]},
             {"days": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 30, 31], "costs": [2, 7, 15]}],
    hidden=[{"days": [1], "costs": [5, 10, 20]},
            {"days": [1, 30, 60, 90], "costs": [1, 7, 15]},
            {"days": list(range(1, 366)), "costs": [2, 7, 15]}],
    gen=lambda r: [(lambda ds: {"days": ds,
                                "costs": [r.randint(1, 20), r.randint(1, 40),
                                          r.randint(1, 100)]})
                   (sorted(r.sample(range(1, 41), r.randint(1, 12)))) for _ in range(5)],
    brute=_tickets_brute,
    checks=[({"days": [1, 4, 6, 7, 8, 20], "costs": [2, 7, 15]}, 11),
            ({"days": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 30, 31], "costs": [2, 7, 15]}, 17)],
    source="new_p")


# ===========================================================================
# 11. Replace the Substring for Balanced String
# ===========================================================================
add("replace-the-substring-for-balanced-string",
    "Replace the Substring for Balanced String", "medium",
    ["string", "sliding-window"], "balancedString", [("s", "string")], "int",
    """
A string of `Q`, `W`, `E`, `R` is **balanced** when each of the four characters
appears exactly `len(s)/4` times. You may replace one contiguous substring with any
string of the same length. **Return the minimum length** of substring you must
replace to make `s` balanced (`0` if it already is).

**Examples**
```
s = "QWER"  ->  0
s = "QQWE"  ->  1
s = "QQQW"  ->  2
s = "QQQQ"  ->  3
```

**Constraints:** `1 <= len(s) <= 10^5`, `len(s)` is a multiple of 4, characters are
only `Q`, `W`, `E`, `R`.
""",
    """def balancedString(s):
    from collections import Counter
    n = len(s)
    need = n // 4
    cnt = Counter(s)
    if all(cnt[c] == need for c in "QWER"):
        return 0
    res = n
    l = 0
    for r in range(n):
        cnt[s[r]] -= 1
        while l <= r and all(cnt[c] <= need for c in "QWER"):
            res = min(res, r - l + 1)
            cnt[s[l]] += 1
            l += 1
    return res
""",
    visible=[{"s": "QWER"}, {"s": "QQWE"}, {"s": "QQQW"}],
    hidden=[{"s": "QQQQ"}, {"s": "WWEQ"}, {"s": "QWERQWER"},
            {"s": "QQQQWWWWEEEERRRR"}, {"s": "RRQQ" * 25}],
    gen=lambda r: [{"s": "".join(r.choice("QWER") for _ in range(4 * r.randint(1, 6)))}
                   for _ in range(5)],
    brute=_balanced_brute,
    checks=[({"s": "QWER"}, 0), ({"s": "QQWE"}, 1), ({"s": "QQQW"}, 2),
            ({"s": "QQQQ"}, 3)],
    source="new_p")


# ===========================================================================
# 12. Numbers With Repeated Digits
# ===========================================================================
add("numbers-with-repeated-digits", "Numbers With Repeated Digits", "hard",
    ["math", "dynamic-programming", "combinatorics"], "numDupDigitsAtMostN",
    [("n", "int")], "int",
    """
Given a positive integer `n`, **return how many integers in `[1, n]` have at least
one repeated digit**.

**Examples**
```
n = 20    ->  1     (only 11)
n = 100   ->  10
n = 1000  ->  262
```

**Constraints:** `1 <= n <= 10^9`.
""",
    """def numDupDigitsAtMostN(n):
    digits = list(map(int, str(n)))
    L = len(digits)

    def perm(m, k):
        r = 1
        for i in range(k):
            r *= (m - i)
        return r

    res = 0
    for i in range(1, L):
        res += 9 * perm(9, i - 1)
    seen = set()
    for i, d in enumerate(digits):
        start = 1 if i == 0 else 0
        for x in range(start, d):
            if x not in seen:
                res += perm(9 - i, L - i - 1)
        if d in seen:
            break
        seen.add(d)
    else:
        res += 1
    return n - res
""",
    visible=[{"n": 20}, {"n": 100}, {"n": 1000}],
    hidden=[{"n": 1}, {"n": 9}, {"n": 11}, {"n": 99}, {"n": 12345},
            {"n": 1000000000}],
    gen=lambda r: [{"n": r.randint(1, 3000)} for _ in range(6)],
    checks=[({"n": 20}, 1), ({"n": 100}, 10), ({"n": 1000}, 262),
            ({"n": 10}, 0), ({"n": 11}, 1), ({"n": 99}, 9), ({"n": 1}, 0)],
    source="new_p")


# ===========================================================================
# 13. Validate Stack Sequences
# ===========================================================================
add("validate-stack-sequences", "Validate Stack Sequences", "medium",
    ["stack", "array", "simulation"], "validateStackSequences",
    [("pushed", "int[]"), ("popped", "int[]")], "bool",
    """
Given two sequences `pushed` and `popped`, each a permutation of the same distinct
values, **return `true` if they could result from a sequence of push and pop
operations** on an initially empty stack, otherwise `false`.

**Examples**
```
pushed = [1,2,3,4,5], popped = [4,5,3,2,1]  ->  true
pushed = [1,2,3,4,5], popped = [4,3,5,1,2]  ->  false
```

**Constraints:** `0 <= len(pushed) == len(popped) <= 1000`, values are distinct,
`pushed` is a permutation of `popped`.
""",
    """def validateStackSequences(pushed, popped):
    st = []
    j = 0
    for x in pushed:
        st.append(x)
        while st and j < len(popped) and st[-1] == popped[j]:
            st.pop()
            j += 1
    return j == len(popped)
""",
    visible=[{"pushed": [1, 2, 3, 4, 5], "popped": [4, 5, 3, 2, 1]},
             {"pushed": [1, 2, 3, 4, 5], "popped": [4, 3, 5, 1, 2]}],
    hidden=[{"pushed": [], "popped": []}, {"pushed": [1], "popped": [1]},
            {"pushed": [1, 2], "popped": [2, 1]},
            {"pushed": [1, 2, 3], "popped": [3, 1, 2]}],
    gen=lambda r: [(lambda perm: {"pushed": perm[0], "popped": perm[1]})
                   ((lambda base: (base, r.sample(base, len(base))))
                    (r.sample(range(1, 30), r.randint(0, 6)))) for _ in range(6)],
    brute=_validate_brute,
    checks=[({"pushed": [1, 2, 3, 4, 5], "popped": [4, 5, 3, 2, 1]}, True),
            ({"pushed": [1, 2, 3, 4, 5], "popped": [4, 3, 5, 1, 2]}, False)],
    source="new_p")


# ===========================================================================
# 14. Max Increase to Keep City Skyline
# ===========================================================================
add("max-increase-to-keep-city-skyline", "Max Increase to Keep City Skyline",
    "medium", ["array", "matrix", "greedy"], "maxIncreaseKeepingSkyline",
    [("grid", "int[][]")], "int",
    """
`grid[i][j]` is the height of a building. You may raise any buildings so that the
skyline seen from the top, bottom, left and right is unchanged. The top/bottom
skyline is the per-column maxima; the left/right skyline is the per-row maxima.
**Return the maximum total increase** in height.

A building at `(i, j)` may rise to `min(rowMax[i], colMax[j])` without changing any
skyline.

**Example**
```
grid = [[3,0,8,4],[2,4,5,7],[9,2,6,3],[0,3,1,0]]  ->  35
```

**Constraints:** `2 <= len(grid) == len(grid[0]) <= 50`, `0 <= grid[i][j] <= 100`.
""",
    """def maxIncreaseKeepingSkyline(grid):
    rows = [max(r) for r in grid]
    cols = [max(c) for c in zip(*grid)]
    total = 0
    for i, r in enumerate(grid):
        for j, v in enumerate(r):
            total += min(rows[i], cols[j]) - v
    return total
""",
    visible=[{"grid": [[3, 0, 8, 4], [2, 4, 5, 7], [9, 2, 6, 3], [0, 3, 1, 0]]}],
    hidden=[{"grid": [[0, 0], [0, 0]]}, {"grid": [[5, 5], [5, 5]]},
            {"grid": [[1, 2], [3, 4]]},
            {"grid": [[100, 0], [0, 100]]}],
    gen=lambda r: [{"grid": [[r.randint(0, 20) for _ in range(c)] for _ in range(c)]}
                   for c in (r.randint(2, 6),) for _ in range(1)] + [
                   {"grid": [[r.randint(0, 9) for _ in range(3)] for _ in range(3)]}
                   for _ in range(4)],
    checks=[({"grid": [[3, 0, 8, 4], [2, 4, 5, 7], [9, 2, 6, 3], [0, 3, 1, 0]]}, 35),
            ({"grid": [[0, 0], [0, 0]]}, 0), ({"grid": [[5, 5], [5, 5]]}, 0),
            ({"grid": [[1, 2], [3, 4]]}, 1), ({"grid": [[100, 0], [0, 100]]}, 200)],
    source="new_p")


# ===========================================================================
# 15. Minimum One Bit Operations to Make Integers Zero
# ===========================================================================
add("minimum-one-bit-operations-to-make-integers-zero",
    "Minimum One Bit Operations to Make Integers Zero", "hard",
    ["bit-manipulation", "math"], "minimumOneBitOperations", [("n", "int")], "int",
    """
Transform an integer `n` into `0` using these operations any number of times:

- flip the rightmost (0th) bit;
- flip bit `i` (for `i >= 1`) **only when** bit `i-1` is `1` and bits `0..i-2` are
  all `0`.

**Return the minimum number of operations** needed.

This equals the inverse Gray code of `n`: `f(n) = n XOR f(n >> 1)`.

**Examples**
```
n = 0    ->  0
n = 3    ->  2
n = 6    ->  4
n = 333  ->  393
```

**Constraints:** `0 <= n <= 10^9`.
""",
    """def minimumOneBitOperations(n):
    res = 0
    while n:
        res ^= n
        n >>= 1
    return res
""",
    visible=[{"n": 0}, {"n": 3}, {"n": 6}],
    hidden=[{"n": 1}, {"n": 2}, {"n": 9}, {"n": 333}, {"n": 1000000000}],
    gen=lambda r: [{"n": r.randint(0, 1023)} for _ in range(6)],
    checks=[({"n": 0}, 0), ({"n": 3}, 2), ({"n": 6}, 4), ({"n": 9}, 14),
            ({"n": 333}, 393), ({"n": 1}, 1), ({"n": 2}, 3)],
    source="new_p")


# ===========================================================================
# 16. Maximum Length of Subarray With Positive Product
# ===========================================================================
add("maximum-length-of-subarray-with-positive-product",
    "Maximum Length of Subarray With Positive Product", "medium",
    ["array", "dynamic-programming", "greedy"], "getMaxLen",
    [("nums", "int[]")], "int",
    """
Given an array `nums`, **return the maximum length of a contiguous subarray whose
product is strictly positive**. A subarray containing a `0` has product `0` (not
positive), so it must avoid zeros.

**Examples**
```
nums = [1,-2,-3,4]      ->  4    (whole array, product 24)
nums = [0,1,-2,-3,-4]   ->  3    ([1,-2,-3])
nums = [-1,-2,-3,0,1]   ->  2
```

**Constraints:** `1 <= len(nums) <= 10^5`, `-10^9 <= nums[i] <= 10^9`.
""",
    """def getMaxLen(nums):
    pos = neg = 0
    best = 0
    for x in nums:
        if x == 0:
            pos = neg = 0
        elif x > 0:
            pos += 1
            neg = neg + 1 if neg > 0 else 0
        else:
            new_pos = neg + 1 if neg > 0 else 0
            new_neg = pos + 1
            pos, neg = new_pos, new_neg
        best = max(best, pos)
    return best
""",
    visible=[{"nums": [1, -2, -3, 4]}, {"nums": [0, 1, -2, -3, -4]},
             {"nums": [-1, -2, -3, 0, 1]}],
    hidden=[{"nums": [-1, 2]}, {"nums": [1, 2, 3, 5, -6, 4, 0, 10]},
            {"nums": [0]}, {"nums": [-1]}, {"nums": [-1, -1, -1, -1]},
            {"nums": [(-1 if i % 7 == 0 else 1) * ((i % 5) - 2 or 1)
                      for i in range(2000)]}],
    gen=lambda r: [{"nums": ilist(r, 1, 20, -3, 3)} for _ in range(6)],
    brute=_maxlen_brute,
    checks=[({"nums": [1, -2, -3, 4]}, 4), ({"nums": [0, 1, -2, -3, -4]}, 3),
            ({"nums": [-1, -2, -3, 0, 1]}, 2), ({"nums": [-1, 2]}, 1),
            ({"nums": [1, 2, 3, 5, -6, 4, 0, 10]}, 4)],
    source="new_p")


# ===========================================================================
# 17. Delete Columns to Make Sorted II
# ===========================================================================
add("delete-columns-to-make-sorted-ii", "Delete Columns to Make Sorted II",
    "medium", ["array", "string", "greedy"], "minDeletionSize",
    [("strs", "string[]")], "int",
    """
Given `strs`, a list of equal-length lowercase strings, you may delete a chosen set
of column indices from every string. **Return the minimum number of columns** you
must delete so the remaining rows are in non-decreasing lexicographic order
(`strs[0] <= strs[1] <= ...`).

**Examples**
```
strs = ["ca","bb","ac"]   ->  1
strs = ["xc","yb","za"]   ->  0
strs = ["zyx","wvu","tsr"] ->  3
```

**Constraints:** `1 <= len(strs) <= 100`, `1 <= len(strs[i]) <= 100`, all equal
length.
""",
    """def minDeletionSize(strs):
    n = len(strs)
    m = len(strs[0])
    settled = [False] * (n - 1)
    res = 0
    for c in range(m):
        if any(not settled[i] and strs[i][c] > strs[i + 1][c]
               for i in range(n - 1)):
            res += 1
            continue
        for i in range(n - 1):
            if not settled[i] and strs[i][c] < strs[i + 1][c]:
                settled[i] = True
    return res
""",
    visible=[{"strs": ["ca", "bb", "ac"]}, {"strs": ["xc", "yb", "za"]},
             {"strs": ["zyx", "wvu", "tsr"]}],
    hidden=[{"strs": ["a"]}, {"strs": ["ab", "ab"]},
            {"strs": ["abx", "abz", "aby"]}, {"strs": ["bca", "abc", "cba"]}],
    gen=lambda r: [(lambda n, m: {"strs": ["".join(r.choice("ab") for _ in range(m))
                                           for _ in range(n)]})
                   (r.randint(1, 4), r.randint(1, 5)) for _ in range(6)],
    brute=_delcols_brute,
    checks=[({"strs": ["ca", "bb", "ac"]}, 1), ({"strs": ["xc", "yb", "za"]}, 0),
            ({"strs": ["zyx", "wvu", "tsr"]}, 3)],
    source="new_p")


# ===========================================================================
# 18. Maximum XOR of Two Numbers in an Array
# ===========================================================================
add("maximum-xor-of-two-numbers-in-an-array",
    "Maximum XOR of Two Numbers in an Array", "medium",
    ["bit-manipulation", "trie", "hash-table"], "findMaximumXOR",
    [("nums", "int[]")], "int",
    """
Given an array `nums`, **return the maximum value of `nums[i] XOR nums[j]`** over
all pairs `i, j`.

**Example**
```
nums = [3,10,5,25,2,8]  ->  28    (5 XOR 25)
```

**Constraints:** `1 <= len(nums) <= 2*10^5`, `0 <= nums[i] < 2^31`.
""",
    """def findMaximumXOR(nums):
    mask = 0
    res = 0
    for i in range(31, -1, -1):
        mask |= (1 << i)
        prefixes = {x & mask for x in nums}
        cand = res | (1 << i)
        if any((cand ^ p) in prefixes for p in prefixes):
            res = cand
    return res
""",
    visible=[{"nums": [3, 10, 5, 25, 2, 8]}, {"nums": [0]}],
    hidden=[{"nums": [2, 4]}, {"nums": [8, 10, 2]},
            {"nums": [14, 70, 53, 83, 49, 91, 36, 80, 92, 51, 66, 70]},
            {"nums": [0, 0, 0]}, {"nums": [2147483647, 0]}],
    gen=lambda r: [{"nums": ilist(r, 1, 25, 0, 1023)} for _ in range(6)],
    brute=_maxxor_brute,
    checks=[({"nums": [3, 10, 5, 25, 2, 8]}, 28), ({"nums": [0]}, 0)],
    source="new_p")


# ===========================================================================
# 19. Boats to Save People
# ===========================================================================
add("boats-to-save-people", "Boats to Save People", "medium",
    ["array", "greedy", "two-pointers", "sorting"], "numRescueBoats",
    [("people", "int[]"), ("limit", "int")], "int",
    """
The `i`-th person weighs `people[i]`. Each boat holds at most two people and at
most `limit` total weight. **Return the minimum number of boats** needed to carry
everyone (every person fits in some boat).

**Examples**
```
people = [1,2], limit = 3        ->  1
people = [3,2,2,1], limit = 3    ->  3
people = [3,5,3,4], limit = 5    ->  4
```

**Constraints:** `1 <= len(people) <= 5*10^4`, `1 <= people[i] <= limit <= 3*10^4`.
""",
    """def numRescueBoats(people, limit):
    people = sorted(people)
    i, j = 0, len(people) - 1
    boats = 0
    while i <= j:
        if people[i] + people[j] <= limit:
            i += 1
        j -= 1
        boats += 1
    return boats
""",
    visible=[{"people": [1, 2], "limit": 3},
             {"people": [3, 2, 2, 1], "limit": 3},
             {"people": [3, 5, 3, 4], "limit": 5}],
    hidden=[{"people": [5], "limit": 5}, {"people": [2, 2], "limit": 6},
            {"people": [1, 1, 1, 1], "limit": 2},
            {"people": [3, 2, 2, 1, 5, 4, 3, 2], "limit": 6}],
    gen=lambda r: [(lambda lim: {"people": [r.randint(1, lim) for _ in range(r.randint(1, 8))],
                                 "limit": lim})
                   (r.randint(2, 12)) for _ in range(6)],
    brute=_boats_brute,
    checks=[({"people": [1, 2], "limit": 3}, 1),
            ({"people": [3, 2, 2, 1], "limit": 3}, 3),
            ({"people": [3, 5, 3, 4], "limit": 5}, 4)],
    source="new_p")


# ===========================================================================
# 20. Longest Uncommon Subsequence II
# ===========================================================================
add("longest-uncommon-subsequence-ii", "Longest Uncommon Subsequence II",
    "medium", ["string", "sorting", "hash-table"], "findLUSlength",
    [("strs", "string[]")], "int",
    """
A *longest uncommon subsequence* is a string that is a subsequence of exactly one
of the given strings and **not** a subsequence of any other. Given the list `strs`,
**return the length of the longest uncommon subsequence**, or `-1` if none exists.
(Every string is a subsequence of itself.)

**Example**
```
strs = ["aba","cdc","eae"]  ->  3
strs = ["aaa","aaa","aa"]   ->  -1
```

**Constraints:** `2 <= len(strs) <= 50`, `1 <= len(strs[i]) <= 10`, lowercase
letters.
""",
    """def findLUSlength(strs):
    def is_sub(a, b):
        it = iter(b)
        return all(c in it for c in a)
    res = -1
    for i, s in enumerate(strs):
        if all(i == j or not is_sub(s, t) for j, t in enumerate(strs)):
            res = max(res, len(s))
    return res
""",
    visible=[{"strs": ["aba", "cdc", "eae"]}, {"strs": ["aaa", "aaa", "aa"]}],
    hidden=[{"strs": ["aabbcc", "aabbcc", "cb", "abc", "cbc"]},
            {"strs": ["ab", "ab"]}, {"strs": ["a", "b", "c"]},
            {"strs": ["abc", "abcd"]}],
    gen=lambda r: [{"strs": [sstr(r, 1, 5, "ab") for _ in range(r.randint(2, 6))]}
                   for _ in range(6)],
    brute=_lus_brute,
    checks=[({"strs": ["aba", "cdc", "eae"]}, 3),
            ({"strs": ["aaa", "aaa", "aa"]}, -1),
            ({"strs": ["ab", "ab"]}, -1)],
    source="new_p")
