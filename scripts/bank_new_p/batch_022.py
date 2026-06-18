"""Batch 022 of the new_p.txt import (20 problems).

Skips recorded in `_skips.py` for this group:
  - `find-a-corresponding-node-of-a-binary-tree-in-a-clone-of-that-tree`
    (returns a node *pointer* in a clone -- meaningless in our array repr),
  - `sort-list` (sorting a linked list, reframed to an array, is the existing
    `sort-an-array`),
  - `course-schedule-ii` (lexicographically-smallest topo order is the existing
    `course-schedule-ordering`; "can finish" is `course-schedule`),
  - `time-based-key-value-store` (== existing `time-based-kv-store`),
  - `dinner-plate-stacks` (stateful design class),
  - `mini-parser` (deserialize a NestedInteger codec).

Reframes:
  - `largest-divisible-subset` -> return the SIZE of the largest divisible subset
    (LeetCode asks for "any" such subset, not single-answer gradable).
  - `prefix-and-suffix-search` -> batch `WordFilter.f` queries: given the word list
    and a list of `[prefix, suffix]` queries, return one answer per query.
  - `stamping-the-sequence` -> feasibility bool `canStamp` (LeetCode returns "any"
    valid stamp order).
  - `apply-discount-every-n-orders` -> batch `getBill` calls (the `Cashier` state is
    just the running customer count); float bills rounded to 5 decimals.

`invalid-transactions` allows any output order -> COMPARE "unordered" (norm=sorted).

Trees are passed as LeetCode level-order arrays (None for a missing child) and rebuilt
inside each solution; linked lists as arrays of values; grids as rectangular int[][].
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
# brute / gen helpers
# =========================================================================== #
def _area_of(g, n, m):
    from collections import deque
    seen = [[False] * m for _ in range(n)]
    best = 0
    for i in range(n):
        for j in range(m):
            if g[i][j] == 1 and not seen[i][j]:
                dq = deque([(i, j)]); seen[i][j] = True; c = 0
                while dq:
                    x, y = dq.popleft(); c += 1
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < m and g[nx][ny] == 1 and not seen[nx][ny]:
                            seen[nx][ny] = True; dq.append((nx, ny))
                best = max(best, c)
    return best


def _largeisland_brute(grid):
    n, m = len(grid), len(grid[0])
    best = _area_of([row[:] for row in grid], n, m)
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 0:
                g = [row[:] for row in grid]; g[i][j] = 1
                best = max(best, _area_of(g, n, m))
    return best


def _grid01_gen(r):
    out = []
    for _ in range(6):
        rows, cols = r.randint(1, 4), r.randint(1, 4)
        out.append({"grid": [[r.randint(0, 1) for _ in range(cols)] for _ in range(rows)]})
    return out


def _seqdig_brute(low, high):
    res = []
    for v in range(low, high + 1):
        s = str(v)
        if all(int(s[i + 1]) - int(s[i]) == 1 for i in range(len(s) - 1)):
            res.append(v)
    return res


def _seqdig_gen(r):
    out = []
    for _ in range(8):
        lo = r.randint(10, 500)
        hi = r.randint(lo, 5000)
        out.append({"low": lo, "high": hi})
    return out


def _mst_brute(points):
    n = len(points)
    if n <= 1:
        return 0
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            w = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
            edges.append((w, i, j))
    edges.sort()
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x

    total = used = 0
    for w, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            par[ri] = rj; total += w; used += 1
        if used == n - 1:
            break
    return total


def _points_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(1, 6)
        coords = r.sample([(x, y) for x in range(-10, 11) for y in range(-10, 11)], n)
        out.append({"points": [list(c) for c in coords]})
    return out


def _ldss_brute(nums):
    nums = sorted(nums)
    n = len(nums)
    best = 0
    for mask in range(1 << n):
        sub = [nums[i] for i in range(n) if mask & (1 << i)]
        ok = all(sub[b] % sub[a] == 0 for a in range(len(sub)) for b in range(a + 1, len(sub)))
        if ok:
            best = max(best, len(sub))
    return best


def _ldss_gen(r):
    return [{"nums": r.sample(range(1, 60), r.randint(1, 12))} for _ in range(8)]


def _queue_brute(people):
    from itertools import permutations
    n = len(people)
    for perm in permutations(range(n)):
        arr = [people[i] for i in perm]
        ok = True
        for i in range(n):
            cnt = sum(1 for j in range(i) if arr[j][0] >= arr[i][0])
            if cnt != arr[i][1]:
                ok = False; break
        if ok:
            return [list(x) for x in arr]
    return []


def _queue_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(1, 6)
        queue = [r.randint(1, 6) for _ in range(n)]
        people = []
        for i, h in enumerate(queue):
            k = sum(1 for j in range(i) if queue[j] >= h)
            people.append([h, k])
        r.shuffle(people)
        out.append({"people": people})
    return out


def _bordered_brute(grid):
    m, n = len(grid), len(grid[0])
    best = 0
    for i in range(m):
        for j in range(n):
            maxs = min(m - i, n - j)
            for s in range(1, maxs + 1):
                ok = True
                for c in range(s):
                    if (grid[i][j + c] != 1 or grid[i + s - 1][j + c] != 1 or
                            grid[i + c][j] != 1 or grid[i + c][j + s - 1] != 1):
                        ok = False; break
                if ok:
                    best = max(best, s)
    return best * best


def _revk_brute(head, k):
    out = []; i = 0; n = len(head)
    while i < n:
        chunk = head[i:i + k]
        out.extend(chunk[::-1] if len(chunk) == k else chunk)
        i += k
    return out


def _revk_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(0, 12)
        head = [r.randint(0, 99) for _ in range(n)]
        k = r.randint(1, n) if n >= 1 else 1
        out.append({"head": head, "k": k})
    return out


def _wf_brute(words, queries):
    res = []
    for prefix, suffix in queries:
        ans = -1
        for i, w in enumerate(words):
            if w.startswith(prefix) and w.endswith(suffix):
                ans = i
        res.append(ans)
    return res


def _wf_gen(r):
    out = []
    letters = "abc"
    for _ in range(6):
        words = ["".join(r.choice(letters) for _ in range(r.randint(1, 4)))
                 for _ in range(r.randint(1, 6))]
        queries = []
        for _ in range(r.randint(1, 5)):
            pre = "".join(r.choice(letters) for _ in range(r.randint(0, 2)))
            suf = "".join(r.choice(letters) for _ in range(r.randint(0, 2)))
            queries.append([pre, suf])
        out.append({"words": words, "queries": queries})
    return out


def _prevperm_brute(A):
    n = len(A); best = None
    for i in range(n):
        for j in range(i + 1, n):
            B = A[:]; B[i], B[j] = B[j], B[i]
            if B < A and (best is None or B > best):
                best = B
    return best if best is not None else A[:]


def _prevperm_gen(r):
    return [{"A": [r.randint(1, 6) for _ in range(r.randint(1, 8))]} for _ in range(8)]


def _twocity_brute(costs):
    from itertools import combinations
    m = len(costs); n = m // 2; best = None
    for combo in combinations(range(m), n):
        sset = set(combo)
        s = sum(costs[i][0] if i in sset else costs[i][1] for i in range(m))
        best = s if best is None else min(best, s)
    return best


def _twocity_gen(r):
    out = []
    for _ in range(6):
        n = r.choice([1, 2, 3, 4])
        out.append({"costs": [[r.randint(1, 50), r.randint(1, 50)] for _ in range(2 * n)]})
    return out


def _stamp_brute(stamp, target):
    from collections import deque
    n, m = len(target), len(stamp)
    if m > n:
        return False
    start = "?" * n
    seen = {start}
    dq = deque([start])
    while dq:
        cur = dq.popleft()
        if cur == target:
            return True
        for i in range(n - m + 1):
            nxt = cur[:i] + stamp + cur[i + m:]
            if nxt not in seen:
                seen.add(nxt); dq.append(nxt)
    return target in seen


def _stamp_gen(r):
    out = []
    for _ in range(8):
        m = r.randint(1, 3)
        stamp = "".join(r.choice("ab") for _ in range(m))
        n = r.randint(m, 5)
        target = "".join(r.choice("ab") for _ in range(n))
        out.append({"stamp": stamp, "target": target})
    return out


def _atoms_brute(formula):
    from collections import Counter
    pos = [0]; n = len(formula)

    def read_num():
        start = pos[0]
        while pos[0] < n and formula[pos[0]].isdigit():
            pos[0] += 1
        return int(formula[start:pos[0]] or 1)

    def parse():
        counts = Counter()
        while pos[0] < n and formula[pos[0]] != ')':
            if formula[pos[0]] == '(':
                pos[0] += 1
                inner = parse()
                pos[0] += 1  # skip ')'
                num = read_num()
                for k, v in inner.items():
                    counts[k] += v * num
            else:
                name = formula[pos[0]]; pos[0] += 1
                while pos[0] < n and formula[pos[0]].islower():
                    name += formula[pos[0]]; pos[0] += 1
                counts[name] += read_num()
        return counts

    res = parse()
    return "".join(k + (str(res[k]) if res[k] > 1 else "") for k in sorted(res))


def _atoms_gen(r):
    elems = ["H", "O", "Mg", "K", "N", "S", "Ca", "Na"]

    def build(depth):
        parts = []
        for _ in range(r.randint(1, 3)):
            if depth < 2 and r.random() < 0.3:
                inner = build(depth + 1)
                mult = r.randint(1, 4)
                parts.append("(" + inner + ")" + (str(mult) if mult > 1 else ""))
            else:
                e = r.choice(elems); c = r.randint(1, 5)
                parts.append(e + (str(c) if c > 1 else ""))
        return "".join(parts)

    return [{"formula": build(0)} for _ in range(6)]


def _camera_brute(root):
    left, right, val = _build_tree(root)
    nodes = list(val.keys())
    n = len(nodes)
    parent = {}
    for nd in nodes:
        for ch in (left.get(nd), right.get(nd)):
            if ch is not None:
                parent[ch] = nd
    best = n + 1
    for mask in range(1 << n):
        cams = {nodes[idx] for idx in range(n) if mask & (1 << idx)}
        covered = set()
        for cam in cams:
            covered.add(cam)
            for ch in (left.get(cam), right.get(cam)):
                if ch is not None:
                    covered.add(ch)
            if cam in parent:
                covered.add(parent[cam])
        if len(covered) == n:
            best = min(best, len(cams))
    return best


def _camera_gen(r):
    return [{"root": _rand_tree_vals(r, r.randint(1, 8), 0, 0)} for _ in range(6)]


def _countsmaller_brute(nums):
    n = len(nums)
    return [sum(1 for j in range(i + 1, n) if nums[j] < nums[i]) for i in range(n)]


def _countsmaller_gen(r):
    return [{"nums": [r.randint(-20, 20) for _ in range(r.randint(0, 30))]} for _ in range(8)]


def _invalidtx_brute(transactions):
    rows = [t.split(",") for t in transactions]
    res = []
    for i, (name, time, amount, city) in enumerate(rows):
        bad = int(amount) > 1000
        if not bad:
            for j, (n2, t2, a2, c2) in enumerate(rows):
                if i != j and n2 == name and c2 != city and abs(int(t2) - int(time)) <= 60:
                    bad = True; break
        if bad:
            res.append(transactions[i])
    return res


def _invalidtx_gen(r):
    names = ["alice", "bob", "carol"]
    cities = ["mtv", "beijing", "la"]
    out = []
    for _ in range(8):
        k = r.randint(1, 5)
        txns = ["{},{},{},{}".format(r.choice(names), r.randint(0, 200),
                                     r.randint(0, 2000), r.choice(cities))
                for _ in range(k)]
        out.append({"transactions": txns})
    return out


def _bst_brute(preorder):
    idx = [0]; n = len(preorder)

    def build(lo, hi):
        if idx[0] >= n:
            return None
        v = preorder[idx[0]]
        if v < lo or v > hi:
            return None
        idx[0] += 1
        node = [v, None, None]
        node[1] = build(lo, v - 1)
        node[2] = build(v + 1, hi)
        return node

    root = build(float("-inf"), float("inf"))
    from collections import deque
    out = [root[0]]; q = deque([root])
    while q:
        nd = q.popleft()
        for ch in (nd[1], nd[2]):
            if ch is None:
                out.append(None)
            else:
                out.append(ch[0]); q.append(ch)
    while out and out[-1] is None:
        out.pop()
    return out


def _bst_gen(r):
    out = []
    for _ in range(6):
        vals = r.sample(range(1, 60), r.randint(1, 8))
        rootval = vals[0]
        tree = {rootval: [None, None]}
        for v in vals[1:]:
            cur = rootval
            while True:
                node = tree[cur]
                side = 0 if v < cur else 1
                if node[side] is None:
                    node[side] = v; tree[v] = [None, None]; break
                cur = node[side]
        pre = []

        def dfs(x):
            if x is None:
                return
            pre.append(x); dfs(tree[x][0]); dfs(tree[x][1])

        dfs(rootval)
        out.append({"preorder": pre})
    return out


def _closest_brute(num):
    best = None
    for target in (num + 1, num + 2):
        i = 1; pair = [1, target]
        while i * i <= target:
            if target % i == 0:
                pair = [i, target // i]
            i += 1
        if best is None or (pair[1] - pair[0]) < (best[1] - best[0]):
            best = pair
    return best


def _closest_gen(r):
    return [{"num": r.randint(1, 2000)} for _ in range(10)]


def _discount_gen(r):
    out = []
    for _ in range(5):
        k = r.randint(1, 5)
        products = r.sample(range(1, 30), k)
        prices = [r.randint(1, 100) for _ in products]
        n = r.randint(1, 4); discount = r.randint(0, 100)
        op, oa = [], []
        for _ in range(r.randint(1, 5)):
            cnt = r.randint(1, k)
            prod = r.sample(products, cnt)
            op.append(prod); oa.append([r.randint(1, 10) for _ in prod])
        out.append({"n": n, "discount": discount, "products": products,
                    "prices": prices, "order_products": op, "order_amounts": oa})
    return out


def _subpath_brute(head, root):
    left, right, val = _build_tree(root)
    L = len(head)
    found = [False]

    def dfs(node, path):
        if node is None:
            return
        path = path + [val[node]]
        if len(path) >= L and path[-L:] == head:
            found[0] = True
        dfs(left.get(node), path)
        dfs(right.get(node), path)

    dfs(0, [])
    return found[0]


def _subpath_gen(r):
    out = []
    for _ in range(8):
        tree = _rand_tree_vals(r, r.randint(1, 12), 1, 4)
        head = [r.randint(1, 4) for _ in range(r.randint(1, 4))]
        out.append({"head": head, "root": tree})
    return out


def _coloring_brute(root, n, x):
    from collections import deque
    left, right, val = _build_tree(root)
    xn = next(nd for nd in val if val[nd] == x)
    adj = {nd: [] for nd in val}
    for nd in val:
        for ch in (left.get(nd), right.get(nd)):
            if ch is not None:
                adj[nd].append(ch); adj[ch].append(nd)
    best = 0
    for y in val:
        if y == xn:
            continue
        dq = deque([y]); vis = {y, xn}; size = 0
        while dq:
            u = dq.popleft()
            if u != xn:
                size += 1
            for w in adj[u]:
                if w not in vis:
                    vis.add(w); dq.append(w)
        best = max(best, size)
    return best > n // 2


def _coloring_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(1, 10)
        tree = _rand_distinct_tree(r, n)
        present = [v for v in tree if v is not None]
        out.append({"root": tree, "n": len(present), "x": r.choice(present)})
    return out


# =========================================================================== #
# 1. Making A Large Island
# =========================================================================== #
add("making-a-large-island", "Making A Large Island", "hard",
    ["array", "depth-first-search", "breadth-first-search", "union-find", "matrix"],
    "largestIsland", [("grid", "int[][]")], "int",
    """
