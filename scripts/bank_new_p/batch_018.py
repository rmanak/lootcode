"""Batch 018 of the new_p.txt import (20 problems).

Two entries from this group were dropped to `_skips.py` before authoring:
  - `product-of-array-except-self` (== `product-except-self`)
  - `random-pick-index`           (stateful design class + random output)

Reframes in this batch (the LeetCode form is not a single gradable answer):
  - `minimum-remove-to-make-valid-parentheses` -> return the MIN COUNT of
    parentheses to remove (the removed string itself is not unique).
  - `online-stock-span` -> take the full price list, return the span list.
  - `online-majority-element-in-subarray` -> take `arr` + a list of
    `[left, right, threshold]` queries, return one answer per query.

`simplified-fractions` keeps its "in any order" wording, so its COMPARE mode is
set to "unordered".

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


def _rand_tree_vals(r, n, lo, hi):
    """Build a random binary tree with `n` nodes and serialize it to a LeetCode
    level-order list (None for missing children, trailing Nones trimmed)."""
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


# --------------------------- brute / reference helpers ---------------------
def _rearrange_brute(text):
    words = text.lower().split()
    order = sorted(range(len(words)), key=lambda i: (len(words[i]), i))
    res = " ".join(words[i] for i in order)
    return res[:1].upper() + res[1:]


def _rearrange_gen(r):
    out = []
    bank = ["a", "to", "the", "code", "happy", "leetcode", "is", "be", "or", "not"]
    for _ in range(8):
        words = [r.choice(bank) for _ in range(r.randint(1, 7))]
        text = " ".join(words)
        text = text[:1].upper() + text[1:]
        out.append({"text": text})
    return out


def _revparen_brute(s):
    while '(' in s:
        i = s.rfind('(')
        j = s.find(')', i)
        s = s[:i] + s[i + 1:j][::-1] + s[j + 1:]
    return s


def _revparen_gen(r):
    def make(depth):
        a = "".join(r.choice("abcde") for _ in range(r.randint(0, 2)))
        b = "".join(r.choice("abcde") for _ in range(r.randint(0, 2)))
        if depth <= 0 or r.random() < 0.4:
            return a + b
        return a + "(" + make(depth - 1) + ")" + b
    return [{"s": make(r.randint(0, 3))} for _ in range(8)]


def _minremove_brute(s):
    stack = []
    to_remove = 0
    for ch in s:
        if ch == '(':
            stack.append(ch)
        elif ch == ')':
            if stack:
                stack.pop()
            else:
                to_remove += 1
    return to_remove + len(stack)


def _minremove_gen(r):
    return [{"s": "".join(r.choice("()ab") for _ in range(r.randint(0, 14)))}
            for _ in range(8)]


def _atoi_brute(s):
    import re
    m = re.match(r'^ *([+-]?)(\d*)', s)
    digits = m.group(2)
    if not digits:
        return 0
    sign = -1 if m.group(1) == '-' else 1
    num = sign * int(digits)
    return max(-2 ** 31, min(2 ** 31 - 1, num))


def _atoi_gen(r):
    chars = "0123456789+- ab"
    return [{"s": "".join(r.choice(chars) for _ in range(r.randint(0, 12)))}
            for _ in range(10)]


def _single_brute(nums):
    x = 0
    for v in nums:
        x ^= v
    return x


def _single_gen(r):
    out = []
    for _ in range(8):
        k = r.randint(0, 6)
        vals = sorted(r.sample(range(0, 50), k + 1))
        single_idx = r.randint(0, k)
        arr = []
        for i, v in enumerate(vals):
            arr += [v] if i == single_idx else [v, v]
        arr.sort()
        out.append({"nums": arr})
    return out


def _falling2_brute(arr):
    n = len(arr)
    prev = arr[0][:]
    for i in range(1, n):
        cur = []
        for j in range(n):
            best = min(prev[k] for k in range(n) if k != j)
            cur.append(arr[i][j] + best)
        prev = cur
    return min(prev)


def _falling2_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(1, 6)
        out.append({"arr": [[r.randint(-9, 9) for _ in range(n)] for _ in range(n)]})
    return out


def _stone2_brute(piles):
    n = len(piles)

    def dp(i, m):
        if i >= n:
            return 0
        if i + 2 * m >= n:
            return sum(piles[i:])
        total = sum(piles[i:])
        best = 0
        for x in range(1, 2 * m + 1):
            best = max(best, total - dp(i + x, max(m, x)))
        return best

    return dp(0, 1)


def _stone2_gen(r):
    return [{"piles": [r.randint(1, 12) for _ in range(r.randint(1, 8))]} for _ in range(8)]


def _watched_brute(watchedVideos, friends, id, level):
    from collections import deque, Counter
    n = len(friends)
    dist = [-1] * n
    dist[id] = 0
    q = deque([id])
    while q:
        u = q.popleft()
        for v in friends[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                q.append(v)
    cnt = Counter()
    for u in range(n):
        if dist[u] == level:
            for vid in watchedVideos[u]:
                cnt[vid] += 1
    return sorted(cnt, key=lambda x: (cnt[x], x))


def _watched_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(2, 6)
        adj = [set() for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                if r.random() < 0.5:
                    adj[i].add(j); adj[j].add(i)
        friends = [sorted(s) for s in adj]
        watched = [[r.choice("ABCD") for _ in range(r.randint(1, 3))] for _ in range(n)]
        out.append({"watchedVideos": watched, "friends": friends,
                    "id": r.randint(0, n - 1), "level": r.randint(1, n - 1)})
    return out


def _rabbits_brute(answers):
    from collections import defaultdict
    capacity = defaultdict(int)
    total = 0
    for x in answers:
        if capacity[x] > 0:
            capacity[x] -= 1
        else:
            total += x + 1
            capacity[x] = x
    return total


def _rabbits_gen(r):
    return [{"answers": [r.randint(0, 5) for _ in range(r.randint(0, 12))]} for _ in range(8)]


def _frac_brute(n):
    from fractions import Fraction
    seen = set()
    res = []
    for d in range(2, n + 1):
        for num in range(1, d):
            f = Fraction(num, d)
            if f not in seen:
                seen.add(f)
                res.append(f"{num}/{d}")
    return res


def _frac_gen(r):
    return [{"n": r.randint(1, 20)} for _ in range(8)]


def _folder_brute(names):
    used = set()
    res = []
    for name in names:
        if name not in used:
            used.add(name)
            res.append(name)
        else:
            k = 1
            while f"{name}({k})" in used:
                k += 1
            new = f"{name}({k})"
            used.add(new)
            res.append(new)
    return res


def _folder_gen(r):
    pool = ["a", "b", "gta", "a(1)", "b(2)", "x"]
    return [{"names": [r.choice(pool) for _ in range(r.randint(1, 8))]} for _ in range(8)]


def _span_brute(prices):
    res = []
    for i in range(len(prices)):
        s = 1
        j = i - 1
        while j >= 0 and prices[j] <= prices[i]:
            s += 1
            j -= 1
        res.append(s)
    return res


def _span_gen(r):
    return [{"prices": [r.randint(1, 20) for _ in range(r.randint(1, 12))]} for _ in range(8)]


def _majq_brute(arr, queries):
    res = []
    for left, right, threshold in queries:
        window = arr[left:right + 1]
        best = -1
        for v in set(window):
            if window.count(v) >= threshold:
                best = v
                break
        res.append(best)
    return res


def _majq_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(1, 10)
        arr = [r.randint(1, 5) for _ in range(n)]
        queries = []
        for _ in range(r.randint(1, 4)):
            l = r.randint(0, n - 1)
            rr = r.randint(l, n - 1)
            length = rr - l + 1
            threshold = r.randint(length // 2 + 1, length)
            queries.append([l, rr, threshold])
        out.append({"arr": arr, "queries": queries})
    return out


def _shelf_brute(books, shelfWidth):
    from functools import lru_cache
    n = len(books)

    @lru_cache(None)
    def solve(i):
        if i == n:
            return 0
        width = 0
        height = 0
        best = float('inf')
        j = i
        while j < n and width + books[j][0] <= shelfWidth:
            width += books[j][0]
            height = max(height, books[j][1])
            best = min(best, height + solve(j + 1))
            j += 1
        return best

    return solve(0)


def _shelf_gen(r):
    out = []
    for _ in range(8):
        sw = r.randint(2, 8)
        n = r.randint(1, 8)
        books = [[r.randint(1, sw), r.randint(1, 10)] for _ in range(n)]
        out.append({"books": books, "shelfWidth": sw})
    return out


def _exctime_brute(n, logs):
    parsed = [(int(a), b, int(c)) for a, b, c in (log.split(':') for log in logs)]
    res = [0] * n
    stack = []
    idx = 0
    L = len(parsed)
    max_t = max(p[2] for p in parsed)
    for t in range(max_t + 1):
        while idx < L and parsed[idx][1] == 'start' and parsed[idx][2] == t:
            stack.append(parsed[idx][0])
            idx += 1
        if stack:
            res[stack[-1]] += 1
        while idx < L and parsed[idx][1] == 'end' and parsed[idx][2] == t:
            stack.pop()
            idx += 1
    return res


def _exctime_gen(r):
    out = []
    for _ in range(6):
        n = r.randint(1, 4)
        logs = []
        stack = []
        t = 0
        next_fid = 0
        while next_fid < n or stack:
            if next_fid < n and (not stack or r.random() < 0.5):
                logs.append(f"{next_fid}:start:{t}")
                stack.append(next_fid)
                next_fid += 1
            else:
                logs.append(f"{stack.pop()}:end:{t}")
            t += 1
        out.append({"n": n, "logs": logs})
    return out


def _shift_brute(S, shifts):
    arr = [ord(c) - 97 for c in S]
    for i, x in enumerate(shifts):
        x %= 26
        for j in range(i + 1):
            arr[j] = (arr[j] + x) % 26
    return "".join(chr(97 + a) for a in arr)


def _shift_gen(r):
    out = []
    for _ in range(8):
        n = r.randint(1, 10)
        S = "".join(r.choice("abcxyz") for _ in range(n))
        shifts = [r.randint(0, 10 ** 9) for _ in range(n)]
        out.append({"S": S, "shifts": shifts})
    return out


def _alert_brute(keyName, keyTime):
    from collections import defaultdict
    times = defaultdict(list)
    for name, t in zip(keyName, keyTime):
        h, m = t.split(':')
        times[name].append(int(h) * 60 + int(m))
    res = set()
    for name, ts in times.items():
        ts.sort()
        n = len(ts)
        for i in range(n):
            cnt = sum(1 for j in range(n) if 0 <= ts[j] - ts[i] <= 60)
            if cnt >= 3:
                res.add(name)
    return sorted(res)


def _alert_gen(r):
    out = []
    pool = ["a", "b", "c"]
    for _ in range(8):
        kn, kt = [], []
        used = set()
        for _ in range(r.randint(1, 10)):
            name = r.choice(pool)
            t = f"{r.randint(0, 23):02d}:{r.randint(0, 59):02d}"
            if (name, t) in used:
                continue
            used.add((name, t))
            kn.append(name); kt.append(t)
        if not kn:
            kn, kt = ["a"], ["00:00"]
        out.append({"keyName": kn, "keyTime": kt})
    return out


def _smallestleaf_brute(root):
    if not root:
        return ""
    left, right, val = _build_tree(root)
    res = []

    def dfs(node, path):
        path = chr(97 + val[node]) + path
        if node not in left and node not in right:
            res.append(path)
        else:
            if node in left:
                dfs(left[node], path)
            if node in right:
                dfs(right[node], path)

    dfs(0, "")
    return min(res)


def _smallestleaf_gen(r):
    return [{"root": _rand_tree_vals(r, r.randint(1, 12), 0, 25)} for _ in range(8)]


def _largestrow_brute(root):
    if not root or root[0] is None:
        return []
    left, right, val = _build_tree(root)
    depth_max = {}

    def dfs(node, d):
        if d not in depth_max or val[node] > depth_max[d]:
            depth_max[d] = val[node]
        if node in left:
            dfs(left[node], d + 1)
        if node in right:
            dfs(right[node], d + 1)

    dfs(0, 0)
    return [depth_max[d] for d in range(len(depth_max))]


def _largestrow_gen(r):
    return [{"root": _rand_tree_vals(r, r.randint(1, 12), -50, 50)} for _ in range(8)]


def _sort_brute(nums):
    return sorted(nums)


def _sort_gen(r):
    return [{"nums": [r.randint(-50, 50) for _ in range(r.randint(1, 20))]} for _ in range(8)]


# ===========================================================================
# 1. Rearrange Words in a Sentence
# ===========================================================================
add("rearrange-words-in-a-sentence", "Rearrange Words in a Sentence", "medium",
    ["string", "sorting"], "arrangeWords", [("text", "str")], "str",
    """
