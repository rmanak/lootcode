"""Batch 021 of the new_p.txt import (20 problems).

Skips recorded in `_skips.py` for this group:
  - `word-ladder-ii` (returns all shortest sequences; the length is the existing
    `word-ladder-length`),
  - `range-sum-query-mutable` (stateful design class).

Reframes:
  - `find-k-pairs-with-smallest-sums` -> return the `k` smallest pair *sums* in
    non-decreasing order (which pairs realise a tied sum is not unique).

`most-frequent-subtree-sum`, `path-sum-ii`, and `delete-nodes-and-return-forest`
allow any output order -> COMPARE "unordered" (with norm=sorted cross-check).

Trees are passed as LeetCode level-order arrays (None for a missing child) and
rebuilt inside each solution; linked lists as arrays of values; boards as list-of-
lists of single-character strings.
"""
from scripts.build_bank import add, COMPARE  # noqa: F401


# --------------------------- shared tree helpers ---------------------------
def _build_tree(vals):
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


def _rand_tree_vals(r, n, lo, hi):
    from collections import deque
    vals = [r.randint(lo, hi)]
    children = {0: [None, None]}
    avail = [(0, 0), (0, 1)]
    created = 1
    while created < n and avail:
        idx = r.randrange(len(avail))
        node, side = avail.pop(idx)
        new_id = len(vals)
        vals.append(r.randint(lo, hi))
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


def _rand_distinct_tree(r, n):
    shape = _rand_tree_vals(r, n, 0, 0)
    vals = list(range(1, sum(1 for x in shape if x is not None) + 1))
    r.shuffle(vals)
    it = iter(vals)
    return [next(it) if x is not None else None for x in shape]


# =========================================================================== #
# brute / reference helpers
# =========================================================================== #
def _subtreesum_brute(root):
    from collections import Counter
    left, right, val = _build_tree(root)
    if not val:
        return []
    counts = Counter()

    def dfs(node):
        s = val[node]
        for ch in (left.get(node), right.get(node)):
            if ch is not None:
                s += dfs(ch)
        counts[s] += 1
        return s

    dfs(0)
    mx = max(counts.values())
    return [s for s, c in counts.items() if c == mx]


def _insuff_brute(root, limit):
    from collections import deque
    left, right, val = _build_tree(root)
    if not val:
        return []
    rootsum = {0: val[0]}
    dq = deque([0])
    while dq:
        nd = dq.popleft()
        for ch in (left.get(nd), right.get(nd)):
            if ch is not None:
                rootsum[ch] = rootsum[nd] + val[ch]; dq.append(ch)
    downmax = {}

    def down(nd):
        l, r = left.get(nd), right.get(nd)
        if l is None and r is None:
            downmax[nd] = val[nd]; return val[nd]
        best = -(10 ** 18)
        if l is not None:
            best = max(best, down(l))
        if r is not None:
            best = max(best, down(r))
        downmax[nd] = val[nd] + best
        return downmax[nd]

    down(0)
    keep = {nd for nd in val if (rootsum[nd] - val[nd]) + downmax[nd] >= limit}
    if 0 not in keep:
        return []
    out = [val[0]]; dq = deque([0])
    while dq:
        nd = dq.popleft()
        for ch in (left.get(nd), right.get(nd)):
            if ch is None or ch not in keep:
                out.append(None)
            else:
                out.append(val[ch]); dq.append(ch)
    while out and out[-1] is None:
        out.pop()
    return out


def _ksym_brute(N, K):
    row = "0"
    for _ in range(N - 1):
        row = "".join("01" if c == "0" else "10" for c in row)
    return int(row[K - 1])


def _ksym_gen(r):
    out = []
    for _ in range(8):
        N = r.randint(1, 11)
        K = r.randint(1, 2 ** (N - 1))
        out.append({"N": N, "K": K})
    return out


def _deepest_brute(root):
    left, right, val = _build_tree(root)
    by_depth = {}

    def dfs(nd, d):
        by_depth.setdefault(d, 0)
        by_depth[d] += val[nd]
        for ch in (left.get(nd), right.get(nd)):
            if ch is not None:
                dfs(ch, d + 1)

    dfs(0, 0)
    return by_depth[max(by_depth)]


def _prison_step(c):
    return [0] + [1 if c[i - 1] == c[i + 1] else 0 for i in range(1, 7)] + [0]


def _prison_brute(cells, N):
    cur = cells[:]
    for _ in range(N):
        cur = _prison_step(cur)
    return cur


def _prison_gen(r):
    return [{"cells": [r.randint(0, 1) for _ in range(8)], "N": r.randint(1, 30)}
            for _ in range(8)]


def _swap_brute(head):
    res = []
    i = 0
    while i < len(head):
        if i + 1 < len(head):
            res.append(head[i + 1]); res.append(head[i]); i += 2
        else:
            res.append(head[i]); i += 1
    return res


def _uniqpaths_gen(r):
    out = []
    for _ in range(5):
        m, n = r.randint(1, 3), r.randint(2, 4)
        cells = [(i, j) for i in range(m) for j in range(n)]
        grid = [[0] * n for _ in range(m)]
        (si, sj), (ei, ej) = r.sample(cells, 2)
        grid[si][sj] = 1; grid[ei][ej] = 2
        rest = [c for c in cells if c not in ((si, sj), (ei, ej))]
        for c in r.sample(rest, min(len(rest), r.randint(0, 2))):
            grid[c[0]][c[1]] = -1
        out.append({"grid": grid})
    return out


def _circle_brute(M):
    n = len(M)
    seen = [False] * n
    circles = 0
    for s in range(n):
        if not seen[s]:
            circles += 1
            stack = [s]; seen[s] = True
            while stack:
                x = stack.pop()
                for y in range(n):
                    if M[x][y] == 1 and not seen[y]:
                        seen[y] = True; stack.append(y)
    return circles


def _circle_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(1, 7)
        M = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if r.random() < 0.3:
                    M[i][j] = M[j][i] = 1
        out.append({"M": M})
    return out


def _addrow_brute(root, v, d):
    left, right, val = _build_tree(root)

    def build(node):
        if node is None:
            return None
        return (val[node], build(left.get(node)), build(right.get(node)))

    tree = build(0) if val else None

    def add(node, depth):
        if depth == 1:
            return (v, node, None)
        if node is None:
            return None
        nv, l, r = node
        if depth == 2:
            return (nv, (v, l, None), (v, None, r))
        return (nv, add(l, depth - 1), add(r, depth - 1))

    res = add(tree, d)
    if res is None:
        return []
    from collections import deque
    out = [res[0]]; q = deque([res])
    while q:
        node = q.popleft()
        for ch in (node[1], node[2]):
            if ch is None:
                out.append(None)
            else:
                out.append(ch[0]); q.append(ch)
    while out and out[-1] is None:
        out.pop()
    return out


