"""Batch 020 of the new_p.txt import (20 problems).

Skips recorded in `_skips.py` for this group:
  - `all-oone-data-structure`, `subrectangle-queries`,
    `insert-delete-getrandom-o1-duplicates-allowed` (stateful design classes),
  - `unique-binary-search-trees-ii` (returns all BST shapes; the count is the
    existing `unique-binary-search-trees`),
  - `pancake-sorting`, `beautiful-array` (return any valid answer).

Reframes:
  - `find-elements-in-a-contaminated-binary-tree` -> take the contaminated tree plus
    a batch of `queries` and return one bool per query.

`all-paths-from-source-to-target` allows any output order -> COMPARE "unordered".

Trees are passed as LeetCode level-order arrays (None for a missing child) and
rebuilt inside each solution. Grids are passed as int[][] or list-of-strings.
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


def _rand_tree_shape(r, n):
    """Random tree serialized with all node values = -1 (a 'contaminated' shape)."""
    return _rand_tree_vals(r, n, -1, -1)


def _rand_tree(r):
    return _rand_tree_vals(r, r.randint(1, 14), -8, 8)


# =========================================================================== #
# brute / reference helpers
# =========================================================================== #
def _sumdist_brute(n, edges):
    from collections import defaultdict, deque
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    res = []
    for s in range(n):
        dist = {s: 0}
        dq = deque([s]); tot = 0
        while dq:
            x = dq.popleft()
            for y in adj[x]:
                if y not in dist:
                    dist[y] = dist[x] + 1; tot += dist[y]; dq.append(y)
        res.append(tot)
    return res


def _rand_tree_edges(r, n):
    edges = []
    for v in range(1, n):
        u = r.randint(0, v - 1)
        edges.append([u, v])
    return edges


def _sumdist_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(1, 12)
        out.append({"n": n, "edges": _rand_tree_edges(r, n)})
    return out


def _stitch_brute(clips, T):
    if T == 0:
        return 0
    cur = {0}
    seen = {0}
    steps = 0
    while cur:
        steps += 1
        nxt = set()
        for x in cur:
            for s, e in clips:
                if s <= x < e:
                    ne = min(e, T)
                    if ne >= T:
                        return steps
                    if ne not in seen:
                        seen.add(ne); nxt.add(ne)
        cur = nxt
    return -1


def _stitch_gen(r):
    out = []
    for _ in range(8):
        T = r.randint(0, 14)
        clips = []
        for _ in range(r.randint(1, 8)):
            a = r.randint(0, 14)
            b = r.randint(a, 15)
            clips.append([a, b])
        out.append({"clips": clips, "T": T})
    return out


def _findcity_brute(n, edges, distanceThreshold):
    import heapq
    from collections import defaultdict
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w)); adj[v].append((u, w))
    best_city, best_count = -1, n + 1
    for s in range(n):
        dist = {s: 0}
        pq = [(0, s)]
        while pq:
            d, x = heapq.heappop(pq)
            if d > dist.get(x, 1 << 60):
                continue
            for y, w in adj[x]:
                nd = d + w
                if nd < dist.get(y, 1 << 60):
                    dist[y] = nd; heapq.heappush(pq, (nd, y))
        c = sum(1 for j in range(n) if j != s and dist.get(j, 1 << 60) <= distanceThreshold)
        if c <= best_count:
            best_count, best_city = c, s
    return best_city


def _findcity_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(2, 6)
        pairs = set()
        edges = []
        for v in range(1, n):
            u = r.randint(0, v - 1)
            pairs.add((u, v)); edges.append([u, v, r.randint(1, 8)])
        for _ in range(r.randint(0, 2)):
            a, b = r.randint(0, n - 1), r.randint(0, n - 1)
            if a != b and (min(a, b), max(a, b)) not in pairs:
                pairs.add((min(a, b), max(a, b)))
                edges.append([min(a, b), max(a, b), r.randint(1, 8)])
        out.append({"n": n, "edges": edges, "distanceThreshold": r.randint(1, 16)})
    return out


def _rob_brute(root):
    import itertools
    left, right, val = _build_tree(root)
    nodes = list(val)
    edges = [(nd, left[nd]) for nd in left] + [(nd, right[nd]) for nd in right]
    best = 0
    for rr in range(len(nodes) + 1):
        for combo in itertools.combinations(nodes, rr):
            sset = set(combo)
            if all(not (a in sset and b in sset) for a, b in edges):
                best = max(best, sum(val[x] for x in combo))
    return best


def _rob_gen(r):
    return [{"root": _rand_tree_vals(r, r.randint(1, 11), 0, 12)} for _ in range(6)]


def _snake_brute(grid):
    from collections import deque
    n = len(grid)

    def empty(r, c):
        return 0 <= r < n and 0 <= c < n and grid[r][c] == 0

    start = ((0, 0), (0, 1))
    target = ((n - 1, n - 2), (n - 1, n - 1))
    seen = {start}
    dq = deque([(start, 0)])
    while dq:
        (a, b), d = dq.popleft()
        if (a, b) == target:
            return d
        (r1, c1), (r2, c2) = a, b
        moves = []
        if r1 == r2:  # horizontal
            if empty(r1, c2 + 1):
                moves.append(((r1, c1 + 1), (r1, c2 + 1)))
            if empty(r1 + 1, c1) and empty(r1 + 1, c2):
                moves.append(((r1 + 1, c1), (r1 + 1, c2)))
            if empty(r1 + 1, c1) and empty(r1 + 1, c2):
                moves.append(((r1, c1), (r1 + 1, c1)))
        else:          # vertical
            if empty(r1, c1 + 1) and empty(r2, c1 + 1):
                moves.append(((r1, c1 + 1), (r2, c1 + 1)))
            if empty(r2 + 1, c1):
                moves.append(((r1 + 1, c1), (r2 + 1, c1)))
            if empty(r1, c1 + 1) and empty(r2, c1 + 1):
                moves.append(((r1, c1), (r1, c1 + 1)))
        for st in moves:
            if st not in seen:
                seen.add(st); dq.append((st, d + 1))
    return -1


def _snake_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(2, 4)
        grid = [[0] * n for _ in range(n)]
        # start cells must be empty
        for i in range(n):
            for j in range(n):
                if (i, j) in ((0, 0), (0, 1)):
                    continue
                if r.random() < 0.18:
                    grid[i][j] = 1
        out.append({"grid": grid})
    return out


def _cinema_brute(n, reservedSeats):
    from collections import defaultdict
    rows = defaultdict(set)
    for r, c in reservedSeats:
        rows[r].add(c)
    total = (n - len(rows)) * 2
    groups = [{2, 3, 4, 5}, {4, 5, 6, 7}, {6, 7, 8, 9}]
    for occ in rows.values():
        free = [i for i, g in enumerate(groups) if not (g & occ)]
        best = 0
        for mask in range(8):
            sel = [i for i in range(3) if (mask >> i) & 1 and i in free]
            ok = all(not (groups[sel[a]] & groups[sel[b]])
                     for a in range(len(sel)) for b in range(a + 1, len(sel)))
            if ok:
                best = max(best, len(sel))
        total += best
    return total


def _cinema_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(1, 10)
        seen = set()
        reserved = []
        for _ in range(r.randint(1, 12)):
            row, col = r.randint(1, n), r.randint(1, 10)
            if (row, col) not in seen:
                seen.add((row, col)); reserved.append([row, col])
        out.append({"n": n, "reservedSeats": reserved})
    return out


def _findelem_brute(root, queries):
    left, right, _ = _build_tree(root)
    present = set()

    def assign(node, v):
        if node is None:
            return
        present.add(v)
        assign(left.get(node), 2 * v + 1)
        assign(right.get(node), 2 * v + 2)

    if root and root[0] is not None:
        assign(0, 0)
    return [q in present for q in queries]


def _findelem_gen(r):
    out = []
    for _ in range(6):
        shape = _rand_tree_shape(r, r.randint(1, 12))
        queries = [r.randint(0, 30) for _ in range(r.randint(1, 6))]
        out.append({"root": shape, "queries": queries})
    return out


def _countsq_brute(matrix):
    m, n = len(matrix), len(matrix[0])
    total = 0
    for i in range(m):
        for j in range(n):
            side = 1
            while i + side <= m and j + side <= n:
                ok = all(matrix[a][b] == 1
                         for a in range(i, i + side) for b in range(j, j + side))
                if not ok:
                    break
                total += 1
                side += 1
    return total


def _countsq_gen(r):
    out = []
    for _ in range(6):
        m, n = r.randint(1, 5), r.randint(1, 5)
        out.append({"matrix": [[r.randint(0, 1) for _ in range(n)] for _ in range(m)]})
    return out


def _falling_brute(positions):
    xs = sorted(set([l for l, _ in positions] + [l + s for l, s in positions]))
    seg_h = {(xs[i], xs[i + 1]): 0 for i in range(len(xs) - 1)}
    res = []
    best = 0
    for (l, s) in positions:
        r = l + s
        affected = [seg for seg in seg_h if seg[0] >= l and seg[1] <= r]
        base = max((seg_h[seg] for seg in affected), default=0)
        for seg in affected:
            seg_h[seg] = base + s
        best = max(best, base + s)
        res.append(best)
    return res


def _falling_gen(r):
    out = []
    for _ in range(6):
        pos = []
        for _ in range(r.randint(1, 6)):
            pos.append([r.randint(1, 8), r.randint(1, 5)])
        out.append({"positions": pos})
    return out


def _minrect_brute(points):
    from itertools import combinations
    pts = set(map(tuple, points))
    best = float("inf")
    for four in combinations(map(tuple, points), 4):
        xs = sorted({p[0] for p in four})
        ys = sorted({p[1] for p in four})
        if len(xs) == 2 and len(ys) == 2:
            need = {(xs[0], ys[0]), (xs[0], ys[1]), (xs[1], ys[0]), (xs[1], ys[1])}
            if set(four) == need:
                best = min(best, (xs[1] - xs[0]) * (ys[1] - ys[0]))
    return 0 if best == float("inf") else best


def _minrect_gen(r):
    out = []
    for _ in range(6):
        seen = set()
        pts = []
        for _ in range(r.randint(1, 9)):
            p = (r.randint(0, 5), r.randint(0, 5))
            if p not in seen:
                seen.add(p); pts.append([p[0], p[1]])
        out.append({"points": pts})
    return out


def _vert_brute(root):
    from collections import deque, defaultdict
    left, right, val = _build_tree(root)
    if not val:
        return []
    nodes = []
    dq = deque([(0, 0, 0)])
    while dq:
        node, x, y = dq.popleft()
        nodes.append((x, y, val[node]))
        if left.get(node) is not None:
            dq.append((left[node], x - 1, y - 1))
        if right.get(node) is not None:
            dq.append((right[node], x + 1, y - 1))
    cols = defaultdict(list)
    for x, y, v in nodes:
        cols[x].append((y, v))
    return [[v for _, v in sorted(cols[x], key=lambda t: (-t[0], t[1]))] for x in sorted(cols)]


def _vert_gen(r):
    return [{"root": _rand_tree_vals(r, r.randint(1, 14), 0, 20)} for _ in range(6)]


def _box_brute(grid):
    from collections import deque
    m, n = len(grid), len(grid[0])
    box = player = target = None
    for i in range(m):
        for j in range(n):
            ch = grid[i][j]
            if ch == "B":
                box = (i, j)
            elif ch == "S":
                player = (i, j)
            elif ch == "T":
                target = (i, j)

    def ok(r, c):
        return 0 <= r < m and 0 <= c < n and grid[r][c] != "#"

    def can_reach(s, e, blocked):
        if s == e:
            return True
        st = [s]; seen = {s, blocked}
        while st:
            r, c = st.pop()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if ok(nr, nc) and (nr, nc) not in seen:
                    if (nr, nc) == e:
                        return True
                    seen.add((nr, nc)); st.append((nr, nc))
        return False

    start = (box, player)
    dist = {start: 0}
    dq = deque([start])
    while dq:
        b, p = dq.popleft()
        d = dist[(b, p)]
        if b == target:
            return d
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (b[0] + dr, b[1] + dc)
            pp = (b[0] - dr, b[1] - dc)
            if ok(*nb) and ok(*pp) and can_reach(p, pp, b):
                ns = (nb, b)
                if ns not in dist:
                    dist[ns] = d + 1; dq.append(ns)
    return -1


def _box_gen(r):
    out = []
    for _ in range(5):
        m, n = r.randint(3, 5), r.randint(3, 5)
        grid = [["#" if (i in (0, m - 1) or j in (0, n - 1)) else "."
                 for j in range(n)] for i in range(m)]
        interior = [(i, j) for i in range(1, m - 1) for j in range(1, n - 1)]
        if len(interior) < 3:
            continue
        cells = r.sample(interior, 3)
        (si, sj), (bi, bj), (ti, tj) = cells
        grid[si][sj] = "S"; grid[bi][bj] = "B"; grid[ti][tj] = "T"
        rest = [c for c in interior if c not in cells]
        for c in r.sample(rest, min(len(rest), r.randint(0, 2))):
            grid[c[0]][c[1]] = "#"
        out.append({"grid": ["".join(row) for row in grid]})
    return out


def _maxdiff_brute(root):
    left, right, val = _build_tree(root)
    best = 0

    def dfs(node, ancestors):
        v = val[node]
        for a in ancestors:
            if abs(v - a) > best[0]:
                best[0] = abs(v - a)
        for ch in (left.get(node), right.get(node)):
            if ch is not None:
                dfs(ch, ancestors + [v])

    best = [0]
    dfs(0, [])
    return best[0]


def _maxlevel_brute(root):
    from collections import deque
    left, right, val = _build_tree(root)
    best_level, best_sum, level = 1, None, 1
    q = deque([0])
    while q:
        s = sum(val[x] for x in q)
        if best_sum is None or s > best_sum:
            best_sum, best_level = s, level
        nxt = []
        for x in q:
            if left.get(x) is not None:
                nxt.append(left[x])
            if right.get(x) is not None:
                nxt.append(right[x])
        q = deque(nxt); level += 1
    return best_level


def _preimage_brute(K):
    def f(x):
        c = 0
        while x > 0:
            x //= 5; c += x
        return c
    cnt, x = 0, 0
    while f(x) <= K + 5:
        if f(x) == K:
            cnt += 1
        x += 1
    return cnt


def _preimage_gen(r):
    return [{"K": r.randint(0, 60)} for _ in range(8)]


def _allpaths_brute(graph):
    from collections import deque
    n = len(graph)
    res = []
    dq = deque([[0]])
    while dq:
        path = dq.popleft()
        node = path[-1]
        if node == n - 1:
            res.append(path); continue
        for nb in graph[node]:
            dq.append(path + [nb])
    return res


def _allpaths_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(2, 7)
        graph = []
        for i in range(n):
            if i == n - 1:
                graph.append([])
            else:
                succ = [j for j in range(i + 1, n) if r.random() < 0.5]
                if not succ:
                    succ = [r.randint(i + 1, n - 1)]
                graph.append(succ)
        out.append({"graph": graph})
    return out


def _count_from(pairs):
    arr = [0] * 256
    for k, v in pairs.items():
        arr[k] = v
    return arr


def _stats_brute(count):
    sample = []
    for k in range(256):
        sample.extend([k] * count[k])
    sample.sort()
    n = len(sample)
    mn = float(sample[0]); mx = float(sample[-1])
    mean = round(sum(sample) / n, 5)
    if n % 2 == 1:
        med = float(sample[n // 2])
    else:
        med = (sample[n // 2 - 1] + sample[n // 2]) / 2
    mode = float(max(range(256), key=lambda k: count[k]))
    return [mn, mx, mean, round(med, 5), mode]


def _stats_gen(r):
    out = []
    for _ in range(6):
        d = {}
        for _ in range(r.randint(1, 5)):
            d[r.randint(0, 255)] = r.randint(1, 4)
        if not d:
            d[r.randint(0, 255)] = 1
        out.append({"count": _count_from(d)})
    return out


# =========================================================================== #
# 1. Sum of Distances in Tree
# =========================================================================== #
add("sum-of-distances-in-tree", "Sum of Distances in Tree", "hard",
    ["tree", "graph", "depth-first-search", "dynamic-programming"],
    "sumOfDistancesInTree", [("n", "int"), ("edges", "int[][]")], "int[]",
    """