`text` is a sentence: space-separated words, the first word capitalised and every
other character lowercase. Rearrange the words in **increasing order of their
length**; words of equal length keep their original relative order (a stable
sort). Re-emit the result in the same format: capitalise only the first letter of
the new sentence and lowercase the rest.

**Examples**
```
text = "Leetcode is cool"        ->  "Is cool leetcode"
text = "Keep calm and code on"   ->  "On and keep calm code"
text = "To be or not to be"      ->  "To be or to be not"
```

**Constraints:** `text` begins with a capital letter followed by lowercase letters
and single spaces, `1 <= len(text) <= 10^5`.
""",
    """def arrangeWords(text):
    words = text.lower().split()
    words.sort(key=len)
    res = " ".join(words)
    return res[:1].upper() + res[1:]
""",
    visible=[{"text": "Leetcode is cool"}, {"text": "Keep calm and code on"},
             {"text": "To be or not to be"}],
    hidden=[{"text": "A"}, {"text": "Hello"}, {"text": "I love leetcode"},
            {"text": "Cat dog bird ox"}],
    gen=_rearrange_gen,
    brute=_rearrange_brute,
    checks=[({"text": "Leetcode is cool"}, "Is cool leetcode"),
            ({"text": "Keep calm and code on"}, "On and keep calm code"),
            ({"text": "To be or not to be"}, "To be or to be not"),
            ({"text": "A"}, "A")],
    source="new_p")


# ===========================================================================
# 2. Reverse Substrings Between Each Pair of Parentheses
# ===========================================================================
add("reverse-substrings-between-each-pair-of-parentheses",
    "Reverse Substrings Between Each Pair of Parentheses", "medium",
    ["string", "stack"], "reverseParentheses", [("s", "str")], "str",
    """