def _tree_depth(shape):
    left, right, val = _build_tree(shape)
    if not val:
        return 0

    def depth(nd):
        ch = [c for c in (left.get(nd), right.get(nd)) if c is not None]
        return 1 + (max(depth(c) for c in ch) if ch else 0)

    return depth(0)


def _addrow_gen(r):
    out = []
    for _ in range(6):
        tree = _rand_tree_vals(r, r.randint(1, 10), 1, 30)
        maxd = _tree_depth(tree)
        d = r.randint(1, maxd + 1)
        out.append({"root": tree, "v": r.randint(1, 9), "d": d})
    return out


def _smallrange_brute(nums):
    import itertools
    best = None
    for combo in itertools.product(*nums):
        a, b = min(combo), max(combo)
        if best is None or (b - a < best[1] - best[0]) or \
                (b - a == best[1] - best[0] and a < best[0]):
            best = [a, b]
    return best


def _smallrange_gen(r):
    out = []
    for _ in range(6):
        k = r.randint(2, 4)
        nums = []
        for _ in range(k):
            size = r.randint(1, 4)
            nums.append(sorted(r.randint(-10, 10) for _ in range(size)))
        out.append({"nums": nums})
    return out


def _bottomleft_brute(root):
    left, right, val = _build_tree(root)
    best = [0, val[0]]  # [depth, value]

    def dfs(nd, d):
        if d > best[0]:
            best[0] = d; best[1] = val[nd]
        if left.get(nd) is not None:
            dfs(left[nd], d + 1)
        if right.get(nd) is not None:
            dfs(right[nd], d + 1)

    dfs(0, 0)
    return best[1]


def _pathsum_brute(root, targetSum):
    left, right, val = _build_tree(root)
    if not val:
        return []
    res = []

    def dfs(nd, path):
        path = path + [val[nd]]
        l, r = left.get(nd), right.get(nd)
        if l is None and r is None:
            if sum(path) == targetSum:
                res.append(path)
            return
        if l is not None:
            dfs(l, path)
        if r is not None:
            dfs(r, path)

    dfs(0, [])
    return res


def _pathsum_gen(r):
    out = []
    for _ in range(6):
        tree = _rand_tree_vals(r, r.randint(1, 12), -3, 6)
        out.append({"root": tree, "targetSum": r.randint(-3, 12)})
    return out


def _sudoku_brute(board):
    def dup(cells):
        seen = set()
        for c in cells:
            if c == ".":
                continue
            if c in seen:
                return True
            seen.add(c)
        return False

    for i in range(9):
        if dup(board[i]) or dup([board[r][i] for r in range(9)]):
            return False
    for bi in range(3):
        for bj in range(3):
            cells = [board[bi * 3 + x][bj * 3 + y] for x in range(3) for y in range(3)]
            if dup(cells):
                return False
    return True


def _sudoku_gen(r):
    out = []
    for _ in range(4):
        board = [["." for _ in range(9)] for _ in range(9)]
        for _ in range(r.randint(5, 20)):
            i, j = r.randint(0, 8), r.randint(0, 8)
            board[i][j] = str(r.randint(1, 9))
        out.append({"board": board})
    return out


def _split_brute(root, k):
    n = len(root)
    base, extra = divmod(n, k)
    sizes = [base + 1 if i < extra else base for i in range(k)]
    res = []
    idx = 0
    for sz in sizes:
        res.append(root[idx:idx + sz]); idx += sz
    return res


def _split_gen(r):
    return [{"root": [r.randint(0, 50) for _ in range(r.randint(0, 12))], "k": r.randint(1, 6)}
            for _ in range(8)]


def _xorgame_brute(nums):
    from functools import lru_cache

    def xall(t):
        x = 0
        for v in t:
            x ^= v
        return x

    @lru_cache(maxsize=None)
    def win(state):
        if xall(state) == 0:
            return True
        for i in range(len(state)):
            ns = state[:i] + state[i + 1:]
            if xall(ns) == 0:
                continue
            if not win(ns):
                return True
        return False

    return win(tuple(sorted(nums)))


def _xorgame_gen(r):
    return [{"nums": [r.randint(0, 7) for _ in range(r.randint(1, 6))]} for _ in range(8)]


def _kpairs_brute(nums1, nums2, k):
    sums = sorted(a + b for a in nums1 for b in nums2)
    return sums[:k]


def _kpairs_gen(r):
    out = []
    for _ in range(8):
        a = sorted(r.randint(0, 15) for _ in range(r.randint(1, 5)))
        b = sorted(r.randint(0, 15) for _ in range(r.randint(1, 5)))
        out.append({"nums1": a, "nums2": b, "k": r.randint(1, len(a) * len(b))})
    return out


def _xorq_brute(arr, queries):
    return [(lambda lo, hi: __import__("functools").reduce(lambda x, y: x ^ y, arr[lo:hi + 1], 0))(l, r)
            for l, r in queries]


def _xorq_gen(r):
    out = []
    for _ in range(6):
        arr = [r.randint(1, 30) for _ in range(r.randint(1, 8))]
        queries = []
        for _ in range(r.randint(1, 5)):
            a = r.randint(0, len(arr) - 1)
            b = r.randint(a, len(arr) - 1)
            queries.append([a, b])
        out.append({"arr": arr, "queries": queries})
    return out


def _delnodes_brute(root, to_delete):
    from collections import deque
    left, right, val = _build_tree(root)
    todel = set(to_delete)
    parent = {}
    for nd in list(val):
        for ch in (left.get(nd), right.get(nd)):
            if ch is not None:
                parent[ch] = nd

    def serialize(rid):
        out = [val[rid]]; q = deque([rid])
        while q:
            node = q.popleft()
            for ch in (left.get(node), right.get(node)):
                if ch is None or val[ch] in todel:
                    out.append(None)
                else:
                    out.append(val[ch]); q.append(ch)
        while out and out[-1] is None:
            out.pop()
        return out

    roots = []
    for nd in val:
        if val[nd] in todel:
            continue
        p = parent.get(nd)
        if p is None or val[p] in todel:
            roots.append(nd)
    return [serialize(rid) for rid in roots]


def _delnodes_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(1, 10)
        tree = _rand_distinct_tree(r, n)
        present = [v for v in tree if v is not None]
        todel = r.sample(present, r.randint(0, len(present)))
        out.append({"root": tree, "to_delete": todel})
    return out


def _width_brute(root):
    from collections import deque
    left, right, val = _build_tree(root)
    if not val:
        return 0
    q = deque([(0, 0)])
    best = 0
    while q:
        best = max(best, q[-1][1] - q[0][1] + 1)
        nxt = []
        for node, idx in q:
            if left.get(node) is not None:
                nxt.append((left[node], 2 * idx))
            if right.get(node) is not None:
                nxt.append((right[node], 2 * idx + 1))
        q = deque(nxt)
    return best