An undirected, connected tree has `n` nodes labelled `0..n-1` and `n - 1` edges;
`edges[i] = [a, b]` joins nodes `a` and `b`. Return a list `ans` where `ans[i]` is
the sum of the distances between node `i` and every other node.

**Example**
```
n = 6, edges = [[0,1],[0,2],[2,3],[2,4],[2,5]]   ->  [8,12,6,10,10,10]
```

**Constraints:** `1 <= n <= 10^4`; the input forms a valid tree.
""",
    """def sumOfDistancesInTree(n, edges):
    from collections import defaultdict
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    count = [1] * n
    ans = [0] * n
    parent = [-1] * n
    visited = [False] * n
    order = []
    stack = [0]; visited[0] = True
    while stack:
        node = stack.pop(); order.append(node)
        for nb in adj[node]:
            if not visited[nb]:
                visited[nb] = True; parent[nb] = node; stack.append(nb)
    for node in reversed(order):
        p = parent[node]
        if p != -1:
            count[p] += count[node]
            ans[p] += ans[node] + count[node]
    for node in order[1:]:
        p = parent[node]
        ans[node] = ans[p] - count[node] + (n - count[node])
    return ans
""",
    visible=[{"n": 6, "edges": [[0, 1], [0, 2], [2, 3], [2, 4], [2, 5]]}],
    hidden=[{"n": 1, "edges": []}, {"n": 2, "edges": [[0, 1]]},
            {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]}],
    gen=_sumdist_gen,
    brute=_sumdist_brute,
    checks=[({"n": 6, "edges": [[0, 1], [0, 2], [2, 3], [2, 4], [2, 5]]}, [8, 12, 6, 10, 10, 10]),
            ({"n": 1, "edges": []}, [0]), ({"n": 2, "edges": [[0, 1]]}, [1, 1])],
    source="new_p")


# =========================================================================== #
# 2. Video Stitching
# =========================================================================== #
add("video-stitching", "Video Stitching", "medium",
    ["array", "dynamic-programming", "greedy"], "videoStitching",
    [("clips", "int[][]"), ("T", "int")], "int",
    """