`s` consists of lowercase letters and balanced parentheses. Reverse the contents of
each pair of matching parentheses, starting with the innermost pair. The returned
string must contain no brackets.

**Examples**
```
s = "(abcd)"                      ->  "dcba"
s = "(u(love)i)"                  ->  "iloveu"
s = "(ed(et(oc))el)"              ->  "leetcode"
s = "a(bcdefghijkl(mno)p)q"       ->  "apmnolkjihgfedcbq"
```

**Constraints:** `0 <= len(s) <= 2000`, `s` is lowercase letters and balanced
parentheses.
""",
    """def reverseParentheses(s):
    stack = [[]]
    for ch in s:
        if ch == '(':
            stack.append([])
        elif ch == ')':
            top = stack.pop()
            top.reverse()
            stack[-1].extend(top)
        else:
            stack[-1].append(ch)
    return "".join(stack[0])
""",
    visible=[{"s": "(abcd)"}, {"s": "(u(love)i)"}, {"s": "(ed(et(oc))el)"}],
    hidden=[{"s": ""}, {"s": "abc"}, {"s": "a(bcdefghijkl(mno)p)q"},
            {"s": "()"}, {"s": "(a(b(c)d)e)"}],
    gen=_revparen_gen,
    brute=_revparen_brute,
    checks=[({"s": "(abcd)"}, "dcba"), ({"s": "(u(love)i)"}, "iloveu"),
            ({"s": "(ed(et(oc))el)"}, "leetcode"),
            ({"s": "a(bcdefghijkl(mno)p)q"}, "apmnolkjihgfedcbq"),
            ({"s": "abc"}, "abc")],
    source="new_p")


# ===========================================================================
# 3. Minimum Remove to Make Valid Parentheses (reframed -> min count removed)
# ===========================================================================
add("minimum-remove-to-make-valid-parentheses",
    "Minimum Remove to Make Valid Parentheses", "medium",
    ["string", "stack", "greedy"], "minRemovals", [("s", "str")], "int",
    """
`s` consists of `'('`, `')'` and lowercase letters. You may delete parentheses
(at any positions). Return the **minimum number of parentheses you must remove** so
that the remaining string is valid — i.e. every `'('` has a matching later `')'`
and vice versa. (The minimum count is unique even though the resulting string need
not be.)

**Examples**
```
s = "lee(t(c)o)de)"   ->  1     (drop the trailing ')')
s = "a)b(c)d"         ->  1
s = "))(("            ->  4
s = "(a(b(c)d)"       ->  1
```

**Constraints:** `1 <= len(s) <= 10^5`, each character is `'('`, `')'` or a
lowercase letter.
""",
    """def minRemovals(s):
    open_unmatched = 0
    removals = 0
    for ch in s:
        if ch == '(':
            open_unmatched += 1
        elif ch == ')':
            if open_unmatched > 0:
                open_unmatched -= 1
            else:
                removals += 1
    return removals + open_unmatched
""",
    visible=[{"s": "lee(t(c)o)de)"}, {"s": "a)b(c)d"}, {"s": "))(("}, {"s": "(a(b(c)d)"}],
    hidden=[{"s": "abc"}, {"s": "("}, {"s": ")"}, {"s": "()"}, {"s": "(((((" }],
    gen=_minremove_gen,
    brute=_minremove_brute,
    checks=[({"s": "lee(t(c)o)de)"}, 1), ({"s": "a)b(c)d"}, 1), ({"s": "))(("}, 4),
            ({"s": "(a(b(c)d)"}, 1), ({"s": "abc"}, 0), ({"s": "()"}, 0)],
    source="new_p")


# ===========================================================================
# 4. String to Integer (atoi)
# ===========================================================================
add("string-to-integer-atoi", "String to Integer (atoi)", "medium",
    ["string"], "myAtoi", [("s", "str")], "int",
    """
