"""Batch 013 of the new_p.txt import (19 problems).

One entry was dropped as a duplicate under a different slug (see `_skips.py`):
`word-ladder` (== `word-ladder-length`).

Two problems return approximate floats; following the bank's established pattern
(see `soup-servings`) the canonical ROUNDS to 5 decimals and the statement asks for
that, so the strict judge can compare exactly: `largest-sum-of-averages`,
`new-21-game` (no brute — rounded known-answer checks instead).
"""
from scripts.build_bank import add, ilist, sstr  # noqa: F401

MOD = 10 ** 9 + 7


# --------------------------- brute / reference helpers ---------------------
def _rep_brute(s1, n1, s2, n2):
    S1 = s1 * n1
    idx = 0
    cnt = 0
    L = len(s2)
    for ch in S1:
        if ch == s2[idx]:
            idx += 1
            if idx == L:
                idx = 0
                cnt += 1
    return cnt // n2


def _numways_brute(s):
    n = len(s)
    cnt = 0
    for i in range(1, n - 1):
        for j in range(i + 1, n):
            a = s[:i].count('1')
            b = s[i:j].count('1')
            c = s[j:].count('1')
            if a == b == c:
                cnt += 1
    return cnt % MOD


def _ugly3_brute(n, a, b, c):
    x = 0
    cnt = 0
    while cnt < n:
        x += 1
        if x % a == 0 or x % b == 0 or x % c == 0:
            cnt += 1
    return x


def _minmoves2_brute(nums):
    return min(sum(abs(x - t) for x in nums) for t in range(min(nums), max(nums) + 1))


def _oej_brute(A):
    n = len(A)
    good = 0
    for start in range(n):
        i, jump, ok = start, 1, True
        while i != n - 1:
            cands = list(range(i + 1, n))
            if jump % 2 == 1:
                valid = [j for j in cands if A[j] >= A[i]]
                if not valid:
                    ok = False
                    break
                m = min(A[j] for j in valid)
            else:
                valid = [j for j in cands if A[j] <= A[i]]
                if not valid:
                    ok = False
                    break
                m = max(A[j] for j in valid)
            j = min(j for j in valid if A[j] == m)
            i = j
            jump += 1
        if i == n - 1 and ok:
            good += 1
    return good


def _repunit_brute(K):
    if K % 2 == 0 or K % 5 == 0:
        return -1
    n = 0
    for length in range(1, K + 1):
        n = n * 10 + 1
        if n % K == 0:
            return length
    return -1


def _digitone_brute(n):
    return sum(str(x).count('1') for x in range(n + 1))


def _div3_brute(nums):
    n = len(nums)
    best = 0
    for mask in range(1 << n):
        s = sum(nums[i] for i in range(n) if mask >> i & 1)
        if s % 3 == 0:
            best = max(best, s)
    return best


def _triplet_brute(nums):
    n = len(nums)
    for j in range(1, n - 1):
        if any(nums[i] < nums[j] for i in range(j)) and \
           any(nums[k] > nums[j] for k in range(j + 1, n)):
            return True
    return False


def _score_brute(S):
    def helper(s):
        total, depth, start = 0, 0, 0
        for i, c in enumerate(s):
            depth += 1 if c == '(' else -1
            if depth == 0:
                inner = s[start + 1:i]
                total += 1 if inner == '' else 2 * helper(inner)
                start = i + 1
        return total
    return helper(S)


def _mutate_brute(arr, target):
    best, bd = 0, float('inf')
    for v in range(0, max(arr) + 1):
        d = abs(sum(min(a, v) for a in arr) - target)
        if d < bd:
            bd, best = d, v
    return best


def _kcat_brute(arr, k):
    a = arr * k
    best = cur = 0
    for x in a:
        cur = max(0, cur + x)
        best = max(best, cur)
    return best % MOD


def _stone4_brute(n):
    from functools import lru_cache

    @lru_cache(None)
    def win(m):
        j = 1
        while j * j <= m:
            if not win(m - j * j):
                return True
            j += 1
        return False

    return win(n)


def _splitavg_brute(nums):
    n = len(nums)
    if n < 2:
        return False
    from itertools import combinations
    total = sum(nums)
    for k in range(1, n):
        for comb in combinations(range(n), k):
            s = sum(nums[i] for i in comb)
            if s * (n - k) == (total - s) * k:
                return True
    return False


def _hindex_brute(citations):
    n = len(citations)
    best = 0
    for h in range(0, n + 1):
        if sum(1 for c in citations if c >= h) >= h:
            best = max(best, h)
    return best


# --------------------------- gen helpers -----------------------------------
def _rank_gen(r):
    k = r.randint(1, 4)
    letters = [chr(ord('A') + i) for i in range(k)]
    votes = []
    for _ in range(r.randint(1, 5)):
        perm = letters[:]
        r.shuffle(perm)
        votes.append("".join(perm))
    return {"votes": votes}


def _rep_gen(r):
    s1 = sstr(r, 1, 6, "ab")
    s2 = sstr(r, 1, 4, "ab")
    return {"s1": s1, "n1": r.randint(0, 30), "s2": s2, "n2": r.randint(1, 4)}


def _oej_gen(r):
    return {"A": [r.randint(0, 9) for _ in range(r.randint(1, 10))]}


