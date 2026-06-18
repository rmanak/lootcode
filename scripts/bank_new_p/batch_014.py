"""Batch 014 of the new_p.txt import (19 problems).

One entry was dropped as a duplicate under a different slug (see `_skips.py`):
`divide-array-in-sets-of-k-consecutive-numbers` (== `hand-of-straights`).

`cat-and-mouse` ships a retrograde-BFS canonical cross-checked against an
independent depth-limited minimax brute (cap = 2*n^2 plies, the number of game
positions, which provably bounds any forced win).
"""
from scripts.build_bank import add, ilist, sstr  # noqa: F401

MOD = 10 ** 9 + 7


# --------------------------- brute / reference helpers ---------------------
def _power_brute(lo, hi, k):
    def power(x):
        s = 0
        while x != 1:
            x = x // 2 if x % 2 == 0 else 3 * x + 1
            s += 1
        return s
    return sorted(range(lo, hi + 1), key=lambda x: (power(x), x))[k - 1]


def _dice_brute(d, f, target):
    from itertools import product
    return sum(1 for combo in product(range(1, f + 1), repeat=d)
               if sum(combo) == target) % MOD


def _break_brute(palindrome):
    n = len(palindrome)
    best = None
    for i in range(n):
        for ch in "abcdefghijklmnopqrstuvwxyz":
            if ch == palindrome[i]:
                continue
            cand = palindrome[:i] + ch + palindrome[i + 1:]
            if cand != cand[::-1]:
                if best is None or cand < best:
                    best = cand
    return best if best is not None else ""


def _winner_brute(arr, k):
    from collections import deque
    mx = max(arr)
    q = deque(arr)
    cur = q.popleft()
    win = 0
    while True:
        if cur == mx:
            return cur
        nxt = q.popleft()
        if cur > nxt:
            win += 1
            q.append(nxt)
        else:
            q.append(cur)
            cur = nxt
            win = 1
        if win == k:
            return cur


def _minswap_brute(A, B):
    n = len(A)
    best = float('inf')
    for mask in range(1 << n):
        a, b, cnt = A[:], B[:], 0
        for i in range(n):
            if mask >> i & 1:
                a[i], b[i] = b[i], a[i]
                cnt += 1
        if all(a[i] < a[i + 1] for i in range(n - 1)) and \
           all(b[i] < b[i + 1] for i in range(n - 1)):
            best = min(best, cnt)
    return best


def _catmouse_brute(graph):
    n = len(graph)
    DRAW, MOUSE, CAT = 0, 1, 2
    from functools import lru_cache
    cap = 2 * n * n

    @lru_cache(None)
    def solve(m, c, turn, t):
        if c == m:
            return CAT
        if m == 0:
            return MOUSE
        if t == cap:
            return DRAW
        if turn == 0:
            outs = [solve(nb, c, 1, t + 1) for nb in graph[m]]
            if not outs:           # mouse stuck -> unresolved (draw), matching retrograde
                return DRAW
            if MOUSE in outs:
                return MOUSE
            return DRAW if DRAW in outs else CAT
        outs = [solve(m, nb, 0, t + 1) for nb in graph[c] if nb != 0]
        if not outs:               # cat stuck -> unresolved (draw), matching retrograde
            return DRAW
        if CAT in outs:
            return CAT
        return DRAW if DRAW in outs else MOUSE

    return solve(1, 2, 0, 0)


