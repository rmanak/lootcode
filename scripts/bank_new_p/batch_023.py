"""Batch 023 of the new_p.txt import (20 problems).

Skips recorded in `_skips.py` for this group:
  - `remove-nth-node-from-end-of-list` (== existing `remove-nth-from-end`),
  - `throne-inheritance` + `design-twitter` (stateful design classes),
  - `maximum-number-of-darts-inside-of-a-circular-dartboard` (geometry over floats;
    points lying exactly on the circle are not robustly gradable under exact compare).

Reframes:
  - `smallest-sufficient-team` -> return the minimum team SIZE (LeetCode asks for "any"
    smallest team, which is not single-answer gradable).
  - `word-subsets` -> universal words returned in the order they appear in `A` (the
    original "any order" wording would force a non-exact compare).

Representation conventions (as in earlier batches): trees are passed as LeetCode
level-order arrays (None for a missing child) and rebuilt inside each solution;
linked lists as arrays of values; grids/matrices as rectangular int[][]; a Sudoku
board as a list of 9 length-9 strings ('.' = empty).
"""
from scripts.build_bank import add, COMPARE, ilist, sstr  # noqa: F401


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


# =========================================================================== #
# brute / gen helpers
# =========================================================================== #
def _cm_brute(num1, num2):
    import re

    def parse(s):
        m = re.match(r'(-?\d+)\+(-?\d+)i', s)
        return int(m.group(1)), int(m.group(2))

    a1, b1 = parse(num1)
    a2, b2 = parse(num2)
    return "{}+{}i".format(a1 * a2 - b1 * b2, a1 * b2 + a2 * b1)


def _cm_gen(r):
    out = []
    for _ in range(8):
        a1, b1 = r.randint(-100, 100), r.randint(-100, 100)
        a2, b2 = r.randint(-100, 100), r.randint(-100, 100)
        out.append({"num1": "{}+{}i".format(a1, b1), "num2": "{}+{}i".format(a2, b2)})
    return out


def _zigzag_brute(root):
    left, right, val = _build_tree(root)
    if not val:
        return []
    res, level, ltr = [], [0], True
    while level:
        row = [val[x] for x in level]
        res.append(row if ltr else row[::-1])
        nxt = []
        for x in level:
            if x in left:
                nxt.append(left[x])
            if x in right:
                nxt.append(right[x])
        level, ltr = nxt, not ltr
    return res


def _zigzag_gen(r):
    return [{"root": _rand_tree_vals(r, r.randint(1, 12), -5, 9)} for _ in range(6)]


def _lr_brute(start, end):
    from collections import deque
    if len(start) != len(end):
        return False
    seen = {start}
    dq = deque([start])
    while dq:
        cur = dq.popleft()
        if cur == end:
            return True
        for i in range(len(cur) - 1):
            two = cur[i:i + 2]
            if two == "XL":
                nxt = cur[:i] + "LX" + cur[i + 2:]
            elif two == "RX":
                nxt = cur[:i] + "XR" + cur[i + 2:]
            else:
                continue
            if nxt not in seen:
                seen.add(nxt); dq.append(nxt)
    return end in seen


def _lr_gen(r):
    out = []
    for _ in range(10):
        n = r.randint(1, 6)
        start = "".join(r.choice("LRX") for _ in range(n))
        end = "".join(r.choice("LRX") for _ in range(n))
        out.append({"start": start, "end": end})
    return out


def _zzp_label(r, p):
    lo, hi = 1 << (r - 1), (1 << r) - 1
    return lo + p if r % 2 == 1 else hi - p


def _zzpath_brute(label):
    r = label.bit_length()
    p = (label - (1 << (r - 1))) if r % 2 == 1 else ((1 << r) - 1 - label)
    path = []
    while r >= 1:
        path.append(_zzp_label(r, p))
        r -= 1
        p //= 2
    return path[::-1]


def _zzpath_gen(r):
    return [{"label": r.randint(1, 1000000)} for _ in range(10)]


def _rect_brute(rectangles):
    cells = set()
    for x1, y1, x2, y2 in rectangles:
        for x in range(x1, x2):
            for y in range(y1, y2):
                cells.add((x, y))
    return len(cells) % (10 ** 9 + 7)


def _rect_gen(r):
    out = []
    for _ in range(6):
        rects = []
        for _ in range(r.randint(1, 5)):
            x1 = r.randint(0, 8); x2 = x1 + r.randint(1, 5)
            y1 = r.randint(0, 8); y2 = y1 + r.randint(1, 5)
            rects.append([x1, y1, x2, y2])
        out.append({"rectangles": rects})
    return out


def _spell_brute(wordlist, queries):
    def dv(w):
        return "".join('*' if c in 'aeiou' else c for c in w.lower())

    res = []
    for q in queries:
        ans = ""
        if q in wordlist:
            ans = q
        else:
            hit = next((w for w in wordlist if w.lower() == q.lower()), None)
            if hit is not None:
                ans = hit
            else:
                hit = next((w for w in wordlist if dv(w) == dv(q)), None)
                if hit is not None:
                    ans = hit
        res.append(ans)
    return res


def _spell_gen(r):
    base = ["kite", "hare", "bot", "moon", "leet"]
    out = []
    for _ in range(6):
        words = []
        for _ in range(r.randint(1, 5)):
            w = r.choice(base)
            w = "".join(c.upper() if r.random() < 0.3 else c for c in w)
            words.append(w)
        queries = []
        for _ in range(r.randint(1, 6)):
            w = r.choice(base)
            w = list(w)
            if r.random() < 0.5:
                i = r.randrange(len(w))
                if w[i] in "aeiou":
                    w[i] = r.choice("aeiou")
            w = "".join(c.upper() if r.random() < 0.3 else c for c in w)
            queries.append(w)
        out.append({"wordlist": words, "queries": queries})
    return out


def _ngn_brute(head):
    n = len(head)
    res = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if head[j] > head[i]:
                res[i] = head[j]
                break
    return res


def _ngn_gen(r):
    return [{"head": [r.randint(1, 20) for _ in range(r.randint(0, 12))]} for _ in range(8)]


def _nvw_brute(words, puzzles):
    res = []
    for p in puzzles:
        pset = set(p)
        first = p[0]
        res.append(sum(1 for w in words if first in w and set(w) <= pset))
    return res


def _nvw_gen(r):
    letters = "abcdefg"
    out = []
    for _ in range(5):
        words = ["".join(r.choice(letters) for _ in range(r.randint(4, 7)))
                 for _ in range(r.randint(1, 8))]
        puzzles = ["".join(r.sample(letters, 7)) for _ in range(r.randint(1, 4))]
        out.append({"words": words, "puzzles": puzzles})
    return out


def _favorite_brute(favoriteCompanies):
    sets = [set(f) for f in favoriteCompanies]
    res = []
    for i in range(len(sets)):
        if not any(i != j and sets[i] <= sets[j] for j in range(len(sets))):
            res.append(i)
    return res


def _favorite_gen(r):
    comps = ["a", "b", "c", "d", "e", "f"]
    out = []
    for _ in range(6):
        seen, fav = set(), []
        for _ in range(r.randint(1, 5)):
            lst = sorted(r.sample(comps, r.randint(1, 4)))
            key = tuple(lst)
            if key not in seen:
                seen.add(key); fav.append(lst)
        if fav:
            out.append({"favoriteCompanies": fav})
    return out