def _maze_gen(r):
    blocked = []
    seen = set()
    for _ in range(r.randint(0, 5)):
        p = (r.randint(0, 4), r.randint(0, 4))
        if p not in seen:
            seen.add(p)
            blocked.append([p[0], p[1]])
    while True:
        src = [r.randint(0, 6), r.randint(0, 6)]
        tgt = [r.randint(0, 6), r.randint(0, 6)]
        if tuple(src) not in seen and tuple(tgt) not in seen and src != tgt:
            return {"blocked": blocked, "source": src, "target": tgt}


def _score_gen(r):
    # build a random balanced parentheses string
    n = r.randint(1, 4)
    s = ""
    for _ in range(n):
        s = "(" + s + ")" if r.random() < 0.5 else s + "()"
    return {"S": s}


# ===========================================================================
# 1. Rank Teams by Votes
# ===========================================================================
add("rank-teams-by-votes", "Rank Teams by Votes", "medium",
    ["array", "hash-table", "string", "sorting", "counting"], "rankTeams",
    [("votes", "string[]")], "string",
    """
Each voter ranks all teams from highest to lowest. Teams are ordered by the number
of first-place votes; ties are broken by second-place votes, then third, and so on.
If still tied after every position, order them **alphabetically** by team letter.
**Return the teams as a single string in final ranked order.**

**Examples**
```
votes = ["ABC","ACB","ABC","ACB","ACB"]  ->  "ACB"
votes = ["WXYZ","XYZW"]                   ->  "XWYZ"
votes = ["BCA","CAB","CBA","ABC","ACB","BAC"]  ->  "ABC"
```

**Constraints:** `1 <= len(votes) <= 1000`, all votes are permutations of the same
upper-case letters.
""",
    """def rankTeams(votes):
    from collections import defaultdict
    m = len(votes[0])
    rank = defaultdict(lambda: [0] * m)
    for vote in votes:
        for i, team in enumerate(vote):
            rank[team][i] += 1
    teams = list(rank.keys())
    teams.sort(key=lambda t: (tuple(-c for c in rank[t]), t))
    return "".join(teams)
""",
    visible=[{"votes": ["ABC", "ACB", "ABC", "ACB", "ACB"]}, {"votes": ["WXYZ", "XYZW"]},
             {"votes": ["BCA", "CAB", "CBA", "ABC", "ACB", "BAC"]}],
    hidden=[{"votes": ["ZMNAGUEDSJYLBOPHRQICWFXTVK"]}, {"votes": ["M", "M", "M", "M"]},
            {"votes": ["AB", "AB", "BA"]}, {"votes": ["FVSHJIEMNGYPTQOURDABKWLZCX"]}],
    gen=lambda r: [_rank_gen(r) for _ in range(8)],
    checks=[({"votes": ["ABC", "ACB", "ABC", "ACB", "ACB"]}, "ACB"),
            ({"votes": ["WXYZ", "XYZW"]}, "XWYZ"),
            ({"votes": ["BCA", "CAB", "CBA", "ABC", "ACB", "BAC"]}, "ABC"),
            ({"votes": ["M", "M", "M", "M"]}, "M"),
            ({"votes": ["AB", "AB", "BA"]}, "AB")],
    source="new_p")


# ===========================================================================
# 2. H-Index
# ===========================================================================
add("h-index", "H-Index", "medium",
    ["array", "sorting", "counting"], "hIndex", [("citations", "int[]")], "int",
    """
A researcher's *h-index* is the largest `h` such that they have at least `h` papers
with `h` or more citations each. Given the `citations` count of each paper, **return
the h-index.**

**Example**
```
citations = [3,0,6,1,5]  ->  3   (3 papers with >= 3 citations)
```

**Constraints:** `0 <= len(citations) <= 5000`, `0 <= citations[i] <= 1000`.
""",
    """def hIndex(citations):
    citations.sort(reverse=True)
    h = 0
    for i, c in enumerate(citations):
        if c >= i + 1:
            h = i + 1
        else:
            break
    return h
""",
    visible=[{"citations": [3, 0, 6, 1, 5]}],
    hidden=[{"citations": []}, {"citations": [0]}, {"citations": [100]},
            {"citations": [1, 1, 1]}, {"citations": [0, 0, 0]}, {"citations": [4, 4, 0, 0]}],
    gen=lambda r: [{"citations": [r.randint(0, 10) for _ in range(r.randint(0, 10))]}
                   for _ in range(8)],
    brute=_hindex_brute,
    checks=[({"citations": [3, 0, 6, 1, 5]}, 3), ({"citations": []}, 0),
            ({"citations": [100]}, 1), ({"citations": [1, 1, 1]}, 1)],
    source="new_p")