Video clips cover a sporting event lasting `T` seconds. Clip `clips[i] = [a, b]`
covers the interval `[a, b]` and may be cut freely. Return the minimum number of
clips needed to cover `[0, T]` entirely, or `-1` if it is impossible.

**Examples**
```
clips = [[0,2],[4,6],[8,10],[1,9],[1,5],[5,9]], T = 10   ->  3
clips = [[0,1],[1,2]], T = 5                              ->  -1
clips = [[0,4],[2,8]], T = 5                              ->  2
```

**Constraints:** `1 <= len(clips) <= 100`, `0 <= a <= b <= 100`, `0 <= T <= 100`.
""",
    """def videoStitching(clips, T):
    INF = float("inf")
    dp = [0] + [INF] * T
    for i in range(1, T + 1):
        for s, e in clips:
            if s < i <= e and dp[s] + 1 < dp[i]:
                dp[i] = dp[s] + 1
    return -1 if dp[T] == INF else dp[T]
""",
    visible=[{"clips": [[0, 2], [4, 6], [8, 10], [1, 9], [1, 5], [5, 9]], "T": 10},
             {"clips": [[0, 1], [1, 2]], "T": 5},
             {"clips": [[0, 4], [2, 8]], "T": 5}],
    hidden=[{"clips": [[0, 1]], "T": 0}, {"clips": [[1, 2]], "T": 5},
            {"clips": [[0, 5]], "T": 5},
            {"clips": [[0, 1], [6, 8], [0, 2], [5, 6], [0, 4], [0, 3], [6, 7], [1, 3],
                       [4, 7], [1, 4], [2, 5], [2, 6], [3, 4], [4, 5], [5, 7], [6, 9]], "T": 9}],
    gen=_stitch_gen,
    brute=_stitch_brute,
    checks=[({"clips": [[0, 2], [4, 6], [8, 10], [1, 9], [1, 5], [5, 9]], "T": 10}, 3),
            ({"clips": [[0, 1], [1, 2]], "T": 5}, -1),
            ({"clips": [[0, 4], [2, 8]], "T": 5}, 2),
            ({"clips": [[0, 1]], "T": 0}, 0)],
    source="new_p")


# =========================================================================== #
# 3. Find the City With the Smallest Number of Neighbors at a Threshold Distance
# =========================================================================== #
add("find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance",
    "Find the City With the Smallest Number of Neighbors at a Threshold Distance",
    "medium", ["graph", "shortest-path"], "findTheCity",
    [("n", "int"), ("edges", "int[][]"), ("distanceThreshold", "int")], "int",
    """
There are `n` cities `0..n-1`. Each `edges[i] = [a, b, w]` is a bidirectional road of
weight `w`. For a threshold `distanceThreshold`, find the city that can reach the
**fewest** other cities within total path distance `<= distanceThreshold`. If several
cities tie, return the one with the **greatest** index.

**Examples**
```
n = 4, edges = [[0,1,3],[1,2,1],[1,3,4],[2,3,1]], distanceThreshold = 4   ->  3
n = 5, edges = [[0,1,2],[0,4,8],[1,2,3],[1,4,2],[2,3,1],[3,4,1]], distanceThreshold = 2 -> 0
```

**Constraints:** `2 <= n <= 100`, `0 <= a < b < n`, `1 <= w, distanceThreshold <= 10^4`.
""",
    """def findTheCity(n, edges, distanceThreshold):
    INF = float("inf")
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)
        dist[v][u] = min(dist[v][u], w)
    for k in range(n):
        dk = dist[k]
        for i in range(n):
            dik = dist[i][k]
            if dik == INF:
                continue
            di = dist[i]
            for j in range(n):
                nd = dik + dk[j]
                if nd < di[j]:
                    di[j] = nd
    best_city, best_count = -1, n + 1
    for i in range(n):
        c = sum(1 for j in range(n) if j != i and dist[i][j] <= distanceThreshold)
        if c <= best_count:
            best_count, best_city = c, i
    return best_city
""",
    visible=[{"n": 4, "edges": [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]], "distanceThreshold": 4},
             {"n": 5, "edges": [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]],
              "distanceThreshold": 2}],
    hidden=[{"n": 2, "edges": [[0, 1, 10]], "distanceThreshold": 5},
            {"n": 3, "edges": [[0, 1, 1], [1, 2, 1]], "distanceThreshold": 2}],
    gen=_findcity_gen,
    brute=_findcity_brute,
    checks=[({"n": 4, "edges": [[0, 1, 3], [1, 2, 1], [1, 3, 4], [2, 3, 1]], "distanceThreshold": 4}, 3),
            ({"n": 5, "edges": [[0, 1, 2], [0, 4, 8], [1, 2, 3], [1, 4, 2], [2, 3, 1], [3, 4, 1]],
              "distanceThreshold": 2}, 0),
            ({"n": 2, "edges": [[0, 1, 10]], "distanceThreshold": 5}, 1)],
    source="new_p")


# =========================================================================== #
# 4. House Robber III
# =========================================================================== #
add("house-robber-iii", "House Robber III", "medium",
    ["tree", "dynamic-programming", "depth-first-search"], "rob",
    [("root", "int[]")], "int",
    """
Houses form a binary tree, given as a LeetCode **level-order array** (`null`/`None`
marks a missing child) and rebuilt inside your function. The alarm triggers if two
**directly-linked** houses (a parent and its child) are both robbed. Return the
maximum total amount that can be robbed without alerting the police.

