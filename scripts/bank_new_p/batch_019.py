"""Batch 019 of the new_p.txt import (20 problems).

Two entries triaged out of this group land in `_skips.py`:
  - `count-good-nodes-in-binary-tree` (== existing `count-good-nodes`)
  - `insert-delete-getrandom-o1`      (stateful design class + random output)

Reframes in this batch (the LeetCode form is not a single gradable answer):
  - `lowest-common-ancestor-of-deepest-leaves` -> return the VALUE of the LCA node
    (node values are unique). This makes `smallest-subtree-with-all-the-deepest-nodes`
    the same problem -> it is skipped as a dup.
  - `distant-barcodes` -> "return any arrangement" is not gradable; reframe to the
    feasibility bool `canRearrange` (true iff max frequency <= (n+1)//2).
  - `avoid-flood-in-the-city` -> the schedule is not unique; reframe to the bool
    `canAvoidFlood` (is it possible to avoid every flood?).
  - `binary-tree-pruning` -> return the pruned tree's level-order serialization.
  - `tweet-counts-per-frequency` -> single function over one tweet's recorded times.

`numbers-with-same-consecutive-differences` and `the-k-strongest-values-in-an-array`
allow any output order -> COMPARE set to "unordered" (with norm=sorted cross-check).

`smallest-good-base` has a big-integer answer and no feasible brute -> it relies on
known-answer checks only.

Trees are passed as LeetCode level-order arrays (None for a missing child) and
rebuilt inside each solution.
"""
from scripts.build_bank import add, COMPARE  # noqa: F401


# --------------------------- shared tree helpers ---------------------------
def _build_tree(vals):
    """LeetCode level-order list (None for missing) -> (left, right, val) dicts
    keyed by integer node id; root id is 0."""
    if not vals or vals[0] is None:
        return {}, {}, {}
    from collections import deque
    val = {0: vals[0]}
    left, right = {}, {}
    q = deque([0])
    nid = 1
    i = 1
    n = len(vals)
    while q and i < n:
        cur = q.popleft()
        if i < n:
            v = vals[i]; i += 1
            if v is not None:
                val[nid] = v; left[cur] = nid; q.append(nid); nid += 1
        if i < n:
            v = vals[i]; i += 1
            if v is not None:
                val[nid] = v; right[cur] = nid; q.append(nid); nid += 1
    return left, right, val


def _rand_tree_vals(r, n, lo, hi, distinct=False):
    """Random binary tree with `n` nodes serialized to a LeetCode level-order list
    (None for missing children, trailing Nones trimmed)."""
    from collections import deque
    pool = None
    if distinct:
        pool = r.sample(range(lo, hi + 1), min(n, hi - lo + 1))
        n = len(pool)
    nxt = [0]

    def newval():
        if pool is not None:
            v = pool[nxt[0]]; nxt[0] += 1; return v
        return r.randint(lo, hi)

    vals = [newval()]
    children = {0: [None, None]}
    avail = [(0, 0), (0, 1)]
    created = 1
    while created < n and avail:
        idx = r.randrange(len(avail))
        node, side = avail.pop(idx)
        new_id = len(vals)
        vals.append(newval())
        children[node][side] = new_id
        children[new_id] = [None, None]
        avail.append((new_id, 0))
        avail.append((new_id, 1))
        created += 1
    out = [vals[0]]
    q = deque([0])
    while q:
        node = q.popleft()
        for c in children[node]:
            if c is None:
                out.append(None)
            else:
                out.append(vals[c])
                q.append(c)
    while out and out[-1] is None:
        out.pop()
    return out


def _rand_tree_vals_01(r, n):
    return _rand_tree_vals(r, n, 0, 1)


# =========================================================================== #
# brute / reference helpers
# =========================================================================== #
def _topk_words_brute(words, k):
    from collections import Counter
    c = Counter(words)
    pool = list(c)
    res = []
    while pool and len(res) < k:
        best = min(pool, key=lambda w: (-c[w], w))
        res.append(best)
        pool.remove(best)
    return res


def _topk_words_gen(r):
    out = []
    for _ in range(6):
        words = [r.choice(["a", "ab", "abc", "b", "bb", "cc", "z"]) for _ in range(r.randint(1, 12))]
        uniq = len(set(words))
        out.append({"words": words, "k": r.randint(1, uniq)})
    return out


def _nlis_brute(nums):
    from itertools import combinations
    n = len(nums)
    best_len = 0
    for L in range(n, 0, -1):
        cnt = 0
        for combo in combinations(range(n), L):
            if all(nums[combo[i]] < nums[combo[i + 1]] for i in range(L - 1)):
                cnt += 1
        if cnt:
            return cnt
    return 0


def _nlis_gen(r):
    return [{"nums": [r.randint(0, 6) for _ in range(r.randint(1, 9))]} for _ in range(6)]


def _lca_brute(root):
    left, right, val = _build_tree(root)
    # paths from root to each node
    depth = {}
    path = {}

    def dfs(node, d, p):
        depth[node] = d
        path[node] = p + [node]
        if node in left:
            dfs(left[node], d + 1, path[node])
        if node in right:
            dfs(right[node], d + 1, path[node])

    dfs(0, 0, [])
    maxd = max(depth.values())
    deepest = [nd for nd, d in depth.items() if d == maxd]
    common = path[deepest[0]]
    for nd in deepest[1:]:
        p = path[nd]
        i = 0
        while i < len(common) and i < len(p) and common[i] == p[i]:
            i += 1
        common = common[:i]
    return val[common[-1]]


def _lca_gen(r):
    return [{"root": _rand_tree_vals(r, r.randint(1, 14), 1, 200, distinct=True)} for _ in range(8)]


def _matblock_brute(mat, k):
    m, n = len(mat), len(mat[0])
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            s = 0
            for r1 in range(max(0, i - k), min(m - 1, i + k) + 1):
                for c1 in range(max(0, j - k), min(n - 1, j + k) + 1):
                    s += mat[r1][c1]
            out[i][j] = s
    return out


def _matblock_gen(r):
    out = []
    for _ in range(6):
        m, n = r.randint(1, 6), r.randint(1, 6)
        mat = [[r.randint(0, 9) for _ in range(n)] for _ in range(m)]
        out.append({"mat": mat, "k": r.randint(0, 4)})
    return out


def _barcode_brute(barcodes):
    from itertools import permutations
    n = len(barcodes)
    if n <= 1:
        return True
    for p in set(permutations(barcodes)):
        if all(p[i] != p[i + 1] for i in range(n - 1)):
            return True
    return False


def _barcode_gen(r):
    return [{"barcodes": [r.randint(1, 3) for _ in range(r.randint(1, 7))]} for _ in range(8)]


def _flood_brute(rains):
    n = len(rains)

    def rec(i, full):
        if i == n:
            return True
        r = rains[i]
        if r > 0:
            if r in full:
                return False
            return rec(i + 1, full | {r})
        if rec(i + 1, full):
            return True
        for lake in full:
            if rec(i + 1, full - {lake}):
                return True
        return False

    return rec(0, frozenset())


def _flood_gen(r):
    out = []
    for _ in range(8):
        rains = [r.randint(0, 3) for _ in range(r.randint(1, 9))]
        out.append({"rains": rains})
    return out


def _bestrot_brute(nums):
    n = len(nums)
    best_k, best = 0, -1
    for K in range(n):
        rot = nums[K:] + nums[:K]
        sc = sum(1 for i, x in enumerate(rot) if x <= i)
        if sc > best:
            best, best_k = sc, K
    return best_k


def _bestrot_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(1, 14)
        out.append({"nums": [r.randint(0, n) for _ in range(n)]})
    return out