# ===========================================================================
# 3. Split Array with Same Average
# ===========================================================================
add("split-array-with-same-average", "Split Array with Same Average", "hard",
    ["array", "math", "dynamic-programming", "bitmask"], "splitArraySameAverage",
    [("nums", "int[]")], "bool",
    """
Move every element of `nums` into one of two non-empty lists `B` and `C`. **Return
`true` if it is possible to do so such that `B` and `C` have the same average.**

**Example**
```
nums = [1,2,3,4,5,6,7,8]  ->  true   ([1,4,5,8] and [2,3,6,7] both average 4.5)
```

**Constraints:** `1 <= len(nums) <= 30`, `0 <= nums[i] <= 10^4`.
""",
    """def splitArraySameAverage(nums):
    n = len(nums)
    total = sum(nums)
    dp = [set() for _ in range(n // 2 + 1)]
    dp[0].add(0)
    for x in nums:
        for k in range(len(dp) - 1, 0, -1):
            for s in dp[k - 1]:
                dp[k].add(s + x)
    for k in range(1, n // 2 + 1):
        if total * k % n == 0 and (total * k // n) in dp[k]:
            return True
    return False
""",
    visible=[{"nums": [1, 2, 3, 4, 5, 6, 7, 8]}],
    hidden=[{"nums": [2, 2]}, {"nums": [3, 1]}, {"nums": [1, 2, 3]}, {"nums": [1]},
            {"nums": [0, 0, 0, 0]}, {"nums": [5, 3, 7, 1, 9]}],
    gen=lambda r: [{"nums": [r.randint(0, 12) for _ in range(r.randint(1, 10))]}
                   for _ in range(6)],
    brute=_splitavg_brute,
    checks=[({"nums": [1, 2, 3, 4, 5, 6, 7, 8]}, True), ({"nums": [2, 2]}, True),
            ({"nums": [3, 1]}, False), ({"nums": [1, 2, 3]}, True), ({"nums": [1]}, False)],
    source="new_p")


# ===========================================================================
# 4. Stone Game IV
# ===========================================================================
add("stone-game-iv", "Stone Game IV", "hard",
    ["math", "dynamic-programming", "game-theory"], "winnerSquareGame",
    [("n", "int")], "bool",
    """
Alice and Bob alternate turns (Alice first) with `n` stones in a pile. On a turn a
player removes a non-zero **perfect-square** number of stones; a player who cannot
move loses. Both play optimally. **Return `true` if Alice wins.**

**Examples**
```
n = 1  ->  true
n = 2  ->  false
n = 4  ->  true
n = 7  ->  false
```

**Constraints:** `1 <= n <= 10^5`.
""",
    """def winnerSquareGame(n):
    dp = [False] * (n + 1)
    for i in range(1, n + 1):
        j = 1
        while j * j <= i:
            if not dp[i - j * j]:
                dp[i] = True
                break
            j += 1
    return dp[n]
""",
    visible=[{"n": 1}, {"n": 2}, {"n": 4}, {"n": 7}],
    hidden=[{"n": 3}, {"n": 17}, {"n": 5}, {"n": 9}, {"n": 13}],
    gen=lambda r: [{"n": r.randint(1, 50)} for _ in range(8)],
    brute=_stone4_brute,
    checks=[({"n": 1}, True), ({"n": 2}, False), ({"n": 4}, True), ({"n": 7}, False),
            ({"n": 17}, False)],
    source="new_p")


# ===========================================================================
# 5. Count the Repetitions
# ===========================================================================
add("count-the-repetitions", "Count the Repetitions", "hard",
    ["string", "dynamic-programming"], "getMaxRepetitions",
    [("s1", "string"), ("n1", "int"), ("s2", "string"), ("n2", "int")], "int",
    """
Define `[s, k]` as `s` concatenated `k` times. String `p` *can be obtained from* `q`
if `p` is a subsequence of `q`. With `S1 = [s1, n1]` and `S2 = [s2, n2]`, **return the
maximum integer `M` such that `[S2, M]` can be obtained from `S1`.**

**Example**
```
s1 = "acb", n1 = 4, s2 = "ab", n2 = 2  ->  2
```

**Constraints:** `1 <= len(s1), len(s2) <= 100`, `0 <= n1 <= 10^6`, `1 <= n2 <= 10^6`.
""",
    """def getMaxRepetitions(s1, n1, s2, n2):
    if n1 == 0:
        return 0
    len2 = len(s2)
    s2cnt = [0] * len2
    nxt = [0] * len2
    for i in range(len2):
        cnt, idx = 0, i
        for ch in s1:
            if ch == s2[idx]:
                idx += 1
                if idx == len2:
                    idx = 0
                    cnt += 1
        s2cnt[i] = cnt
        nxt[i] = idx
    total, idx = 0, 0
    for _ in range(n1):
        total += s2cnt[idx]
        idx = nxt[idx]
    return total // n2
""",
    visible=[{"s1": "acb", "n1": 4, "s2": "ab", "n2": 2}],
    hidden=[{"s1": "aaa", "n1": 3, "s2": "aa", "n2": 1},
            {"s1": "abc", "n1": 0, "s2": "a", "n2": 1},
            {"s1": "abcd", "n1": 5, "s2": "dcba", "n2": 1},
            {"s1": "baba", "n1": 11, "s2": "baab", "n2": 1},
            {"s1": "ab", "n1": 10, "s2": "ab", "n2": 3}],
    gen=lambda r: [_rep_gen(r) for _ in range(8)],
    brute=_rep_brute,
    checks=[({"s1": "acb", "n1": 4, "s2": "ab", "n2": 2}, 2),
            ({"s1": "aaa", "n1": 3, "s2": "aa", "n2": 1}, 4),
            ({"s1": "abc", "n1": 0, "s2": "a", "n2": 1}, 0)],
    source="new_p")