**Examples**
```
root = [3,2,3,null,3,null,1]   ->  7   (3 + 3 + 1)
root = [3,4,5,1,3,null,1]      ->  9   (4 + 5)
```

**Constraints:** `1 <= number of nodes <= 10^4`, `0 <= node value <= 10^4`.
""",
    """def rob(root):
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

    def dfs(node):
        if node is None:
            return (0, 0)
        l = dfs(left.get(node))
        r = dfs(right.get(node))
        rob_this = val[node] + l[1] + r[1]
        skip = max(l) + max(r)
        return (rob_this, skip)

    return max(dfs(0))
""",
    visible=[{"root": [3, 2, 3, None, 3, None, 1]}, {"root": [3, 4, 5, 1, 3, None, 1]}],
    hidden=[{"root": [0]}, {"root": [5]}, {"root": [1, 2, 3]},
            {"root": [4, 1, None, 2, None, 3]}],
    gen=_rob_gen,
    brute=_rob_brute,
    checks=[({"root": [3, 2, 3, None, 3, None, 1]}, 7),
            ({"root": [3, 4, 5, 1, 3, None, 1]}, 9), ({"root": [0]}, 0)],
    source="new_p")


# =========================================================================== #
# 5. Minimum Moves to Reach Target with Rotations
# =========================================================================== #
add("minimum-moves-to-reach-target-with-rotations",
    "Minimum Moves to Reach Target with Rotations", "hard",
    ["array", "breadth-first-search", "matrix"], "minimumMoves",
    [("grid", "int[][]")], "int",
    """
In an `n x n` grid (`0` = empty, `1` = blocked), a snake occupies two cells and
starts horizontally at `(0,0)` and `(0,1)`. Each move it may:

- move right one cell (if the destination cells are empty),
- move down one cell (if the destination cells are empty),
- rotate **clockwise** from horizontal to vertical when the two cells directly below
  it are both empty: `(r,c),(r,c+1)` -> `(r,c),(r+1,c)`,
- rotate **counter-clockwise** from vertical to horizontal when the two cells
  directly to its right are both empty: `(r,c),(r+1,c)` -> `(r,c),(r,c+1)`.

Return the minimum number of moves so the snake reaches `(n-1,n-2)` and `(n-1,n-1)`,
or `-1` if impossible.

**Example**
```
grid = [[0,0,0,0,0,1],[1,1,0,0,1,0],[0,0,0,0,1,1],
        [0,0,1,0,1,0],[0,1,1,0,0,0],[0,1,1,0,0,0]]   ->  11
```

**Constraints:** `2 <= n <= 100`; the snake starts on empty cells.
""",
    """def minimumMoves(grid):
    from collections import deque
    n = len(grid)
    start = (0, 0, 0)            # row, col, orientation (0 horizontal, 1 vertical)
    target = (n - 1, n - 2, 0)
    seen = {start}
    dq = deque([(start, 0)])
    while dq:
        (r, c, o), d = dq.popleft()
        if (r, c, o) == target:
            return d
        nxts = []
        if o == 0:  # horizontal: cells (r,c),(r,c+1)
            if c + 2 < n and grid[r][c + 2] == 0:
                nxts.append((r, c + 1, 0))
            if r + 1 < n and grid[r + 1][c] == 0 and grid[r + 1][c + 1] == 0:
                nxts.append((r + 1, c, 0))
                nxts.append((r, c, 1))
        else:       # vertical: cells (r,c),(r+1,c)
            if c + 1 < n and grid[r][c + 1] == 0 and grid[r + 1][c + 1] == 0:
                nxts.append((r, c + 1, 1))
                nxts.append((r, c, 0))
            if r + 2 < n and grid[r + 2][c] == 0:
                nxts.append((r + 1, c, 1))
        for st in nxts:
            if st not in seen:
                seen.add(st); dq.append((st, d + 1))
    return -1
""",
    visible=[{"grid": [[0, 0, 0, 0, 0, 1], [1, 1, 0, 0, 1, 0], [0, 0, 0, 0, 1, 1],
                      [0, 0, 1, 0, 1, 0], [0, 1, 1, 0, 0, 0], [0, 1, 1, 0, 0, 0]]},
             {"grid": [[0, 0, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1], [1, 1, 0, 0, 0, 1],
                      [1, 1, 1, 0, 0, 1], [1, 1, 1, 0, 0, 1], [1, 1, 1, 0, 0, 0]]}],
    hidden=[{"grid": [[0, 0], [0, 0]]}, {"grid": [[0, 0], [1, 0]]},
            {"grid": [[0, 0, 0], [0, 0, 0], [0, 0, 0]]}],
    gen=_snake_gen,
    brute=_snake_brute,
    checks=[({"grid": [[0, 0, 0, 0, 0, 1], [1, 1, 0, 0, 1, 0], [0, 0, 0, 0, 1, 1],
                      [0, 0, 1, 0, 1, 0], [0, 1, 1, 0, 0, 0], [0, 1, 1, 0, 0, 0]]}, 11),
            ({"grid": [[0, 0, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1], [1, 1, 0, 0, 0, 1],
                      [1, 1, 1, 0, 0, 1], [1, 1, 1, 0, 0, 1], [1, 1, 1, 0, 0, 0]]}, 9),
            ({"grid": [[0, 0], [0, 0]]}, 1), ({"grid": [[0, 0], [1, 0]]}, -1)],
    source="new_p")


# =========================================================================== #
# 6. Cinema Seat Allocation
# =========================================================================== #
add("cinema-seat-allocation", "Cinema Seat Allocation", "medium",
    ["array", "hash-table", "greedy", "bit-manipulation"], "maxNumberOfFamilies",
    [("n", "int"), ("reservedSeats", "int[][]")], "int",
    """
A cinema has `n` rows numbered `1..n`, each with seats `1..10`. Aisles split a row
into seats `1`, `2..3`, `4..7`, `8..9`, `10`. A four-person family needs four
**adjacent** seats; the only spans that work are `[2,3,4,5]`, `[4,5,6,7]`, and
`[6,7,8,9]`. Given the already-reserved seats `reservedSeats[i] = [row, col]`, return
the maximum number of four-person families that can be seated.

**Examples**
```
n = 3, reservedSeats = [[1,2],[1,3],[1,8],[2,6],[3,1],[3,10]]   ->  4
n = 2, reservedSeats = [[2,1],[1,8],[2,6]]                      ->  2
```

**Constraints:** `1 <= n <= 10^9`, `1 <= len(reservedSeats) <= min(10*n, 10^4)`.
""",
    """def maxNumberOfFamilies(n, reservedSeats):
    from collections import defaultdict
    rows = defaultdict(set)
    for r, c in reservedSeats:
        rows[r].add(c)
    total = (n - len(rows)) * 2
    for occ in rows.values():
        left = not (occ & {2, 3, 4, 5})
        mid = not (occ & {4, 5, 6, 7})
        right = not (occ & {6, 7, 8, 9})
        if left and right:
            total += 2
        elif left or mid or right:
            total += 1
    return total
""",
    visible=[{"n": 3, "reservedSeats": [[1, 2], [1, 3], [1, 8], [2, 6], [3, 1], [3, 10]]},
             {"n": 2, "reservedSeats": [[2, 1], [1, 8], [2, 6]]},
             {"n": 4, "reservedSeats": [[4, 3], [1, 4], [4, 6], [1, 7]]}],
    hidden=[{"n": 1, "reservedSeats": [[1, 5]]}, {"n": 1, "reservedSeats": [[1, 1]]},
            {"n": 5, "reservedSeats": [[1, 5]]}],
    gen=_cinema_gen,
    brute=_cinema_brute,
    checks=[({"n": 3, "reservedSeats": [[1, 2], [1, 3], [1, 8], [2, 6], [3, 1], [3, 10]]}, 4),
            ({"n": 2, "reservedSeats": [[2, 1], [1, 8], [2, 6]]}, 2),
            ({"n": 4, "reservedSeats": [[4, 3], [1, 4], [4, 6], [1, 7]]}, 4),
            ({"n": 1, "reservedSeats": [[1, 1]]}, 2)],
    source="new_p")


# =========================================================================== #
# 7. Find Elements in a Contaminated Binary Tree  (reframed -> batch of queries)
# =========================================================================== #
add("find-elements-in-a-contaminated-binary-tree",
    "Find Elements in a Contaminated Binary Tree", "medium",
    ["tree", "hash-table", "depth-first-search"], "findElements",
    [("root", "int[]"), ("queries", "int[]")], "bool[]",
    """