def _interval_brute(A, B):
    res = []
    for a in A:
        for b in B:
            lo, hi = max(a[0], b[0]), min(a[1], b[1])
            if lo <= hi:
                res.append([lo, hi])
    res.sort()
    return res


def _interval_gen(r):
    def mk():
        ivs, cur = [], r.randint(0, 5)
        for _ in range(r.randint(0, 5)):
            a = cur + r.randint(0, 3)
            b = a + r.randint(0, 4)
            ivs.append([a, b])
            cur = b + r.randint(1, 3)
        return ivs

    return [{"A": mk(), "B": mk()} for _ in range(8)]


def _flip_brute(matrix):
    best = 0
    for i in range(len(matrix)):
        cnt = 0
        for j in range(len(matrix)):
            if (matrix[j] == matrix[i] or
                    all(matrix[j][k] != matrix[i][k] for k in range(len(matrix[i])))):
                cnt += 1
        best = max(best, cnt)
    return best


def _flip_gen(r):
    out = []
    for _ in range(8):
        rows, cols = r.randint(1, 5), r.randint(1, 5)
        out.append({"matrix": [[r.randint(0, 1) for _ in range(cols)] for _ in range(rows)]})
    return out


def _wordsubsets_brute(A, B):
    from collections import Counter
    res = []
    for a in A:
        ac = Counter(a)
        if all(not (Counter(b) - ac) for b in B):
            res.append(a)
    return res


def _wordsubsets_gen(r):
    out = []
    for _ in range(8):
        A = [sstr(r, 1, 5, "abcde") for _ in range(r.randint(1, 6))]
        B = [sstr(r, 1, 3, "abcde") for _ in range(r.randint(1, 4))]
        out.append({"A": A, "B": B})
    return out


def _gold_brute(grid):
    m, n = len(grid), len(grid[0])
    best = 0

    def dfs(i, j, visited, cur):
        nonlocal best
        cur += grid[i][j]
        best = max(best, cur)
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] != 0 and (ni, nj) not in visited:
                visited.add((ni, nj)); dfs(ni, nj, visited, cur); visited.remove((ni, nj))

    for i in range(m):
        for j in range(n):
            if grid[i][j] != 0:
                dfs(i, j, {(i, j)}, 0)
    return best


def _gold_gen(r):
    out = []
    for _ in range(6):
        rows, cols = r.randint(1, 3), r.randint(1, 3)
        grid = [[r.choice([0, 0, r.randint(1, 10)]) for _ in range(cols)] for _ in range(rows)]
        out.append({"grid": grid})
    return out


def _rmdup2_brute(head):
    res, i, n = [], 0, len(head)
    while i < n:
        j = i
        while j < n and head[j] == head[i]:
            j += 1
        if j - i == 1:
            res.append(head[i])
        i = j
    return res


def _rmdup2_gen(r):
    out = []
    for _ in range(8):
        vals = sorted(r.randint(1, 6) for _ in range(r.randint(0, 10)))
        out.append({"head": vals})
    return out


def _maxtree2_construct(arr):
    if not arr:
        return None
    mi = arr.index(max(arr))
    return [arr[mi], _maxtree2_construct(arr[:mi]), _maxtree2_construct(arr[mi + 1:])]


def _serialize(troot):
    from collections import deque
    if troot is None:
        return []
    out = [troot[0]]
    q = deque([troot])
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


def _maxtree2_brute(root, val):
    left, right, valm = _build_tree(root)
    A = []

    def ino(x):
        if x is None:
            return
        ino(left.get(x)); A.append(valm[x]); ino(right.get(x))

    if valm:
        ino(0)
    return _serialize(_maxtree2_construct(A + [val]))


def _maxtree2_gen(r):
    out = []
    for _ in range(6):
        A = r.sample(range(1, 50), r.randint(1, 7))
        ser = _serialize(_maxtree2_construct(A))
        val = r.choice([x for x in range(1, 100) if x not in set(A)])
        out.append({"root": ser, "val": val})
    return out


def _revii_brute(head, m, n):
    a = head[:]
    i, j = m - 1, n - 1
    while i < j:
        a[i], a[j] = a[j], a[i]
        i += 1; j -= 1
    return a


def _revii_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(1, 10)
        head = [r.randint(0, 99) for _ in range(n)]
        m = r.randint(1, n)
        nn = r.randint(m, n)
        out.append({"head": head, "m": m, "n": nn})
    return out


def _team_brute(req_skills, people):
    from itertools import combinations
    full = set(req_skills)
    for size in range(len(people) + 1):
        for combo in combinations(range(len(people)), size):
            covered = set()
            for idx in combo:
                covered |= set(people[idx])
            if full <= covered:
                return size
    return len(people)


def _team_gen(r):
    skills = ["a", "b", "c", "d", "e"]
    out = []
    for _ in range(6):
        ns = r.randint(1, 5)
        req = r.sample(skills, ns)
        people = []
        for _ in range(r.randint(ns, 8)):
            people.append(r.sample(req, r.randint(1, ns)))
        covered = set()
        for p in people:
            covered |= set(p)
        for s in req:
            if s not in covered:
                people.append([s])
        out.append({"req_skills": req, "people": people})
    return out


def _sss_brute(s, pairs):
    n = len(s)
    adj = {i: [] for i in range(n)}
    for a, b in pairs:
        adj[a].append(b); adj[b].append(a)
    seen = [False] * n
    res = list(s)
    for i in range(n):
        if not seen[i]:
            comp, stack = [], [i]
            seen[i] = True
            while stack:
                u = stack.pop(); comp.append(u)
                for w in adj[u]:
                    if not seen[w]:
                        seen[w] = True; stack.append(w)
            chars = sorted(res[k] for k in comp)
            for k, ch in zip(sorted(comp), chars):
                res[k] = ch
    return "".join(res)


def _sss_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(1, 8)
        s = "".join(r.choice("abcde") for _ in range(n))
        pairs = []
        for _ in range(r.randint(0, n)):
            a, b = r.randint(0, n - 1), r.randint(0, n - 1)
            if a != b:
                pairs.append([a, b])
        out.append({"s": s, "pairs": pairs})
    return out


_SUDOKU_SOLUTION = ["534678912", "672195348", "198342567",
                    "859761423", "426853791", "713924856",
                    "961537284", "287419635", "345286179"]
_SUDOKU_PUZZLE = ["53..7....", "6..195...", ".98....6.",
                  "8...6...3", "4..8.3..1", "7...2...6",
                  ".6....28.", "...419..5", "....8..79"]


def _sudoku_gen(r):
    out = []
    for _ in range(6):
        i, j = r.randint(0, 8), r.randint(0, 8)
        board = list(_SUDOKU_SOLUTION)
        row = list(board[i]); row[j] = '.'; board[i] = "".join(row)
        out.append({"board": board})
    return out