You are given an `n x n` binary `grid`. You may change **at most one** `0` to a `1`.
Return the size of the largest island (a 4-directionally connected group of `1`s) you
can obtain afterward. If the grid is all `1`s, no change is made.

**Examples**
```
grid = [[1,0],[0,1]]   ->  3   (flip one 0 to join the two 1s)
grid = [[1,1],[1,0]]   ->  4   (flip the 0)
grid = [[1,1],[1,1]]   ->  4   (already one island)
```

**Constraints:** `1 <= n <= 50`, `grid[i][j]` is `0` or `1`.
""",
    """def largestIsland(grid):
    from collections import deque
    g = [row[:] for row in grid]
    n, m = len(g), len(g[0])
    size = {}
    label = 2
    for i in range(n):
        for j in range(m):
            if g[i][j] == 1:
                dq = deque([(i, j)]); g[i][j] = label; cnt = 0
                while dq:
                    x, y = dq.popleft(); cnt += 1
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < n and 0 <= ny < m and g[nx][ny] == 1:
                            g[nx][ny] = label; dq.append((nx, ny))
                size[label] = cnt; label += 1
    best = max(size.values()) if size else 0
    for i in range(n):
        for j in range(m):
            if g[i][j] == 0:
                seen = set(); tot = 1
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = i + dx, j + dy
                    if 0 <= nx < n and 0 <= ny < m and g[nx][ny] > 1 and g[nx][ny] not in seen:
                        seen.add(g[nx][ny]); tot += size[g[nx][ny]]
                best = max(best, tot)
    return best