def _reach_brute(edges, maxMoves, n):
    import heapq
    adj = {i: [] for i in range(n)}
    nid = n
    for u, v, cnt in edges:
        prev = u
        for _ in range(cnt):
            adj.setdefault(nid, [])
            adj[prev].append(nid)
            adj[nid].append(prev)
            prev = nid
            nid += 1
        adj[prev].append(v)
        adj[v].append(prev)
    dist = {0: 0}
    pq = [(0, 0)]
    while pq:
        d, node = heapq.heappop(pq)
        if d > dist.get(node, 1 << 30):
            continue
        for nb in adj[node]:
            nd = d + 1
            if nd <= maxMoves and nd < dist.get(nb, 1 << 30):
                dist[nb] = nd
                heapq.heappush(pq, (nd, nb))
    return len(dist)


def _reach_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(2, 4)
        pairs = set()
        edges = []
        for v in range(1, n):
            u = r.randint(0, v - 1)
            key = (u, v)
            pairs.add(key)
            edges.append([u, v, r.randint(0, 3)])
        extra = r.randint(0, 1)
        for _ in range(extra):
            a, b = r.randint(0, n - 1), r.randint(0, n - 1)
            if a != b:
                key = (min(a, b), max(a, b))
                if key not in pairs:
                    pairs.add(key)
                    edges.append([key[0], key[1], r.randint(0, 3)])
        out.append({"edges": edges, "maxMoves": r.randint(0, 10), "n": n})
    return out


def _flipscore_brute(grid):
    m, n = len(grid), len(grid[0])
    best = 0
    for rmask in range(1 << m):
        for cmask in range(1 << n):
            s = 0
            for i in range(m):
                val = 0
                for j in range(n):
                    bit = grid[i][j]
                    if (rmask >> i) & 1:
                        bit ^= 1
                    if (cmask >> j) & 1:
                        bit ^= 1
                    val = val * 2 + bit
                s += val
            best = max(best, s)
    return best


def _flipscore_gen(r):
    out = []
    for _ in range(6):
        m, n = r.randint(1, 4), r.randint(1, 4)
        out.append({"grid": [[r.randint(0, 1) for _ in range(n)] for _ in range(m)]})
    return out


def _consecdiff_brute(n, k):
    res = []
    lo, hi = 10 ** (n - 1), 10 ** n
    for num in range(lo, hi):
        s = str(num)
        if all(abs(int(s[i]) - int(s[i + 1])) == k for i in range(len(s) - 1)):
            res.append(num)
    return res


def _consecdiff_gen(r):
    return [{"n": r.randint(2, 5), "k": r.randint(0, 9)} for _ in range(8)]


def _displaytable_brute(orders):
    foods = sorted({o[2] for o in orders})
    tables = sorted({int(o[1]) for o in orders})
    res = [["Table"] + foods]
    for t in tables:
        row = [str(t)]
        for f in foods:
            row.append(str(sum(1 for o in orders if int(o[1]) == t and o[2] == f)))
        res.append(row)
    return res


def _displaytable_gen(r):
    names = ["Ann", "Bob", "Cy", "Di"]
    foodset = ["Soda", "Cake", "Pie", "Tea"]
    out = []
    for _ in range(6):
        orders = []
        for _ in range(r.randint(1, 8)):
            orders.append([r.choice(names), str(r.randint(1, 4)), r.choice(foodset)])
        out.append({"orders": orders})
    return out


def _reaching_brute(sx, sy, tx, ty):
    from collections import deque
    seen = set()
    dq = deque([(sx, sy)])
    while dq:
        x, y = dq.popleft()
        if (x, y) == (tx, ty):
            return True
        if x > tx or y > ty or (x, y) in seen:
            continue
        seen.add((x, y))
        dq.append((x, x + y))
        dq.append((x + y, y))
    return False


def _reaching_gen(r):
    out = []
    for _ in range(8):
        sx, sy = r.randint(1, 4), r.randint(1, 4)
        tx, ty = r.randint(1, 18), r.randint(1, 18)
        out.append({"sx": sx, "sy": sy, "tx": tx, "ty": ty})
    return out