Convert the string `s` to a 32-bit signed integer (like C's `atoi`):

1. Skip leading spaces (`' '` is the only whitespace considered).
2. Read an optional single `'+'` or `'-'` sign.
3. Read the following digits until a non-digit character (or the end) is reached.
4. Anything after the digits is ignored.

If no digits were read, return `0`. Clamp the result to the 32-bit signed range
`[-2^31, 2^31 - 1]`: values below `-2^31` become `-2^31` (`-2147483648`) and values
above `2^31 - 1` become `2^31 - 1` (`2147483647`).

**Examples**
```
s = "42"             ->  42
s = "   -42"         ->  -42
s = "4193 with words"->  4193
s = "words and 987"  ->  0
s = "-91283472332"   ->  -2147483648
```

**Constraints:** `0 <= len(s) <= 200`, `s` consists of digits, letters, `' '`,
`'+'` and `'-'`.
""",
    """def myAtoi(s):
    i, n = 0, len(s)
    while i < n and s[i] == ' ':
        i += 1
    sign = 1
    if i < n and s[i] in '+-':
        if s[i] == '-':
            sign = -1
        i += 1
    num = 0
    while i < n and s[i].isdigit():
        num = num * 10 + int(s[i])
        i += 1
    num *= sign
    INT_MIN, INT_MAX = -2 ** 31, 2 ** 31 - 1
    return max(INT_MIN, min(INT_MAX, num))
""",
    visible=[{"s": "42"}, {"s": "   -42"}, {"s": "4193 with words"},
             {"s": "words and 987"}, {"s": "-91283472332"}],
    hidden=[{"s": ""}, {"s": "   "}, {"s": "+1"}, {"s": "+-12"}, {"s": "00123"},
            {"s": "2147483648"}, {"s": "-2147483649"}, {"s": "  0 123"}],
    gen=_atoi_gen,
    brute=_atoi_brute,
    checks=[({"s": "42"}, 42), ({"s": "   -42"}, -42), ({"s": "4193 with words"}, 4193),
            ({"s": "words and 987"}, 0), ({"s": "-91283472332"}, -2147483648),
            ({"s": "2147483648"}, 2147483647), ({"s": "+1"}, 1), ({"s": ""}, 0)],
    source="new_p")


# ===========================================================================
# 5. Single Element in a Sorted Array
# ===========================================================================
add("single-element-in-a-sorted-array", "Single Element in a Sorted Array", "medium",
    ["array", "binary-search"], "singleNonDuplicate", [("nums", "int[]")], "int",
    """
`nums` is sorted in non-decreasing order; every value appears exactly twice except
for one value, which appears once. Return that single value. Aim for `O(log n)`
time and `O(1)` extra space.

**Examples**
```
nums = [1,1,2,3,3,4,4,8,8]   ->  2
nums = [3,3,7,7,10,11,11]    ->  10
```

**Constraints:** `1 <= len(nums) <= 10^5`, `0 <= nums[i] <= 10^5`, the array has the
structure described above.
""",
    """def singleNonDuplicate(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if mid % 2 == 1:
            mid -= 1
        if nums[mid] == nums[mid + 1]:
            lo = mid + 2
        else:
            hi = mid
    return nums[lo]
""",
    visible=[{"nums": [1, 1, 2, 3, 3, 4, 4, 8, 8]}, {"nums": [3, 3, 7, 7, 10, 11, 11]}],
    hidden=[{"nums": [1]}, {"nums": [0, 0, 5, 5, 7]}, {"nums": [7, 7, 9]},
            {"nums": [2, 4, 4]}, {"nums": [1, 1, 2, 2, 3, 3, 4]}],
    gen=_single_gen,
    brute=_single_brute,
    checks=[({"nums": [1, 1, 2, 3, 3, 4, 4, 8, 8]}, 2),
            ({"nums": [3, 3, 7, 7, 10, 11, 11]}, 10), ({"nums": [1]}, 1),
            ({"nums": [0, 0, 5, 5, 7]}, 7), ({"nums": [7, 7, 9]}, 9)],
    source="new_p")


# ===========================================================================
# 6. Minimum Falling Path Sum II
# ===========================================================================
add("minimum-falling-path-sum-ii", "Minimum Falling Path Sum II", "hard",
    ["array", "dynamic-programming", "matrix"], "minFallingPathSumII",
    [("arr", "int[][]")], "int",
    """
`arr` is an `n x n` grid of integers. A **falling path with non-zero shifts** picks
exactly one element from each row so that no two elements chosen in adjacent rows
share the same column. Return the minimum possible sum of such a path.

**Example**
```
arr = [[1,2,3],
       [4,5,6],
       [7,8,9]]   ->  13     (path 1 -> 5 -> 7)
```

**Constraints:** `1 <= n <= 200`, `-99 <= arr[i][j] <= 99`.
""",
    """def minFallingPathSumII(arr):
    n = len(arr)
    prev = arr[0][:]
    for i in range(1, n):
        m1 = m2 = None
        i1 = -1
        for j, v in enumerate(prev):
            if m1 is None or v < m1:
                m2 = m1; m1 = v; i1 = j
            elif m2 is None or v < m2:
                m2 = v
        cur = []
        for j in range(n):
            cur.append(arr[i][j] + (m2 if j == i1 else m1))
        prev = cur
    return min(prev)
""",
    visible=[{"arr": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}],
    hidden=[{"arr": [[7]]}, {"arr": [[1, 2], [3, 4]]},
            {"arr": [[-1, -2, -3], [-4, -5, -6], [-7, -8, -9]]},
            {"arr": [[2, 2, 1, 2, 2]]}, {"arr": [[5, 5], [5, 5]]}],
    gen=_falling2_gen,
    brute=_falling2_brute,
    checks=[({"arr": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}, 13), ({"arr": [[7]]}, 7),
            ({"arr": [[1, 2], [3, 4]]}, 5), ({"arr": [[2, 2, 1, 2, 2]]}, 1)],
    source="new_p")


# ===========================================================================
# 7. Stone Game II
# ===========================================================================
add("stone-game-ii", "Stone Game II", "medium",
    ["array", "dynamic-programming", "math", "prefix-sum"], "stoneGameII",
    [("piles", "int[]")], "int",
    """
`piles[i]` is the number of stones in the `i`-th pile, arranged in a row. Alice and
Bob alternate turns, Alice first, with `M = 1` initially. On a turn the current
player takes **all** the stones in the first `X` remaining piles for some
`1 <= X <= 2M`, then `M` becomes `max(M, X)`. Play continues until no piles remain.
Both play optimally to maximise their own stones; return the maximum number of
stones Alice can collect.

**Example**
```
piles = [2,7,9,4,4]   ->  10
```

**Constraints:** `1 <= len(piles) <= 100`, `1 <= piles[i] <= 10^4`.
""",
    """def stoneGameII(piles):
    from functools import lru_cache
    n = len(piles)
    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + piles[i]

    @lru_cache(None)
    def dp(i, m):
        if i >= n:
            return 0
        if i + 2 * m >= n:
            return suffix[i]
        best = 0
        for x in range(1, 2 * m + 1):
            best = max(best, suffix[i] - dp(i + x, max(m, x)))
        return best

    return dp(0, 1)
""",
    visible=[{"piles": [2, 7, 9, 4, 4]}],
    hidden=[{"piles": [1]}, {"piles": [2, 2]}, {"piles": [1, 2, 3, 4]},
            {"piles": [5, 5, 5, 5, 5, 5]}, {"piles": [3, 1, 4, 1, 5, 9, 2, 6]}],
    gen=_stone2_gen,
    brute=_stone2_brute,
    checks=[({"piles": [2, 7, 9, 4, 4]}, 10), ({"piles": [1]}, 1),
            ({"piles": [2, 2]}, 4), ({"piles": [1, 2, 3, 4, 5, 100]}, 104)],
    source="new_p")


# ===========================================================================
# 8. Get Watched Videos by Your Friends
# ===========================================================================
add("get-watched-videos-by-your-friends", "Get Watched Videos by Your Friends", "medium",
    ["graph", "breadth-first-search", "hash-table", "sorting"],
    "watchedVideosByFriends",
    [("watchedVideos", "str[][]"), ("friends", "int[][]"), ("id", "int"), ("level", "int")],
    "str[]",
    """
There are `n` people with ids `0..n-1`. `watchedVideos[i]` lists the videos watched
by person `i`, and `friends[i]` lists that person's friends (the friendship graph is
undirected). Starting from person `id`, the people at *level k* are exactly those
whose shortest-path distance to you equals `k`.

Collect all videos watched by the people at the given `level`, and return them
ordered by **frequency (increasing)**; videos with equal frequency are ordered
alphabetically.

**Examples**
```
watchedVideos = [["A","B"],["C"],["B","C"],["D"]],
friends = [[1,2],[0,3],[0,3],[1,2]], id = 0, level = 1   ->  ["B","C"]

same graph, level = 2                                    ->  ["D"]
```

**Constraints:** `2 <= n <= 100`, `1 <= level < n`, the graph is undirected.
""",
    """def watchedVideosByFriends(watchedVideos, friends, id, level):
    from collections import deque, Counter
    n = len(friends)
    visited = [False] * n
    visited[id] = True
    q = deque([id])
    for _ in range(level):
        for _ in range(len(q)):
            u = q.popleft()
            for v in friends[u]:
                if not visited[v]:
                    visited[v] = True
                    q.append(v)
    cnt = Counter()
    for u in q:
        for vid in watchedVideos[u]:
            cnt[vid] += 1
    return sorted(cnt, key=lambda x: (cnt[x], x))
""",
    visible=[{"watchedVideos": [["A", "B"], ["C"], ["B", "C"], ["D"]],
              "friends": [[1, 2], [0, 3], [0, 3], [1, 2]], "id": 0, "level": 1},
             {"watchedVideos": [["A", "B"], ["C"], ["B", "C"], ["D"]],
              "friends": [[1, 2], [0, 3], [0, 3], [1, 2]], "id": 0, "level": 2}],
    hidden=[{"watchedVideos": [["W"], ["X"]], "friends": [[1], [0]], "id": 0, "level": 1},
            {"watchedVideos": [["A"], ["A"], ["A"]], "friends": [[1, 2], [0], [0]],
             "id": 0, "level": 1},
            {"watchedVideos": [["bb", "aa"], ["aa"]], "friends": [[1], [0]],
             "id": 1, "level": 1}],
    gen=_watched_gen,
    brute=_watched_brute,
    checks=[({"watchedVideos": [["A", "B"], ["C"], ["B", "C"], ["D"]],
              "friends": [[1, 2], [0, 3], [0, 3], [1, 2]], "id": 0, "level": 1}, ["B", "C"]),
            ({"watchedVideos": [["A", "B"], ["C"], ["B", "C"], ["D"]],
              "friends": [[1, 2], [0, 3], [0, 3], [1, 2]], "id": 0, "level": 2}, ["D"])],
    source="new_p")


# ===========================================================================
# 9. Rabbits in Forest
# ===========================================================================
add("rabbits-in-forest", "Rabbits in Forest", "medium",
    ["array", "hash-table", "math", "greedy"], "numRabbits", [("answers", "int[]")], "int",
    """
Each rabbit in a forest has a colour. Some rabbits told you how many **other**
rabbits share their colour; those replies are collected in `answers`. Return the
minimum number of rabbits that could be in the forest consistent with the replies.

Two rabbits giving the same answer `x` may share a colour, but each colour group
that answers `x` holds exactly `x + 1` rabbits.

**Examples**
```
answers = [1,1,2]      ->  5
answers = [10,10,10]   ->  11
answers = []           ->  0
```

**Constraints:** `0 <= len(answers) <= 1000`, `0 <= answers[i] <= 999`.
""",
    """def numRabbits(answers):
    from collections import Counter
    total = 0
    for x, c in Counter(answers).items():
        group = x + 1
        groups = (c + group - 1) // group
        total += groups * group
    return total
""",
    visible=[{"answers": [1, 1, 2]}, {"answers": [10, 10, 10]}, {"answers": []}],
    hidden=[{"answers": [0]}, {"answers": [0, 0, 0]}, {"answers": [1]},
            {"answers": [2, 2, 2, 2]}, {"answers": [3, 0, 1, 1, 0]}],
    gen=_rabbits_gen,
    brute=_rabbits_brute,
    checks=[({"answers": [1, 1, 2]}, 5), ({"answers": [10, 10, 10]}, 11),
            ({"answers": []}, 0), ({"answers": [0, 0, 0]}, 3), ({"answers": [1]}, 2)],
    source="new_p")


# ===========================================================================
# 10. Simplified Fractions  (COMPARE: unordered)
# ===========================================================================
add("simplified-fractions", "Simplified Fractions", "medium",
    ["math", "string", "number-theory"], "simplifiedFractions", [("n", "int")], "str[]",
    """
Given an integer `n`, return every simplified fraction strictly between `0` and `1`
whose denominator is at most `n`. A fraction `a/b` is *simplified* when `gcd(a, b)`
is `1`. Each fraction is formatted as `"numerator/denominator"`. The fractions may
be returned **in any order**.

**Examples**
```
n = 2   ->  ["1/2"]
n = 3   ->  ["1/2","1/3","2/3"]
n = 4   ->  ["1/2","1/3","1/4","2/3","3/4"]
n = 1   ->  []
```

**Constraints:** `1 <= n <= 100`.
""",
    """def simplifiedFractions(n):
    from math import gcd
    res = []
    for d in range(2, n + 1):
        for num in range(1, d):
            if gcd(num, d) == 1:
                res.append(f"{num}/{d}")
    return res
""",
    visible=[{"n": 2}, {"n": 3}, {"n": 4}],
    hidden=[{"n": 1}, {"n": 5}, {"n": 6}, {"n": 10}],
    gen=_frac_gen,
    brute=_frac_brute,
    checks=[({"n": 2}, ["1/2"]), ({"n": 3}, ["1/2", "1/3", "2/3"]),
            ({"n": 4}, ["1/2", "1/3", "1/4", "2/3", "3/4"]), ({"n": 1}, [])],
    norm=sorted,
    source="new_p")
COMPARE["simplified-fractions"] = "unordered"


# ===========================================================================
# 11. Making File Names Unique
# ===========================================================================
add("making-file-names-unique", "Making File Names Unique", "medium",
    ["array", "hash-table", "string"], "getFolderNames", [("names", "str[]")], "str[]",
    """
You create `n` folders in order; at minute `i` you request the name `names[i]`. If a
requested name is already taken, the system appends the smallest suffix `(k)` with
`k` a positive integer making the name unique. Return the list of names actually
assigned, in order.

Note the suffix is added even to a name that already ends in `(k)`.

**Examples**
```
names = ["pes","fifa","gta","pes(2019)"]
  ->  ["pes","fifa","gta","pes(2019)"]
names = ["gta","gta(1)","gta","avalon"]
  ->  ["gta","gta(1)","gta(2)","avalon"]
names = ["kaido","kaido(1)","kaido","kaido(1)"]
  ->  ["kaido","kaido(1)","kaido(2)","kaido(1)(1)"]
```

**Constraints:** `1 <= len(names) <= 5*10^4`, names use lowercase letters, digits and
round brackets, `1 <= len(names[i]) <= 20`.
""",
    """def getFolderNames(names):
    seen = {}
    res = []
    for name in names:
        if name not in seen:
            seen[name] = 1
            res.append(name)
        else:
            k = seen[name]
            while f"{name}({k})" in seen:
                k += 1
            new = f"{name}({k})"
            seen[name] = k + 1
            seen[new] = 1
            res.append(new)
    return res
""",
    visible=[{"names": ["pes", "fifa", "gta", "pes(2019)"]},
             {"names": ["gta", "gta(1)", "gta", "avalon"]},
             {"names": ["kaido", "kaido(1)", "kaido", "kaido(1)"]}],
    hidden=[{"names": ["wano", "wano", "wano", "wano"]},
            {"names": ["onepiece", "onepiece(1)", "onepiece(2)", "onepiece(3)", "onepiece"]},
            {"names": ["a"]}, {"names": ["a", "a", "a(1)"]}],
    gen=_folder_gen,
    brute=_folder_brute,
    checks=[({"names": ["pes", "fifa", "gta", "pes(2019)"]},
             ["pes", "fifa", "gta", "pes(2019)"]),
            ({"names": ["gta", "gta(1)", "gta", "avalon"]},
             ["gta", "gta(1)", "gta(2)", "avalon"]),
            ({"names": ["onepiece", "onepiece(1)", "onepiece(2)", "onepiece(3)", "onepiece"]},
             ["onepiece", "onepiece(1)", "onepiece(2)", "onepiece(3)", "onepiece(4)"]),
            ({"names": ["wano", "wano", "wano", "wano"]},
             ["wano", "wano(1)", "wano(2)", "wano(3)"]),
            ({"names": ["kaido", "kaido(1)", "kaido", "kaido(1)"]},
             ["kaido", "kaido(1)", "kaido(2)", "kaido(1)(1)"])],
    source="new_p")


# ===========================================================================
# 12. Online Stock Span (reframed -> price list to span list)
# ===========================================================================
add("online-stock-span", "Online Stock Span", "medium",
    ["array", "stack", "monotonic-stack"], "stockSpans", [("prices", "int[]")], "int[]",
    """
Given the daily stock `prices` in order, return the list of **spans**. The span on a
day is the number of consecutive days ending on that day (going backwards) for which
the price was less than or equal to that day's price.

**Example**
```
prices = [100,80,60,70,60,75,85]   ->  [1,1,1,2,1,4,6]
```

**Constraints:** `1 <= len(prices) <= 10^4`, `1 <= prices[i] <= 10^5`.
""",
    """def stockSpans(prices):
    res = []
    stack = []  # (price, span)
    for p in prices:
        span = 1
        while stack and stack[-1][0] <= p:
            span += stack.pop()[1]
        stack.append((p, span))
        res.append(span)
    return res
""",
    visible=[{"prices": [100, 80, 60, 70, 60, 75, 85]}],
    hidden=[{"prices": [100]}, {"prices": [10, 20, 30]}, {"prices": [30, 20, 10]},
            {"prices": [5, 5, 5, 5]}, {"prices": [1, 3, 2, 4, 3, 5]}],
    gen=_span_gen,
    brute=_span_brute,
    checks=[({"prices": [100, 80, 60, 70, 60, 75, 85]}, [1, 1, 1, 2, 1, 4, 6]),
            ({"prices": [100]}, [1]), ({"prices": [10, 20, 30]}, [1, 2, 3]),
            ({"prices": [30, 20, 10]}, [1, 1, 1]), ({"prices": [5, 5, 5, 5]}, [1, 2, 3, 4])],
    source="new_p")


# ===========================================================================
# 13. Online Majority Element in Subarray (reframed -> batch of queries)
# ===========================================================================
add("online-majority-element-in-subarray", "Online Majority Element in Subarray", "hard",
    ["array", "binary-search", "segment-tree"], "majorityQueries",
    [("arr", "int[]"), ("queries", "int[][]")], "int[]",
    """
You are given an array `arr` and a list of `queries`, each a triple
`[left, right, threshold]`. For each query, return the value that occurs **at least
`threshold` times** in the subarray `arr[left..right]` (inclusive), or `-1` if no
value does. It is guaranteed that `2 * threshold > right - left + 1`, so at most one
value can qualify per query. Return one answer per query, in order.

**Example**
```
arr = [1,1,2,2,1,1]
queries = [[0,5,4],[0,3,3],[2,3,2]]   ->  [1,-1,2]
```

**Constraints:** `1 <= len(arr) <= 2*10^4`, `1 <= arr[i] <= 2*10^4`,
`0 <= left <= right < len(arr)`, `2 * threshold > right - left + 1`.
""",
    """def majorityQueries(arr, queries):
    from collections import Counter
    res = []
    for left, right, threshold in queries:
        cnt = Counter(arr[left:right + 1])
        ans = -1
        for val, c in cnt.items():
            if c >= threshold:
                ans = val
                break
        res.append(ans)
    return res
""",
    visible=[{"arr": [1, 1, 2, 2, 1, 1], "queries": [[0, 5, 4], [0, 3, 3], [2, 3, 2]]}],
    hidden=[{"arr": [5], "queries": [[0, 0, 1]]},
            {"arr": [1, 2, 3, 4], "queries": [[0, 3, 3]]},
            {"arr": [2, 2, 2], "queries": [[0, 2, 2], [1, 2, 2]]},
            {"arr": [7, 7, 7, 7, 8], "queries": [[0, 4, 3], [3, 4, 2]]}],
    gen=_majq_gen,
    brute=_majq_brute,
    checks=[({"arr": [1, 1, 2, 2, 1, 1], "queries": [[0, 5, 4], [0, 3, 3], [2, 3, 2]]},
             [1, -1, 2]),
            ({"arr": [5], "queries": [[0, 0, 1]]}, [5]),
            ({"arr": [1, 2, 3, 4], "queries": [[0, 3, 3]]}, [-1])],
    source="new_p")


# ===========================================================================
# 14. Filling Bookcase Shelves
# ===========================================================================
add("filling-bookcase-shelves", "Filling Bookcase Shelves", "medium",
    ["array", "dynamic-programming"], "minHeightShelves",
    [("books", "int[][]"), ("shelfWidth", "int")], "int",
    """
`books[i] = [thickness, height]`. Place the books, **in the given order**, onto
shelves each of width `shelfWidth`. Fill a shelf with a prefix of the remaining
books whose total thickness is at most `shelfWidth`, then start a new shelf above it;
that shelf adds the maximum height of the books on it to the total height. Return the
minimum possible total height of the bookcase.

**Example**
```
books = [[1,1],[2,3],[2,3],[1,1],[1,1],[1,1],[1,2]], shelfWidth = 4   ->  6
```

**Constraints:** `1 <= len(books) <= 1000`,
`1 <= books[i][0] <= shelfWidth <= 1000`, `1 <= books[i][1] <= 1000`.
""",
    """def minHeightShelves(books, shelfWidth):
    n = len(books)
    INF = float('inf')
    dp = [0] + [INF] * n
    for i in range(1, n + 1):
        width = 0
        height = 0
        j = i
        while j >= 1 and width + books[j - 1][0] <= shelfWidth:
            width += books[j - 1][0]
            height = max(height, books[j - 1][1])
            dp[i] = min(dp[i], dp[j - 1] + height)
            j -= 1
    return dp[n]
""",
    visible=[{"books": [[1, 1], [2, 3], [2, 3], [1, 1], [1, 1], [1, 1], [1, 2]], "shelfWidth": 4}],
    hidden=[{"books": [[1, 1]], "shelfWidth": 1}, {"books": [[1, 3], [2, 4]], "shelfWidth": 2},
            {"books": [[1, 5], [1, 5], [1, 5]], "shelfWidth": 3},
            {"books": [[3, 2], [1, 4], [2, 1]], "shelfWidth": 3}],
    gen=_shelf_gen,
    brute=_shelf_brute,
    checks=[({"books": [[1, 1], [2, 3], [2, 3], [1, 1], [1, 1], [1, 1], [1, 2]], "shelfWidth": 4}, 6),
            ({"books": [[1, 1]], "shelfWidth": 1}, 1),
            ({"books": [[1, 3], [2, 4]], "shelfWidth": 2}, 7),
            ({"books": [[1, 5], [1, 5], [1, 5]], "shelfWidth": 3}, 5)],
    source="new_p")


# ===========================================================================
# 15. Exclusive Time of Functions
# ===========================================================================
add("exclusive-time-of-functions", "Exclusive Time of Functions", "medium",
    ["array", "stack"], "exclusiveTime", [("n", "int"), ("logs", "str[]")], "int[]",
    """
`n` functions (ids `0..n-1`) run on a single-threaded CPU. `logs` is ordered by
time; each entry is `"id:start:t"` or `"id:end:t"`. `"id:start:t"` means the function
begins at the start of time unit `t`; `"id:end:t"` means it ends at the end of time
unit `t` (so it occupied unit `t`). Functions may call each other (and recurse), and
calls are properly nested.

The **exclusive time** of a function is the number of time units spent in it, not
counting time spent inside functions it called. Return the exclusive time of each
function, indexed by id.

**Example**
```
n = 2
logs = ["0:start:0","1:start:2","1:end:5","0:end:6"]   ->  [3,4]
```

**Constraints:** `1 <= n <= 100`, `1 <= len(logs) <= 500`, timestamps fit in a
32-bit integer.
""",
    """def exclusiveTime(n, logs):
    res = [0] * n
    stack = []
    prev = 0
    for log in logs:
        fid_s, typ, ts_s = log.split(':')
        fid, ts = int(fid_s), int(ts_s)
        if typ == 'start':
            if stack:
                res[stack[-1]] += ts - prev
            stack.append(fid)
            prev = ts
        else:
            res[stack.pop()] += ts - prev + 1
            prev = ts + 1
    return res
""",
    visible=[{"n": 2, "logs": ["0:start:0", "1:start:2", "1:end:5", "0:end:6"]}],
    hidden=[{"n": 1, "logs": ["0:start:0", "0:end:0"]},
            {"n": 1, "logs": ["0:start:0", "0:end:5"]},
            {"n": 2, "logs": ["0:start:0", "0:end:1", "1:start:2", "1:end:3"]},
            {"n": 3, "logs": ["0:start:0", "1:start:1", "2:start:2", "2:end:3", "1:end:4", "0:end:5"]}],
    gen=_exctime_gen,
    brute=_exctime_brute,
    checks=[({"n": 2, "logs": ["0:start:0", "1:start:2", "1:end:5", "0:end:6"]}, [3, 4]),
            ({"n": 1, "logs": ["0:start:0", "0:end:0"]}, [1]),
            ({"n": 1, "logs": ["0:start:0", "0:end:5"]}, [6]),
            ({"n": 2, "logs": ["0:start:0", "0:end:1", "1:start:2", "1:end:3"]}, [2, 2])],
    source="new_p")


# ===========================================================================
# 16. Shifting Letters
# ===========================================================================
add("shifting-letters", "Shifting Letters", "medium",
    ["array", "string", "prefix-sum"], "shiftingLetters",
    [("S", "str"), ("shifts", "int[]")], "str",
    """
`S` is a string of lowercase letters and `shifts` has the same length. To *shift* a
letter means to advance it in the alphabet, wrapping `'z'` to `'a'`. For each `i`,
`shifts[i]` shifts the **first `i + 1` letters** of `S` by `shifts[i]` positions.
Return the final string after all shifts are applied.

**Example**
```
S = "abc", shifts = [3,5,9]   ->  "rpl"
```

**Constraints:** `1 <= len(S) == len(shifts) <= 2*10^4`, `0 <= shifts[i] <= 10^9`.
""",
    """def shiftingLetters(S, shifts):
    n = len(S)
    res = [''] * n
    suffix = 0
    for i in range(n - 1, -1, -1):
        suffix = (suffix + shifts[i]) % 26
        res[i] = chr(97 + (ord(S[i]) - 97 + suffix) % 26)
    return "".join(res)
""",
    visible=[{"S": "abc", "shifts": [3, 5, 9]}],
    hidden=[{"S": "a", "shifts": [0]}, {"S": "z", "shifts": [1]},
            {"S": "aaa", "shifts": [1, 1, 1]}, {"S": "xyz", "shifts": [26, 52, 1]},
            {"S": "ruby", "shifts": [1000000000, 0, 5, 7]}],
    gen=_shift_gen,
    brute=_shift_brute,
    checks=[({"S": "abc", "shifts": [3, 5, 9]}, "rpl"), ({"S": "a", "shifts": [0]}, "a"),
            ({"S": "z", "shifts": [1]}, "a"), ({"S": "aaa", "shifts": [1, 1, 1]}, "dcb")],
    source="new_p")


# ===========================================================================
# 17. Alert Using Same Key-Card Three or More Times in a One-Hour Period
# ===========================================================================
add("alert-using-same-key-card-three-or-more-times-in-a-one-hour-period",
    "Alert Using Same Key-Card Three or More Times in a One-Hour Period", "medium",
    ["array", "hash-table", "string", "sorting"], "alertNames",
    [("keyName", "str[]"), ("keyTime", "str[]")], "str[]",
    """
Each worker swipes a key-card to open doors; `[keyName[i], keyTime[i]]` records who
swiped and when, in `"HH:MM"` 24-hour time on a single day. An alert fires for a
worker who swipes **three or more times within any one-hour window** (a window of at
most 60 minutes, inclusive — e.g. `"10:00"`–`"11:00"` counts, `"22:51"`–`"23:52"`
does not). Return the alerted workers' names, sorted alphabetically.

**Examples**
```
keyName = ["daniel","daniel","daniel","luis","luis","luis","luis"],
keyTime = ["10:00","10:40","11:00","09:00","11:00","13:00","15:00"]   ->  ["daniel"]

keyName = ["leslie","leslie","leslie","clare","clare","clare","clare"],
keyTime = ["13:00","13:20","14:00","18:00","18:51","19:30","19:49"]   ->  ["clare","leslie"]
```

**Constraints:** `1 <= len(keyName) == len(keyTime) <= 10^5`, names are lowercase,
each `[name, time]` pair is unique.
""",
    """def alertNames(keyName, keyTime):
    from collections import defaultdict
    times = defaultdict(list)
    for name, t in zip(keyName, keyTime):
        h, m = t.split(':')
        times[name].append(int(h) * 60 + int(m))
    res = []
    for name, ts in times.items():
        ts.sort()
        for i in range(2, len(ts)):
            if ts[i] - ts[i - 2] <= 60:
                res.append(name)
                break
    return sorted(res)
""",
    visible=[{"keyName": ["daniel", "daniel", "daniel", "luis", "luis", "luis", "luis"],
              "keyTime": ["10:00", "10:40", "11:00", "09:00", "11:00", "13:00", "15:00"]},
             {"keyName": ["leslie", "leslie", "leslie", "clare", "clare", "clare", "clare"],
              "keyTime": ["13:00", "13:20", "14:00", "18:00", "18:51", "19:30", "19:49"]}],
    hidden=[{"keyName": ["alice", "alice", "alice", "bob", "bob", "bob", "bob"],
             "keyTime": ["12:01", "12:00", "18:00", "21:00", "21:20", "21:30", "23:00"]},
            {"keyName": ["john", "john", "john"], "keyTime": ["23:58", "23:59", "00:01"]},
            {"keyName": ["a"], "keyTime": ["00:00"]},
            {"keyName": ["z", "z", "z"], "keyTime": ["00:00", "00:30", "01:00"]}],
    gen=_alert_gen,
    brute=_alert_brute,
    checks=[({"keyName": ["daniel", "daniel", "daniel", "luis", "luis", "luis", "luis"],
              "keyTime": ["10:00", "10:40", "11:00", "09:00", "11:00", "13:00", "15:00"]},
             ["daniel"]),
            ({"keyName": ["alice", "alice", "alice", "bob", "bob", "bob", "bob"],
              "keyTime": ["12:01", "12:00", "18:00", "21:00", "21:20", "21:30", "23:00"]},
             ["bob"]),
            ({"keyName": ["john", "john", "john"], "keyTime": ["23:58", "23:59", "00:01"]}, []),
            ({"keyName": ["leslie", "leslie", "leslie", "clare", "clare", "clare", "clare"],
              "keyTime": ["13:00", "13:20", "14:00", "18:00", "18:51", "19:30", "19:49"]},
             ["clare", "leslie"])],
    source="new_p")


# ===========================================================================
# 18. Smallest String Starting From Leaf
# ===========================================================================
add("smallest-string-starting-from-leaf", "Smallest String Starting From Leaf", "medium",
    ["tree", "depth-first-search", "string"], "smallestFromLeaf",
    [("root", "int[]")], "str",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and is rebuilt inside your function. Each node's value is `0..25`,
representing `'a'..'z'`.

Consider every path that starts at a leaf and ends at the root, reading the
corresponding letters. Return the lexicographically smallest such string. (Recall a
shorter string that is a prefix of another is the smaller one, e.g. `"ab" < "aba"`.)

**Examples**
```
root = [0,1,2,3,4,3,4]            ->  "dba"
root = [25,1,3,1,3,0,2]           ->  "adz"
root = [2,2,1,null,1,0,null,0]    ->  "abc"
```

**Constraints:** `1 <= number of nodes <= 8500`, each value is `0..25`.
""",
    """def smallestFromLeaf(root):
    if not root:
        return ""
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
    best = [None]

    def dfs(node, suffix):
        s = chr(97 + val[node]) + suffix
        l, rr = left.get(node), right.get(node)
        if l is None and rr is None:
            if best[0] is None or s < best[0]:
                best[0] = s
            return
        if l is not None:
            dfs(l, s)
        if rr is not None:
            dfs(rr, s)

    dfs(0, "")
    return best[0]
""",
    visible=[{"root": [0, 1, 2, 3, 4, 3, 4]}, {"root": [25, 1, 3, 1, 3, 0, 2]},
             {"root": [2, 2, 1, None, 1, 0, None, 0]}],
    hidden=[{"root": [0]}, {"root": [25]}, {"root": [1, 0]},
            {"root": [3, 1, 2, None, None, 0]}, {"root": [0, 0, 0, 0]}],
    gen=_smallestleaf_gen,
    brute=_smallestleaf_brute,
    checks=[({"root": [0, 1, 2, 3, 4, 3, 4]}, "dba"),
            ({"root": [25, 1, 3, 1, 3, 0, 2]}, "adz"),
            ({"root": [2, 2, 1, None, 1, 0, None, 0]}, "abc"), ({"root": [0]}, "a")],
    source="new_p")