""",
    visible=[{"grid": [[1, 0], [0, 1]]}, {"grid": [[1, 1], [1, 0]]},
             {"grid": [[1, 1], [1, 1]]}],
    hidden=[{"grid": [[0]]}, {"grid": [[1]]}, {"grid": [[0, 0], [0, 0]]},
            {"grid": [[1, 0, 1], [0, 0, 0], [1, 0, 1]]}],
    gen=_grid01_gen,
    brute=_largeisland_brute,
    checks=[({"grid": [[1, 0], [0, 1]]}, 3), ({"grid": [[1, 1], [1, 0]]}, 4),
            ({"grid": [[1, 1], [1, 1]]}, 4), ({"grid": [[0]]}, 1),
            ({"grid": [[0, 0], [0, 0]]}, 1)],
    source="new_p")


# =========================================================================== #
# 2. Sequential Digits
# =========================================================================== #
add("sequential-digits", "Sequential Digits", "medium", ["enumeration"],
    "sequentialDigits", [("low", "int"), ("high", "int")], "int[]",
    """
An integer has *sequential digits* if and only if each digit is exactly one more than
the previous digit. Return a **sorted** list of every integer in the range
`[low, high]` (inclusive) that has sequential digits.

**Examples**
```
low = 100,  high = 300   ->  [123,234]
low = 1000, high = 13000 ->  [1234,2345,3456,4567,5678,6789,12345]
```

**Constraints:** `10 <= low <= high <= 10^9`.
""",
    """def sequentialDigits(low, high):
    digits = "123456789"
    res = []
    for length in range(1, 10):
        for start in range(0, 10 - length):
            num = int(digits[start:start + length])
            if low <= num <= high:
                res.append(num)
    return sorted(res)
""",
    visible=[{"low": 100, "high": 300}, {"low": 1000, "high": 13000}],
    hidden=[{"low": 10, "high": 10}, {"low": 10, "high": 100},
            {"low": 58, "high": 155}],
    gen=_seqdig_gen,
    brute=_seqdig_brute,
    checks=[({"low": 100, "high": 300}, [123, 234]),
            ({"low": 1000, "high": 13000}, [1234, 2345, 3456, 4567, 5678, 6789, 12345]),
            ({"low": 10, "high": 100}, [12, 23, 34, 45, 56, 67, 78, 89]),
            ({"low": 10, "high": 10}, [])],
    source="new_p")


# =========================================================================== #
# 3. Min Cost to Connect All Points
# =========================================================================== #
add("min-cost-to-connect-all-points", "Min Cost To Connect All Points", "medium",
    ["array", "union-find", "graph", "minimum-spanning-tree"], "minCostConnectPoints",
    [("points", "int[][]")], "int",
    """
You are given `points`, where `points[i] = [xi, yi]` is an integer coordinate on a
2D plane. The cost of connecting two points is the Manhattan distance between them,
`|xi - xj| + |yi - yj|`. Return the minimum total cost to connect all points so that
there is exactly one simple path between any two points.

**Examples**
```
points = [[0,0],[2,2],[3,10],[5,2],[7,0]]   ->  20
points = [[3,12],[-2,5],[-4,1]]             ->  18
points = [[0,0]]                            ->  0
```

**Constraints:** `1 <= len(points) <= 1000`, `-10^6 <= xi, yi <= 10^6`, points distinct.
""",
    """def minCostConnectPoints(points):
    import heapq
    n = len(points)
    if n <= 1:
        return 0
    in_tree = [False] * n
    dist = [float('inf')] * n
    dist[0] = 0
    total = 0
    heap = [(0, 0)]
    cnt = 0
    while heap and cnt < n:
        d, u = heapq.heappop(heap)
        if in_tree[u]:
            continue
        in_tree[u] = True; total += d; cnt += 1
        ux, uy = points[u]
        for v in range(n):
            if not in_tree[v]:
                w = abs(ux - points[v][0]) + abs(uy - points[v][1])
                if w < dist[v]:
                    dist[v] = w; heapq.heappush(heap, (w, v))
    return total