# ===========================================================================
# 6. Number of Ways to Split a String
# ===========================================================================
add("number-of-ways-to-split-a-string", "Number of Ways to Split a String", "medium",
    ["string", "math"], "numWays", [("s", "string")], "int",
    """
Split a binary string `s` into three non-empty parts `s1 + s2 + s3 = s`. **Return the
number of splits where `s1`, `s2`, and `s3` contain the same number of `'1'`s**,
modulo `10^9 + 7`.

**Examples**
```
s = "10101"  ->  4
s = "1001"   ->  0
s = "0000"   ->  3
```

**Constraints:** `3 <= len(s) <= 10^5`, `s[i]` is `'0'` or `'1'`.
""",
    """def numWays(s):
    MOD = 10 ** 9 + 7
    total = s.count('1')
    n = len(s)
    if total % 3 != 0:
        return 0
    if total == 0:
        return (n - 1) * (n - 2) // 2 % MOD
    each = total // 3
    ones = [i for i, c in enumerate(s) if c == '1']
    way1 = ones[each] - ones[each - 1]
    way2 = ones[2 * each] - ones[2 * each - 1]
    return (way1 * way2) % MOD
""",
    visible=[{"s": "10101"}, {"s": "1001"}, {"s": "0000"}],
    hidden=[{"s": "100100010100110"}, {"s": "111"}, {"s": "000"}, {"s": "110011"},
            {"s": "101"}],
    gen=lambda r: [{"s": "".join(r.choice("01") for _ in range(r.randint(3, 14)))}
                   for _ in range(8)],
    brute=_numways_brute,
    checks=[({"s": "10101"}, 4), ({"s": "1001"}, 0), ({"s": "0000"}, 3),
            ({"s": "100100010100110"}, 12), ({"s": "111"}, 1)],
    source="new_p")


# ===========================================================================
# 7. Ugly Number III
# ===========================================================================
add("ugly-number-iii", "Ugly Number III", "medium",
    ["math", "binary-search", "number-theory"], "nthUglyNumber",
    [("n", "int"), ("a", "int"), ("b", "int"), ("c", "int")], "int",
    """
An *ugly number* here is a positive integer divisible by `a`, `b`, or `c`. **Return
the `n`-th ugly number** (1-indexed).

**Examples**
```
n = 3, a = 2, b = 3, c = 5   ->  4    (2, 3, 4, 5, 6, ...)
n = 4, a = 2, b = 3, c = 4   ->  6
n = 5, a = 2, b = 11, c = 13 ->  10
```

**Constraints:** `1 <= n, a, b, c <= 10^9`, `1 <= a*b*c <= 10^18`, answer in `[1, 2*10^9]`.
""",
    """def nthUglyNumber(n, a, b, c):
    from math import gcd

    def lcm(x, y):
        return x * y // gcd(x, y)

    ab, ac, bc = lcm(a, b), lcm(a, c), lcm(b, c)
    abc = lcm(ab, c)

    def count(x):
        return x // a + x // b + x // c - x // ab - x // ac - x // bc + x // abc

    lo, hi = 1, 2 * 10 ** 9
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo
""",
    visible=[{"n": 3, "a": 2, "b": 3, "c": 5}, {"n": 4, "a": 2, "b": 3, "c": 4},
             {"n": 5, "a": 2, "b": 11, "c": 13}],
    hidden=[{"n": 1, "a": 2, "b": 3, "c": 4}, {"n": 10, "a": 2, "b": 3, "c": 5},
            {"n": 1, "a": 1, "b": 1, "c": 1}, {"n": 25, "a": 3, "b": 4, "c": 6},
            {"n": 5, "a": 2, "b": 4, "c": 8}],
    gen=lambda r: [{"n": r.randint(1, 30), "a": r.randint(2, 6), "b": r.randint(2, 6),
                    "c": r.randint(2, 6)} for _ in range(8)],
    brute=_ugly3_brute,
    checks=[({"n": 3, "a": 2, "b": 3, "c": 5}, 4), ({"n": 4, "a": 2, "b": 3, "c": 4}, 6),
            ({"n": 5, "a": 2, "b": 11, "c": 13}, 10),
            ({"n": 1000000000, "a": 2, "b": 217983653, "c": 336916467}, 1999999984)],
    source="new_p")


# ===========================================================================
# 8. Minimum Moves to Equal Array Elements II
# ===========================================================================
add("minimum-moves-to-equal-array-elements-ii",
    "Minimum Moves to Equal Array Elements II", "medium",
    ["array", "math", "sorting"], "minMoves2", [("nums", "int[]")], "int",
    """
In one move you increment or decrement a single element by `1`. **Return the minimum
number of moves to make all elements of `nums` equal.**

**Example**
```
nums = [1,2,3]  ->  2   ([1,2,3] -> [2,2,3] -> [2,2,2])
```

**Constraints:** `1 <= len(nums) <= 10^4`, `-10^9 <= nums[i] <= 10^9`.
""",
    """def minMoves2(nums):
    nums.sort()
    med = nums[len(nums) // 2]
    return sum(abs(x - med) for x in nums)
""",
    visible=[{"nums": [1, 2, 3]}],
    hidden=[{"nums": [1]}, {"nums": [1, 10, 2, 9]}, {"nums": [1, 0, 0, 8, 6]},
            {"nums": [-5, 5]}, {"nums": [3, 3, 3]}],
    gen=lambda r: [{"nums": [r.randint(-20, 20) for _ in range(r.randint(1, 10))]}
                   for _ in range(8)],
    brute=_minmoves2_brute,
    checks=[({"nums": [1, 2, 3]}, 2), ({"nums": [1, 10, 2, 9]}, 16), ({"nums": [1]}, 0)],
    source="new_p")