_TTT_LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
              (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def _ttt_brute(board):
    target = "".join(board)
    reachable = set()

    def won(b):
        for p in "XO":
            if any(all(b[i] == p for i in line) for line in _TTT_LINES):
                return p
        return None

    def dfs(b, turn):
        if b in reachable:
            return
        reachable.add(b)
        if won(b) or all(c != " " for c in b):
            return
        for i in range(9):
            if b[i] == " ":
                nb = b[:i] + turn + b[i + 1:]
                dfs(nb, "O" if turn == "X" else "X")

    dfs(" " * 9, "X")
    return target in reachable


def _ttt_gen(r):
    out = []
    for _ in range(8):
        cells = [r.choice([" ", "X", "O"]) for _ in range(9)]
        board = ["".join(cells[0:3]), "".join(cells[3:6]), "".join(cells[6:9])]
        out.append({"board": board})
    return out


def _zigzag_brute(root):
    left, right, val = _build_tree(root)

    def walk(node, godir):
        length = 0
        cur = node
        while cur is not None:
            nxt = left.get(cur) if godir == "L" else right.get(cur)
            godir = "R" if godir == "L" else "L"
            if nxt is None:
                break
            length += 1
            cur = nxt
        return length

    best = 0
    for node in val:
        best = max(best, walk(node, "L"), walk(node, "R"))
    return best


def _zigzag_gen(r):
    return [{"root": _rand_tree_vals(r, r.randint(1, 14), 1, 100)} for _ in range(8)]


def _strongest_brute(arr, k):
    s = sorted(arr)
    m = s[(len(s) - 1) // 2]
    order = sorted(arr, key=lambda x: (abs(x - m), x), reverse=True)
    return order[:k]


def _strongest_gen(r):
    out = []
    for _ in range(6):
        arr = [r.randint(-8, 8) for _ in range(r.randint(1, 12))]
        out.append({"arr": arr, "k": r.randint(1, len(arr))})
    return out


def _tweet_brute(freq, times, startTime, endTime):
    delta = {"minute": 60, "hour": 3600, "day": 86400}[freq]
    res = []
    s = startTime
    while s <= endTime:
        e = min(s + delta, endTime + 1)
        res.append(sum(1 for tm in times if s <= tm < e))
        s += delta
    return res


def _tweet_gen(r):
    out = []
    for _ in range(8):
        freq = r.choice(["minute", "hour", "day"])
        start = r.randint(0, 50)
        end = start + r.randint(0, 200)
        times = [r.randint(0, 300) for _ in range(r.randint(0, 10))]
        out.append({"freq": freq, "times": times, "startTime": start, "endTime": end})
    return out


def _mintime_brute(timePoints):
    mins = [int(t[:2]) * 60 + int(t[3:]) for t in timePoints]
    best = 1440
    for i in range(len(mins)):
        for j in range(i + 1, len(mins)):
            d = abs(mins[i] - mins[j])
            best = min(best, d, 1440 - d)
    return best


def _mintime_gen(r):
    out = []
    for _ in range(8):
        pts = []
        for _ in range(r.randint(2, 8)):
            h, mm = r.randint(0, 23), r.randint(0, 59)
            pts.append(f"{h:02d}:{mm:02d}")
        out.append({"timePoints": pts})
    return out


def _prune_brute(root):
    if not root or root[0] is None:
        return []
    left, right, val = _build_tree(root)

    def keep(node):
        if node is None:
            return False
        kl = keep(left.get(node))
        kr = keep(right.get(node))
        return val[node] == 1 or kl or kr

    if not keep(0):
        return []
    from collections import deque
    out = [val[0]]
    q = deque([0])
    while q:
        node = q.popleft()
        for ch in (left.get(node), right.get(node)):
            if ch is None or not keep(ch):
                out.append(None)
            else:
                out.append(val[ch]); q.append(ch)
    while out and out[-1] is None:
        out.pop()
    return out


def _prune_gen(r):
    return [{"root": _rand_tree_vals_01(r, r.randint(1, 12))} for _ in range(8)]


# =========================================================================== #
# 1. Top K Frequent Words
# =========================================================================== #
add("top-k-frequent-words", "Top K Frequent Words", "medium",
    ["hash-table", "string", "sorting", "heap"], "topKFrequent",
    [("words", "string[]"), ("k", "int")], "str[]",
    """
Given a list of `words` and an integer `k`, return the `k` most frequent words.
The answer must be sorted by frequency from highest to lowest; words with the same
frequency are ordered by their **alphabetical** order (smaller first).

**Examples**
```
words = ["i","love","leetcode","i","love","coding"], k = 2  ->  ["i","love"]
words = ["the","day","is","sunny","the","the","the","sunny","is","is"], k = 4
    ->  ["the","is","sunny","day"]
```

**Constraints:** `1 <= len(words) <= 500`, words are lowercase, `1 <= k <=` number
of distinct words.
""",
    """def topKFrequent(words, k):
    from collections import Counter
    c = Counter(words)
    return sorted(c, key=lambda w: (-c[w], w))[:k]
""",
    visible=[{"words": ["i", "love", "leetcode", "i", "love", "coding"], "k": 2},
             {"words": ["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], "k": 4}],
    hidden=[{"words": ["a"], "k": 1}, {"words": ["b", "a", "b", "a", "c"], "k": 2},
            {"words": ["z", "z", "y", "y", "x"], "k": 3}],
    gen=_topk_words_gen,
    brute=_topk_words_brute,
    checks=[({"words": ["i", "love", "leetcode", "i", "love", "coding"], "k": 2}, ["i", "love"]),
            ({"words": ["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], "k": 4},
             ["the", "is", "sunny", "day"]),
            ({"words": ["b", "a", "b", "a", "c"], "k": 2}, ["a", "b"])],
    source="new_p")


# =========================================================================== #
# 2. Number of Longest Increasing Subsequence
# =========================================================================== #
add("number-of-longest-increasing-subsequence", "Number of Longest Increasing Subsequence",
    "medium", ["array", "dynamic-programming"], "findNumberOfLIS",
    [("nums", "int[]")], "int",
    """
Given an integer array `nums`, return the number of **longest strictly increasing
subsequences**. A subsequence keeps the original order but need not be contiguous.

**Examples**
```
nums = [1,3,5,4,7]   ->  2   (the LIS are [1,3,4,7] and [1,3,5,7])
nums = [2,2,2,2,2]   ->  5   (each single element is an LIS of length 1)
```

**Constraints:** `1 <= len(nums) <= 2000`, the answer fits in a 32-bit integer.
""",
    """def findNumberOfLIS(nums):
    n = len(nums)
    if n == 0:
        return 0
    length = [1] * n
    count = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                if length[j] + 1 > length[i]:
                    length[i] = length[j] + 1
                    count[i] = count[j]
                elif length[j] + 1 == length[i]:
                    count[i] += count[j]
    mx = max(length)
    return sum(c for l, c in zip(length, count) if l == mx)
""",
    visible=[{"nums": [1, 3, 5, 4, 7]}, {"nums": [2, 2, 2, 2, 2]}],
    hidden=[{"nums": [1]}, {"nums": [1, 2, 3, 4]}, {"nums": [3, 2, 1]},
            {"nums": [1, 1, 1, 2, 2, 2, 3, 3, 3]}],
    gen=_nlis_gen,
    brute=_nlis_brute,
    checks=[({"nums": [1, 3, 5, 4, 7]}, 2), ({"nums": [2, 2, 2, 2, 2]}, 5),
            ({"nums": [1, 2, 3, 4]}, 1)],
    source="new_p")


# =========================================================================== #
# 3. Lowest Common Ancestor of Deepest Leaves  (reframed -> value of the LCA)
# =========================================================================== #
add("lowest-common-ancestor-of-deepest-leaves", "Lowest Common Ancestor of Deepest Leaves",
    "medium", ["tree", "depth-first-search"], "lcaDeepestLeaves",
    [("root", "int[]")], "int",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and is rebuilt inside your function. All node values are distinct.

The depth of the root is `0`. The *deepest leaves* are the leaves at the maximum
depth in the tree. Return the **value** of the lowest common ancestor (the deepest
node that has all of the deepest leaves in its subtree) of those deepest leaves.

**Examples**
```
root = [1,2,3]          ->  1   (deepest leaves 2 and 3; their LCA is the root)
root = [1,2,3,4]        ->  4   (the single deepest leaf is its own ancestor)
root = [1,2,3,4,5]      ->  2   (deepest leaves 4 and 5; their LCA is node 2)
```

**Constraints:** `1 <= number of nodes <= 1000`, node values are distinct.
""",
    """def lcaDeepestLeaves(root):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0])
    nid, i, n = 1, 1, len(root)
    while q and i < n:
        cur = q.popleft()
        if i < n:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; left[cur] = nid; q.append(nid); nid += 1
        if i < n:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; right[cur] = nid; q.append(nid); nid += 1

    def dfs(node):
        if node is None:
            return (0, None)
        dl, ln = dfs(left.get(node))
        dr, rn = dfs(right.get(node))
        if dl == dr:
            return (dl + 1, node)
        if dl > dr:
            return (dl + 1, ln)
        return (dr + 1, rn)

    return val[dfs(0)[1]]
""",
    visible=[{"root": [1, 2, 3]}, {"root": [1, 2, 3, 4]}, {"root": [1, 2, 3, 4, 5]}],
    hidden=[{"root": [1]}, {"root": [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]},
            {"root": [10, 20, 30, None, None, 40, 50]}],
    gen=_lca_gen,
    brute=_lca_brute,
    checks=[({"root": [1, 2, 3]}, 1), ({"root": [1, 2, 3, 4]}, 4),
            ({"root": [1, 2, 3, 4, 5]}, 2), ({"root": [1]}, 1)],
    source="new_p")


# =========================================================================== #
# 4. Matrix Block Sum
# =========================================================================== #
add("matrix-block-sum", "Matrix Block Sum", "medium",
    ["array", "matrix", "prefix-sum"], "matrixBlockSum",
    [("mat", "int[][]"), ("k", "int")], "int[][]",
    """
Given an `m x n` matrix `mat` and an integer `k`, return a matrix `answer` where
`answer[i][j]` is the sum of every `mat[r][c]` with `i - k <= r <= i + k`,
`j - k <= c <= j + k`, and `(r, c)` a valid cell of `mat`.

**Examples**
```
mat = [[1,2,3],[4,5,6],[7,8,9]], k = 1  ->  [[12,21,16],[27,45,33],[24,39,28]]
mat = [[1,2,3],[4,5,6],[7,8,9]], k = 2  ->  [[45,45,45],[45,45,45],[45,45,45]]
```

**Constraints:** `1 <= m, n, k <= 100`, `1 <= mat[i][j] <= 100`.
""",
    """def matrixBlockSum(mat, k):
    m, n = len(mat), len(mat[0])
    pre = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            pre[i + 1][j + 1] = mat[i][j] + pre[i][j + 1] + pre[i + 1][j] - pre[i][j]
    out = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            r1, c1 = max(0, i - k), max(0, j - k)
            r2, c2 = min(m - 1, i + k), min(n - 1, j + k)
            out[i][j] = (pre[r2 + 1][c2 + 1] - pre[r1][c2 + 1]
                         - pre[r2 + 1][c1] + pre[r1][c1])
    return out
""",
    visible=[{"mat": [[1, 2, 3], [4, 5, 6], [7, 8, 9]], "k": 1},
             {"mat": [[1, 2, 3], [4, 5, 6], [7, 8, 9]], "k": 2}],
    hidden=[{"mat": [[5]], "k": 0}, {"mat": [[1, 2]], "k": 1},
            {"mat": [[1], [2], [3]], "k": 1}],
    gen=_matblock_gen,
    brute=_matblock_brute,
    checks=[({"mat": [[1, 2, 3], [4, 5, 6], [7, 8, 9]], "k": 1},
             [[12, 21, 16], [27, 45, 33], [24, 39, 28]]),
            ({"mat": [[1, 2, 3], [4, 5, 6], [7, 8, 9]], "k": 2},
             [[45, 45, 45], [45, 45, 45], [45, 45, 45]]),
            ({"mat": [[5]], "k": 0}, [[5]])],
    source="new_p")


# =========================================================================== #
# 5. Smallest Good Base
# =========================================================================== #
add("smallest-good-base", "Smallest Good Base", "hard",
    ["math", "binary-search"], "smallestGoodBase",
    [("n", "string")], "str",
    """
For an integer `n`, a base `k >= 2` is a *good base* if every digit of `n` written
in base `k` equals `1`. Given `n` as a decimal string, return the **smallest** good
base of `n`, also as a string.

If `n` written in base `k` is all ones with `L` digits, then
`n = 1 + k + k^2 + ... + k^(L-1)`. A larger number of digits forces a smaller base,
so the smallest good base comes from the longest all-ones representation.

**Examples**
```
n = "13"                   ->  "3"     (13 = 111 in base 3)
n = "4681"                 ->  "8"     (4681 = 11111 in base 8)
n = "1000000000000000000"  ->  "999999999999999999"   (= 11 in that base)
```

**Constraints:** `3 <= n <= 10^18`.
""",
    """def smallestGoodBase(n):
    num = int(n)
    for length in range(num.bit_length(), 1, -1):
        # length = number of all-ones digits; find base k via binary search
        lo, hi = 2, int(num ** (1.0 / (length - 1))) + 2
        while lo <= hi:
            mid = (lo + hi) // 2
            s, cur, over = 0, 1, False
            for _ in range(length):
                s += cur
                if s > num:
                    over = True
                    break
                cur *= mid
            if not over and s == num:
                return str(mid)
            if over or s > num:
                hi = mid - 1
            else:
                lo = mid + 1
    return str(num - 1)
""",
    visible=[{"n": "13"}, {"n": "4681"}, {"n": "1000000000000000000"}],
    hidden=[{"n": "3"}, {"n": "7"}, {"n": "1000000"}, {"n": "2097151"}],
    checks=[({"n": "13"}, "3"), ({"n": "4681"}, "8"),
            ({"n": "1000000000000000000"}, "999999999999999999"),
            ({"n": "7"}, "2"), ({"n": "3"}, "2"),
            ({"n": "2097151"}, "2")],
    source="new_p")


# =========================================================================== #
# 6. Distant Barcodes  (reframed -> feasibility bool)
# =========================================================================== #
add("distant-barcodes", "Distant Barcodes", "medium",
    ["array", "hash-table", "greedy", "counting"], "canRearrange",
    [("barcodes", "int[]")], "bool",
    """
You are given a list `barcodes`. Return `true` if and only if the barcodes can be
rearranged so that **no two adjacent barcodes are equal** (otherwise `false`).

Such a rearrangement exists exactly when no single value occurs too often: it is
possible iff the most frequent value appears at most `(len(barcodes) + 1) // 2`
times.

**Examples**
```
barcodes = [1,1,1,2,2,2]    ->  true   (e.g. [1,2,1,2,1,2])
barcodes = [1,1,1,1,2,2,3]  ->  false  (value 1 appears 4 > (7+1)//2 = 4? no -> ...)
barcodes = [1,2]            ->  true
```

**Constraints:** `1 <= len(barcodes) <= 10^4`, `1 <= barcodes[i] <= 10^4`.
""",
    """def canRearrange(barcodes):
    from collections import Counter
    n = len(barcodes)
    if n == 0:
        return True
    return max(Counter(barcodes).values()) <= (n + 1) // 2
""",
    visible=[{"barcodes": [1, 1, 1, 2, 2, 2]}, {"barcodes": [1, 1, 1, 1, 2]},
             {"barcodes": [1, 2]}],
    hidden=[{"barcodes": [1]}, {"barcodes": [2, 2, 2, 2]},
            {"barcodes": [1, 1, 2, 3]}, {"barcodes": [5, 5, 5, 6, 6, 6, 7]}],
    gen=_barcode_gen,
    brute=_barcode_brute,
    checks=[({"barcodes": [1, 1, 1, 2, 2, 2]}, True), ({"barcodes": [1, 1, 1, 1, 2]}, False),
            ({"barcodes": [1, 2]}, True), ({"barcodes": [2, 2, 2, 2]}, False)],
    source="new_p")


# =========================================================================== #
# 7. Avoid Flood in The City  (reframed -> feasibility bool)
# =========================================================================== #
add("avoid-flood-in-the-city", "Avoid Flood in The City", "medium",
    ["array", "hash-table", "binary-search", "greedy"], "canAvoidFlood",
    [("rains", "int[]")], "bool",
    """
There are infinitely many lakes, all initially empty. You are given an array
`rains`:

- `rains[i] > 0`: it rains on lake `rains[i]`, filling it. If that lake is already
  full, a flood occurs.
- `rains[i] == 0`: a dry day — you may dry exactly one (any) currently-full lake,
  emptying it.

Return `true` if it is possible to choose the dry-day actions so that **no flood
ever happens**, and `false` otherwise.

**Examples**
```
rains = [1,2,3,4]      ->  true
rains = [1,2,0,0,2,1]  ->  true
rains = [1,2,0,1,2]    ->  false
rains = [10,20,20]     ->  false
```

**Constraints:** `1 <= len(rains) <= 10^5`, `0 <= rains[i] <= 10^9`.
""",
    """def canAvoidFlood(rains):
    import bisect
    full = {}        # lake -> day it was last filled
    dry_days = []    # sorted indices of available dry days
    for i, r in enumerate(rains):
        if r == 0:
            bisect.insort(dry_days, i)
        else:
            if r in full:
                pos = bisect.bisect_right(dry_days, full[r])
                if pos == len(dry_days):
                    return False
                dry_days.pop(pos)
            full[r] = i
    return True
""",
    visible=[{"rains": [1, 2, 3, 4]}, {"rains": [1, 2, 0, 0, 2, 1]},
             {"rains": [1, 2, 0, 1, 2]}, {"rains": [10, 20, 20]}],
    hidden=[{"rains": [0]}, {"rains": [1, 0, 1]}, {"rains": [1, 1]},
            {"rains": [69, 0, 0, 0, 69]}, {"rains": [1, 2, 0, 2, 3, 0, 1]}],
    gen=_flood_gen,
    brute=_flood_brute,
    checks=[({"rains": [1, 2, 3, 4]}, True), ({"rains": [1, 2, 0, 0, 2, 1]}, True),
            ({"rains": [1, 2, 0, 1, 2]}, False), ({"rains": [10, 20, 20]}, False),
            ({"rains": [69, 0, 0, 0, 69]}, True)],
    source="new_p")


# =========================================================================== #
# 8. Smallest Rotation with Highest Score
# =========================================================================== #
add("smallest-rotation-with-highest-score", "Smallest Rotation with Highest Score",
    "hard", ["array", "prefix-sum"], "bestRotation",
    [("nums", "int[]")], "int",
    """
Rotate `nums` by a non-negative integer `K`, producing
`nums[K], nums[K+1], ..., nums[n-1], nums[0], ..., nums[K-1]`. After rotating, any
entry that is **less than or equal to its new index** earns 1 point.

Over all rotations, return the index `K` that yields the highest score. If several
`K` tie, return the **smallest** such `K`.

**Examples**
```
nums = [2,3,1,4,0]  ->  3   (rotation by 3 scores 4, the maximum)
nums = [1,3,0,2,4]  ->  0   (every rotation scores 3, so pick the smallest K)
```

**Constraints:** `1 <= len(nums) <= 2000`, `0 <= nums[i] <= len(nums)`.
""",
    """def bestRotation(nums):
    n = len(nums)
    best_k, best = 0, -1
    for K in range(n):
        score = 0
        for i in range(n):
            if nums[(K + i) % n] <= i:
                score += 1
        if score > best:
            best, best_k = score, K
    return best_k
""",
    visible=[{"nums": [2, 3, 1, 4, 0]}, {"nums": [1, 3, 0, 2, 4]}],
    hidden=[{"nums": [0]}, {"nums": [1, 1]}, {"nums": [0, 0, 0]},
            {"nums": [3, 2, 1, 0]}],
    gen=_bestrot_gen,
    brute=_bestrot_brute,
    checks=[({"nums": [2, 3, 1, 4, 0]}, 3), ({"nums": [1, 3, 0, 2, 4]}, 0),
            ({"nums": [0]}, 0)],
    source="new_p")


# =========================================================================== #
# 9. Reachable Nodes In Subdivided Graph
# =========================================================================== #
add("reachable-nodes-in-subdivided-graph", "Reachable Nodes In Subdivided Graph",
    "hard", ["graph", "shortest-path", "heap"], "reachableNodes",
    [("edges", "int[][]"), ("maxMoves", "int"), ("n", "int")], "int",
    """
Start from an undirected graph with nodes `0..n-1`. Each entry `edges[k] =
[u, v, cnt]` means the edge `(u, v)` is replaced by a chain that inserts `cnt` new
intermediate nodes between `u` and `v` (so the chain has `cnt + 1` unit-length
edges).

Starting at node `0`, each move travels along one unit edge. Return how many nodes
(original **and** newly inserted) are reachable using at most `maxMoves` moves.

**Examples**
```
edges = [[0,1,10],[0,2,1],[1,2,2]], maxMoves = 6, n = 3   ->  13
edges = [[0,1,4],[1,2,6],[0,2,8],[1,3,1]], maxMoves = 10, n = 4   ->  23
```

**Constraints:** `0 <= len(edges) <= 10^4`, `0 <= cnt <= 10^4`,
`0 <= maxMoves <= 10^9`, `1 <= n <= 3000`.
""",
    """def reachableNodes(edges, maxMoves, n):
    import heapq
    graph = [dict() for _ in range(n)]
    for u, v, cnt in edges:
        graph[u][v] = cnt
        graph[v][u] = cnt
    seen = {}                     # node -> max moves left when first settled
    pq = [(-maxMoves, 0)]
    while pq:
        ml, node = heapq.heappop(pq)
        ml = -ml
        if node in seen:
            continue
        seen[node] = ml
        for nei, cnt in graph[node].items():
            rem = ml - cnt - 1
            if nei not in seen and rem >= 0:
                heapq.heappush(pq, (-rem, nei))
    result = len(seen)
    for u, v, cnt in edges:
        a = min(cnt, seen.get(u, 0))
        b = min(cnt, seen.get(v, 0))
        result += min(cnt, a + b)
    return result
""",
    visible=[{"edges": [[0, 1, 10], [0, 2, 1], [1, 2, 2]], "maxMoves": 6, "n": 3},
             {"edges": [[0, 1, 4], [1, 2, 6], [0, 2, 8], [1, 3, 1]], "maxMoves": 10, "n": 4}],
    hidden=[{"edges": [], "maxMoves": 5, "n": 1},
            {"edges": [[0, 1, 0]], "maxMoves": 0, "n": 2},
            {"edges": [[0, 1, 3]], "maxMoves": 2, "n": 2}],
    gen=_reach_gen,
    brute=_reach_brute,
    checks=[({"edges": [[0, 1, 10], [0, 2, 1], [1, 2, 2]], "maxMoves": 6, "n": 3}, 13),
            ({"edges": [[0, 1, 4], [1, 2, 6], [0, 2, 8], [1, 3, 1]], "maxMoves": 10, "n": 4}, 23),
            ({"edges": [], "maxMoves": 5, "n": 1}, 1)],
    source="new_p")


# =========================================================================== #
# 10. Score After Flipping Matrix
# =========================================================================== #
add("score-after-flipping-matrix", "Score After Flipping Matrix", "medium",
    ["array", "greedy", "bit-manipulation", "matrix"], "matrixScore",
    [("grid", "int[][]")], "int",
    """
Given a binary matrix `grid`, a move toggles every value in a chosen row or column
(`0 <-> 1`). After any number of moves, each row is read as a binary number; the
matrix score is the sum of those numbers. Return the highest achievable score.

**Example**
```
grid = [[0,0,1,1],[1,0,1,0],[1,1,0,0]]  ->  39
    (toggle to [[1,1,1,1],[1,0,0,1],[1,1,1,1]] -> 15 + 9 + 15 = 39)
```

**Constraints:** `1 <= m, n <= 20`, every `grid[i][j]` is `0` or `1`.
""",
    """def matrixScore(grid):
    m, n = len(grid), len(grid[0])
    g = [row[:] for row in grid]
    for i in range(m):
        if g[i][0] == 0:
            g[i] = [1 - x for x in g[i]]
    total = 0
    for j in range(n):
        ones = sum(g[i][j] for i in range(m))
        ones = max(ones, m - ones)
        total += ones * (1 << (n - 1 - j))
    return total
""",
    visible=[{"grid": [[0, 0, 1, 1], [1, 0, 1, 0], [1, 1, 0, 0]]}],
    hidden=[{"grid": [[0]]}, {"grid": [[1]]}, {"grid": [[0, 0], [0, 0]]},
            {"grid": [[1, 0, 1], [0, 1, 0]]}],
    gen=_flipscore_gen,
    brute=_flipscore_brute,
    checks=[({"grid": [[0, 0, 1, 1], [1, 0, 1, 0], [1, 1, 0, 0]]}, 39),
            ({"grid": [[0]]}, 1), ({"grid": [[1]]}, 1)],
    source="new_p")


# =========================================================================== #
# 11. Numbers With Same Consecutive Differences
# =========================================================================== #
add("numbers-with-same-consecutive-differences", "Numbers With Same Consecutive Differences",
    "medium", ["backtracking", "breadth-first-search"], "numsSameConsecDiff",
    [("n", "int"), ("k", "int")], "int[]",
    """
Return all non-negative integers of length `n` such that the absolute difference
between every two consecutive digits equals `k`. No number may have a leading zero
(so `01` is invalid, but the single digit `0` would be valid — note `n >= 2` here).
You may return the answer in **any order**.

**Examples**
```
n = 3, k = 7  ->  [181,292,707,818,929]
n = 2, k = 1  ->  [10,12,21,23,32,34,43,45,54,56,65,67,76,78,87,89,98]
n = 2, k = 0  ->  [11,22,33,44,55,66,77,88,99]
```

**Constraints:** `2 <= n <= 9`, `0 <= k <= 9`.
""",
    """def numsSameConsecDiff(n, k):
    res = []

    def dfs(num, length):
        if length == n:
            res.append(num)
            return
        last = num % 10
        for d in {last + k, last - k}:
            if 0 <= d <= 9:
                dfs(num * 10 + d, length + 1)

    for start in range(1, 10):
        dfs(start, 1)
    return res
""",
    visible=[{"n": 3, "k": 7}, {"n": 2, "k": 1}, {"n": 2, "k": 0}],
    hidden=[{"n": 2, "k": 9}, {"n": 4, "k": 0}, {"n": 3, "k": 0}],
    gen=_consecdiff_gen,
    brute=_consecdiff_brute,
    checks=[({"n": 3, "k": 7}, [181, 292, 707, 818, 929]),
            ({"n": 2, "k": 0}, [11, 22, 33, 44, 55, 66, 77, 88, 99]),
            ({"n": 2, "k": 9}, [90])],
    norm=sorted,
    source="new_p")
COMPARE["numbers-with-same-consecutive-differences"] = "unordered"


# =========================================================================== #
# 12. Display Table of Food Orders in a Restaurant
# =========================================================================== #
add("display-table-of-food-orders-in-a-restaurant",
    "Display Table of Food Orders in a Restaurant", "medium",
    ["array", "hash-table", "sorting"], "displayTable",
    [("orders", "string[][]")], "str[][]",
    """
Each entry of `orders` is `[customerName, tableNumber, foodItem]`. Build the
restaurant's display table:

- The first row is a header: `"Table"` followed by every distinct food item in
  **alphabetical order**.
- Each later row starts with a table number and lists how many of each food that
  table ordered, in the same column order as the header.
- Rows are sorted by table number in **numerically increasing** order.

All numbers in the result are returned as strings.

**Example**
```
orders = [["David","3","Ceviche"],["Corina","10","Beef Burrito"],
          ["David","3","Fried Chicken"],["Carla","5","Water"],
          ["Carla","5","Ceviche"],["Rous","3","Ceviche"]]
->  [["Table","Beef Burrito","Ceviche","Fried Chicken","Water"],
     ["3","0","2","1","0"],["5","0","1","0","1"],["10","1","0","0","0"]]
```

**Constraints:** `1 <= len(orders) <= 5*10^4`; table numbers are between `1` and
`500`.
""",
    """def displayTable(orders):
    from collections import defaultdict
    foods = set()
    tables = defaultdict(lambda: defaultdict(int))
    for name, table, food in orders:
        foods.add(food)
        tables[int(table)][food] += 1
    food_list = sorted(foods)
    res = [["Table"] + food_list]
    for t in sorted(tables):
        res.append([str(t)] + [str(tables[t][f]) for f in food_list])
    return res
""",
    visible=[{"orders": [["David", "3", "Ceviche"], ["Corina", "10", "Beef Burrito"],
                         ["David", "3", "Fried Chicken"], ["Carla", "5", "Water"],
                         ["Carla", "5", "Ceviche"], ["Rous", "3", "Ceviche"]]},
             {"orders": [["James", "12", "Fried Chicken"], ["Ratesh", "12", "Fried Chicken"],
                         ["Amadeus", "12", "Fried Chicken"], ["Adam", "1", "Canadian Waffles"],
                         ["Brianna", "1", "Canadian Waffles"]]}],
    hidden=[{"orders": [["Laura", "2", "Bean Burrito"], ["Jhon", "2", "Beef Burrito"],
                        ["Melissa", "2", "Soda"]]},
            {"orders": [["A", "1", "X"]]}],
    gen=_displaytable_gen,
    brute=_displaytable_brute,
    checks=[({"orders": [["David", "3", "Ceviche"], ["Corina", "10", "Beef Burrito"],
                         ["David", "3", "Fried Chicken"], ["Carla", "5", "Water"],
                         ["Carla", "5", "Ceviche"], ["Rous", "3", "Ceviche"]]},
             [["Table", "Beef Burrito", "Ceviche", "Fried Chicken", "Water"],
              ["3", "0", "2", "1", "0"], ["5", "0", "1", "0", "1"], ["10", "1", "0", "0", "0"]]),
            ({"orders": [["A", "1", "X"]]}, [["Table", "X"], ["1", "1"]])],
    source="new_p")


# =========================================================================== #
# 13. Reaching Points
# =========================================================================== #
add("reaching-points", "Reaching Points", "hard", ["math"], "reachingPoints",
    [("sx", "int"), ("sy", "int"), ("tx", "int"), ("ty", "int")], "bool",
    """
A move takes a point `(x, y)` to either `(x, x + y)` or `(x + y, y)`. Given a start
`(sx, sy)` and a target `(tx, ty)`, return `true` if some sequence of moves
transforms the start into the target, and `false` otherwise.

**Examples**
```
sx=1, sy=1, tx=3, ty=5  ->  true   ((1,1)->(1,2)->(3,2)->(3,5))
sx=1, sy=1, tx=2, ty=2  ->  false
sx=1, sy=1, tx=1, ty=1  ->  true
```

**Constraints:** `1 <= sx, sy, tx, ty <= 10^9`.
""",
    """def reachingPoints(sx, sy, tx, ty):
    while tx >= sx and ty >= sy:
        if tx == ty:
            break
        if tx > ty:
            if ty > sy:
                tx %= ty
            else:
                return (tx - sx) % ty == 0
        else:
            if tx > sx:
                ty %= tx
            else:
                return (ty - sy) % tx == 0
    return tx == sx and ty == sy
""",
    visible=[{"sx": 1, "sy": 1, "tx": 3, "ty": 5}, {"sx": 1, "sy": 1, "tx": 2, "ty": 2},
             {"sx": 1, "sy": 1, "tx": 1, "ty": 1}],
    hidden=[{"sx": 2, "sy": 3, "tx": 2, "ty": 3}, {"sx": 1, "sy": 1, "tx": 1, "ty": 6},
            {"sx": 3, "sy": 3, "tx": 12, "ty": 9}],
    gen=_reaching_gen,
    brute=_reaching_brute,
    checks=[({"sx": 1, "sy": 1, "tx": 3, "ty": 5}, True),
            ({"sx": 1, "sy": 1, "tx": 2, "ty": 2}, False),
            ({"sx": 1, "sy": 1, "tx": 1, "ty": 1}, True),
            ({"sx": 1, "sy": 1, "tx": 1, "ty": 6}, True),
            # large boundary: checks bypass the (BFS) brute
            ({"sx": 1, "sy": 1, "tx": 1000000000, "ty": 1}, True),
            ({"sx": 3, "sy": 7, "tx": 999999999, "ty": 7}, False)],
    source="new_p")


# =========================================================================== #
# 14. Valid Tic-Tac-Toe State
# =========================================================================== #
add("valid-tic-tac-toe-state", "Valid Tic-Tac-Toe State", "medium",
    ["array", "string"], "validTicTacToe",
    [("board", "string[]")], "bool",
    """
A Tic-Tac-Toe `board` is a length-3 array of length-3 strings over `' '`, `'X'`,
`'O'`. Return `true` if and only if this position can be reached during a valid
game. `'X'` always moves first, players alternate, marks go only on empty squares,
and the game stops once a row, column, or diagonal is filled with one mark (or the
board is full).

**Examples**
```
board = ["O  ","   ","   "]  ->  false   ('X' must move first)
board = ["XOX"," X ","   "]  ->  false   (too many X's)
board = ["XXX","   ","OOO"]  ->  false   (both cannot win)
board = ["XOX","O O","XOX"]  ->  true
```

**Constraints:** `board` is `3 x 3`; each cell is `' '`, `'X'`, or `'O'`.
""",
    """def validTicTacToe(board):
    b = "".join(board)
    xc, oc = b.count("X"), b.count("O")
    if oc != xc and oc != xc - 1:
        return False
    lines = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6),
             (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]

    def wins(p):
        return any(all(b[i] == p for i in line) for line in lines)

    if wins("X") and xc != oc + 1:
        return False
    if wins("O") and oc != xc:
        return False
    return True
""",
    visible=[{"board": ["O  ", "   ", "   "]}, {"board": ["XOX", " X ", "   "]},
             {"board": ["XXX", "   ", "OOO"]}, {"board": ["XOX", "O O", "XOX"]}],
    hidden=[{"board": ["   ", "   ", "   "]}, {"board": ["X  ", "   ", "   "]},
            {"board": ["XXX", "OO ", "   "]}, {"board": ["XOX", "OXO", "XOX"]}],
    gen=_ttt_gen,
    brute=_ttt_brute,
    checks=[({"board": ["O  ", "   ", "   "]}, False),
            ({"board": ["XOX", " X ", "   "]}, False),
            ({"board": ["XXX", "   ", "OOO"]}, False),
            ({"board": ["XOX", "O O", "XOX"]}, True),
            ({"board": ["   ", "   ", "   "]}, True)],
    source="new_p")


# =========================================================================== #
# 15. Longest ZigZag Path in a Binary Tree
# =========================================================================== #
add("longest-zigzag-path-in-a-binary-tree", "Longest ZigZag Path in a Binary Tree",
    "medium", ["tree", "dynamic-programming", "depth-first-search"], "longestZigZag",
    [("root", "int[]")], "int",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and is rebuilt inside your function. A *zigzag path* starts at any
node and a chosen direction, alternates left/right at each step, and stops when it
cannot move. Its length is the number of nodes visited minus one (a single node has
length `0`). Return the longest zigzag path length in the tree.

**Examples**
```
root = [1]              ->  0
root = [1,2,3]          ->  1
root = [1,2,null,null,3] -> 2   (1 -> left 2 -> right 3)
```

**Constraints:** `1 <= number of nodes <= 5*10^4`.
""",
    """def longestZigZag(root):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0])
    nid, i, n = 1, 1, len(root)
    while q and i < n:
        cur = q.popleft()
        if i < n:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; left[cur] = nid; q.append(nid); nid += 1
        if i < n:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; right[cur] = nid; q.append(nid); nid += 1
    best = [0]

    def dfs(node):
        if node is None:
            return (-1, -1)
        ll = dfs(left.get(node))
        rr = dfs(right.get(node))
        dl = ll[1] + 1   # go left, then continue with the child's right length
        dr = rr[0] + 1   # go right, then continue with the child's left length
        best[0] = max(best[0], dl, dr)
        return (dl, dr)

    dfs(0)
    return best[0]
""",
    visible=[{"root": [1]}, {"root": [1, 2, 3]}, {"root": [1, 2, None, None, 3]}],
    hidden=[{"root": [1, 1, 1, None, 1, None, None, 1, 1, None, 1]},
            {"root": [1, 2, 3, 4, 5, 6, 7]},
            {"root": [1, None, 2, None, 3, None, 4]}],
    gen=_zigzag_gen,
    brute=_zigzag_brute,
    checks=[({"root": [1]}, 0), ({"root": [1, 2, 3]}, 1),
            ({"root": [1, 2, None, None, 3]}, 2),
            ({"root": [1, None, 2, None, 3, None, 4]}, 1)],
    source="new_p")


# =========================================================================== #
# 16. The k Strongest Values in an Array
# =========================================================================== #
add("the-k-strongest-values-in-an-array", "The k Strongest Values in an Array",
    "medium", ["array", "two-pointers", "sorting"], "getStrongest",
    [("arr", "int[]"), ("k", "int")], "int[]",
    """
A value `arr[i]` is *stronger* than `arr[j]` if `|arr[i] - m| > |arr[j] - m|`, where
`m` is the median of `arr`; ties (equal distance to `m`) are broken by the larger
value being stronger. The median is the element at index `(len(arr) - 1) // 2` of
the sorted array.

Return the `k` strongest values, in **any order**.

**Examples**
```
arr = [1,2,3,4,5], k = 2   ->  [5,1]   (median 3)
arr = [1,1,3,5,5], k = 2   ->  [5,5]   (median 3)
arr = [6,-3,7,2,11], k = 3 ->  [11,-3,2]   (median 6; any order accepted)
```

**Constraints:** `1 <= len(arr) <= 10^5`, `-10^5 <= arr[i] <= 10^5`,
`1 <= k <= len(arr)`.
""",
    """def getStrongest(arr, k):
    s = sorted(arr)
    m = s[(len(s) - 1) // 2]
    s.sort(key=lambda x: (abs(x - m), x), reverse=True)
    return s[:k]
""",
    visible=[{"arr": [1, 2, 3, 4, 5], "k": 2}, {"arr": [1, 1, 3, 5, 5], "k": 2},
             {"arr": [6, -3, 7, 2, 11], "k": 3}],
    hidden=[{"arr": [1], "k": 1}, {"arr": [-7, 22, 17, 3], "k": 2},
            {"arr": [6, 7, 11, 7, 6, 8], "k": 5}],
    gen=_strongest_gen,
    brute=_strongest_brute,
    checks=[({"arr": [1, 2, 3, 4, 5], "k": 2}, sorted([5, 1])),
            ({"arr": [1, 1, 3, 5, 5], "k": 2}, sorted([5, 5])),
            ({"arr": [-7, 22, 17, 3], "k": 2}, sorted([22, 17]))],
    norm=sorted,
    source="new_p")
COMPARE["the-k-strongest-values-in-an-array"] = "unordered"


# =========================================================================== #
# 17. Frog Position After T Seconds
# =========================================================================== #
add("frog-position-after-t-seconds", "Frog Position After T Seconds", "hard",
    ["tree", "graph", "breadth-first-search"], "frogPosition",
    [("n", "int"), ("edges", "int[][]"), ("t", "int"), ("target", "int")], "float",
    """
An undirected tree has `n` vertices numbered `1..n`. A frog starts at vertex `1`.
Each second it jumps to an **unvisited** neighbour, chosen uniformly at random among
the unvisited neighbours; if there is no unvisited neighbour it stays in place
forever. Given the tree `edges`, return the probability that after `t` seconds the
frog sits on vertex `target`, **rounded to 5 decimal places**.

**Examples**
```
n = 7, edges = [[1,2],[1,3],[1,7],[2,4],[2,6],[3,5]], t = 2, target = 4  ->  0.16667
n = 7, edges = [[1,2],[1,3],[1,7],[2,4],[2,6],[3,5]], t = 1, target = 7  ->  0.33333
n = 7, edges = [[1,2],[1,3],[1,7],[2,4],[2,6],[3,5]], t = 20, target = 6 ->  0.16667
```

**Constraints:** `1 <= n <= 100`, `edges.length == n - 1`, `1 <= t <= 50`,
`1 <= target <= n`.
""",
    """def frogPosition(n, edges, t, target):
    from collections import defaultdict, deque
    if n == 1:
        return 1.0 if target == 1 else 0.0
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    visited = {1}
    dq = deque([(1, 1.0, 0)])
    while dq:
        node, prob, time = dq.popleft()
        children = [c for c in adj[node] if c not in visited]
        if node == target:
            if time == t or not children:
                return round(prob, 5)
            return 0.0
        if time == t:
            continue
        for c in children:
            visited.add(c)
            dq.append((c, prob / len(children), time + 1))
    return 0.0
""",
    visible=[{"n": 7, "edges": [[1, 2], [1, 3], [1, 7], [2, 4], [2, 6], [3, 5]], "t": 2, "target": 4},
             {"n": 7, "edges": [[1, 2], [1, 3], [1, 7], [2, 4], [2, 6], [3, 5]], "t": 1, "target": 7},
             {"n": 7, "edges": [[1, 2], [1, 3], [1, 7], [2, 4], [2, 6], [3, 5]], "t": 20, "target": 6}],
    hidden=[{"n": 1, "edges": [], "t": 1, "target": 1},
            {"n": 3, "edges": [[1, 2], [1, 3]], "t": 1, "target": 2},
            {"n": 7, "edges": [[1, 2], [1, 3], [1, 7], [2, 4], [2, 6], [3, 5]], "t": 1, "target": 6}],
    checks=[({"n": 7, "edges": [[1, 2], [1, 3], [1, 7], [2, 4], [2, 6], [3, 5]], "t": 2, "target": 4}, 0.16667),
            ({"n": 7, "edges": [[1, 2], [1, 3], [1, 7], [2, 4], [2, 6], [3, 5]], "t": 1, "target": 7}, 0.33333),
            ({"n": 7, "edges": [[1, 2], [1, 3], [1, 7], [2, 4], [2, 6], [3, 5]], "t": 20, "target": 6}, 0.16667),
            ({"n": 1, "edges": [], "t": 1, "target": 1}, 1.0),
            ({"n": 3, "edges": [[1, 2], [1, 3]], "t": 1, "target": 2}, 0.5)],
    source="new_p")


# =========================================================================== #
# 18. Tweet Counts Per Frequency  (reframed -> one tweet's recorded times)
# =========================================================================== #
add("tweet-counts-per-frequency", "Tweet Counts Per Frequency", "medium",
    ["array", "hash-table", "sorting"], "tweetCounts",
    [("freq", "string"), ("times", "int[]"), ("startTime", "int"), ("endTime", "int")], "int[]",
    """
A tweet was recorded at each second in `times`. Given a bucket size `freq`
(`"minute"` = 60s, `"hour"` = 3600s, `"day"` = 86400s) and a window
`[startTime, endTime]`, split the window into consecutive intervals
`[startTime + d*i, startTime + d*(i+1))` (where `d` is the bucket size in seconds),
clipping the final interval at `endTime + 1`. Return the number of recorded times
that fall in each interval, in order.

**Examples**
```
freq="minute", times=[0,60,10], startTime=0, endTime=59   ->  [2]
freq="minute", times=[0,60,10], startTime=0, endTime=60   ->  [2,1]
freq="hour",   times=[0,10,60,120], startTime=0, endTime=210  ->  [4]
```

**Constraints:** `0 <= times[i], startTime, endTime <= 10^9`,
`0 <= endTime - startTime <= 10^4`.
""",
    """def tweetCounts(freq, times, startTime, endTime):
    delta = {"minute": 60, "hour": 3600, "day": 86400}[freq]
    buckets = (endTime - startTime) // delta + 1
    res = [0] * buckets
    for tm in times:
        if startTime <= tm <= endTime:
            res[(tm - startTime) // delta] += 1
    return res
""",
    visible=[{"freq": "minute", "times": [0, 60, 10], "startTime": 0, "endTime": 59},
             {"freq": "minute", "times": [0, 60, 10], "startTime": 0, "endTime": 60},
             {"freq": "hour", "times": [0, 10, 60, 120], "startTime": 0, "endTime": 210}],
    hidden=[{"freq": "day", "times": [], "startTime": 0, "endTime": 100},
            {"freq": "minute", "times": [5, 5, 5], "startTime": 0, "endTime": 0},
            {"freq": "minute", "times": [0, 59, 60, 119], "startTime": 0, "endTime": 119}],
    gen=_tweet_gen,
    brute=_tweet_brute,
    checks=[({"freq": "minute", "times": [0, 60, 10], "startTime": 0, "endTime": 59}, [2]),
            ({"freq": "minute", "times": [0, 60, 10], "startTime": 0, "endTime": 60}, [2, 1]),
            ({"freq": "hour", "times": [0, 10, 60, 120], "startTime": 0, "endTime": 210}, [4]),
            ({"freq": "minute", "times": [0, 59, 60, 119], "startTime": 0, "endTime": 119}, [2, 2])],
    source="new_p")


# =========================================================================== #
# 19. Minimum Time Difference
# =========================================================================== #
add("minimum-time-difference", "Minimum Time Difference", "medium",
    ["array", "math", "string", "sorting"], "findMinDifference",
    [("timePoints", "string[]")], "int",
    """
Given a list of 24-hour clock times as `"HH:MM"` strings, return the smallest number
of minutes between any two of them. The clock is circular, so the gap from `23:59`
to `00:00` is `1` minute.

**Example**
```
timePoints = ["23:59","00:00"]  ->  1
```

**Constraints:** `2 <= len(timePoints) <= 2*10^4`; each time is a valid `"HH:MM"`.
""",
    """def findMinDifference(timePoints):
    mins = sorted(int(t[:2]) * 60 + int(t[3:]) for t in timePoints)
    if len(mins) > 1440:
        return 0
    best = min(b - a for a, b in zip(mins, mins[1:]))
    return min(best, 1440 - mins[-1] + mins[0])
""",
    visible=[{"timePoints": ["23:59", "00:00"]}],
    hidden=[{"timePoints": ["00:00", "23:59", "00:00"]},
            {"timePoints": ["01:01", "02:01", "03:00"]},
            {"timePoints": ["12:00", "00:00"]}],
    gen=_mintime_gen,
    brute=_mintime_brute,
    checks=[({"timePoints": ["23:59", "00:00"]}, 1),
            ({"timePoints": ["00:00", "23:59", "00:00"]}, 0),
            ({"timePoints": ["12:00", "00:00"]}, 720)],
    source="new_p")


# =========================================================================== #
# 20. Binary Tree Pruning  (reframed -> return the pruned tree, serialized)
# =========================================================================== #
add("binary-tree-pruning", "Binary Tree Pruning", "medium",
    ["tree", "depth-first-search"], "pruneTree",
    [("root", "int[]")], "int[]",
    """
A binary tree with values `0`/`1` is given as a LeetCode **level-order array**
(`null`/`None` marks a missing child) and rebuilt inside your function. Remove every
subtree that does not contain a `1` (i.e. a subtree whose nodes are all `0`).

Return the resulting tree as a level-order array (`None` for a missing child, with
trailing `None`s trimmed); return `[]` if the whole tree is removed.

**Examples**
```
root = [1,null,0,0,1]   ->  [1,null,0,null,1]
root = [0]              ->  []
root = [1]              ->  [1]
```

**Constraints:** `1 <= number of nodes <= 200`, each value is `0` or `1`.
""",
    """def pruneTree(root):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0])
    nid, i, n = 1, 1, len(root)
    while q and i < n:
        cur = q.popleft()
        if i < n:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; left[cur] = nid; q.append(nid); nid += 1
        if i < n:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; right[cur] = nid; q.append(nid); nid += 1

    def keep(node):
        if node is None:
            return False
        kl = keep(left.get(node))
        kr = keep(right.get(node))
        if not kl:
            left.pop(node, None)
        if not kr:
            right.pop(node, None)
        return val[node] == 1 or kl or kr

    if not keep(0):
        return []
    out = [val[0]]
    q = deque([0])
    while q:
        node = q.popleft()
        for ch in (left.get(node), right.get(node)):
            if ch is None:
                out.append(None)
            else:
                out.append(val[ch]); q.append(ch)
    while out and out[-1] is None:
        out.pop()
    return out
""",
    visible=[{"root": [1, None, 0, 0, 1]}, {"root": [0]}, {"root": [1]}],
    hidden=[{"root": [0, None, 0, 0, 1]}, {"root": [0, 0, 0]},
            {"root": [1, 0, 1, 0, 0, 0, 1]}, {"root": [1, 1, 1]}],
    gen=_prune_gen,
    brute=_prune_brute,
    checks=[({"root": [1, None, 0, 0, 1]}, [1, None, 0, None, 1]),
            ({"root": [0]}, []), ({"root": [1]}, [1]),
            ({"root": [0, None, 0, 0, 1]}, [0, None, 0, None, 1])],
    source="new_p")