""",
    visible=[{"points": [[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]},
             {"points": [[3, 12], [-2, 5], [-4, 1]]}, {"points": [[0, 0]]}],
    hidden=[{"points": [[0, 0], [1, 1], [1, 0], [-1, 1]]},
            {"points": [[2, -3], [-17, -8], [13, 8], [-17, -15]]}],
    gen=_points_gen,
    brute=_mst_brute,
    checks=[({"points": [[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]}, 20),
            ({"points": [[3, 12], [-2, 5], [-4, 1]]}, 18),
            ({"points": [[0, 0], [1, 1], [1, 0], [-1, 1]]}, 4),
            ({"points": [[0, 0]]}, 0),
            ({"points": [[-1000000, -1000000], [1000000, 1000000]]}, 4000000)],
    source="new_p")


# =========================================================================== #
# 4. Largest Divisible Subset (reframed -> size)
# =========================================================================== #
add("largest-divisible-subset", "Largest Divisible Subset", "medium",
    ["array", "math", "dynamic-programming", "sorting"], "largestDivisibleSubsetSize",
    [("nums", "int[]")], "int",
    """
Given a set of **distinct** positive integers `nums`, find the largest subset such
that every pair `(a, b)` of its elements satisfies `a % b == 0` or `b % a == 0`.
Return the **size** of that largest subset.

**Examples**
```
nums = [1,2,3]     ->  2   (e.g. {1,2})
nums = [1,2,4,8]   ->  4   ({1,2,4,8})
```

**Constraints:** `1 <= len(nums) <= 1000`, elements are distinct positive integers.
""",
    """def largestDivisibleSubsetSize(nums):
    if not nums:
        return 0
    nums = sorted(nums)
    n = len(nums)
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[i] % nums[j] == 0:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
""",
    visible=[{"nums": [1, 2, 3]}, {"nums": [1, 2, 4, 8]}],
    hidden=[{"nums": [1]}, {"nums": [3, 5, 7]}, {"nums": [2, 4, 8, 16, 32]},
            {"nums": [4, 8, 10, 240]}],
    gen=_ldss_gen,
    brute=_ldss_brute,
    checks=[({"nums": [1, 2, 3]}, 2), ({"nums": [1, 2, 4, 8]}, 4), ({"nums": [1]}, 1),
            ({"nums": [2, 4, 8, 16, 32]}, 5), ({"nums": [3, 5, 7]}, 1)],
    source="new_p")


# =========================================================================== #
# 5. Queue Reconstruction by Height
# =========================================================================== #
add("queue-reconstruction-by-height", "Queue Reconstruction By Height", "medium",
    ["array", "greedy", "binary-indexed-tree", "sorting"], "reconstructQueue",
    [("people", "int[][]")], "int[][]",
    """