# ===========================================================================
# 9. Odd Even Jump
# ===========================================================================
add("odd-even-jump", "Odd Even Jump", "hard",
    ["array", "dynamic-programming", "stack", "monotonic-stack", "sorting"], "oddEvenJumps",
    [("A", "int[]")], "int",
    """
From an index `i` you may jump forward to some `j > i`. On odd-numbered jumps
(1st, 3rd, ...) you go to the `j` with the smallest `A[j]` that is `>= A[i]`; on
even-numbered jumps to the `j` with the largest `A[j]` that is `<= A[i]` (ties broken
by smallest index; sometimes no legal jump exists). An index is *good* if from it you
can reach the last index. **Return the number of good starting indices.**

**Examples**
```
A = [10,13,12,14,15]  ->  2
A = [2,3,1,1,4]       ->  3
A = [5,1,3,4,2]       ->  3
```

**Constraints:** `1 <= len(A) <= 2*10^4`, `0 <= A[i] < 10^5`.
""",
    """def oddEvenJumps(A):
    n = len(A)

    def make(indices):
        result = [None] * n
        stack = []
        for i in indices:
            while stack and i > stack[-1]:
                result[stack.pop()] = i
            stack.append(i)
        return result

    idx_asc = sorted(range(n), key=lambda i: (A[i], i))
    odd_next = make(idx_asc)
    idx_desc = sorted(range(n), key=lambda i: (-A[i], i))
    even_next = make(idx_desc)

    odd = [False] * n
    even = [False] * n
    odd[n - 1] = even[n - 1] = True
    for i in range(n - 2, -1, -1):
        if odd_next[i] is not None:
            odd[i] = even[odd_next[i]]
        if even_next[i] is not None:
            even[i] = odd[even_next[i]]
    return sum(odd)
""",
    visible=[{"A": [10, 13, 12, 14, 15]}, {"A": [2, 3, 1, 1, 4]}, {"A": [5, 1, 3, 4, 2]}],
    hidden=[{"A": [1]}, {"A": [5, 5, 5]}, {"A": [1, 2]}, {"A": [2, 1]},
            {"A": [4, 3, 2, 1, 0]}],
    gen=lambda r: [_oej_gen(r) for _ in range(8)],
    brute=_oej_brute,
    checks=[({"A": [10, 13, 12, 14, 15]}, 2), ({"A": [2, 3, 1, 1, 4]}, 3),
            ({"A": [5, 1, 3, 4, 2]}, 3), ({"A": [1]}, 1)],
    source="new_p")


# ===========================================================================
# 10. Smallest Integer Divisible by K
# ===========================================================================
add("smallest-integer-divisible-by-k", "Smallest Integer Divisible by K", "medium",
    ["math", "hash-table"], "smallestRepunitDivByK", [("K", "int")], "int",
    """
Find the smallest positive integer `N` made up only of the digit `1` (a *repunit*:
`1, 11, 111, ...`) that is divisible by `K`. **Return the length of `N`, or `-1` if no
such `N` exists.**

**Examples**
```
K = 1  ->  1    (N = 1)
K = 2  ->  -1
K = 3  ->  3    (N = 111)
```

**Constraints:** `1 <= K <= 10^5`.
""",
    """def smallestRepunitDivByK(K):
    if K % 2 == 0 or K % 5 == 0:
        return -1
    rem = 0
    for length in range(1, K + 1):
        rem = (rem * 10 + 1) % K
        if rem == 0:
            return length
    return -1
""",
    visible=[{"K": 1}, {"K": 2}, {"K": 3}],
    hidden=[{"K": 7}, {"K": 5}, {"K": 9}, {"K": 11}, {"K": 13}, {"K": 17}],
    gen=lambda r: [{"K": r.randint(1, 200)} for _ in range(8)],
    brute=_repunit_brute,
    checks=[({"K": 1}, 1), ({"K": 2}, -1), ({"K": 3}, 3), ({"K": 7}, 6), ({"K": 11}, 2)],
    source="new_p")


# ===========================================================================
# 11. Number of Digit One
# ===========================================================================
add("number-of-digit-one", "Number of Digit One", "hard",
    ["math", "recursion"], "countDigitOne", [("n", "int")], "int",
    """
**Return the total number of digit `1`s appearing across all integers from `0` to
`n` inclusive.**

**Example**
```
n = 13  ->  6    (digit 1 appears in 1, 10, 11, 12, 13)
```

**Constraints:** `0 <= n <= 2*10^9`.
""",
    """def countDigitOne(n):
    if n < 0:
        return 0
    count = 0
    i = 1
    while i <= n:
        high = n // (i * 10)
        cur = (n // i) % 10
        low = n % i
        if cur == 0:
            count += high * i
        elif cur == 1:
            count += high * i + low + 1
        else:
            count += (high + 1) * i
        i *= 10
    return count
""",
    visible=[{"n": 13}],
    hidden=[{"n": 0}, {"n": 1}, {"n": 20}, {"n": 100}, {"n": 99}, {"n": 1000}],
    gen=lambda r: [{"n": r.randint(0, 2000)} for _ in range(8)],
    brute=_digitone_brute,
    checks=[({"n": 13}, 6), ({"n": 0}, 0), ({"n": 1}, 1), ({"n": 20}, 12),
            ({"n": 100}, 21)],
    source="new_p")