# ===========================================================================
# 19. Find Largest Value in Each Tree Row
# ===========================================================================
add("find-largest-value-in-each-tree-row", "Find Largest Value in Each Tree Row", "medium",
    ["tree", "breadth-first-search", "depth-first-search"], "largestValues",
    [("root", "int[]")], "int[]",
    """
A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and is rebuilt inside your function. Return a list whose `i`-th entry
is the largest value found in the `i`-th row (level) of the tree, top to bottom. An
empty tree returns an empty list.

**Example**
```
root = [1,3,2,5,3,null,9]   ->  [1,3,9]
```

**Constraints:** `0 <= number of nodes <= 10^4`, node values fit in a 32-bit
integer.
""",
    """def largestValues(root):
    if not root:
        return []
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
    res = []
    level = [0]
    while level:
        res.append(max(val[x] for x in level))
        nxt = []
        for x in level:
            if x in left:
                nxt.append(left[x])
            if x in right:
                nxt.append(right[x])
        level = nxt
    return res
""",
    visible=[{"root": [1, 3, 2, 5, 3, None, 9]}],
    hidden=[{"root": []}, {"root": [1]}, {"root": [-5]},
            {"root": [1, 2, 3, 4, 5, 6, 7]}, {"root": [10, -1, -2, None, -3]}],
    gen=_largestrow_gen,
    brute=_largestrow_brute,
    checks=[({"root": [1, 3, 2, 5, 3, None, 9]}, [1, 3, 9]), ({"root": []}, []),
            ({"root": [1]}, [1]), ({"root": [1, 2, 3, 4, 5, 6, 7]}, [1, 3, 7])],
    source="new_p")