You are given `people`, a list of pairs `[h, k]`: `h` is a person's height and `k`
is the number of people in front of this person who have a height **greater than or
equal to** `h`. Reconstruct and return the queue (the unique arrangement of `people`
that satisfies every pair's `k`).

**Example**
```
people = [[7,0],[4,4],[7,1],[5,0],[6,1],[5,2]]
    ->  [[5,0],[7,0],[5,2],[6,1],[4,4],[7,1]]
```

**Constraints:** `1 <= len(people) <= 2000`, the input is always reconstructable.
""",
    """def reconstructQueue(people):
    people = sorted(people, key=lambda p: (-p[0], p[1]))
    res = []
    for p in people:
        res.insert(p[1], p)
    return res
""",
    visible=[{"people": [[7, 0], [4, 4], [7, 1], [5, 0], [6, 1], [5, 2]]}],
    hidden=[{"people": [[1, 0]]}, {"people": [[2, 0], [1, 0]]},
            {"people": [[6, 0], [5, 0], [4, 0], [3, 2], [2, 2], [1, 4]]}],
    gen=_queue_gen,
    brute=_queue_brute,
    checks=[({"people": [[7, 0], [4, 4], [7, 1], [5, 0], [6, 1], [5, 2]]},
             [[5, 0], [7, 0], [5, 2], [6, 1], [4, 4], [7, 1]]),
            ({"people": [[1, 0]]}, [[1, 0]]),
            ({"people": [[2, 0], [1, 0]]}, [[1, 0], [2, 0]])],
    source="new_p")


# =========================================================================== #
# 6. Largest 1-Bordered Square
# =========================================================================== #
add("largest-1-bordered-square", "Largest 1 Bordered Square", "medium",
    ["array", "dynamic-programming", "matrix"], "largest1BorderedSquare",
    [("grid", "int[][]")], "int",
    """
Given a 2D `grid` of `0`s and `1`s, return the number of elements in the largest
**square** subgrid whose border is made entirely of `1`s, or `0` if no such subgrid
exists.

**Examples**
```
grid = [[1,1,1],[1,0,1],[1,1,1]]   ->  9
grid = [[1,1,0,0]]                 ->  1
```

**Constraints:** `1 <= rows, cols <= 100`, `grid[i][j]` is `0` or `1`.
""",
    """def largest1BorderedSquare(grid):
    m, n = len(grid), len(grid[0])
    hor = [[0] * n for _ in range(m)]
    ver = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                hor[i][j] = (hor[i][j - 1] if j > 0 else 0) + 1
                ver[i][j] = (ver[i - 1][j] if i > 0 else 0) + 1
    best = 0
    for i in range(m):
        for j in range(n):
            side = min(hor[i][j], ver[i][j])
            while side > best:
                if ver[i][j - side + 1] >= side and hor[i - side + 1][j] >= side:
                    best = side
                    break
                side -= 1
    return best * best
""",
    visible=[{"grid": [[1, 1, 1], [1, 0, 1], [1, 1, 1]]}, {"grid": [[1, 1, 0, 0]]}],
    hidden=[{"grid": [[0, 0], [0, 0]]}, {"grid": [[1]]},
            {"grid": [[1, 1, 1, 1], [1, 0, 0, 1], [1, 0, 0, 1], [1, 1, 1, 1]]}],
    gen=_grid01_gen,
    brute=_bordered_brute,
    checks=[({"grid": [[1, 1, 1], [1, 0, 1], [1, 1, 1]]}, 9),
            ({"grid": [[1, 1, 0, 0]]}, 1), ({"grid": [[0, 0], [0, 0]]}, 0),
            ({"grid": [[1]]}, 1)],
    source="new_p")


# =========================================================================== #
# 7. Reverse Nodes in k-Group
# =========================================================================== #
add("reverse-nodes-in-k-group", "Reverse Nodes In K Group", "hard",
    ["linked-list", "recursion"], "reverseKGroup",
    [("head", "int[]"), ("k", "int")], "int[]",
    """
A singly linked list is given as an array of values `head`. Reverse the nodes `k` at
a time and return the resulting list of values. If the number of nodes is not a
multiple of `k`, the leftover nodes at the end stay as they are.

**Examples**
```
head = [1,2,3,4,5], k = 2   ->  [2,1,4,3,5]
head = [1,2,3,4,5], k = 3   ->  [3,2,1,4,5]
```

**Constraints:** `0 <= len(head) <= 5000`, `1 <= k <= len(head)` (or `k = 1` when empty).
""",
    """def reverseKGroup(head, k):
    res = []
    n = len(head)
    i = 0
    while i + k <= n:
        res.extend(head[i:i + k][::-1])
        i += k
    res.extend(head[i:])
    return res
""",
    visible=[{"head": [1, 2, 3, 4, 5], "k": 2}, {"head": [1, 2, 3, 4, 5], "k": 3}],
    hidden=[{"head": [1], "k": 1}, {"head": [1, 2, 3, 4], "k": 4},
            {"head": [1, 2, 3, 4, 5], "k": 1}, {"head": [], "k": 1}],
    gen=_revk_gen,
    brute=_revk_brute,
    checks=[({"head": [1, 2, 3, 4, 5], "k": 2}, [2, 1, 4, 3, 5]),
            ({"head": [1, 2, 3, 4, 5], "k": 3}, [3, 2, 1, 4, 5]),
            ({"head": [1, 2, 3, 4], "k": 4}, [4, 3, 2, 1]),
            ({"head": [1], "k": 1}, [1])],
    source="new_p")


# =========================================================================== #
# 8. Prefix and Suffix Search (reframed -> batch queries)
# =========================================================================== #
add("prefix-and-suffix-search", "Prefix And Suffix Search", "hard",
    ["string", "trie", "design"], "wordFilter",
    [("words", "string[]"), ("queries", "string[][]")], "int[]",
    """
Each word `words[i]` has *weight* `i` (its index). For each query `[prefix, suffix]`,
return the **largest** weight of a word that starts with `prefix` **and** ends with
`suffix`, or `-1` if no such word exists. Return one answer per query, in order.

**Example**
```
words = ["apple"]
queries = [["a","e"], ["b",""]]   ->  [0, -1]
```

**Constraints:** `1 <= len(words) <= 15000`, word/prefix/suffix lengths in `[0, 10]`,
lowercase letters only.
""",
    """def wordFilter(words, queries):
    res = []
    for prefix, suffix in queries:
        ans = -1
        for i in range(len(words) - 1, -1, -1):
            if words[i].startswith(prefix) and words[i].endswith(suffix):
                ans = i
                break
        res.append(ans)
    return res
""",
    visible=[{"words": ["apple"], "queries": [["a", "e"], ["b", ""]]}],
    hidden=[{"words": ["abc", "abcd", "xbc"], "queries": [["a", "c"], ["", "d"], ["x", ""]]},
            {"words": ["a", "a", "a"], "queries": [["a", "a"], ["", ""]]}],
    gen=_wf_gen,
    brute=_wf_brute,
    checks=[({"words": ["apple"], "queries": [["a", "e"], ["b", ""]]}, [0, -1]),
            ({"words": ["abc", "abcd", "xbc"], "queries": [["a", "c"], ["", "d"], ["x", ""]]},
             [0, 1, 2]),
            ({"words": ["a", "a", "a"], "queries": [["a", "a"], ["", ""]]}, [2, 2])],
    source="new_p")


# =========================================================================== #
# 9. Previous Permutation With One Swap
# =========================================================================== #
add("previous-permutation-with-one-swap", "Previous Permutation With One Swap", "medium",
    ["array", "greedy"], "prevPermOpt1", [("A", "int[]")], "int[]",
    """
Given an array `A` of positive integers (not necessarily distinct), return the
**lexicographically largest** permutation that is strictly smaller than `A` and can be
obtained with a single swap of two elements. If no such permutation exists, return `A`
unchanged.

**Examples**
```
A = [3,2,1]      ->  [3,1,2]
A = [1,1,5]      ->  [1,1,5]
A = [1,9,4,6,7]  ->  [1,7,4,6,9]
```

**Constraints:** `1 <= len(A) <= 10^4`, `1 <= A[i] <= 10^4`.
""",
    """def prevPermOpt1(A):
    A = A[:]
    n = len(A)
    for i in range(n - 2, -1, -1):
        if A[i] > A[i + 1]:
            j = -1
            for k in range(i + 1, n):
                if A[k] < A[i] and (j == -1 or A[k] > A[j]):
                    j = k
            A[i], A[j] = A[j], A[i]
            return A
    return A
""",
    visible=[{"A": [3, 2, 1]}, {"A": [1, 1, 5]}, {"A": [1, 9, 4, 6, 7]}],
    hidden=[{"A": [3, 1, 1, 3]}, {"A": [1]}, {"A": [1, 2, 3]}, {"A": [5, 4, 3, 2, 1]}],
    gen=_prevperm_gen,
    brute=_prevperm_brute,
    checks=[({"A": [3, 2, 1]}, [3, 1, 2]), ({"A": [1, 1, 5]}, [1, 1, 5]),
            ({"A": [1, 9, 4, 6, 7]}, [1, 7, 4, 6, 9]), ({"A": [3, 1, 1, 3]}, [1, 3, 1, 3]),
            ({"A": [1]}, [1])],
    source="new_p")


# =========================================================================== #
# 10. Two City Scheduling
# =========================================================================== #
add("two-city-scheduling", "Two City Scheduling", "medium",
    ["array", "greedy", "sorting"], "twoCitySchedCost", [("costs", "int[][]")], "int",
    """
A company is interviewing `2n` people. `costs[i] = [aCost, bCost]` is the cost of
flying person `i` to city A or city B respectively. Return the minimum total cost to
fly everyone such that **exactly `n` people** go to each city.

**Example**
```
costs = [[10,20],[30,200],[400,50],[30,20]]   ->  110
```

**Constraints:** `2n == len(costs)`, `2 <= len(costs) <= 100` (even), `1 <= cost <= 1000`.
""",
    """def twoCitySchedCost(costs):
    costs = sorted(costs, key=lambda c: c[0] - c[1])
    n = len(costs) // 2
    return sum((c[0] if i < n else c[1]) for i, c in enumerate(costs))
""",
    visible=[{"costs": [[10, 20], [30, 200], [400, 50], [30, 20]]}],
    hidden=[{"costs": [[259, 770], [448, 54], [926, 667], [184, 139], [840, 118], [577, 469]]},
            {"costs": [[10, 20], [30, 20]]}],
    gen=_twocity_gen,
    brute=_twocity_brute,
    checks=[({"costs": [[10, 20], [30, 200], [400, 50], [30, 20]]}, 110),
            ({"costs": [[259, 770], [448, 54], [926, 667], [184, 139], [840, 118], [577, 469]]},
             1859),
            ({"costs": [[515, 563], [451, 713], [537, 709], [343, 819], [855, 779],
                        [457, 60], [650, 359], [631, 42]]}, 3086)],
    source="new_p")


# =========================================================================== #
# 11. Stamping the Sequence (reframed -> feasibility bool)
# =========================================================================== #
add("stamping-the-sequence", "Stamping The Sequence", "hard",
    ["string", "greedy", "stack"], "canStamp",
    [("stamp", "string"), ("target", "string")], "bool",
    """
You start with a sequence of `len(target)` `'?'` characters and a `stamp` of lowercase
letters. On each turn you may place the stamp over a fully-contained window of the
sequence, overwriting those positions with the stamp's letters. Return `True` if the
sequence can be turned into `target` using any number of stamping turns, otherwise
`False`.

**Examples**
```
stamp = "abc",  target = "ababc"    ->  true
stamp = "abca", target = "aabcaca"  ->  true
stamp = "ab",   target = "aba"      ->  false
```

**Constraints:** `1 <= len(stamp) <= len(target) <= 1000`, lowercase letters only.
""",
    """def canStamp(stamp, target):
    t = list(target)
    n, m = len(target), len(stamp)
    total = 0
    while total < n:
        progressed = False
        for i in range(n - m + 1):
            ok = True
            has_real = False
            for j in range(m):
                if t[i + j] == '*':
                    continue
                has_real = True
                if t[i + j] != stamp[j]:
                    ok = False
                    break
            if ok and has_real:
                for j in range(m):
                    if t[i + j] != '*':
                        t[i + j] = '*'
                        total += 1
                progressed = True
        if not progressed:
            break
    return total == n
""",
    visible=[{"stamp": "abc", "target": "ababc"}, {"stamp": "abca", "target": "aabcaca"},
             {"stamp": "ab", "target": "aba"}],
    hidden=[{"stamp": "a", "target": "aaa"}, {"stamp": "abc", "target": "abcabc"},
            {"stamp": "ab", "target": "ba"}, {"stamp": "ab", "target": "ab"}],
    gen=_stamp_gen,
    brute=_stamp_brute,
    checks=[({"stamp": "abc", "target": "ababc"}, True),
            ({"stamp": "abca", "target": "aabcaca"}, True),
            ({"stamp": "ab", "target": "aba"}, False),
            ({"stamp": "a", "target": "aaa"}, True),
            ({"stamp": "ab", "target": "ba"}, False)],
    source="new_p")


# =========================================================================== #
# 12. Number of Atoms
# =========================================================================== #
add("number-of-atoms", "Number Of Atoms", "hard",
    ["hash-table", "string", "stack", "sorting"], "countOfAtoms",
    [("formula", "string")], "string",
    """
Given a chemical `formula`, return the count of each atom. An element name starts with
an uppercase letter followed by zero or more lowercase letters; an optional count (only
shown when `> 1`) follows. Formulas can be concatenated and grouped in parentheses with
an optional multiplier, e.g. `(H2O2)3`. Output the elements in **sorted (alphabetical)
order**, each name followed by its total count (omit the count when it is `1`).

**Examples**
```
formula = "H2O"               ->  "H2O"
formula = "Mg(OH)2"           ->  "H2MgO2"
formula = "K4(ON(SO3)2)2"     ->  "K4N2O14S4"
```

**Constraints:** `1 <= len(formula) <= 1000`, a valid formula of letters, digits, `()`.
""",
    """def countOfAtoms(formula):
    from collections import Counter
    n = len(formula)
    stack = [Counter()]
    i = 0
    while i < n:
        c = formula[i]
        if c == '(':
            stack.append(Counter()); i += 1
        elif c == ')':
            i += 1
            start = i
            while i < n and formula[i].isdigit():
                i += 1
            mult = int(formula[start:i] or 1)
            top = stack.pop()
            for el, cnt in top.items():
                stack[-1][el] += cnt * mult
        else:
            start = i; i += 1
            while i < n and formula[i].islower():
                i += 1
            name = formula[start:i]
            start = i
            while i < n and formula[i].isdigit():
                i += 1
            cnt = int(formula[start:i] or 1)
            stack[-1][name] += cnt
    counter = stack[0]
    return "".join(name + (str(counter[name]) if counter[name] > 1 else "")
                   for name in sorted(counter))
""",
    visible=[{"formula": "H2O"}, {"formula": "Mg(OH)2"}, {"formula": "K4(ON(SO3)2)2"}],
    hidden=[{"formula": "OH"}, {"formula": "H"}, {"formula": "(H2O2)3"},
            {"formula": "Be32"}],
    gen=_atoms_gen,
    brute=_atoms_brute,
    checks=[({"formula": "H2O"}, "H2O"), ({"formula": "Mg(OH)2"}, "H2MgO2"),
            ({"formula": "K4(ON(SO3)2)2"}, "K4N2O14S4"), ({"formula": "OH"}, "HO"),
            ({"formula": "(H2O2)3"}, "H6O6")],
    source="new_p")


# =========================================================================== #
# 13. Binary Tree Cameras
# =========================================================================== #
add("binary-tree-cameras", "Binary Tree Cameras", "hard",
    ["tree", "depth-first-search", "dynamic-programming", "greedy"], "minCameraCover",
    [("root", "int[]")], "int",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. A camera placed on a node monitors its
parent, itself, and its immediate children. Return the minimum number of cameras needed
so that **every** node is monitored.

**Examples**
```
root = [0,0,null,0,0]              ->  1
root = [0,0,null,0,null,0,null,null,0]  ->  2
```

**Constraints:** `1 <= number of nodes <= 1000`; every node value is `0`.
""",
    """def minCameraCover(root):
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
    cameras = [0]

    def dfs(node):
        if node is None:
            return 1  # covered, no camera
        l = dfs(left.get(node))
        r = dfs(right.get(node))
        if l == 0 or r == 0:
            cameras[0] += 1
            return 2  # has camera
        if l == 2 or r == 2:
            return 1  # covered by a child's camera
        return 0      # not covered

    if dfs(0) == 0:
        cameras[0] += 1
    return cameras[0]
""",
    visible=[{"root": [0, 0, None, 0, 0]},
             {"root": [0, 0, None, 0, None, 0, None, None, 0]}],
    hidden=[{"root": [0]}, {"root": [0, 0]}, {"root": [0, 0, 0]},
            {"root": [0, 0, 0, None, 0, None, 0]}],
    gen=_camera_gen,
    brute=_camera_brute,
    checks=[({"root": [0, 0, None, 0, 0]}, 1),
            ({"root": [0, 0, None, 0, None, 0, None, None, 0]}, 2),
            ({"root": [0]}, 1), ({"root": [0, 0]}, 1)],
    source="new_p")


