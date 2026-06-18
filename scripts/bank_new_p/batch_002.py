"""Batch 002 of the new_p.txt import (20 problems)."""
import re

from scripts.build_bank import add, ilist, sstr  # noqa: F401

MOD = 10 ** 9 + 7


# --------------------------- brute / reference helpers ---------------------
def _fruit_brute(tree):
    n = len(tree)
    best = 0
    for l in range(n):
        kinds = set()
        for r in range(l, n):
            kinds.add(tree[r])
            if len(kinds) > 2:
                break
            best = max(best, r - l + 1)
    return best


def _keys_brute(n):
    from collections import deque
    if n == 1:
        return 0
    seen = set()
    dq = deque([(1, 0, 0)])
    while dq:
        a, c, s = dq.popleft()
        if a == n:
            return s
        if (a, c) in seen:
            continue
        seen.add((a, c))
        if c != a:
            dq.append((a, a, s + 1))
        if c > 0 and a + c <= n:
            dq.append((a + c, c, s + 1))
    return -1


def _gen_encoded(r, depth):
    out = []
    for _ in range(r.randint(1, 3)):
        if depth > 0 and r.random() < 0.5:
            out.append(f"{r.randint(1, 3)}[{_gen_encoded(r, depth - 1)}]")
        else:
            out.append("".join(r.choice("ab") for _ in range(r.randint(1, 3))))
    return "".join(out)


def _decode_brute(s):
    pat = re.compile(r'(\d+)\[([a-z]*)\]')
    while '[' in s:
        s = pat.sub(lambda m: int(m.group(1)) * m.group(2), s)
    return s


def _perf_brute(n, speed, efficiency, k):
    from itertools import combinations
    best = 0
    idx = list(range(n))
    for size in range(1, k + 1):
        for combo in combinations(idx, size):
            spd = sum(speed[i] for i in combo)
            eff = min(efficiency[i] for i in combo)
            best = max(best, spd * eff)
    return best % (10 ** 9 + 7)


def _assign_brute(difficulty, profit, worker):
    total = 0
    for w in worker:
        best = 0
        for d, p in zip(difficulty, profit):
            if d <= w:
                best = max(best, p)
        total += best
    return total


def _rmdup_brute(s, k):
    while True:
        m = re.search(r'(.)\1{' + str(k - 1) + ',}', s)
        if not m:
            break
        s = s[:m.start()] + m.group(1) * (len(m.group(0)) - k) + s[m.end():]
    return s


def _partition_brute(nums):
    n = len(nums)
    for i in range(1, n):
        if max(nums[:i]) <= min(nums[i:]):
            return i
    return n


def _gen_partition(r):
    left = [r.randint(0, 5) for _ in range(r.randint(1, 5))]
    mx = max(left)
    right = [r.randint(mx, mx + 5) for _ in range(r.randint(1, 5))]
    return {"nums": left + right}


def _magnet_brute(position, m):
    from itertools import combinations
    pos = sorted(position)
    best = 0
    for combo in combinations(pos, m):
        best = max(best, min(combo[i + 1] - combo[i] for i in range(m - 1)))
    return best


def _matchsticks_brute(matchsticks):
    from itertools import product
    total = sum(matchsticks)
    if total == 0 or total % 4:
        return False
    side = total // 4
    n = len(matchsticks)
    for assign in product(range(4), repeat=n):
        sums = [0, 0, 0, 0]
        for i, g in enumerate(assign):
            sums[g] += matchsticks[i]
        if all(x == side for x in sums):
            return True
    return False


def _cake_brute(h, w, horizontalCuts, verticalCuts):
    hh = sorted([0] + sorted(horizontalCuts) + [h])
    ww = sorted([0] + sorted(verticalCuts) + [w])
    mh = max(hh[i + 1] - hh[i] for i in range(len(hh) - 1))
    mw = max(ww[i + 1] - ww[i] for i in range(len(ww) - 1))
    return (mh * mw) % (10 ** 9 + 7)


def _jump5_brute(arr, d):
    n = len(arr)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for step in (-1, 1):
            for x in range(1, d + 1):
                j = i + step * x
                if not (0 <= j < n) or arr[j] >= arr[i]:
                    break
                adj[i].append(j)
    from functools import lru_cache

    @lru_cache(None)
    def f(i):
        return 1 + max((f(j) for j in adj[i]), default=0)
    return max(f(i) for i in range(n))


def _scs_brute(str1, str2):
    from functools import lru_cache

    @lru_cache(None)
    def lcs(i, j):
        if i == 0 or j == 0:
            return 0
        if str1[i - 1] == str2[j - 1]:
            return 1 + lcs(i - 1, j - 1)
        return max(lcs(i - 1, j), lcs(i, j - 1))
    return len(str1) + len(str2) - lcs(len(str1), len(str2))


def _wild_brute(s, p):
    regex = '^' + ''.join('.*' if c == '*' else ('.' if c == '?' else re.escape(c))
                          for c in p) + '$'
    return re.match(regex, s) is not None


def _gen_anagram(r):
    base = [r.choice("abc") for _ in range(r.randint(1, 6))]
    b = base[:]
    r.shuffle(b)
    return {"A": "".join(base), "B": "".join(b)}


def _css_brute(nums, k):
    n = len(nums)
    dp = [0] * n
    res = float('-inf')
    for i in range(n):
        best = 0
        for j in range(max(0, i - k), i):
            best = max(best, dp[j])
        dp[i] = nums[i] + best
        res = max(res, dp[i])
    return res


def _preorder_brute(preorder):
    stack = []
    for node in preorder.split(','):
        stack.append(node)
        while len(stack) >= 3 and stack[-1] == '#' and stack[-2] == '#' and stack[-3] != '#':
            stack.pop()
            stack.pop()
            stack.pop()
            stack.append('#')
    return stack == ['#']


def _gen_preorder(r):
    def build(depth):
        if depth <= 0 or r.random() < 0.4:
            return ['#']
        return [str(r.randint(1, 9))] + build(depth - 1) + build(depth - 1)
    seq = build(r.randint(0, 3))
    s = ",".join(seq)
    if r.random() < 0.35 and len(seq) > 1:
        s = ",".join(seq[:-1]) if r.random() < 0.5 else s + ",#"
    return {"preorder": s}


def _issub_brute(s, t):
    i = 0
    for c in t:
        if i < len(s) and s[i] == c:
            i += 1
    return i == len(s)