A binary tree obeys: `root.val == 0`, a left child's value is `2*x + 1`, and a right
child's value is `2*x + 2`, where `x` is the parent's value. The tree is
*contaminated* — every stored value was replaced by `-1` — and is given as a LeetCode
**level-order array** of `-1`/`None` (so it conveys only the tree's **shape**).

First recover the original values from the shape, then for each value in `queries`
report whether that value exists in the recovered tree. Return one bool per query.

**Examples**
```
root = [-1,null,-1],     queries = [1,2]     ->  [false,true]
root = [-1,-1,-1,-1,-1],  queries = [1,3,5]   ->  [true,true,false]
```

**Constraints:** tree height `<= 20`, `1 <= number of nodes <= 10^4`,
`0 <= query value <= 10^6`.
""",
    """def findElements(root, queries):
    from collections import deque
    present = set()
    if root and root[0] is not None:
        assigned = {0: 0}
        present.add(0)
        q = deque([0]); nid, i, n = 1, 1, len(root)
        while q and i < n:
            cur = q.popleft()
            if i < n:
                v = root[i]; i += 1
                if v is not None:
                    cv = 2 * assigned[cur] + 1
                    assigned[nid] = cv; present.add(cv); q.append(nid); nid += 1
            if i < n:
                v = root[i]; i += 1
                if v is not None:
                    cv = 2 * assigned[cur] + 2
                    assigned[nid] = cv; present.add(cv); q.append(nid); nid += 1
    return [qv in present for qv in queries]
""",
    visible=[{"root": [-1, None, -1], "queries": [1, 2]},
             {"root": [-1, -1, -1, -1, -1], "queries": [1, 3, 5]},
             {"root": [-1, None, -1, -1, None, -1], "queries": [2, 3, 4, 5]}],
    hidden=[{"root": [-1], "queries": [0, 1]},
            {"root": [-1, -1, -1], "queries": [0, 1, 2, 3]}],
    gen=_findelem_gen,
    brute=_findelem_brute,
    checks=[({"root": [-1, None, -1], "queries": [1, 2]}, [False, True]),
            ({"root": [-1, -1, -1, -1, -1], "queries": [1, 3, 5]}, [True, True, False]),
            ({"root": [-1, None, -1, -1, None, -1], "queries": [2, 3, 4, 5]},
             [True, False, False, True]),
            ({"root": [-1], "queries": [0, 1]}, [True, False])],
    source="new_p")


# =========================================================================== #
# 8. Count Square Submatrices with All Ones
# =========================================================================== #
add("count-square-submatrices-with-all-ones", "Count Square Submatrices with All Ones",
    "medium", ["array", "dynamic-programming", "matrix"], "countSquares",
    [("matrix", "int[][]")], "int",
    """
Given an `m x n` matrix of `0`s and `1`s, return how many square submatrices contain
only `1`s.

**Examples**
```
matrix = [[0,1,1,1],[1,1,1,1],[0,1,1,1]]   ->  15
matrix = [[1,0,1],[1,1,0],[1,1,0]]         ->  7
```

**Constraints:** `1 <= m, n <= 300`, each entry is `0` or `1`.
""",
    """def countSquares(matrix):
    m, n = len(matrix), len(matrix[0])
    dp = [[0] * n for _ in range(m)]
    total = 0
    for i in range(m):
        for j in range(n):
            if matrix[i][j] == 1:
                if i == 0 or j == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
                total += dp[i][j]
    return total
""",
    visible=[{"matrix": [[0, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]]},
             {"matrix": [[1, 0, 1], [1, 1, 0], [1, 1, 0]]}],
    hidden=[{"matrix": [[0]]}, {"matrix": [[1]]}, {"matrix": [[1, 1], [1, 1]]},
            {"matrix": [[0, 0], [0, 0]]}],
    gen=_countsq_gen,
    brute=_countsq_brute,
    checks=[({"matrix": [[0, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]]}, 15),
            ({"matrix": [[1, 0, 1], [1, 1, 0], [1, 1, 0]]}, 7),
            ({"matrix": [[1, 1], [1, 1]]}, 5)],
    source="new_p")


# =========================================================================== #
# 9. Falling Squares
# =========================================================================== #
add("falling-squares", "Falling Squares", "hard",
    ["array", "segment-tree", "ordered-set"], "fallingSquares",
    [("positions", "int[][]")], "int[]",
    """
Squares are dropped onto a number line one at a time. The `i`-th drop
`positions[i] = [left, side]` places a square whose left edge is at `left` with side
length `side`. Each square falls from above and sticks the moment it lands on the
number line or on top of any square it overlaps (sharing only a corner does **not**
count). After each drop, record the current tallest stack height. Return the list of
these heights.

**Example**
```
positions = [[1,2],[2,3],[6,1]]   ->  [2,5,5]
```

**Constraints:** `1 <= len(positions) <= 1000`, `1 <= left, side <= 10^8`.
""",
    """def fallingSquares(positions):
    n = len(positions)
    heights = [0] * n
    res = []
    best = 0
    for i, (l, s) in enumerate(positions):
        r = l + s
        base = 0
        for j in range(i):
            lj, sj = positions[j]
            if l < lj + sj and lj < r:
                base = max(base, heights[j])
        heights[i] = base + s
        best = max(best, heights[i])
        res.append(best)
    return res
""",
    visible=[{"positions": [[1, 2], [2, 3], [6, 1]]}],
    hidden=[{"positions": [[100, 100], [200, 100]]}, {"positions": [[1, 5]]},
            {"positions": [[1, 2], [2, 3]]}, {"positions": [[2, 1], [1, 1], [3, 1]]}],
    gen=_falling_gen,
    brute=_falling_brute,
    checks=[({"positions": [[1, 2], [2, 3], [6, 1]]}, [2, 5, 5]),
            ({"positions": [[100, 100], [200, 100]]}, [100, 100]),
            ({"positions": [[1, 2], [2, 3]]}, [2, 5])],
    source="new_p")


# =========================================================================== #
# 10. Minimum Area Rectangle
# =========================================================================== #
add("minimum-area-rectangle", "Minimum Area Rectangle", "medium",
    ["array", "hash-table", "math", "geometry"], "minAreaRect",
    [("points", "int[][]")], "int",
    """
Given distinct points in the plane, find the minimum area of a rectangle whose sides
are parallel to the axes and whose four corners are all among the points. Return `0`
if no such rectangle exists.

**Examples**
```
points = [[1,1],[1,3],[3,1],[3,3],[2,2]]            ->  4
points = [[1,1],[1,3],[3,1],[3,3],[4,1],[4,3]]      ->  2
```

**Constraints:** `1 <= len(points) <= 500`, `0 <= coordinate <= 4*10^4`, points are
distinct.
""",
    """def minAreaRect(points):
    pts = set(map(tuple, points))
    best = float("inf")
    P = [tuple(p) for p in points]
    for i in range(len(P)):
        x1, y1 = P[i]
        for j in range(i + 1, len(P)):
            x2, y2 = P[j]
            if x1 != x2 and y1 != y2 and (x1, y2) in pts and (x2, y1) in pts:
                area = abs(x1 - x2) * abs(y1 - y2)
                if area < best:
                    best = area
    return 0 if best == float("inf") else best
""",
    visible=[{"points": [[1, 1], [1, 3], [3, 1], [3, 3], [2, 2]]},
             {"points": [[1, 1], [1, 3], [3, 1], [3, 3], [4, 1], [4, 3]]}],
    hidden=[{"points": [[0, 0]]}, {"points": [[0, 0], [1, 1]]},
            {"points": [[0, 0], [0, 1], [1, 0], [1, 1]]}],
    gen=_minrect_gen,
    brute=_minrect_brute,
    checks=[({"points": [[1, 1], [1, 3], [3, 1], [3, 3], [2, 2]]}, 4),
            ({"points": [[1, 1], [1, 3], [3, 1], [3, 3], [4, 1], [4, 3]]}, 2),
            ({"points": [[0, 0], [0, 1], [1, 0], [1, 1]]}, 1)],
    source="new_p")


# =========================================================================== #
# 11. Vertical Order Traversal of a Binary Tree
# =========================================================================== #
add("vertical-order-traversal-of-a-binary-tree", "Vertical Order Traversal of a Binary Tree",
    "hard", ["tree", "depth-first-search", "breadth-first-search", "sorting"],
    "verticalTraversal", [("root", "int[]")], "int[][]",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. The root is at column `0`, row `0`;
a left child is at `(col-1, row+1)` and a right child at `(col+1, row+1)`.

Return the vertical order traversal: process columns from left to right; within a
column list nodes from the top row down; nodes sharing the same `(col, row)` are
ordered by **increasing value**.

**Examples**
```
root = [3,9,20,null,null,15,7]   ->  [[9],[3,15],[20],[7]]
root = [1,2,3,4,5,6,7]           ->  [[4],[2],[1,5,6],[3],[7]]
```

**Constraints:** `1 <= number of nodes <= 1000`, `0 <= node value <= 1000`.
""",
    """def verticalTraversal(root):
    from collections import deque, defaultdict
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
    nodes = []

    def dfs(node, x, y):
        if node is None:
            return
        nodes.append((x, y, val[node]))
        dfs(left.get(node), x - 1, y + 1)
        dfs(right.get(node), x + 1, y + 1)

    dfs(0, 0, 0)
    cols = defaultdict(list)
    for x, y, v in nodes:
        cols[x].append((y, v))
    return [[v for _, v in sorted(cols[x], key=lambda t: (t[0], t[1]))] for x in sorted(cols)]
""",
    visible=[{"root": [3, 9, 20, None, None, 15, 7]}, {"root": [1, 2, 3, 4, 5, 6, 7]}],
    hidden=[{"root": [0]}, {"root": [1, 2]}, {"root": [1, 2, 3, 4, 6, 5, 7]}],
    gen=_vert_gen,
    brute=_vert_brute,
    checks=[({"root": [3, 9, 20, None, None, 15, 7]}, [[9], [3, 15], [20], [7]]),
            ({"root": [1, 2, 3, 4, 5, 6, 7]}, [[4], [2], [1, 5, 6], [3], [7]]),
            ({"root": [0]}, [[0]])],
    source="new_p")