def _rand_tree(r):
    return [{"root": _rand_tree_vals(r, r.randint(1, 14), 0, 30)} for _ in range(6)]


# =========================================================================== #
# 1. Most Frequent Subtree Sum
# =========================================================================== #
add("most-frequent-subtree-sum", "Most Frequent Subtree Sum", "medium",
    ["tree", "hash-table", "depth-first-search", "counting"], "findFrequentTreeSum",
    [("root", "int[]")], "int[]",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. The *subtree sum* of a node is the
sum of all values in the subtree rooted at that node. Return all subtree-sum values
that occur most frequently (in **any order**).

**Examples**
```
root = [5,2,-3]   ->  [2,-3,4]   (each sum occurs once)
root = [5,2,-5]   ->  [2]        (sum 2 occurs twice)
```

**Constraints:** `1 <= number of nodes <= 10^4`.
""",
    """def findFrequentTreeSum(root):
    from collections import deque, Counter
    if not root:
        return []
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
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
    counts = Counter()

    def dfs(node):
        s = val[node]
        for ch in (left.get(node), right.get(node)):
            if ch is not None:
                s += dfs(ch)
        counts[s] += 1
        return s

    dfs(0)
    mx = max(counts.values())
    return [s for s, c in counts.items() if c == mx]
""",
    visible=[{"root": [5, 2, -3]}, {"root": [5, 2, -5]}],
    hidden=[{"root": [0]}, {"root": [1, 1, 1]}, {"root": [3, 1, 2]}],
    gen=_rand_tree,
    brute=_subtreesum_brute,
    checks=[({"root": [5, 2, -3]}, sorted([2, -3, 4])), ({"root": [5, 2, -5]}, [2]),
            ({"root": [0]}, [0])],
    norm=sorted,
    source="new_p")
COMPARE["most-frequent-subtree-sum"] = "unordered"


# =========================================================================== #
# 2. Pour Water
# =========================================================================== #
add("pour-water", "Pour Water", "medium", ["array", "simulation"], "pourWater",
    [("heights", "int[]"), ("V", "int"), ("K", "int")], "int[]",
    """
`heights[i]` is the terrain height at index `i` (each column has width 1). Drop `V`
units of water one at a time at index `K`. Each unit settles by the rule: if it can
eventually fall lower by moving left, it moves left to the lowest such position;
otherwise if it can eventually fall lower by moving right, it goes right; otherwise it
rests at `K`. "Level" means terrain height plus any water already there. Return the
final heights (terrain + water) at each index.

**Examples**
```
heights = [2,1,1,2,1,2,2], V = 4, K = 3   ->  [2,2,2,3,2,2,2]
heights = [1,2,3,4], V = 2, K = 2          ->  [2,3,3,4]
heights = [3,1,3], V = 5, K = 1            ->  [4,4,4]
```

**Constraints:** `1 <= len(heights) <= 100`, `0 <= heights[i] <= 99`,
`0 <= V <= 2000`, `0 <= K < len(heights)`.
""",
    """def pourWater(heights, V, K):
    h = heights[:]
    n = len(h)
    for _ in range(V):
        best = K
        i = K
        while i - 1 >= 0 and h[i - 1] <= h[i]:
            i -= 1
            if h[i] < h[best]:
                best = i
        if best != K:
            h[best] += 1
            continue
        i = K
        while i + 1 < n and h[i + 1] <= h[i]:
            i += 1
            if h[i] < h[best]:
                best = i
        h[best] += 1
    return h
""",
    visible=[{"heights": [2, 1, 1, 2, 1, 2, 2], "V": 4, "K": 3},
             {"heights": [1, 2, 3, 4], "V": 2, "K": 2},
             {"heights": [3, 1, 3], "V": 5, "K": 1}],
    hidden=[{"heights": [5], "V": 3, "K": 0}, {"heights": [2, 2], "V": 2, "K": 0},
            {"heights": [1, 1, 1], "V": 0, "K": 1}],
    checks=[({"heights": [2, 1, 1, 2, 1, 2, 2], "V": 4, "K": 3}, [2, 2, 2, 3, 2, 2, 2]),
            ({"heights": [1, 2, 3, 4], "V": 2, "K": 2}, [2, 3, 3, 4]),
            ({"heights": [3, 1, 3], "V": 5, "K": 1}, [4, 4, 4]),
            ({"heights": [5], "V": 3, "K": 0}, [8]),
            ({"heights": [2, 2], "V": 2, "K": 0}, [3, 3])],
    source="new_p")


# =========================================================================== #
# 3. Insufficient Nodes in Root to Leaf Paths
# =========================================================================== #
add("insufficient-nodes-in-root-to-leaf-paths", "Insufficient Nodes in Root to Leaf Paths",
    "medium", ["tree", "depth-first-search"], "sufficientSubset",
    [("root", "int[]"), ("limit", "int")], "int[]",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. A node is *insufficient* if every
root-to-leaf path passing through it has sum **strictly less than** `limit`. Delete
all insufficient nodes simultaneously and return the resulting tree as a level-order
array (`None` for a missing child, trailing `None`s trimmed); return `[]` if the whole
tree is deleted.

**Examples**
```
root = [1,2,3,4,-99,-99,7,8,9,-99,-99,12,13,-99,14], limit = 1
    ->  [1,2,3,4,null,null,7,8,9,null,14]
root = [1,2,-3,-5,null,4,null], limit = -1   ->  [1,null,-3,4]
```

**Constraints:** `1 <= number of nodes <= 5000`, `-10^5 <= value <= 10^5`.
""",
    """def sufficientSubset(root, limit):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
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

    def dfs(node, s):
        if node is None:
            return None
        s += val[node]
        if node not in left and node not in right:
            return node if s >= limit else None
        l = dfs(left.get(node), s)
        r = dfs(right.get(node), s)
        if l is None:
            left.pop(node, None)
        if r is None:
            right.pop(node, None)
        if node not in left and node not in right:
            return None
        return node

    if dfs(0, 0) is None:
        return []
    out = [val[0]]; q = deque([0])
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
    visible=[{"root": [1, 2, 3, 4, -99, -99, 7, 8, 9, -99, -99, 12, 13, -99, 14], "limit": 1},
             {"root": [1, 2, -3, -5, None, 4, None], "limit": -1}],
    hidden=[{"root": [5, 4, 8, 11, None, 17, 4, 7, 1, None, None, 5, 3], "limit": 22},
            {"root": [1], "limit": 2}, {"root": [1], "limit": 0}],
    gen=lambda r: [{"root": _rand_tree_vals(r, r.randint(1, 12), -5, 6), "limit": r.randint(-3, 10)}
                   for _ in range(8)],
    brute=_insuff_brute,
    checks=[({"root": [1, 2, 3, 4, -99, -99, 7, 8, 9, -99, -99, 12, 13, -99, 14], "limit": 1},
             [1, 2, 3, 4, None, None, 7, 8, 9, None, 14]),
            ({"root": [1, 2, -3, -5, None, 4, None], "limit": -1}, [1, None, -3, 4]),
            ({"root": [1], "limit": 2}, [])],
    source="new_p")


# =========================================================================== #
# 4. K-th Symbol in Grammar
# =========================================================================== #
add("k-th-symbol-in-grammar", "K-th Symbol in Grammar", "medium",
    ["math", "bit-manipulation", "recursion"], "kthGrammar",
    [("N", "int"), ("K", "int")], "int",
    """
Row 1 is `0`. Each later row is formed from the previous one by replacing every `0`
with `01` and every `1` with `10`. Given a row number `N` and a **1-indexed** position
`K`, return the symbol at that position.

```
row 1: 0
row 2: 01
row 3: 0110
row 4: 01101001
```

**Examples**
```
N = 1, K = 1  ->  0
N = 2, K = 2  ->  1
N = 4, K = 5  ->  1
```

**Constraints:** `1 <= N <= 30`, `1 <= K <= 2^(N-1)`.
""",
    """def kthGrammar(N, K):
    return bin(K - 1).count("1") & 1
""",
    visible=[{"N": 1, "K": 1}, {"N": 2, "K": 1}, {"N": 2, "K": 2}, {"N": 4, "K": 5}],
    hidden=[{"N": 3, "K": 3}, {"N": 3, "K": 4}, {"N": 5, "K": 16}],
    gen=_ksym_gen,
    brute=_ksym_brute,
    checks=[({"N": 1, "K": 1}, 0), ({"N": 2, "K": 2}, 1), ({"N": 4, "K": 5}, 1),
            ({"N": 30, "K": 2}, 1)],
    source="new_p")


# =========================================================================== #
# 5. Deepest Leaves Sum
# =========================================================================== #
add("deepest-leaves-sum", "Deepest Leaves Sum", "medium",
    ["tree", "breadth-first-search", "depth-first-search"], "deepestLeavesSum",
    [("root", "int[]")], "int",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. Return the sum of the values of the
deepest leaves (the nodes at maximum depth).

**Example**
```
root = [1,2,3,4,5,null,6,7,null,null,null,null,8]   ->  15
```

**Constraints:** `1 <= number of nodes <= 10^4`, `1 <= value <= 100`.
""",
    """def deepestLeavesSum(root):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
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
    q = deque([0])
    s = 0
    while q:
        s = sum(val[x] for x in q)
        nxt = []
        for x in q:
            if left.get(x) is not None:
                nxt.append(left[x])
            if right.get(x) is not None:
                nxt.append(right[x])
        q = deque(nxt)
    return s
""",
    visible=[{"root": [1, 2, 3, 4, 5, None, 6, 7, None, None, None, None, 8]}],
    hidden=[{"root": [1]}, {"root": [1, 2, 3]}, {"root": [5, 4, 6, 3, None, None, 7]}],
    gen=lambda r: [{"root": _rand_tree_vals(r, r.randint(1, 14), 1, 100)} for _ in range(6)],
    brute=_deepest_brute,
    checks=[({"root": [1, 2, 3, 4, 5, None, 6, 7, None, None, None, None, 8]}, 15),
            ({"root": [1]}, 1), ({"root": [1, 2, 3]}, 5)],
    source="new_p")