# =========================================================================== #
# 14. Count of Smaller Numbers After Self
# =========================================================================== #
add("count-of-smaller-numbers-after-self", "Count Of Smaller Numbers After Self", "hard",
    ["array", "binary-indexed-tree", "divide-and-conquer", "merge-sort"], "countSmaller",
    [("nums", "int[]")], "int[]",
    """
Given an integer array `nums`, return a new array `counts` where `counts[i]` is the
number of elements to the **right** of `nums[i]` that are smaller than `nums[i]`.

**Example**
```
nums = [5,2,6,1]   ->  [2,1,1,0]
```

**Constraints:** `0 <= len(nums) <= 10^5`, values fit in a 32-bit integer.
""",
    """def countSmaller(nums):
    if not nums:
        return []
    vals = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    m = len(vals)
    bit = [0] * (m + 1)

    def update(i):
        while i <= m:
            bit[i] += 1
            i += i & (-i)

    def query(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    res = [0] * len(nums)
    for idx in range(len(nums) - 1, -1, -1):
        r = rank[nums[idx]]
        res[idx] = query(r - 1)
        update(r)
    return res
""",
    visible=[{"nums": [5, 2, 6, 1]}],
    hidden=[{"nums": []}, {"nums": [1]}, {"nums": [2, 2, 2]}, {"nums": [-1, -1]},
            {"nums": [5, 4, 3, 2, 1]}],
    gen=_countsmaller_gen,
    brute=_countsmaller_brute,
    checks=[({"nums": [5, 2, 6, 1]}, [2, 1, 1, 0]), ({"nums": []}, []),
            ({"nums": [1]}, [0]), ({"nums": [5, 4, 3, 2, 1]}, [4, 3, 2, 1, 0])],
    source="new_p")