# =========================================================================== #
# 12. Brace Expansion II
# =========================================================================== #
add("brace-expansion-ii", "Brace Expansion II", "hard",
    ["string", "stack", "breadth-first-search"], "braceExpansionII",
    [("expression", "string")], "str[]",
    """
A grammar over lowercase letters builds sets of words:

- a single letter `x` denotes `{x}`;
- a comma-separated list inside braces is the **union** of its parts, e.g.
  `{a,b,c}` -> `{a,b,c}`;
- writing expressions next to each other is the set of **concatenations**, e.g.
  `{a,b}{c,d}` -> `{ac,ad,bc,bd}`.

Given such an `expression`, return the sorted list of distinct words it represents.

**Examples**
```
"{a,b}{c,{d,e}}"          ->  ["ac","ad","ae","bc","bd","be"]
"{{a,z},a{b,c},{ab,z}}"   ->  ["a","ab","ac","z"]
```

**Constraints:** `1 <= len(expression) <= 60`; characters are `{`, `}`, `,`, or
lowercase letters.
""",
    """def braceExpansionII(expression):
    s = expression
    pos = [0]

    def parse():
        result = set()
        cur = {""}
        while pos[0] < len(s) and s[pos[0]] != "}":
            ch = s[pos[0]]
            if ch == "{":
                pos[0] += 1
                sub = parse()
                pos[0] += 1  # skip '}'
                cur = {a + b for a in cur for b in sub}
            elif ch == ",":
                pos[0] += 1
                result |= cur
                cur = {""}
            else:
                j = pos[0]
                while j < len(s) and s[j].isalpha():
                    j += 1
                token = s[pos[0]:j]
                pos[0] = j
                cur = {a + token for a in cur}
        result |= cur
        return result

    return sorted(parse())
""",
    visible=[{"expression": "{a,b}{c,{d,e}}"}, {"expression": "{{a,z},a{b,c},{ab,z}}"},
             {"expression": "{a,b}{c,d}"}],
    hidden=[{"expression": "a"}, {"expression": "abc"}, {"expression": "{a,b,c}"},
            {"expression": "{{a,b},{b,c}}"}],
    checks=[({"expression": "{a,b}{c,{d,e}}"}, ["ac", "ad", "ae", "bc", "bd", "be"]),
            ({"expression": "{{a,z},a{b,c},{ab,z}}"}, ["a", "ab", "ac", "z"]),
            ({"expression": "{a,b}{c,d}"}, ["ac", "ad", "bc", "bd"]),
            ({"expression": "a"}, ["a"]),
            ({"expression": "{a,b,c}"}, ["a", "b", "c"]),
            ({"expression": "{{a,b},{b,c}}"}, ["a", "b", "c"]),
            ({"expression": "abc"}, ["abc"])],
    source="new_p")


# =========================================================================== #
# 13. Minimum Moves to Move a Box to Their Target Location
# =========================================================================== #
add("minimum-moves-to-move-a-box-to-their-target-location",
    "Minimum Moves to Move a Box to Their Target Location", "hard",
    ["array", "breadth-first-search", "heap", "matrix"], "minPushBox",
    [("grid", "string[]")], "int",
    """
A warehouse grid (`m` rows of equal-length strings) uses `'#'` for walls, `'.'` for
floor, `'S'` for the player, `'B'` for the single box, and `'T'` for the target. The
player walks up/down/left/right over floor cells and may **push** the box by standing
on the cell opposite the direction of motion (the cell the box moves into must be
floor). The player cannot walk through the box. Return the minimum number of
**pushes** to bring the box onto the target, or `-1` if impossible.

**Examples**
```
grid = ["######","#T#####","#..B.#","#.##.#","#...S#","######"]   ->  3
grid = ["######","#T#####","#..B.#","####.#","#...S#","######"]   ->  -1
```

**Constraints:** `1 <= m, n <= 20`; exactly one `S`, `B`, and `T`.
""",
    """def minPushBox(grid):
    import heapq
    m, n = len(grid), len(grid[0])
    box = player = target = None
    for i in range(m):
        for j in range(n):
            ch = grid[i][j]
            if ch == "B":
                box = (i, j)
            elif ch == "S":
                player = (i, j)
            elif ch == "T":
                target = (i, j)

    def ok(r, c):
        return 0 <= r < m and 0 <= c < n and grid[r][c] != "#"

    def reachable(start, end, blocked):
        if start == end:
            return True
        from collections import deque
        seen = {start, blocked}
        dq = deque([start])
        while dq:
            r, c = dq.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if ok(nr, nc) and (nr, nc) not in seen:
                    if (nr, nc) == end:
                        return True
                    seen.add((nr, nc)); dq.append((nr, nc))
        return False

    dist = {(box, player): 0}
    pq = [(0, box, player)]
    while pq:
        d, b, p = heapq.heappop(pq)
        if b == target:
            return d
        if d > dist.get((b, p), 1 << 60):
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (b[0] + dr, b[1] + dc)
            pp = (b[0] - dr, b[1] - dc)
            if ok(*nb) and ok(*pp) and reachable(p, pp, b):
                ns = (nb, b)
                if d + 1 < dist.get(ns, 1 << 60):
                    dist[ns] = d + 1
                    heapq.heappush(pq, (d + 1, nb, b))
    return -1
""",
    visible=[{"grid": ["######", "#T#####", "#..B.#", "#.##.#", "#...S#", "######"]},
             {"grid": ["######", "#T#####", "#..B.#", "####.#", "#...S#", "######"]}],
    hidden=[{"grid": ["######", "#T..##", "#.#B.#", "#....#", "#...S#", "######"]},
            {"grid": ["#######", "#S#.BT#", "#######"]}],
    gen=_box_gen,
    brute=_box_brute,
    checks=[({"grid": ["######", "#T#####", "#..B.#", "#.##.#", "#...S#", "######"]}, 3),
            ({"grid": ["######", "#T#####", "#..B.#", "####.#", "#...S#", "######"]}, -1),
            ({"grid": ["######", "#T..##", "#.#B.#", "#....#", "#...S#", "######"]}, 5),
            ({"grid": ["#######", "#S#.BT#", "#######"]}, -1)],
    source="new_p")