# =========================================================================== #
# 6. Prison Cells After N Days
# =========================================================================== #
add("prison-cells-after-n-days", "Prison Cells After N Days", "medium",
    ["array", "hash-table", "math", "simulation"], "prisonAfterNDays",
    [("cells", "int[]"), ("N", "int")], "int[]",
    """
There are 8 prison cells in a row (`1` = occupied, `0` = vacant). Each day, a cell
becomes occupied if its two neighbours were both occupied or both vacant, otherwise it
becomes vacant; the two end cells (which lack two neighbours) always become vacant.
Return the state after `N` days.

**Examples**
```
cells = [0,1,0,1,1,0,0,1], N = 7         ->  [0,0,1,1,0,0,0,0]
cells = [1,0,0,1,0,0,1,0], N = 1000000000 ->  [0,0,1,1,1,1,1,0]
```

**Constraints:** `cells.length == 8`, `1 <= N <= 10^9`.
""",
    """def prisonAfterNDays(cells, N):
    def step(c):
        return [0] + [1 if c[i - 1] == c[i + 1] else 0 for i in range(1, 7)] + [0]

    seen = {}
    cur = cells[:]
    day = 0
    while day < N:
        key = tuple(cur)
        if key in seen:
            cycle = day - seen[key]
            for _ in range((N - day) % cycle):
                cur = step(cur)
            return cur
        seen[key] = day
        cur = step(cur)
        day += 1
    return cur
""",
    visible=[{"cells": [0, 1, 0, 1, 1, 0, 0, 1], "N": 7}],
    hidden=[{"cells": [1, 0, 0, 1, 0, 0, 1, 0], "N": 1}, {"cells": [0, 0, 0, 0, 0, 0, 0, 0], "N": 3}],
    gen=_prison_gen,
    brute=_prison_brute,
    checks=[({"cells": [0, 1, 0, 1, 1, 0, 0, 1], "N": 7}, [0, 0, 1, 1, 0, 0, 0, 0]),
            ({"cells": [1, 0, 0, 1, 0, 0, 1, 0], "N": 1000000000}, [0, 0, 1, 1, 1, 1, 1, 0])],
    source="new_p")


# =========================================================================== #
# 7. Swap Nodes in Pairs
# =========================================================================== #
add("swap-nodes-in-pairs", "Swap Nodes in Pairs", "medium",
    ["linked-list", "recursion"], "swapPairs", [("head", "int[]")], "int[]",
    """
A singly linked list is given as an array of its values. Swap every two adjacent
nodes and return the resulting list of values. If the list has an odd length, the last
element stays in place.

**Example**
```
head = [1,2,3,4]   ->  [2,1,4,3]
```

**Constraints:** `0 <= len(head) <= 1000`.
""",
    """def swapPairs(head):
    res = head[:]
    for i in range(0, len(res) - 1, 2):
        res[i], res[i + 1] = res[i + 1], res[i]
    return res
""",
    visible=[{"head": [1, 2, 3, 4]}, {"head": [1, 2, 3]}],
    hidden=[{"head": []}, {"head": [1]}, {"head": [5, 6, 7, 8, 9]}],
    gen=lambda r: [{"head": [r.randint(0, 99) for _ in range(r.randint(0, 12))]} for _ in range(6)],
    brute=_swap_brute,
    checks=[({"head": [1, 2, 3, 4]}, [2, 1, 4, 3]), ({"head": [1, 2, 3]}, [2, 1, 3]),
            ({"head": []}, []), ({"head": [1]}, [1])],
    source="new_p")