def _intrep_brute(n):
    from collections import deque
    seen = {n}
    q = deque([(n, 0)])
    while q:
        v, d = q.popleft()
        if v == 1:
            return d
        nxts = [v // 2] if v % 2 == 0 else [v - 1, v + 1]
        for nv in nxts:
            if nv >= 1 and nv not in seen:
                seen.add(nv)
                q.append((nv, d + 1))
    return -1


def _bulb_brute(n):
    bulbs = [False] * (n + 1)
    for r in range(1, n + 1):
        for i in range(r, n + 1, r):
            bulbs[i] = not bulbs[i]
    return sum(bulbs[1:])


def _vowelseven_brute(s):
    vowels = "aeiou"
    n = len(s)
    best = 0
    for i in range(n):
        cnt = {v: 0 for v in vowels}
        for j in range(i, n):
            if s[j] in cnt:
                cnt[s[j]] += 1
            if all(v % 2 == 0 for v in cnt.values()):
                best = max(best, j - i + 1)
    return best


def _lastsub_brute(s):
    return max(s[i:] for i in range(len(s)))


def _arith_brute(arr, difference):
    n = len(arr)
    if n == 0:
        return 0
    dp = [1] * n
    best = 1
    for i in range(n):
        for j in range(i):
            if arr[i] - arr[j] == difference:
                dp[i] = max(dp[i], dp[j] + 1)
        best = max(best, dp[i])
    return best


def _overlap_brute(img1, img2):
    n = len(img1)
    best = 0
    for dx in range(-n + 1, n):
        for dy in range(-n + 1, n):
            c = 0
            for i in range(n):
                for j in range(n):
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < n and 0 <= nj < n and img1[ni][nj] == 1 and img2[i][j] == 1:
                        c += 1
            best = max(best, c)
    return best


def _divide_brute(dividend, divisor):
    INT_MAX, INT_MIN = 2 ** 31 - 1, -2 ** 31
    q = abs(dividend) // abs(divisor)
    if (dividend < 0) != (divisor < 0):
        q = -q
    return max(INT_MIN, min(INT_MAX, q))


def _reorder_brute(N):
    from itertools import permutations
    for p in set(permutations(str(N))):
        if p[0] == '0':
            continue
        v = int("".join(p))
        if v > 0 and (v & (v - 1)) == 0:
            return True
    return False


def _orders_brute(n):
    from itertools import permutations
    items = []
    for i in range(n):
        items += [('P', i), ('D', i)]
    cnt = 0
    for perm in set(permutations(items)):
        idx = {x: k for k, x in enumerate(perm)}
        if all(idx[('D', i)] > idx[('P', i)] for i in range(n)):
            cnt += 1
    return cnt % MOD


def _hint_brute(secret, guess):
    bulls = 0
    s_rem, g_rem = [0] * 10, [0] * 10
    for a, b in zip(secret, guess):
        if a == b:
            bulls += 1
        else:
            s_rem[int(a)] += 1
            g_rem[int(b)] += 1
    cows = sum(min(s_rem[d], g_rem[d]) for d in range(10))
    return f"{bulls}A{cows}B"


def _distsub_brute(S):
    subs = set()
    n = len(S)
    for mask in range(1, 1 << n):
        subs.add("".join(S[i] for i in range(n) if mask >> i & 1))
    return len(subs) % MOD


def _submin_brute(A):
    n = len(A)
    res = 0
    for i in range(n):
        m = A[i]
        for j in range(i, n):
            m = min(m, A[j])
            res += m
    return res % MOD


# --------------------------- gen helpers -----------------------------------
def _break_gen(r):
    half = sstr(r, 1, 4, "ab")
    mid = r.choice(["", r.choice("ab")])
    return {"palindrome": half + mid + half[::-1]}


def _minswap_gen(r):
    n = r.randint(1, 8)
    A = sorted(r.sample(range(0, 40), n))
    B = sorted(r.sample(range(0, 40), n))
    for i in range(n):
        if r.random() < 0.5:
            A[i], B[i] = B[i], A[i]
    return {"A": A, "B": B}


def _catmouse_gen(r):
    n = r.randint(3, 6)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if r.random() < 0.45:
                adj[i].add(j)
                adj[j].add(i)
    if not adj[1]:
        j = r.choice([x for x in range(n) if x != 1])
        adj[1].add(j)
        adj[j].add(1)
    if not any(x != 0 for x in adj[2]):
        j = r.choice([x for x in range(1, n) if x != 2])
        adj[2].add(j)
        adj[j].add(2)
    return {"graph": [sorted(adj[i]) for i in range(n)]}


def _overlap_gen(r):
    n = r.randint(1, 5)
    return {"img1": [[r.randint(0, 1) for _ in range(n)] for _ in range(n)],
            "img2": [[r.randint(0, 1) for _ in range(n)] for _ in range(n)]}


def _hint_gen(r):
    n = r.randint(1, 6)
    return {"secret": "".join(r.choice("0123") for _ in range(n)),
            "guess": "".join(r.choice("0123") for _ in range(n))}


# ===========================================================================
# 1. Sort Integers by the Power Value
# ===========================================================================
add("sort-integers-by-the-power-value", "Sort Integers by the Power Value", "medium",
    ["array", "math", "sorting", "memoization"], "getKth",
    [("lo", "int"), ("hi", "int"), ("k", "int")], "int",
    """
The *power* of `x` is the number of Collatz steps to reach `1` (`x -> x/2` if even,
`x -> 3x+1` if odd). Sort the integers in `[lo, hi]` by power ascending, breaking ties
by the integer value ascending. **Return the `k`-th integer (1-indexed) in that order.**

**Examples**
```
lo = 12, hi = 15, k = 2  ->  13
lo = 7, hi = 11, k = 4   ->  7
lo = 1, hi = 1000, k = 777  ->  570
```

**Constraints:** `1 <= lo <= hi <= 1000`, `1 <= k <= hi - lo + 1`.
""",
    """def getKth(lo, hi, k):
    memo = {1: 0}

    def power(x):
        path = []
        cur = x
        while cur not in memo:
            path.append(cur)
            cur = cur // 2 if cur % 2 == 0 else 3 * cur + 1
        base = memo[cur]
        for i, v in enumerate(reversed(path)):
            memo[v] = base + i + 1
        return memo[x]

    return sorted(range(lo, hi + 1), key=lambda x: (power(x), x))[k - 1]
""",
    visible=[{"lo": 12, "hi": 15, "k": 2}, {"lo": 7, "hi": 11, "k": 4},
             {"lo": 1, "hi": 1000, "k": 777}],
    hidden=[{"lo": 1, "hi": 1, "k": 1}, {"lo": 10, "hi": 20, "k": 5},
            {"lo": 1, "hi": 10, "k": 10}, {"lo": 100, "hi": 200, "k": 50}],
    gen=lambda r: [(lambda lo, hi: {"lo": lo, "hi": hi, "k": r.randint(1, hi - lo + 1)})
                   (*sorted([r.randint(1, 100), r.randint(1, 100)])) for _ in range(8)],
    brute=_power_brute,
    checks=[({"lo": 12, "hi": 15, "k": 2}, 13), ({"lo": 1, "hi": 1, "k": 1}, 1),
            ({"lo": 7, "hi": 11, "k": 4}, 7), ({"lo": 10, "hi": 20, "k": 5}, 13),
            ({"lo": 1, "hi": 1000, "k": 777}, 570)],
    source="new_p")


# ===========================================================================
# 2. Number of Dice Rolls with Target Sum
# ===========================================================================
add("number-of-dice-rolls-with-target-sum", "Number of Dice Rolls with Target Sum",
    "medium", ["dynamic-programming"], "numRollsToTarget",
    [("d", "int"), ("f", "int"), ("target", "int")], "int",
    """
You roll `d` dice, each with faces `1..f`. **Return the number of ways the faces can
sum to `target`**, modulo `10^9 + 7`.

**Examples**
```
d = 1, f = 6, target = 3   ->  1
d = 2, f = 6, target = 7   ->  6
d = 2, f = 5, target = 10  ->  1
d = 1, f = 2, target = 3   ->  0
```

**Constraints:** `1 <= d, f <= 30`, `1 <= target <= 1000`.
""",
    """def numRollsToTarget(d, f, target):
    MOD = 10 ** 9 + 7
    dp = [0] * (target + 1)
    dp[0] = 1
    for _ in range(d):
        ndp = [0] * (target + 1)
        for s in range(target + 1):
            if dp[s]:
                for face in range(1, f + 1):
                    if s + face <= target:
                        ndp[s + face] = (ndp[s + face] + dp[s]) % MOD
        dp = ndp
    return dp[target]
""",
    visible=[{"d": 1, "f": 6, "target": 3}, {"d": 2, "f": 6, "target": 7},
             {"d": 2, "f": 5, "target": 10}, {"d": 1, "f": 2, "target": 3}],
    hidden=[{"d": 1, "f": 1, "target": 1}, {"d": 3, "f": 4, "target": 6},
            {"d": 2, "f": 3, "target": 1}, {"d": 4, "f": 6, "target": 24}],
    gen=lambda r: [{"d": r.randint(1, 4), "f": r.randint(1, 6), "target": r.randint(1, 15)}
                   for _ in range(8)],
    brute=_dice_brute,
    checks=[({"d": 1, "f": 6, "target": 3}, 1), ({"d": 2, "f": 6, "target": 7}, 6),
            ({"d": 2, "f": 5, "target": 10}, 1), ({"d": 1, "f": 2, "target": 3}, 0),
            ({"d": 30, "f": 30, "target": 500}, 222616187)],
    source="new_p")


# ===========================================================================
# 3. Break a Palindrome
# ===========================================================================
add("break-a-palindrome", "Break a Palindrome", "medium",
    ["string", "greedy"], "breakPalindrome", [("palindrome", "string")], "string",
    """
Replace **exactly one** character of the palindromic string `palindrome` with any
lowercase letter so the result is **not a palindrome** and is **lexicographically
smallest**. **Return the result, or `""` if it cannot be done.**

**Examples**
```
palindrome = "abccba"  ->  "aaccba"
palindrome = "a"       ->  ""
```

**Constraints:** `1 <= len(palindrome) <= 1000`, lowercase letters.
""",
    """def breakPalindrome(palindrome):
    n = len(palindrome)
    if n == 1:
        return ""
    s = list(palindrome)
    for i in range(n // 2):
        if s[i] != 'a':
            s[i] = 'a'
            return "".join(s)
    s[-1] = 'b'
    return "".join(s)
""",
    visible=[{"palindrome": "abccba"}, {"palindrome": "a"}],
    hidden=[{"palindrome": "aa"}, {"palindrome": "aba"}, {"palindrome": "aaa"},
            {"palindrome": "bab"}, {"palindrome": "aba"}],
    gen=lambda r: [_break_gen(r) for _ in range(8)],
    brute=_break_brute,
    checks=[({"palindrome": "abccba"}, "aaccba"), ({"palindrome": "a"}, ""),
            ({"palindrome": "aa"}, "ab"), ({"palindrome": "aba"}, "abb"),
            ({"palindrome": "aaa"}, "aab")],
    source="new_p")


# ===========================================================================
# 4. Find the Winner of an Array Game
# ===========================================================================
add("find-the-winner-of-an-array-game", "Find the Winner of an Array Game", "medium",
    ["array", "simulation"], "getWinner", [("arr", "int[]"), ("k", "int")], "int",
    """
Play a game between `arr[0]` and `arr[1]`: the larger stays at the front, the smaller
goes to the back. **Return the integer that first wins `k` consecutive rounds.**

**Examples**
```
arr = [2,1,3,5,4,6,7], k = 2  ->  5
arr = [3,2,1], k = 10         ->  3
arr = [1,9,8,2,3,7,6,4,5], k = 7  ->  9
```

**Constraints:** `2 <= len(arr) <= 10^5`, distinct integers, `1 <= k <= 10^9`.
""",
    """def getWinner(arr, k):
    cur = arr[0]
    win = 0
    for i in range(1, len(arr)):
        if arr[i] > cur:
            cur = arr[i]
            win = 1
        else:
            win += 1
        if win == k:
            return cur
    return cur
""",
    visible=[{"arr": [2, 1, 3, 5, 4, 6, 7], "k": 2}, {"arr": [3, 2, 1], "k": 10},
             {"arr": [1, 9, 8, 2, 3, 7, 6, 4, 5], "k": 7}],
    hidden=[{"arr": [1, 11, 22, 33, 44, 55, 66, 77, 88, 99], "k": 1000000000},
            {"arr": [2, 1], "k": 1}, {"arr": [1, 2], "k": 1}, {"arr": [5, 4, 3, 2, 1], "k": 1}],
    gen=lambda r: [(lambda a: {"arr": a, "k": r.randint(1, 6)})
                   (r.sample(range(1, 30), r.randint(2, 8))) for _ in range(8)],
    brute=_winner_brute,
    checks=[({"arr": [2, 1, 3, 5, 4, 6, 7], "k": 2}, 5), ({"arr": [3, 2, 1], "k": 10}, 3),
            ({"arr": [1, 9, 8, 2, 3, 7, 6, 4, 5], "k": 7}, 9),
            ({"arr": [1, 11, 22, 33, 44, 55, 66, 77, 88, 99], "k": 1000000000}, 99)],
    source="new_p")


# ===========================================================================
# 5. Minimum Swaps to Make Sequences Increasing
# ===========================================================================
add("minimum-swaps-to-make-sequences-increasing",
    "Minimum Swaps to Make Sequences Increasing", "hard",
    ["array", "dynamic-programming"], "minSwap", [("A", "int[]"), ("B", "int[]")], "int",
    """
You may swap `A[i]` with `B[i]` at any index `i`. **Return the minimum number of swaps
so that both `A` and `B` become strictly increasing.** The input is always solvable.

**Example**
```
A = [1,3,5,4], B = [1,2,3,7]  ->  1   (swap index 3)
```

**Constraints:** `1 <= len(A) == len(B) <= 1000`, `0 <= A[i], B[i] <= 2000`.
""",
    """def minSwap(A, B):
    n = len(A)
    INF = float('inf')
    keep = [INF] * n
    swap = [INF] * n
    keep[0] = 0
    swap[0] = 1
    for i in range(1, n):
        if A[i] > A[i - 1] and B[i] > B[i - 1]:
            keep[i] = keep[i - 1]
            swap[i] = swap[i - 1] + 1
        if A[i] > B[i - 1] and B[i] > A[i - 1]:
            keep[i] = min(keep[i], swap[i - 1])
            swap[i] = min(swap[i], keep[i - 1] + 1)
    return min(keep[-1], swap[-1])
""",
    visible=[{"A": [1, 3, 5, 4], "B": [1, 2, 3, 7]}],
    hidden=[{"A": [1, 2, 3], "B": [1, 2, 3]}, {"A": [3, 5], "B": [1, 2]},
            {"A": [0, 3, 5, 8, 9], "B": [2, 1, 4, 6, 9]}, {"A": [1], "B": [1]}],
    gen=lambda r: [_minswap_gen(r) for _ in range(8)],
    brute=_minswap_brute,
    checks=[({"A": [1, 3, 5, 4], "B": [1, 2, 3, 7]}, 1),
            ({"A": [1, 2, 3], "B": [1, 2, 3]}, 0), ({"A": [3, 5], "B": [1, 2]}, 0)],
    source="new_p")


# ===========================================================================
# 6. Cat and Mouse
# ===========================================================================
add("cat-and-mouse", "Cat and Mouse", "hard",
    ["graph", "breadth-first-search", "game-theory", "memoization"], "catMouseGame",
    [("graph", "int[][]")], "int",
    """
On an undirected graph (`graph[a]` lists the neighbours of `a`), Mouse starts at node
`1` and moves first, Cat starts at node `2`, and the Hole is node `0`. Players
alternate, each moving along one edge; the Cat may never move to the Hole. The Cat
wins if it ever shares Mouse's node; the Mouse wins by reaching the Hole; a repeated
position (same nodes and same player to move) is a draw. With optimal play, **return
`1` if Mouse wins, `2` if Cat wins, `0` for a draw.**

**Example**
```
graph = [[2,5],[3],[0,4,5],[1,4,5],[2,3],[0,2,3]]  ->  0
```

**Constraints:** `3 <= len(graph) <= 50`, `graph[1]` non-empty, `graph[2]` has a
non-zero neighbour.
""",
    """def catMouseGame(graph):
    n = len(graph)
    DRAW, MOUSE, CAT = 0, 1, 2
    color = [[[DRAW] * 2 for _ in range(n)] for _ in range(n)]
    degree = [[[0] * 2 for _ in range(n)] for _ in range(n)]
    for m in range(n):
        for c in range(n):
            degree[m][c][0] = len(graph[m])
            degree[m][c][1] = len(graph[c])
            for x in graph[c]:
                if x == 0:
                    degree[m][c][1] -= 1

    from collections import deque
    q = deque()
    for c in range(n):
        for t in range(2):
            color[0][c][t] = MOUSE
            q.append((0, c, t, MOUSE))
            if c > 0:
                color[c][c][t] = CAT
                q.append((c, c, t, CAT))

    def parents(m, c, t):
        if t == 0:
            for x in graph[c]:
                if x != 0:
                    yield (m, x, 1)
        else:
            for x in graph[m]:
                yield (x, c, 0)

    while q:
        m, c, t, result = q.popleft()
        for pm, pc, pt in parents(m, c, t):
            if color[pm][pc][pt] != DRAW:
                continue
            mover = MOUSE if pt == 0 else CAT
            if result == mover:
                color[pm][pc][pt] = result
                q.append((pm, pc, pt, result))
            else:
                degree[pm][pc][pt] -= 1
                if degree[pm][pc][pt] == 0:
                    color[pm][pc][pt] = result
                    q.append((pm, pc, pt, result))
    return color[1][2][0]
""",
    visible=[{"graph": [[2, 5], [3], [0, 4, 5], [1, 4, 5], [2, 3], [0, 2, 3]]}],
    hidden=[{"graph": [[1, 2], [0, 2], [0, 1]]}, {"graph": [[1, 2], [0, 3], [0, 3], [1, 2]]},
            {"graph": [[1, 3], [0, 2], [3], [0, 1, 2]]},
            {"graph": [[2, 4], [3, 4], [0, 4], [1, 4], [0, 1, 2, 3]]}],
    gen=lambda r: [_catmouse_gen(r) for _ in range(6)],
    brute=_catmouse_brute,
    checks=[({"graph": [[2, 5], [3], [0, 4, 5], [1, 4, 5], [2, 3], [0, 2, 3]]}, 0),
            ({"graph": [[1, 2], [0, 2], [0, 1]]}, 1)],
    source="new_p")


# ===========================================================================
# 7. Integer Replacement
# ===========================================================================
add("integer-replacement", "Integer Replacement", "medium",
    ["math", "bit-manipulation", "greedy"], "integerReplacement", [("n", "int")], "int",
    """
Starting from `n`: if `n` is even replace it with `n/2`, else replace it with `n+1`
or `n-1`. **Return the minimum number of replacements to reach `1`.**

**Examples**
```
n = 8  ->  3    (8 -> 4 -> 2 -> 1)
n = 7  ->  4    (7 -> 8 -> 4 -> 2 -> 1)
```

**Constraints:** `1 <= n <= 2^31 - 1`.
""",
    """def integerReplacement(n):
    count = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        elif n == 3 or n % 4 == 1:
            n -= 1
        else:
            n += 1
        count += 1
    return count
""",
    visible=[{"n": 8}, {"n": 7}],
    hidden=[{"n": 1}, {"n": 2}, {"n": 10}, {"n": 65535}, {"n": 3}],
    gen=lambda r: [{"n": r.randint(1, 500)} for _ in range(8)],
    brute=_intrep_brute,
    checks=[({"n": 8}, 3), ({"n": 7}, 4), ({"n": 1}, 0), ({"n": 2}, 1), ({"n": 10}, 4)],
    source="new_p")


# ===========================================================================
# 8. Bulb Switcher
# ===========================================================================
add("bulb-switcher", "Bulb Switcher", "medium",
    ["math"], "bulbSwitch", [("n", "int")], "int",
    """
There are `n` bulbs, initially off. On round `i` you toggle every `i`-th bulb (rounds
`1` through `n`). **Return how many bulbs are on after `n` rounds.**

**Example**
```
n = 3  ->  1
```

**Constraints:** `0 <= n <= 10^9`.
""",
    """def bulbSwitch(n):
    import math
    return math.isqrt(n)
""",
    visible=[{"n": 3}],
    hidden=[{"n": 0}, {"n": 1}, {"n": 10}, {"n": 99}, {"n": 100}],
    gen=lambda r: [{"n": r.randint(0, 150)} for _ in range(8)],
    brute=_bulb_brute,
    checks=[({"n": 3}, 1), ({"n": 0}, 0), ({"n": 1}, 1), ({"n": 10}, 3), ({"n": 100}, 10)],
    source="new_p")


# ===========================================================================
# 9. Find the Longest Substring Containing Vowels in Even Counts
# ===========================================================================
add("find-the-longest-substring-containing-vowels-in-even-counts",
    "Find the Longest Substring Containing Vowels in Even Counts", "medium",
    ["string", "hash-table", "bitmask", "prefix-sum"], "findTheLongestSubstring",
    [("s", "string")], "int",
    """
**Return the length of the longest substring of `s` in which each vowel
(`a, e, i, o, u`) appears an even number of times** (zero counts as even).

**Examples**
```
s = "eleetminicoworoep"  ->  13
s = "leetcodeisgreat"    ->  5
s = "bcbcbc"             ->  6
```

**Constraints:** `1 <= len(s) <= 5*10^5`, lowercase letters.
""",
    """def findTheLongestSubstring(s):
    vowels = {'a': 0, 'e': 1, 'i': 2, 'o': 3, 'u': 4}
    first = {0: -1}
    mask = 0
    best = 0
    for i, c in enumerate(s):
        if c in vowels:
            mask ^= 1 << vowels[c]
        if mask in first:
            best = max(best, i - first[mask])
        else:
            first[mask] = i
    return best
""",
    visible=[{"s": "eleetminicoworoep"}, {"s": "leetcodeisgreat"}, {"s": "bcbcbc"}],
    hidden=[{"s": ""}, {"s": "a"}, {"s": "aa"}, {"s": "abcde"}, {"s": "aeiouaeiou"}],
    gen=lambda r: [{"s": sstr(r, 0, 15, "abcdeiou")} for _ in range(8)],
    brute=_vowelseven_brute,
    checks=[({"s": "eleetminicoworoep"}, 13), ({"s": "leetcodeisgreat"}, 5),
            ({"s": "bcbcbc"}, 6), ({"s": "aa"}, 2)],
    source="new_p")


# ===========================================================================
# 10. Last Substring in Lexicographical Order
# ===========================================================================
add("last-substring-in-lexicographical-order", "Last Substring in Lexicographical Order",
    "hard", ["string", "two-pointers"], "lastSubstring", [("s", "string")], "string",
    """
**Return the substring of `s` that is largest in lexicographical order.** (It is
always one of the suffixes of `s`.)

**Examples**
```
s = "abab"      ->  "bab"
s = "leetcode"  ->  "tcode"
```

**Constraints:** `1 <= len(s) <= 4*10^5`, lowercase letters.
""",
    """def lastSubstring(s):
    i, j, k = 0, 1, 0
    n = len(s)
    while j + k < n:
        if s[i + k] == s[j + k]:
            k += 1
        elif s[i + k] < s[j + k]:
            i = max(i + k + 1, j)
            j = i + 1
            k = 0
        else:
            j = j + k + 1
            k = 0
    return s[i:]
""",
    visible=[{"s": "abab"}, {"s": "leetcode"}],
    hidden=[{"s": "a"}, {"s": "zazb"}, {"s": "bb"}, {"s": "cacacb"}, {"s": "aaaaa"}],
    gen=lambda r: [{"s": sstr(r, 1, 15, "abc")} for _ in range(8)],
    brute=_lastsub_brute,
    checks=[({"s": "abab"}, "bab"), ({"s": "leetcode"}, "tcode"), ({"s": "a"}, "a"),
            ({"s": "zazb"}, "zb")],
    source="new_p")


# ===========================================================================
# 11. Longest Arithmetic Subsequence of Given Difference
# ===========================================================================
add("longest-arithmetic-subsequence-of-given-difference",
    "Longest Arithmetic Subsequence of Given Difference", "medium",
    ["array", "hash-table", "dynamic-programming"], "longestSubsequence",
    [("arr", "int[]"), ("difference", "int")], "int",
    """
**Return the length of the longest subsequence of `arr` that forms an arithmetic
sequence with common difference exactly `difference`** (consecutive chosen elements
differ by `difference`).

**Examples**
```
arr = [1,2,3,4], difference = 1            ->  4
arr = [1,3,5,7], difference = 1            ->  1
arr = [1,5,7,8,5,3,4,2,1], difference = -2 ->  4
```

**Constraints:** `1 <= len(arr) <= 10^5`, `-10^4 <= arr[i], difference <= 10^4`.
""",
    """def longestSubsequence(arr, difference):
    dp = {}
    best = 0
    for x in arr:
        dp[x] = dp.get(x - difference, 0) + 1
        best = max(best, dp[x])
    return best
""",
    visible=[{"arr": [1, 2, 3, 4], "difference": 1}, {"arr": [1, 3, 5, 7], "difference": 1},
             {"arr": [1, 5, 7, 8, 5, 3, 4, 2, 1], "difference": -2}],
    hidden=[{"arr": [1], "difference": 5}, {"arr": [3, 0, 0, 4], "difference": 0},
            {"arr": [2, 2, 2], "difference": 0}, {"arr": [-1, -2, -3, -4], "difference": -1}],
    gen=lambda r: [{"arr": [r.randint(-8, 8) for _ in range(r.randint(1, 12))],
                    "difference": r.randint(-3, 3)} for _ in range(8)],
    brute=_arith_brute,
    checks=[({"arr": [1, 2, 3, 4], "difference": 1}, 4),
            ({"arr": [1, 3, 5, 7], "difference": 1}, 1),
            ({"arr": [1, 5, 7, 8, 5, 3, 4, 2, 1], "difference": -2}, 4),
            ({"arr": [2, 2, 2], "difference": 0}, 3)],
    source="new_p")


# ===========================================================================
# 12. Image Overlap
# ===========================================================================
add("image-overlap", "Image Overlap", "medium",
    ["array", "matrix"], "largestOverlap",
    [("img1", "int[][]"), ("img2", "int[][]")], "int",
    """
`img1` and `img2` are `n x n` binary matrices. You may translate `img1` (slide it any
number of cells up/down/left/right, no rotation) and place it over `img2`. **Return
the largest number of positions where both have a `1` after some translation.**

**Examples**
```
img1 = [[1,1,0],[0,1,0],[0,1,0]], img2 = [[0,0,0],[0,1,1],[0,0,1]]  ->  3
img1 = [[1]], img2 = [[1]]  ->  1
img1 = [[0]], img2 = [[0]]  ->  0
```

**Constraints:** `1 <= n <= 30`, entries are `0` or `1`.
""",
    """def largestOverlap(img1, img2):
    from collections import Counter
    n = len(img1)
    ones1 = [(i, j) for i in range(n) for j in range(n) if img1[i][j] == 1]
    ones2 = [(i, j) for i in range(n) for j in range(n) if img2[i][j] == 1]
    cnt = Counter()
    for i1, j1 in ones1:
        for i2, j2 in ones2:
            cnt[(i1 - i2, j1 - j2)] += 1
    return max(cnt.values()) if cnt else 0
""",
    visible=[{"img1": [[1, 1, 0], [0, 1, 0], [0, 1, 0]],
              "img2": [[0, 0, 0], [0, 1, 1], [0, 0, 1]]},
             {"img1": [[1]], "img2": [[1]]}, {"img1": [[0]], "img2": [[0]]}],
    hidden=[{"img1": [[1, 0], [0, 1]], "img2": [[0, 0], [1, 1]]},
            {"img1": [[1, 1], [1, 1]], "img2": [[1, 1], [1, 1]]},
            {"img1": [[0, 0], [0, 0]], "img2": [[1, 1], [1, 1]]},
            {"img1": [[1, 0, 0], [0, 0, 0], [0, 0, 1]],
             "img2": [[0, 0, 0], [0, 1, 0], [0, 0, 0]]}],
    gen=lambda r: [_overlap_gen(r) for _ in range(8)],
    brute=_overlap_brute,
    checks=[({"img1": [[1, 1, 0], [0, 1, 0], [0, 1, 0]],
              "img2": [[0, 0, 0], [0, 1, 1], [0, 0, 1]]}, 3),
            ({"img1": [[1]], "img2": [[1]]}, 1), ({"img1": [[0]], "img2": [[0]]}, 0)],
    source="new_p")


# ===========================================================================
# 13. Divide Two Integers
# ===========================================================================
add("divide-two-integers", "Divide Two Integers", "medium",
    ["math", "bit-manipulation"], "divide",
    [("dividend", "int"), ("divisor", "int")], "int",
    """
Divide `dividend` by `divisor` **without using multiplication, division, or modulo**,
truncating toward zero. The result is clamped to the signed 32-bit range
`[-2^31, 2^31 - 1]` (return `2^31 - 1` on overflow). **Return the quotient.**

**Examples**
```
dividend = 10, divisor = 3   ->  3
dividend = 7, divisor = -3   ->  -2
```

**Constraints:** both fit in signed 32 bits, `divisor != 0`.
""",
    """def divide(dividend, divisor):
    INT_MAX, INT_MIN = 2 ** 31 - 1, -2 ** 31
    if dividend == INT_MIN and divisor == -1:
        return INT_MAX
    neg = (dividend < 0) != (divisor < 0)
    a, b = abs(dividend), abs(divisor)
    q = 0
    while a >= b:
        temp, m = b, 1
        while a >= (temp << 1):
            temp <<= 1
            m <<= 1
        a -= temp
        q += m
    q = -q if neg else q
    return max(INT_MIN, min(INT_MAX, q))
""",
    visible=[{"dividend": 10, "divisor": 3}, {"dividend": 7, "divisor": -3}],
    hidden=[{"dividend": -7, "divisor": 3}, {"dividend": 0, "divisor": 5},
            {"dividend": -2147483648, "divisor": -1}, {"dividend": 1, "divisor": 1},
            {"dividend": -2147483648, "divisor": 2}],
    gen=lambda r: [(lambda dv: {"dividend": r.randint(-1000, 1000), "divisor": dv})
                   (r.choice([x for x in range(-10, 11) if x != 0])) for _ in range(8)],
    brute=_divide_brute,
    checks=[({"dividend": 10, "divisor": 3}, 3), ({"dividend": 7, "divisor": -3}, -2),
            ({"dividend": -7, "divisor": 3}, -2),
            ({"dividend": -2147483648, "divisor": -1}, 2147483647),
            ({"dividend": 0, "divisor": 5}, 0)],
    source="new_p")


# ===========================================================================
# 14. Reordered Power of 2
# ===========================================================================
add("reordered-power-of-2", "Reordered Power of 2", "medium",
    ["math", "counting", "sorting"], "reorderedPowerOf2", [("N", "int")], "bool",
    """
**Return `true` if the digits of `N` can be rearranged (no leading zero) to form a
power of `2`.**

**Examples**
```
N = 1   ->  true
N = 10  ->  false
N = 16  ->  true
N = 46  ->  true
```

**Constraints:** `1 <= N <= 10^9`.
""",
    """def reorderedPowerOf2(N):
    from collections import Counter
    target = Counter(str(N))
    return any(Counter(str(1 << i)) == target for i in range(31))
""",
    visible=[{"N": 1}, {"N": 10}, {"N": 16}, {"N": 46}],
    hidden=[{"N": 24}, {"N": 2}, {"N": 61}, {"N": 128}, {"N": 821}],
    gen=lambda r: [{"N": r.randint(1, 2000)} for _ in range(8)],
    brute=_reorder_brute,
    checks=[({"N": 1}, True), ({"N": 10}, False), ({"N": 16}, True), ({"N": 24}, False),
            ({"N": 46}, True)],
    source="new_p")


# ===========================================================================
# 15. Count All Valid Pickup and Delivery Options
# ===========================================================================
add("count-all-valid-pickup-and-delivery-options",
    "Count All Valid Pickup and Delivery Options", "hard",
    ["math", "dynamic-programming", "combinatorics"], "countOrders",
    [("n", "int")], "int",
    """
There are `n` orders, each with a pickup `P_i` and a delivery `D_i`. **Return the
number of sequences of all `2n` events in which every `D_i` comes after its `P_i`**,
modulo `10^9 + 7`.

**Examples**
```
n = 1  ->  1
n = 2  ->  6
n = 3  ->  90
```

**Constraints:** `1 <= n <= 500`.
""",
    """def countOrders(n):
    MOD = 10 ** 9 + 7
    res = 1
    for i in range(1, n + 1):
        res = res * i * (2 * i - 1) % MOD
    return res
""",
    visible=[{"n": 1}, {"n": 2}, {"n": 3}],
    # brute is factorial in n; keep visible/hidden/gen at n<=4. Larger n only in checks.
    hidden=[{"n": 4}, {"n": 1}, {"n": 2}, {"n": 3}],
    gen=lambda r: [{"n": r.randint(1, 4)} for _ in range(6)],
    brute=_orders_brute,
    checks=[({"n": 1}, 1), ({"n": 2}, 6), ({"n": 3}, 90), ({"n": 4}, 2520),
            ({"n": 5}, 113400)],
    source="new_p")


# ===========================================================================
# 16. Shortest Path to Get All Keys
# ===========================================================================
add("shortest-path-to-get-all-keys", "Shortest Path to Get All Keys", "hard",
    ["array", "bitmask", "breadth-first-search", "matrix"], "shortestPathAllKeys",
    [("grid", "string[]")], "int",
    """
In the grid, `.` is empty, `#` is a wall, `@` is the start, lowercase letters are
keys and uppercase letters are locks. You move in the 4 directions, picking up keys
you step on; you may enter a lock only if you already hold its key. **Return the
fewest moves to collect every key, or `-1` if impossible.**

**Examples**
```
["@.a.#","###.#","b.A.B"]  ->  8
["@..aA","..B#.","....b"]   ->  6
```

**Constraints:** `1 <= rows, cols <= 30`, keys are `a..f`, `1..6` keys.
""",
    """def shortestPathAllKeys(grid):
    from collections import deque
    R, C = len(grid), len(grid[0])
    start = None
    total = 0
    for i in range(R):
        for j in range(C):
            ch = grid[i][j]
            if ch == '@':
                start = (i, j)
            elif ch.islower():
                total += 1
    full = (1 << total) - 1
    q = deque([(start[0], start[1], 0, 0)])
    seen = {(start[0], start[1], 0)}
    while q:
        r, c, keys, d = q.popleft()
        if keys == full:
            return d
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                ch = grid[nr][nc]
                if ch == '#':
                    continue
                if ch.isupper() and not (keys >> (ord(ch) - ord('A')) & 1):
                    continue
                nk = keys
                if ch.islower():
                    nk = keys | (1 << (ord(ch) - ord('a')))
                if (nr, nc, nk) not in seen:
                    seen.add((nr, nc, nk))
                    q.append((nr, nc, nk, d + 1))
    return -1
""",
    visible=[{"grid": ["@.a.#", "###.#", "b.A.B"]}, {"grid": ["@..aA", "..B#.", "....b"]}],
    hidden=[{"grid": ["@a"]}, {"grid": ["@.a"]}, {"grid": ["@#a"]}, {"grid": ["@aA"]},
            {"grid": ["a.@.A"]}],
    checks=[({"grid": ["@.a.#", "###.#", "b.A.B"]}, 8),
            ({"grid": ["@..aA", "..B#.", "....b"]}, 6), ({"grid": ["@a"]}, 1),
            ({"grid": ["@.a"]}, 2), ({"grid": ["@#a"]}, -1)],
    source="new_p")


# ===========================================================================
# 17. Bulls and Cows
# ===========================================================================
add("bulls-and-cows", "Bulls and Cows", "medium",
    ["string", "hash-table", "counting"], "getHint",
    [("secret", "string"), ("guess", "string")], "string",
    """
Compare a `guess` to a `secret` number (digit strings of equal length). A *bull* is a
digit correct in both value and position; a *cow* is a digit present in the secret but
in the wrong position (each secret digit matches at most one guess digit). **Return
the hint as `"xAyB"`** where `x` is bulls and `y` is cows.

**Examples**
```
secret = "1807", guess = "7810"  ->  "1A3B"
secret = "1123", guess = "0111"  ->  "1A1B"
```

**Constraints:** equal-length digit strings.
""",
    """def getHint(secret, guess):
    from collections import Counter
    bulls = sum(1 for s, g in zip(secret, guess) if s == g)
    sc = Counter(s for s, g in zip(secret, guess) if s != g)
    gc = Counter(g for s, g in zip(secret, guess) if s != g)
    cows = sum(min(sc[d], gc[d]) for d in sc)
    return f"{bulls}A{cows}B"
""",
    visible=[{"secret": "1807", "guess": "7810"}, {"secret": "1123", "guess": "0111"}],
    hidden=[{"secret": "1", "guess": "0"}, {"secret": "1", "guess": "1"},
            {"secret": "11", "guess": "10"}, {"secret": "1122", "guess": "2211"},
            {"secret": "0", "guess": "0"}],
    gen=lambda r: [_hint_gen(r) for _ in range(8)],
    brute=_hint_brute,
    checks=[({"secret": "1807", "guess": "7810"}, "1A3B"),
            ({"secret": "1123", "guess": "0111"}, "1A1B"),
            ({"secret": "1", "guess": "1"}, "1A0B"),
            ({"secret": "1122", "guess": "2211"}, "0A4B")],
    source="new_p")


# ===========================================================================
# 18. Distinct Subsequences II
# ===========================================================================
add("distinct-subsequences-ii", "Distinct Subsequences II", "hard",
    ["string", "dynamic-programming"], "distinctSubseqII", [("S", "string")], "int",
    """
**Return the number of distinct non-empty subsequences of `S`**, modulo `10^9 + 7`.

**Examples**
```
S = "abc"  ->  7
S = "aba"  ->  6
S = "aaa"  ->  3
```

**Constraints:** `1 <= len(S) <= 2000`, lowercase letters.
""",
    """def distinctSubseqII(S):
    MOD = 10 ** 9 + 7
    end = {}
    for c in S:
        end[c] = (sum(end.values()) + 1) % MOD
    return sum(end.values()) % MOD
""",
    visible=[{"S": "abc"}, {"S": "aba"}, {"S": "aaa"}],
    hidden=[{"S": "a"}, {"S": "ab"}, {"S": "abab"}, {"S": "aabb"}, {"S": "abcabc"}],
    gen=lambda r: [{"S": sstr(r, 0, 12, "abc")} for _ in range(8)],
    brute=_distsub_brute,
    checks=[({"S": "abc"}, 7), ({"S": "aba"}, 6), ({"S": "aaa"}, 3), ({"S": "ab"}, 3)],
    source="new_p")


# ===========================================================================
# 19. Sum of Subarray Minimums
# ===========================================================================
add("sum-of-subarray-minimums", "Sum of Subarray Minimums", "medium",
    ["array", "stack", "monotonic-stack", "dynamic-programming"], "sumSubarrayMins",
    [("A", "int[]")], "int",
    """
**Return the sum of `min(B)` over every contiguous subarray `B` of `A`**, modulo
`10^9 + 7`.

**Example**
```
A = [3,1,2,4]  ->  17
```

**Constraints:** `1 <= len(A) <= 3*10^4`, `1 <= A[i] <= 3*10^4`.
""",
    """def sumSubarrayMins(A):
    MOD = 10 ** 9 + 7
    n = len(A)
    prev = [-1] * n
    nxt = [n] * n
    stack = []
    for i in range(n):
        while stack and A[stack[-1]] > A[i]:
            stack.pop()
        prev[i] = stack[-1] if stack else -1
        stack.append(i)
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and A[stack[-1]] >= A[i]:
            stack.pop()
        nxt[i] = stack[-1] if stack else n
        stack.append(i)
    res = 0
    for i in range(n):
        res = (res + A[i] * (i - prev[i]) * (nxt[i] - i)) % MOD
    return res % MOD
""",
    visible=[{"A": [3, 1, 2, 4]}],
    hidden=[{"A": [1]}, {"A": [3, 3, 3]}, {"A": [1, 2, 3]}, {"A": [4, 3, 2, 1]},
            {"A": [11, 81, 94, 43, 3]}],
    gen=lambda r: [{"A": [r.randint(1, 10) for _ in range(r.randint(1, 12))]}
                   for _ in range(8)],
    brute=_submin_brute,
    checks=[({"A": [3, 1, 2, 4]}, 17), ({"A": [3, 3, 3]}, 18), ({"A": [1, 2, 3]}, 10),
            ({"A": [1]}, 1)],
    source="new_p")