# =========================================================================== #
# 15. Invalid Transactions (any order -> unordered)
# =========================================================================== #
add("invalid-transactions", "Invalid Transactions", "medium",
    ["array", "string", "sorting"], "invalidTransactions",
    [("transactions", "string[]")], "string[]",
    """
A transaction string is `"{name},{time},{amount},{city}"`. A transaction is **possibly
invalid** if its `amount` exceeds `1000`, **or** if there is another transaction with
the same `name`, a different `city`, and a `time` within `60` minutes (inclusive).
Return the list of all possibly-invalid transaction strings, in **any order**.

**Examples**
```
["alice,20,800,mtv","alice,50,100,beijing"]   ->  both transactions
["alice,20,800,mtv","alice,50,1200,mtv"]      ->  ["alice,50,1200,mtv"]
```

**Constraints:** `len(transactions) <= 1000`; names/cities are 1-10 lowercase letters,
`0 <= time <= 1000`, `0 <= amount <= 2000`.
""",
    """def invalidTransactions(transactions):
    parsed = []
    for t in transactions:
        name, time, amount, city = t.split(",")
        parsed.append((name, int(time), int(amount), city))
    n = len(parsed)
    invalid = set()
    for i in range(n):
        name, time, amount, city = parsed[i]
        if amount > 1000:
            invalid.add(i)
            continue
        for j in range(n):
            if i != j:
                n2, t2, a2, c2 = parsed[j]
                if name == n2 and city != c2 and abs(time - t2) <= 60:
                    invalid.add(i)
                    break
    return [transactions[i] for i in sorted(invalid)]
""",
    visible=[{"transactions": ["alice,20,800,mtv", "alice,50,100,beijing"]},
             {"transactions": ["alice,20,800,mtv", "alice,50,1200,mtv"]},
             {"transactions": ["alice,20,800,mtv", "bob,50,1200,mtv"]}],
    hidden=[{"transactions": ["alice,20,800,mtv"]},
            {"transactions": ["bob,689,1029,barcelona"]},
            {"transactions": ["alice,20,800,mtv", "alice,85,800,beijing"]}],
    gen=_invalidtx_gen,
    brute=_invalidtx_brute,
    checks=[({"transactions": ["alice,20,800,mtv", "alice,50,100,beijing"]},
             sorted(["alice,20,800,mtv", "alice,50,100,beijing"])),
            ({"transactions": ["alice,20,800,mtv", "alice,50,1200,mtv"]},
             ["alice,50,1200,mtv"]),
            ({"transactions": ["alice,20,800,mtv", "bob,50,1200,mtv"]},
             ["bob,50,1200,mtv"]),
            ({"transactions": ["alice,20,800,mtv"]}, [])],
    norm=sorted,
    source="new_p")
COMPARE["invalid-transactions"] = "unordered"