# =========================================================================== #
# 8. Unique Paths III
# =========================================================================== #
add("unique-paths-iii", "Unique Paths III", "hard",
    ["array", "backtracking", "matrix"], "uniquePathsIII",
    [("grid", "int[][]")], "int",
    """
On a 2D grid, `1` is the start, `2` is the end, `0` is a walkable empty square, and
`-1` is an obstacle. Return the number of 4-directional walks from the start to the
end that step on **every** non-obstacle square exactly once.

**Examples**
```
grid = [[1,0,0,0],[0,0,0,0],[0,0,2,-1]]   ->  2
grid = [[1,0,0,0],[0,0,0,0],[0,0,0,2]]     ->  4
grid = [[0,1],[2,0]]                        ->  0
```

**Constraints:** `1 <= rows * cols <= 20`.
""",
    """def uniquePathsIII(grid):
    m, n = len(grid), len(grid[0])
    empty = 1
    sr = sc = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 0:
                empty += 1
            elif grid[i][j] == 1:
                sr, sc = i, j

    def dfs(i, j, remaining):
        if grid[i][j] == 2:
            return 1 if remaining == 0 else 0
        if grid[i][j] == -1:
            return 0
        save = grid[i][j]
        grid[i][j] = -1
        total = 0
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + dr, j + dc
            if 0 <= ni < m and 0 <= nj < n:
                total += dfs(ni, nj, remaining - 1)
        grid[i][j] = save
        return total

    return dfs(sr, sc, empty)
""",
    visible=[{"grid": [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 2, -1]]},
             {"grid": [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]]},
             {"grid": [[0, 1], [2, 0]]}],
    hidden=[{"grid": [[1, 2]]}, {"grid": [[1, 0, 2]]}, {"grid": [[1, -1, 2]]},
            {"grid": [[0, 0, 0], [0, 1, 0], [0, 0, 2]]}],
    gen=_uniqpaths_gen,
    checks=[({"grid": [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 2, -1]]}, 2),
            ({"grid": [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 2]]}, 4),
            ({"grid": [[0, 1], [2, 0]]}, 0), ({"grid": [[1, 2]]}, 1),
            ({"grid": [[1, -1, 2]]}, 0)],
    source="new_p")


# =========================================================================== #
# 9. Friend Circles
# =========================================================================== #
add("friend-circles", "Friend Circles", "medium",
    ["graph", "union-find", "depth-first-search"], "findCircleNum",
    [("M", "int[][]")], "int",
    """
There are `n` students. `M` is an `n x n` matrix where `M[i][j] == 1` means students
`i` and `j` are direct friends (`M` is symmetric with `1`s on the diagonal).
Friendship is transitive: a *friend circle* is a maximal group of directly or
indirectly connected students. Return the number of friend circles.

**Examples**
```
M = [[1,1,0],[1,1,0],[0,0,1]]   ->  2
M = [[1,0,0],[0,1,0],[0,0,1]]   ->  3
```

**Constraints:** `1 <= n <= 200`, `M[i][j]` is `0` or `1`, `M[i][i] == 1`,
`M[i][j] == M[j][i]`.
""",
    """def findCircleNum(M):
    n = len(M)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if M[i][j] == 1:
                parent[find(i)] = find(j)
    return len({find(i) for i in range(n)})
""",
    visible=[{"M": [[1, 1, 0], [1, 1, 0], [0, 0, 1]]},
             {"M": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}],
    hidden=[{"M": [[1]]}, {"M": [[1, 1], [1, 1]]},
            {"M": [[1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1]]}],
    gen=_circle_gen,
    brute=_circle_brute,
    checks=[({"M": [[1, 1, 0], [1, 1, 0], [0, 0, 1]]}, 2),
            ({"M": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}, 3),
            ({"M": [[1, 1], [1, 1]]}, 1)],
    source="new_p")


# =========================================================================== #
# 10. Add One Row to Tree
# =========================================================================== #
add("add-one-row-to-tree", "Add One Row to Tree", "medium",
    ["tree", "depth-first-search", "breadth-first-search"], "addOneRow",
    [("root", "int[]"), ("v", "int"), ("d", "int")], "int[]",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. The root is at depth `1`. Insert a
new row of nodes all holding value `v` at depth `d`: for every node `N` at depth
`d-1`, `N`'s original left subtree becomes the left subtree of a new left child
(value `v`), and `N`'s original right subtree becomes the right subtree of a new right
child (value `v`). If `d == 1`, a new root with value `v` is created whose left child
is the original tree. Return the new tree as a level-order array.

**Examples**
```
root = [4,2,6,3,1,5], v = 1, d = 2   ->  [4,1,1,2,null,null,6,3,1,5]
root = [4,2,null,3,1], v = 1, d = 3  ->  [4,2,null,1,1,3,null,null,1]
```

**Constraints:** `1 <= number of nodes`; `1 <= d <= (tree depth) + 1`.
""",
    """def addOneRow(root, v, d):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
    while q and i < n:
        cur = q.popleft()
        if i < n:
            x = root[i]; i += 1
            if x is not None:
                val[nid] = x; left[cur] = nid; q.append(nid); nid += 1
        if i < n:
            x = root[i]; i += 1
            if x is not None:
                val[nid] = x; right[cur] = nid; q.append(nid); nid += 1
    counter = [max(val) + 1]

    def fresh(value):
        node = counter[0]; counter[0] += 1; val[node] = value
        return node

    if d == 1:
        nr = fresh(v); left[nr] = 0
        rootid = nr
    else:
        level = [0]; depth = 1
        while depth < d - 1:
            nxt = []
            for x in level:
                if left.get(x) is not None:
                    nxt.append(left[x])
                if right.get(x) is not None:
                    nxt.append(right[x])
            level = nxt; depth += 1
        for x in level:
            old_l, old_r = left.get(x), right.get(x)
            nl = fresh(v); nrr = fresh(v)
            left[x] = nl; right[x] = nrr
            if old_l is not None:
                left[nl] = old_l
            if old_r is not None:
                right[nrr] = old_r
        rootid = 0
    out = [val[rootid]]; q = deque([rootid])
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
    visible=[{"root": [4, 2, 6, 3, 1, 5], "v": 1, "d": 2},
             {"root": [4, 2, None, 3, 1], "v": 1, "d": 3}],
    hidden=[{"root": [1, 2, 3], "v": 5, "d": 1}, {"root": [1], "v": 2, "d": 2},
            {"root": [1, 2, 3, 4], "v": 9, "d": 2}],
    gen=_addrow_gen,
    brute=_addrow_brute,
    checks=[({"root": [4, 2, 6, 3, 1, 5], "v": 1, "d": 2},
             [4, 1, 1, 2, None, None, 6, 3, 1, 5]),
            ({"root": [4, 2, None, 3, 1], "v": 1, "d": 3}, [4, 2, None, 1, 1, 3, None, None, 1]),
            ({"root": [1, 2, 3], "v": 5, "d": 1}, [5, 1, None, 2, 3])],
    source="new_p")