# ===========================================================================
# 12. Greatest Sum Divisible by Three
# ===========================================================================
add("greatest-sum-divisible-by-three", "Greatest Sum Divisible by Three", "medium",
    ["array", "dynamic-programming", "greedy"], "maxSumDivThree",
    [("nums", "int[]")], "int",
    """
**Return the maximum sum of a subset of `nums` that is divisible by `3`** (choose the
empty subset, sum `0`, if nothing better is possible).

**Examples**
```
nums = [3,6,5,1,8]   ->  18   (3 + 6 + 1 + 8)
nums = [4]           ->  0
nums = [1,2,3,4,4]   ->  12
```

**Constraints:** `1 <= len(nums) <= 4*10^4`, `1 <= nums[i] <= 10^4`.
""",
    """def maxSumDivThree(nums):
    NEG = float('-inf')
    dp = [0, NEG, NEG]
    for x in nums:
        ndp = dp[:]
        for r in range(3):
            if dp[r] > NEG:
                nr = (r + x) % 3
                ndp[nr] = max(ndp[nr], dp[r] + x)
        dp = ndp
    return dp[0]
""",
    visible=[{"nums": [3, 6, 5, 1, 8]}, {"nums": [4]}, {"nums": [1, 2, 3, 4, 4]}],
    hidden=[{"nums": [1]}, {"nums": [3]}, {"nums": [2, 2, 2]}, {"nums": [1, 2, 3, 4, 5, 6]},
            {"nums": [9, 9, 9]}],
    gen=lambda r: [{"nums": [r.randint(1, 20) for _ in range(r.randint(1, 12))]}
                   for _ in range(8)],
    brute=_div3_brute,
    checks=[({"nums": [3, 6, 5, 1, 8]}, 18), ({"nums": [4]}, 0),
            ({"nums": [1, 2, 3, 4, 4]}, 12), ({"nums": [1]}, 0)],
    source="new_p")


# ===========================================================================
# 13. Escape a Large Maze
# ===========================================================================
add("escape-a-large-maze", "Escape a Large Maze", "hard",
    ["array", "hash-table", "breadth-first-search", "depth-first-search"],
    "isEscapePossible",
    [("blocked", "int[][]"), ("source", "int[]"), ("target", "int[]")], "bool",
    """
On a `10^6 x 10^6` grid (`0 <= x, y < 10^6`) some cells are blocked. From `source`
you may step to a 4-directionally adjacent in-grid cell that is not blocked. **Return
`true` if `target` is reachable from `source`.**

**Examples**
```
blocked = [[0,1],[1,0]], source = [0,0], target = [0,2]  ->  false
blocked = [], source = [0,0], target = [999999,999999]    ->  true
```

**Constraints:** `0 <= len(blocked) <= 200`, all coordinates in `[0, 10^6)`,
`source != target`.
""",
    """def isEscapePossible(blocked, source, target):
    if not blocked:
        return True
    from collections import deque
    block = set(map(tuple, blocked))
    B = len(blocked)
    limit = B * (B - 1) // 2
    M = 10 ** 6

    def bfs(s, t):
        s, t = tuple(s), tuple(t)
        seen = {s}
        q = deque([s])
        while q:
            if len(seen) > limit:
                return True
            x, y = q.popleft()
            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < M and 0 <= ny < M and (nx, ny) not in block and (nx, ny) not in seen:
                    if (nx, ny) == t:
                        return True
                    seen.add((nx, ny))
                    q.append((nx, ny))
        return False

    return bfs(source, target) and bfs(target, source)
""",
    visible=[{"blocked": [[0, 1], [1, 0]], "source": [0, 0], "target": [0, 2]},
             {"blocked": [], "source": [0, 0], "target": [999999, 999999]}],
    hidden=[{"blocked": [[0, 1], [1, 0]], "source": [2, 0], "target": [0, 0]},
            {"blocked": [[0, 1]], "source": [0, 0], "target": [2, 2]},
            {"blocked": [], "source": [5, 5], "target": [6, 6]},
            {"blocked": [[1, 0], [0, 1]], "source": [0, 0], "target": [5, 5]}],
    gen=lambda r: [_maze_gen(r) for _ in range(6)],
    checks=[({"blocked": [[0, 1], [1, 0]], "source": [0, 0], "target": [0, 2]}, False),
            ({"blocked": [], "source": [0, 0], "target": [999999, 999999]}, True),
            ({"blocked": [[0, 1], [1, 0]], "source": [2, 0], "target": [0, 0]}, False),
            ({"blocked": [[0, 1]], "source": [0, 0], "target": [2, 2]}, True)],
    source="new_p")


# ===========================================================================
# 14. Increasing Triplet Subsequence
# ===========================================================================
add("increasing-triplet-subsequence", "Increasing Triplet Subsequence", "medium",
    ["array", "greedy"], "increasingTriplet", [("nums", "int[]")], "bool",
    """
**Return `true` if there exist indices `i < j < k` with
`nums[i] < nums[j] < nums[k]`.** Aim for `O(n)` time and `O(1)` space.

**Examples**
```
nums = [1,2,3,4,5]  ->  true
nums = [5,4,3,2,1]  ->  false
nums = [2,1,5,0,4,6] ->  true
```

**Constraints:** `1 <= len(nums) <= 5*10^5`, `-2^31 <= nums[i] <= 2^31 - 1`.
""",
    """def increasingTriplet(nums):
    first = second = float('inf')
    for x in nums:
        if x <= first:
            first = x
        elif x <= second:
            second = x
        else:
            return True
    return False
""",
    visible=[{"nums": [1, 2, 3, 4, 5]}, {"nums": [5, 4, 3, 2, 1]}, {"nums": [2, 1, 5, 0, 4, 6]}],
    hidden=[{"nums": [1]}, {"nums": [1, 1, 1]}, {"nums": [2, 4, -2, -3, 0, 1]},
            {"nums": [20, 100, 10, 12, 5, 13]}, {"nums": [5, 5, 5, 4]}],
    gen=lambda r: [{"nums": [r.randint(-5, 5) for _ in range(r.randint(0, 10))]}
                   for _ in range(8)],
    brute=_triplet_brute,
    checks=[({"nums": [1, 2, 3, 4, 5]}, True), ({"nums": [5, 4, 3, 2, 1]}, False),
            ({"nums": [2, 1, 5, 0, 4, 6]}, True), ({"nums": [1, 1, 1]}, False)],
    source="new_p")