# =========================================================================== #
# 14. Text Justification
# =========================================================================== #
add("text-justification", "Text Justification", "hard",
    ["array", "string", "simulation"], "fullJustify",
    [("words", "string[]"), ("maxWidth", "int")], "str[]",
    """
Given an array of `words` and a width `maxWidth`, format the text so every line is
exactly `maxWidth` characters and fully justified. Pack greedily; distribute extra
spaces between words as evenly as possible, with the **left** gaps receiving more
spaces when they do not divide evenly. The **last** line is left-justified (single
spaces between words, padded with trailing spaces). A line with one word is also left-
justified.

**Example**
```
words = ["This","is","an","example","of","text","justification."], maxWidth = 16
->  ["This    is    an","example  of text","justification.  "]
```

**Constraints:** `1 <= len(words)`, each word length `<= maxWidth`, `1 <= maxWidth`.
""",
    """def fullJustify(words, maxWidth):
    res = []
    line = []
    length = 0
    for w in words:
        if length + len(line) + len(w) > maxWidth:
            spaces = maxWidth - length
            if len(line) == 1:
                res.append(line[0] + " " * spaces)
            else:
                gaps = len(line) - 1
                base, extra = divmod(spaces, gaps)
                row = ""
                for i, word in enumerate(line):
                    row += word
                    if i < gaps:
                        row += " " * (base + (1 if i < extra else 0))
                res.append(row)
            line = []
            length = 0
        line.append(w)
        length += len(w)
    last = " ".join(line)
    last += " " * (maxWidth - len(last))
    res.append(last)
    return res
""",
    visible=[{"words": ["This", "is", "an", "example", "of", "text", "justification."],
              "maxWidth": 16},
             {"words": ["What", "must", "be", "acknowledgment", "shall", "be"], "maxWidth": 16}],
    hidden=[{"words": ["Science", "is", "what", "we", "understand", "well", "enough", "to",
                       "explain", "to", "a", "computer.", "Art", "is", "everything", "else",
                       "we", "do"], "maxWidth": 20},
            {"words": ["a"], "maxWidth": 1},
            {"words": ["a", "b", "c"], "maxWidth": 3}],
    checks=[({"words": ["This", "is", "an", "example", "of", "text", "justification."],
              "maxWidth": 16},
             ["This    is    an", "example  of text", "justification.  "]),
            ({"words": ["What", "must", "be", "acknowledgment", "shall", "be"], "maxWidth": 16},
             ["What   must   be", "acknowledgment  ", "shall be        "]),
            ({"words": ["a"], "maxWidth": 1}, ["a"]),
            ({"words": ["a", "b", "c"], "maxWidth": 3}, ["a b", "c  "])],
    source="new_p")