# =========================================================================== #
# 11. Smallest Range Covering Elements from K Lists
# =========================================================================== #
add("smallest-range", "Smallest Range Covering Elements from K Lists", "hard",
    ["array", "heap", "sliding-window", "sorting"], "smallestRange",
    [("nums", "int[][]")], "int[]",
    """
You have `k` lists of integers, each sorted in non-decreasing order. Find the smallest
range `[a, b]` that includes **at least one** number from each of the `k` lists.
Range `[a, b]` is smaller than `[c, d]` if `b - a < d - c`, or `b - a == d - c` and
`a < c`. Return the range as `[a, b]`.

**Example**
```
nums = [[4,10,15,24,26],[0,9,12,20],[5,18,22,30]]   ->  [20,24]
```

**Constraints:** `1 <= k`; each list is non-decreasing; values fit in `int`.
""",
    """def smallestRange(nums):
    import heapq
    heap = [(lst[0], i, 0) for i, lst in enumerate(nums)]
    heapq.heapify(heap)
    cur_max = max(lst[0] for lst in nums)
    best = [heap[0][0], cur_max]
    while True:
        mn, i, j = heapq.heappop(heap)
        if (cur_max - mn < best[1] - best[0] or
                (cur_max - mn == best[1] - best[0] and mn < best[0])):
            best = [mn, cur_max]
        if j + 1 == len(nums[i]):
            break
        nxt = nums[i][j + 1]
        cur_max = max(cur_max, nxt)
        heapq.heappush(heap, (nxt, i, j + 1))
    return best
""",
    visible=[{"nums": [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]}],
    hidden=[{"nums": [[1], [2], [3]]}, {"nums": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]},
            {"nums": [[10, 10], [11, 11]]}],
    gen=_smallrange_gen,
    brute=_smallrange_brute,
    checks=[({"nums": [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]}, [20, 24]),
            ({"nums": [[1], [2], [3]]}, [1, 3]),
            ({"nums": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}, [1, 1])],
    source="new_p")


# =========================================================================== #
# 12. Find Bottom Left Tree Value
# =========================================================================== #
add("find-bottom-left-tree-value", "Find Bottom Left Tree Value", "medium",
    ["tree", "breadth-first-search", "depth-first-search"], "findBottomLeftValue",
    [("root", "int[]")], "int",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. Return the leftmost value in the
**last** (deepest) row of the tree.

**Examples**
```
root = [2,1,3]                          ->  1
root = [1,2,3,4,null,5,6,null,null,7]   ->  7
```

**Constraints:** `1 <= number of nodes <= 10^4`.
""",
    """def findBottomLeftValue(root):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
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
    q = deque([0])
    leftmost = val[0]
    while q:
        leftmost = val[q[0]]
        nxt = []
        for x in q:
            if left.get(x) is not None:
                nxt.append(left[x])
            if right.get(x) is not None:
                nxt.append(right[x])
        q = deque(nxt)
    return leftmost
""",
    visible=[{"root": [2, 1, 3]}, {"root": [1, 2, 3, 4, None, 5, 6, None, None, 7]}],
    hidden=[{"root": [1]}, {"root": [1, 2]}, {"root": [3, 1, 2]}],
    gen=lambda r: [{"root": _rand_tree_vals(r, r.randint(1, 14), 0, 50)} for _ in range(6)],
    brute=_bottomleft_brute,
    checks=[({"root": [2, 1, 3]}, 1),
            ({"root": [1, 2, 3, 4, None, 5, 6, None, None, 7]}, 7), ({"root": [1]}, 1)],
    source="new_p")


# =========================================================================== #
# 13. Path Sum II
# =========================================================================== #
add("path-sum-ii", "Path Sum II", "medium",
    ["tree", "backtracking", "depth-first-search"], "pathSum",
    [("root", "int[]"), ("targetSum", "int")], "int[][]",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. Return all root-to-leaf paths whose
node values sum to `targetSum`. Each path lists node values from root to leaf; the
paths may be returned in **any order**.

**Example**
```
root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22
    ->  [[5,4,11,2],[5,8,4,5]]
```

**Constraints:** `0 <= number of nodes <= 5000`.
""",
    """def pathSum(root, targetSum):
    if not root:
        return []
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
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
    res = []

    def dfs(node, remaining, path):
        v = val[node]
        path.append(v)
        l, r = left.get(node), right.get(node)
        if l is None and r is None and remaining == v:
            res.append(path[:])
        else:
            if l is not None:
                dfs(l, remaining - v, path)
            if r is not None:
                dfs(r, remaining - v, path)
        path.pop()

    dfs(0, targetSum, [])
    return res
""",
    visible=[{"root": [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], "targetSum": 22}],
    hidden=[{"root": [1, 2, 3], "targetSum": 5}, {"root": [1, 2], "targetSum": 3},
            {"root": [1, 2], "targetSum": 0}, {"root": [], "targetSum": 0}],
    gen=_pathsum_gen,
    brute=_pathsum_brute,
    checks=[({"root": [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1], "targetSum": 22},
             sorted([[5, 4, 11, 2], [5, 8, 4, 5]])),
            ({"root": [1, 2], "targetSum": 3}, [[1, 2]]),
            ({"root": [1, 2], "targetSum": 0}, [])],
    norm=sorted,
    source="new_p")
COMPARE["path-sum-ii"] = "unordered"