# ===========================================================================
# 15. Largest Sum of Averages  (float -> rounded to 5 decimals)
# ===========================================================================
add("largest-sum-of-averages", "Largest Sum of Averages", "medium",
    ["array", "dynamic-programming", "prefix-sum"], "largestSumOfAverages",
    [("A", "int[]"), ("K", "int")], "float",
    """
Partition `A` into at most `K` non-empty **adjacent** groups. The score is the sum of
the averages of the groups. **Return the largest possible score, rounded to 5 decimal
places.** (Answers within `1e-6` are accepted.)

**Example**
```
A = [9,1,2,3,9], K = 3  ->  20.00000   (groups [9], [1,2,3], [9]: 9 + 2 + 9)
```

**Constraints:** `1 <= len(A) <= 100`, `1 <= A[i] <= 10^4`, `1 <= K <= len(A)`.
""",
    """def largestSumOfAverages(A, K):
    from functools import lru_cache
    n = len(A)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + A[i]

    def avg(i, j):
        return (pre[j] - pre[i]) / (j - i)

    @lru_cache(None)
    def dp(i, k):
        if k == 1:
            return avg(i, n)
        best = 0.0
        for j in range(i + 1, n - k + 2):
            best = max(best, avg(i, j) + dp(j, k - 1))
        return best

    return round(dp(0, K), 5)
""",
    visible=[{"A": [9, 1, 2, 3, 9], "K": 3}],
    hidden=[{"A": [1], "K": 1}, {"A": [1, 2, 3, 4, 5], "K": 1},
            {"A": [4, 1, 1, 1], "K": 2}, {"A": [4, 1, 1, 1], "K": 4},
            {"A": [10, 10, 10], "K": 2}],
    gen=lambda r: [(lambda a: {"A": a, "K": r.randint(1, len(a))})
                   ([r.randint(1, 20) for _ in range(r.randint(1, 7))]) for _ in range(6)],
    checks=[({"A": [9, 1, 2, 3, 9], "K": 3}, 20.0), ({"A": [1], "K": 1}, 1.0),
            ({"A": [1, 2, 3, 4, 5], "K": 1}, 3.0), ({"A": [4, 1, 1, 1], "K": 2}, 5.0)],
    source="new_p")


# ===========================================================================
# 16. New 21 Game  (float -> rounded to 5 decimals)
# ===========================================================================
add("new-21-game", "New 21 Game", "medium",
    ["math", "dynamic-programming", "probability", "sliding-window"], "new21Game",
    [("N", "int"), ("K", "int"), ("W", "int")], "float",
    """
Alice starts with `0` points and repeatedly draws while she has fewer than `K`
points; each draw adds a uniformly random integer in `[1, W]`. She stops once she has
`K` or more points. **Return the probability that her final score is `<= N`, rounded
to 5 decimal places.** (Answers within `1e-5` are accepted.)

**Examples**
```
N = 10, K = 1, W = 10  ->  1.00000
N = 6, K = 1, W = 10   ->  0.60000
N = 21, K = 17, W = 10 ->  0.73278
```

**Constraints:** `0 <= K <= N <= 10^4`, `1 <= W <= 10^4`.
""",
    """def new21Game(N, K, W):
    if K == 0 or N >= K - 1 + W:
        return 1.0
    dp = [0.0] * (N + 1)
    dp[0] = 1.0
    Wsum = 1.0
    res = 0.0
    for i in range(1, N + 1):
        dp[i] = Wsum / W
        if i < K:
            Wsum += dp[i]
        else:
            res += dp[i]
        if 0 <= i - W < K:
            Wsum -= dp[i - W]
    return round(res, 5)
""",
    visible=[{"N": 10, "K": 1, "W": 10}, {"N": 6, "K": 1, "W": 10},
             {"N": 21, "K": 17, "W": 10}],
    hidden=[{"N": 1, "K": 0, "W": 1}, {"N": 5, "K": 1, "W": 1},
            {"N": 0, "K": 0, "W": 1}, {"N": 8, "K": 5, "W": 5}, {"N": 3, "K": 2, "W": 3}],
    gen=lambda r: [(lambda k, w: {"N": r.randint(k, k + w + 2), "K": k, "W": w})
                   (r.randint(0, 8), r.randint(1, 8)) for _ in range(6)],
    checks=[({"N": 10, "K": 1, "W": 10}, 1.0), ({"N": 6, "K": 1, "W": 10}, 0.6),
            ({"N": 21, "K": 17, "W": 10}, 0.73278), ({"N": 1, "K": 0, "W": 1}, 1.0),
            ({"N": 5, "K": 1, "W": 1}, 1.0)],
    source="new_p")