def _minint_brute(num, k):
    s = list(num)
    n = len(s)
    i = 0
    while i < n and k > 0:
        best = i
        for j in range(i + 1, min(n, i + k + 1)):
            if s[j] < s[best]:
                best = j
        cost = best - i
        if cost <= k:
            s.insert(i, s.pop(best))
            k -= cost
        i += 1
    return "".join(s)


# ===========================================================================
# 1. Fruit Into Baskets
# ===========================================================================
add("fruit-into-baskets", "Fruit Into Baskets", "medium",
    ["array", "sliding-window", "hash-table"], "totalFruit",
    [("tree", "int[]")], "int",
    """
Walking left to right past a row of trees, `tree[i]` is the fruit type of tree `i`.
You carry two baskets and each basket holds only one type of fruit. Starting at any
tree, you pick one fruit from each tree moving right and stop when you'd need a
third type. **Return the maximum number of fruits** you can collect — i.e. the
length of the longest contiguous subarray containing at most two distinct values.

**Examples**
```
tree = [1,2,1]                       ->  3
tree = [0,1,2,2]                     ->  3   ([1,2,2])
tree = [1,2,3,2,2]                   ->  4   ([2,3,2,2])
tree = [3,3,3,1,2,1,1,2,3,3,4]       ->  5   ([1,2,1,1,2])
```

**Constraints:** `1 <= len(tree) <= 4*10^4`, `0 <= tree[i] < len(tree)`.
""",
    """def totalFruit(tree):
    from collections import defaultdict
    count = defaultdict(int)
    l = 0
    best = 0
    for r, t in enumerate(tree):
        count[t] += 1
        while len(count) > 2:
            count[tree[l]] -= 1
            if count[tree[l]] == 0:
                del count[tree[l]]
            l += 1
        best = max(best, r - l + 1)
    return best
""",
    visible=[{"tree": [1, 2, 1]}, {"tree": [0, 1, 2, 2]}, {"tree": [1, 2, 3, 2, 2]}],
    hidden=[{"tree": [3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4]}, {"tree": [0]},
            {"tree": [1, 1, 1, 1]}, {"tree": [(i // 3) % 5 for i in range(1000)]}],
    gen=lambda r: [{"tree": ilist(r, 1, 20, 0, 4)} for _ in range(5)],
    brute=_fruit_brute,
    checks=[({"tree": [1, 2, 1]}, 3), ({"tree": [0, 1, 2, 2]}, 3),
            ({"tree": [1, 2, 3, 2, 2]}, 4),
            ({"tree": [3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4]}, 5)],
    source="new_p")


# ===========================================================================
# 2. 2 Keys Keyboard
# ===========================================================================
add("2-keys-keyboard", "2 Keys Keyboard", "medium",
    ["math", "dynamic-programming"], "minSteps", [("n", "int")], "int",
    """
A notepad starts with a single `'A'`. Each step is either **Copy All** (copy the
entire current contents) or **Paste** (append the last copied contents). **Return
the minimum number of steps** to make the notepad contain exactly `n` copies of
`'A'`. (The answer is the sum of the prime factors of `n`.)

**Examples**
```
n = 1  ->  0
n = 3  ->  3   (Copy All, Paste, Paste)
n = 6  ->  5   (A -> AA in 2 steps, then -> AAAAAA in 3)
```

**Constraints:** `1 <= n <= 1000`.
""",
    """def minSteps(n):
    res = 0
    d = 2
    while n > 1:
        while n % d == 0:
            res += d
            n //= d
        d += 1
    return res
""",
    visible=[{"n": 1}, {"n": 3}, {"n": 6}],
    hidden=[{"n": 2}, {"n": 4}, {"n": 9}, {"n": 12}, {"n": 1000}],
    gen=lambda r: [{"n": r.randint(1, 80)} for _ in range(6)],
    brute=_keys_brute,
    checks=[({"n": 1}, 0), ({"n": 3}, 3), ({"n": 6}, 5), ({"n": 4}, 4),
            ({"n": 997}, 997)],
    source="new_p")


# ===========================================================================
# 3. 24 Game
# ===========================================================================
add("24-game", "24 Game", "hard", ["array", "backtracking", "math"],
    "judgePoint24", [("cards", "int[]")], "bool",
    """
You have four cards, each a number from `1` to `9`. Using `+`, `-`, `*`, `/` and
parentheses (each operator is binary; no unary minus, no digit concatenation),
**return `true` if the four cards can be combined to make `24`**, else `false`.
Division is real division (e.g. `4 / (1 - 2/3) = 12`).

**Examples**
```
cards = [4,1,8,7]  ->  true    ((8-4) * (7-1) = 24)
cards = [1,2,1,2]  ->  false
```

**Constraints:** `cards.length == 4`, `1 <= cards[i] <= 9`.
""",
    """def judgePoint24(cards):
    def solve(nums):
        if len(nums) == 1:
            return abs(nums[0] - 24) < 1e-6
        for i in range(len(nums)):
            for j in range(len(nums)):
                if i == j:
                    continue
                rest = [nums[k] for k in range(len(nums)) if k != i and k != j]
                cand = [nums[i] + nums[j], nums[i] - nums[j], nums[i] * nums[j]]
                if abs(nums[j]) > 1e-6:
                    cand.append(nums[i] / nums[j])
                for v in cand:
                    if solve(rest + [v]):
                        return True
        return False
    return solve([float(c) for c in cards])
""",
    visible=[{"cards": [4, 1, 8, 7]}, {"cards": [1, 2, 1, 2]}],
    hidden=[{"cards": [1, 1, 1, 1]}, {"cards": [3, 3, 8, 8]},
            {"cards": [4, 4, 6, 6]}, {"cards": [1, 5, 5, 5]},
            {"cards": [2, 2, 2, 2]}],
    gen=lambda r: [{"cards": [r.randint(1, 9) for _ in range(4)]} for _ in range(6)],
    checks=[({"cards": [4, 1, 8, 7]}, True), ({"cards": [1, 2, 1, 2]}, False),
            ({"cards": [1, 1, 1, 1]}, False), ({"cards": [3, 3, 8, 8]}, True),
            ({"cards": [1, 5, 5, 5]}, True)],
    source="new_p")


# ===========================================================================
# 4. Decode String
# ===========================================================================
add("decode-string", "Decode String", "medium",
    ["string", "stack", "recursion"], "decodeString", [("s", "string")], "string",
    """
Decode a string encoded with the rule `k[encoded_string]`, meaning
`encoded_string` repeated `k` times (`k` a positive integer). Encodings may nest.
The input is always valid and digits appear only as repeat counts. **Return the
decoded string.**

**Examples**
```
s = "3[a]2[bc]"      ->  "aaabcbc"
s = "3[a2[c]]"       ->  "accaccacc"
s = "2[abc]3[cd]ef"  ->  "abcabccdcdcdef"
```

**Constraints:** `1 <= len(s) <= 30`, decoded length fits comfortably in memory.
""",
    """def decodeString(s):
    stack = []
    cur = ""
    num = 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == '[':
            stack.append((cur, num))
            cur = ""
            num = 0
        elif ch == ']':
            prev, k = stack.pop()
            cur = prev + cur * k
        else:
            cur += ch
    return cur
""",
    visible=[{"s": "3[a]2[bc]"}, {"s": "3[a2[c]]"}, {"s": "2[abc]3[cd]ef"}],
    hidden=[{"s": "abc"}, {"s": "10[a]"}, {"s": "2[2[2[a]]]"},
            {"s": "3[z]2[2[y]pq]"}],
    gen=lambda r: [{"s": _gen_encoded(r, 2)} for _ in range(6)],
    brute=_decode_brute,
    checks=[({"s": "3[a]2[bc]"}, "aaabcbc"), ({"s": "3[a2[c]]"}, "accaccacc"),
            ({"s": "2[abc]3[cd]ef"}, "abcabccdcdcdef"), ({"s": "10[a]"}, "a" * 10)],
    source="new_p")


# ===========================================================================
# 5. Maximum Performance of a Team
# ===========================================================================
add("maximum-performance-of-a-team", "Maximum Performance of a Team", "hard",
    ["array", "heap", "greedy", "sorting"], "maxPerformance",
    [("n", "int"), ("speed", "int[]"), ("efficiency", "int[]"), ("k", "int")], "int",
    """
There are `n` engineers; engineer `i` has `speed[i]` and `efficiency[i]`. A team's
performance is `(sum of its members' speeds) * (minimum efficiency among them)`.
Choose **at most `k`** engineers to **maximize performance**; return it modulo
`10^9 + 7`.

**Examples**
```
n=6, speed=[2,10,3,1,5,8], efficiency=[5,4,3,9,7,2], k=2  ->  60   ((10+5)*4)
n=6, speed=[2,10,3,1,5,8], efficiency=[5,4,3,9,7,2], k=3  ->  68   ((2+10+5)*4)
n=6, speed=[2,10,3,1,5,8], efficiency=[5,4,3,9,7,2], k=4  ->  72
```

**Constraints:** `1 <= n <= 10^5`, `1 <= speed[i] <= 10^5`,
`1 <= efficiency[i] <= 10^8`, `1 <= k <= n`. (Take the max before applying the
modulo.)
""",
    """def maxPerformance(n, speed, efficiency, k):
    import heapq
    MOD = 10 ** 9 + 7
    engineers = sorted(zip(efficiency, speed), reverse=True)
    heap = []
    sum_speed = 0
    best = 0
    for eff, spd in engineers:
        heapq.heappush(heap, spd)
        sum_speed += spd
        if len(heap) > k:
            sum_speed -= heapq.heappop(heap)
        best = max(best, sum_speed * eff)
    return best % MOD
""",
    visible=[{"n": 6, "speed": [2, 10, 3, 1, 5, 8],
              "efficiency": [5, 4, 3, 9, 7, 2], "k": 2},
             {"n": 6, "speed": [2, 10, 3, 1, 5, 8],
              "efficiency": [5, 4, 3, 9, 7, 2], "k": 3},
             {"n": 6, "speed": [2, 10, 3, 1, 5, 8],
              "efficiency": [5, 4, 3, 9, 7, 2], "k": 4}],
    hidden=[{"n": 1, "speed": [5], "efficiency": [3], "k": 1},
            {"n": 3, "speed": [2, 8, 2], "efficiency": [2, 7, 1], "k": 2},
            {"n": 4, "speed": [4, 3, 2, 1], "efficiency": [1, 2, 3, 4], "k": 4}],
    gen=lambda r: [(lambda nn: {"n": nn,
                                "speed": [r.randint(1, 10) for _ in range(nn)],
                                "efficiency": [r.randint(1, 10) for _ in range(nn)],
                                "k": r.randint(1, nn)})(r.randint(1, 8))
                   for _ in range(6)],
    brute=_perf_brute,
    checks=[({"n": 6, "speed": [2, 10, 3, 1, 5, 8],
              "efficiency": [5, 4, 3, 9, 7, 2], "k": 2}, 60),
            ({"n": 6, "speed": [2, 10, 3, 1, 5, 8],
              "efficiency": [5, 4, 3, 9, 7, 2], "k": 3}, 68),
            ({"n": 6, "speed": [2, 10, 3, 1, 5, 8],
              "efficiency": [5, 4, 3, 9, 7, 2], "k": 4}, 72)],
    source="new_p")


# ===========================================================================
# 6. Most Profit Assigning Work
# ===========================================================================
add("most-profit-assigning-work", "Most Profit Assigning Work", "medium",
    ["array", "two-pointers", "greedy", "sorting"], "maxProfitAssignment",
    [("difficulty", "int[]"), ("profit", "int[]"), ("worker", "int[]")], "int",
    """
Job `i` has difficulty `difficulty[i]` and pays `profit[i]`. Worker `j` can do any
single job with difficulty at most `worker[j]` (a job may be done by many workers).
**Return the maximum total profit.** A worker who cannot do any job earns `0`.

**Example**
```
difficulty = [2,4,6,8,10], profit = [10,20,30,40,50], worker = [4,5,6,7]  ->  100
```

**Constraints:** `1 <= len(difficulty) == len(profit) <= 10^4`,
`1 <= len(worker) <= 10^4`, all values in `[1, 10^5]`.
""",
    """def maxProfitAssignment(difficulty, profit, worker):
    jobs = sorted(zip(difficulty, profit))
    worker = sorted(worker)
    i = 0
    best = 0
    total = 0
    for w in worker:
        while i < len(jobs) and jobs[i][0] <= w:
            best = max(best, jobs[i][1])
            i += 1
        total += best
    return total
""",
    visible=[{"difficulty": [2, 4, 6, 8, 10], "profit": [10, 20, 30, 40, 50],
              "worker": [4, 5, 6, 7]}],
    hidden=[{"difficulty": [5], "profit": [10], "worker": [1]},
            {"difficulty": [5], "profit": [10], "worker": [5, 5, 5]},
            {"difficulty": [13, 37, 71], "profit": [4, 7, 8], "worker": [4, 9, 15]},
            {"difficulty": [68, 35, 52, 47, 86], "profit": [67, 17, 1, 81, 3],
             "worker": [92, 10, 85, 84, 82]}],
    gen=lambda r: [(lambda j, wk: {"difficulty": [r.randint(1, 15) for _ in range(j)],
                                   "profit": [r.randint(1, 20) for _ in range(j)],
                                   "worker": [r.randint(1, 15) for _ in range(wk)]})
                   (r.randint(1, 6), r.randint(1, 6)) for _ in range(6)],
    brute=_assign_brute,
    checks=[({"difficulty": [2, 4, 6, 8, 10], "profit": [10, 20, 30, 40, 50],
              "worker": [4, 5, 6, 7]}, 100)],
    source="new_p")


# ===========================================================================
# 7. Remove All Adjacent Duplicates in String II
# ===========================================================================
add("remove-all-adjacent-duplicates-in-string-ii",
    "Remove All Adjacent Duplicates in String II", "medium",
    ["string", "stack"], "removeDuplicates",
    [("s", "string"), ("k", "int")], "string",
    """
A *k-duplicate removal* deletes `k` adjacent equal letters, after which the two
sides join. Repeat until no such group remains. **Return the final string** (it is
unique).

**Examples**
```
s = "abcd", k = 2            ->  "abcd"
s = "deeedbbcccbdaa", k = 3  ->  "aa"
s = "pbbcggttciiippooaais", k = 2 ->  "ps"
```

**Constraints:** `1 <= len(s) <= 10^5`, `2 <= k <= 10^4`, lowercase letters.
""",
    """def removeDuplicates(s, k):
    stack = []
    for c in s:
        if stack and stack[-1][0] == c:
            stack[-1][1] += 1
            if stack[-1][1] == k:
                stack.pop()
        else:
            stack.append([c, 1])
    return "".join(c * cnt for c, cnt in stack)
""",
    visible=[{"s": "abcd", "k": 2}, {"s": "deeedbbcccbdaa", "k": 3},
             {"s": "pbbcggttciiippooaais", "k": 2}],
    hidden=[{"s": "aaa", "k": 3}, {"s": "aaaa", "k": 2}, {"s": "aabbccddeeff", "k": 2},
            {"s": "yfttttfbbpieik", "k": 4}],
    gen=lambda r: [{"s": "".join(r.choice("ab") for _ in range(r.randint(1, 14))),
                    "k": r.randint(2, 4)} for _ in range(6)],
    brute=_rmdup_brute,
    checks=[({"s": "abcd", "k": 2}, "abcd"),
            ({"s": "deeedbbcccbdaa", "k": 3}, "aa"),
            ({"s": "pbbcggttciiippooaais", "k": 2}, "ps")],
    source="new_p")


# ===========================================================================
# 8. Partition Array into Disjoint Intervals
# ===========================================================================
add("partition-array-into-disjoint-intervals",
    "Partition Array into Disjoint Intervals", "medium",
    ["array", "greedy"], "partitionDisjoint", [("nums", "int[]")], "int",
    """
Partition `nums` into a contiguous `left` and `right` (both non-empty) so that every
element of `left` is `<=` every element of `right`, with `left` as short as
possible. **Return the length of `left`.** A valid partition is guaranteed to exist.

**Examples**
```
nums = [5,0,3,8,6]      ->  3   (left = [5,0,3], right = [8,6])
nums = [1,1,1,0,6,12]   ->  4   (left = [1,1,1,0])
```

**Constraints:** `2 <= len(nums) <= 3*10^4`, `0 <= nums[i] <= 10^6`, a valid
partition exists.
""",
    """def partitionDisjoint(nums):
    n = len(nums)
    left_max = nums[0]
    cur_max = nums[0]
    partition = 0
    for i in range(1, n):
        if nums[i] < left_max:
            partition = i
            left_max = cur_max
        else:
            cur_max = max(cur_max, nums[i])
    return partition + 1
""",
    visible=[{"nums": [5, 0, 3, 8, 6]}, {"nums": [1, 1, 1, 0, 6, 12]}],
    hidden=[{"nums": [1, 1]}, {"nums": [0, 1]}, {"nums": [1, 0]},
            {"nums": [2, 2, 4, 3, 3, 5]}, {"nums": [i % 50 for i in range(800)] + [100]}],
    gen=lambda r: [_gen_partition(r) for _ in range(6)],
    brute=_partition_brute,
    checks=[({"nums": [5, 0, 3, 8, 6]}, 3), ({"nums": [1, 1, 1, 0, 6, 12]}, 4)],
    source="new_p")


# ===========================================================================
# 9. Strong Password Checker
# ===========================================================================
add("strong-password-checker", "Strong Password Checker", "hard",
    ["string", "greedy", "dynamic-programming"], "strongPasswordChecker",
    [("s", "string")], "int",
    """
A password is *strong* if it (1) has `6..20` characters, (2) contains at least one
lowercase, one uppercase and one digit, and (3) has no run of three identical
characters in a row. One change = inserting, deleting, or replacing a single
character. **Return the minimum number of changes** to make `s` strong (`0` if it
already is).

**Examples**
```
s = "a"          ->  5
s = "aA1"        ->  3
s = "1337C0d3"   ->  0
s = "aaa123"     ->  1
```

**Constraints:** `0 <= len(s) <= 100`, printable ASCII letters/digits.
""",
    """def strongPasswordChecker(s):
    n = len(s)
    missing_type = 3
    if any(c.islower() for c in s):
        missing_type -= 1
    if any(c.isupper() for c in s):
        missing_type -= 1
    if any(c.isdigit() for c in s):
        missing_type -= 1

    change = 0
    one = two = 0
    p = 2
    while p < n:
        if s[p] == s[p - 1] == s[p - 2]:
            length = 2
            while p < n and s[p] == s[p - 1]:
                length += 1
                p += 1
            change += length // 3
            if length % 3 == 0:
                one += 1
            elif length % 3 == 1:
                two += 1
        else:
            p += 1

    if n < 6:
        return max(missing_type, 6 - n)
    elif n <= 20:
        return max(missing_type, change)
    else:
        delete = n - 20
        change -= min(delete, one)
        change -= min(max(delete - one, 0), two * 2) // 2
        change -= max(delete - one - 2 * two, 0) // 3
        return delete + max(missing_type, change)
""",
    visible=[{"s": "a"}, {"s": "aA1"}, {"s": "1337C0d3"}],
    hidden=[{"s": "aaa123"}, {"s": ""}, {"s": "aaaaa"}, {"s": "ABABABABABABABABABAB1"},
            {"s": "aaaaaaaaaaaaaaaaaaaaa"}, {"s": "1234567890Aa"}],
    gen=lambda r: [{"s": "".join(r.choice("aA1bc!") for _ in range(r.randint(0, 14)))}
                   for _ in range(6)],
    checks=[({"s": "a"}, 5), ({"s": "aA1"}, 3), ({"s": "1337C0d3"}, 0),
            ({"s": "aaa123"}, 1), ({"s": ""}, 6), ({"s": "aaaaa"}, 2)],
    source="new_p")


# ===========================================================================
# 10. Magnetic Force Between Two Balls
# ===========================================================================
add("magnetic-force-between-two-balls", "Magnetic Force Between Two Balls",
    "medium", ["array", "binary-search", "greedy", "sorting"], "maxDistance",
    [("position", "int[]"), ("m", "int")], "int",
    """
Place `m` balls into baskets located at the distinct positions `position` so that
the **minimum** distance between any two balls is as **large** as possible. **Return
that maximum possible minimum distance.**

**Examples**
```
position = [1,2,3,4,7], m = 3            ->  3   (use 1, 4, 7)
position = [5,4,3,2,1,1000000000], m = 2 ->  999999999
```

**Constraints:** `2 <= len(position) <= 10^5`, `1 <= position[i] <= 10^9` distinct,
`2 <= m <= len(position)`.
""",
    """def maxDistance(position, m):
    position = sorted(position)

    def feasible(d):
        count = 1
        last = position[0]
        for p in position[1:]:
            if p - last >= d:
                count += 1
                last = p
        return count >= m

    lo, hi = 1, position[-1] - position[0]
    res = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            res = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return res
""",
    visible=[{"position": [1, 2, 3, 4, 7], "m": 3},
             {"position": [5, 4, 3, 2, 1, 1000000000], "m": 2}],
    hidden=[{"position": [1, 2], "m": 2}, {"position": [1, 2, 3, 4, 5], "m": 5},
            {"position": [10, 1, 100, 50], "m": 2},
            {"position": [79, 74, 57, 22], "m": 4}],
    gen=lambda r: [(lambda p: {"position": p, "m": r.randint(2, len(p))})
                   (r.sample(range(1, 60), r.randint(2, 8))) for _ in range(6)],
    brute=_magnet_brute,
    checks=[({"position": [1, 2, 3, 4, 7], "m": 3}, 3),
            ({"position": [5, 4, 3, 2, 1, 1000000000], "m": 2}, 999999999)],
    source="new_p")


# ===========================================================================
# 11. Matchsticks to Square
# ===========================================================================
add("matchsticks-to-square", "Matchsticks to Square", "medium",
    ["array", "backtracking", "bitmask", "dynamic-programming"], "makesquare",
    [("matchsticks", "int[]")], "bool",
    """
Given the lengths `matchsticks`, **return `true` if you can use every matchstick
exactly once to form the four equal sides of a square** (no breaking, no leftovers),
else `false`.

**Examples**
```
matchsticks = [1,1,2,2,2]  ->  true   (sides of length 2)
matchsticks = [3,3,3,3,4]  ->  false
```

**Constraints:** `1 <= len(matchsticks) <= 15`, `1 <= matchsticks[i] <= 10^8`.
""",
    """def makesquare(matchsticks):
    total = sum(matchsticks)
    if not matchsticks or total % 4 != 0:
        return False
    side = total // 4
    matchsticks.sort(reverse=True)
    if matchsticks[0] > side:
        return False
    sides = [0] * 4

    def dfs(i):
        if i == len(matchsticks):
            return True
        for j in range(4):
            if sides[j] + matchsticks[i] <= side:
                sides[j] += matchsticks[i]
                if dfs(i + 1):
                    return True
                sides[j] -= matchsticks[i]
            if sides[j] == 0:
                break
        return False

    return dfs(0)
""",
    visible=[{"matchsticks": [1, 1, 2, 2, 2]}, {"matchsticks": [3, 3, 3, 3, 4]}],
    hidden=[{"matchsticks": [5, 5, 5, 5]}, {"matchsticks": [1]},
            {"matchsticks": [2, 2, 2, 2, 2, 2, 2, 2]},
            {"matchsticks": [4, 4, 4, 4, 1, 1, 1, 1]}],
    gen=lambda r: [{"matchsticks": ilist(r, 1, 7, 1, 6)} for _ in range(6)],
    brute=_matchsticks_brute,
    checks=[({"matchsticks": [1, 1, 2, 2, 2]}, True),
            ({"matchsticks": [3, 3, 3, 3, 4]}, False),
            ({"matchsticks": [5, 5, 5, 5]}, True), ({"matchsticks": [1]}, False)],
    source="new_p")


# ===========================================================================
# 12. Maximum Area of a Piece of Cake After Cuts
# ===========================================================================
add("maximum-area-of-a-piece-of-cake-after-horizontal-and-vertical-cuts",
    "Maximum Area of a Piece of Cake After Horizontal and Vertical Cuts", "medium",
    ["array", "greedy", "sorting"], "maxArea",
    [("h", "int"), ("w", "int"), ("horizontalCuts", "int[]"), ("verticalCuts", "int[]")],
    "int",
    """
A cake is `h` tall and `w` wide. `horizontalCuts[i]` is the distance from the top to
a horizontal cut; `verticalCuts[j]` is the distance from the left to a vertical cut.
After all cuts, **return the area of the largest piece**, modulo `10^9 + 7`. The
largest piece is the largest gap between consecutive horizontal cuts (including the
borders) times the largest such vertical gap.

**Examples**
```
h=5, w=4, horizontalCuts=[1,2,4], verticalCuts=[1,3]  ->  4
h=5, w=4, horizontalCuts=[3,1],  verticalCuts=[1]     ->  6
h=5, w=4, horizontalCuts=[3],    verticalCuts=[3]     ->  9
```

**Constraints:** `2 <= h, w <= 10^9`, cuts are distinct and strictly inside the
cake. (Take the max gap product before applying the modulo.)
""",
    """def maxArea(h, w, horizontalCuts, verticalCuts):
    MOD = 10 ** 9 + 7
    hc = sorted(horizontalCuts)
    vc = sorted(verticalCuts)
    max_h = max(hc[0], h - hc[-1])
    for i in range(1, len(hc)):
        max_h = max(max_h, hc[i] - hc[i - 1])
    max_v = max(vc[0], w - vc[-1])
    for i in range(1, len(vc)):
        max_v = max(max_v, vc[i] - vc[i - 1])
    return (max_h * max_v) % MOD
""",
    visible=[{"h": 5, "w": 4, "horizontalCuts": [1, 2, 4], "verticalCuts": [1, 3]},
             {"h": 5, "w": 4, "horizontalCuts": [3, 1], "verticalCuts": [1]},
             {"h": 5, "w": 4, "horizontalCuts": [3], "verticalCuts": [3]}],
    hidden=[{"h": 1000000000, "w": 1000000000, "horizontalCuts": [2],
             "verticalCuts": [2]},
            {"h": 10, "w": 10, "horizontalCuts": [5], "verticalCuts": [5]},
            {"h": 7, "w": 9, "horizontalCuts": [1, 3, 5], "verticalCuts": [2, 4, 8]}],
    gen=lambda r: [(lambda hh, ww: {"h": hh, "w": ww,
                                    "horizontalCuts": sorted(r.sample(range(1, hh), r.randint(1, min(4, hh - 1)))),
                                    "verticalCuts": sorted(r.sample(range(1, ww), r.randint(1, min(4, ww - 1))))})
                   (r.randint(3, 12), r.randint(3, 12)) for _ in range(6)],
    brute=_cake_brute,
    checks=[({"h": 5, "w": 4, "horizontalCuts": [1, 2, 4], "verticalCuts": [1, 3]}, 4),
            ({"h": 5, "w": 4, "horizontalCuts": [3, 1], "verticalCuts": [1]}, 6),
            ({"h": 5, "w": 4, "horizontalCuts": [3], "verticalCuts": [3]}, 9)],
    source="new_p")


# ===========================================================================
# 13. Jump Game V
# ===========================================================================
add("jump-game-v", "Jump Game V", "hard",
    ["array", "dynamic-programming", "sorting"], "maxJumps",
    [("arr", "int[]"), ("d", "int")], "int",
    """
From index `i` you may jump to `i ± x` for `1 <= x <= d` (staying in bounds), but
only if `arr[i]` is strictly greater than `arr[j]` and strictly greater than every
element strictly between `i` and `j`. Starting anywhere, **return the maximum number
of indices you can visit** (the start counts as one).

**Examples**
```
arr = [6,4,14,6,8,13,9,7,10,6,12], d = 2  ->  4
arr = [3,3,3,3,3], d = 3                   ->  1
arr = [7,6,5,4,3,2,1], d = 1               ->  7
```

**Constraints:** `1 <= len(arr) <= 1000`, `1 <= arr[i] <= 10^5`,
`1 <= d <= len(arr)`.
""",
    """def maxJumps(arr, d):
    import sys
    sys.setrecursionlimit(5000)
    n = len(arr)
    from functools import lru_cache

    @lru_cache(None)
    def dp(i):
        best = 1
        for step in (-1, 1):
            for x in range(1, d + 1):
                j = i + step * x
                if not (0 <= j < n) or arr[j] >= arr[i]:
                    break
                best = max(best, 1 + dp(j))
        return best

    return max(dp(i) for i in range(n))
""",
    visible=[{"arr": [6, 4, 14, 6, 8, 13, 9, 7, 10, 6, 12], "d": 2},
             {"arr": [3, 3, 3, 3, 3], "d": 3},
             {"arr": [7, 6, 5, 4, 3, 2, 1], "d": 1}],
    hidden=[{"arr": [7, 1, 7, 1, 7, 1], "d": 2}, {"arr": [66], "d": 1},
            {"arr": [1, 2, 3, 4, 5], "d": 2},
            {"arr": [83, 11, 83, 70, 75, 35, 67, 87, 90, 13], "d": 3}],
    gen=lambda r: [(lambda a: {"arr": a, "d": r.randint(1, len(a))})
                   (ilist(r, 1, 12, 1, 8)) for _ in range(6)],
    brute=_jump5_brute,
    checks=[({"arr": [6, 4, 14, 6, 8, 13, 9, 7, 10, 6, 12], "d": 2}, 4),
            ({"arr": [3, 3, 3, 3, 3], "d": 3}, 1),
            ({"arr": [7, 6, 5, 4, 3, 2, 1], "d": 1}, 7),
            ({"arr": [7, 1, 7, 1, 7, 1], "d": 2}, 2), ({"arr": [66], "d": 1}, 1)],
    source="new_p")


# ===========================================================================
# 14. Shortest Common Supersequence (length variant)
# ===========================================================================
add("shortest-common-supersequence", "Shortest Common Supersequence", "hard",
    ["string", "dynamic-programming"], "shortestCommonSupersequence",
    [("str1", "string"), ("str2", "string")], "int",
    """
A *common supersequence* of `str1` and `str2` is a string that has both as
subsequences. **Return the length of the shortest common supersequence**, which
equals `len(str1) + len(str2) - LCS(str1, str2)`.

**Examples**
```
str1 = "abac", str2 = "cab"   ->  5    (e.g. "cabac")
str1 = "abc",  str2 = "abc"   ->  3
str1 = "abc",  str2 = "def"   ->  6
```

**Constraints:** `1 <= len(str1), len(str2) <= 1000`, lowercase letters.
""",
    """def shortestCommonSupersequence(str1, str2):
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return m + n - dp[m][n]
""",
    visible=[{"str1": "abac", "str2": "cab"}, {"str1": "abc", "str2": "abc"},
             {"str1": "abc", "str2": "def"}],
    hidden=[{"str1": "a", "str2": "a"}, {"str1": "a", "str2": "b"},
            {"str1": "aaaa", "str2": "aa"}, {"str1": "geek", "str2": "eke"}],
    gen=lambda r: [{"str1": sstr(r, 1, 8, "ab"), "str2": sstr(r, 1, 8, "ab")}
                   for _ in range(6)],
    brute=_scs_brute,
    checks=[({"str1": "abac", "str2": "cab"}, 5), ({"str1": "abc", "str2": "abc"}, 3),
            ({"str1": "abc", "str2": "def"}, 6), ({"str1": "geek", "str2": "eke"}, 5)],
    source="new_p")


# ===========================================================================
# 15. Wildcard Matching
# ===========================================================================
add("wildcard-matching", "Wildcard Matching", "hard",
    ["string", "dynamic-programming", "greedy"], "isMatch",
    [("s", "string"), ("p", "string")], "bool",
    """
Implement wildcard matching where `'?'` matches any single character and `'*'`
matches any sequence (possibly empty). The whole string `s` must be matched by the
pattern `p`. **Return `true` if `p` matches `s`**, else `false`.

**Examples**
```
s = "aa",    p = "a"     ->  false
s = "aa",    p = "*"     ->  true
s = "cb",    p = "?a"    ->  false
s = "adceb", p = "*a*b"  ->  true
s = "acdcb", p = "a*c?b" ->  false
```

**Constraints:** `0 <= len(s), len(p) <= 2000`; `s` is lowercase letters, `p` is
lowercase letters plus `?` and `*`.
""",
    """def isMatch(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for j in range(1, n + 1):
        if p[j - 1] == '*':
            dp[0][j] = dp[0][j - 1]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == '*':
                dp[i][j] = dp[i - 1][j] or dp[i][j - 1]
            elif p[j - 1] == '?' or p[j - 1] == s[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
    return dp[m][n]
""",
    visible=[{"s": "aa", "p": "a"}, {"s": "aa", "p": "*"}, {"s": "cb", "p": "?a"},
             {"s": "adceb", "p": "*a*b"}, {"s": "acdcb", "p": "a*c?b"}],
    hidden=[{"s": "", "p": ""}, {"s": "", "p": "*"}, {"s": "abc", "p": "***"},
            {"s": "abc", "p": ""}, {"s": "mississippi", "p": "m??*ss*?i*pi"}],
    gen=lambda r: [{"s": sstr(r, 0, 6, "ab"),
                    "p": "".join(r.choice("ab?*") for _ in range(r.randint(0, 6)))}
                   for _ in range(6)],
    brute=_wild_brute,
    checks=[({"s": "aa", "p": "a"}, False), ({"s": "aa", "p": "*"}, True),
            ({"s": "cb", "p": "?a"}, False), ({"s": "adceb", "p": "*a*b"}, True),
            ({"s": "acdcb", "p": "a*c?b"}, False)],
    source="new_p")


# ===========================================================================
# 16. K-Similar Strings
# ===========================================================================
add("k-similar-strings", "K-Similar Strings", "hard",
    ["string", "breadth-first-search"], "kSimilarity",
    [("A", "string"), ("B", "string")], "int",
    """
Two anagrams `A` and `B` are *K-similar* if `A` can be turned into `B` by swapping
two characters `K` times. **Return the smallest such `K`.**

**Examples**
```
A = "ab",   B = "ba"    ->  1
A = "abc",  B = "bca"   ->  2
A = "abac", B = "baca"  ->  2
```

**Constraints:** `1 <= len(A) == len(B) <= 20`, `A` and `B` are anagrams over the
letters `a`..`f`.
""",
    """def kSimilarity(A, B):
    from collections import deque
    if A == B:
        return 0
    n = len(A)

    def neighbors(s):
        i = 0
        while s[i] == B[i]:
            i += 1
        res = []
        for j in range(i + 1, n):
            if s[j] == B[i] and s[j] != B[j]:
                res.append(s[:i] + s[j] + s[i + 1:j] + s[i] + s[j + 1:])
        return res

    seen = {A}
    dq = deque([(A, 0)])
    while dq:
        cur, k = dq.popleft()
        if cur == B:
            return k
        for nb in neighbors(cur):
            if nb not in seen:
                seen.add(nb)
                dq.append((nb, k + 1))
    return -1
""",
    visible=[{"A": "ab", "B": "ba"}, {"A": "abc", "B": "bca"},
             {"A": "abac", "B": "baca"}],
    hidden=[{"A": "aabc", "B": "abca"}, {"A": "a", "B": "a"},
            {"A": "abcba", "B": "bacba"}, {"A": "abcdef", "B": "fedcba"}],
    gen=lambda r: [_gen_anagram(r) for _ in range(6)],
    checks=[({"A": "ab", "B": "ba"}, 1), ({"A": "abc", "B": "bca"}, 2),
            ({"A": "abac", "B": "baca"}, 2), ({"A": "aabc", "B": "abca"}, 2),
            ({"A": "a", "B": "a"}, 0)],
    source="new_p")


# ===========================================================================
# 17. Constrained Subsequence Sum
# ===========================================================================
add("constrained-subsequence-sum", "Constrained Subsequence Sum", "hard",
    ["array", "dynamic-programming", "heap", "sliding-window"], "constrainedSubsetSum",
    [("nums", "int[]"), ("k", "int")], "int",
    """
**Return the maximum sum of a non-empty subsequence** of `nums` such that any two
consecutive chosen elements are at most `k` indices apart (if `nums[i]` and
`nums[j]` are consecutive in the subsequence with `i < j`, then `j - i <= k`).

**Examples**
```
nums = [10,2,-10,5,20], k = 2  ->  37   ([10,2,5,20])
nums = [-1,-2,-3], k = 1       ->  -1
nums = [10,-2,-10,-5,20], k = 2 ->  23   ([10,-2,-5,20])
```

**Constraints:** `1 <= k <= len(nums) <= 10^5`, `-10^4 <= nums[i] <= 10^4`.
""",
    """def constrainedSubsetSum(nums, k):
    from collections import deque
    n = len(nums)
    dp = [0] * n
    dq = deque()
    res = float('-inf')
    for i in range(n):
        while dq and dq[0] < i - k:
            dq.popleft()
        best_prev = dp[dq[0]] if dq else 0
        dp[i] = nums[i] + max(best_prev, 0)
        res = max(res, dp[i])
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()
        dq.append(i)
    return res
""",
    visible=[{"nums": [10, 2, -10, 5, 20], "k": 2}, {"nums": [-1, -2, -3], "k": 1},
             {"nums": [10, -2, -10, -5, 20], "k": 2}],
    hidden=[{"nums": [-5], "k": 1}, {"nums": [5], "k": 1},
            {"nums": [-8269, 3217, -4023, -4138, -683, 6455], "k": 3},
            {"nums": [(-1) ** i * (i % 7) for i in range(1000)], "k": 4}],
    gen=lambda r: [(lambda a: {"nums": a, "k": r.randint(1, len(a))})
                   (ilist(r, 1, 14, -8, 8)) for _ in range(6)],
    brute=_css_brute,
    checks=[({"nums": [10, 2, -10, 5, 20], "k": 2}, 37),
            ({"nums": [-1, -2, -3], "k": 1}, -1),
            ({"nums": [10, -2, -10, -5, 20], "k": 2}, 23)],
    source="new_p")


# ===========================================================================
# 18. Verify Preorder Serialization of a Binary Tree
# ===========================================================================
add("verify-preorder-serialization-of-a-binary-tree",
    "Verify Preorder Serialization of a Binary Tree", "medium",
    ["string", "stack", "tree"], "isValidSerialization",
    [("preorder", "string")], "bool",
    """
A binary tree's preorder traversal is serialized as comma-separated values, using
`#` for a null child. Given such a string, **return `true` if it is a valid preorder
serialization** of some binary tree — without reconstructing the tree.

**Examples**
```
preorder = "9,3,4,#,#,1,#,#,2,#,6,#,#"  ->  true
preorder = "1,#"                        ->  false
preorder = "9,#,#,1"                    ->  false
```

**Constraints:** values are integers or `#`, comma-separated, no empty tokens.
""",
    """def isValidSerialization(preorder):
    slots = 1
    for node in preorder.split(','):
        if slots == 0:
            return False
        if node == '#':
            slots -= 1
        else:
            slots += 1
    return slots == 0
""",
    visible=[{"preorder": "9,3,4,#,#,1,#,#,2,#,6,#,#"}, {"preorder": "1,#"},
             {"preorder": "9,#,#,1"}],
    hidden=[{"preorder": "#"}, {"preorder": "1,#,#"}, {"preorder": "1,#,#,#"},
            {"preorder": "7"}],
    gen=lambda r: [_gen_preorder(r) for _ in range(6)],
    brute=_preorder_brute,
    checks=[({"preorder": "9,3,4,#,#,1,#,#,2,#,6,#,#"}, True),
            ({"preorder": "1,#"}, False), ({"preorder": "9,#,#,1"}, False),
            ({"preorder": "#"}, True), ({"preorder": "1,#,#"}, True)],
    source="new_p")


# ===========================================================================
# 19. Is Subsequence
# ===========================================================================
add("is-subsequence", "Is Subsequence", "easy",
    ["string", "two-pointers", "dynamic-programming"], "isSubsequence",
    [("s", "string"), ("t", "string")], "bool",
    """
Given strings `s` and `t`, **return `true` if `s` is a subsequence of `t`** (i.e.
`s` can be formed by deleting some characters of `t` without reordering the rest),
else `false`. The empty string is a subsequence of every string.

**Examples**
```
s = "abc", t = "ahbgdc"  ->  true
s = "axc", t = "ahbgdc"  ->  false
```

**Constraints:** `0 <= len(s) <= 100`, `0 <= len(t) <= 10^4`, lowercase letters.
""",
    """def isSubsequence(s, t):
    it = iter(t)
    return all(c in it for c in s)
""",
    visible=[{"s": "abc", "t": "ahbgdc"}, {"s": "axc", "t": "ahbgdc"}],
    hidden=[{"s": "", "t": "abc"}, {"s": "abc", "t": ""}, {"s": "abc", "t": "abc"},
            {"s": "b", "t": "abc"}, {"s": "aaaa", "t": "aa"}],
    gen=lambda r: [{"s": sstr(r, 0, 5, "abc"), "t": sstr(r, 0, 12, "abc")}
                   for _ in range(6)],
    brute=_issub_brute,
    checks=[({"s": "abc", "t": "ahbgdc"}, True), ({"s": "axc", "t": "ahbgdc"}, False),
            ({"s": "", "t": "abc"}, True), ({"s": "abc", "t": ""}, False)],
    source="new_p")


# ===========================================================================
# 20. Minimum Possible Integer After at Most K Adjacent Swaps on Digits
# ===========================================================================
add("minimum-possible-integer-after-at-most-k-adjacent-swaps-on-digits",
    "Minimum Possible Integer After at Most K Adjacent Swaps on Digits", "hard",
    ["string", "greedy", "binary-indexed-tree"], "minInteger",
    [("num", "string"), ("k", "int")], "string",
    """
Given a digit string `num`, you may swap **adjacent** digits at most `k` times.
**Return the smallest integer (as a string)** obtainable. Leading zeros in the
result are allowed.

**Examples**
```
num = "4321", k = 4   ->  "1342"
num = "100", k = 1    ->  "010"
num = "36789", k = 1000 ->  "36789"
```

**Constraints:** `1 <= len(num) <= 3*10^4`, digits only with no leading zero,
`1 <= k <= 10^9`.
""",
    """def minInteger(num, k):
    n = len(num)
    from collections import deque
    pos = [deque() for _ in range(10)]
    for i, c in enumerate(num):
        pos[int(c)].append(i)
    bit = [0] * (n + 1)

    def update(i):
        i += 1
        while i <= n:
            bit[i] += 1
            i += i & -i

    def query(i):
        i += 1
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & -i
        return s

    res = []
    for _ in range(n):
        for d in range(10):
            if pos[d]:
                idx = pos[d][0]
                removed_before = query(idx - 1) if idx > 0 else 0
                cost = idx - removed_before
                if cost <= k:
                    k -= cost
                    res.append(str(d))
                    pos[d].popleft()
                    update(idx)
                    break
    return "".join(res)
""",
    visible=[{"num": "4321", "k": 4}, {"num": "100", "k": 1},
             {"num": "36789", "k": 1000}],
    hidden=[{"num": "22", "k": 22}, {"num": "9438957234785635408", "k": 23},
            {"num": "1", "k": 1}, {"num": "294984148179", "k": 11}],
    gen=lambda r: [{"num": str(r.randint(1, 9)) + "".join(str(r.randint(0, 9))
                                                          for _ in range(r.randint(0, 8))),
                    "k": r.randint(1, 20)} for _ in range(6)],
    brute=_minint_brute,
    checks=[({"num": "4321", "k": 4}, "1342"), ({"num": "100", "k": 1}, "010"),
            ({"num": "36789", "k": 1000}, "36789"), ({"num": "22", "k": 22}, "22"),
            ({"num": "9438957234785635408", "k": 23}, "0345989723478563548")],
    source="new_p")