# ===========================================================================
# 20. Sort an Array
# ===========================================================================
add("sort-an-array", "Sort an Array", "medium",
    ["array", "sorting", "divide-and-conquer"], "sortArray", [("nums", "int[]")], "int[]",
    """
Given an array of integers `nums`, return it sorted in ascending order.

**Examples**
```
nums = [5,2,3,1]       ->  [1,2,3,5]
nums = [5,1,1,2,0,0]   ->  [0,0,1,1,2,5]
```

**Constraints:** `1 <= len(nums) <= 5*10^4`, `-5*10^4 <= nums[i] <= 5*10^4`.
""",
    """def sortArray(nums):
    def merge_sort(a):
        if len(a) <= 1:
            return a
        mid = len(a) // 2
        left = merge_sort(a[:mid])
        right = merge_sort(a[mid:])
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i]); i += 1
            else:
                merged.append(right[j]); j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged
    return merge_sort(list(nums))
""",
    visible=[{"nums": [5, 2, 3, 1]}, {"nums": [5, 1, 1, 2, 0, 0]}],
    hidden=[{"nums": [1]}, {"nums": [2, 1]}, {"nums": [-3, -1, -2, 0]},
            {"nums": [4, 4, 4, 4]}, {"nums": [10, -10, 5, -5, 0]}],
    gen=_sort_gen,
    brute=_sort_brute,
    checks=[({"nums": [5, 2, 3, 1]}, [1, 2, 3, 5]),
            ({"nums": [5, 1, 1, 2, 0, 0]}, [0, 0, 1, 1, 2, 5]), ({"nums": [1]}, [1]),
            ({"nums": [-3, -1, -2, 0]}, [-3, -2, -1, 0])],
    source="new_p")