# =========================================================================== #
# 1. Complex Number Multiplication
# =========================================================================== #
add("complex-number-multiplication", "Complex Number Multiplication", "medium",
    ["math", "string"], "complexNumberMultiply",
    [("num1", "string"), ("num2", "string")], "string",
    """
You are given two strings `num1` and `num2`, each a complex number written in the form
`"a+bi"`, where `a` and `b` are integers and `i` is the imaginary unit with `i^2 = -1`.
Return their product, also formatted as `"a+bi"`.

**Examples**
```
num1 = "1+1i",  num2 = "1+1i"    ->  "0+2i"     ((1+i)(1+i) = 2i)
num1 = "1+-1i", num2 = "1+-1i"   ->  "0+-2i"    ((1-i)(1-i) = -2i)
```

**Constraints:** the integers `a` and `b` are in `[-100, 100]`; the input has no spaces.
""",
    """def complexNumberMultiply(num1, num2):
    def parse(s):
        s = s[:-1]
        p = s.rfind('+')
        return int(s[:p]), int(s[p + 1:])
    a1, b1 = parse(num1)
    a2, b2 = parse(num2)
    real = a1 * a2 - b1 * b2
    imag = a1 * b2 + a2 * b1
    return "{}+{}i".format(real, imag)
""",
    visible=[{"num1": "1+1i", "num2": "1+1i"}, {"num1": "1+-1i", "num2": "1+-1i"}],
    hidden=[{"num1": "0+0i", "num2": "5+5i"}, {"num1": "1+0i", "num2": "0+1i"},
            {"num1": "-5+3i", "num2": "2+-4i"}],
    gen=_cm_gen,
    brute=_cm_brute,
    checks=[({"num1": "1+1i", "num2": "1+1i"}, "0+2i"),
            ({"num1": "1+-1i", "num2": "1+-1i"}, "0+-2i"),
            ({"num1": "1+2i", "num2": "3+4i"}, "-5+10i"),
            ({"num1": "0+0i", "num2": "5+5i"}, "0+0i")],
    source="new_p")


