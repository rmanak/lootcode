"""Batch 007 of the new_p.txt import (18 problems).

Two entries from this slice of the worklist were dropped as duplicates of
existing bank problems under different slugs (see `_skips.py`):
`path-with-maximum-probability` (== maximum-probability-path) and
`kth-largest-element-in-an-array` (== kth-largest-element).
"""
from scripts.build_bank import add, ilist, sstr  # noqa: F401


# --------------------------- brute / reference helpers ---------------------
def _koko_brute(piles, H):
    k = 1
    while True:
        if sum((p + k - 1) // k for p in piles) <= H:
            return k
        k += 1


def _divisor_brute(nums, threshold):
    d = 1
    while True:
        if sum((x + d - 1) // d for x in nums) <= threshold:
            return d
        d += 1


def _wiggle_brute(nums):
    n = len(nums)
    if n < 2:
        return n
    up = [1] * n
    down = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[i] > nums[j]:
                up[i] = max(up[i], down[j] + 1)
            elif nums[i] < nums[j]:
                down[i] = max(down[i], up[j] + 1)
    return max(max(up), max(down))


def _verbal_brute(words, result):
    from itertools import permutations
    letters = list(set("".join(words) + result))
    if len(letters) > 10:
        return False
    if any(len(w) > len(result) for w in words):
        return False
    leading = set(w[0] for w in (words + [result]) if len(w) > 1)
    for perm in permutations(range(10), len(letters)):
        m = dict(zip(letters, perm))
        if any(m[c] == 0 for c in leading):
            continue
        s = sum(int("".join(str(m[c]) for c in w)) for w in words)
        if s == int("".join(str(m[c]) for c in result)):
            return True
    return False


_KNIGHT_MOVES = {0: [4, 6], 1: [6, 8], 2: [7, 9], 3: [4, 8], 4: [0, 3, 9],
                 5: [], 6: [0, 1, 7], 7: [2, 6], 8: [1, 3], 9: [2, 4]}


def _knight_brute(n):
    def dfs(d, steps):
        if steps == 0:
            return 1
        return sum(dfs(nx, steps - 1) for nx in _KNIGHT_MOVES[d])
    return sum(dfs(d, n - 1) for d in range(10)) % (10 ** 9 + 7)


def _maxlen_brute(arr):
    valid = [s for s in arr if len(set(s)) == len(s)]
    m = len(valid)
    best = 0
    for mask in range(1 << m):
        chars = "".join(valid[i] for i in range(m) if mask & (1 << i))
        if len(set(chars)) == len(chars):
            best = max(best, len(chars))
    return best


def _maxnonover_brute(nums, target):
    n = len(nums)
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i - 1]
        s = 0
        for j in range(i - 1, -1, -1):
            s += nums[j]
            if s == target:
                dp[i] = max(dp[i], dp[j] + 1)
    return dp[n]


def _numsplits_brute(s):
    n = len(s)
    return sum(1 for i in range(1, n) if len(set(s[:i])) == len(set(s[i:])))


def _baseneg2_brute(N):
    if N == 0:
        return "0"
    for L in range(1, 40):
        for mask in range(1 << (L - 1), 1 << L):
            bits = bin(mask)[2:]
            val = sum((1 if bits[L - 1 - k] == '1' else 0) * ((-2) ** k)
                      for k in range(L))
            if val == N:
                return bits
    return ""


def _kapart_brute(nums, k):
    pos = [i for i, x in enumerate(nums) if x == 1]
    return all(pos[i + 1] - pos[i] - 1 >= k for i in range(len(pos) - 1))


def _happy_brute(n, k):
    res = []

    def dfs(cur):
        if len(cur) == n:
            res.append(cur)
            return
        for c in "abc":
            if cur and cur[-1] == c:
                continue
            dfs(cur + c)
    dfs("")
    return res[k - 1] if k <= len(res) else ""


def _candies_brute(status, candies, keys, containedBoxes, initialBoxes):
    have_box = set(initialBoxes)
    have_key = set()
    opened = set()
    changed = True
    while changed:
        changed = False
        for b in list(have_box):
            if b not in opened and (status[b] == 1 or b in have_key):
                opened.add(b)
                changed = True
                for k in keys[b]:
                    if k not in have_key:
                        have_key.add(k)
                        changed = True
                for nb in containedBoxes[b]:
                    if nb not in have_box:
                        have_box.add(nb)
                        changed = True
    return sum(candies[b] for b in opened)


def _racecar_brute(target):
    dp = [0, 1, 4] + [0] * target
    for t in range(3, target + 1):
        k = t.bit_length()
        if t == (1 << k) - 1:
            dp[t] = k
            continue
        dp[t] = k + 1 + dp[(1 << k) - 1 - t]
        for j in range(k - 1):
            dp[t] = min(dp[t], dp[t - (1 << (k - 1)) + (1 << j)] + (k - 1) + j + 2)
    return dp[target]


def _absdiff_brute(nums, limit):
    n = len(nums)
    best = 0
    for i in range(n):
        mn = mx = nums[i]
        for j in range(i, n):
            mn = min(mn, nums[j])
            mx = max(mx, nums[j])
            if mx - mn <= limit:
                best = max(best, j - i + 1)
            else:
                break
    return best


def _vps_brute(s):
    from functools import lru_cache

    @lru_cache(None)
    def go(i, bal):
        if bal < 0:
            return False
        if i == len(s):
            return bal == 0
        c = s[i]
        if c == '(':
            return go(i + 1, bal + 1)
        if c == ')':
            return go(i + 1, bal - 1)
        return go(i + 1, bal + 1) or go(i + 1, bal - 1) or go(i + 1, bal)
    return go(0, 0)


def _bulb_brute(light):
    n = len(light)
    on = set()
    ans = 0
    for k in range(n):
        on.add(light[k])
        if on == set(range(1, k + 2)):
            ans += 1
    return ans


# gen helpers ---------------------------------------------------------------
_DIGIT_WORDS = ["zero", "one", "two", "three", "four", "five", "six",
                "seven", "eight", "nine"]


def _scrambled_digits(r):
    ds = [r.randint(0, 9) for _ in range(r.randint(1, 5))]
    letters = list("".join(_DIGIT_WORDS[d] for d in ds))
    return {"s": "".join(r.sample(letters, len(letters)))}


def _zuma_board(r):
    chars = "RYBGW"
    b = []
    for _ in range(r.randint(1, 6)):
        c = r.choice(chars)
        while len(b) >= 2 and b[-1] == c and b[-2] == c:
            c = r.choice(chars)
        b.append(c)
    return "".join(b)


# ===========================================================================
# 1. Koko Eating Bananas
# ===========================================================================
add("koko-eating-bananas", "Koko Eating Bananas", "medium",
    ["array", "binary-search"], "minEatingSpeed",
    [("piles", "int[]"), ("H", "int")], "int",
    """
Koko has `len(piles)` piles of bananas; pile `i` has `piles[i]` bananas. The guards
return in `H` hours. At a chosen integer speed `K` bananas/hour she eats from one
pile each hour, finishing that pile early if it has fewer than `K` left (she does not
move on to another pile that hour). **Return the smallest `K`** that lets her eat
everything within `H` hours.

**Examples**
```
piles = [3,6,7,11], H = 8        ->  4
piles = [30,11,23,4,20], H = 5   ->  30
piles = [30,11,23,4,20], H = 6   ->  23
```

**Constraints:** `1 <= len(piles) <= 10^4`, `len(piles) <= H <= 10^9`,
`1 <= piles[i] <= 10^9`.
""",
    """def minEatingSpeed(piles, H):
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        hours = sum((p + mid - 1) // mid for p in piles)
        if hours <= H:
            hi = mid
        else:
            lo = mid + 1
    return lo
""",
    visible=[{"piles": [3, 6, 7, 11], "H": 8}, {"piles": [30, 11, 23, 4, 20], "H": 5},
             {"piles": [30, 11, 23, 4, 20], "H": 6}],
    hidden=[{"piles": [1], "H": 1}, {"piles": [312884470], "H": 312884469},
            {"piles": [3, 6, 7, 11], "H": 4}],
    gen=lambda r: [(lambda p: {"piles": p, "H": r.randint(len(p), 3 * len(p))})
                   ([r.randint(1, 20) for _ in range(r.randint(1, 6))]) for _ in range(6)],
    brute=_koko_brute,
    checks=[({"piles": [3, 6, 7, 11], "H": 8}, 4),
            ({"piles": [30, 11, 23, 4, 20], "H": 5}, 30),
            ({"piles": [30, 11, 23, 4, 20], "H": 6}, 23),
            ({"piles": [1000000000], "H": 2}, 500000000)],
    source="new_p")


# ===========================================================================
# 2. Reconstruct Original Digits From English
# ===========================================================================
add("reconstruct-original-digits-from-english",
    "Reconstruct Original Digits From English", "medium",
    ["string", "hash-table", "math"], "originalDigits", [("s", "string")], "string",
    """
`s` is an out-of-order English spelling of some digits `0`-`9` (each digit `d`
contributes the letters of its English word, e.g. `"two"` for `2`). The input is
guaranteed valid. **Return the digits in ascending order** as a string.

**Examples**
```
s = "owoztneoer"  ->  "012"
s = "fviefuro"    ->  "45"
```

**Constraints:** `s` is lowercase letters, `1 <= len(s) < 50000`.
""",
    """def originalDigits(s):
    from collections import Counter
    c = Counter(s)
    cnt = [0] * 10
    cnt[0] = c['z']
    cnt[2] = c['w']
    cnt[4] = c['u']
    cnt[6] = c['x']
    cnt[8] = c['g']
    cnt[3] = c['h'] - cnt[8]
    cnt[5] = c['f'] - cnt[4]
    cnt[7] = c['s'] - cnt[6]
    cnt[1] = c['o'] - cnt[0] - cnt[2] - cnt[4]
    cnt[9] = c['i'] - cnt[5] - cnt[6] - cnt[8]
    return "".join(str(d) * cnt[d] for d in range(10))
""",
    visible=[{"s": "owoztneoer"}, {"s": "fviefuro"}],
    hidden=[{"s": "zeroonetwothreefourfivesixseveneightnine"},
            {"s": "nine"}, {"s": "eight"}, {"s": "zero"}],
    gen=lambda r: [_scrambled_digits(r) for _ in range(8)],
    checks=[({"s": "owoztneoer"}, "012"), ({"s": "fviefuro"}, "45"),
            ({"s": "zeroonetwothreefourfivesixseveneightnine"}, "0123456789"),
            ({"s": "nine"}, "9")],
    source="new_p")


# ===========================================================================
# 3. Find the Smallest Divisor Given a Threshold
# ===========================================================================
add("find-the-smallest-divisor-given-a-threshold",
    "Find the Smallest Divisor Given a Threshold", "medium",
    ["array", "binary-search"], "smallestDivisor",
    [("nums", "int[]"), ("threshold", "int")], "int",
    """
Choose a positive integer divisor `d`, divide every element of `nums` by `d`
**rounding each quotient up** to the nearest integer, and sum the results. **Return
the smallest `d`** for which that sum is `<= threshold` (a valid answer is
guaranteed).

**Examples**
```
nums = [1,2,5,9], threshold = 6       ->  5
nums = [2,3,5,7,11], threshold = 11   ->  3
nums = [19], threshold = 5            ->  4
```

**Constraints:** `1 <= len(nums) <= 5*10^4`, `1 <= nums[i] <= 10^6`,
`len(nums) <= threshold <= 10^6`.
""",
    """def smallestDivisor(nums, threshold):
    lo, hi = 1, max(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        s = sum((x + mid - 1) // mid for x in nums)
        if s <= threshold:
            hi = mid
        else:
            lo = mid + 1
    return lo
""",
    visible=[{"nums": [1, 2, 5, 9], "threshold": 6},
             {"nums": [2, 3, 5, 7, 11], "threshold": 11}, {"nums": [19], "threshold": 5}],
    hidden=[{"nums": [1], "threshold": 1},
            {"nums": [2, 3, 5, 7, 11], "threshold": 5}, {"nums": [1, 1, 1], "threshold": 3}],
    gen=lambda r: [(lambda nums: {"nums": nums, "threshold": r.randint(len(nums), 4 * len(nums))})
                   ([r.randint(1, 30) for _ in range(r.randint(1, 6))]) for _ in range(6)],
    brute=_divisor_brute,
    checks=[({"nums": [1, 2, 5, 9], "threshold": 6}, 5),
            ({"nums": [2, 3, 5, 7, 11], "threshold": 11}, 3),
            ({"nums": [19], "threshold": 5}, 4),
            ({"nums": [1000000], "threshold": 1}, 1000000)],
    source="new_p")


# ===========================================================================
# 4. Wiggle Subsequence
# ===========================================================================
add("wiggle-subsequence", "Wiggle Subsequence", "medium",
    ["array", "dynamic-programming", "greedy"], "wiggleMaxLength",
    [("nums", "int[]")], "int",
    """
A *wiggle sequence* is one whose successive differences strictly alternate between
positive and negative (a sequence of fewer than two elements is trivially a wiggle
sequence). **Return the length of the longest subsequence of `nums` that is a wiggle
sequence** (a subsequence deletes zero or more elements, keeping the order).

**Examples**
```
nums = [1,7,4,9,2,5]                  ->  6
nums = [1,17,5,10,13,15,10,5,16,8]    ->  7
nums = [1,2,3,4,5,6,7,8,9]            ->  2
```

**Constraints:** `1 <= len(nums) <= 1000`, `0 <= nums[i] <= 1000`.
""",
    """def wiggleMaxLength(nums):
    if len(nums) < 2:
        return len(nums)
    up = down = 1
    for i in range(1, len(nums)):
        if nums[i] > nums[i - 1]:
            up = down + 1
        elif nums[i] < nums[i - 1]:
            down = up + 1
    return max(up, down)
""",
    visible=[{"nums": [1, 7, 4, 9, 2, 5]},
             {"nums": [1, 17, 5, 10, 13, 15, 10, 5, 16, 8]},
             {"nums": [1, 2, 3, 4, 5, 6, 7, 8, 9]}],
    hidden=[{"nums": [0]}, {"nums": [3, 3, 3]}, {"nums": [1, 2]}, {"nums": [2, 1]}],
    gen=lambda r: [{"nums": [r.randint(0, 6) for _ in range(r.randint(1, 12))]}
                   for _ in range(6)],
    brute=_wiggle_brute,
    checks=[({"nums": [1, 7, 4, 9, 2, 5]}, 6),
            ({"nums": [1, 17, 5, 10, 13, 15, 10, 5, 16, 8]}, 7),
            ({"nums": [1, 2, 3, 4, 5, 6, 7, 8, 9]}, 2)],
    source="new_p")


# ===========================================================================
# 5. Verbal Arithmetic Puzzle
# ===========================================================================
add("verbal-arithmetic-puzzle", "Verbal Arithmetic Puzzle", "hard",
    ["math", "backtracking"], "isSolvable",
    [("words", "string[]"), ("result", "string")], "bool",
    """
Each distinct letter maps to a distinct digit `0`-`9`; every word (and `result`) is
read as a number with **no leading zero** (a single-letter word may be `0`). **Return
`true` if the letters can be assigned so that the `words` sum to `result`.**

**Examples**
```
words = ["SEND","MORE"], result = "MONEY"          ->  true
words = ["SIX","SEVEN","SEVEN"], result = "TWENTY"  ->  true
words = ["LEET","CODE"], result = "POINT"          ->  false
```

**Constraints:** `2 <= len(words) <= 5`, `1 <= len(words[i]), len(result) <= 7`,
uppercase letters, at most 10 distinct letters overall.
""",
    """def isSolvable(words, result):
    rows = words + [result]
    if any(len(w) > len(result) for w in words):
        return False
    L = len(result)
    leading = set(w[0] for w in rows if len(w) > 1)
    cols = []
    for i in range(L):
        wc = [w[-1 - i] for w in words if i < len(w)]
        rc = result[-1 - i]
        cols.append((wc, rc))
    assigned = {}
    used = [False] * 10

    def place(col, carry):
        if col == L:
            return carry == 0
        wc, rc = cols[col]

        def rec(k, s):
            if k == len(wc):
                total = s + carry
                d = total % 10
                nc = total // 10
                if rc in assigned:
                    if assigned[rc] != d or (d == 0 and rc in leading):
                        return False
                    return place(col + 1, nc)
                if used[d] or (d == 0 and rc in leading):
                    return False
                assigned[rc] = d
                used[d] = True
                ok = place(col + 1, nc)
                del assigned[rc]
                used[d] = False
                return ok
            ch = wc[k]
            if ch in assigned:
                return rec(k + 1, s + assigned[ch])
            for d in range(10):
                if used[d] or (d == 0 and ch in leading):
                    continue
                assigned[ch] = d
                used[d] = True
                if rec(k + 1, s + d):
                    del assigned[ch]
                    used[d] = False
                    return True
                del assigned[ch]
                used[d] = False
            return False

        return rec(0, 0)

    return place(0, 0)
""",
    visible=[{"words": ["SEND", "MORE"], "result": "MONEY"},
             {"words": ["SIX", "SEVEN", "SEVEN"], "result": "TWENTY"},
             {"words": ["LEET", "CODE"], "result": "POINT"}],
    hidden=[{"words": ["A", "B"], "result": "A"}, {"words": ["AB", "BA"], "result": "AA"},
            {"words": ["ACA", "DD"], "result": "BD"}, {"words": ["THIS", "IS"], "result": "TOO"}],
    gen=lambda r: [(lambda nw: {"words": ["".join(r.choice("ABCD") for _ in range(r.randint(1, 3)))
                                          for _ in range(nw)],
                                "result": "".join(r.choice("ABCD") for _ in range(r.randint(1, 3)))})
                   (r.randint(2, 3)) for _ in range(8)],
    brute=_verbal_brute,
    checks=[({"words": ["SEND", "MORE"], "result": "MONEY"}, True),
            ({"words": ["SIX", "SEVEN", "SEVEN"], "result": "TWENTY"}, True),
            ({"words": ["LEET", "CODE"], "result": "POINT"}, False)],
    source="new_p")


# ===========================================================================
# 6. Knight Dialer
# ===========================================================================
add("knight-dialer", "Knight Dialer", "medium",
    ["dynamic-programming", "math"], "knightDialer", [("n", "int")], "int",
    """
A chess knight stands on a phone keypad and makes `n - 1` knight moves, spelling an
`n`-digit number. The keypad and the moves from each digit are:
```
1 2 3
4 5 6
7 8 9
  0
0 -> 4,6   1 -> 6,8   2 -> 7,9   3 -> 4,8   4 -> 0,3,9
5 -> (none)  6 -> 0,1,7  7 -> 2,6   8 -> 1,3   9 -> 2,4
```
The knight may start on any digit. **Return how many distinct numbers of length `n`
can be dialed, modulo `10^9 + 7`.**

**Examples**
```
n = 1     ->  10
n = 2     ->  20
n = 3     ->  46
n = 3131  ->  136006598
```

**Constraints:** `1 <= n <= 5000`.
""",
    """def knightDialer(n):
    MOD = 10 ** 9 + 7
    moves = {0: [4, 6], 1: [6, 8], 2: [7, 9], 3: [4, 8], 4: [0, 3, 9],
             5: [], 6: [0, 1, 7], 7: [2, 6], 8: [1, 3], 9: [2, 4]}
    dp = [1] * 10
    for _ in range(n - 1):
        ndp = [0] * 10
        for d in range(10):
            for nx in moves[d]:
                ndp[nx] = (ndp[nx] + dp[d]) % MOD
        dp = ndp
    return sum(dp) % MOD
""",
    visible=[{"n": 1}, {"n": 2}, {"n": 3}],
    hidden=[{"n": 4}, {"n": 5}, {"n": 6}, {"n": 7}],
    gen=lambda r: [{"n": r.randint(1, 7)} for _ in range(6)],
    brute=_knight_brute,
    checks=[({"n": 1}, 10), ({"n": 2}, 20), ({"n": 3}, 46), ({"n": 4}, 104),
            ({"n": 3131}, 136006598)],
    source="new_p")


# ===========================================================================
# 7. Maximum Length of a Concatenated String with Unique Characters
# ===========================================================================
add("maximum-length-of-a-concatenated-string-with-unique-characters",
    "Maximum Length of a Concatenated String with Unique Characters", "medium",
    ["array", "string", "backtracking", "bit-manipulation"], "maxLength",
    [("arr", "string[]")], "int",
    """
Pick a subsequence of `arr` and concatenate the chosen strings. The concatenation is
valid only if it has **no repeated character**. **Return the maximum possible length**
of such a concatenation (the empty concatenation has length `0`).

**Examples**
```
arr = ["un","iq","ue"]              ->  4
arr = ["cha","r","act","ers"]       ->  6
arr = ["abcdefghijklmnopqrstuvwxyz"] ->  26
```

**Constraints:** `1 <= len(arr) <= 16`, `1 <= len(arr[i]) <= 26`, lowercase letters.
""",
    """def maxLength(arr):
    masks = [0]
    best = 0
    for s in arr:
        if len(set(s)) != len(s):
            continue
        m = 0
        ok = True
        for ch in s:
            b = 1 << (ord(ch) - 97)
            if m & b:
                ok = False
                break
            m |= b
        if not ok:
            continue
        for prev in masks[:]:
            if prev & m:
                continue
            comb = prev | m
            masks.append(comb)
            best = max(best, bin(comb).count("1"))
    return best
""",
    visible=[{"arr": ["un", "iq", "ue"]}, {"arr": ["cha", "r", "act", "ers"]},
             {"arr": ["abcdefghijklmnopqrstuvwxyz"]}],
    hidden=[{"arr": ["aa", "bb"]}, {"arr": ["a", "b", "c"]}, {"arr": ["aabc", "abc"]},
            {"arr": ["yy", "bkhwmpbiisbldzknpm"]}],
    gen=lambda r: [{"arr": [sstr(r, 1, 3, "abcd") for _ in range(r.randint(1, 7))]}
                   for _ in range(6)],
    brute=_maxlen_brute,
    checks=[({"arr": ["un", "iq", "ue"]}, 4),
            ({"arr": ["cha", "r", "act", "ers"]}, 6),
            ({"arr": ["abcdefghijklmnopqrstuvwxyz"]}, 26)],
    source="new_p")


# ===========================================================================
# 8. Maximum Number of Non-Overlapping Subarrays With Sum Equals Target
# ===========================================================================
add("maximum-number-of-non-overlapping-subarrays-with-sum-equals-target",
    "Maximum Number of Non-Overlapping Subarrays With Sum Equals Target", "medium",
    ["array", "hash-table", "greedy", "prefix-sum"], "maxNonOverlapping",
    [("nums", "int[]"), ("target", "int")], "int",
    """
**Return the maximum number of non-empty, non-overlapping subarrays of `nums` whose
sum each equals `target`.**

**Examples**
```
nums = [1,1,1,1,1], target = 2          ->  2
nums = [-1,3,5,1,4,2,-9], target = 6    ->  2
nums = [-2,6,6,3,5,4,1,2,8], target = 10 ->  3
nums = [0,0,0], target = 0              ->  3
```

**Constraints:** `1 <= len(nums) <= 10^5`, `-10^4 <= nums[i] <= 10^4`,
`0 <= target <= 10^6`.
""",
    """def maxNonOverlapping(nums, target):
    seen = {0}
    prefix = 0
    count = 0
    for x in nums:
        prefix += x
        if prefix - target in seen:
            count += 1
            seen = {0}
            prefix = 0
        else:
            seen.add(prefix)
    return count
""",
    visible=[{"nums": [1, 1, 1, 1, 1], "target": 2},
             {"nums": [-1, 3, 5, 1, 4, 2, -9], "target": 6},
             {"nums": [-2, 6, 6, 3, 5, 4, 1, 2, 8], "target": 10},
             {"nums": [0, 0, 0], "target": 0}],
    hidden=[{"nums": [1], "target": 1}, {"nums": [1], "target": 2},
            {"nums": [2, 2, 2, 2], "target": 4}, {"nums": [5, -5, 5, -5], "target": 0}],
    gen=lambda r: [{"nums": [r.randint(-3, 3) for _ in range(r.randint(1, 12))],
                    "target": r.randint(0, 5)} for _ in range(6)],
    brute=_maxnonover_brute,
    checks=[({"nums": [1, 1, 1, 1, 1], "target": 2}, 2),
            ({"nums": [-1, 3, 5, 1, 4, 2, -9], "target": 6}, 2),
            ({"nums": [-2, 6, 6, 3, 5, 4, 1, 2, 8], "target": 10}, 3),
            ({"nums": [0, 0, 0], "target": 0}, 3)],
    source="new_p")


# ===========================================================================
# 9. Number of Good Ways to Split a String
# ===========================================================================
add("number-of-good-ways-to-split-a-string",
    "Number of Good Ways to Split a String", "medium",
    ["string", "hash-table", "dynamic-programming", "bit-manipulation"], "numSplits",
    [("s", "string")], "int",
    """
Split `s` into two non-empty parts `p + q`. The split is *good* when `p` and `q`
contain the **same number of distinct letters**. **Return how many good splits
exist.**

**Examples**
```
s = "aacaba"  ->  2
s = "abcd"    ->  1
s = "aaaaa"   ->  4
```

**Constraints:** `1 <= len(s) <= 10^5`, lowercase letters.
""",
    """def numSplits(s):
    n = len(s)
    left = [0] * n
    seen = set()
    for i, ch in enumerate(s):
        seen.add(ch)
        left[i] = len(seen)
    right = [0] * n
    seen = set()
    for i in range(n - 1, -1, -1):
        seen.add(s[i])
        right[i] = len(seen)
    return sum(1 for i in range(n - 1) if left[i] == right[i + 1])
""",
    visible=[{"s": "aacaba"}, {"s": "abcd"}, {"s": "aaaaa"}],
    hidden=[{"s": "ab"}, {"s": "aa"}, {"s": "acbadbaada"}, {"s": "a"}],
    gen=lambda r: [{"s": sstr(r, 1, 14, "abc")} for _ in range(6)],
    brute=_numsplits_brute,
    checks=[({"s": "aacaba"}, 2), ({"s": "abcd"}, 1), ({"s": "aaaaa"}, 4),
            ({"s": "acbadbaada"}, 2)],
    source="new_p")


# ===========================================================================
# 10. Convert to Base -2
# ===========================================================================
add("convert-to-base-2", "Convert to Base -2", "medium",
    ["math"], "baseNeg2", [("N", "int")], "string",
    """
**Return the base `-2` (negative two) representation of the non-negative integer
`N`** as a string of `0`s and `1`s, with no leading zeros (except `"0"` itself). The
value of a string `b` is `sum(b[i] * (-2)^(len(b)-1-i))`.

**Examples**
```
N = 2  ->  "110"     ((-2)^2 + (-2)^1 = 4 - 2 = 2)
N = 3  ->  "111"     (4 - 2 + 1 = 3)
N = 4  ->  "100"
```

**Constraints:** `0 <= N <= 10^9`.
""",
    """def baseNeg2(N):
    if N == 0:
        return "0"
    digits = []
    while N != 0:
        r = N % (-2)
        N //= (-2)
        if r < 0:
            r += 2
            N += 1
        digits.append(str(r))
    return "".join(reversed(digits))
""",
    visible=[{"N": 2}, {"N": 3}, {"N": 4}],
    hidden=[{"N": 0}, {"N": 1}, {"N": 6}, {"N": 50}, {"N": 99}],
    gen=lambda r: [{"N": r.randint(0, 60)} for _ in range(8)],
    brute=_baseneg2_brute,
    checks=[({"N": 0}, "0"), ({"N": 1}, "1"), ({"N": 2}, "110"), ({"N": 3}, "111"),
            ({"N": 4}, "100"), ({"N": 6}, "11010")],
    source="new_p")


# ===========================================================================
# 11. Check If All 1's Are at Least Length K Places Away
# ===========================================================================
add("check-if-all-1s-are-at-least-length-k-places-away",
    "Check If All 1's Are at Least Length K Places Away", "easy",
    ["array"], "kLengthApart", [("nums", "int[]"), ("k", "int")], "bool",
    """
`nums` is an array of `0`s and `1`s. **Return `true` if every pair of consecutive
`1`s is separated by at least `k` `0`s** (i.e. their index difference is `> k`),
otherwise `false`.

**Examples**
```
nums = [1,0,0,0,1,0,0,1], k = 2  ->  true
nums = [1,0,0,1,0,1], k = 2      ->  false
nums = [1,1,1,1,1], k = 0        ->  true
```

**Constraints:** `1 <= len(nums) <= 10^5`, `0 <= k <= len(nums)`, `nums[i]` in
`{0,1}`.
""",
    """def kLengthApart(nums, k):
    prev = -1
    for i, x in enumerate(nums):
        if x == 1:
            if prev != -1 and i - prev - 1 < k:
                return False
            prev = i
    return True
""",
    visible=[{"nums": [1, 0, 0, 0, 1, 0, 0, 1], "k": 2},
             {"nums": [1, 0, 0, 1, 0, 1], "k": 2}, {"nums": [1, 1, 1, 1, 1], "k": 0}],
    hidden=[{"nums": [0, 1, 0, 1], "k": 1}, {"nums": [0, 0, 0], "k": 2},
            {"nums": [1], "k": 5}, {"nums": [1, 0, 1], "k": 2}],
    gen=lambda r: [{"nums": [r.randint(0, 1) for _ in range(r.randint(1, 12))],
                    "k": r.randint(0, 5)} for _ in range(6)],
    brute=_kapart_brute,
    checks=[({"nums": [1, 0, 0, 0, 1, 0, 0, 1], "k": 2}, True),
            ({"nums": [1, 0, 0, 1, 0, 1], "k": 2}, False),
            ({"nums": [1, 1, 1, 1, 1], "k": 0}, True),
            ({"nums": [0, 1, 0, 1], "k": 1}, True)],
    source="new_p")


# ===========================================================================
# 12. The k-th Lexicographical String of All Happy Strings of Length n
# ===========================================================================
add("the-k-th-lexicographical-string-of-all-happy-strings-of-length-n",
    "The k-th Lexicographical String of All Happy Strings of Length n", "medium",
    ["string", "backtracking"], "getHappyString",
    [("n", "int"), ("k", "int")], "string",
    """
A *happy string* uses only `'a'`, `'b'`, `'c'` and never repeats a letter in
adjacent positions. List all happy strings of length `n` in lexicographic order.
**Return the `k`-th string in that list (1-indexed)**, or `""` if fewer than `k`
exist.

**Examples**
```
n = 1, k = 3   ->  "c"
n = 1, k = 4   ->  ""
n = 3, k = 9   ->  "cab"
n = 10, k = 100 -> "abacbabacb"
```

**Constraints:** `1 <= n <= 10`, `1 <= k <= 100`.
""",
    """def getHappyString(n, k):
    total = 3 * (2 ** (n - 1))
    if k > total:
        return ""
    res = []
    per = total
    prev = ""
    for pos in range(n):
        if pos == 0:
            choices = ['a', 'b', 'c']
            per //= 3
        else:
            choices = [c for c in 'abc' if c != prev]
            per //= 2
        idx = (k - 1) // per
        ch = choices[idx]
        res.append(ch)
        k -= idx * per
        prev = ch
    return "".join(res)
""",
    visible=[{"n": 1, "k": 3}, {"n": 1, "k": 4}, {"n": 3, "k": 9},
             {"n": 10, "k": 100}],
    hidden=[{"n": 2, "k": 7}, {"n": 1, "k": 1}, {"n": 2, "k": 1}, {"n": 3, "k": 12}],
    gen=lambda r: [{"n": r.randint(1, 6), "k": r.randint(1, 30)} for _ in range(8)],
    brute=_happy_brute,
    checks=[({"n": 1, "k": 3}, "c"), ({"n": 1, "k": 4}, ""), ({"n": 3, "k": 9}, "cab"),
            ({"n": 10, "k": 100}, "abacbabacb"), ({"n": 2, "k": 7}, "")],
    source="new_p")


# ===========================================================================
# 13. Maximum Candies You Can Get from Boxes
# ===========================================================================
add("maximum-candies-you-can-get-from-boxes",
    "Maximum Candies You Can Get from Boxes", "hard",
    ["array", "breadth-first-search", "graph"], "maxCandies",
    [("status", "int[]"), ("candies", "int[]"), ("keys", "int[][]"),
     ("containedBoxes", "int[][]"), ("initialBoxes", "int[]")], "int",
    """
There are `n` boxes. Box `i` is open if `status[i] == 1` and holds `candies[i]`
candies, the keys in `keys[i]` (each opening one box), and the boxes listed in
`containedBoxes[i]`. You start holding the boxes in `initialBoxes`. You may take the
candies from any box you hold that is open (or that you have a key for), and use its
keys and contained boxes. **Return the maximum number of candies you can collect.**

**Examples**
```
status=[1,0,1,0], candies=[7,5,4,100], keys=[[],[],[1],[]],
containedBoxes=[[1,2],[3],[],[]], initialBoxes=[0]   ->  16
status=[1,0,0,0,0,0], candies=[1,1,1,1,1,1], keys=[[1,2,3,4,5],[],[],[],[],[]],
containedBoxes=[[1,2,3,4,5],[],[],[],[],[]], initialBoxes=[0]   ->  6
```

**Constraints:** `1 <= n <= 1000`, `status[i]` in `{0,1}`, `1 <= candies[i] <= 1000`,
all key / box indices valid.
""",
    """def maxCandies(status, candies, keys, containedBoxes, initialBoxes):
    from collections import deque
    n = len(status)
    have_box = [False] * n
    have_key = [False] * n
    opened = [False] * n
    queue = deque()

    def try_open(b):
        if have_box[b] and not opened[b] and (status[b] == 1 or have_key[b]):
            opened[b] = True
            queue.append(b)

    for b in initialBoxes:
        have_box[b] = True
    for b in initialBoxes:
        try_open(b)
    total = 0
    while queue:
        b = queue.popleft()
        total += candies[b]
        for k in keys[b]:
            if not have_key[k]:
                have_key[k] = True
                try_open(k)
        for nb in containedBoxes[b]:
            if not have_box[nb]:
                have_box[nb] = True
                try_open(nb)
    return total
""",
    visible=[{"status": [1, 0, 1, 0], "candies": [7, 5, 4, 100],
              "keys": [[], [], [1], []], "containedBoxes": [[1, 2], [3], [], []],
              "initialBoxes": [0]},
             {"status": [1, 0, 0, 0, 0, 0], "candies": [1, 1, 1, 1, 1, 1],
              "keys": [[1, 2, 3, 4, 5], [], [], [], [], []],
              "containedBoxes": [[1, 2, 3, 4, 5], [], [], [], [], []],
              "initialBoxes": [0]}],
    hidden=[{"status": [1, 1, 1], "candies": [100, 1, 100],
             "keys": [[], [0, 2], []], "containedBoxes": [[], [], []],
             "initialBoxes": [1]},
            {"status": [1], "candies": [100], "keys": [[]],
             "containedBoxes": [[]], "initialBoxes": []},
            {"status": [1, 1, 1], "candies": [2, 3, 2], "keys": [[], [], []],
             "containedBoxes": [[], [], []], "initialBoxes": [2, 1, 0]}],
    gen=lambda r: [(lambda n: {
        "status": [r.randint(0, 1) for _ in range(n)],
        "candies": [r.randint(1, 10) for _ in range(n)],
        "keys": [r.sample(range(n), r.randint(0, min(2, n))) for _ in range(n)],
        "containedBoxes": [r.sample(range(n), r.randint(0, min(2, n))) for _ in range(n)],
        "initialBoxes": r.sample(range(n), r.randint(1, n)),
    })(r.randint(1, 5)) for _ in range(6)],
    brute=_candies_brute,
    checks=[({"status": [1, 0, 1, 0], "candies": [7, 5, 4, 100],
              "keys": [[], [], [1], []], "containedBoxes": [[1, 2], [3], [], []],
              "initialBoxes": [0]}, 16),
            ({"status": [1, 1, 1], "candies": [100, 1, 100],
              "keys": [[], [0, 2], []], "containedBoxes": [[], [], []],
              "initialBoxes": [1]}, 1),
            ({"status": [1, 1, 1], "candies": [2, 3, 2], "keys": [[], [], []],
              "containedBoxes": [[], [], []], "initialBoxes": [2, 1, 0]}, 7)],
    source="new_p")


# ===========================================================================
# 14. Race Car
# ===========================================================================
add("race-car", "Race Car", "hard",
    ["dynamic-programming", "breadth-first-search"], "racecar", [("target", "int")], "int",
    """
Your car starts at position `0` with speed `+1` on an infinite number line and obeys
two instructions:
- `'A'`: `position += speed`, then `speed *= 2`;
- `'R'`: if `speed > 0` set `speed = -1`, else `speed = 1` (position unchanged).

**Return the length of the shortest instruction sequence that ends at position
`target`.**

**Examples**
```
target = 3  ->  2     ("AA": 0 -> 1 -> 3)
target = 6  ->  5     ("AAARA": 0 -> 1 -> 3 -> 7 -> 7 -> 6)
```

**Constraints:** `1 <= target <= 10000`.
""",
    """def racecar(target):
    from collections import deque
    q = deque([(0, 1)])
    seen = {(0, 1)}
    steps = 0
    while q:
        for _ in range(len(q)):
            pos, speed = q.popleft()
            if pos == target:
                return steps
            np_, ns = pos + speed, speed * 2
            if (np_, ns) not in seen and abs(np_) <= 2 * target:
                seen.add((np_, ns))
                q.append((np_, ns))
            ns2 = -1 if speed > 0 else 1
            if (pos, ns2) not in seen:
                seen.add((pos, ns2))
                q.append((pos, ns2))
        steps += 1
    return -1
""",
    visible=[{"target": 3}, {"target": 6}],
    hidden=[{"target": 1}, {"target": 2}, {"target": 4}, {"target": 5},
            {"target": 7}, {"target": 100}],
    gen=lambda r: [{"target": r.randint(1, 40)} for _ in range(6)],
    brute=_racecar_brute,
    checks=[({"target": 3}, 2), ({"target": 6}, 5), ({"target": 1}, 1),
            ({"target": 2}, 4)],
    source="new_p")


# ===========================================================================
# 15. Longest Continuous Subarray With Absolute Diff <= Limit
# ===========================================================================
add("longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit",
    "Longest Continuous Subarray With Absolute Diff Less Than or Equal to Limit",
    "medium", ["array", "sliding-window", "heap", "ordered-set"], "longestSubarray",
    [("nums", "int[]"), ("limit", "int")], "int",
    """
**Return the length of the longest non-empty contiguous subarray of `nums` in which
the absolute difference between any two elements is `<= limit`.**

**Examples**
```
nums = [8,2,4,7], limit = 4         ->  2
nums = [10,1,2,4,7,2], limit = 5    ->  4
nums = [4,2,2,2,4,4,2,2], limit = 0 ->  3
```

**Constraints:** `1 <= len(nums) <= 10^5`, `1 <= nums[i] <= 10^9`,
`0 <= limit <= 10^9`.
""",
    """def longestSubarray(nums, limit):
    from collections import deque
    maxd = deque()
    mind = deque()
    l = 0
    best = 0
    for r, x in enumerate(nums):
        while maxd and nums[maxd[-1]] <= x:
            maxd.pop()
        maxd.append(r)
        while mind and nums[mind[-1]] >= x:
            mind.pop()
        mind.append(r)
        while nums[maxd[0]] - nums[mind[0]] > limit:
            l += 1
            if maxd[0] < l:
                maxd.popleft()
            if mind[0] < l:
                mind.popleft()
        best = max(best, r - l + 1)
    return best
""",
    visible=[{"nums": [8, 2, 4, 7], "limit": 4},
             {"nums": [10, 1, 2, 4, 7, 2], "limit": 5},
             {"nums": [4, 2, 2, 2, 4, 4, 2, 2], "limit": 0}],
    hidden=[{"nums": [1], "limit": 0}, {"nums": [5, 5, 5], "limit": 0},
            {"nums": [1, 5, 6, 7, 8, 10, 6, 5, 6], "limit": 4},
            {"nums": [2, 1], "limit": 1}],
    gen=lambda r: [{"nums": [r.randint(1, 10) for _ in range(r.randint(1, 12))],
                    "limit": r.randint(0, 6)} for _ in range(6)],
    brute=_absdiff_brute,
    checks=[({"nums": [8, 2, 4, 7], "limit": 4}, 2),
            ({"nums": [10, 1, 2, 4, 7, 2], "limit": 5}, 4),
            ({"nums": [4, 2, 2, 2, 4, 4, 2, 2], "limit": 0}, 3)],
    source="new_p")


# ===========================================================================
# 16. Valid Parenthesis String
# ===========================================================================
add("valid-parenthesis-string", "Valid Parenthesis String", "medium",
    ["string", "dynamic-programming", "stack", "greedy"], "checkValidString",
    [("s", "string")], "bool",
    """
`s` contains only `'('`, `')'` and `'*'`. Each `'*'` may stand for `'('`, `')'`, or
an empty string. **Return `true` if `s` can be made into a valid parenthesis
string.**

**Examples**
```
s = "()"    ->  true
s = "(*)"   ->  true
s = "(*))"  ->  true
```

**Constraints:** `1 <= len(s) <= 100`.
""",
    """def checkValidString(s):
    lo = hi = 0
    for c in s:
        if c == '(':
            lo += 1
            hi += 1
        elif c == ')':
            lo -= 1
            hi -= 1
        else:
            lo -= 1
            hi += 1
        if hi < 0:
            return False
        if lo < 0:
            lo = 0
    return lo == 0
""",
    visible=[{"s": "()"}, {"s": "(*)"}, {"s": "(*))"}],
    hidden=[{"s": "*"}, {"s": ")("}, {"s": "(("}, {"s": "(*()"}, {"s": "**"}],
    gen=lambda r: [{"s": sstr(r, 1, 10, "()*")} for _ in range(6)],
    brute=_vps_brute,
    checks=[({"s": "()"}, True), ({"s": "(*)"}, True), ({"s": "(*))"}, True),
            ({"s": ")("}, False)],
    source="new_p")


# ===========================================================================
# 17. Zuma Game
# ===========================================================================
add("zuma-game", "Zuma Game", "hard",
    ["string", "breadth-first-search", "memoization"], "findMinStep",
    [("board", "string"), ("hand", "string")], "int",
    """
A row of colored balls (`board`) sits on the table; you hold more balls (`hand`),
each colored `R`/`Y`/`B`/`G`/`W`. Repeatedly insert one ball from your hand anywhere
in the row; whenever `>= 3` same-colored balls become adjacent they are removed (and
removals cascade). **Return the minimum number of balls you must insert to clear the
board**, or `-1` if it is impossible.

**Examples**
```
board = "WWRRBBWW", hand = "WRBRW"   ->  2
board = "G", hand = "GGGGG"          ->  2
board = "RBYYBBRRB", hand = "YRBGB"  ->  3
board = "WRRBBW", hand = "RB"        ->  -1
```

**Constraints:** `1 <= len(board) <= 16`, `1 <= len(hand) <= 5`, colors in
`RYBGW`.
""",
    """def findMinStep(board, hand):
    from collections import deque

    def remove(s):
        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]:
                j += 1
            if j - i >= 3:
                s = s[:i] + s[j:]
                i = 0
            else:
                i = j
        return s

    start = (board, "".join(sorted(hand)))
    seen = {start}
    q = deque([(start[0], start[1], 0)])
    while q:
        b, h, steps = q.popleft()
        if b == "":
            return steps
        for i in range(len(b) + 1):
            for j in range(len(h)):
                if j > 0 and h[j] == h[j - 1]:
                    continue
                nb = remove(b[:i] + h[j] + b[i:])
                nh = h[:j] + h[j + 1:]
                state = (nb, nh)
                if state not in seen:
                    seen.add(state)
                    q.append((nb, nh, steps + 1))
    return -1
""",
    visible=[{"board": "WWRRBBWW", "hand": "WRBRW"}, {"board": "G", "hand": "GGGGG"},
             {"board": "RBYYBBRRB", "hand": "YRBGB"}],
    hidden=[{"board": "WRRBBW", "hand": "RB"}, {"board": "RRBBRR", "hand": "B"},
            {"board": "RYBG", "hand": "RY"}, {"board": "R", "hand": "RR"}],
    gen=lambda r: [{"board": _zuma_board(r),
                    "hand": "".join(r.choice("RYBGW") for _ in range(r.randint(1, 3)))}
                   for _ in range(5)],
    checks=[({"board": "WWRRBBWW", "hand": "WRBRW"}, 2),
            ({"board": "G", "hand": "GGGGG"}, 2),
            ({"board": "RBYYBBRRB", "hand": "YRBGB"}, 3),
            ({"board": "WRRBBW", "hand": "RB"}, -1)],
    source="new_p")


# ===========================================================================
# 18. Bulb Switcher III
# ===========================================================================
add("bulb-switcher-iii", "Bulb Switcher III", "medium",
    ["array", "hash-table"], "numTimesAllBlue", [("light", "int[]")], "int",
    """
Bulbs `1..n` start off. At moment `k` (for `k = 0..n-1`) you switch on bulb
`light[k]`. A lit bulb turns **blue** only once every bulb to its left is also on.
**Return the number of moments at which all currently-on bulbs are blue**, i.e. the
on-bulbs are exactly `1..k+1`.

**Examples**
```
light = [2,1,3,5,4]  ->  3
light = [3,2,4,1,5]  ->  2
light = [4,1,2,3]    ->  1
```

**Constraints:** `1 <= n <= 5*10^4`, `light` is a permutation of `1..n`.
""",
    """def numTimesAllBlue(light):
    rightmost = 0
    ans = 0
    for i, b in enumerate(light):
        rightmost = max(rightmost, b)
        if rightmost == i + 1:
            ans += 1
    return ans
""",
    visible=[{"light": [2, 1, 3, 5, 4]}, {"light": [3, 2, 4, 1, 5]},
             {"light": [4, 1, 2, 3]}],
    hidden=[{"light": [1]}, {"light": [1, 2, 3, 4, 5, 6]},
            {"light": [2, 1, 4, 3, 6, 5]}, {"light": [6, 5, 4, 3, 2, 1]}],
    gen=lambda r: [(lambda n: {"light": r.sample(range(1, n + 1), n)})
                   (r.randint(1, 10)) for _ in range(6)],
    brute=_bulb_brute,
    checks=[({"light": [2, 1, 3, 5, 4]}, 3), ({"light": [3, 2, 4, 1, 5]}, 2),
            ({"light": [4, 1, 2, 3]}, 1), ({"light": [1, 2, 3, 4, 5, 6]}, 6)],
    source="new_p")