# =========================================================================== #
# 14. Valid Sudoku
# =========================================================================== #
add("valid-sudoku", "Valid Sudoku", "medium",
    ["array", "hash-table", "matrix"], "isValidSudoku",
    [("board", "string[][]")], "bool",
    """
Determine whether a `9 x 9` Sudoku board is valid. Only the filled cells need to be
checked: each row, each column, and each of the nine `3 x 3` sub-boxes must contain
the digits `1-9` without repetition. Empty cells hold `'.'`. The board need not be
solvable.

**Example**
```
A board with no repeated digit in any row, column, or box  ->  true
The same board with a duplicate inside one 3x3 box          ->  false
```

**Constraints:** the board is `9 x 9`; each cell is a digit `'1'`-`'9'` or `'.'`.
""",
    """def isValidSudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for i in range(9):
        for j in range(9):
            c = board[i][j]
            if c == ".":
                continue
            b = (i // 3) * 3 + j // 3
            if c in rows[i] or c in cols[j] or c in boxes[b]:
                return False
            rows[i].add(c); cols[j].add(c); boxes[b].add(c)
    return True
""",
    visible=[{"board": [["5", "3", ".", ".", "7", ".", ".", ".", "."],
                        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
                        [".", "9", "8", ".", ".", ".", ".", "6", "."],
                        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
                        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
                        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
                        [".", "6", ".", ".", ".", ".", "2", "8", "."],
                        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
                        [".", ".", ".", ".", "8", ".", ".", "7", "9"]]},
             {"board": [["8", "3", ".", ".", "7", ".", ".", ".", "."],
                        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
                        [".", "9", "8", ".", ".", ".", ".", "6", "."],
                        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
                        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
                        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
                        [".", "6", ".", ".", ".", ".", "2", "8", "."],
                        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
                        [".", ".", ".", ".", "8", ".", ".", "7", "9"]]}],
    hidden=[{"board": [["." for _ in range(9)] for _ in range(9)]}],
    gen=_sudoku_gen,
    brute=_sudoku_brute,
    checks=[({"board": [["5", "3", ".", ".", "7", ".", ".", ".", "."],
                        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
                        [".", "9", "8", ".", ".", ".", ".", "6", "."],
                        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
                        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
                        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
                        [".", "6", ".", ".", ".", ".", "2", "8", "."],
                        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
                        [".", ".", ".", ".", "8", ".", ".", "7", "9"]]}, True),
            ({"board": [["8", "3", ".", ".", "7", ".", ".", ".", "."],
                        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
                        [".", "9", "8", ".", ".", ".", ".", "6", "."],
                        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
                        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
                        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
                        [".", "6", ".", ".", ".", ".", "2", "8", "."],
                        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
                        [".", ".", ".", ".", "8", ".", ".", "7", "9"]]}, False)],
    source="new_p")


# =========================================================================== #
# 15. Split Linked List in Parts
# =========================================================================== #
add("split-linked-list-in-parts", "Split Linked List in Parts", "medium",
    ["linked-list"], "splitListToParts", [("root", "int[]"), ("k", "int")], "int[][]",
    """
A singly linked list is given as an array of values `root`. Split it into `k`
consecutive parts whose sizes differ by at most one, with earlier parts being at least
as large as later parts. Some parts may be empty. Return the list of parts (each as an
array of values; an empty part is `[]`).

**Examples**
```
root = [1,2,3], k = 5                     ->  [[1],[2],[3],[],[]]
root = [1,2,3,4,5,6,7,8,9,10], k = 3      ->  [[1,2,3,4],[5,6,7],[8,9,10]]
```

**Constraints:** `0 <= len(root) <= 1000`, `1 <= k <= 50`.
""",
    """def splitListToParts(root, k):
    n = len(root)
    base, extra = divmod(n, k)
    res = []
    idx = 0
    for i in range(k):
        size = base + (1 if i < extra else 0)
        res.append(root[idx:idx + size])
        idx += size
    return res
""",
    visible=[{"root": [1, 2, 3], "k": 5},
             {"root": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "k": 3}],
    hidden=[{"root": [], "k": 3}, {"root": [1], "k": 1}, {"root": [1, 2, 3, 4, 5], "k": 2}],
    gen=_split_gen,
    brute=_split_brute,
    checks=[({"root": [1, 2, 3], "k": 5}, [[1], [2], [3], [], []]),
            ({"root": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "k": 3},
             [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10]]),
            ({"root": [], "k": 3}, [[], [], []])],
    source="new_p")


# =========================================================================== #
# 16. Chalkboard XOR Game
# =========================================================================== #
add("chalkboard-xor-game", "Chalkboard XOR Game", "hard",
    ["array", "math", "bit-manipulation", "game-theory"], "xorGame",
    [("nums", "int[]")], "bool",
    """
Numbers `nums` are written on a chalkboard. Alice and Bob alternately erase exactly
one number, Alice first. If erasing a number makes the XOR of all remaining numbers
equal to `0`, the player who erased it **loses**. If the XOR of all numbers is already
`0` at the start of a player's turn, that player **wins**. Return `true` if and only
if Alice wins with optimal play.

**Example**
```
nums = [1,1,2]   ->  false
```

**Constraints:** `1 <= len(nums) <= 1000`, `0 <= nums[i] < 2^16`.
""",
    """def xorGame(nums):
    x = 0
    for v in nums:
        x ^= v
    return x == 0 or len(nums) % 2 == 0
""",
    visible=[{"nums": [1, 1, 2]}, {"nums": [1, 1]}, {"nums": [1, 2, 3]}],
    hidden=[{"nums": [0]}, {"nums": [1]}, {"nums": [1, 2, 4, 7]}, {"nums": [5, 5, 5]}],
    gen=_xorgame_gen,
    brute=_xorgame_brute,
    checks=[({"nums": [1, 1, 2]}, False), ({"nums": [1, 1]}, True),
            ({"nums": [1, 2, 3]}, True), ({"nums": [0]}, True), ({"nums": [1]}, False)],
    source="new_p")


# =========================================================================== #
# 17. Find K Pairs with Smallest Sums  (reframed -> the k smallest pair sums)
# =========================================================================== #
add("find-k-pairs-with-smallest-sums", "Find K Pairs with Smallest Sums", "medium",
    ["array", "heap"], "kSmallestPairs",
    [("nums1", "int[]"), ("nums2", "int[]"), ("k", "int")], "int[]",
    """
Given two ascending integer arrays `nums1` and `nums2` and an integer `k`, consider
all pairs `(u, v)` with `u` from `nums1` and `v` from `nums2`. Return the `k` smallest
**pair sums** `u + v`, listed in non-decreasing order. (If fewer than `k` pairs exist,
return all of them.)

**Examples**
```
nums1 = [1,7,11], nums2 = [2,4,6], k = 3   ->  [3,5,7]
nums1 = [1,1,2], nums2 = [1,2,3], k = 2     ->  [2,2]
```

**Constraints:** `1 <= len(nums1), len(nums2)`, both ascending, `1 <= k`.
""",
    """def kSmallestPairs(nums1, nums2, k):
    import heapq
    if not nums1 or not nums2:
        return []
    res = []
    heap = [(nums1[0] + nums2[0], 0, 0)]
    visited = {(0, 0)}
    while heap and len(res) < k:
        s, i, j = heapq.heappop(heap)
        res.append(s)
        if i + 1 < len(nums1) and (i + 1, j) not in visited:
            visited.add((i + 1, j))
            heapq.heappush(heap, (nums1[i + 1] + nums2[j], i + 1, j))
        if j + 1 < len(nums2) and (i, j + 1) not in visited:
            visited.add((i, j + 1))
            heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))
    return res
""",
    visible=[{"nums1": [1, 7, 11], "nums2": [2, 4, 6], "k": 3},
             {"nums1": [1, 1, 2], "nums2": [1, 2, 3], "k": 2}],
    hidden=[{"nums1": [1, 2], "nums2": [3], "k": 3}, {"nums1": [1], "nums2": [1], "k": 1},
            {"nums1": [1, 1, 2], "nums2": [1, 2, 3], "k": 100}],
    gen=_kpairs_gen,
    brute=_kpairs_brute,
    checks=[({"nums1": [1, 7, 11], "nums2": [2, 4, 6], "k": 3}, [3, 5, 7]),
            ({"nums1": [1, 1, 2], "nums2": [1, 2, 3], "k": 2}, [2, 2]),
            ({"nums1": [1, 2], "nums2": [3], "k": 3}, [4, 5])],
    source="new_p")