# =========================================================================== #
# 2. Binary Tree Zigzag Level Order Traversal
# =========================================================================== #
add("binary-tree-zigzag-level-order-traversal", "Binary Tree Zigzag Level Order Traversal",
    "medium", ["binary-tree", "breadth-first-search", "tree"], "zigzagLevelOrder",
    [("root", "int[]")], "int[][]",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. Return its *zigzag* level-order
traversal: read the first level left-to-right, the next right-to-left, and keep
alternating.

**Example**
```
root = [3,9,20,null,null,15,7]   ->  [[3],[20,9],[15,7]]
```

**Constraints:** `0 <= number of nodes <= 2000`.
""",
    """def zigzagLevelOrder(root):
    from collections import deque
    if not root or root[0] is None:
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
    res, level, ltr = [], [0], True
    while level:
        row = [val[x] for x in level]
        res.append(row if ltr else row[::-1])
        nxt = []
        for x in level:
            if x in left:
                nxt.append(left[x])
            if x in right:
                nxt.append(right[x])
        level, ltr = nxt, not ltr
    return res
""",
    visible=[{"root": [3, 9, 20, None, None, 15, 7]}],
    hidden=[{"root": []}, {"root": [1]}, {"root": [1, 2, 3, 4, None, None, 5]},
            {"root": [1, 2, 3, 4, 5, 6, 7]}],
    gen=_zigzag_gen,
    brute=_zigzag_brute,
    checks=[({"root": [3, 9, 20, None, None, 15, 7]}, [[3], [20, 9], [15, 7]]),
            ({"root": []}, []), ({"root": [1]}, [[1]]),
            ({"root": [1, 2, 3, 4, 5, 6, 7]}, [[1], [3, 2], [4, 5, 6, 7]])],
    source="new_p")


# =========================================================================== #
# 3. Swap Adjacent in LR String
# =========================================================================== #
add("swap-adjacent-in-lr-string", "Swap Adjacent In LR String", "medium",
    ["string", "two-pointers"], "canTransform",
    [("start", "string"), ("end", "string")], "bool",
    """
A string is composed of the characters `'L'`, `'R'`, and `'X'`. A move replaces one
occurrence of `"XL"` with `"LX"` (an `L` slides one step left) or one occurrence of
`"RX"` with `"XR"` (an `R` slides one step right). Given `start` and `end`, return
`True` if and only if some sequence of moves turns `start` into `end`.

**Examples**
```
start = "RXXLRXRXL", end = "XRLXXRRLX"   ->  true
start = "XL",        end = "LX"          ->  true
start = "LX",        end = "XL"          ->  false
```

**Constraints:** `1 <= len(start) == len(end) <= 10^4`; both contain only `L`, `R`, `X`.
""",
    """def canTransform(start, end):
    if len(start) != len(end):
        return False
    if start.replace('X', '') != end.replace('X', ''):
        return False
    s = [(c, i) for i, c in enumerate(start) if c != 'X']
    e = [(c, i) for i, c in enumerate(end) if c != 'X']
    for (c, i), (_, j) in zip(s, e):
        if c == 'L' and i < j:
            return False
        if c == 'R' and i > j:
            return False
    return True
""",
    visible=[{"start": "XL", "end": "LX"}, {"start": "LX", "end": "XL"},
             {"start": "RX", "end": "XR"}],
    hidden=[{"start": "X", "end": "L"}, {"start": "XXX", "end": "XXX"},
            {"start": "LRX", "end": "LXR"}, {"start": "RXL", "end": "XRL"}],
    gen=_lr_gen,
    brute=_lr_brute,
    checks=[({"start": "RXXLRXRXL", "end": "XRLXXRRLX"}, True),
            ({"start": "XL", "end": "LX"}, True),
            ({"start": "LX", "end": "XL"}, False),
            ({"start": "X", "end": "L"}, False),
            ({"start": "XXX", "end": "XXX"}, True)],
    source="new_p")


# =========================================================================== #
# 4. Path In Zigzag Labelled Binary Tree
# =========================================================================== #
add("path-in-zigzag-labelled-binary-tree", "Path In Zigzag Labelled Binary Tree", "medium",
    ["math", "binary-tree", "tree"], "pathInZigZagTree", [("label", "int")], "int[]",
    """
In an infinite binary tree whose nodes are labelled row by row, the **odd** rows
(1st, 3rd, ...) are labelled left-to-right and the **even** rows (2nd, 4th, ...) are
labelled right-to-left. Given the `label` of a node, return the labels on the path
from the root down to that node.

**Examples**
```
label = 14   ->  [1,3,4,14]
label = 26   ->  [1,2,6,10,26]
```

**Constraints:** `1 <= label <= 10^6`.
""",
    """def pathInZigZagTree(label):
    path = []
    while label >= 1:
        path.append(label)
        L = label.bit_length()
        lo, hi = 1 << (L - 1), (1 << L) - 1
        label = (lo + hi - label) // 2
    return path[::-1]
""",
    visible=[{"label": 14}, {"label": 26}],
    hidden=[{"label": 1}, {"label": 2}, {"label": 3}, {"label": 1000000}],
    gen=_zzpath_gen,
    brute=_zzpath_brute,
    checks=[({"label": 14}, [1, 3, 4, 14]), ({"label": 26}, [1, 2, 6, 10, 26]),
            ({"label": 1}, [1]), ({"label": 2}, [1, 2]), ({"label": 3}, [1, 3])],
    source="new_p")


# =========================================================================== #
# 5. Rectangle Area II
# =========================================================================== #
add("rectangle-area-ii", "Rectangle Area II", "hard",
    ["array", "math", "sorting"], "rectangleArea", [("rectangles", "int[][]")], "int",
    """
You are given axis-aligned `rectangles` where `rectangles[i] = [x1, y1, x2, y2]` are
the bottom-left and top-right corners of the i-th rectangle. Return the **total area**
covered by the union of all rectangles. Because the answer may be large, return it
modulo `10^9 + 7`.

**Examples**
```
rectangles = [[0,0,2,2],[1,0,2,3],[1,0,3,1]]   ->  6
rectangles = [[0,0,1000000000,1000000000]]     ->  49   (10^18 mod (10^9 + 7))
```

**Constraints:** `1 <= len(rectangles) <= 200`, `0 <= xi, yi <= 10^9`.
""",
    """def rectangleArea(rectangles):
    MOD = 10 ** 9 + 7
    xs = sorted({r[0] for r in rectangles} | {r[2] for r in rectangles})
    total = 0
    for k in range(len(xs) - 1):
        x1, x2 = xs[k], xs[k + 1]
        width = x2 - x1
        if width == 0:
            continue
        spans = sorted((r[1], r[3]) for r in rectangles if r[0] <= x1 and r[2] >= x2)
        covered = 0
        cur_lo = cur_hi = None
        for lo, hi in spans:
            if cur_hi is None:
                cur_lo, cur_hi = lo, hi
            elif lo > cur_hi:
                covered += cur_hi - cur_lo
                cur_lo, cur_hi = lo, hi
            else:
                cur_hi = max(cur_hi, hi)
        if cur_hi is not None:
            covered += cur_hi - cur_lo
        total += width * covered
    return total % MOD
""",
    visible=[{"rectangles": [[0, 0, 2, 2], [1, 0, 2, 3], [1, 0, 3, 1]]}],
    hidden=[{"rectangles": [[0, 0, 1, 1]]}, {"rectangles": [[0, 0, 2, 2], [1, 1, 3, 3]]},
            {"rectangles": [[0, 0, 3, 3], [0, 0, 3, 3]]}],
    gen=_rect_gen,
    brute=_rect_brute,
    checks=[({"rectangles": [[0, 0, 2, 2], [1, 0, 2, 3], [1, 0, 3, 1]]}, 6),
            ({"rectangles": [[0, 0, 1000000000, 1000000000]]}, 49),
            ({"rectangles": [[0, 0, 1, 1]]}, 1),
            ({"rectangles": [[0, 0, 2, 2], [1, 1, 3, 3]]}, 7)],
    source="new_p")


# =========================================================================== #
# 6. Vowel Spellchecker
# =========================================================================== #
add("vowel-spellchecker", "Vowel Spellchecker", "medium",
    ["array", "hash-table", "string"], "spellchecker",
    [("wordlist", "string[]"), ("queries", "string[]")], "string[]",
    """
Given a `wordlist`, build a spellchecker that maps each query word to a correct word
using this precedence:

1. **Exact match** (case-sensitive): return the query unchanged.
2. **Capitalization**: if the query matches a wordlist word ignoring case, return the
   first such wordlist word.
3. **Vowel error**: treating every vowel (`a, e, i, o, u`) as interchangeable and
   ignoring case, if the query matches a wordlist word, return the first such word.
4. Otherwise return the empty string `""`.

Return `answer`, where `answer[i]` is the correct word for `queries[i]`.

**Example**
```
wordlist = ["KiTe","kite","hare","Hare"]
queries  = ["kite","Kite","KiTe","Hare","HARE","Hear","hear","keti","keet","keto"]
   ->  ["kite","KiTe","KiTe","Hare","hare","","","KiTe","","KiTe"]
```

**Constraints:** `1 <= len(wordlist), len(queries) <= 5000`; word lengths in `[1, 7]`;
letters only.
""",
    """def spellchecker(wordlist, queries):
    def devowel(w):
        return "".join('*' if c in 'aeiou' else c for c in w.lower())
    exact = set(wordlist)
    cap, vow = {}, {}
    for w in wordlist:
        cap.setdefault(w.lower(), w)
        vow.setdefault(devowel(w), w)
    res = []
    for q in queries:
        if q in exact:
            res.append(q)
        elif q.lower() in cap:
            res.append(cap[q.lower()])
        elif devowel(q) in vow:
            res.append(vow[devowel(q)])
        else:
            res.append("")
    return res
""",
    visible=[{"wordlist": ["KiTe", "kite", "hare", "Hare"],
              "queries": ["kite", "Kite", "KiTe", "Hare", "HARE", "Hear",
                          "hear", "keti", "keet", "keto"]}],
    hidden=[{"wordlist": ["yellow"], "queries": ["YellOw"]},
            {"wordlist": ["Yellow"], "queries": ["yellow"]},
            {"wordlist": ["abc"], "queries": ["xyz"]}],
    gen=_spell_gen,
    brute=_spell_brute,
    checks=[({"wordlist": ["KiTe", "kite", "hare", "Hare"],
              "queries": ["kite", "Kite", "KiTe", "Hare", "HARE", "Hear",
                          "hear", "keti", "keet", "keto"]},
             ["kite", "KiTe", "KiTe", "Hare", "hare", "", "", "KiTe", "", "KiTe"]),
            ({"wordlist": ["yellow"], "queries": ["YellOw"]}, ["yellow"]),
            ({"wordlist": ["abc"], "queries": ["xyz"]}, [""])],
    source="new_p")


# =========================================================================== #
# 7. Next Greater Node In Linked List
# =========================================================================== #
add("next-greater-node-in-linked-list", "Next Greater Node In Linked List", "medium",
    ["array", "linked-list", "stack"], "nextLargerNodes", [("head", "int[]")], "int[]",
    """
A singly linked list is given as an array of values `head` (the i-th value is the
i-th node). For each node, find the value of the **first node after it** that is
strictly larger; if there is none, use `0`. Return these values as an array `answer`
of the same length as `head`.

**Examples**
```
head = [2,1,5]               ->  [5,5,0]
head = [2,7,4,3,5]           ->  [7,0,5,5,0]
head = [1,7,5,1,9,2,5,1]     ->  [7,9,9,9,0,5,0,0]
```

**Constraints:** `0 <= len(head) <= 10^4`, `1 <= head[i] <= 10^9`.
""",
    """def nextLargerNodes(head):
    res = [0] * len(head)
    stack = []
    for i, v in enumerate(head):
        while stack and head[stack[-1]] < v:
            res[stack.pop()] = v
        stack.append(i)
    return res
""",
    visible=[{"head": [2, 1, 5]}, {"head": [2, 7, 4, 3, 5]},
             {"head": [1, 7, 5, 1, 9, 2, 5, 1]}],
    hidden=[{"head": []}, {"head": [5]}, {"head": [1, 2, 3, 4]}, {"head": [4, 3, 2, 1]}],
    gen=_ngn_gen,
    brute=_ngn_brute,
    checks=[({"head": [2, 1, 5]}, [5, 5, 0]),
            ({"head": [2, 7, 4, 3, 5]}, [7, 0, 5, 5, 0]),
            ({"head": [1, 7, 5, 1, 9, 2, 5, 1]}, [7, 9, 9, 9, 0, 5, 0, 0]),
            ({"head": []}, []), ({"head": [5]}, [0])],
    source="new_p")


# =========================================================================== #
# 8. Number Of Valid Words For Each Puzzle
# =========================================================================== #
add("number-of-valid-words-for-each-puzzle", "Number Of Valid Words For Each Puzzle",
    "hard", ["array", "hash-table", "string", "bitmask"], "findNumOfValidWords",
    [("words", "string[]"), ("puzzles", "string[]")], "int[]",
    """
A word is **valid** with respect to a puzzle string if (1) the word contains the
puzzle's **first** letter, and (2) every letter of the word appears in the puzzle.
For each puzzle, count how many words in `words` are valid for it. Return `answer`,
where `answer[i]` is the count for `puzzles[i]`.

**Example**
```
words   = ["aaaa","asas","able","ability","actt","actor","access"]
puzzles = ["aboveyz","abrodyz","abslute","absoryz","actresz","gaswxyz"]
   ->  [1,1,3,2,4,0]
```

**Constraints:** `1 <= len(words) <= 10^5`, `4 <= len(words[i]) <= 50`,
`1 <= len(puzzles) <= 10^4`, `len(puzzles[i]) == 7` with distinct letters; lowercase.
""",
    """def findNumOfValidWords(words, puzzles):
    from collections import Counter
    cnt = Counter()
    for w in words:
        mask = 0
        for c in set(w):
            mask |= 1 << (ord(c) - 97)
        cnt[mask] += 1
    res = []
    for p in puzzles:
        first = 1 << (ord(p[0]) - 97)
        pmask = 0
        for c in p:
            pmask |= 1 << (ord(c) - 97)
        total = 0
        sub = pmask
        while sub:
            if sub & first:
                total += cnt.get(sub, 0)
            sub = (sub - 1) & pmask
        res.append(total)
    return res
""",
    visible=[{"words": ["aaaa", "asas", "able", "ability", "actt", "actor", "access"],
              "puzzles": ["aboveyz", "abrodyz", "abslute", "absoryz", "actresz", "gaswxyz"]}],
    hidden=[{"words": ["apple", "pleas", "please"], "puzzles": ["aelwxyz", "aelpxyz"]},
            {"words": ["aaaa"], "puzzles": ["abcdefg"]}],
    gen=_nvw_gen,
    brute=_nvw_brute,
    checks=[({"words": ["aaaa", "asas", "able", "ability", "actt", "actor", "access"],
              "puzzles": ["aboveyz", "abrodyz", "abslute", "absoryz", "actresz", "gaswxyz"]},
             [1, 1, 3, 2, 4, 0]),
            ({"words": ["aaaa"], "puzzles": ["abcdefg"]}, [1])],
    source="new_p")


# =========================================================================== #
# 9. People Whose List Of Favorite Companies Is Not A Subset
# =========================================================================== #
add("people-whose-list-of-favorite-companies-is-not-a-subset-of-another-list",
    "People Whose List Of Favorite Companies Is Not A Subset Of Another List", "medium",
    ["array", "hash-table", "string"], "peopleIndexes",
    [("favoriteCompanies", "string[][]")], "int[]",
    """
`favoriteCompanies[i]` is the list of companies the i-th person likes. Return, in
**increasing order**, the indices of people whose favorite list is **not** a subset
of any other person's favorite list.

**Examples**
```
[["leetcode","google","facebook"],["google","microsoft"],
 ["google","facebook"],["google"],["amazon"]]            ->  [0,1,4]
[["leetcode","google","facebook"],["leetcode","amazon"],
 ["facebook","google"]]                                  ->  [0,1]
```

**Constraints:** `1 <= len(favoriteCompanies) <= 100`; all lists are distinct.
""",
    """def peopleIndexes(favoriteCompanies):
    sets = [set(f) for f in favoriteCompanies]
    n = len(sets)
    res = []
    for i in range(n):
        if not any(i != j and sets[i] <= sets[j] for j in range(n)):
            res.append(i)
    return res
""",
    visible=[{"favoriteCompanies": [["leetcode", "google", "facebook"],
                                    ["google", "microsoft"], ["google", "facebook"],
                                    ["google"], ["amazon"]]},
             {"favoriteCompanies": [["leetcode", "google", "facebook"],
                                    ["leetcode", "amazon"], ["facebook", "google"]]}],
    hidden=[{"favoriteCompanies": [["leetcode"], ["google"], ["facebook"], ["amazon"]]},
            {"favoriteCompanies": [["a"]]},
            {"favoriteCompanies": [["a", "b"], ["a"], ["b"]]}],
    gen=_favorite_gen,
    brute=_favorite_brute,
    checks=[({"favoriteCompanies": [["leetcode", "google", "facebook"],
                                    ["google", "microsoft"], ["google", "facebook"],
                                    ["google"], ["amazon"]]}, [0, 1, 4]),
            ({"favoriteCompanies": [["leetcode", "google", "facebook"],
                                    ["leetcode", "amazon"], ["facebook", "google"]]}, [0, 1]),
            ({"favoriteCompanies": [["leetcode"], ["google"], ["facebook"], ["amazon"]]},
             [0, 1, 2, 3])],
    source="new_p")


# =========================================================================== #
# 10. Interval List Intersections
# =========================================================================== #
add("interval-list-intersections", "Interval List Intersections", "medium",
    ["array", "two-pointers"], "intervalIntersection",
    [("A", "int[][]"), ("B", "int[][]")], "int[][]",
    """
You are given two lists of closed intervals, `A` and `B`. Each list is pairwise
disjoint and sorted by start. Return the intersection of the two lists: every closed
interval `[lo, hi]` (with `lo <= hi`) common to one interval of `A` and one of `B`,
in sorted order.

**Example**
```
A = [[0,2],[5,10],[13,23],[24,25]]
B = [[1,5],[8,12],[15,24],[25,26]]
   ->  [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]
```

**Constraints:** `0 <= len(A), len(B) < 1000`, `0 <= endpoints < 10^9`.
""",
    """def intervalIntersection(A, B):
    i = j = 0
    res = []
    while i < len(A) and j < len(B):
        lo = max(A[i][0], B[j][0])
        hi = min(A[i][1], B[j][1])
        if lo <= hi:
            res.append([lo, hi])
        if A[i][1] < B[j][1]:
            i += 1
        else:
            j += 1
    return res
""",
    visible=[{"A": [[0, 2], [5, 10], [13, 23], [24, 25]],
              "B": [[1, 5], [8, 12], [15, 24], [25, 26]]}],
    hidden=[{"A": [], "B": [[1, 2]]}, {"A": [[1, 3]], "B": [[2, 4]]},
            {"A": [[1, 7]], "B": [[3, 10]]}, {"A": [[1, 2]], "B": [[3, 4]]}],
    gen=_interval_gen,
    brute=_interval_brute,
    checks=[({"A": [[0, 2], [5, 10], [13, 23], [24, 25]],
              "B": [[1, 5], [8, 12], [15, 24], [25, 26]]},
             [[1, 2], [5, 5], [8, 10], [15, 23], [24, 24], [25, 25]]),
            ({"A": [], "B": [[1, 2]]}, []),
            ({"A": [[1, 3]], "B": [[2, 4]]}, [[2, 3]])],
    source="new_p")


# =========================================================================== #
# 11. Solve The Equation
# =========================================================================== #
add("solve-the-equation", "Solve The Equation", "medium",
    ["math", "string", "simulation"], "solveEquation",
    [("equation", "string")], "string",
    """
Solve a linear equation in the single variable `x`. The equation uses only `+`, `-`,
the variable `x`, and non-negative integer coefficients, with exactly one `=`. Return
the answer as `"x=#value"`. If there is no solution return `"No solution"`; if every
value of `x` works return `"Infinite solutions"`. When a unique solution exists it is
guaranteed to be an integer.

**Examples**
```
"x+5-3+x=6+x-2"     ->  "x=2"
"x=x"               ->  "Infinite solutions"
"2x=x"              ->  "x=0"
"2x+3x-6x=x+2"      ->  "x=-1"
"x=x+2"             ->  "No solution"
```

**Constraints:** the input is a valid equation as described.
""",
    """def solveEquation(equation):
    def parse(expr):
        coef = const = 0
        i, n = 0, len(expr)
        while i < n:
            sign = 1
            if expr[i] == '+':
                i += 1
            elif expr[i] == '-':
                sign = -1; i += 1
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            num = expr[i:j]
            if j < n and expr[j] == 'x':
                coef += sign * (int(num) if num else 1)
                i = j + 1
            else:
                const += sign * (int(num) if num else 0)
                i = j
        return coef, const
    lhs, rhs = equation.split('=')
    lc, lk = parse(lhs)
    rc, rk = parse(rhs)
    a = lc - rc
    b = rk - lk
    if a == 0:
        return "Infinite solutions" if b == 0 else "No solution"
    return "x=" + str(b // a)
""",
    visible=[{"equation": "x+5-3+x=6+x-2"}, {"equation": "x=x"}, {"equation": "2x=x"}],
    hidden=[{"equation": "2x+3x-6x=x+2"}, {"equation": "x=x+2"},
            {"equation": "0=0"}, {"equation": "-x=-1"}, {"equation": "3x=33"}],
    checks=[({"equation": "x+5-3+x=6+x-2"}, "x=2"),
            ({"equation": "x=x"}, "Infinite solutions"),
            ({"equation": "2x=x"}, "x=0"),
            ({"equation": "2x+3x-6x=x+2"}, "x=-1"),
            ({"equation": "x=x+2"}, "No solution"),
            ({"equation": "-x=-1"}, "x=1"),
            ({"equation": "3x=33"}, "x=11")],
    source="new_p")


# =========================================================================== #
# 12. Flip Columns For Maximum Number Of Equal Rows
# =========================================================================== #
add("flip-columns-for-maximum-number-of-equal-rows",
    "Flip Columns For Maximum Number Of Equal Rows", "medium",
    ["array", "hash-table", "matrix"], "maxEqualRowsAfterFlips",
    [("matrix", "int[][]")], "int",
    """
You are given a `matrix` of `0`s and `1`s. You may choose any set of columns and flip
every cell in each chosen column (`0 <-> 1`). Return the maximum number of rows that
can be made **all equal** (every cell in the row identical) after some choice of flips.

**Examples**
```
[[0,1],[1,1]]            ->  1
[[0,1],[1,0]]            ->  2
[[0,0,0],[0,0,1],[1,1,0]]   ->  2
```

**Constraints:** `1 <= rows, cols <= 300`, `matrix[i][j]` is `0` or `1`.
""",
    """def maxEqualRowsAfterFlips(matrix):
    from collections import Counter
    cnt = Counter()
    for row in matrix:
        key = tuple(c ^ row[0] for c in row)
        cnt[key] += 1
    return max(cnt.values())
""",
    visible=[{"matrix": [[0, 1], [1, 1]]}, {"matrix": [[0, 1], [1, 0]]},
             {"matrix": [[0, 0, 0], [0, 0, 1], [1, 1, 0]]}],
    hidden=[{"matrix": [[1]]}, {"matrix": [[0], [1]]},
            {"matrix": [[1, 1, 1], [0, 0, 0]]}],
    gen=_flip_gen,
    brute=_flip_brute,
    checks=[({"matrix": [[0, 1], [1, 1]]}, 1), ({"matrix": [[0, 1], [1, 0]]}, 2),
            ({"matrix": [[0, 0, 0], [0, 0, 1], [1, 1, 0]]}, 2),
            ({"matrix": [[1, 1, 1], [0, 0, 0]]}, 2)],
    source="new_p")


# =========================================================================== #
# 13. Word Subsets (universal words in A's order)
# =========================================================================== #
add("word-subsets", "Word Subsets", "medium",
    ["array", "hash-table", "string"], "wordSubsets",
    [("A", "string[]"), ("B", "string[]")], "string[]",
    """
For two words `a` and `b`, say `b` is a *subset* of `a` if every letter of `b` occurs
in `a`, counting multiplicity (so `"wrr"` is a subset of `"warrior"` but not of
`"world"`). A word `a` in `A` is **universal** if every word `b` in `B` is a subset of
`a`. Return all universal words of `A`, **in the order they appear in `A`**.

**Examples**
```
A = ["amazon","apple","facebook","google","leetcode"], B = ["e","o"]
   ->  ["facebook","google","leetcode"]
A = ["amazon","apple","facebook","google","leetcode"], B = ["lo","eo"]
   ->  ["google","leetcode"]
```

**Constraints:** `1 <= len(A), len(B) <= 10^4`, `1 <= len(A[i]), len(B[i]) <= 10`.
""",
    """def wordSubsets(A, B):
    from collections import Counter
    need = Counter()
    for b in B:
        for ch, k in Counter(b).items():
            need[ch] = max(need[ch], k)
    res = []
    for a in A:
        ac = Counter(a)
        if all(ac[ch] >= k for ch, k in need.items()):
            res.append(a)
    return res
""",
    visible=[{"A": ["amazon", "apple", "facebook", "google", "leetcode"], "B": ["e", "o"]},
             {"A": ["amazon", "apple", "facebook", "google", "leetcode"], "B": ["lo", "eo"]}],
    hidden=[{"A": ["amazon", "apple", "facebook", "google", "leetcode"], "B": ["e", "oo"]},
            {"A": ["amazon", "apple", "facebook", "google", "leetcode"],
             "B": ["ec", "oc", "ceo"]},
            {"A": ["a"], "B": ["b"]}],
    gen=_wordsubsets_gen,
    brute=_wordsubsets_brute,
    checks=[({"A": ["amazon", "apple", "facebook", "google", "leetcode"], "B": ["e", "o"]},
             ["facebook", "google", "leetcode"]),
            ({"A": ["amazon", "apple", "facebook", "google", "leetcode"], "B": ["lo", "eo"]},
             ["google", "leetcode"]),
            ({"A": ["amazon", "apple", "facebook", "google", "leetcode"], "B": ["e", "oo"]},
             ["facebook", "google"]),
            ({"A": ["a"], "B": ["b"]}, [])],
    source="new_p")


# =========================================================================== #
# 14. Path With Maximum Gold
# =========================================================================== #
add("path-with-maximum-gold", "Path With Maximum Gold", "medium",
    ["array", "backtracking", "matrix", "depth-first-search"], "getMaximumGold",
    [("grid", "int[][]")], "int",
    """
In a gold-mine `grid`, each cell holds an amount of gold (`0` means empty). Starting
from any non-empty cell, you repeatedly walk one step up/down/left/right into a cell
that still has gold, collecting all the gold in each cell you enter. You may not revisit
a cell and may not step onto a `0` cell. Return the maximum gold you can collect.

**Examples**
```
grid = [[0,6,0],[5,8,7],[0,9,0]]                 ->  24   (9 -> 8 -> 7)
grid = [[1,0,7],[2,0,6],[3,4,5],[0,3,0],[9,0,20]]   ->  28   (1->2->3->4->5->6->7)
```

**Constraints:** `1 <= rows, cols <= 15`, `0 <= grid[i][j] <= 100`, at most 25 gold cells.
""",
    """def getMaximumGold(grid):
    grid = [row[:] for row in grid]
    m, n = len(grid), len(grid[0])
    best = [0]

    def dfs(i, j, cur):
        cur += grid[i][j]
        best[0] = max(best[0], cur)
        keep = grid[i][j]
        grid[i][j] = 0
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] != 0:
                dfs(ni, nj, cur)
        grid[i][j] = keep

    for i in range(m):
        for j in range(n):
            if grid[i][j] != 0:
                dfs(i, j, 0)
    return best[0]
""",
    visible=[{"grid": [[0, 6, 0], [5, 8, 7], [0, 9, 0]]},
             {"grid": [[1, 0, 7], [2, 0, 6], [3, 4, 5], [0, 3, 0], [9, 0, 20]]}],
    hidden=[{"grid": [[0]]}, {"grid": [[10]]}, {"grid": [[1, 1], [1, 1]]},
            {"grid": [[0, 0], [0, 0]]}],
    gen=_gold_gen,
    brute=_gold_brute,
    checks=[({"grid": [[0, 6, 0], [5, 8, 7], [0, 9, 0]]}, 24),
            ({"grid": [[1, 0, 7], [2, 0, 6], [3, 4, 5], [0, 3, 0], [9, 0, 20]]}, 28),
            ({"grid": [[0]]}, 0), ({"grid": [[10]]}, 10),
            ({"grid": [[1, 1], [1, 1]]}, 4)],
    source="new_p")


# =========================================================================== #
# 15. Remove Duplicates From Sorted List II
# =========================================================================== #
add("remove-duplicates-from-sorted-list-ii", "Remove Duplicates From Sorted List II",
    "medium", ["linked-list", "two-pointers"], "deleteDuplicates",
    [("head", "int[]")], "int[]",
    """
A sorted singly linked list is given as an array of values `head`. Delete **every**
node that has a duplicate value, leaving only the values that appear exactly once.
Return the remaining values as an array (still sorted).

**Examples**
```
head = [1,2,3,3,4,4,5]   ->  [1,2,5]
head = [1,1,1,2,3]       ->  [2,3]
```

**Constraints:** `0 <= len(head) <= 300`, values are sorted in non-decreasing order.
""",
    """def deleteDuplicates(head):
    res = []
    i, n = 0, len(head)
    while i < n:
        j = i
        while j < n and head[j] == head[i]:
            j += 1
        if j - i == 1:
            res.append(head[i])
        i = j
    return res
""",
    visible=[{"head": [1, 2, 3, 3, 4, 4, 5]}, {"head": [1, 1, 1, 2, 3]}],
    hidden=[{"head": []}, {"head": [1]}, {"head": [1, 1]},
            {"head": [1, 2, 2, 3, 3, 4]}],
    gen=_rmdup2_gen,
    brute=_rmdup2_brute,
    checks=[({"head": [1, 2, 3, 3, 4, 4, 5]}, [1, 2, 5]),
            ({"head": [1, 1, 1, 2, 3]}, [2, 3]), ({"head": []}, []),
            ({"head": [1]}, [1]), ({"head": [1, 1]}, [])],
    source="new_p")


# =========================================================================== #
# 16. Maximum Binary Tree II
# =========================================================================== #
add("maximum-binary-tree-ii", "Maximum Binary Tree II", "medium",
    ["tree", "binary-tree"], "insertIntoMaxTree",
    [("root", "int[]"), ("val", "int")], "int[]",
    """
A *maximum tree* is built from a list `A` of distinct values: the root is the maximum
of `A`, its left subtree is the maximum tree of the elements before it, and its right
subtree the maximum tree of the elements after it. You are given such a tree as a
LeetCode **level-order array** `root` (it was built from some `A`) and a value `val`
to append to the end of `A`. Return the level-order array of the maximum tree built
from `A + [val]`.

**Examples**
```
root = [4,1,3,null,null,2], val = 5   ->  [5,4,null,1,3,null,null,2]
root = [5,2,4,null,1],      val = 3   ->  [5,2,4,null,1,null,3]
root = [5,2,3,null,1],      val = 4   ->  [5,2,4,null,1,3]
```

**Constraints:** the resulting list has length in `[1, 100]` with unique values.
""",
    """def insertIntoMaxTree(root, val):
    from collections import deque

    def arr_to_nested(arr):
        if not arr or arr[0] is None:
            return None
        node0 = [arr[0], None, None]
        q = deque([node0]); i, n = 1, len(arr)
        while q and i < n:
            nd = q.popleft()
            if i < n:
                v = arr[i]; i += 1
                if v is not None:
                    nd[1] = [v, None, None]; q.append(nd[1])
            if i < n:
                v = arr[i]; i += 1
                if v is not None:
                    nd[2] = [v, None, None]; q.append(nd[2])
        return node0

    def insert(nd):
        if nd is None or val > nd[0]:
            return [val, nd, None]
        nd[2] = insert(nd[2])
        return nd

    troot = insert(arr_to_nested(root))
    if troot is None:
        return []
    out = [troot[0]]; q = deque([troot])
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
""",
    visible=[{"root": [4, 1, 3, None, None, 2], "val": 5},
             {"root": [5, 2, 4, None, 1], "val": 3},
             {"root": [5, 2, 3, None, 1], "val": 4}],
    hidden=[{"root": [1], "val": 2}, {"root": [2], "val": 1},
            {"root": [5, 4, 3, 2, 1], "val": 6}],
    gen=_maxtree2_gen,
    brute=_maxtree2_brute,
    checks=[({"root": [4, 1, 3, None, None, 2], "val": 5},
             [5, 4, None, 1, 3, None, None, 2]),
            ({"root": [5, 2, 4, None, 1], "val": 3}, [5, 2, 4, None, 1, None, 3]),
            ({"root": [5, 2, 3, None, 1], "val": 4}, [5, 2, 4, None, 1, 3]),
            ({"root": [1], "val": 2}, [2, 1]),
            ({"root": [2], "val": 1}, [2, None, 1])],
    source="new_p")


# =========================================================================== #
# 17. Reverse Linked List II
# =========================================================================== #
add("reverse-linked-list-ii", "Reverse Linked List II", "medium",
    ["linked-list"], "reverseBetween",
    [("head", "int[]"), ("m", "int"), ("n", "int")], "int[]",
    """
A singly linked list is given as an array of values `head`. Reverse the nodes from
position `m` to position `n` (1-indexed, inclusive) and return the resulting values.

**Example**
```
head = [1,2,3,4,5], m = 2, n = 4   ->  [1,4,3,2,5]
```

**Constraints:** `1 <= m <= n <= len(head)`, `1 <= len(head) <= 500`.
""",
    """def reverseBetween(head, m, n):
    a = head[:]
    a[m - 1:n] = a[m - 1:n][::-1]
    return a
""",
    visible=[{"head": [1, 2, 3, 4, 5], "m": 2, "n": 4}],
    hidden=[{"head": [5], "m": 1, "n": 1}, {"head": [1, 2], "m": 1, "n": 2},
            {"head": [1, 2, 3, 4, 5], "m": 1, "n": 5},
            {"head": [3, 5], "m": 1, "n": 1}],
    gen=_revii_gen,
    brute=_revii_brute,
    checks=[({"head": [1, 2, 3, 4, 5], "m": 2, "n": 4}, [1, 4, 3, 2, 5]),
            ({"head": [5], "m": 1, "n": 1}, [5]),
            ({"head": [1, 2], "m": 1, "n": 2}, [2, 1]),
            ({"head": [1, 2, 3, 4, 5], "m": 1, "n": 5}, [5, 4, 3, 2, 1])],
    source="new_p")


# =========================================================================== #
# 18. Smallest Sufficient Team (reframed -> team size)
# =========================================================================== #
add("smallest-sufficient-team", "Smallest Sufficient Team", "hard",
    ["dynamic-programming", "bitmask", "bit-manipulation"], "smallestSufficientTeamSize",
    [("req_skills", "string[]"), ("people", "string[][]")], "int",
    """
You are given a list of required skills `req_skills` and a list of `people`, where
`people[i]` is the set of skills person `i` has. A team is **sufficient** if, for every
required skill, at least one team member has it. Return the **size** of the smallest
sufficient team (it is guaranteed one exists).

**Examples**
```
req_skills = ["java","nodejs","reactjs"]
people = [["java"],["nodejs"],["nodejs","reactjs"]]            ->  2
req_skills = ["algorithms","math","java","reactjs","csharp","aws"]
people = [["algorithms","math","java"],["algorithms","math","reactjs"],
          ["java","csharp","aws"],["reactjs","csharp"],
          ["csharp","math"],["aws","java"]]                    ->  2
```

**Constraints:** `1 <= len(req_skills) <= 16`, `1 <= len(people) <= 60`; every skill in
`people[i]` is in `req_skills`.
""",
    """def smallestSufficientTeamSize(req_skills, people):
    n = len(req_skills)
    sid = {s: i for i, s in enumerate(req_skills)}
    full = (1 << n) - 1
    INF = float('inf')
    dp = [INF] * (1 << n)
    dp[0] = 0
    pmasks = []
    for p in people:
        m = 0
        for s in p:
            if s in sid:
                m |= 1 << sid[s]
        pmasks.append(m)
    for mask in range(1 << n):
        if dp[mask] == INF:
            continue
        for pm in pmasks:
            nm = mask | pm
            if dp[nm] > dp[mask] + 1:
                dp[nm] = dp[mask] + 1
    return dp[full]
""",
    visible=[{"req_skills": ["java", "nodejs", "reactjs"],
              "people": [["java"], ["nodejs"], ["nodejs", "reactjs"]]}],
    hidden=[{"req_skills": ["a"], "people": [["a"]]},
            {"req_skills": ["a", "b"], "people": [["a"], ["b"], ["a", "b"]]},
            {"req_skills": ["a", "b", "c"], "people": [["a", "b"], ["b", "c"], ["a", "c"]]}],
    gen=_team_gen,
    brute=_team_brute,
    checks=[({"req_skills": ["java", "nodejs", "reactjs"],
              "people": [["java"], ["nodejs"], ["nodejs", "reactjs"]]}, 2),
            ({"req_skills": ["algorithms", "math", "java", "reactjs", "csharp", "aws"],
              "people": [["algorithms", "math", "java"], ["algorithms", "math", "reactjs"],
                         ["java", "csharp", "aws"], ["reactjs", "csharp"],
                         ["csharp", "math"], ["aws", "java"]]}, 2),
            ({"req_skills": ["a", "b"], "people": [["a"], ["b"], ["a", "b"]]}, 1)],
    source="new_p")


# =========================================================================== #
# 19. Smallest String With Swaps
# =========================================================================== #
add("smallest-string-with-swaps", "Smallest String With Swaps", "medium",
    ["hash-table", "string", "union-find", "sorting"], "smallestStringWithSwaps",
    [("s", "string"), ("pairs", "int[][]")], "string",
    """
You are given a string `s` and a list of index `pairs`. You may swap the characters at
any listed pair of indices, any number of times. Return the lexicographically smallest
string reachable.

**Examples**
```
s = "dcab", pairs = [[0,3],[1,2]]         ->  "bacd"
s = "dcab", pairs = [[0,3],[1,2],[0,2]]   ->  "abcd"
s = "cba",  pairs = [[0,1],[1,2]]         ->  "abc"
```

**Constraints:** `1 <= len(s) <= 10^5`, `0 <= len(pairs) <= 10^5`, lowercase letters.
""",
    """def smallestStringWithSwaps(s, pairs):
    n = len(s)
    par = list(range(n))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for a, b in pairs:
        par[find(a)] = find(b)
    from collections import defaultdict
    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)
    res = list(s)
    for idxs in groups.values():
        chars = sorted(res[i] for i in idxs)
        for i, ch in zip(idxs, chars):
            res[i] = ch
    return "".join(res)