# =========================================================================== #
# 15. Recover a Tree From Preorder Traversal
# =========================================================================== #
add("recover-a-tree-from-preorder-traversal", "Recover a Tree From Preorder Traversal",
    "hard", ["tree", "string", "depth-first-search"], "recoverFromPreorder",
    [("traversal", "string")], "int[]",
    """
A preorder DFS prints, for each node, `D` dashes (where `D` is the node's depth, root
depth `0`) followed by the node's value. A node with a single child always has that
child on the **left**. Given the printed string `traversal`, rebuild the tree and
return its **level-order array** (`None` for a missing child, trailing `None`s
trimmed).

**Examples**
```
"1-2--3--4-5--6--7"      ->  [1,2,5,3,4,6,7]
"1-2--3---4-5--6---7"    ->  [1,2,5,3,null,6,null,4,null,7]
"1-401--349---90--88"    ->  [1,401,null,349,88,90]
```

**Constraints:** `1 <= number of nodes <= 1000`, `1 <= node value <= 10^9`.
""",
    """def recoverFromPreorder(traversal):
    s = traversal
    tokens = []
    i = 0
    while i < len(s):
        d = 0
        while i < len(s) and s[i] == "-":
            d += 1; i += 1
        j = i
        while j < len(s) and s[j].isdigit():
            j += 1
        tokens.append((d, int(s[i:j])))
        i = j
    val, left, right = {}, {}, {}
    stack = []
    nid = 0
    for d, v in tokens:
        node = nid; nid += 1
        val[node] = v
        while stack and stack[-1][0] >= d:
            stack.pop()
        if stack:
            parent = stack[-1][1]
            if parent not in left:
                left[parent] = node
            else:
                right[parent] = node
        stack.append((d, node))
    from collections import deque
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
    visible=[{"traversal": "1-2--3--4-5--6--7"}, {"traversal": "1-2--3---4-5--6---7"},
             {"traversal": "1-401--349---90--88"}],
    hidden=[{"traversal": "1"}, {"traversal": "1-2"}, {"traversal": "10-5-6"}],
    checks=[({"traversal": "1-2--3--4-5--6--7"}, [1, 2, 5, 3, 4, 6, 7]),
            ({"traversal": "1-2--3---4-5--6---7"}, [1, 2, 5, 3, None, 6, None, 4, None, 7]),
            ({"traversal": "1-401--349---90--88"}, [1, 401, None, 349, 88, 90]),
            ({"traversal": "1"}, [1]), ({"traversal": "1-2"}, [1, 2]),
            ({"traversal": "10-5-6"}, [10, 5, 6])],
    source="new_p")


# =========================================================================== #
# 16. Statistics from a Large Sample
# =========================================================================== #
add("statistics-from-a-large-sample", "Statistics from a Large Sample", "medium",
    ["array", "math", "probability-and-statistics"], "sampleStats",
    [("count", "int[]")], "float[]",
    """
We sampled integers in the range `0..255`; `count[k]` is how many times the value `k`
appeared (`count` has length 256). Return `[minimum, maximum, mean, median, mode]` as
floating-point numbers, each **rounded to 5 decimal places**. The mode is guaranteed
to be unique. (For an even-sized sample, the median is the average of the two middle
values.)

**Examples**
```
count with {1:1, 2:3, 3:4}        ->  [1.0, 3.0, 2.375, 2.5, 3.0]
count with {1:4, 2:3, 3:2, 4:2}   ->  [1.0, 4.0, 2.18182, 2.0, 1.0]
```

**Constraints:** `count.length == 256`, `1 <= sum(count) <= 10^9`, unique mode.
""",
    """def sampleStats(count):
    total = sum(count)
    mn = next(k for k in range(256) if count[k] > 0)
    mx = next(k for k in range(255, -1, -1) if count[k] > 0)
    mean = sum(k * count[k] for k in range(256)) / total
    mode = max(range(256), key=lambda k: count[k])

    def kth(target):
        c = 0
        for k in range(256):
            c += count[k]
            if c >= target:
                return k

    if total % 2 == 1:
        median = float(kth(total // 2 + 1))
    else:
        median = (kth(total // 2) + kth(total // 2 + 1)) / 2
    return [float(mn), float(mx), round(mean, 5), round(median, 5), float(mode)]
""",
    visible=[{"count": _count_from({1: 1, 2: 3, 3: 4})},
             {"count": _count_from({1: 4, 2: 3, 3: 2, 4: 2})}],
    hidden=[{"count": _count_from({0: 1})}, {"count": _count_from({5: 2, 7: 2})},
            {"count": _count_from({0: 1, 255: 1, 100: 3})}],
    gen=_stats_gen,
    brute=_stats_brute,
    checks=[({"count": _count_from({1: 1, 2: 3, 3: 4})}, [1.0, 3.0, 2.375, 2.5, 3.0]),
            ({"count": _count_from({1: 4, 2: 3, 3: 2, 4: 2})}, [1.0, 4.0, 2.18182, 2.0, 1.0]),
            ({"count": _count_from({0: 1})}, [0.0, 0.0, 0.0, 0.0, 0.0])],
    source="new_p")


# =========================================================================== #
# 17. Maximum Difference Between Node and Ancestor
# =========================================================================== #
add("maximum-difference-between-node-and-ancestor", "Maximum Difference Between Node and Ancestor",
    "medium", ["tree", "depth-first-search"], "maxAncestorDiff",
    [("root", "int[]")], "int",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. Return the maximum value `|a - b|`
over all pairs of nodes where one is an **ancestor** of the other.

**Examples**
```
root = [8,3,10,1,6,null,14,null,null,4,7,13]   ->  7   (|8 - 1| = 7)
root = [1,null,2,null,0,3]                      ->  3
```

**Constraints:** `2 <= number of nodes <= 5000`, `0 <= node value <= 10^5`.
""",
    """def maxAncestorDiff(root):
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
    best = [0]

    def dfs(node, lo, hi):
        if node is None:
            return
        v = val[node]
        if abs(v - lo) > best[0]:
            best[0] = abs(v - lo)
        if abs(v - hi) > best[0]:
            best[0] = abs(v - hi)
        lo = min(lo, v); hi = max(hi, v)
        dfs(left.get(node), lo, hi)
        dfs(right.get(node), lo, hi)

    dfs(0, val[0], val[0])
    return best[0]
""",
    visible=[{"root": [8, 3, 10, 1, 6, None, 14, None, None, 4, 7, 13]},
             {"root": [1, None, 2, None, 0, 3]}],
    hidden=[{"root": [1, 2]}, {"root": [5, 0, 10]}, {"root": [3, 1, 4, 0, 2]}],
    gen=lambda r: [{"root": _rand_tree_vals(r, r.randint(2, 14), 0, 30)} for _ in range(6)],
    brute=_maxdiff_brute,
    checks=[({"root": [8, 3, 10, 1, 6, None, 14, None, None, 4, 7, 13]}, 7),
            ({"root": [1, None, 2, None, 0, 3]}, 3), ({"root": [1, 2]}, 1)],
    source="new_p")


# =========================================================================== #
# 18. Maximum Level Sum of a Binary Tree
# =========================================================================== #
add("maximum-level-sum-of-a-binary-tree", "Maximum Level Sum of a Binary Tree", "medium",
    ["tree", "breadth-first-search"], "maxLevelSum", [("root", "int[]")], "int",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. Levels are numbered from `1` at the
root. Return the **smallest** level whose node values sum to the maximum.

**Examples**
```
root = [1,7,0,7,-8,null,null]   ->  2   (level 2 sum = 7 is maximal)
```

**Constraints:** `1 <= number of nodes <= 10^4`, `-10^5 <= node value <= 10^5`.
""",
    """def maxLevelSum(root):
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
    best_level, best_sum, level = 1, None, 1
    q = deque([0])
    while q:
        s = sum(val[x] for x in q)
        if best_sum is None or s > best_sum:
            best_sum, best_level = s, level
        nxt = []
        for x in q:
            if left.get(x) is not None:
                nxt.append(left[x])
            if right.get(x) is not None:
                nxt.append(right[x])
        q = deque(nxt); level += 1
    return best_level
""",
    visible=[{"root": [1, 7, 0, 7, -8, None, None]}],
    hidden=[{"root": [989, None, 10250, 98693, -89388, None, None, None, -32127]},
            {"root": [1]}, {"root": [-100, -200, -300]}],
    gen=lambda r: [{"root": _rand_tree_vals(r, r.randint(1, 14), -20, 20)} for _ in range(6)],
    brute=_maxlevel_brute,
    checks=[({"root": [1, 7, 0, 7, -8, None, None]}, 2),
            ({"root": [989, None, 10250, 98693, -89388, None, None, None, -32127]}, 2),
            ({"root": [1]}, 1)],
    source="new_p")


# =========================================================================== #
# 19. Preimage Size of Factorial Zeroes Function
# =========================================================================== #
add("preimage-size-of-factorial-zeroes-function", "Preimage Size of Factorial Zeroes Function",
    "hard", ["math", "binary-search"], "preimageSizeFZF", [("K", "int")], "int",
    """
Let `f(x)` be the number of trailing zeroes of `x!`. Given `K`, return how many
non-negative integers `x` satisfy `f(x) == K`. (The answer is always `0` or `5`.)

**Examples**
```
K = 0   ->  5   (0!, 1!, 2!, 3!, 4! all end in 0 zeroes)
K = 5   ->  0   (no x! ends in exactly 5 zeroes)
```

**Constraints:** `0 <= K <= 10^9`.
""",
    """def preimageSizeFZF(K):
    def f(x):
        c = 0
        while x > 0:
            x //= 5
            c += x
        return c

    lo, hi = 0, 5 * (K + 1)
    while lo < hi:
        mid = (lo + hi) // 2
        if f(mid) < K:
            lo = mid + 1
        else:
            hi = mid
    return 5 if f(lo) == K else 0
""",
    visible=[{"K": 0}, {"K": 5}],
    hidden=[{"K": 3}, {"K": 6}, {"K": 7}, {"K": 11}, {"K": 24}],
    gen=_preimage_gen,
    brute=_preimage_brute,
    checks=[({"K": 0}, 5), ({"K": 5}, 0), ({"K": 3}, 5), ({"K": 6}, 5),
            ({"K": 1000000000}, 5)],
    source="new_p")


# =========================================================================== #
# 20. All Paths From Source to Target
# =========================================================================== #
add("all-paths-from-source-to-target", "All Paths From Source to Target", "medium",
    ["graph", "backtracking", "depth-first-search"], "allPathsSourceTarget",
    [("graph", "int[][]")], "int[][]",
    """
Given a directed acyclic graph of `n` nodes where `graph[i]` lists the nodes reachable
by a direct edge from `i`, return **all** paths from node `0` to node `n - 1`. The
paths may be returned in any order, but the nodes within each path must stay in
traversal order.

**Example**
```
graph = [[1,2],[3],[3],[]]   ->  [[0,1,3],[0,2,3]]
```

**Constraints:** `2 <= n <= 15`; the graph is acyclic.
""",
    """def allPathsSourceTarget(graph):
    n = len(graph)
    res = []

    def dfs(node, path):
        if node == n - 1:
            res.append(path[:])
            return
        for nb in graph[node]:
            path.append(nb)
            dfs(nb, path)
            path.pop()

    dfs(0, [0])
    return res
""",
    visible=[{"graph": [[1, 2], [3], [3], []]},
             {"graph": [[4, 3, 1], [3, 2, 4], [3], [4], []]}],
    hidden=[{"graph": [[1], []]}, {"graph": [[1, 2, 3], [3], [3], []]},
            {"graph": [[2], [], [1]]}],
    gen=_allpaths_gen,
    brute=_allpaths_brute,
    checks=[({"graph": [[1, 2], [3], [3], []]}, [[0, 1, 3], [0, 2, 3]]),
            ({"graph": [[4, 3, 1], [3, 2, 4], [3], [4], []]},
             [[0, 4], [0, 3, 4], [0, 1, 3, 4], [0, 1, 2, 3, 4], [0, 1, 4]]),
            ({"graph": [[1], []]}, [[0, 1]])],
    norm=sorted,
    source="new_p")
COMPARE["all-paths-from-source-to-target"] = "unordered"