# =========================================================================== #
# 16. Construct Binary Search Tree from Preorder Traversal
# =========================================================================== #
add("construct-binary-search-tree-from-preorder-traversal",
    "Construct Binary Search Tree From Preorder Traversal", "medium",
    ["stack", "tree", "binary-search-tree", "binary-tree"], "bstFromPreorder",
    [("preorder", "int[]")], "int[]",
    """
Given the `preorder` traversal of a binary search tree (every value distinct), build
the BST and return it as a LeetCode **level-order array** (`None` for a missing child,
trailing `None`s trimmed). Recall a BST keeps `node.left < node < node.right`.

**Example**
```
preorder = [8,5,1,7,10,12]   ->  [8,5,10,1,7,null,12]
```

**Constraints:** `1 <= len(preorder) <= 100`, `1 <= preorder[i] <= 10^8`, distinct.
""",
    """def bstFromPreorder(preorder):
    from collections import deque
    val = {0: preorder[0]}
    left, right = {}, {}
    nid = 0
    for v in preorder[1:]:
        nid += 1
        val[nid] = v
        cur = 0
        while True:
            if v < val[cur]:
                if cur in left:
                    cur = left[cur]
                else:
                    left[cur] = nid; break
            else:
                if cur in right:
                    cur = right[cur]
                else:
                    right[cur] = nid; break
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
    visible=[{"preorder": [8, 5, 1, 7, 10, 12]}],
    hidden=[{"preorder": [1]}, {"preorder": [2, 1, 3]}, {"preorder": [1, 2, 3]},
            {"preorder": [5, 4, 3, 2, 1]}],
    gen=_bst_gen,
    brute=_bst_brute,
    checks=[({"preorder": [8, 5, 1, 7, 10, 12]}, [8, 5, 10, 1, 7, None, 12]),
            ({"preorder": [1]}, [1]), ({"preorder": [2, 1, 3]}, [2, 1, 3]),
            ({"preorder": [1, 2, 3]}, [1, None, 2, None, 3])],
    source="new_p")


# =========================================================================== #
# 17. Closest Divisors
# =========================================================================== #
add("closest-divisors", "Closest Divisors", "medium", ["math"], "closestDivisors",
    [("num", "int")], "int[]",
    """
Given an integer `num`, consider `num + 1` and `num + 2`. Among all ways to write
either of them as a product of two positive integers, find the pair with the smallest
absolute difference. Return that pair as `[smaller, larger]`.

**Examples**
```
num = 8     ->  [3,3]     (9 = 3 x 3)
num = 123   ->  [5,25]    (125 = 5 x 25)
num = 999   ->  [25,40]   (1000 = 25 x 40)
```

**Constraints:** `1 <= num <= 10^9`.
""",
    """def closestDivisors(num):
    import math
    best = None
    for target in (num + 1, num + 2):
        a = int(math.isqrt(target))
        while target % a != 0:
            a -= 1
        pair = [a, target // a]
        if best is None or (pair[1] - pair[0]) < (best[1] - best[0]):
            best = pair
    return best
""",
    visible=[{"num": 8}, {"num": 123}, {"num": 999}],
    hidden=[{"num": 1}, {"num": 2}, {"num": 100}, {"num": 1000000000}],
    gen=_closest_gen,
    brute=_closest_brute,
    checks=[({"num": 8}, [3, 3]), ({"num": 123}, [5, 25]), ({"num": 999}, [25, 40]),
            ({"num": 1}, [1, 2]), ({"num": 2}, [2, 2])],
    source="new_p")


# =========================================================================== #
# 18. Apply Discount Every n Orders (reframed -> batch getBill calls)
# =========================================================================== #
add("apply-discount-every-n-orders", "Apply Discount Every N Orders", "medium",
    ["array", "hash-table", "design"], "getBills",
    [("n", "int"), ("discount", "int"), ("products", "int[]"), ("prices", "int[]"),
     ("order_products", "int[][]"), ("order_amounts", "int[][]")], "float[]",
    """
A supermarket gives a discount to every `n`-th customer. Product `products[i]` has unit
price `prices[i]`. The `c`-th customer (1-indexed) buys, for each `j`,
`order_amounts[c][j]` units of product `order_products[c][j]`. Their bill is the sum of
unit-price times amount; if `c` is a multiple of `n`, the bill becomes
`bill - (discount * bill) / 100`. Return the list of bills, **each rounded to 5
decimal places**.

**Example**
```
n = 3, discount = 50, products = [1,2,3,4,5,6,7],
prices = [100,200,300,400,300,200,100]
order_products = [[1,2],[3,7],[1,2,3,4,5,6,7],[4],[7,3],[7,5,3,1,6,4,2],[2,3,5]]
order_amounts  = [[1,2],[10,10],[1,1,1,1,1,1,1],[10],[10,10],[10,10,10,9,9,9,7],[5,3,2]]
    ->  [500.0,4000.0,800.0,4000.0,4000.0,7350.0,2500.0]
```

**Constraints:** `1 <= n <= 10^4`, `0 <= discount <= 100`, distinct `products`,
`1 <= prices[i] <= 1000`, every ordered product exists, `1 <= amount <= 1000`.
""",
    """def getBills(n, discount, products, prices, order_products, order_amounts):
    price = {p: prices[i] for i, p in enumerate(products)}
    res = []
    for c in range(len(order_products)):
        total = 0
        for pid, amt in zip(order_products[c], order_amounts[c]):
            total += price[pid] * amt
        if (c + 1) % n == 0:
            total = total - (discount * total) / 100
        res.append(round(float(total), 5))
    return res
""",
    visible=[{"n": 3, "discount": 50, "products": [1, 2, 3, 4, 5, 6, 7],
              "prices": [100, 200, 300, 400, 300, 200, 100],
              "order_products": [[1, 2], [3, 7], [1, 2, 3, 4, 5, 6, 7], [4], [7, 3],
                                 [7, 5, 3, 1, 6, 4, 2], [2, 3, 5]],
              "order_amounts": [[1, 2], [10, 10], [1, 1, 1, 1, 1, 1, 1], [10], [10, 10],
                                [10, 10, 10, 9, 9, 9, 7], [5, 3, 2]]}],
    hidden=[{"n": 1, "discount": 0, "products": [1], "prices": [100],
             "order_products": [[1]], "order_amounts": [[1]]},
            {"n": 2, "discount": 100, "products": [1], "prices": [10],
             "order_products": [[1], [1]], "order_amounts": [[1], [1]]}],
    gen=_discount_gen,
    checks=[({"n": 3, "discount": 50, "products": [1, 2, 3, 4, 5, 6, 7],
              "prices": [100, 200, 300, 400, 300, 200, 100],
              "order_products": [[1, 2], [3, 7], [1, 2, 3, 4, 5, 6, 7], [4], [7, 3],
                                 [7, 5, 3, 1, 6, 4, 2], [2, 3, 5]],
              "order_amounts": [[1, 2], [10, 10], [1, 1, 1, 1, 1, 1, 1], [10], [10, 10],
                                [10, 10, 10, 9, 9, 9, 7], [5, 3, 2]]},
             [500.0, 4000.0, 800.0, 4000.0, 4000.0, 7350.0, 2500.0]),
            ({"n": 2, "discount": 100, "products": [1], "prices": [10],
              "order_products": [[1], [1]], "order_amounts": [[1], [1]]}, [10.0, 0.0])],
    source="new_p")


# =========================================================================== #
# 19. Linked List in Binary Tree
# =========================================================================== #
add("linked-list-in-binary-tree", "Linked List In Binary Tree", "medium",
    ["linked-list", "tree", "depth-first-search", "binary-tree"], "isSubPath",
    [("head", "int[]"), ("root", "int[]")], "bool",
    """
A linked list is given as an array of values `head`, and a binary tree as a LeetCode
**level-order array** `root` (`null`/`None` for a missing child). Return `True` if the
values of `head` (starting from its first element) match the values along some
**downward path** in the tree (a path that goes from a node strictly toward its
descendants), otherwise `False`.

**Examples**
```
head = [4,2,8], root = [1,4,4,null,2,2,null,1,null,6,8]   ->  true
head = [1,4,2,6,8], root = [1,4,4,null,2,2,null,1,null,6,8]  ->  false
```

**Constraints:** `1 <= len(head) <= 100`; the tree has between 1 and 2500 nodes;
values are in `[1, 100]`.
""",
    """def isSubPath(head, root):
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

    def match(node, k):
        if k == len(head):
            return True
        if node is None or val[node] != head[k]:
            return False
        return match(left.get(node), k + 1) or match(right.get(node), k + 1)

    return any(match(nd, 0) for nd in val)
""",
    visible=[{"head": [4, 2, 8], "root": [1, 4, 4, None, 2, 2, None, 1, None, 6, 8]},
             {"head": [1, 4, 2, 6, 8],
              "root": [1, 4, 4, None, 2, 2, None, 1, None, 6, 8]}],
    hidden=[{"head": [1], "root": [1]}, {"head": [2], "root": [1]},
            {"head": [1, 4, 2, 6],
             "root": [1, 4, 4, None, 2, 2, None, 1, None, 6, 8]}],
    gen=_subpath_gen,
    brute=_subpath_brute,
    checks=[({"head": [4, 2, 8], "root": [1, 4, 4, None, 2, 2, None, 1, None, 6, 8]}, True),
            ({"head": [1, 4, 2, 6, 8],
              "root": [1, 4, 4, None, 2, 2, None, 1, None, 6, 8]}, False),
            ({"head": [1], "root": [1]}, True), ({"head": [2], "root": [1]}, False)],
    source="new_p")


# =========================================================================== #
# 20. Binary Tree Coloring Game
# =========================================================================== #
add("binary-tree-coloring-game", "Binary Tree Coloring Game", "medium",
    ["tree", "depth-first-search", "binary-tree"], "btreeGameWinningMove",
    [("root", "int[]"), ("n", "int"), ("x", "int")], "bool",
    """
A binary tree with `n` nodes (values `1..n`, all distinct) is given as a LeetCode
**level-order array**. Player 1 colours node `x` red, then Player 2 colours any other
node blue. Players then alternate, each turn colouring an uncoloured node adjacent to
one of their own coloured nodes. Whoever colours more nodes wins. Return `True` if
Player 2 can choose a node guaranteeing a win.

**Example**
```
root = [1,2,3,4,5,6,7,8,9,10,11], n = 11, x = 3   ->  true
```

**Constraints:** `1 <= n <= 100`, node values are a permutation of `1..n`.
""",
    """def btreeGameWinningMove(root, n, x):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, m = 1, 1, len(root)
    while q and i < m:
        cur = q.popleft()
        if i < m:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; left[cur] = nid; q.append(nid); nid += 1
        if i < m:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; right[cur] = nid; q.append(nid); nid += 1
    target = next(nd for nd in val if val[nd] == x)

    def size(node):
        if node is None:
            return 0
        return 1 + size(left.get(node)) + size(right.get(node))

    lsz = size(left.get(target))
    rsz = size(right.get(target))
    psz = n - 1 - lsz - rsz
    return max(lsz, rsz, psz) > n // 2
""",
    visible=[{"root": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], "n": 11, "x": 3}],
    hidden=[{"root": [1, 2, 3], "n": 3, "x": 1}, {"root": [1, 2, 3], "n": 3, "x": 2},
            {"root": [1, 2, 3, 4, 5, 6, 7], "n": 7, "x": 1},
            {"root": [1], "n": 1, "x": 1}],
    gen=_coloring_gen,
    brute=_coloring_brute,
    checks=[({"root": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], "n": 11, "x": 3}, True),
            ({"root": [1, 2, 3], "n": 3, "x": 1}, False),
            ({"root": [1, 2, 3], "n": 3, "x": 2}, True),
            ({"root": [1, 2, 3, 4, 5, 6, 7], "n": 7, "x": 1}, False)],
    source="new_p")