# ===========================================================================
# 17. Score of Parentheses
# ===========================================================================
add("score-of-parentheses", "Score of Parentheses", "medium",
    ["string", "stack"], "scoreOfParentheses", [("S", "string")], "int",
    """
A balanced parentheses string is scored by: `()` is `1`; `AB` is `A + B`; `(A)` is
`2 * A`. **Return the score of `S`.**

**Examples**
```
"()"        ->  1
"(())"      ->  2
"()()"      ->  2
"(()(()))"  ->  6
```

**Constraints:** `2 <= len(S) <= 50`, `S` is a balanced string of `(` and `)`.
""",
    """def scoreOfParentheses(S):
    stack = [0]
    for c in S:
        if c == '(':
            stack.append(0)
        else:
            v = stack.pop()
            stack[-1] += max(2 * v, 1)
    return stack[0]
""",
    visible=[{"S": "()"}, {"S": "(())"}, {"S": "()()"}, {"S": "(()(()))"}],
    hidden=[{"S": "((()))"}, {"S": "()(())"}, {"S": "(()())"}, {"S": "((())())"}],
    gen=lambda r: [_score_gen(r) for _ in range(8)],
    brute=_score_brute,
    checks=[({"S": "()"}, 1), ({"S": "(())"}, 2), ({"S": "()()"}, 2), ({"S": "(()(()))"}, 6)],
    source="new_p")


# ===========================================================================
# 18. Sum of Mutated Array Closest to Target
# ===========================================================================
add("sum-of-mutated-array-closest-to-target", "Sum of Mutated Array Closest to Target",
    "medium", ["array", "binary-search", "sorting"], "findBestValue",
    [("arr", "int[]"), ("target", "int")], "int",
    """
Choose an integer `value`; replace every element of `arr` greater than `value` with
`value`. **Return the `value` that makes the array's sum as close as possible to
`target`** (smallest such `value` on a tie). The answer need not appear in `arr`.

**Examples**
```
arr = [4,9,3], target = 10  ->  3    (becomes [3,3,3], sum 9)
arr = [2,3,5], target = 10  ->  5
```

**Constraints:** `1 <= len(arr) <= 10^4`, `1 <= arr[i], target <= 10^5`.
""",
    """def findBestValue(arr, target):
    arr_sorted = sorted(arr)
    n = len(arr)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + arr_sorted[i]
    import bisect

    def total(v):
        idx = bisect.bisect_right(arr_sorted, v)
        return pre[idx] + (n - idx) * v

    best, bd = 0, float('inf')
    for v in range(0, max(arr) + 1):
        d = abs(total(v) - target)
        if d < bd:
            bd, best = d, v
    return best
""",
    visible=[{"arr": [4, 9, 3], "target": 10}, {"arr": [2, 3, 5], "target": 10}],
    hidden=[{"arr": [2], "target": 5}, {"arr": [1, 1, 1], "target": 1},
            {"arr": [7, 7, 7], "target": 100}, {"arr": [3, 6, 9], "target": 0}],
    gen=lambda r: [{"arr": [r.randint(1, 20) for _ in range(r.randint(1, 8))],
                    "target": r.randint(1, 60)} for _ in range(8)],
    brute=_mutate_brute,
    checks=[({"arr": [4, 9, 3], "target": 10}, 3), ({"arr": [2, 3, 5], "target": 10}, 5),
            ({"arr": [60864, 25176, 27249, 21296, 20204], "target": 56803}, 11361),
            ({"arr": [2], "target": 5}, 2)],
    source="new_p")


# ===========================================================================
# 19. K-Concatenation Maximum Sum
# ===========================================================================
add("k-concatenation-maximum-sum", "K-Concatenation Maximum Sum", "medium",
    ["array", "dynamic-programming"], "kConcatenationMaxSum",
    [("arr", "int[]"), ("k", "int")], "int",
    """
Repeat `arr` `k` times to form a longer array. **Return the maximum subarray sum of
that array** (an empty subarray has sum `0`), modulo `10^9 + 7`.

**Examples**
```
arr = [1,2], k = 3    ->  9
arr = [1,-2,1], k = 5  ->  2
arr = [-1,-2], k = 7   ->  0
```

**Constraints:** `1 <= len(arr) <= 10^5`, `1 <= k <= 10^5`, `-10^4 <= arr[i] <= 10^4`.
""",
    """def kConcatenationMaxSum(arr, k):
    MOD = 10 ** 9 + 7

    def kadane(a):
        best = cur = 0
        for x in a:
            cur = max(0, cur + x)
            best = max(best, cur)
        return best

    total = sum(arr)
    if k == 1:
        return kadane(arr) % MOD
    two = kadane(arr + arr)
    if total > 0:
        return (two + (k - 2) * total) % MOD
    return two % MOD
""",
    visible=[{"arr": [1, 2], "k": 3}, {"arr": [1, -2, 1], "k": 5}, {"arr": [-1, -2], "k": 7}],
    hidden=[{"arr": [1], "k": 1}, {"arr": [-1], "k": 4}, {"arr": [2, -1, 2], "k": 3},
            {"arr": [5], "k": 5}, {"arr": [-2, 3, -1], "k": 2}],
    gen=lambda r: [{"arr": [r.randint(-5, 5) for _ in range(r.randint(1, 6))],
                    "k": r.randint(1, 4)} for _ in range(8)],
    brute=_kcat_brute,
    checks=[({"arr": [1, 2], "k": 3}, 9), ({"arr": [1, -2, 1], "k": 5}, 2),
            ({"arr": [-1, -2], "k": 7}, 0), ({"arr": [5], "k": 5}, 25)],
    source="new_p")