""",
    visible=[{"s": "dcab", "pairs": [[0, 3], [1, 2]]},
             {"s": "dcab", "pairs": [[0, 3], [1, 2], [0, 2]]},
             {"s": "cba", "pairs": [[0, 1], [1, 2]]}],
    hidden=[{"s": "a", "pairs": []}, {"s": "ab", "pairs": []},
            {"s": "ba", "pairs": [[0, 1]]}, {"s": "zyx", "pairs": [[0, 2]]}],
    gen=_sss_gen,
    brute=_sss_brute,
    checks=[({"s": "dcab", "pairs": [[0, 3], [1, 2]]}, "bacd"),
            ({"s": "dcab", "pairs": [[0, 3], [1, 2], [0, 2]]}, "abcd"),
            ({"s": "cba", "pairs": [[0, 1], [1, 2]]}, "abc"),
            ({"s": "ba", "pairs": [[0, 1]]}, "ab")],
    source="new_p")


# =========================================================================== #
# 20. Sudoku Solver
# =========================================================================== #
add("sudoku-solver", "Sudoku Solver", "hard",
    ["array", "backtracking", "matrix"], "solveSudoku",
    [("board", "string[]")], "string[]",
    """
Solve a `9 x 9` Sudoku puzzle. The board is given as a list of 9 strings of length 9;
a `'.'` marks an empty cell and the other cells hold digits `'1'`-`'9'`. Fill every
empty cell so that each row, each column, and each of the nine `3 x 3` boxes contains
the digits `1`-`9` exactly once. Return the completed board in the same format. The
puzzle is guaranteed to have a single unique solution.