# =========================================================================== #
# 18. XOR Queries of a Subarray
# =========================================================================== #
add("xor-queries-of-a-subarray", "XOR Queries of a Subarray", "medium",
    ["array", "bit-manipulation", "prefix-sum"], "xorQueries",
    [("arr", "int[]"), ("queries", "int[][]")], "int[]",
    """
Given an array `arr` of positive integers and a list of `queries` where
`queries[i] = [L, R]`, return for each query the XOR of `arr[L], arr[L+1], ...,
arr[R]`.

**Examples**
```
arr = [1,3,4,8], queries = [[0,1],[1,2],[0,3],[3,3]]   ->  [2,7,14,8]
arr = [4,8,2,10], queries = [[2,3],[1,3],[0,0],[0,3]]  ->  [8,0,4,4]
```

**Constraints:** `1 <= len(arr) <= 3*10^4`, `0 <= L <= R < len(arr)`.
""",
    """def xorQueries(arr, queries):
    pre = [0]
    for x in arr:
        pre.append(pre[-1] ^ x)
    return [pre[r + 1] ^ pre[l] for l, r in queries]
""",
    visible=[{"arr": [1, 3, 4, 8], "queries": [[0, 1], [1, 2], [0, 3], [3, 3]]},
             {"arr": [4, 8, 2, 10], "queries": [[2, 3], [1, 3], [0, 0], [0, 3]]}],
    hidden=[{"arr": [1], "queries": [[0, 0]]},
            {"arr": [7, 7, 7, 7], "queries": [[0, 1], [0, 3]]}],
    gen=_xorq_gen,
    brute=_xorq_brute,
    checks=[({"arr": [1, 3, 4, 8], "queries": [[0, 1], [1, 2], [0, 3], [3, 3]]}, [2, 7, 14, 8]),
            ({"arr": [4, 8, 2, 10], "queries": [[2, 3], [1, 3], [0, 0], [0, 3]]}, [8, 0, 4, 4]),
            ({"arr": [7, 7, 7, 7], "queries": [[0, 1], [0, 3]]}, [0, 0])],
    source="new_p")


# =========================================================================== #
# 19. Delete Nodes And Return Forest
# =========================================================================== #
add("delete-nodes-and-return-forest", "Delete Nodes And Return Forest", "medium",
    ["tree", "depth-first-search"], "delNodes",
    [("root", "int[]"), ("to_delete", "int[]")], "int[][]",
    """
A binary tree with distinct node values is given as a LeetCode **level-order array**
(`null`/`None` marks a missing child) and rebuilt inside your function. After deleting
every node whose value is in `to_delete`, the tree breaks into a forest. Return the
roots of the remaining trees, each serialized as a level-order array (`None` for a
missing child, trailing `None`s trimmed). The trees may be returned in **any order**.

**Example**
```
root = [1,2,3,4,5,6,7], to_delete = [3,5]   ->  [[1,2,null,4],[6],[7]]
```

**Constraints:** `1 <= number of nodes <= 1000`, distinct values in `1..1000`.
""",
    """def delNodes(root, to_delete):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
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
    todel = set(to_delete)
    roots = []

    def dfs(node, is_root):
        if node is None:
            return None
        deleted = val[node] in todel
        if is_root and not deleted:
            roots.append(node)
        l = dfs(left.get(node), deleted)
        r = dfs(right.get(node), deleted)
        if l is None:
            left.pop(node, None)
        else:
            left[node] = l
        if r is None:
            right.pop(node, None)
        else:
            right[node] = r
        return None if deleted else node

    dfs(0, True)

    def serialize(rid):
        out = [val[rid]]; q2 = deque([rid])
        while q2:
            node = q2.popleft()
            for ch in (left.get(node), right.get(node)):
                if ch is None:
                    out.append(None)
                else:
                    out.append(val[ch]); q2.append(ch)
        while out and out[-1] is None:
            out.pop()
        return out

    return [serialize(rid) for rid in roots]
""",
    visible=[{"root": [1, 2, 3, 4, 5, 6, 7], "to_delete": [3, 5]}],
    hidden=[{"root": [1, 2, 3], "to_delete": [1]}, {"root": [1], "to_delete": [1]},
            {"root": [1, 2, 3], "to_delete": []}],
    gen=_delnodes_gen,
    brute=_delnodes_brute,
    checks=[({"root": [1, 2, 3, 4, 5, 6, 7], "to_delete": [3, 5]},
             sorted([[1, 2, None, 4], [6], [7]])),
            ({"root": [1, 2, 3], "to_delete": [1]}, sorted([[2], [3]])),
            ({"root": [1], "to_delete": [1]}, [])],
    norm=sorted,
    source="new_p")
COMPARE["delete-nodes-and-return-forest"] = "unordered"


# =========================================================================== #
# 20. Maximum Width of Binary Tree
# =========================================================================== #
add("maximum-width-of-binary-tree", "Maximum Width of Binary Tree", "medium",
    ["tree", "breadth-first-search", "depth-first-search"], "widthOfBinaryTree",
    [("root", "int[]")], "int",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. The width of a level is the distance
between its leftmost and rightmost non-null nodes, counting the (possibly null)
positions a full binary tree would place between them. Return the maximum width over
all levels.

**Examples**
```
root = [1,3,2,5,3,null,9]                       ->  4
root = [1,3,2,5,null,null,9,6,null,null,7]      ->  8
```

**Constraints:** `1 <= number of nodes <= 3000`; the answer fits in a 32-bit integer.
""",
    """def widthOfBinaryTree(root):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
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
    q = deque([(0, 0)])
    best = 0
    while q:
        best = max(best, q[-1][1] - q[0][1] + 1)
        nxt = []
        for node, idx in q:
            if left.get(node) is not None:
                nxt.append((left[node], 2 * idx))
            if right.get(node) is not None:
                nxt.append((right[node], 2 * idx + 1))
        q = deque(nxt)
    return best
""",
    visible=[{"root": [1, 3, 2, 5, 3, None, 9]},
             {"root": [1, 3, 2, 5, None, None, 9, 6, None, None, 7]}],
    hidden=[{"root": [1]}, {"root": [1, 3, None, 5, 3]}, {"root": [1, 3, 2, 5]}],
    gen=_rand_tree,
    brute=_width_brute,
    checks=[({"root": [1, 3, 2, 5, 3, None, 9]}, 4),
            ({"root": [1, 3, 2, 5, None, None, 9, 6, None, None, 7]}, 8),
            ({"root": [1]}, 1)],
    source="new_p")