**Constraints:** the input is a valid `9 x 9` Sudoku with exactly one solution.
""",
    """def solveSudoku(board):
    grid = [list(row) for row in board]
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empties = []
    for i in range(9):
        for j in range(9):
            c = grid[i][j]
            if c == '.':
                empties.append((i, j))
            else:
                rows[i].add(c); cols[j].add(c); boxes[(i // 3) * 3 + j // 3].add(c)

    def bt(k):
        if k == len(empties):
            return True
        i, j = empties[k]
        b = (i // 3) * 3 + j // 3
        for d in "123456789":
            if d not in rows[i] and d not in cols[j] and d not in boxes[b]:
                grid[i][j] = d
                rows[i].add(d); cols[j].add(d); boxes[b].add(d)
                if bt(k + 1):
                    return True
                grid[i][j] = '.'
                rows[i].discard(d); cols[j].discard(d); boxes[b].discard(d)
        return False

    bt(0)
    return ["".join(row) for row in grid]
""",
    visible=[{"board": list(_SUDOKU_PUZZLE)}],
    hidden=[{"board": list(_SUDOKU_SOLUTION)}],
    gen=_sudoku_gen,
    checks=[({"board": list(_SUDOKU_PUZZLE)}, list(_SUDOKU_SOLUTION)),
            ({"board": list(_SUDOKU_SOLUTION)}, list(_SUDOKU_SOLUTION))],
    source="new_p")
