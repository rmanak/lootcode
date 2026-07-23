"""Bulk-author a bank of coding problems and write them to content/problems/.

Strategy for correctness: each problem ships a canonical Python solution. Test
*inputs* are listed (plus random generators); every test's *expected* output is
COMPUTED by running the canonical solution — never hand-written. Each canonical
is additionally checked against (a) known answers from authoritative examples and
(b) a brute-force reference on random inputs. If anything disagrees, this script
raises before writing, so a buggy problem can't silently enter the bank.

Run:  python scripts/build_bank.py      (then: python scripts/seed.py)
"""
from __future__ import annotations

import copy
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app import content  # noqa: E402
from scripts import figures  # noqa: E402

PROBLEMS: list[dict] = []


def add(slug, title, difficulty, topics, fn, params, ret, statement, solution,
        visible, hidden=None, gen=None, brute=None, checks=None, norm=None,
        source="bank", assets=None):
    PROBLEMS.append(dict(
        slug=slug, title=title, difficulty=difficulty, topics=topics, fn=fn,
        params=params, ret=ret, statement=statement.strip() + "\n", solution=solution,
        visible=visible, hidden=hidden or [], gen=gen, brute=brute,
        checks=checks or [], norm=norm or (lambda x: x), source=source,
        assets=assets or {}))


def stub(fn, params):
    args = ", ".join(p[0] for p in params)
    return f"def {fn}({args}):\n    # Write your solution here.\n    pass\n"


# Random helpers ------------------------------------------------------------
def ilist(rng, n_lo, n_hi, v_lo, v_hi):
    return [rng.randint(v_lo, v_hi) for _ in range(rng.randint(n_lo, n_hi))]


def sstr(rng, n_lo, n_hi, alphabet="abc"):
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(n_lo, n_hi)))


def sorted_unique(rng, n, lo=-60, hi=60):
    return sorted(rng.sample(range(lo, hi), n))


def rotate(a, k):
    if not a:
        return a
    k %= len(a)
    return a[k:] + a[:k]


# ===========================================================================
# Problems sourced from coding_exercise_examples.txt (fitted to one function)
# ===========================================================================

add("longest-consecutive-sequence", "Longest Consecutive Sequence", "medium",
    ["array", "hash-set"], "longestConsecutive", [("nums", "int[]")], "int",
    """
Given an unsorted array of integers `nums`, return the length of the longest
sequence of consecutive integers (in value). Aim for `O(n)` time.

**Example:** `nums = [100, 4, 200, 1, 3, 2]` → `4` (the run `[1, 2, 3, 4]`).

**Constraints:** `0 <= len(nums) <= 10^5`, `-10^9 <= nums[i] <= 10^9`.
""",
    """def longestConsecutive(nums):
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best
""",
    visible=[{"nums": [100, 4, 200, 1, 3, 2]}, {"nums": [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]},
             {"nums": [1, 0, 1, 2]}],
    hidden=[{"nums": []}, {"nums": [5]}, {"nums": [-3, -2, -1, 0, 1]}],
    gen=lambda r: [{"nums": ilist(r, 0, 40, -20, 20)} for _ in range(4)],
    checks=[({"nums": [100, 4, 200, 1, 3, 2]}, 4),
            ({"nums": [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]}, 9), ({"nums": [1, 0, 1, 2]}, 3)],
    source="file")

add("longest-substring-without-repeating", "Longest Substring Without Repeating Characters",
    "medium", ["string", "sliding-window", "hash-table"], "lengthOfLongestSubstring",
    [("s", "string")], "int",
    """
Given a string `s`, return the length of the longest substring without repeating
characters.

**Example:** `s = "abcabcbb"` → `3` (the substring `"abc"`).

**Constraints:** `0 <= len(s) <= 5*10^4`.
""",
    """def lengthOfLongestSubstring(s):
    seen = {}
    start = best = 0
    for i, c in enumerate(s):
        if c in seen and seen[c] >= start:
            start = seen[c] + 1
        seen[c] = i
        best = max(best, i - start + 1)
    return best
""",
    visible=[{"s": "abcabcbb"}, {"s": "bbbbb"}, {"s": "pwwkew"}],
    hidden=[{"s": ""}, {"s": " "}, {"s": "abba"}, {"s": "dvdf"}],
    gen=lambda r: [{"s": sstr(r, 0, 30, "abcd ")} for _ in range(4)],
    checks=[({"s": "abcabcbb"}, 3), ({"s": "bbbbb"}, 1), ({"s": "pwwkew"}, 3),
            ({"s": ""}, 0)], source="file")

add("longest-palindromic-substring", "Longest Palindromic Substring", "medium",
    ["string", "dynamic-programming"], "longestPalindrome", [("s", "string")], "string",
    """
Given a string `s`, return the longest palindromic substring. If several have the
same maximal length, return the one that **starts at the smallest index**.

**Example:** `s = "babad"` → `"bab"`.

**Constraints:** `1 <= len(s) <= 1000`.
""",
    """def longestPalindrome(s):
    if not s:
        return ""
    start, end = 0, 0
    def expand(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return l + 1, r - 1
    for i in range(len(s)):
        for l, r in (expand(i, i), expand(i, i + 1)):
            if r - l > end - start:
                start, end = l, r
    return s[start:end + 1]
""",
    visible=[{"s": "babad"}, {"s": "cbbd"}],
    hidden=[{"s": "a"}, {"s": "ac"}, {"s": "aaaa"}, {"s": "abacdfgdcaba"}],
    gen=lambda r: [{"s": sstr(r, 1, 18, "aba c")} for _ in range(4)],
    checks=[({"s": "babad"}, "bab"), ({"s": "cbbd"}, "bb"), ({"s": "a"}, "a")],
    source="file")

add("palindromic-substrings", "Palindromic Substrings", "medium",
    ["string", "dynamic-programming"], "countSubstrings", [("s", "string")], "int",
    """
Given a string `s`, return the number of palindromic substrings (contiguous,
counted by position).

**Example:** `s = "aaa"` → `6`.

**Constraints:** `1 <= len(s) <= 1000`.
""",
    """def countSubstrings(s):
    n = len(s)
    count = 0
    def expand(l, r):
        c = 0
        while l >= 0 and r < n and s[l] == s[r]:
            c += 1
            l -= 1
            r += 1
        return c
    for i in range(n):
        count += expand(i, i) + expand(i, i + 1)
    return count
""",
    visible=[{"s": "abc"}, {"s": "aaa"}],
    hidden=[{"s": "a"}, {"s": "aba"}, {"s": "abba"}],
    gen=lambda r: [{"s": sstr(r, 1, 16, "ab")} for _ in range(4)],
    checks=[({"s": "abc"}, 3), ({"s": "aaa"}, 6)], source="file")

add("container-with-most-water", "Container With Most Water", "medium",
    ["array", "two-pointers", "greedy"], "maxArea", [("height", "int[]")], "int",
    """
Given `height[i]` (vertical lines), pick two lines that with the x-axis hold the
most water. Return that maximum area.

**Example:** `height = [1,8,6,2,5,4,8,3,7]` → `49`.

**Constraints:** `2 <= len(height) <= 10^5`, `0 <= height[i] <= 10^4`.
""",
    """def maxArea(height):
    l, r = 0, len(height) - 1
    best = 0
    while l < r:
        best = max(best, (r - l) * min(height[l], height[r]))
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return best
""",
    visible=[{"height": [1, 8, 6, 2, 5, 4, 8, 3, 7]}, {"height": [1, 1]}],
    hidden=[{"height": [4, 3, 2, 1, 4]}, {"height": [1, 2, 1]}],
    gen=lambda r: [{"height": ilist(r, 2, 30, 0, 50)} for _ in range(4)],
    brute=lambda height: max((j - i) * min(height[i], height[j])
                             for i in range(len(height)) for j in range(i + 1, len(height))),
    checks=[({"height": [1, 8, 6, 2, 5, 4, 8, 3, 7]}, 49), ({"height": [1, 1]}, 1)],
    source="file")

add("word-break", "Word Break", "medium", ["string", "dynamic-programming"],
    "wordBreak", [("s", "string"), ("wordDict", "string[]")], "bool",
    """
Given a string `s` and a list `wordDict`, return `true` if `s` can be segmented
into a sequence of one or more dictionary words (words may be reused).

**Example:** `s = "leetcode"`, `wordDict = ["leet","code"]` → `true`.

**Constraints:** `1 <= len(s) <= 300`.
""",
    """def wordBreak(s, wordDict):
    words = set(wordDict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[n]
""",
    visible=[{"s": "leetcode", "wordDict": ["leet", "code"]},
             {"s": "applepenapple", "wordDict": ["apple", "pen"]},
             {"s": "catsandog", "wordDict": ["cats", "dog", "sand", "and", "cat"]}],
    hidden=[{"s": "a", "wordDict": ["a"]}, {"s": "ab", "wordDict": ["a"]},
            {"s": "aaaaaaa", "wordDict": ["aaaa", "aaa"]}],
    checks=[({"s": "leetcode", "wordDict": ["leet", "code"]}, True),
            ({"s": "catsandog", "wordDict": ["cats", "dog", "sand", "and", "cat"]}, False)],
    source="file")

add("missing-number", "Missing Number", "easy", ["array", "math", "bit-manipulation"],
    "missingNumber", [("nums", "int[]")], "int",
    """
`nums` contains `n` distinct numbers from the range `[0, n]`. Return the one
number in that range missing from the array.

**Example:** `nums = [3,0,1]` → `2`.

**Constraints:** `1 <= len(nums) <= 10^4`.
""",
    """def missingNumber(nums):
    n = len(nums)
    return n * (n + 1) // 2 - sum(nums)
""",
    visible=[{"nums": [3, 0, 1]}, {"nums": [0, 1]}, {"nums": [9, 6, 4, 2, 3, 5, 7, 0, 1]}],
    hidden=[{"nums": [0]}, {"nums": [1]}],
    gen=lambda r: [(lambda n, miss: {"nums": [x for x in range(n + 1) if x != miss]})
                   (n, r.randint(0, n))
                   for n in [r.randint(1, 25) for _ in range(4)]],
    checks=[({"nums": [3, 0, 1]}, 2), ({"nums": [0, 1]}, 2),
            ({"nums": [9, 6, 4, 2, 3, 5, 7, 0, 1]}, 8)], source="file")

add("reorder-list", "Reorder List", "medium", ["linked-list", "two-pointers"],
    "reorderList", [("head", "int[]")], "int[]",
    """
A list `L0 -> L1 -> ... -> Ln` (given as an array of its values) should be
reordered to `L0 -> Ln -> L1 -> L(n-1) -> ...`. Return the reordered values.

**Example:** `head = [1,2,3,4]` → `[1,4,2,3]`.

**Constraints:** `1 <= len(head) <= 5*10^4`.
""",
    """def reorderList(head):
    res = []
    i, j = 0, len(head) - 1
    while i <= j:
        res.append(head[i])
        if i != j:
            res.append(head[j])
        i += 1
        j -= 1
    return res
""",
    visible=[{"head": [1, 2, 3, 4]}, {"head": [1, 2, 3, 4, 5]}],
    hidden=[{"head": [1]}, {"head": [1, 2]}, {"head": [1, 2, 3]}],
    gen=lambda r: [{"head": list(range(1, r.randint(1, 20)))} for _ in range(3)],
    checks=[({"head": [1, 2, 3, 4]}, [1, 4, 2, 3]),
            ({"head": [1, 2, 3, 4, 5]}, [1, 5, 2, 4, 3])], source="file")

add("remove-nth-from-end", "Remove Nth Node From End of List", "medium",
    ["linked-list", "two-pointers"], "removeNthFromEnd",
    [("head", "int[]"), ("n", "int")], "int[]",
    """
Given a list as an array of values and an integer `n`, remove the `n`-th node
from the end and return the remaining values.

**Example:** `head = [1,2,3,4,5]`, `n = 2` → `[1,2,3,5]`.

**Constraints:** `1 <= len(head) <= 30`, `1 <= n <= len(head)`.
""",
    """def removeNthFromEnd(head, n):
    idx = len(head) - n
    return head[:idx] + head[idx + 1:]
""",
    visible=[{"head": [1, 2, 3, 4, 5], "n": 2}, {"head": [1], "n": 1},
             {"head": [1, 2], "n": 1}],
    hidden=[{"head": [1, 2], "n": 2}, {"head": [7, 8, 9], "n": 3}],
    gen=lambda r: [(lambda h: {"head": h, "n": r.randint(1, len(h))})
                   (list(range(1, r.randint(2, 12)))) for _ in range(3)],
    checks=[({"head": [1, 2, 3, 4, 5], "n": 2}, [1, 2, 3, 5]),
            ({"head": [1], "n": 1}, [])], source="file")

add("valid-parentheses", "Valid Parentheses", "easy", ["stack", "string"],
    "isValid", [("s", "string")], "bool",
    """
Given a string `s` of just `()[]{}`, return `true` if every bracket is closed by
the same type in the correct order.

**Example:** `s = "([])"` → `true`; `s = "([)]"` → `false`.

**Constraints:** `1 <= len(s) <= 10^4`.
""",
    """def isValid(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    st = []
    for c in s:
        if c in pairs:
            if not st or st.pop() != pairs[c]:
                return False
        else:
            st.append(c)
    return not st
""",
    visible=[{"s": "()"}, {"s": "()[]{}"}, {"s": "(]"}, {"s": "([])"}, {"s": "([)]"}],
    hidden=[{"s": "("}, {"s": "]"}, {"s": "{[]}"}],
    gen=lambda r: [{"s": sstr(r, 1, 10, "()[]{}")} for _ in range(4)],
    checks=[({"s": "()[]{}"}, True), ({"s": "(]"}, False), ({"s": "([)]"}, False)],
    source="file")

add("merge-two-sorted-lists", "Merge Two Sorted Lists", "easy", ["linked-list"],
    "mergeTwoLists", [("list1", "int[]"), ("list2", "int[]")], "int[]",
    """
Merge two ascending lists (given as arrays) into one sorted list of their values.

**Example:** `list1 = [1,2,4]`, `list2 = [1,3,4]` → `[1,1,2,3,4,4]`.

**Constraints:** `0 <= len <= 50`, values sorted non-decreasing.
""",
    """def mergeTwoLists(list1, list2):
    res = []
    i = j = 0
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            res.append(list1[i])
            i += 1
        else:
            res.append(list2[j])
            j += 1
    res.extend(list1[i:])
    res.extend(list2[j:])
    return res
""",
    visible=[{"list1": [1, 2, 4], "list2": [1, 3, 4]}, {"list1": [], "list2": []},
             {"list1": [], "list2": [0]}],
    hidden=[{"list1": [1, 3, 5], "list2": [2, 4, 6]}, {"list1": [5], "list2": [1, 2, 3]}],
    gen=lambda r: [{"list1": sorted(ilist(r, 0, 8, -10, 10)),
                    "list2": sorted(ilist(r, 0, 8, -10, 10))} for _ in range(4)],
    brute=lambda list1, list2: sorted(list1 + list2),
    checks=[({"list1": [1, 2, 4], "list2": [1, 3, 4]}, [1, 1, 2, 3, 4, 4])], source="file")

add("merge-k-sorted-lists", "Merge k Sorted Lists", "hard",
    ["linked-list", "heap", "divide-and-conquer"], "mergeKLists",
    [("lists", "int[][]")], "int[]",
    """
Given `k` ascending lists (as an array of arrays), merge them into one sorted
list of all values.

**Example:** `lists = [[1,4,5],[1,3,4],[2,6]]` → `[1,1,2,3,4,4,5,6]`.

**Constraints:** `0 <= k <= 10^4`; total length `<= 10^4`.
""",
    """import heapq
def mergeKLists(lists):
    h = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(h, (lst[0], i, 0))
    res = []
    while h:
        val, i, j = heapq.heappop(h)
        res.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(h, (lists[i][j + 1], i, j + 1))
    return res
""",
    visible=[{"lists": [[1, 4, 5], [1, 3, 4], [2, 6]]}, {"lists": []}, {"lists": [[]]}],
    hidden=[{"lists": [[1], [0]]}, {"lists": [[-2, -1], [], [-3, 0]]}],
    gen=lambda r: [{"lists": [sorted(ilist(r, 0, 6, -9, 9)) for _ in range(r.randint(0, 4))]}
                   for _ in range(4)],
    brute=lambda lists: sorted(x for lst in lists for x in lst),
    checks=[({"lists": [[1, 4, 5], [1, 3, 4], [2, 6]]}, [1, 1, 2, 3, 4, 4, 5, 6])],
    source="file")

add("maximum-product-subarray", "Maximum Product Subarray", "medium",
    ["array", "dynamic-programming"], "maxProduct", [("nums", "int[]")], "int",
    """
Given an integer array `nums`, return the largest product of any contiguous
subarray.

**Example:** `nums = [2,3,-2,4]` → `6`.

**Constraints:** `1 <= len(nums) <= 2*10^4`, `-10 <= nums[i] <= 10`.
""",
    """def maxProduct(nums):
    best = cur_max = cur_min = nums[0]
    for x in nums[1:]:
        cands = (x, cur_max * x, cur_min * x)
        cur_max = max(cands)
        cur_min = min(cands)
        best = max(best, cur_max)
    return best
""",
    visible=[{"nums": [2, 3, -2, 4]}, {"nums": [-2, 0, -1]}],
    hidden=[{"nums": [-2]}, {"nums": [0, 2]}, {"nums": [-2, 3, -4]}],
    gen=lambda r: [{"nums": ilist(r, 1, 9, -4, 4)} for _ in range(5)],
    brute=lambda nums: max((__import__("math").prod(nums[i:j])
                           for i in range(len(nums)) for j in range(i + 1, len(nums) + 1))),
    checks=[({"nums": [2, 3, -2, 4]}, 6), ({"nums": [-2, 0, -1]}, 0)], source="file")

add("find-minimum-rotated-sorted", "Find Minimum in Rotated Sorted Array", "medium",
    ["array", "binary-search"], "findMin", [("nums", "int[]")], "int",
    """
A sorted array of unique values was rotated. Return its minimum in `O(log n)`.

**Example:** `nums = [4,5,6,7,0,1,2]` → `0`.

**Constraints:** `1 <= len(nums) <= 5000`, unique values.
""",
    """def findMin(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]
""",
    visible=[{"nums": [3, 4, 5, 1, 2]}, {"nums": [4, 5, 6, 7, 0, 1, 2]}, {"nums": [11, 13, 15, 17]}],
    hidden=[{"nums": [1]}, {"nums": [2, 1]}],
    gen=lambda r: [{"nums": rotate(sorted_unique(r, r.randint(1, 12)), r.randint(0, 11))}
                   for _ in range(5)],
    brute=lambda nums: min(nums),
    checks=[({"nums": [3, 4, 5, 1, 2]}, 1), ({"nums": [4, 5, 6, 7, 0, 1, 2]}, 0)],
    source="file")

add("search-rotated-sorted", "Search in Rotated Sorted Array", "medium",
    ["array", "binary-search"], "search", [("nums", "int[]"), ("target", "int")], "int",
    """
`nums` is an ascending array of unique values, possibly rotated. Return the index
of `target`, or `-1`. Use `O(log n)` time.

**Example:** `nums = [4,5,6,7,0,1,2]`, `target = 0` → `4`.

**Constraints:** `1 <= len(nums) <= 5000`, unique values.
""",
    """def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
""",
    visible=[{"nums": [4, 5, 6, 7, 0, 1, 2], "target": 0},
             {"nums": [4, 5, 6, 7, 0, 1, 2], "target": 3}, {"nums": [1], "target": 0}],
    hidden=[{"nums": [1], "target": 1}, {"nums": [5, 1, 3], "target": 5}],
    gen=lambda r: [(lambda a: {"nums": a, "target": r.choice(a + [999])})
                   (rotate(sorted_unique(r, r.randint(1, 12)), r.randint(0, 11)))
                   for _ in range(5)],
    brute=lambda nums, target: nums.index(target) if target in nums else -1,
    checks=[({"nums": [4, 5, 6, 7, 0, 1, 2], "target": 0}, 4),
            ({"nums": [4, 5, 6, 7, 0, 1, 2], "target": 3}, -1)], source="file")

add("pacific-atlantic-water-flow", "Pacific Atlantic Water Flow", "medium",
    ["graph", "depth-first-search", "matrix"], "pacificAtlantic",
    [("heights", "int[][]")], "int[][]",
    """
On an `m x n` grid of heights, the Pacific touches the top/left edges and the
Atlantic the bottom/right. Water flows to an equal-or-lower neighbour (N/S/E/W).
Return all cells `[r, c]` from which water can reach **both** oceans, in **any
order** (each cell stays as `[row, col]`).

**Constraints:** `1 <= m, n <= 200`, `0 <= heights[r][c] <= 10^5`.
""",
    """def pacificAtlantic(heights):
    if not heights or not heights[0]:
        return []
    m, n = len(heights), len(heights[0])
    pac = [[False] * n for _ in range(m)]
    atl = [[False] * n for _ in range(m)]
    def dfs(r, c, vis, prev):
        if r < 0 or c < 0 or r >= m or c >= n or vis[r][c] or heights[r][c] < prev:
            return
        vis[r][c] = True
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            dfs(r + dr, c + dc, vis, heights[r][c])
    for i in range(m):
        dfs(i, 0, pac, heights[i][0])
        dfs(i, n - 1, atl, heights[i][n - 1])
    for j in range(n):
        dfs(0, j, pac, heights[0][j])
        dfs(m - 1, j, atl, heights[m - 1][j])
    res = [[i, j] for i in range(m) for j in range(n) if pac[i][j] and atl[i][j]]
    res.sort()
    return res
""",
    visible=[{"heights": [[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1],
                          [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]}, {"heights": [[1]]}],
    hidden=[{"heights": [[1, 1], [1, 1]]}, {"heights": [[3, 3, 3], [3, 1, 3], [3, 3, 3]]}],
    gen=lambda r: [(lambda m, n: {"heights": [[r.randint(0, 6) for _ in range(n)]
                                              for _ in range(m)]})(
                       r.randint(1, 4), r.randint(1, 4)) for _ in range(3)],
    checks=[({"heights": [[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], [2, 4, 5, 3, 1],
                          [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]},
             [[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]),
            ({"heights": [[1]]}, [[0, 0]])], source="file")

add("combination-sum", "Combination Sum", "medium", ["backtracking", "array"],
    "combinationSum", [("candidates", "int[]"), ("target", "int")], "int[][]",
    """
Given distinct positive integers `candidates` and a `target`, return all unique
combinations summing to `target` (a number may be reused). The combinations — and
the numbers within each combination — may be in **any order**.

**Example:** `candidates = [2,3,6,7]`, `target = 7` → `[[2,2,3],[7]]` (any order accepted).

**Constraints:** `1 <= len(candidates) <= 30`, `2 <= candidates[i] <= 40`, `1 <= target <= 40`.
""",
    """def combinationSum(candidates, target):
    candidates = sorted(candidates)
    res = []
    def bt(start, remain, path):
        if remain == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remain:
                break
            path.append(c)
            bt(i, remain - c, path)
            path.pop()
    bt(0, target, [])
    res.sort()
    return res
""",
    visible=[{"candidates": [2, 3, 6, 7], "target": 7},
             {"candidates": [2, 3, 5], "target": 8}, {"candidates": [2], "target": 1}],
    hidden=[{"candidates": [3, 5], "target": 8}, {"candidates": [2, 4], "target": 6}],
    gen=lambda r: [(lambda cs: {"candidates": cs, "target": r.randint(3, 12)})
                   (sorted(r.sample(range(2, 9), r.randint(1, 4)))) for _ in range(4)],
    checks=[({"candidates": [2, 3, 6, 7], "target": 7}, [[2, 2, 3], [7]]),
            ({"candidates": [2, 3, 5], "target": 8}, [[2, 2, 2, 2], [2, 3, 3], [3, 5]]),
            ({"candidates": [2], "target": 1}, [])], source="file")


# ===========================================================================
# Additional similar problems (same techniques / difficulty)
# ===========================================================================

add("contains-duplicate", "Contains Duplicate", "easy", ["array", "hash-set"],
    "containsDuplicate", [("nums", "int[]")], "bool",
    """
Return `true` if any value appears at least twice in `nums`, else `false`.

**Example:** `nums = [1,2,3,1]` → `true`.
""",
    """def containsDuplicate(nums):
    return len(set(nums)) != len(nums)
""",
    visible=[{"nums": [1, 2, 3, 1]}, {"nums": [1, 2, 3, 4]},
             {"nums": [1, 1, 1, 3, 3, 4, 3, 2, 4, 2]}],
    hidden=[{"nums": []}, {"nums": [7]}],
    gen=lambda r: [{"nums": ilist(r, 0, 20, 0, 12)} for _ in range(4)],
    brute=lambda nums: any(nums[i] == nums[j] for i in range(len(nums))
                          for j in range(i + 1, len(nums))),
    checks=[({"nums": [1, 2, 3, 1]}, True), ({"nums": [1, 2, 3, 4]}, False)])

add("valid-anagram", "Valid Anagram", "easy", ["string", "hash-table", "sorting"],
    "isAnagram", [("s", "string"), ("t", "string")], "bool",
    """
Return `true` if `t` is an anagram of `s` (same letters, same counts).

**Example:** `s = "anagram"`, `t = "nagaram"` → `true`.
""",
    """def isAnagram(s, t):
    from collections import Counter
    return Counter(s) == Counter(t)
""",
    visible=[{"s": "anagram", "t": "nagaram"}, {"s": "rat", "t": "car"}],
    hidden=[{"s": "", "t": ""}, {"s": "a", "t": "ab"}, {"s": "ab", "t": "ba"}],
    gen=lambda r: [{"s": sstr(r, 0, 8, "abc"), "t": sstr(r, 0, 8, "abc")} for _ in range(4)],
    brute=lambda s, t: sorted(s) == sorted(t),
    checks=[({"s": "anagram", "t": "nagaram"}, True), ({"s": "rat", "t": "car"}, False)])

add("group-anagrams", "Group Anagrams", "medium", ["string", "hash-table", "sorting"],
    "groupAnagrams", [("strs", "string[]")], "string[][]",
    """
Group the words that are anagrams of one another. The groups — and the words
within each group — may be in **any order**.

**Example:** `strs = ["eat","tea","ate","bat"]` → `[["ate","eat","tea"],["bat"]]` (any order accepted).
""",
    """def groupAnagrams(strs):
    from collections import defaultdict
    groups = defaultdict(list)
    for w in strs:
        groups[''.join(sorted(w))].append(w)
    res = [sorted(v) for v in groups.values()]
    res.sort()
    return res
""",
    visible=[{"strs": ["eat", "tea", "ate", "bat"]}, {"strs": [""]}, {"strs": ["a"]}],
    hidden=[{"strs": ["abc", "bca", "cab", "xyz"]}, {"strs": ["ab", "ba", "abc"]}],
    gen=lambda r: [{"strs": [sstr(r, 1, 4, "abc") for _ in range(r.randint(1, 6))]}
                   for _ in range(4)],
    checks=[({"strs": ["eat", "tea", "ate", "bat"]}, [["ate", "eat", "tea"], ["bat"]]),
            ({"strs": ["a"]}, [["a"]])])

add("top-k-frequent-elements", "Top K Frequent Elements", "medium",
    ["array", "hash-table", "heap"], "topKFrequent",
    [("nums", "int[]"), ("k", "int")], "int[]",
    """
Return the `k` most frequent values in `nums`, in **any order**. If two values
are tied in frequency at the cutoff, prefer the smaller value (so the set of `k`
values is unique).

**Example:** `nums = [1,1,1,2,2,3]`, `k = 2` → `[1,2]` (any order accepted).
""",
    """def topKFrequent(nums, k):
    from collections import Counter
    c = Counter(nums)
    order = sorted(c.keys(), key=lambda v: (-c[v], v))
    return sorted(order[:k])
""",
    visible=[{"nums": [1, 1, 1, 2, 2, 3], "k": 2}, {"nums": [1], "k": 1}],
    hidden=[{"nums": [4, 4, 5, 5, 6], "k": 1}, {"nums": [3, 0, 1, 0], "k": 2}],
    gen=lambda r: [(lambda a: {"nums": a, "k": r.randint(1, max(1, len(set(a))))})
                   (ilist(r, 1, 20, 0, 6)) for _ in range(4)],
    checks=[({"nums": [1, 1, 1, 2, 2, 3], "k": 2}, [1, 2]), ({"nums": [1], "k": 1}, [1])])

add("product-except-self", "Product of Array Except Self", "medium",
    ["array", "prefix-sum"], "productExceptSelf", [("nums", "int[]")], "int[]",
    """
Return an array `out` where `out[i]` is the product of all elements except
`nums[i]` (no division needed).

**Example:** `nums = [1,2,3,4]` → `[24,12,8,6]`.
""",
    """def productExceptSelf(nums):
    n = len(nums)
    res = [1] * n
    pre = 1
    for i in range(n):
        res[i] = pre
        pre *= nums[i]
    suf = 1
    for i in range(n - 1, -1, -1):
        res[i] *= suf
        suf *= nums[i]
    return res
""",
    visible=[{"nums": [1, 2, 3, 4]}, {"nums": [-1, 1, 0, -3, 3]}],
    hidden=[{"nums": [2, 3]}, {"nums": [0, 0]}, {"nums": [5, 1, 1]}],
    gen=lambda r: [{"nums": ilist(r, 2, 8, -4, 4)} for _ in range(4)],
    brute=lambda nums: [__import__("math").prod(nums[:i] + nums[i + 1:]) for i in range(len(nums))],
    checks=[({"nums": [1, 2, 3, 4]}, [24, 12, 8, 6]),
            ({"nums": [-1, 1, 0, -3, 3]}, [0, 0, 9, 0, 0])])

add("best-time-buy-sell-stock", "Best Time to Buy and Sell Stock", "easy",
    ["array", "dynamic-programming"], "maxProfit", [("prices", "int[]")], "int",
    """
`prices[i]` is a stock price on day `i`. Buy once and sell later for the maximum
profit; return that profit (or `0` if impossible).

**Example:** `prices = [7,1,5,3,6,4]` → `5`.
""",
    """def maxProfit(prices):
    best = 0
    lo = float('inf')
    for p in prices:
        lo = min(lo, p)
        best = max(best, p - lo)
    return best
""",
    visible=[{"prices": [7, 1, 5, 3, 6, 4]}, {"prices": [7, 6, 4, 3, 1]}],
    hidden=[{"prices": []}, {"prices": [1]}, {"prices": [2, 4, 1]}],
    gen=lambda r: [{"prices": ilist(r, 0, 20, 0, 30)} for _ in range(4)],
    brute=lambda prices: max([0] + [prices[j] - prices[i] for i in range(len(prices))
                                    for j in range(i + 1, len(prices))]),
    checks=[({"prices": [7, 1, 5, 3, 6, 4]}, 5), ({"prices": [7, 6, 4, 3, 1]}, 0)])

add("valid-palindrome", "Valid Palindrome", "easy", ["string", "two-pointers"],
    "isPalindrome", [("s", "string")], "bool",
    """
Return `true` if `s` reads the same forwards and backwards, considering only
alphanumeric characters and ignoring case.

**Example:** `s = "A man, a plan, a canal: Panama"` → `true`.
""",
    """def isPalindrome(s):
    t = [c.lower() for c in s if c.isalnum()]
    return t == t[::-1]
""",
    visible=[{"s": "A man, a plan, a canal: Panama"}, {"s": "race a car"}, {"s": " "}],
    hidden=[{"s": ""}, {"s": "0P"}, {"s": "ab_a"}],
    gen=lambda r: [{"s": sstr(r, 0, 10, "abAB ,1")} for _ in range(4)],
    checks=[({"s": "A man, a plan, a canal: Panama"}, True),
            ({"s": "race a car"}, False), ({"s": " "}, True)])

add("three-sum", "3Sum", "medium", ["array", "two-pointers", "sorting"],
    "threeSum", [("nums", "int[]")], "int[][]",
    """
Return all unique triplets `[a, b, c]` from `nums` with `a + b + c == 0`. The
triplets — and the values within each triplet — may be in **any order**.

**Example:** `nums = [-1,0,1,2,-1,-4]` → `[[-1,-1,2],[-1,0,1]]` (any order accepted).
""",
    """def threeSum(nums):
    nums = sorted(nums)
    n = len(nums)
    res = []
    for i in range(n):
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            total = nums[i] + nums[l] + nums[r]
            if total < 0:
                l += 1
            elif total > 0:
                r -= 1
            else:
                res.append([nums[i], nums[l], nums[r]])
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:
                    l += 1
                while l < r and nums[r] == nums[r + 1]:
                    r -= 1
    return res
""",
    visible=[{"nums": [-1, 0, 1, 2, -1, -4]}, {"nums": [0, 1, 1]}, {"nums": [0, 0, 0]}],
    hidden=[{"nums": []}, {"nums": [-2, 0, 1, 1, 2]}],
    gen=lambda r: [{"nums": ilist(r, 0, 9, -4, 4)} for _ in range(5)],
    brute=lambda nums: sorted([list(t) for t in {tuple(sorted((nums[i], nums[j], nums[k])))
                              for i in range(len(nums)) for j in range(i + 1, len(nums))
                              for k in range(j + 1, len(nums))
                              if nums[i] + nums[j] + nums[k] == 0}]),
    checks=[({"nums": [-1, 0, 1, 2, -1, -4]}, [[-1, -1, 2], [-1, 0, 1]]),
            ({"nums": [0, 0, 0]}, [[0, 0, 0]])])

add("binary-search", "Binary Search", "easy", ["array", "binary-search"],
    "search", [("nums", "int[]"), ("target", "int")], "int",
    """
Given an ascending array `nums` of unique values and a `target`, return its index
or `-1`. Use `O(log n)` time.

**Example:** `nums = [-1,0,3,5,9,12]`, `target = 9` → `4`.
""",
    """def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
""",
    visible=[{"nums": [-1, 0, 3, 5, 9, 12], "target": 9},
             {"nums": [-1, 0, 3, 5, 9, 12], "target": 2}],
    hidden=[{"nums": [5], "target": 5}, {"nums": [5], "target": -5}, {"nums": [], "target": 1}],
    gen=lambda r: [(lambda a: {"nums": a, "target": r.choice(a + [777])})
                   (sorted_unique(r, r.randint(1, 14))) for _ in range(5)],
    brute=lambda nums, target: nums.index(target) if target in nums else -1,
    checks=[({"nums": [-1, 0, 3, 5, 9, 12], "target": 9}, 4),
            ({"nums": [-1, 0, 3, 5, 9, 12], "target": 2}, -1)])

add("climbing-stairs", "Climbing Stairs", "easy", ["dynamic-programming", "math"],
    "climbStairs", [("n", "int")], "int",
    """
You climb 1 or 2 steps at a time. Return the number of distinct ways to reach the
top of `n` steps.

**Example:** `n = 3` → `3` (1+1+1, 1+2, 2+1).
""",
    """def climbStairs(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a
""",
    visible=[{"n": 2}, {"n": 3}],
    hidden=[{"n": 1}, {"n": 5}, {"n": 10}],
    gen=lambda r: [{"n": r.randint(1, 25)} for _ in range(4)],
    checks=[({"n": 2}, 2), ({"n": 3}, 3), ({"n": 1}, 1), ({"n": 5}, 8)])

add("coin-change", "Coin Change", "medium", ["dynamic-programming", "array"],
    "coinChange", [("coins", "int[]"), ("amount", "int")], "int",
    """
Given coin denominations `coins` and an `amount`, return the fewest coins needed
to make `amount`, or `-1` if impossible. Each coin may be reused.

**Example:** `coins = [1,2,5]`, `amount = 11` → `3` (5+5+1).
""",
    """def coinChange(coins, amount):
    INF = float('inf')
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1
""",
    visible=[{"coins": [1, 2, 5], "amount": 11}, {"coins": [2], "amount": 3},
             {"coins": [1], "amount": 0}],
    hidden=[{"coins": [2, 5], "amount": 7}, {"coins": [3, 7], "amount": 5}],
    gen=lambda r: [{"coins": sorted(r.sample(range(1, 9), r.randint(1, 4))),
                    "amount": r.randint(0, 20)} for _ in range(4)],
    checks=[({"coins": [1, 2, 5], "amount": 11}, 3), ({"coins": [2], "amount": 3}, -1),
            ({"coins": [1], "amount": 0}, 0)])

add("house-robber", "House Robber", "medium", ["dynamic-programming", "array"],
    "rob", [("nums", "int[]")], "int",
    """
Houses in a row hold `nums[i]` money; you can't rob two adjacent houses. Return
the maximum you can rob.

**Example:** `nums = [2,7,9,3,1]` → `12` (rob houses 0, 2, 4).
""",
    """def rob(nums):
    prev = cur = 0
    for x in nums:
        prev, cur = cur, max(cur, prev + x)
    return cur
""",
    visible=[{"nums": [1, 2, 3, 1]}, {"nums": [2, 7, 9, 3, 1]}],
    hidden=[{"nums": []}, {"nums": [5]}, {"nums": [2, 1, 1, 2]}],
    gen=lambda r: [{"nums": ilist(r, 0, 12, 0, 20)} for _ in range(4)],
    brute=lambda nums: (lambda f: f(f, 0))(
        lambda f, i: 0 if i >= len(nums) else max(f(f, i + 1), nums[i] + f(f, i + 2))),
    checks=[({"nums": [1, 2, 3, 1]}, 4), ({"nums": [2, 7, 9, 3, 1]}, 12)])

add("maximum-subarray", "Maximum Subarray", "medium",
    ["array", "dynamic-programming", "divide-and-conquer"], "maxSubArray",
    [("nums", "int[]")], "int",
    """
Return the largest sum of any contiguous subarray of `nums` (Kadane's algorithm).

**Example:** `nums = [-2,1,-3,4,-1,2,1,-5,4]` → `6` (subarray `[4,-1,2,1]`).
""",
    """def maxSubArray(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
""",
    visible=[{"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, {"nums": [1]}, {"nums": [5, 4, -1, 7, 8]}],
    hidden=[{"nums": [-1]}, {"nums": [-2, -1]}, {"nums": [3, -2, 5, -1]}],
    gen=lambda r: [{"nums": ilist(r, 1, 12, -6, 6)} for _ in range(5)],
    brute=lambda nums: max(sum(nums[i:j]) for i in range(len(nums))
                          for j in range(i + 1, len(nums) + 1)),
    checks=[({"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, 6), ({"nums": [5, 4, -1, 7, 8]}, 23)])


# ===========================================================================
# Imported from problemset2.txt — plain-text formatting cleaned (collapsed
# exponents -> 10^k / 2^31), figures regenerated as SVG. See docs/problem-images.md.
# ===========================================================================

# -- gen / brute helpers for this batch -------------------------------------
def _rand_square(r):
    n = r.randint(1, 6)
    return [[r.randint(-50, 50) for _ in range(n)] for _ in range(n)]


def _rand_matrix(r):
    m, n = r.randint(1, 10), r.randint(1, 10)
    return [[r.randint(-100, 100) for _ in range(n)] for _ in range(m)]


def _rand_intervals(r, n_lo, n_hi):
    out = []
    for _ in range(r.randint(n_lo, n_hi)):
        a = r.randint(0, 12)
        out.append([a, a + r.randint(1, 5)])
    return out


def _rand_sorted_disjoint(r):
    """Non-overlapping intervals sorted by start (the Insert-Interval precondition)."""
    out, x = [], r.randint(0, 3)
    for _ in range(r.randint(0, 6)):
        s = x + r.randint(1, 3)
        e = s + r.randint(0, 3)
        out.append([s, e])
        x = e + r.randint(1, 3)
    return out


def _rand_interval(r):
    a = r.randint(0, 18)
    return [a, a + r.randint(0, 6)]


def _rand_tree(r):
    arr = [r.randint(0, 4)]
    for _ in range(r.randint(0, 6)):
        arr.append(r.choice([None, r.randint(0, 4)]))
    return arr


def _b_char_replace(s, k):
    n, best = len(s), 0
    for i in range(n):
        freq, most = {}, 0
        for j in range(i, n):
            freq[s[j]] = freq.get(s[j], 0) + 1
            most = max(most, freq[s[j]])
            if (j - i + 1) - most <= k:
                best = max(best, j - i + 1)
    return best


def _b_lis(nums):
    if not nums:
        return 0
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


def _b_erase(intervals):
    if not intervals:
        return 0
    iv = sorted(intervals)
    n = len(iv)
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            if iv[j][1] <= iv[i][0]:
                dp[i] = max(dp[i], dp[j] + 1)
    return n - max(dp)


def _b_spiral(matrix):
    if not matrix or not matrix[0]:
        return []
    m, n = len(matrix), len(matrix[0])
    seen = [[False] * n for _ in range(m)]
    dr, dc = [0, 1, 0, -1], [1, 0, -1, 0]
    r = c = d = 0
    res = []
    for _ in range(m * n):
        res.append(matrix[r][c])
        seen[r][c] = True
        nr, nc = r + dr[d], c + dc[d]
        if not (0 <= nr < m and 0 <= nc < n and not seen[nr][nc]):
            d = (d + 1) % 4
            nr, nc = r + dr[d], c + dc[d]
        r, c = nr, nc
    return res


def _b_jump(nums):
    n = len(nums)
    dp = [False] * n
    dp[-1] = True
    for i in range(n - 2, -1, -1):
        for j in range(1, nums[i] + 1):
            if i + j < n and dp[i + j]:
                dp[i] = True
                break
    return dp[0]


def _b_merge(intervals):
    iv = [list(x) for x in intervals]
    changed = True
    while changed:
        changed = False
        out = []
        for cur in iv:
            placed = False
            for o in out:
                if cur[0] <= o[1] and o[0] <= cur[1]:
                    o[0], o[1] = min(o[0], cur[0]), max(o[1], cur[1])
                    placed = changed = True
                    break
            if not placed:
                out.append(cur)
        iv = out
    return sorted(iv)


def _b_insert(intervals, newInterval):
    iv = sorted([list(x) for x in intervals] + [list(newInterval)])
    res = []
    for s, e in iv:
        if res and s <= res[-1][1]:
            res[-1][1] = max(res[-1][1], e)
        else:
            res.append([s, e])
    return res


def _b_subtree(root, subRoot):
    from collections import deque

    def build(arr):
        if not arr or arr[0] is None:
            return None
        node = {"v": arr[0], "l": None, "r": None}
        q, i = deque([node]), 1
        while q and i < len(arr):
            cur = q.popleft()
            for side in ("l", "r"):
                if i < len(arr):
                    v = arr[i]
                    i += 1
                    if v is not None:
                        cur[side] = {"v": v, "l": None, "r": None}
                        q.append(cur[side])
        return node

    def ser(n):
        if n is None:
            return "#"
        return "^{}({})({})".format(n["v"], ser(n["l"]), ser(n["r"]))

    return ser(build(subRoot)) in ser(build(root))


def _b_unique(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[-1]


add("longest-repeating-character-replacement", "Longest Repeating Character Replacement",
    "medium", ["string", "sliding-window"], "characterReplacement",
    [("s", "string"), ("k", "int")], "int",
    """
You are given a string `s` of uppercase English letters and an integer `k`. You may
pick **at most `k`** positions in `s` and replace each with any uppercase letter.

Return **the length of the longest substring made of a single repeated letter** you
can obtain after performing at most `k` replacements.

## Constraints
- `1 <= len(s) <= 10^5`
- `s` consists of uppercase English letters only.
- `0 <= k <= len(s)`

## Examples
Input: `s = "ABAB", k = 2`
Output: `4`
Explanation: Replace the two `A`s with `B`s (or vice versa) to get `"BBBB"`.

Input: `s = "AABABBA", k = 1`
Output: `4`
Explanation: Replace the middle `A` with `B` to get `"AABBBBA"`; the run `"BBBB"` has length 4.
""",
    """def characterReplacement(s, k):
    from collections import Counter
    count = Counter()
    left = 0
    most = 0
    best = 0
    for right, ch in enumerate(s):
        count[ch] += 1
        most = max(most, count[ch])
        while (right - left + 1) - most > k:
            count[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
""",
    visible=[{"s": "ABAB", "k": 2}, {"s": "AABABBA", "k": 1}],
    hidden=[{"s": "A", "k": 0}, {"s": "AAAA", "k": 0}, {"s": "ABCDE", "k": 0},
            {"s": "AABA", "k": 0}, {"s": "AB" * 400, "k": 3}],
    gen=lambda r: [{"s": sstr(r, 1, 40, "ABCD"), "k": r.randint(0, 5)} for _ in range(5)],
    brute=_b_char_replace,
    checks=[({"s": "ABAB", "k": 2}, 4), ({"s": "AABABBA", "k": 1}, 4)])

add("longest-increasing-subsequence", "Longest Increasing Subsequence", "medium",
    ["array", "dynamic-programming", "binary-search"], "lengthOfLIS",
    [("nums", "int[]")], "int",
    """
Given an integer array `nums`, return **the length of the longest strictly
increasing subsequence**. A subsequence keeps the original order but may drop
elements.

## Constraints
- `1 <= len(nums) <= 2500`
- `-10^4 <= nums[i] <= 10^4`

## Examples
Input: `nums = [10,9,2,5,3,7,101,18]`
Output: `4`
Explanation: One longest increasing subsequence is `[2,3,7,101]`.

Input: `nums = [0,1,0,3,2,3]`
Output: `4`

Input: `nums = [7,7,7,7,7,7,7]`
Output: `1`
Explanation: No two equal values form a *strictly* increasing pair.
""",
    """def lengthOfLIS(nums):
    import bisect
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
""",
    visible=[{"nums": [10, 9, 2, 5, 3, 7, 101, 18]}, {"nums": [0, 1, 0, 3, 2, 3]},
             {"nums": [7, 7, 7, 7, 7, 7, 7]}],
    hidden=[{"nums": [1]}, {"nums": [1, 2, 3, 4, 5]}, {"nums": [5, 4, 3, 2, 1]},
            {"nums": [-2, -1, -3, 0, -1, 2]}, {"nums": [i % 50 for i in range(1500)]}],
    gen=lambda r: [{"nums": ilist(r, 1, 40, -15, 15)} for _ in range(5)],
    brute=_b_lis,
    checks=[({"nums": [10, 9, 2, 5, 3, 7, 101, 18]}, 4),
            ({"nums": [0, 1, 0, 3, 2, 3]}, 4), ({"nums": [7, 7, 7, 7, 7, 7, 7]}, 1)])

add("rotate-image", "Rotate Image", "medium", ["array", "matrix", "math"], "rotate",
    [("matrix", "int[][]")], "int[][]",
    """
You are given an `n x n` 2D `matrix` representing an image. **Rotate the matrix 90
degrees clockwise, in place, and return it.** Modify the input directly — do not
allocate a second `n x n` matrix.

![Example 1: rotate the 3x3 matrix 90 degrees clockwise](/problems/rotate-image/assets/example-1.svg)

## Constraints
- `n == len(matrix) == len(matrix[i])`
- `1 <= n <= 20`
- `-1000 <= matrix[i][j] <= 1000`

## Examples
Input: `matrix = [[1,2,3],[4,5,6],[7,8,9]]`
Output: `[[7,4,1],[8,5,2],[9,6,3]]`

![Example 2: rotate the 4x4 matrix 90 degrees clockwise](/problems/rotate-image/assets/example-2.svg)

Input: `matrix = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]`
Output: `[[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]`
""",
    """def rotate(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()
    return matrix
""",
    visible=[{"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]},
             {"matrix": [[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]]}],
    hidden=[{"matrix": [[1]]}, {"matrix": [[1, 2], [3, 4]]},
            {"matrix": [[-1, -2, -3], [-4, -5, -6], [-7, -8, -9]]},
            {"matrix": [[r * 10 + c for c in range(10)] for r in range(10)]}],
    gen=lambda r: [{"matrix": _rand_square(r)} for _ in range(4)],
    brute=lambda matrix: [[matrix[len(matrix) - 1 - j][i] for j in range(len(matrix))]
                          for i in range(len(matrix))],
    checks=[({"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]},
             [[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
            ({"matrix": [[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]]},
             [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]])],
    assets={
        "example-1.svg": figures.rotate_image_svg(
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
        "example-2.svg": figures.rotate_image_svg(
            [[5, 1, 9, 11], [2, 4, 8, 10], [13, 3, 6, 7], [15, 14, 12, 16]],
            [[15, 13, 2, 5], [14, 3, 4, 1], [12, 6, 8, 9], [16, 7, 10, 11]])})

add("non-overlapping-intervals", "Non-overlapping Intervals", "medium",
    ["array", "greedy", "sorting"], "eraseOverlapIntervals", [("intervals", "int[][]")],
    "int",
    """
Given an array `intervals` where `intervals[i] = [start_i, end_i]`, return **the
minimum number of intervals to remove** so that the rest are non-overlapping.

Intervals that only touch at a point are non-overlapping — e.g. `[1,2]` and `[2,3]`.

## Constraints
- `1 <= len(intervals) <= 10^5`
- `intervals[i].length == 2`
- `-5 * 10^4 <= start_i < end_i <= 5 * 10^4`

## Examples
Input: `intervals = [[1,2],[2,3],[3,4],[1,3]]`
Output: `1`
Explanation: Remove `[1,3]` and the rest are non-overlapping.

Input: `intervals = [[1,2],[1,2],[1,2]]`
Output: `2`
Explanation: Remove two copies of `[1,2]`.

Input: `intervals = [[1,2],[2,3]]`
Output: `0`
""",
    """def eraseOverlapIntervals(intervals):
    intervals.sort(key=lambda x: x[1])
    removed = 0
    prev_end = float("-inf")
    for s, e in intervals:
        if s >= prev_end:
            prev_end = e
        else:
            removed += 1
    return removed
""",
    visible=[{"intervals": [[1, 2], [2, 3], [3, 4], [1, 3]]},
             {"intervals": [[1, 2], [1, 2], [1, 2]]}, {"intervals": [[1, 2], [2, 3]]}],
    hidden=[{"intervals": [[1, 2]]},
            {"intervals": [[1, 100], [11, 22], [1, 11], [2, 12]]},
            {"intervals": [[-5, -2], [-3, 0], [0, 3]]},
            {"intervals": [[i, i + 10] for i in range(120)]}],
    gen=lambda r: [{"intervals": _rand_intervals(r, 0, 6)} for _ in range(5)],
    brute=_b_erase,
    checks=[({"intervals": [[1, 2], [2, 3], [3, 4], [1, 3]]}, 1),
            ({"intervals": [[1, 2], [1, 2], [1, 2]]}, 2),
            ({"intervals": [[1, 2], [2, 3]]}, 0)])

add("spiral-matrix", "Spiral Matrix", "medium", ["array", "matrix", "simulation"],
    "spiralOrder", [("matrix", "int[][]")], "int[]",
    """
Given an `m x n` `matrix`, return **all of its elements in spiral order** — starting
at the top-left and winding clockwise inward.

![Example 1: spiral traversal of a 3x3 matrix](/problems/spiral-matrix/assets/example-1.svg)

## Constraints
- `m == len(matrix)`, `n == len(matrix[i])`
- `1 <= m, n <= 10`
- `-100 <= matrix[i][j] <= 100`

## Examples
Input: `matrix = [[1,2,3],[4,5,6],[7,8,9]]`
Output: `[1,2,3,6,9,8,7,4,5]`

![Example 2: spiral traversal of a 3x4 matrix](/problems/spiral-matrix/assets/example-2.svg)

Input: `matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]`
Output: `[1,2,3,4,8,12,11,10,9,5,6,7]`
""",
    """def spiralOrder(matrix):
    res = []
    if not matrix or not matrix[0]:
        return res
    top, bot = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bot and left <= right:
        for c in range(left, right + 1):
            res.append(matrix[top][c])
        top += 1
        for r in range(top, bot + 1):
            res.append(matrix[r][right])
        right -= 1
        if top <= bot:
            for c in range(right, left - 1, -1):
                res.append(matrix[bot][c])
            bot -= 1
        if left <= right:
            for r in range(bot, top - 1, -1):
                res.append(matrix[r][left])
            left += 1
    return res
""",
    visible=[{"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]},
             {"matrix": [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]}],
    hidden=[{"matrix": [[7]]}, {"matrix": [[1, 2, 3]]}, {"matrix": [[1], [2], [3]]},
            {"matrix": [[1, 2], [3, 4]]},
            {"matrix": [[r * 10 + c for c in range(10)] for r in range(10)]}],
    gen=lambda r: [{"matrix": _rand_matrix(r)} for _ in range(4)],
    brute=_b_spiral,
    checks=[({"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]},
             [1, 2, 3, 6, 9, 8, 7, 4, 5]),
            ({"matrix": [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]},
             [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7])],
    assets={
        "example-1.svg": figures.spiral_matrix_svg([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
        "example-2.svg": figures.spiral_matrix_svg(
            [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])})

add("jump-game", "Jump Game", "medium", ["array", "greedy", "dynamic-programming"],
    "canJump", [("nums", "int[]")], "bool",
    """
You start at index `0` of an integer array `nums`; `nums[i]` is the maximum jump
length from index `i`. Return **`true` if you can reach the last index**, otherwise
`false`.

## Constraints
- `1 <= len(nums) <= 10^4`
- `0 <= nums[i] <= 10^5`

## Examples
Input: `nums = [2,3,1,1,4]`
Output: `true`
Explanation: Jump 1 step to index 1, then 3 steps to the last index.

Input: `nums = [3,2,1,0,4]`
Output: `false`
Explanation: You always land on index 3 (value 0) and can move no further.
""",
    """def canJump(nums):
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + x)
    return True
""",
    visible=[{"nums": [2, 3, 1, 1, 4]}, {"nums": [3, 2, 1, 0, 4]}],
    hidden=[{"nums": [0]}, {"nums": [1, 0]}, {"nums": [2, 0, 0]}, {"nums": [0, 1]},
            {"nums": [1] * 500 + [0] + [1] * 500}],
    gen=lambda r: [{"nums": [r.randint(0, 4) for _ in range(r.randint(1, 12))]}
                   for _ in range(5)],
    brute=_b_jump,
    checks=[({"nums": [2, 3, 1, 1, 4]}, True), ({"nums": [3, 2, 1, 0, 4]}, False)])

add("merge-intervals", "Merge Intervals", "medium", ["array", "sorting"], "merge",
    [("intervals", "int[][]")], "int[][]",
    """
Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all
overlapping intervals and return **the merged intervals sorted by start**. Intervals
that touch at an endpoint (e.g. `[1,4]` and `[4,5]`) are considered overlapping.

## Constraints
- `1 <= len(intervals) <= 10^4`
- `intervals[i].length == 2`
- `0 <= start_i <= end_i <= 10^4`

## Examples
Input: `intervals = [[1,3],[2,6],[8,10],[15,18]]`
Output: `[[1,6],[8,10],[15,18]]`
Explanation: `[1,3]` and `[2,6]` overlap, so they merge into `[1,6]`.

Input: `intervals = [[1,4],[4,5]]`
Output: `[[1,5]]`

Input: `intervals = [[4,7],[1,4]]`
Output: `[[1,7]]`
""",
    """def merge(intervals):
    intervals.sort(key=lambda x: x[0])
    res = []
    for s, e in intervals:
        if res and s <= res[-1][1]:
            res[-1][1] = max(res[-1][1], e)
        else:
            res.append([s, e])
    return res
""",
    visible=[{"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]},
             {"intervals": [[1, 4], [4, 5]]}, {"intervals": [[4, 7], [1, 4]]}],
    hidden=[{"intervals": [[1, 4]]}, {"intervals": [[1, 2], [3, 4]]},
            {"intervals": [[1, 4], [2, 3]]}, {"intervals": [[1, 4], [0, 4]]},
            {"intervals": [[i, i + 5] for i in range(120)]}],
    gen=lambda r: [{"intervals": _rand_intervals(r, 1, 8)} for _ in range(5)],
    brute=_b_merge,
    checks=[({"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]},
             [[1, 6], [8, 10], [15, 18]]),
            ({"intervals": [[1, 4], [4, 5]]}, [[1, 5]]),
            ({"intervals": [[4, 7], [1, 4]]}, [[1, 7]])])

add("insert-interval", "Insert Interval", "medium", ["array"], "insert",
    [("intervals", "int[][]"), ("newInterval", "int[]")], "int[][]",
    """
You are given non-overlapping `intervals` sorted by start, and a `newInterval`.
**Insert `newInterval`, merging as needed, and return the resulting sorted list of
non-overlapping intervals.** You may build and return a new list.

## Constraints
- `0 <= len(intervals) <= 10^4`
- `intervals[i].length == 2`, `newInterval.length == 2`
- `0 <= start_i <= end_i <= 10^5` and `0 <= start <= end <= 10^5`
- `intervals` is sorted by start in ascending order.

## Examples
Input: `intervals = [[1,3],[6,9]], newInterval = [2,5]`
Output: `[[1,5],[6,9]]`

Input: `intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]`
Output: `[[1,2],[3,10],[12,16]]`
Explanation: `[4,8]` overlaps `[3,5]`, `[6,7]`, and `[8,10]`.
""",
    """def insert(intervals, newInterval):
    res = []
    i, n = 0, len(intervals)
    s, e = newInterval
    while i < n and intervals[i][1] < s:
        res.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= e:
        s = min(s, intervals[i][0])
        e = max(e, intervals[i][1])
        i += 1
    res.append([s, e])
    while i < n:
        res.append(intervals[i])
        i += 1
    return res
""",
    visible=[{"intervals": [[1, 3], [6, 9]], "newInterval": [2, 5]},
             {"intervals": [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]],
              "newInterval": [4, 8]}],
    hidden=[{"intervals": [], "newInterval": [5, 7]},
            {"intervals": [[1, 5]], "newInterval": [2, 3]},
            {"intervals": [[1, 5]], "newInterval": [6, 8]},
            {"intervals": [[3, 5], [7, 9]], "newInterval": [0, 1]},
            {"intervals": [[i, i + 1] for i in range(0, 2000, 2)], "newInterval": [3, 7]}],
    gen=lambda r: [{"intervals": _rand_sorted_disjoint(r), "newInterval": _rand_interval(r)}
                   for _ in range(5)],
    brute=_b_insert,
    checks=[({"intervals": [[1, 3], [6, 9]], "newInterval": [2, 5]}, [[1, 5], [6, 9]]),
            ({"intervals": [[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]],
              "newInterval": [4, 8]}, [[1, 2], [3, 10], [12, 16]])])

add("subtree-of-another-tree", "Subtree of Another Tree", "easy",
    ["tree", "binary-tree", "depth-first-search"], "isSubtree",
    [("root", "int[]"), ("subRoot", "int[]")], "bool",
    """
The binary trees `root` and `subRoot` are given as level-order arrays, where `null`
marks a missing child (e.g. `[3,4,5,1,2]`). Return **`true` if some subtree of
`root` has exactly the same structure and node values as `subRoot`**, otherwise
`false`. A tree is a subtree of itself.

![Example 1: subRoot [4,1,2] matches a subtree of root [3,4,5,1,2]](/problems/subtree-of-another-tree/assets/example-1.svg)

## Constraints
- The number of nodes in `root` is in `[1, 2000]`; in `subRoot`, `[1, 1000]`.
- `-10^4 <= node value <= 10^4`

## Examples
Input: `root = [3,4,5,1,2], subRoot = [4,1,2]`
Output: `true`

![Example 2: subRoot [4,1,2] does not match — the candidate node 2 has an extra child](/problems/subtree-of-another-tree/assets/example-2.svg)

Input: `root = [3,4,5,1,2,null,null,null,null,0], subRoot = [4,1,2]`
Output: `false`
Explanation: The only `4`-rooted subtree has an extra node `0`, so it is not identical to `subRoot`.
""",
    """def isSubtree(root, subRoot):
    class N:
        __slots__ = ("v", "l", "r")

        def __init__(self, v):
            self.v, self.l, self.r = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        node = N(arr[0])
        q, i = [node], 1
        while q and i < len(arr):
            cur = q.pop(0)
            if i < len(arr):
                v = arr[i]
                i += 1
                if v is not None:
                    cur.l = N(v)
                    q.append(cur.l)
            if i < len(arr):
                v = arr[i]
                i += 1
                if v is not None:
                    cur.r = N(v)
                    q.append(cur.r)
        return node

    def same(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.v == b.v and same(a.l, b.l) and same(a.r, b.r)

    def dfs(node):
        if node is None:
            return False
        if same(node, sub):
            return True
        return dfs(node.l) or dfs(node.r)

    sub = build(subRoot)
    return dfs(build(root))
""",
    visible=[{"root": [3, 4, 5, 1, 2], "subRoot": [4, 1, 2]},
             {"root": [3, 4, 5, 1, 2, None, None, None, None, 0], "subRoot": [4, 1, 2]}],
    hidden=[{"root": [1, 2, 3], "subRoot": [1, 2, 3]},
            {"root": [1, 2, 3], "subRoot": [2]},
            {"root": [1], "subRoot": [2]},
            {"root": [1, 1], "subRoot": [1]},
            {"root": [(i % 5) for i in range(400)], "subRoot": [99]}],
    gen=lambda r: [{"root": _rand_tree(r), "subRoot": _rand_tree(r)} for _ in range(6)],
    brute=_b_subtree,
    checks=[({"root": [3, 4, 5, 1, 2], "subRoot": [4, 1, 2]}, True),
            ({"root": [3, 4, 5, 1, 2, None, None, None, None, 0], "subRoot": [4, 1, 2]},
             False)],
    assets={
        "example-1.svg": figures.tree_pair_svg([3, 4, 5, 1, 2], [4, 1, 2], {4, 1, 2}),
        "example-2.svg": figures.tree_pair_svg(
            [3, 4, 5, 1, 2, None, None, None, None, 0], [4, 1, 2], None)})

add("unique-paths", "Unique Paths", "medium",
    ["math", "dynamic-programming", "combinatorics"], "uniquePaths",
    [("m", "int"), ("n", "int")], "int",
    """
A robot starts at the top-left cell of an `m x n` grid and wants to reach the
bottom-right cell. At each step it may move **only right or down**. Return **the
number of distinct paths**.

![Example 1: a 3x7 grid with the start, finish, and one sample path](/problems/unique-paths/assets/example-1.svg)

## Constraints
- `1 <= m, n <= 100`
- The answer is guaranteed to be at most `2 * 10^9`.

## Examples
Input: `m = 3, n = 7`
Output: `28`

Input: `m = 3, n = 2`
Output: `3`
Explanation: Down-Down-Right, Down-Right-Down, and Right-Down-Down.
""",
    """def uniquePaths(m, n):
    from math import comb
    return comb(m + n - 2, m - 1)
""",
    visible=[{"m": 3, "n": 7}, {"m": 3, "n": 2}],
    # Answers stay within the stated bound (<= 2*10^9); m or n may still be 100
    # since those degenerate rows/cols have answer 1.
    hidden=[{"m": 1, "n": 1}, {"m": 1, "n": 100}, {"m": 100, "n": 1},
            {"m": 3, "n": 3}, {"m": 10, "n": 10}, {"m": 17, "n": 17}],
    gen=lambda r: [{"m": r.randint(1, 16), "n": r.randint(1, 16)} for _ in range(5)],
    brute=_b_unique,
    checks=[({"m": 3, "n": 7}, 28), ({"m": 3, "n": 2}, 3), ({"m": 1, "n": 1}, 1)],
    assets={"example-1.svg": figures.unique_paths_svg(3, 7)})

add("reverse-bits", "Reverse Bits", "easy", ["bit-manipulation", "divide-and-conquer"],
    "reverseBits", [("n", "int")], "int",
    """
Given a 32-bit unsigned integer `n`, **reverse the order of its 32 bits and return
the resulting unsigned integer.**

## Constraints
- `0 <= n <= 2^31 - 1`

## Examples
Input: `n = 43261596`
Output: `964176192`
Explanation: `n` is `00000010100101000001111010011100` in 32-bit binary; reversed it
is `00111001011110000010100101000000`, which is `964176192`.

Input: `n = 2147483644`
Output: `1073741822`
Explanation: `01111111111111111111111111111100` reversed is
`00111111111111111111111111111110`.
""",
    """def reverseBits(n):
    res = 0
    for _ in range(32):
        res = (res << 1) | (n & 1)
        n >>= 1
    return res
""",
    visible=[{"n": 43261596}, {"n": 2147483644}],
    hidden=[{"n": 0}, {"n": 1}, {"n": 2}, {"n": 1073741824}, {"n": 2147483647}],
    gen=lambda r: [{"n": r.randint(0, 2 ** 31 - 1)} for _ in range(5)],
    brute=lambda n: int(format(n & 0xFFFFFFFF, "032b")[::-1], 2),
    checks=[({"n": 43261596}, 964176192), ({"n": 2147483644}, 1073741822)])

add("number-of-1-bits", "Number of 1 Bits", "easy",
    ["bit-manipulation", "divide-and-conquer"], "hammingWeight", [("n", "int")], "int",
    """
Given a positive integer `n`, return **the number of set bits (`1`s) in its binary
representation** — the Hamming weight.

## Constraints
- `1 <= n <= 2^31 - 1`

## Examples
Input: `n = 11`
Output: `3`
Explanation: `11` is `1011` in binary — three set bits.

Input: `n = 128`
Output: `1`
Explanation: `128` is `10000000` in binary — one set bit.

Input: `n = 2147483645`
Output: `30`
""",
    """def hammingWeight(n):
    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
""",
    visible=[{"n": 11}, {"n": 128}, {"n": 2147483645}],
    hidden=[{"n": 1}, {"n": 2}, {"n": 3}, {"n": 1073741824}, {"n": 2147483647}],
    gen=lambda r: [{"n": r.randint(1, 2 ** 31 - 1)} for _ in range(5)],
    brute=lambda n: bin(n & 0xFFFFFFFF).count("1"),
    checks=[({"n": 11}, 3), ({"n": 128}, 1), ({"n": 2147483645}, 30)])


# ===========================================================================
# Problems sourced from problemset3.txt (LeetCode-style; fitted to one function)
# ===========================================================================

# ---- Binary-tree helpers (module-level; used by brute/gen references) -------
class _TN:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val, self.left, self.right = val, None, None


def _build_tree(arr):
    if not arr or arr[0] is None:
        return None
    root = _TN(arr[0])
    q, i = [root], 1
    while q and i < len(arr):
        node = q.pop(0)
        if i < len(arr):
            v = arr[i]; i += 1
            if v is not None:
                node.left = _TN(v); q.append(node.left)
        if i < len(arr):
            v = arr[i]; i += 1
            if v is not None:
                node.right = _TN(v); q.append(node.right)
    return root


def _serialize_tree(root):
    out, q = [], [root]
    while q:
        node = q.pop(0)
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        q.append(node.left)
        q.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def _rand_tree_root(r, n, v_lo=-20, v_hi=20):
    if n <= 0:
        return None
    root = _TN(r.randint(v_lo, v_hi))
    open_slots = [root]
    count = 1
    while count < n and open_slots:
        parent = r.choice(open_slots)
        child = _TN(r.randint(v_lo, v_hi))
        if parent.left is None and parent.right is None:
            if r.random() < 0.5:
                parent.left = child
            else:
                parent.right = child
        elif parent.left is None:
            parent.left = child
        else:
            parent.right = child
        if parent.left is not None and parent.right is not None:
            open_slots.remove(parent)
        open_slots.append(child)
        count += 1
    return root


def _rand_tree_arr(r, n_lo=1, n_hi=12, v_lo=-20, v_hi=20):
    return _serialize_tree(_rand_tree_root(r, r.randint(n_lo, n_hi), v_lo, v_hi))


def _rand_tree_root_from_vals(r, vals):
    root = _rand_tree_root(r, len(vals))
    it = iter(vals)
    q = [root]
    while q:
        node = q.pop(0)
        node.val = next(it)
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
    return root


def _bst_insert(root, v):
    if root is None:
        return _TN(v)
    cur = root
    while True:
        if v < cur.val:
            if cur.left is None:
                cur.left = _TN(v)
                return root
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = _TN(v)
                return root
            cur = cur.right


def _rand_bst(r, n_lo=1, n_hi=12, lo=-40, hi=40):
    n = min(r.randint(n_lo, n_hi), hi - lo)
    vals = r.sample(range(lo, hi), n)
    root = None
    for v in vals:
        root = _bst_insert(root, v)
    return _serialize_tree(root), vals


def _preorder_vals(root):
    if root is None:
        return []
    return [root.val] + _preorder_vals(root.left) + _preorder_vals(root.right)


def _inorder_vals(root):
    if root is None:
        return []
    return _inorder_vals(root.left) + [root.val] + _inorder_vals(root.right)


def _path_to(root, target):
    if root is None:
        return None
    if root.val == target:
        return [root]
    for child in (root.left, root.right):
        p = _path_to(child, target)
        if p:
            return [root] + p
    return None


# ---- Independent brute-force references ------------------------------------
def _b_islands(grid):
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    parent = list(range(rows * cols))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    land = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                land += 1
                for dr, dc in ((1, 0), (0, 1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1":
                        parent[find(r * cols + c)] = find(nr * cols + nc)
    roots = {find(r * cols + c) for r in range(rows) for c in range(cols)
             if grid[r][c] == "1"}
    return len(roots)


def _b_setzero(matrix):
    rows, cols = len(matrix), len(matrix[0])
    res = [[matrix[r][c] for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 0:
                for k in range(cols):
                    res[r][k] = 0
                for k in range(rows):
                    res[k][c] = 0
    return res


def _b_minwindow(s, t):
    from collections import Counter
    need = Counter(t)
    best = ""
    n = len(s)
    for i in range(n):
        cnt = {}
        for j in range(i, n):
            cnt[s[j]] = cnt.get(s[j], 0) + 1
            if all(cnt.get(ch, 0) >= need[ch] for ch in need):
                w = s[i:j + 1]
                if best == "" or len(w) < len(best):
                    best = w
                break
    return best


def _b_word_exist(board, word):
    rows, cols = len(board), len(board[0])

    def dfs(r, c, k, seen):
        if k == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols):
            return False
        if (r, c) in seen or board[r][c] != word[k]:
            return False
        seen.add((r, c))
        found = (dfs(r + 1, c, k + 1, seen) or dfs(r - 1, c, k + 1, seen)
                 or dfs(r, c + 1, k + 1, seen) or dfs(r, c - 1, k + 1, seen))
        seen.discard((r, c))
        return found

    if not word:
        return True
    return any(dfs(r, c, 0, set()) for r in range(rows) for c in range(cols))


def _b_findwords(board, words):
    return [w for w in words if _b_word_exist(board, w)]


def _b_course(numCourses, prerequisites):
    adj = [[] for _ in range(numCourses)]
    for a, b in prerequisites:
        adj[a].append(b)
    state = [0] * numCourses

    def dfs(u):
        if state[u] == 1:
            return False
        if state[u] == 2:
            return True
        state[u] = 1
        for v in adj[u]:
            if not dfs(v):
                return False
        state[u] = 2
        return True

    return all(dfs(u) for u in range(numCourses))


def _b_robii(nums):
    n = len(nums)
    if n == 1:
        return nums[0]
    best = 0
    for mask in range(1 << n):
        ok = all(not ((mask >> i) & 1 and (mask >> ((i + 1) % n)) & 1)
                 for i in range(n))
        if ok:
            best = max(best, sum(nums[i] for i in range(n) if (mask >> i) & 1))
    return best


def _b_decode(s):
    from functools import lru_cache

    @lru_cache(None)
    def rec(i):
        if i == len(s):
            return 1
        if s[i] == "0":
            return 0
        total = rec(i + 1)
        if i + 1 < len(s) and int(s[i:i + 2]) <= 26:
            total += rec(i + 2)
        return total

    return rec(0)


def _b_valid_bst(root):
    vals = _inorder_vals(_build_tree(root))
    return all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))


def _b_invert(root):
    def inv(n):
        if n is None:
            return None
        n.left, n.right = inv(n.right), inv(n.left)
        return n

    return _serialize_tree(inv(_build_tree(root)))


def _b_same_tree(p, q):
    def same(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)

    return same(_build_tree(p), _build_tree(q))


def _b_lcs(text1, text2):
    from functools import lru_cache

    @lru_cache(None)
    def rec(i, j):
        if i == len(text1) or j == len(text2):
            return 0
        if text1[i] == text2[j]:
            return 1 + rec(i + 1, j + 1)
        return max(rec(i + 1, j), rec(i, j + 1))

    return rec(0, 0)


def _b_level_order(root):
    res = []

    def dfs(node, depth):
        if node is None:
            return
        if depth == len(res):
            res.append([])
        res[depth].append(node.val)
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)

    dfs(_build_tree(root), 0)
    return res


def _b_kth(root, k):
    return sorted(_inorder_vals(_build_tree(root)))[k - 1]


def _b_maxdepth(root):
    node = _build_tree(root)
    if node is None:
        return 0
    q, depth = [node], 0
    while q:
        depth += 1
        nxt = []
        for x in q:
            if x.left:
                nxt.append(x.left)
            if x.right:
                nxt.append(x.right)
        q = nxt
    return depth


def _b_build_tree(preorder, inorder):
    def build(pre, ino):
        if not pre:
            return None
        root = _TN(pre[0])
        idx = ino.index(pre[0])
        root.left = build(pre[1:1 + idx], ino[:idx])
        root.right = build(pre[1 + idx:], ino[idx + 1:])
        return root

    return _serialize_tree(build(preorder, inorder))


def _b_lca(root, p, q):
    node = _build_tree(root)
    pp, qp = _path_to(node, p), _path_to(node, q)
    lca = None
    for a, b in zip(pp, qp):
        if a is b:
            lca = a
        else:
            break
    return lca.val


def _b_maxpath(root):
    node = _build_tree(root)
    nodes, adj = [], {}

    def collect(n):
        if n is None:
            return
        nodes.append(n)
        adj.setdefault(id(n), [])
        for c in (n.left, n.right):
            if c is not None:
                adj[id(n)].append(c)
                adj.setdefault(id(c), []).append(n)
        collect(n.left)
        collect(n.right)

    collect(node)
    best = [-10 ** 9]

    def dfs(n, seen, total):
        total += n.val
        best[0] = max(best[0], total)
        for nb in adj[id(n)]:
            if id(nb) not in seen:
                seen.add(id(nb))
                dfs(nb, seen, total)
                seen.discard(id(nb))

    for n in nodes:
        dfs(n, {id(n)}, 0)
    return best[0]


# ---- Random input generators -----------------------------------------------
def _gen_islands(r):
    out = []
    for _ in range(5):
        rows, cols = r.randint(1, 6), r.randint(1, 6)
        out.append({"grid": [[r.choice("01") for _ in range(cols)]
                             for _ in range(rows)]})
    out.append({"grid": [[r.choice("0011") for _ in range(40)] for _ in range(40)]})
    return out


def _gen_setzero(r):
    out = []
    for _ in range(5):
        rows, cols = r.randint(1, 4), r.randint(1, 4)
        out.append({"matrix": [[r.choice([0, 0, 1, 2, 3, -1]) for _ in range(cols)]
                              for _ in range(rows)]})
    return out


def _gen_minwindow(r):
    out = []
    for _ in range(6):
        out.append({"s": "".join(r.choice("abc") for _ in range(r.randint(1, 10))),
                    "t": "".join(r.choice("abc") for _ in range(r.randint(1, 3)))})
    return out


def _gen_list(r):
    return [{"head": [r.randint(-50, 50) for _ in range(r.randint(0, 8))]}
            for _ in range(5)]


def _gen_word_search(r):
    out = []
    for _ in range(4):
        rows, cols = r.randint(1, 4), r.randint(1, 4)
        board = [[r.choice("ABCD") for _ in range(cols)] for _ in range(rows)]
        cr, cc = r.randint(0, rows - 1), r.randint(0, cols - 1)
        seen, word = {(cr, cc)}, board[cr][cc]
        for _ in range(r.randint(0, 4)):
            nbrs = [(cr + dr, cc + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if 0 <= cr + dr < rows and 0 <= cc + dc < cols
                    and (cr + dr, cc + dc) not in seen]
            if not nbrs:
                break
            cr, cc = r.choice(nbrs)
            seen.add((cr, cc))
            word += board[cr][cc]
        out.append({"board": [row[:] for row in board], "word": word})
        out.append({"board": [row[:] for row in board],
                    "word": "".join(r.choice("ABCD") for _ in range(r.randint(1, 5)))})
    return out


def _gen_findwords(r):
    out = []
    for _ in range(4):
        rows, cols = r.randint(1, 4), r.randint(1, 4)
        board = [[r.choice("abc") for _ in range(cols)] for _ in range(rows)]
        words = {"".join(r.choice("abc") for _ in range(r.randint(1, 4)))
                 for _ in range(r.randint(1, 4))}
        out.append({"board": board, "words": list(words)})
    return out


def _gen_course(r):
    out = []
    for _ in range(5):
        n = r.randint(1, 6)
        prereqs = []
        for _ in range(r.randint(0, n + 2)):
            a, b = r.randint(0, n - 1), r.randint(0, n - 1)
            if a != b and [a, b] not in prereqs:
                prereqs.append([a, b])
        out.append({"numCourses": n, "prerequisites": prereqs})
    return out


def _gen_countbits(r):
    return [{"n": r.randint(0, 50)} for _ in range(5)]


def _gen_robii(r):
    return [{"nums": [r.randint(0, 20) for _ in range(r.randint(1, 12))]}
            for _ in range(5)]


def _gen_decode(r):
    return [{"s": "".join(r.choice("0123456789") for _ in range(r.randint(1, 8)))}
            for _ in range(6)]


def _gen_lcs(r):
    return [{"text1": "".join(r.choice("abc") for _ in range(r.randint(1, 8))),
             "text2": "".join(r.choice("abc") for _ in range(r.randint(1, 8)))}
            for _ in range(6)]


def _gen_valid_bst(r):
    out = [{"root": _rand_tree_arr(r, 1, 10, -15, 15)} for _ in range(3)]
    out += [{"root": _rand_bst(r, 1, 10, -30, 30)[0]} for _ in range(3)]
    return out


def _gen_tree(r):
    return [{"root": _rand_tree_arr(r, 1, 10)} for _ in range(5)] + [{"root": []}]


def _gen_tree_small(r):
    return [{"root": _rand_tree_arr(r, 1, 7)} for _ in range(5)]


def _gen_same(r):
    out = []
    for _ in range(5):
        a = _rand_tree_arr(r, 1, 8)
        q = list(a) if r.random() < 0.5 else _rand_tree_arr(r, 1, 8)
        out.append({"p": a, "q": q})
    return out


def _gen_kth(r):
    out = []
    for _ in range(5):
        arr, vals = _rand_bst(r, 1, 10, -30, 30)
        out.append({"root": arr, "k": r.randint(1, len(vals))})
    return out


def _gen_construct(r):
    out = []
    for _ in range(5):
        vals = r.sample(range(-30, 30), r.randint(1, 9))
        root = _rand_tree_root_from_vals(r, vals)
        out.append({"preorder": _preorder_vals(root), "inorder": _inorder_vals(root)})
    return out


def _gen_lca(r):
    out = []
    for _ in range(5):
        vals = r.sample(range(-30, 30), r.randint(2, 10))
        root = _rand_tree_root_from_vals(r, vals)
        p, q = r.sample(vals, 2)
        out.append({"root": _serialize_tree(root), "p": p, "q": q})
    return out


def _gen_lca_bst(r):
    out = []
    for _ in range(5):
        arr, vals = _rand_bst(r, 2, 10, -40, 40)
        p, q = r.sample(vals, 2)
        out.append({"root": arr, "p": p, "q": q})
    return out


add("number-of-islands", "Number of Islands", "medium",
    ["graph", "matrix", "depth-first-search", "union-find"], "numIslands",
    [("grid", "string[][]")], "int",
    """
Given an `m x n` 2D binary grid `grid` of `'1'`s (land) and `'0'`s (water), return
**the number of islands**. An island is formed by connecting adjacent land cells
**horizontally or vertically** and is surrounded by water; assume all four edges
of the grid are surrounded by water.

## Constraints
- `m == len(grid)`, `n == len(grid[0])`, `1 <= m, n <= 300`
- `grid[i][j]` is `'0'` or `'1'`

## Examples
![Example 1: one connected island](/problems/number-of-islands/assets/example-1.svg)

Input: `grid = [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]`
Output: `1`

![Example 2: three separate islands](/problems/number-of-islands/assets/example-2.svg)

Input: `grid = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]`
Output: `3`
""",
    """def numIslands(grid):
    if not grid or not grid[0]:
        return 0
    rows, cols = len(grid), len(grid[0])
    seen = [[False] * cols for _ in range(rows)]

    def flood(sr, sc):
        stack = [(sr, sc)]
        while stack:
            r, c = stack.pop()
            if 0 <= r < rows and 0 <= c < cols and not seen[r][c] and grid[r][c] == "1":
                seen[r][c] = True
                stack.extend([(r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)])

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and not seen[r][c]:
                flood(r, c)
                count += 1
    return count
""",
    visible=[{"grid": [["1", "1", "1", "1", "0"], ["1", "1", "0", "1", "0"],
                       ["1", "1", "0", "0", "0"], ["0", "0", "0", "0", "0"]]},
             {"grid": [["1", "1", "0", "0", "0"], ["1", "1", "0", "0", "0"],
                       ["0", "0", "1", "0", "0"], ["0", "0", "0", "1", "1"]]}],
    hidden=[{"grid": [["0", "0"], ["0", "0"]]}, {"grid": [["1"]]}, {"grid": [["0"]]},
            {"grid": [["1", "0"], ["0", "1"]]}, {"grid": [["1", "1"], ["1", "1"]]}],
    gen=_gen_islands, brute=_b_islands,
    checks=[({"grid": [["1", "1", "1", "1", "0"], ["1", "1", "0", "1", "0"],
                       ["1", "1", "0", "0", "0"], ["0", "0", "0", "0", "0"]]}, 1),
            ({"grid": [["1", "1", "0", "0", "0"], ["1", "1", "0", "0", "0"],
                       ["0", "0", "1", "0", "0"], ["0", "0", "0", "1", "1"]]}, 3),
            ({"grid": [["1", "0"], ["0", "1"]]}, 2)],
    assets={
        "example-1.svg": figures.islands_svg(
            [["1", "1", "1", "1", "0"], ["1", "1", "0", "1", "0"],
             ["1", "1", "0", "0", "0"], ["0", "0", "0", "0", "0"]], "1 island"),
        "example-2.svg": figures.islands_svg(
            [["1", "1", "0", "0", "0"], ["1", "1", "0", "0", "0"],
             ["0", "0", "1", "0", "0"], ["0", "0", "0", "1", "1"]], "3 islands"),
    })

add("set-matrix-zeroes", "Set Matrix Zeroes", "medium",
    ["array", "matrix", "hash-table"], "setZeroes", [("matrix", "int[][]")], "int[][]",
    """
Given an `m x n` integer matrix, if an element is `0`, set its **entire row and
column** to `0`. Do it in place and **return the modified matrix**.

## Constraints
- `m == len(matrix)`, `n == len(matrix[0])`, `1 <= m, n <= 200`
- `-2^31 <= matrix[i][j] <= 2^31 - 1`

## Examples
![Example 1: the middle 0 clears its row and column](/problems/set-matrix-zeroes/assets/example-1.svg)

Input: `matrix = [[1,1,1],[1,0,1],[1,1,1]]`
Output: `[[1,0,1],[0,0,0],[1,0,1]]`

![Example 2](/problems/set-matrix-zeroes/assets/example-2.svg)

Input: `matrix = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]`
Output: `[[0,0,0,0],[0,4,5,0],[0,3,1,0]]`
""",
    """def setZeroes(matrix):
    rows, cols = len(matrix), len(matrix[0])
    zero_rows, zero_cols = set(), set()
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 0:
                zero_rows.add(r)
                zero_cols.add(c)
    for r in range(rows):
        for c in range(cols):
            if r in zero_rows or c in zero_cols:
                matrix[r][c] = 0
    return matrix
""",
    visible=[{"matrix": [[1, 1, 1], [1, 0, 1], [1, 1, 1]]},
             {"matrix": [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]}],
    hidden=[{"matrix": [[0]]}, {"matrix": [[5]]}, {"matrix": [[1, 2, 3]]},
            {"matrix": [[1], [0], [1]]}],
    gen=_gen_setzero, brute=_b_setzero,
    checks=[({"matrix": [[1, 1, 1], [1, 0, 1], [1, 1, 1]]},
             [[1, 0, 1], [0, 0, 0], [1, 0, 1]]),
            ({"matrix": [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]},
             [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]])],
    assets={
        "example-1.svg": figures.matrix_zeroes_svg(
            [[1, 1, 1], [1, 0, 1], [1, 1, 1]], [[1, 0, 1], [0, 0, 0], [1, 0, 1]]),
        "example-2.svg": figures.matrix_zeroes_svg(
            [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]],
            [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]),
    })

add("minimum-window-substring", "Minimum Window Substring", "hard",
    ["string", "sliding-window", "hash-table"], "minWindow",
    [("s", "string"), ("t", "string")], "string",
    """
Given strings `s` and `t`, return **the shortest substring of `s` that contains
every character of `t` (counting duplicates)**. If no such window exists, return
the empty string `""`.

## Constraints
- `1 <= len(s), len(t) <= 10^5`
- `s` and `t` consist of uppercase and lowercase English letters
- The answer is unique; when lengths tie, the leftmost window is returned

## Examples
Input: `s = "ADOBECODEBANC", t = "ABC"`
Output: `"BANC"`

Input: `s = "a", t = "a"`
Output: `"a"`

Input: `s = "a", t = "aa"`
Output: `""`
Explanation: `s` has a single `'a'`, so it cannot cover both.
""",
    """def minWindow(s, t):
    if not t or len(t) > len(s):
        return ""
    from collections import Counter
    need = Counter(t)
    missing = len(t)
    left = start = end = 0
    best_len = float("inf")
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            if right - left + 1 < best_len:
                best_len = right - left + 1
                start, end = left, right + 1
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return s[start:end] if best_len != float("inf") else ""
""",
    visible=[{"s": "ADOBECODEBANC", "t": "ABC"}, {"s": "a", "t": "a"},
             {"s": "a", "t": "aa"}],
    hidden=[{"s": "ab", "t": "b"}, {"s": "abc", "t": "cba"}, {"s": "aa", "t": "aa"},
            {"s": "bba", "t": "ab"}, {"s": "cabwefgewcwaefgcf", "t": "cae"}],
    gen=_gen_minwindow, brute=_b_minwindow,
    checks=[({"s": "ADOBECODEBANC", "t": "ABC"}, "BANC"), ({"s": "a", "t": "a"}, "a"),
            ({"s": "a", "t": "aa"}, "")])

add("reverse-linked-list", "Reverse Linked List", "easy",
    ["linked-list", "recursion"], "reverseList", [("head", "int[]")], "int[]",
    """
The values of a singly linked list are given in order as an array `head`. Return
**the values after the list is reversed**.

## Constraints
- `0 <= len(head) <= 5000`
- `-5000 <= head[i] <= 5000`

## Examples
Input: `head = [1,2,3,4,5]`
Output: `[5,4,3,2,1]`

Input: `head = [1,2]`
Output: `[2,1]`

Input: `head = []`
Output: `[]`
""",
    """def reverseList(head):
    result = []
    for value in head:
        result.insert(0, value)
    return result
""",
    visible=[{"head": [1, 2, 3, 4, 5]}, {"head": [1, 2]}, {"head": []}],
    hidden=[{"head": [1]}, {"head": [-1, 0, 1]}, {"head": list(range(100))}],
    gen=_gen_list, brute=lambda head: list(reversed(head)),
    checks=[({"head": [1, 2, 3, 4, 5]}, [5, 4, 3, 2, 1]), ({"head": [1, 2]}, [2, 1]),
            ({"head": []}, [])])

add("word-search", "Word Search", "medium",
    ["backtracking", "matrix", "depth-first-search"], "exist",
    [("board", "string[][]"), ("word", "string")], "bool",
    """
Given an `m x n` grid of characters `board` and a string `word`, return **`true`
if `word` can be spelled out from sequentially adjacent cells**, where adjacent
cells neighbour horizontally or vertically. The same cell may not be used more
than once in a single match.

## Constraints
- `m == len(board)`, `n == len(board[0])`, `1 <= m, n <= 6`
- `1 <= len(word) <= 15`
- `board` and `word` consist of English letters

## Examples
![Example 1: the path spelling ABCCED](/problems/word-search/assets/example-1.svg)

Input: `board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"`
Output: `true`

Input: `board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "SEE"`
Output: `true`

Input: `board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCB"`
Output: `false`
Explanation: the second `B` would reuse the only `B` cell.
""",
    """def exist(board, word):
    rows, cols = len(board), len(board[0])

    def dfs(r, c, k):
        if k == len(word):
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols or board[r][c] != word[k]:
            return False
        tmp = board[r][c]
        board[r][c] = "#"
        found = (dfs(r + 1, c, k + 1) or dfs(r - 1, c, k + 1)
                 or dfs(r, c + 1, k + 1) or dfs(r, c - 1, k + 1))
        board[r][c] = tmp
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False
""",
    visible=[{"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"],
                        ["A", "D", "E", "E"]], "word": "ABCCED"},
             {"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"],
                        ["A", "D", "E", "E"]], "word": "SEE"},
             {"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"],
                        ["A", "D", "E", "E"]], "word": "ABCB"}],
    hidden=[{"board": [["A"]], "word": "A"}, {"board": [["A"]], "word": "B"},
            {"board": [["A", "B"], ["C", "D"]], "word": "ABDC"},
            {"board": [["A", "A"]], "word": "AAA"}],
    gen=_gen_word_search, brute=_b_word_exist,
    checks=[({"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"],
                        ["A", "D", "E", "E"]], "word": "ABCCED"}, True),
            ({"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"],
                        ["A", "D", "E", "E"]], "word": "SEE"}, True),
            ({"board": [["A", "B", "C", "E"], ["S", "F", "C", "S"],
                        ["A", "D", "E", "E"]], "word": "ABCB"}, False)],
    assets={
        "example-1.svg": figures.word_search_svg(
            [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]],
            "ABCCED", [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1)]),
    })

add("course-schedule", "Course Schedule", "medium",
    ["graph", "topological-sort", "depth-first-search"], "canFinish",
    [("numCourses", "int"), ("prerequisites", "int[][]")], "bool",
    """
There are `numCourses` courses labelled `0` to `numCourses - 1`. Each
`prerequisites[i] = [a, b]` means course `b` must be taken before course `a`.
Return **`true` if it is possible to finish every course** — i.e. the
prerequisite graph contains no cycle.

## Constraints
- `1 <= numCourses <= 2000`
- `0 <= len(prerequisites) <= 5000`, `prerequisites[i].length == 2`
- `0 <= a, b < numCourses`; all pairs are distinct

## Examples
Input: `numCourses = 2, prerequisites = [[1,0]]`
Output: `true`

Input: `numCourses = 2, prerequisites = [[1,0],[0,1]]`
Output: `false`
Explanation: courses `0` and `1` each require the other.
""",
    """def canFinish(numCourses, prerequisites):
    from collections import deque
    adj = [[] for _ in range(numCourses)]
    indeg = [0] * numCourses
    for a, b in prerequisites:
        adj[b].append(a)
        indeg[a] += 1
    q = deque(i for i in range(numCourses) if indeg[i] == 0)
    done = 0
    while q:
        u = q.popleft()
        done += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return done == numCourses
""",
    visible=[{"numCourses": 2, "prerequisites": [[1, 0]]},
             {"numCourses": 2, "prerequisites": [[1, 0], [0, 1]]}],
    hidden=[{"numCourses": 1, "prerequisites": []},
            {"numCourses": 3, "prerequisites": [[1, 0], [2, 1]]},
            {"numCourses": 3, "prerequisites": [[0, 1], [1, 2], [2, 0]]},
            {"numCourses": 4, "prerequisites": [[1, 0], [2, 0], [3, 1], [3, 2]]}],
    gen=_gen_course, brute=_b_course,
    checks=[({"numCourses": 2, "prerequisites": [[1, 0]]}, True),
            ({"numCourses": 2, "prerequisites": [[1, 0], [0, 1]]}, False),
            ({"numCourses": 3, "prerequisites": [[0, 1], [1, 2], [2, 0]]}, False)])

add("counting-bits", "Counting Bits", "easy",
    ["bit-manipulation", "dynamic-programming"], "countBits", [("n", "int")], "int[]",
    """
Given an integer `n`, return **an array `ans` of length `n + 1`** where `ans[i]`
is the number of set bits (`1`s) in the binary representation of `i`.

## Constraints
- `0 <= n <= 10^5`

## Examples
Input: `n = 2`
Output: `[0,1,1]`

Input: `n = 5`
Output: `[0,1,1,2,1,2]`
Explanation: `3 = 11` has two set bits, `5 = 101` has two.
""",
    """def countBits(n):
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        dp[i] = dp[i >> 1] + (i & 1)
    return dp
""",
    visible=[{"n": 2}, {"n": 5}],
    hidden=[{"n": 0}, {"n": 1}, {"n": 16}, {"n": 31}],
    gen=_gen_countbits, brute=lambda n: [bin(i).count("1") for i in range(n + 1)],
    checks=[({"n": 2}, [0, 1, 1]), ({"n": 5}, [0, 1, 1, 2, 1, 2])])

add("word-search-ii", "Word Search II", "hard",
    ["trie", "backtracking", "matrix"], "findWords",
    [("board", "string[][]"), ("words", "string[]")], "string[]",
    """
Given an `m x n` `board` of lowercase letters and a list of `words`, return
**all words from the list that can be found on the board**, in any order. A word
is formed from sequentially adjacent cells (horizontal/vertical) without reusing
a cell within that word.

## Constraints
- `m == len(board)`, `n == len(board[i])`, `1 <= m, n <= 12`
- `1 <= len(words) <= 3 * 10^4`, `1 <= len(words[i]) <= 10`
- `board[i][j]` and `words[i]` are lowercase English letters; words are unique

## Examples
Input: `board = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]], words = ["oath","pea","eat","rain"]`
Output: `["eat","oath"]`
Explanation: the answer may be returned in any order.

Input: `board = [["a","b"],["c","d"]], words = ["abcb"]`
Output: `[]`
""",
    """def findWords(board, words):
    rows, cols = len(board), len(board[0])
    trie = {}
    for w in words:
        node = trie
        for ch in w:
            node = node.setdefault(ch, {})
        node["$"] = w
    res = []

    def dfs(r, c, node):
        ch = board[r][c]
        if ch not in node:
            return
        nxt = node[ch]
        word = nxt.pop("$", None)
        if word is not None:
            res.append(word)
        board[r][c] = "#"
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                dfs(nr, nc, nxt)
        board[r][c] = ch

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie)
    return res
""",
    visible=[{"board": [["o", "a", "a", "n"], ["e", "t", "a", "e"],
                        ["i", "h", "k", "r"], ["i", "f", "l", "v"]],
              "words": ["oath", "pea", "eat", "rain"]},
             {"board": [["a", "b"], ["c", "d"]], "words": ["abcb"]}],
    hidden=[{"board": [["a"]], "words": ["a"]}, {"board": [["a"]], "words": ["b"]},
            {"board": [["a", "b"], ["c", "d"]], "words": ["abdc", "ab", "acdb"]}],
    gen=_gen_findwords, brute=_b_findwords, norm=lambda x: sorted(x),
    checks=[({"board": [["o", "a", "a", "n"], ["e", "t", "a", "e"],
                        ["i", "h", "k", "r"], ["i", "f", "l", "v"]],
              "words": ["oath", "pea", "eat", "rain"]}, ["oath", "eat"]),
            ({"board": [["a", "b"], ["c", "d"]], "words": ["abcb"]}, [])])

add("house-robber-ii", "House Robber II", "medium",
    ["array", "dynamic-programming"], "rob", [("nums", "int[]")], "int",
    """
Houses are arranged in a **circle**, so the first and the last house are
adjacent. House `i` holds `nums[i]` money and you cannot rob two adjacent houses.
Return **the maximum amount of money you can rob**.

## Constraints
- `1 <= len(nums) <= 100`
- `0 <= nums[i] <= 1000`

## Examples
Input: `nums = [2,3,2]`
Output: `3`
Explanation: houses 1 and 3 are adjacent in the circle, so you cannot take both 2s.

Input: `nums = [1,2,3,1]`
Output: `4`

Input: `nums = [1,2,3]`
Output: `3`
""",
    """def rob(nums):
    def rob_line(arr):
        prev = cur = 0
        for x in arr:
            prev, cur = cur, max(cur, prev + x)
        return cur

    if len(nums) == 1:
        return nums[0]
    return max(rob_line(nums[1:]), rob_line(nums[:-1]))
""",
    visible=[{"nums": [2, 3, 2]}, {"nums": [1, 2, 3, 1]}, {"nums": [1, 2, 3]}],
    hidden=[{"nums": [5]}, {"nums": [2, 3]}, {"nums": [1, 2, 1, 1]},
            {"nums": [200, 3, 140, 20, 10]}],
    gen=_gen_robii, brute=_b_robii,
    checks=[({"nums": [2, 3, 2]}, 3), ({"nums": [1, 2, 3, 1]}, 4),
            ({"nums": [1, 2, 3]}, 3), ({"nums": [5]}, 5)])

add("decode-ways", "Decode Ways", "medium",
    ["string", "dynamic-programming"], "numDecodings", [("s", "string")], "int",
    """
A digit string is decoded with the mapping `"1" -> 'A'`, `"2" -> 'B'`, …,
`"26" -> 'Z'`. Given a string `s` of digits, return **the number of ways to decode
it**. A `'0'` cannot begin a code, and some strings cannot be decoded at all
(return `0`).

## Constraints
- `1 <= len(s) <= 100`
- `s` contains only digits and may contain leading zeros

## Examples
Input: `s = "12"`
Output: `2`
Explanation: `"AB"` (1 2) or `"L"` (12).

Input: `s = "226"`
Output: `3`
Explanation: `"BZ"` (2 26), `"VF"` (22 6) or `"BBF"` (2 2 6).

Input: `s = "06"`
Output: `0`
Explanation: a leading zero is invalid.
""",
    """def numDecodings(s):
    if not s or s[0] == "0":
        return 0
    prev2, prev1 = 1, 1
    for i in range(1, len(s)):
        cur = 0
        if s[i] != "0":
            cur += prev1
        if 10 <= int(s[i - 1:i + 1]) <= 26:
            cur += prev2
        prev2, prev1 = prev1, cur
    return prev1
""",
    visible=[{"s": "12"}, {"s": "226"}, {"s": "06"}],
    hidden=[{"s": "0"}, {"s": "10"}, {"s": "27"}, {"s": "11106"}, {"s": "100"}],
    gen=_gen_decode, brute=_b_decode,
    checks=[({"s": "12"}, 2), ({"s": "226"}, 3), ({"s": "06"}, 0),
            ({"s": "11106"}, 2), ({"s": "100"}, 0)])

add("validate-binary-search-tree", "Validate Binary Search Tree", "medium",
    ["tree", "binary-search-tree", "depth-first-search"], "isValidBST",
    [("root", "int[]")], "bool",
    """
Given the level-order array `root` of a binary tree (`null`/`None` marks a missing
child), return **`true` if it is a valid binary search tree**: every node's left
subtree holds only smaller keys, its right subtree only larger keys, and both
subtrees are themselves valid BSTs.

## Constraints
- `1 <= number of nodes <= 10^4`
- `-2^31 <= Node.val <= 2^31 - 1`

## Examples
Input: `root = [2,1,3]`
Output: `true`

Input: `root = [5,1,4,null,null,3,6]`
Output: `false`
Explanation: the right child `4` is smaller than the root `5`.
""",
    """def isValidBST(root):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        q, i = [head], 1
        while q and i < len(arr):
            cur = q.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); q.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); q.append(cur.right)
        return head

    def check(node, lo, hi):
        if node is None:
            return True
        if not (lo < node.val < hi):
            return False
        return check(node.left, lo, node.val) and check(node.right, node.val, hi)

    return check(build(root), float("-inf"), float("inf"))
""",
    visible=[{"root": [2, 1, 3]}, {"root": [5, 1, 4, None, None, 3, 6]}],
    hidden=[{"root": [1]}, {"root": [2, 2]},
            {"root": [5, 4, 6, None, None, 3, 7]},
            {"root": [10, 5, 15, 2, 7, 12, 20]}],
    gen=_gen_valid_bst, brute=_b_valid_bst,
    checks=[({"root": [2, 1, 3]}, True),
            ({"root": [5, 1, 4, None, None, 3, 6]}, False), ({"root": [1]}, True),
            ({"root": [5, 4, 6, None, None, 3, 7]}, False)])

add("invert-binary-tree", "Invert Binary Tree", "easy",
    ["tree", "depth-first-search", "breadth-first-search"], "invertTree",
    [("root", "int[]")], "int[]",
    """
Given the level-order array `root` of a binary tree, invert it (mirror every
left/right pair) and **return the level-order array of the inverted tree**
(`null`/`None` marks a missing child; trailing nulls are dropped).

## Constraints
- `0 <= number of nodes <= 100`
- `-100 <= Node.val <= 100`

## Examples
![Example 1: mirroring every left/right pair](/problems/invert-binary-tree/assets/example-1.svg)

Input: `root = [4,2,7,1,3,6,9]`
Output: `[4,7,2,9,6,3,1]`

Input: `root = [2,1,3]`
Output: `[2,3,1]`

Input: `root = []`
Output: `[]`
""",
    """def invertTree(root):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        q, i = [head], 1
        while q and i < len(arr):
            cur = q.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); q.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); q.append(cur.right)
        return head

    def serialize(node):
        out, q = [], [node]
        while q:
            cur = q.pop(0)
            if cur is None:
                out.append(None)
                continue
            out.append(cur.val); q.append(cur.left); q.append(cur.right)
        while out and out[-1] is None:
            out.pop()
        return out

    def invert(n):
        if n is None:
            return None
        n.left, n.right = invert(n.right), invert(n.left)
        return n

    return serialize(invert(build(root)))
""",
    visible=[{"root": [4, 2, 7, 1, 3, 6, 9]}, {"root": [2, 1, 3]}, {"root": []}],
    hidden=[{"root": [1]}, {"root": [1, 2]}, {"root": [1, None, 2]}],
    gen=_gen_tree, brute=_b_invert,
    checks=[({"root": [4, 2, 7, 1, 3, 6, 9]}, [4, 7, 2, 9, 6, 3, 1]),
            ({"root": [2, 1, 3]}, [2, 3, 1]), ({"root": []}, [])],
    assets={
        "example-1.svg": figures.tree_transform_svg(
            [4, 2, 7, 1, 3, 6, 9], [4, 7, 2, 9, 6, 3, 1]),
    })

add("same-tree", "Same Tree", "easy", ["tree", "depth-first-search"], "isSameTree",
    [("p", "int[]"), ("q", "int[]")], "bool",
    """
Given the level-order arrays `p` and `q` of two binary trees, return **`true` if
the trees are identical** — same shape and same node values.

## Constraints
- `0 <= number of nodes in each tree <= 100`
- `-10^4 <= Node.val <= 10^4`

## Examples
Input: `p = [1,2,3], q = [1,2,3]`
Output: `true`

Input: `p = [1,2], q = [1,null,2]`
Output: `false`

Input: `p = [1,2,1], q = [1,1,2]`
Output: `false`
""",
    """def isSameTree(p, q):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        qq, i = [head], 1
        while qq and i < len(arr):
            cur = qq.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); qq.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); qq.append(cur.right)
        return head

    def same(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)

    return same(build(p), build(q))
""",
    visible=[{"p": [1, 2, 3], "q": [1, 2, 3]}, {"p": [1, 2], "q": [1, None, 2]},
             {"p": [1, 2, 1], "q": [1, 1, 2]}],
    hidden=[{"p": [], "q": []}, {"p": [1], "q": []}, {"p": [1], "q": [1]}],
    gen=_gen_same, brute=_b_same_tree,
    checks=[({"p": [1, 2, 3], "q": [1, 2, 3]}, True),
            ({"p": [1, 2], "q": [1, None, 2]}, False),
            ({"p": [1, 2, 1], "q": [1, 1, 2]}, False)])

add("longest-common-subsequence", "Longest Common Subsequence", "medium",
    ["string", "dynamic-programming"], "longestCommonSubsequence",
    [("text1", "string"), ("text2", "string")], "int",
    """
Given strings `text1` and `text2`, return **the length of their longest common
subsequence**, or `0` if there is none. A subsequence keeps relative order but may
drop characters.

## Constraints
- `1 <= len(text1), len(text2) <= 1000`
- both consist of lowercase English letters

## Examples
Input: `text1 = "abcde", text2 = "ace"`
Output: `3`
Explanation: the LCS is `"ace"`.

Input: `text1 = "abc", text2 = "abc"`
Output: `3`

Input: `text1 = "abc", text2 = "def"`
Output: `0`
""",
    """def longestCommonSubsequence(text1, text2):
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if text1[i] == text2[j]:
                dp[i][j] = 1 + dp[i + 1][j + 1]
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
    return dp[0][0]
""",
    visible=[{"text1": "abcde", "text2": "ace"}, {"text1": "abc", "text2": "abc"},
             {"text1": "abc", "text2": "def"}],
    hidden=[{"text1": "a", "text2": "a"}, {"text1": "abcba", "text2": "bca"},
            {"text1": "aaaa", "text2": "aa"}],
    gen=_gen_lcs, brute=_b_lcs,
    checks=[({"text1": "abcde", "text2": "ace"}, 3),
            ({"text1": "abc", "text2": "abc"}, 3),
            ({"text1": "abc", "text2": "def"}, 0)])

add("binary-tree-level-order-traversal", "Binary Tree Level Order Traversal",
    "medium", ["tree", "breadth-first-search"], "levelOrder",
    [("root", "int[]")], "int[][]",
    """
Given the level-order array `root` of a binary tree, return **its level-order
traversal as a list of levels** — top to bottom, left to right within each level.

## Constraints
- `0 <= number of nodes <= 2000`
- `-1000 <= Node.val <= 1000`

## Examples
Input: `root = [3,9,20,null,null,15,7]`
Output: `[[3],[9,20],[15,7]]`

Input: `root = [1]`
Output: `[[1]]`

Input: `root = []`
Output: `[]`
""",
    """def levelOrder(root):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        q, i = [head], 1
        while q and i < len(arr):
            cur = q.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); q.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); q.append(cur.right)
        return head

    from collections import deque
    node = build(root)
    if node is None:
        return []
    q, res = deque([node]), []
    while q:
        level = []
        for _ in range(len(q)):
            cur = q.popleft()
            level.append(cur.val)
            if cur.left:
                q.append(cur.left)
            if cur.right:
                q.append(cur.right)
        res.append(level)
    return res
""",
    visible=[{"root": [3, 9, 20, None, None, 15, 7]}, {"root": [1]}, {"root": []}],
    hidden=[{"root": [1, 2, 3, 4, 5]}, {"root": [1, None, 2]}],
    gen=_gen_tree, brute=_b_level_order,
    checks=[({"root": [3, 9, 20, None, None, 15, 7]}, [[3], [9, 20], [15, 7]]),
            ({"root": [1]}, [[1]]), ({"root": []}, [])])

add("kth-smallest-element-in-a-bst", "Kth Smallest Element in a BST", "medium",
    ["tree", "binary-search-tree", "depth-first-search"], "kthSmallest",
    [("root", "int[]"), ("k", "int")], "int",
    """
Given the level-order array `root` of a binary search tree and an integer `k`,
return **the `k`-th smallest value** (1-indexed) among all node values.

## Constraints
- `1 <= k <= n` where `n` is the number of nodes, `1 <= n <= 10^4`
- `0 <= Node.val <= 10^4`

## Examples
Input: `root = [3,1,4,null,2], k = 1`
Output: `1`

Input: `root = [5,3,6,2,4,null,null,1], k = 3`
Output: `3`
""",
    """def kthSmallest(root, k):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        q, i = [head], 1
        while q and i < len(arr):
            cur = q.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); q.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); q.append(cur.right)
        return head

    stack, node = [], build(root)
    while stack or node:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val
        node = node.right
""",
    visible=[{"root": [3, 1, 4, None, 2], "k": 1},
             {"root": [5, 3, 6, 2, 4, None, None, 1], "k": 3}],
    hidden=[{"root": [1], "k": 1}, {"root": [2, 1, 3], "k": 3},
            {"root": [2, 1, 3], "k": 2}],
    gen=_gen_kth, brute=_b_kth,
    checks=[({"root": [3, 1, 4, None, 2], "k": 1}, 1),
            ({"root": [5, 3, 6, 2, 4, None, None, 1], "k": 3}, 3)])

add("maximum-depth-of-binary-tree", "Maximum Depth of Binary Tree", "easy",
    ["tree", "depth-first-search", "breadth-first-search"], "maxDepth",
    [("root", "int[]")], "int",
    """
Given the level-order array `root` of a binary tree, return **its maximum depth**
— the number of nodes on the longest path from the root down to a leaf.

## Constraints
- `0 <= number of nodes <= 10^4`
- `-100 <= Node.val <= 100`

## Examples
Input: `root = [3,9,20,null,null,15,7]`
Output: `3`

Input: `root = [1,null,2]`
Output: `2`
""",
    """def maxDepth(root):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        q, i = [head], 1
        while q and i < len(arr):
            cur = q.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); q.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); q.append(cur.right)
        return head

    def depth(n):
        if n is None:
            return 0
        return 1 + max(depth(n.left), depth(n.right))

    return depth(build(root))
""",
    visible=[{"root": [3, 9, 20, None, None, 15, 7]}, {"root": [1, None, 2]}],
    hidden=[{"root": []}, {"root": [0]}, {"root": [1, 2, None, 3]}],
    gen=_gen_tree, brute=_b_maxdepth,
    checks=[({"root": [3, 9, 20, None, None, 15, 7]}, 3),
            ({"root": [1, None, 2]}, 2), ({"root": []}, 0)])

add("construct-binary-tree-from-preorder-and-inorder-traversal",
    "Construct Binary Tree from Preorder and Inorder Traversal", "medium",
    ["tree", "array", "divide-and-conquer"], "buildTree",
    [("preorder", "int[]"), ("inorder", "int[]")], "int[]",
    """
Given `preorder` and `inorder` traversals of a binary tree with **unique** values,
reconstruct the tree and **return its level-order array** (`null`/`None` marks a
missing child; trailing nulls are dropped).

## Constraints
- `1 <= len(preorder) <= 3000`, `len(inorder) == len(preorder)`
- `-3000 <= preorder[i], inorder[i] <= 3000`; all values unique
- `inorder` is a permutation of `preorder` consistent with some binary tree

## Examples
![Example 1: the reconstructed tree](/problems/construct-binary-tree-from-preorder-and-inorder-traversal/assets/example-1.svg)

Input: `preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]`
Output: `[3,9,20,null,null,15,7]`

Input: `preorder = [-1], inorder = [-1]`
Output: `[-1]`
""",
    """def buildTree(preorder, inorder):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    index = {v: i for i, v in enumerate(inorder)}
    ptr = [0]

    def construct(lo, hi):
        if lo > hi:
            return None
        val = preorder[ptr[0]]
        ptr[0] += 1
        node = Node(val)
        mid = index[val]
        node.left = construct(lo, mid - 1)
        node.right = construct(mid + 1, hi)
        return node

    def serialize(node):
        out, q = [], [node]
        while q:
            cur = q.pop(0)
            if cur is None:
                out.append(None)
                continue
            out.append(cur.val); q.append(cur.left); q.append(cur.right)
        while out and out[-1] is None:
            out.pop()
        return out

    return serialize(construct(0, len(inorder) - 1))
""",
    visible=[{"preorder": [3, 9, 20, 15, 7], "inorder": [9, 3, 15, 20, 7]},
             {"preorder": [-1], "inorder": [-1]}],
    hidden=[{"preorder": [1, 2], "inorder": [2, 1]},
            {"preorder": [1, 2], "inorder": [1, 2]},
            {"preorder": [3, 1, 2], "inorder": [1, 3, 2]}],
    gen=_gen_construct, brute=_b_build_tree,
    checks=[({"preorder": [3, 9, 20, 15, 7], "inorder": [9, 3, 15, 20, 7]},
             [3, 9, 20, None, None, 15, 7]),
            ({"preorder": [-1], "inorder": [-1]}, [-1]),
            ({"preorder": [1, 2], "inorder": [2, 1]}, [1, 2])],
    assets={
        "example-1.svg": figures.tree_svg(
            [3, 9, 20, None, None, 15, 7], caption="reconstructed tree"),
    })

add("lowest-common-ancestor-of-a-binary-tree",
    "Lowest Common Ancestor of a Binary Tree", "medium",
    ["tree", "depth-first-search"], "lowestCommonAncestor",
    [("root", "int[]"), ("p", "int"), ("q", "int")], "int",
    """
Given the level-order array `root` of a binary tree and two values `p` and `q`
present in it, return **the value of their lowest common ancestor** — the deepest
node having both as descendants (a node may be a descendant of itself).

## Constraints
- `2 <= number of nodes <= 10^5`
- `-10^9 <= Node.val <= 10^9`; all values unique
- `p != q`; both `p` and `q` exist in the tree

## Examples
![Example 1: LCA of 5 and 1 is 3](/problems/lowest-common-ancestor-of-a-binary-tree/assets/example-1.svg)

Input: `root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1`
Output: `3`

Input: `root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 4`
Output: `5`
Explanation: `4` is in the subtree of `5`, so `5` is its own ancestor here.

Input: `root = [1,2], p = 1, q = 2`
Output: `1`
""",
    """def lowestCommonAncestor(root, p, q):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        qq, i = [head], 1
        while qq and i < len(arr):
            cur = qq.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); qq.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); qq.append(cur.right)
        return head

    def lca(n):
        if n is None or n.val == p or n.val == q:
            return n
        left = lca(n.left)
        right = lca(n.right)
        if left and right:
            return n
        return left or right

    return lca(build(root)).val
""",
    visible=[{"root": [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], "p": 5, "q": 1},
             {"root": [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], "p": 5, "q": 4},
             {"root": [1, 2], "p": 1, "q": 2}],
    hidden=[{"root": [1, 2, 3, 4, 5, 6, 7], "p": 4, "q": 7},
            {"root": [1, 2, 3, 4, 5, 6, 7], "p": 4, "q": 5}],
    gen=_gen_lca, brute=_b_lca,
    checks=[({"root": [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], "p": 5, "q": 1}, 3),
            ({"root": [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], "p": 5, "q": 4}, 5),
            ({"root": [1, 2], "p": 1, "q": 2}, 1)],
    assets={
        "example-1.svg": figures.tree_svg(
            [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4], highlight={5, 1},
            highlight2={3}, caption="LCA(5, 1) = 3"),
    })

add("sum-of-two-integers", "Sum of Two Integers", "medium",
    ["bit-manipulation", "math"], "getSum", [("a", "int"), ("b", "int")], "int",
    """
Given two integers `a` and `b`, return **their sum** without using the `+` or `-`
operators.

## Constraints
- `-1000 <= a, b <= 1000`

## Examples
Input: `a = 1, b = 2`
Output: `3`

Input: `a = 2, b = 3`
Output: `5`
""",
    """def getSum(a, b):
    mask = 0xFFFFFFFF
    a &= mask
    b &= mask
    while b:
        carry = ((a & b) << 1) & mask
        a = (a ^ b) & mask
        b = carry
    return a if a <= 0x7FFFFFFF else a - 0x100000000
""",
    visible=[{"a": 1, "b": 2}, {"a": 2, "b": 3}],
    hidden=[{"a": -1, "b": 1}, {"a": -2, "b": -3}, {"a": 0, "b": 0},
            {"a": -1000, "b": 1000}, {"a": 1000, "b": 1000}],
    gen=lambda r: [{"a": r.randint(-1000, 1000), "b": r.randint(-1000, 1000)}
                   for _ in range(6)],
    brute=lambda a, b: a + b,
    checks=[({"a": 1, "b": 2}, 3), ({"a": 2, "b": 3}, 5), ({"a": -1, "b": 1}, 0),
            ({"a": -2, "b": -3}, -5)])

add("binary-tree-maximum-path-sum", "Binary Tree Maximum Path Sum", "hard",
    ["tree", "depth-first-search", "dynamic-programming"], "maxPathSum",
    [("root", "int[]")], "int",
    """
A path is a sequence of nodes connected by edges, each used at most once; it need
not pass through the root. Given the level-order array `root` of a binary tree,
return **the maximum path sum over all non-empty paths**.

## Constraints
- `1 <= number of nodes <= 3 * 10^4`
- `-1000 <= Node.val <= 1000`

## Examples
Input: `root = [1,2,3]`
Output: `6`
Explanation: the path `2 -> 1 -> 3` sums to `6`.

![Example 2: best path 15 -> 20 -> 7](/problems/binary-tree-maximum-path-sum/assets/example-2.svg)

Input: `root = [-10,9,20,null,null,15,7]`
Output: `42`
Explanation: the path `15 -> 20 -> 7` sums to `42`.
""",
    """def maxPathSum(root):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        q, i = [head], 1
        while q and i < len(arr):
            cur = q.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); q.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); q.append(cur.right)
        return head

    best = [float("-inf")]

    def gain(n):
        if n is None:
            return 0
        left = max(gain(n.left), 0)
        right = max(gain(n.right), 0)
        best[0] = max(best[0], n.val + left + right)
        return n.val + max(left, right)

    gain(build(root))
    return best[0]
""",
    visible=[{"root": [1, 2, 3]}, {"root": [-10, 9, 20, None, None, 15, 7]}],
    hidden=[{"root": [-3]}, {"root": [2, -1]}, {"root": [-2, -1]},
            {"root": [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]}],
    gen=_gen_tree_small, brute=_b_maxpath,
    checks=[({"root": [1, 2, 3]}, 6),
            ({"root": [-10, 9, 20, None, None, 15, 7]}, 42), ({"root": [-3]}, -3)],
    assets={
        "example-2.svg": figures.tree_svg(
            [-10, 9, 20, None, None, 15, 7], highlight={15, 20, 7},
            caption="path 15 -> 20 -> 7 = 42"),
    })

# ===========================================================================
# Imported from large_bank.txt (distinct problems; variants collapsed)
# ===========================================================================
# ---- Wave 1: arrays & two-pointers -----------------------------------------

def _lb_dup_case(r):
    n = r.randint(2, 14)
    arr = list(range(1, n + 1))
    arr.append(r.randint(1, n))
    r.shuffle(arr)
    return {"nums": arr}


add("single-number", "Single Number", "easy",
    ["array", "bit-manipulation"], "singleNumber", [("nums", "int[]")], "int",
    """
Every value in the integer array `nums` appears exactly twice except for one
value that appears once. Return **the value that appears only once**.

Aim for `O(n)` time and `O(1)` extra space.

## Constraints
- `1 <= len(nums) <= 3*10^4` and `len(nums)` is odd.
- Exactly one element appears once; every other element appears exactly twice.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [2,2,1]`
Output: `1`

Input: `nums = [4,1,2,1,2]`
Output: `4`

Input: `nums = [7]`
Output: `7`
""",
    """def singleNumber(nums):
    r = 0
    for x in nums:
        r ^= x
    return r
""",
    visible=[{"nums": [2, 2, 1]}, {"nums": [4, 1, 2, 1, 2]}, {"nums": [7]}],
    hidden=[{"nums": [-5, -5, 9]}, {"nums": [0, 1, 0]},
            {"nums": [10 ** 9, -(10 ** 9), 10 ** 9]},
            {"nums": [i for i in range(1, 5001) for _ in (0, 1)] + [424242]}],
    checks=[({"nums": [2, 2, 1]}, 1), ({"nums": [4, 1, 2, 1, 2]}, 4),
            ({"nums": [7]}, 7)])

add("move-zeroes", "Move Zeroes", "easy",
    ["array", "two-pointers"], "moveZeroes", [("nums", "int[]")], "int[]",
    """
Given an integer array `nums`, move every `0` to the end while keeping the
relative order of the non-zero elements. Return **the resulting array**.

## Constraints
- `0 <= len(nums) <= 10^5`.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [0,1,0,3,12]`
Output: `[1,3,12,0,0]`

Input: `nums = [0]`
Output: `[0]`

Input: `nums = [1,2,3]`
Output: `[1,2,3]`
""",
    """def moveZeroes(nums):
    out = [x for x in nums if x != 0]
    out.extend(0 for x in nums if x == 0)
    return out
""",
    visible=[{"nums": [0, 1, 0, 3, 12]}, {"nums": [0]}, {"nums": [1, 2, 3]}],
    hidden=[{"nums": []}, {"nums": [0, 0, 0]}, {"nums": [-1, 0, -2, 0, 5]}],
    gen=lambda r: [{"nums": ilist(r, 0, 30, -3, 3)} for _ in range(4)],
    brute=lambda nums: [x for x in nums if x != 0] + [0] * nums.count(0),
    checks=[({"nums": [0, 1, 0, 3, 12]}, [1, 3, 12, 0, 0]), ({"nums": [0]}, [0])])

add("sort-colors", "Sort Colors", "medium",
    ["array", "two-pointers", "sorting"], "sortColors", [("nums", "int[]")], "int[]",
    """
Given an array `nums` containing only the integers `0`, `1`, and `2`, sort it in
non-decreasing order and return **the sorted array**. Aim for a single pass with
`O(1)` extra space (Dutch national flag).

## Constraints
- `0 <= len(nums) <= 10^5`.
- Each `nums[i]` is `0`, `1`, or `2`.

## Examples
Input: `nums = [2,0,2,1,1,0]`
Output: `[0,0,1,1,2,2]`

Input: `nums = [2,0,1]`
Output: `[0,1,2]`

Input: `nums = [0]`
Output: `[0]`
""",
    """def sortColors(nums):
    nums = list(nums)
    lo, mid, hi = 0, 0, len(nums) - 1
    while mid <= hi:
        if nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]
            lo += 1
            mid += 1
        elif nums[mid] == 2:
            nums[mid], nums[hi] = nums[hi], nums[mid]
            hi -= 1
        else:
            mid += 1
    return nums
""",
    visible=[{"nums": [2, 0, 2, 1, 1, 0]}, {"nums": [2, 0, 1]}, {"nums": [0]}],
    hidden=[{"nums": []}, {"nums": [1, 1, 1]}, {"nums": [2, 2, 0, 0, 1, 1]}],
    gen=lambda r: [{"nums": ilist(r, 0, 40, 0, 2)} for _ in range(4)],
    brute=lambda nums: sorted(nums),
    checks=[({"nums": [2, 0, 2, 1, 1, 0]}, [0, 0, 1, 1, 2, 2])])

add("remove-duplicates-sorted-array", "Remove Duplicates From Sorted Array", "easy",
    ["array", "two-pointers"], "removeDuplicates", [("nums", "int[]")], "int[]",
    """
Given a sorted array `nums`, keep only one copy of each value and return **the
resulting sorted array** of unique values (still sorted).

## Constraints
- `0 <= len(nums) <= 10^5`.
- `nums` is sorted in non-decreasing order; `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [1,1,2]`
Output: `[1,2]`

Input: `nums = [0,0,1,1,1,2,2,3,3,4]`
Output: `[0,1,2,3,4]`

Input: `nums = []`
Output: `[]`
""",
    """def removeDuplicates(nums):
    out = []
    for x in nums:
        if not out or out[-1] != x:
            out.append(x)
    return out
""",
    visible=[{"nums": [1, 1, 2]}, {"nums": [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]}, {"nums": []}],
    hidden=[{"nums": [5]}, {"nums": [-2, -2, -2]}, {"nums": [1, 2, 3]}],
    gen=lambda r: [{"nums": sorted(ilist(r, 0, 30, -5, 5))} for _ in range(4)],
    brute=lambda nums: sorted(set(nums)),
    checks=[({"nums": [1, 1, 2]}, [1, 2]),
            ({"nums": [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]}, [0, 1, 2, 3, 4])])

add("rotate-array", "Rotate Array Right", "medium",
    ["array", "math"], "rotateArray", [("nums", "int[]"), ("k", "int")], "int[]",
    """
Given an array `nums` and a non-negative integer `k`, rotate the array to the
**right** by `k` positions and return **the resulting array**. Rotations wrap
around, and `k` may exceed the array length.

## Constraints
- `0 <= len(nums) <= 10^5`, `0 <= k <= 10^9`.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [1,2,3,4,5,6,7], k = 3`
Output: `[5,6,7,1,2,3,4]`

Input: `nums = [-1,-100,3,99], k = 2`
Output: `[3,99,-1,-100]`

Input: `nums = [1], k = 5`
Output: `[1]`
""",
    """def rotateArray(nums, k):
    n = len(nums)
    if n == 0:
        return list(nums)
    k %= n
    return list(nums[n - k:]) + list(nums[:n - k])
""",
    visible=[{"nums": [1, 2, 3, 4, 5, 6, 7], "k": 3},
             {"nums": [-1, -100, 3, 99], "k": 2}, {"nums": [1], "k": 5}],
    hidden=[{"nums": [], "k": 3}, {"nums": [1, 2], "k": 0}, {"nums": [1, 2, 3], "k": 3}],
    gen=lambda r: [{"nums": ilist(r, 0, 20, -9, 9), "k": r.randint(0, 25)} for _ in range(4)],
    brute=lambda nums, k: (lambda a, kk: a[len(a) - kk:] + a[:len(a) - kk] if a else a)(
        list(nums), k % len(nums) if nums else 0),
    checks=[({"nums": [1, 2, 3, 4, 5, 6, 7], "k": 3}, [5, 6, 7, 1, 2, 3, 4])])

add("merge-sorted-arrays", "Merge Sorted Arrays", "easy",
    ["array", "two-pointers"], "mergeSortedArrays",
    [("a", "int[]"), ("b", "int[]")], "int[]",
    """
Given two arrays `a` and `b`, each sorted in non-decreasing order, return **one
sorted array** containing all elements of both (a merged multiset).

## Constraints
- `0 <= len(a), len(b) <= 10^5`.
- `a` and `b` are each sorted non-decreasing; `-10^9 <= values <= 10^9`.

## Examples
Input: `a = [1,2,3], b = [2,5,6]`
Output: `[1,2,2,3,5,6]`

Input: `a = [], b = [1]`
Output: `[1]`

Input: `a = [4], b = []`
Output: `[4]`
""",
    """def mergeSortedArrays(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out
""",
    visible=[{"a": [1, 2, 3], "b": [2, 5, 6]}, {"a": [], "b": [1]}, {"a": [4], "b": []}],
    hidden=[{"a": [], "b": []}, {"a": [-3, 0, 0], "b": [-3, 1]},
            {"a": [1, 1, 1], "b": [1, 1]}],
    gen=lambda r: [{"a": sorted(ilist(r, 0, 20, -9, 9)),
                    "b": sorted(ilist(r, 0, 20, -9, 9))} for _ in range(4)],
    brute=lambda a, b: sorted(list(a) + list(b)),
    checks=[({"a": [1, 2, 3], "b": [2, 5, 6]}, [1, 2, 2, 3, 5, 6])])

add("running-average-stream", "Running Average Stream", "easy",
    ["array", "math", "prefix-sum"], "runningAverage", [("nums", "num[]")], "num[]",
    """
Given a stream of numbers `nums` processed left to right, return **an array whose
`i`-th entry is the average of the first `i+1` numbers**, each rounded to 5
decimal places.

## Constraints
- `0 <= len(nums) <= 10^5`.
- `-10^6 <= nums[i] <= 10^6`.

## Examples
Input: `nums = [2,4,6]`
Output: `[2.0, 3.0, 4.0]`
Explanation: averages of `[2]`, `[2,4]`, `[2,4,6]`.

Input: `nums = [1,2]`
Output: `[1.0, 1.5]`

Input: `nums = []`
Output: `[]`
""",
    """def runningAverage(nums):
    out = []
    s = 0
    for i, x in enumerate(nums):
        s += x
        out.append(round(s / (i + 1), 5))
    return out
""",
    visible=[{"nums": [2, 4, 6]}, {"nums": [1, 2]}, {"nums": []}],
    hidden=[{"nums": [5]}, {"nums": [-2, 2]}, {"nums": [1, 1, 1, 1]}],
    checks=[({"nums": [2, 4, 6]}, [2.0, 3.0, 4.0]), ({"nums": [1, 2]}, [1.0, 1.5])])

add("find-duplicate-number", "Find Duplicate Number", "medium",
    ["array", "two-pointers", "binary-search"], "findDuplicate", [("nums", "int[]")], "int",
    """
Given an array `nums` of `n+1` integers where each value is in the range `[1, n]`,
exactly one value is repeated (possibly more than once). Return **the repeated
value**. Do not modify the array and use only `O(1)` extra space.

## Constraints
- `len(nums) == n + 1` with `n >= 1`; every `nums[i]` is in `[1, n]`.
- Exactly one value is duplicated; it may appear two or more times.

## Examples
Input: `nums = [1,3,4,2,2]`
Output: `2`

Input: `nums = [3,1,3,4,2]`
Output: `3`

Input: `nums = [2,2,2,2,2]`
Output: `2`
""",
    """def findDuplicate(nums):
    slow = fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow
""",
    visible=[{"nums": [1, 3, 4, 2, 2]}, {"nums": [3, 1, 3, 4, 2]}, {"nums": [2, 2, 2, 2, 2]}],
    hidden=[{"nums": [1, 1]}, {"nums": [1, 2, 3, 4, 5, 6, 7, 8, 9, 9]}],
    gen=lambda r: [_lb_dup_case(r) for _ in range(5)],
    brute=lambda nums: next(v for v in nums if nums.count(v) > 1),
    checks=[({"nums": [1, 3, 4, 2, 2]}, 2), ({"nums": [3, 1, 3, 4, 2]}, 3)])

add("first-missing-positive", "First Missing Positive", "hard",
    ["array", "hash-table"], "firstMissingPositive", [("nums", "int[]")], "int",
    """
Given an unsorted integer array `nums`, return **the smallest positive integer
that does not appear** in it. Aim for `O(n)` time and `O(1)` extra space.

## Constraints
- `0 <= len(nums) <= 10^5`.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [1,2,0]`
Output: `3`

Input: `nums = [3,4,-1,1]`
Output: `2`

Input: `nums = [7,8,9,11,12]`
Output: `1`
""",
    """def firstMissingPositive(nums):
    nums = list(nums)
    n = len(nums)
    for i in range(n):
        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
            j = nums[i] - 1
            nums[i], nums[j] = nums[j], nums[i]
    for i in range(n):
        if nums[i] != i + 1:
            return i + 1
    return n + 1
""",
    visible=[{"nums": [1, 2, 0]}, {"nums": [3, 4, -1, 1]}, {"nums": [7, 8, 9, 11, 12]}],
    hidden=[{"nums": []}, {"nums": [1]}, {"nums": [-5, -3]}, {"nums": [2, 2, 2]}],
    gen=lambda r: [{"nums": ilist(r, 0, 30, -5, 30)} for _ in range(5)],
    brute=lambda nums: next(i for i in range(1, len(nums) + 2) if i not in set(nums)),
    checks=[({"nums": [1, 2, 0]}, 3), ({"nums": [3, 4, -1, 1]}, 2)])

add("count-pairs-target-sum", "Count Pairs With Target Sum", "easy",
    ["array", "hash-table"], "countPairs",
    [("nums", "int[]"), ("target", "int")], "int",
    """
Given an integer array `nums` and an integer `target`, return **the number of
index pairs `(i, j)` with `i < j` such that `nums[i] + nums[j] == target`**.
Pairs are counted by position, so repeated values produce multiple pairs.

## Constraints
- `0 <= len(nums) <= 10^5`.
- `-10^9 <= nums[i], target <= 10^9`.

## Examples
Input: `nums = [1,1,1], target = 2`
Output: `3`
Explanation: the pairs `(0,1)`, `(0,2)`, `(1,2)`.

Input: `nums = [1,2,3,4], target = 5`
Output: `2`

Input: `nums = [5,5], target = 9`
Output: `0`
""",
    """def countPairs(nums, target):
    from collections import defaultdict
    seen = defaultdict(int)
    count = 0
    for x in nums:
        count += seen[target - x]
        seen[x] += 1
    return count
""",
    visible=[{"nums": [1, 1, 1], "target": 2}, {"nums": [1, 2, 3, 4], "target": 5},
             {"nums": [5, 5], "target": 9}],
    hidden=[{"nums": [], "target": 0}, {"nums": [0, 0, 0, 0], "target": 0},
            {"nums": [-1, 1, -1, 1], "target": 0}],
    gen=lambda r: [{"nums": ilist(r, 0, 30, -4, 4), "target": r.randint(-6, 6)}
                   for _ in range(5)],
    brute=lambda nums, target: sum(
        1 for i in range(len(nums)) for j in range(i + 1, len(nums))
        if nums[i] + nums[j] == target),
    checks=[({"nums": [1, 1, 1], "target": 2}, 3),
            ({"nums": [1, 2, 3, 4], "target": 5}, 2)])

add("subarray-sum-equals-k", "Subarray Sum Equals K", "medium",
    ["array", "hash-table", "prefix-sum"], "subarraySum",
    [("nums", "int[]"), ("k", "int")], "int",
    """
Given an integer array `nums` and an integer `k`, return **the number of
contiguous subarrays whose elements sum to exactly `k`**.

## Constraints
- `1 <= len(nums) <= 2*10^4`.
- `-1000 <= nums[i] <= 1000`, `-10^7 <= k <= 10^7`.

## Examples
Input: `nums = [1,1,1], k = 2`
Output: `2`

Input: `nums = [1,2,3], k = 3`
Output: `2`

Input: `nums = [-1,-1,1], k = 0`
Output: `1`
""",
    """def subarraySum(nums, k):
    from collections import defaultdict
    seen = defaultdict(int)
    seen[0] = 1
    prefix = count = 0
    for x in nums:
        prefix += x
        count += seen[prefix - k]
        seen[prefix] += 1
    return count
""",
    visible=[{"nums": [1, 1, 1], "k": 2}, {"nums": [1, 2, 3], "k": 3},
             {"nums": [-1, -1, 1], "k": 0}],
    hidden=[{"nums": [0, 0, 0], "k": 0}, {"nums": [3], "k": 3}, {"nums": [1, -1, 1, -1], "k": 0}],
    gen=lambda r: [{"nums": ilist(r, 1, 25, -3, 3), "k": r.randint(-5, 5)} for _ in range(5)],
    brute=lambda nums, k: sum(
        1 for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
        if sum(nums[i:j]) == k),
    checks=[({"nums": [1, 1, 1], "k": 2}, 2), ({"nums": [1, 2, 3], "k": 3}, 2)])

add("minimum-size-subarray-sum", "Minimum Size Subarray Sum", "medium",
    ["array", "two-pointers", "sliding-window"], "minSubArrayLen",
    [("target", "int"), ("nums", "int[]")], "int",
    """
Given an array of **positive** integers `nums` and an integer `target`, return
**the length of the shortest contiguous subarray whose sum is at least
`target`**. If no such subarray exists, return `0`.

## Constraints
- `1 <= len(nums) <= 10^5`, `1 <= target <= 10^9`.
- `1 <= nums[i] <= 10^4`.

## Examples
Input: `target = 7, nums = [2,3,1,2,4,3]`
Output: `2`
Explanation: the subarray `[4,3]` has sum `7` and length `2`.

Input: `target = 4, nums = [1,4,4]`
Output: `1`

Input: `target = 11, nums = [1,1,1,1,1,1,1,1]`
Output: `0`
""",
    """def minSubArrayLen(target, nums):
    left = 0
    total = 0
    best = len(nums) + 1
    for right, x in enumerate(nums):
        total += x
        while total >= target:
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return best if best <= len(nums) else 0
""",
    visible=[{"target": 7, "nums": [2, 3, 1, 2, 4, 3]}, {"target": 4, "nums": [1, 4, 4]},
             {"target": 11, "nums": [1, 1, 1, 1, 1, 1, 1, 1]}],
    hidden=[{"target": 1, "nums": [1]}, {"target": 100, "nums": [1, 2, 3]},
            {"target": 6, "nums": [10]}],
    gen=lambda r: [{"target": r.randint(1, 20), "nums": ilist(r, 1, 20, 1, 6)}
                   for _ in range(5)],
    brute=lambda target, nums: min(
        [j - i for i in range(len(nums)) for j in range(i + 1, len(nums) + 1)
         if sum(nums[i:j]) >= target], default=0),
    checks=[({"target": 7, "nums": [2, 3, 1, 2, 4, 3]}, 2),
            ({"target": 4, "nums": [1, 4, 4]}, 1)])

# ---- Wave 2: stacks, greedy, intervals, math -------------------------------

def _lb_intervals(r):
    out = []
    for _ in range(r.randint(0, 8)):
        a = r.randint(0, 20)
        out.append([a, a + r.randint(1, 10)])
    return out


def _lb_brute_rooms(intervals):
    events = []
    for s, e in intervals:
        events.append((s, 1))
        events.append((e, -1))
    events.sort()
    cur = best = 0
    for _, d in events:
        cur += d
        best = max(best, cur)
    return best


def _lb_brute_compress(chars):
    from itertools import groupby
    out = []
    for ch, grp in groupby(chars):
        n = len(list(grp))
        out.append(ch)
        if n > 1:
            out.append(str(n))
    return "".join(out)


def _lb_brute_candy(ratings):
    n = len(ratings)
    candies = [1] * n
    changed = True
    while changed:
        changed = False
        for i in range(n):
            if i > 0 and ratings[i] > ratings[i - 1] and candies[i] <= candies[i - 1]:
                candies[i] = candies[i - 1] + 1
                changed = True
            if i < n - 1 and ratings[i] > ratings[i + 1] and candies[i] <= candies[i + 1]:
                candies[i] = candies[i + 1] + 1
                changed = True
    return sum(candies)


def _lb_brute_least(tasks, n):
    import heapq
    from collections import Counter, deque
    heap = [-v for v in Counter(tasks).values()]
    heapq.heapify(heap)
    cooldown = deque()
    time = 0
    while heap or cooldown:
        time += 1
        if cooldown and cooldown[0][0] == time:
            heapq.heappush(heap, cooldown.popleft()[1])
        if heap:
            c = heapq.heappop(heap) + 1
            if c < 0:
                cooldown.append((time + n + 1, c))
    return time


add("daily-temperatures", "Daily Temperatures", "medium",
    ["array", "stack", "monotonic-stack"], "dailyTemperatures",
    [("temperatures", "int[]")], "int[]",
    """
Given an array `temperatures`, return **an array `answer` where `answer[i]` is the
number of days you must wait after day `i` to get a warmer temperature**. If no
warmer day exists, `answer[i] = 0`.

## Constraints
- `1 <= len(temperatures) <= 10^5`.
- `-50 <= temperatures[i] <= 150`.

## Examples
Input: `temperatures = [73,74,75,71,69,72,76,73]`
Output: `[1,1,4,2,1,1,0,0]`

Input: `temperatures = [30,40,50,60]`
Output: `[1,1,1,0]`

Input: `temperatures = [30,30,30]`
Output: `[0,0,0]`
""",
    """def dailyTemperatures(temperatures):
    answer = [0] * len(temperatures)
    stack = []
    for i, t in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < t:
            j = stack.pop()
            answer[j] = i - j
        stack.append(i)
    return answer
""",
    visible=[{"temperatures": [73, 74, 75, 71, 69, 72, 76, 73]},
             {"temperatures": [30, 40, 50, 60]}, {"temperatures": [30, 30, 30]}],
    hidden=[{"temperatures": [50]}, {"temperatures": [90, 80, 70]},
            {"temperatures": [70, 80, 70, 80, 70]}],
    gen=lambda r: [{"temperatures": ilist(r, 1, 30, -5, 5)} for _ in range(5)],
    brute=lambda temperatures: [
        next((j - i for j in range(i + 1, len(temperatures))
              if temperatures[j] > temperatures[i]), 0)
        for i in range(len(temperatures))],
    checks=[({"temperatures": [73, 74, 75, 71, 69, 72, 76, 73]}, [1, 1, 4, 2, 1, 1, 0, 0])])

add("evaluate-reverse-polish-notation", "Evaluate Reverse Polish Notation", "medium",
    ["stack", "math"], "evalRPN", [("tokens", "string[]")], "int",
    """
Given `tokens` representing an arithmetic expression in Reverse Polish Notation,
evaluate it and return **the integer result**. Valid operators are `+`, `-`, `*`,
`/`; division truncates toward zero. Each operand and intermediate result fits in
a signed 64-bit integer.

## Constraints
- `1 <= len(tokens) <= 10^4`.
- Each token is an operator or an integer in `[-2*10^4, 2*10^4]`.
- The expression is always valid.

## Examples
Input: `tokens = ["2","1","+","3","*"]`
Output: `9`
Explanation: `((2 + 1) * 3) = 9`.

Input: `tokens = ["4","13","5","/","+"]`
Output: `6`
Explanation: `(4 + (13 / 5)) = 6`.

Input: `tokens = ["10","6","9","3","+","-11","*","/","*","17","+","5","+"]`
Output: `22`
""",
    """def evalRPN(tokens):
    stack = []
    ops = {"+", "-", "*", "/"}
    for t in tokens:
        if t in ops:
            b = stack.pop()
            a = stack.pop()
            if t == "+":
                stack.append(a + b)
            elif t == "-":
                stack.append(a - b)
            elif t == "*":
                stack.append(a * b)
            else:
                stack.append(int(a / b))
        else:
            stack.append(int(t))
    return stack[0]
""",
    visible=[{"tokens": ["2", "1", "+", "3", "*"]},
             {"tokens": ["4", "13", "5", "/", "+"]},
             {"tokens": ["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]}],
    hidden=[{"tokens": ["5"]}, {"tokens": ["7", "2", "-"]}, {"tokens": ["6", "-4", "/"]}],
    checks=[({"tokens": ["2", "1", "+", "3", "*"]}, 9),
            ({"tokens": ["4", "13", "5", "/", "+"]}, 6),
            ({"tokens": ["6", "-4", "/"]}, -1)])

add("largest-rectangle-in-histogram", "Largest Rectangle in Histogram", "hard",
    ["array", "stack", "monotonic-stack"], "largestRectangleArea",
    [("heights", "int[]")], "int",
    """
Given an array `heights` of non-negative bar heights (each bar has width 1),
return **the area of the largest rectangle** that fits entirely under the
histogram using contiguous bars.

## Constraints
- `0 <= len(heights) <= 10^5`.
- `0 <= heights[i] <= 10^4`.

## Examples
Input: `heights = [2,1,5,6,2,3]`
Output: `10`
Explanation: bars `5,6` give `2 * 5 = 10`.

Input: `heights = [2,4]`
Output: `4`

Input: `heights = [1,1,1,1]`
Output: `4`
""",
    """def largestRectangleArea(heights):
    stack = []
    best = 0
    for i in range(len(heights) + 1):
        h = heights[i] if i < len(heights) else 0
        while stack and heights[stack[-1]] >= h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            best = max(best, height * width)
        stack.append(i)
    return best
""",
    visible=[{"heights": [2, 1, 5, 6, 2, 3]}, {"heights": [2, 4]}, {"heights": [1, 1, 1, 1]}],
    hidden=[{"heights": []}, {"heights": [0]}, {"heights": [5]}, {"heights": [3, 1, 3]}],
    gen=lambda r: [{"heights": ilist(r, 0, 25, 0, 9)} for _ in range(6)],
    brute=lambda heights: max(
        [min(heights[i:j + 1]) * (j - i + 1)
         for i in range(len(heights)) for j in range(i, len(heights))], default=0),
    checks=[({"heights": [2, 1, 5, 6, 2, 3]}, 10), ({"heights": [2, 4]}, 4)])

add("sliding-window-maximum", "Sliding Window Maximum", "hard",
    ["array", "sliding-window", "monotonic-queue"], "maxSlidingWindow",
    [("nums", "int[]"), ("k", "int")], "int[]",
    """
Given an array `nums` and a window size `k`, return **an array of the maximum
value in each contiguous window of length `k`**, from left to right.

## Constraints
- `1 <= k <= len(nums) <= 10^5`.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [1,3,-1,-3,5,3,6,7], k = 3`
Output: `[3,3,5,5,6,7]`

Input: `nums = [9,11], k = 2`
Output: `[11]`

Input: `nums = [4,-2], k = 1`
Output: `[4,-2]`
""",
    """def maxSlidingWindow(nums, k):
    from collections import deque
    dq = deque()
    out = []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
""",
    visible=[{"nums": [1, 3, -1, -3, 5, 3, 6, 7], "k": 3}, {"nums": [9, 11], "k": 2},
             {"nums": [4, -2], "k": 1}],
    hidden=[{"nums": [1], "k": 1}, {"nums": [7, 6, 5, 4], "k": 2},
            {"nums": [1, 1, 1], "k": 3}],
    gen=lambda r: [(lambda a: {"nums": a, "k": r.randint(1, len(a))})(ilist(r, 1, 20, -9, 9))
                   for _ in range(6)],
    brute=lambda nums, k: [max(nums[i:i + k]) for i in range(len(nums) - k + 1)],
    checks=[({"nums": [1, 3, -1, -3, 5, 3, 6, 7], "k": 3}, [3, 3, 5, 5, 6, 7])])

add("next-permutation", "Next Permutation", "medium",
    ["array", "two-pointers"], "nextPermutation", [("nums", "int[]")], "int[]",
    """
Given an array `nums`, rearrange it into **the next lexicographically greater
permutation of its elements** and return the result. If no greater permutation
exists (the array is in descending order), return the smallest permutation
(ascending order). Use `O(1)` extra space.

## Constraints
- `1 <= len(nums) <= 10^4`.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [1,2,3]`
Output: `[1,3,2]`

Input: `nums = [3,2,1]`
Output: `[1,2,3]`

Input: `nums = [1,1,5]`
Output: `[1,5,1]`
""",
    """def nextPermutation(nums):
    nums = list(nums)
    n = len(nums)
    i = n - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    if i >= 0:
        j = n - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1:] = reversed(nums[i + 1:])
    return nums
""",
    visible=[{"nums": [1, 2, 3]}, {"nums": [3, 2, 1]}, {"nums": [1, 1, 5]}],
    hidden=[{"nums": [1]}, {"nums": [2, 3, 1]}, {"nums": [1, 3, 2]}],
    gen=lambda r: [{"nums": r.sample(range(1, 8), r.randint(1, 6))} for _ in range(6)],
    brute=lambda nums: (lambda perms: list(perms[(perms.index(tuple(nums)) + 1) % len(perms)]))(
        sorted(set(__import__("itertools").permutations(nums)))),
    checks=[({"nums": [1, 2, 3]}, [1, 3, 2]), ({"nums": [3, 2, 1]}, [1, 2, 3])])

add("string-compression", "String Compression", "easy",
    ["string", "two-pointers"], "compress", [("chars", "string")], "string",
    """
Given a string `chars`, compress it by replacing each maximal run of a repeated
character with that character followed by the run length **when the run length is
greater than 1**. Return **the compressed string**. A run of length 1 is written
as just the character.

## Constraints
- `0 <= len(chars) <= 10^5`, lowercase/uppercase letters and digits.

## Examples
Input: `chars = "aabbccc"`
Output: `"a2b2c3"`

Input: `chars = "abc"`
Output: `"abc"`

Input: `chars = "aaa"`
Output: `"a3"`
""",
    """def compress(chars):
    out = []
    i = 0
    n = len(chars)
    while i < n:
        j = i
        while j < n and chars[j] == chars[i]:
            j += 1
        out.append(chars[i])
        if j - i > 1:
            out.append(str(j - i))
        i = j
    return "".join(out)
""",
    visible=[{"chars": "aabbccc"}, {"chars": "abc"}, {"chars": "aaa"}],
    hidden=[{"chars": ""}, {"chars": "a"}, {"chars": "aabaa"}],
    gen=lambda r: [{"chars": sstr(r, 0, 25, "aab")} for _ in range(6)],
    brute=_lb_brute_compress,
    checks=[({"chars": "aabbccc"}, "a2b2c3"), ({"chars": "abc"}, "abc")])

add("pow-function", "Pow Function", "medium",
    ["math", "recursion"], "myPow", [("x", "num"), ("n", "int")], "num",
    """
Given a floating-point number `x` and an integer `n` (possibly negative), compute
`x` raised to the power `n` and return the result **rounded to 6 decimal places**.
Aim for `O(log n)` multiplications (fast exponentiation).

## Constraints
- `-30.0 <= x <= 30.0`, `-30 <= n <= 30`.
- `x != 0` when `n < 0`.

## Examples
Input: `x = 2.0, n = 10`
Output: `1024.0`

Input: `x = 2.1, n = 3`
Output: `9.261`

Input: `x = 2.0, n = -2`
Output: `0.25`
""",
    """def myPow(x, n):
    if n < 0:
        x = 1 / x
        n = -n
    result = 1.0
    base = x
    while n:
        if n & 1:
            result *= base
        base *= base
        n >>= 1
    return round(result, 6)
""",
    visible=[{"x": 2.0, "n": 10}, {"x": 2.1, "n": 3}, {"x": 2.0, "n": -2}],
    hidden=[{"x": 5.0, "n": 0}, {"x": 1.0, "n": 30}, {"x": -2.0, "n": 3}, {"x": 3.0, "n": -1}],
    checks=[({"x": 2.0, "n": 10}, 1024.0), ({"x": 2.0, "n": -2}, 0.25),
            ({"x": -2.0, "n": 3}, -8.0)])

add("integer-square-root", "Integer Square Root", "easy",
    ["math", "binary-search"], "mySqrt", [("x", "int")], "int",
    """
Given a non-negative integer `x`, return **`floor(sqrt(x))`** — the largest
integer `r` with `r*r <= x`. Do not use any floating-point square-root function.

## Constraints
- `0 <= x <= 2^31 - 1`.

## Examples
Input: `x = 4`
Output: `2`

Input: `x = 8`
Output: `2`
Explanation: `sqrt(8) ≈ 2.828`, floor is `2`.

Input: `x = 0`
Output: `0`
""",
    """def mySqrt(x):
    if x < 2:
        return x
    lo, hi = 1, x
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid * mid <= x:
            lo = mid + 1
        else:
            hi = mid - 1
    return hi
""",
    visible=[{"x": 4}, {"x": 8}, {"x": 0}],
    hidden=[{"x": 1}, {"x": 2}, {"x": 2147395600}, {"x": 2147483647}],
    gen=lambda r: [{"x": r.randint(0, 10 ** 6)} for _ in range(6)],
    brute=lambda x: int(__import__("math").isqrt(x)),
    checks=[({"x": 4}, 2), ({"x": 8}, 2), ({"x": 2147395600}, 46340)])

add("candy-distribution", "Candy Distribution", "hard",
    ["array", "greedy"], "candy", [("ratings", "int[]")], "int",
    """
Each child stands in a line with an integer rating. Distribute candies so that
every child gets at least one candy and any child with a strictly higher rating
than an adjacent neighbor gets strictly more candies than that neighbor. Return
**the minimum total number of candies** required.

## Constraints
- `1 <= len(ratings) <= 2*10^4`.
- `0 <= ratings[i] <= 10^9`.

## Examples
Input: `ratings = [1,0,2]`
Output: `5`
Explanation: candies `[2,1,2]`.

Input: `ratings = [1,2,2]`
Output: `4`
Explanation: candies `[1,2,1]`.

Input: `ratings = [1,3,2,2,1]`
Output: `7`
""",
    """def candy(ratings):
    n = len(ratings)
    candies = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            candies[i] = candies[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            candies[i] = max(candies[i], candies[i + 1] + 1)
    return sum(candies)
""",
    visible=[{"ratings": [1, 0, 2]}, {"ratings": [1, 2, 2]}, {"ratings": [1, 3, 2, 2, 1]}],
    hidden=[{"ratings": [1]}, {"ratings": [1, 2, 3, 4]}, {"ratings": [5, 4, 3, 2, 1]}],
    gen=lambda r: [{"ratings": ilist(r, 1, 12, 1, 4)} for _ in range(6)],
    brute=_lb_brute_candy,
    checks=[({"ratings": [1, 0, 2]}, 5), ({"ratings": [1, 2, 2]}, 4)])

add("task-scheduler-cooldown", "Task Scheduler With Cooldown", "medium",
    ["array", "greedy", "hash-table"], "leastInterval",
    [("tasks", "string[]"), ("n", "int")], "int",
    """
Given a list of `tasks` (each a single uppercase letter) and a cooldown `n`, each
task takes one unit of time and two runs of the **same** task must be separated by
at least `n` idle/other units. Return **the minimum number of time units** needed
to finish all tasks.

## Constraints
- `1 <= len(tasks) <= 10^4`, each task is `A`–`Z`.
- `0 <= n <= 100`.

## Examples
Input: `tasks = ["A","A","A","B","B","B"], n = 2`
Output: `8`
Explanation: `A B idle A B idle A B`.

Input: `tasks = ["A","A","A","B","B","B"], n = 0`
Output: `6`

Input: `tasks = ["A","B","C","D"], n = 2`
Output: `4`
""",
    """def leastInterval(tasks, n):
    from collections import Counter
    counts = Counter(tasks)
    mx = max(counts.values())
    num_max = sum(1 for v in counts.values() if v == mx)
    return max(len(tasks), (mx - 1) * (n + 1) + num_max)
""",
    visible=[{"tasks": ["A", "A", "A", "B", "B", "B"], "n": 2},
             {"tasks": ["A", "A", "A", "B", "B", "B"], "n": 0},
             {"tasks": ["A", "B", "C", "D"], "n": 2}],
    hidden=[{"tasks": ["A"], "n": 5}, {"tasks": ["A", "A", "A"], "n": 2},
            {"tasks": ["A", "A", "B", "B"], "n": 1}],
    gen=lambda r: [{"tasks": [r.choice("ABCD") for _ in range(r.randint(1, 15))],
                    "n": r.randint(0, 3)} for _ in range(6)],
    brute=_lb_brute_least,
    checks=[({"tasks": ["A", "A", "A", "B", "B", "B"], "n": 2}, 8),
            ({"tasks": ["A", "B", "C", "D"], "n": 2}, 4)])

add("meeting-rooms-required", "Meeting Rooms Required", "medium",
    ["intervals", "sorting", "heap"], "minMeetingRooms", [("intervals", "int[][]")], "int",
    """
Given meeting time intervals `[start, end)` (half-open), return **the minimum
number of rooms** required so that no two meetings sharing a room overlap. A
meeting ending exactly when another starts can reuse the room.

## Constraints
- `0 <= len(intervals) <= 10^4`.
- `0 <= start < end <= 10^9`.

## Examples
Input: `intervals = [[0,30],[5,10],[15,20]]`
Output: `2`

Input: `intervals = [[7,10],[2,4]]`
Output: `1`

Input: `intervals = [[1,5],[5,9],[9,12]]`
Output: `1`
""",
    """def minMeetingRooms(intervals):
    starts = sorted(s for s, _ in intervals)
    ends = sorted(e for _, e in intervals)
    rooms = best = 0
    j = 0
    for s in starts:
        while j < len(ends) and ends[j] <= s:
            j += 1
            rooms -= 1
        rooms += 1
        best = max(best, rooms)
    return best
""",
    visible=[{"intervals": [[0, 30], [5, 10], [15, 20]]}, {"intervals": [[7, 10], [2, 4]]},
             {"intervals": [[1, 5], [5, 9], [9, 12]]}],
    hidden=[{"intervals": []}, {"intervals": [[1, 2]]},
            {"intervals": [[1, 10], [2, 7], [3, 19], [8, 12], [10, 20], [11, 30]]}],
    gen=lambda r: [{"intervals": _lb_intervals(r)} for _ in range(6)],
    brute=_lb_brute_rooms,
    checks=[({"intervals": [[0, 30], [5, 10], [15, 20]]}, 2),
            ({"intervals": [[7, 10], [2, 4]]}, 1)])

add("employee-free-time", "Employee Free Time", "hard",
    ["intervals", "sorting"], "employeeFreeTime", [("schedule", "int[][][]")], "int[][]",
    """
Each employee has a list of non-overlapping working intervals `[start, end]`,
sorted by start. Return **the finite intervals of time, sorted, during which every
employee is free** (the common gaps between the union of all working intervals).
Return them as a list of `[start, end]`.

## Constraints
- `1 <= number of employees <= 100`; each has `1` to `100` intervals.
- `0 <= start < end <= 10^9`.

## Examples
Input: `schedule = [[[1,2],[5,6]],[[1,3]],[[4,10]]]`
Output: `[[3,4]]`
Explanation: union of work is `[1,3],[4,10]`; the only common gap is `[3,4]`.

Input: `schedule = [[[1,3],[6,7]],[[2,4]],[[2,5],[9,12]]]`
Output: `[[5,6],[7,9]]`

Input: `schedule = [[[1,4]],[[2,3]]]`
Output: `[]`
""",
    """def employeeFreeTime(schedule):
    intervals = sorted([s, e] for emp in schedule for s, e in emp)
    free = []
    end = intervals[0][1]
    for s, e in intervals[1:]:
        if s > end:
            free.append([end, s])
        end = max(end, e)
    return free
""",
    visible=[{"schedule": [[[1, 2], [5, 6]], [[1, 3]], [[4, 10]]]},
             {"schedule": [[[1, 3], [6, 7]], [[2, 4]], [[2, 5], [9, 12]]]},
             {"schedule": [[[1, 4]], [[2, 3]]]}],
    hidden=[{"schedule": [[[1, 10]]]}, {"schedule": [[[1, 2]], [[3, 4]]]},
            {"schedule": [[[1, 2], [3, 4]], [[5, 6]]]}],
    checks=[({"schedule": [[[1, 2], [5, 6]], [[1, 3]], [[4, 10]]]}, [[3, 4]]),
            ({"schedule": [[[1, 4]], [[2, 3]]]}, [])])

# ---- Wave 3: dynamic programming & string decoding -------------------------

def _lb_brute_edit(word1, word2):
    from functools import lru_cache

    @lru_cache(None)
    def f(i, j):
        if i == len(word1):
            return len(word2) - j
        if j == len(word2):
            return len(word1) - i
        if word1[i] == word2[j]:
            return f(i + 1, j + 1)
        return 1 + min(f(i + 1, j), f(i, j + 1), f(i + 1, j + 1))

    return f(0, 0)


def _lb_brute_change(amount, coins):
    from functools import lru_cache
    coins = tuple(sorted(coins))

    @lru_cache(None)
    def f(i, rem):
        if rem == 0:
            return 1
        if i == len(coins) or rem < 0:
            return 0
        return f(i + 1, rem) + f(i, rem - coins[i])

    return f(0, amount)


def _lb_brute_can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    reach = {0}
    for x in nums:
        reach |= {r + x for r in reach}
    return (total // 2) in reach


def _lb_brute_can_sum(nums, target):
    reach = {0}
    for x in nums:
        reach |= {r + x for r in reach}
    return target in reach


def _lb_brute_knapsack(values, weights, capacity):
    n = len(values)
    best = 0
    for mask in range(1 << n):
        w = sum(weights[i] for i in range(n) if mask >> i & 1)
        if w <= capacity:
            best = max(best, sum(values[i] for i in range(n) if mask >> i & 1))
    return best


def _lb_brute_minpath(grid):
    from functools import lru_cache
    m, n = len(grid), len(grid[0])

    @lru_cache(None)
    def f(i, j):
        if i == m - 1 and j == n - 1:
            return grid[i][j]
        best = float("inf")
        if i + 1 < m:
            best = min(best, f(i + 1, j))
        if j + 1 < n:
            best = min(best, f(i, j + 1))
        return grid[i][j] + best

    return f(0, 0)


def _lb_knapsack_case(r):
    n = r.randint(0, 8)
    return {"values": [r.randint(1, 20) for _ in range(n)],
            "weights": [r.randint(1, 10) for _ in range(n)],
            "capacity": r.randint(0, 25)}


def _lb_grid_case(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    return {"grid": [[r.randint(0, 9) for _ in range(n)] for _ in range(m)]}


add("edit-distance", "Edit Distance", "medium",
    ["string", "dynamic-programming"], "minDistance",
    [("word1", "string"), ("word2", "string")], "int",
    """
Given two strings `word1` and `word2`, return **the minimum number of single-
character insertions, deletions, and substitutions** needed to transform `word1`
into `word2` (the Levenshtein distance).

## Constraints
- `0 <= len(word1), len(word2) <= 500`.
- Strings contain lowercase English letters.

## Examples
Input: `word1 = "horse", word2 = "ros"`
Output: `3`
Explanation: horse → rorse → rose → ros.

Input: `word1 = "intention", word2 = "execution"`
Output: `5`

Input: `word1 = "", word2 = "abc"`
Output: `3`
""",
    """def minDistance(word1, word2):
    m, n = len(word1), len(word2)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[n]
""",
    visible=[{"word1": "horse", "word2": "ros"},
             {"word1": "intention", "word2": "execution"},
             {"word1": "", "word2": "abc"}],
    hidden=[{"word1": "", "word2": ""}, {"word1": "abc", "word2": "abc"},
            {"word1": "a", "word2": "b"}],
    gen=lambda r: [{"word1": sstr(r, 0, 6, "ab"), "word2": sstr(r, 0, 6, "ab")}
                   for _ in range(6)],
    brute=_lb_brute_edit,
    checks=[({"word1": "horse", "word2": "ros"}, 3),
            ({"word1": "intention", "word2": "execution"}, 5)])

add("coin-change-ways", "Coin Change Number of Ways", "medium",
    ["dynamic-programming", "array"], "change",
    [("amount", "int"), ("coins", "int[]")], "int",
    """
Given an integer `amount` and a list of distinct positive coin denominations
`coins` (unlimited supply of each), return **the number of distinct combinations
of coins that sum to `amount`**. Combinations are unordered, so `1+2` and `2+1`
count once.

## Constraints
- `0 <= amount <= 5000`, `1 <= len(coins) <= 300`.
- `1 <= coins[i] <= 5000`, all distinct.

## Examples
Input: `amount = 5, coins = [1,2,5]`
Output: `4`
Explanation: `5`, `2+2+1`, `2+1+1+1`, `1+1+1+1+1`.

Input: `amount = 3, coins = [2]`
Output: `0`

Input: `amount = 0, coins = [7]`
Output: `1`
Explanation: the empty combination.
""",
    """def change(amount, coins):
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for x in range(c, amount + 1):
            dp[x] += dp[x - c]
    return dp[amount]
""",
    visible=[{"amount": 5, "coins": [1, 2, 5]}, {"amount": 3, "coins": [2]},
             {"amount": 0, "coins": [7]}],
    hidden=[{"amount": 10, "coins": [10]}, {"amount": 7, "coins": [2, 4]},
            {"amount": 4, "coins": [1, 2, 3]}],
    gen=lambda r: [{"amount": r.randint(0, 15), "coins": r.sample(range(1, 8), r.randint(1, 4))}
                   for _ in range(6)],
    brute=_lb_brute_change,
    checks=[({"amount": 5, "coins": [1, 2, 5]}, 4), ({"amount": 3, "coins": [2]}, 0)])

add("partition-equal-subset-sum", "Partition Equal Subset Sum", "medium",
    ["dynamic-programming", "array"], "canPartition", [("nums", "int[]")], "bool",
    """
Given an array of positive integers `nums`, return **`true` if it can be split
into two subsets with equal sum**, and `false` otherwise.

## Constraints
- `1 <= len(nums) <= 200`.
- `1 <= nums[i] <= 100`.

## Examples
Input: `nums = [1,5,11,5]`
Output: `true`
Explanation: `[1,5,5]` and `[11]`.

Input: `nums = [1,2,3,5]`
Output: `false`

Input: `nums = [2,2]`
Output: `true`
""",
    """def canPartition(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    bits = 1
    for x in nums:
        bits |= bits << x
    return bool((bits >> target) & 1)
""",
    visible=[{"nums": [1, 5, 11, 5]}, {"nums": [1, 2, 3, 5]}, {"nums": [2, 2]}],
    hidden=[{"nums": [1]}, {"nums": [1, 1]}, {"nums": [3, 3, 3, 4, 5]}],
    gen=lambda r: [{"nums": ilist(r, 1, 10, 1, 8)} for _ in range(6)],
    brute=_lb_brute_can_partition,
    checks=[({"nums": [1, 5, 11, 5]}, True), ({"nums": [1, 2, 3, 5]}, False)])

add("subset-sum-feasibility", "Subset Sum Feasibility", "medium",
    ["dynamic-programming", "array"], "canSum",
    [("nums", "int[]"), ("target", "int")], "bool",
    """
Given an array of non-negative integers `nums` and a non-negative `target`,
return **`true` if some subset of `nums` sums to exactly `target`** (the empty
subset sums to `0`).

## Constraints
- `0 <= len(nums) <= 200`, `0 <= target <= 2*10^4`.
- `0 <= nums[i] <= 1000`.

## Examples
Input: `nums = [3,34,4,12,5,2], target = 9`
Output: `true`
Explanation: `4 + 5 = 9`.

Input: `nums = [3,34,4,12,5,2], target = 30`
Output: `false`

Input: `nums = [1,2,3], target = 0`
Output: `true`
""",
    """def canSum(nums, target):
    if target < 0:
        return False
    bits = 1
    for x in nums:
        bits |= bits << x
    return bool((bits >> target) & 1)
""",
    visible=[{"nums": [3, 34, 4, 12, 5, 2], "target": 9},
             {"nums": [3, 34, 4, 12, 5, 2], "target": 30},
             {"nums": [1, 2, 3], "target": 0}],
    hidden=[{"nums": [], "target": 0}, {"nums": [], "target": 5},
            {"nums": [7], "target": 7}],
    gen=lambda r: [{"nums": ilist(r, 0, 8, 0, 6), "target": r.randint(0, 20)}
                   for _ in range(6)],
    brute=_lb_brute_can_sum,
    checks=[({"nums": [3, 34, 4, 12, 5, 2], "target": 9}, True),
            ({"nums": [1, 2, 3], "target": 0}, True)])

add("knapsack-01", "0-1 Knapsack Maximum Value", "medium",
    ["dynamic-programming", "array"], "knapsack",
    [("values", "int[]"), ("weights", "int[]"), ("capacity", "int")], "int",
    """
Given items with `values[i]` and `weights[i]`, and a knapsack `capacity`, choose a
subset of items (each used at most once) whose total weight does not exceed
`capacity`. Return **the maximum total value** achievable.

## Constraints
- `0 <= len(values) == len(weights) <= 1000`, `0 <= capacity <= 10^4`.
- `0 <= values[i] <= 10^4`, `0 <= weights[i] <= 10^4`.

## Examples
Input: `values = [60,100,120], weights = [10,20,30], capacity = 50`
Output: `220`
Explanation: take items 2 and 3 (weight `50`, value `220`).

Input: `values = [1,2,3], weights = [4,5,6], capacity = 3`
Output: `0`

Input: `values = [10], weights = [5], capacity = 5`
Output: `10`
""",
    """def knapsack(values, weights, capacity):
    dp = [0] * (capacity + 1)
    for v, w in zip(values, weights):
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]
""",
    visible=[{"values": [60, 100, 120], "weights": [10, 20, 30], "capacity": 50},
             {"values": [1, 2, 3], "weights": [4, 5, 6], "capacity": 3},
             {"values": [10], "weights": [5], "capacity": 5}],
    hidden=[{"values": [], "weights": [], "capacity": 10},
            {"values": [5, 4, 3], "weights": [1, 1, 1], "capacity": 2},
            {"values": [2, 2], "weights": [3, 3], "capacity": 2}],
    gen=lambda r: [_lb_knapsack_case(r) for _ in range(6)],
    brute=_lb_brute_knapsack,
    checks=[({"values": [60, 100, 120], "weights": [10, 20, 30], "capacity": 50}, 220)])

add("minimum-path-sum-in-grid", "Minimum Path Sum in Grid", "medium",
    ["dynamic-programming", "matrix"], "minPathSum", [("grid", "int[][]")], "int",
    """
Given an `m x n` grid of non-negative numbers, find a path from the top-left cell
to the bottom-right cell that minimizes the sum of the numbers along it. You may
only move **right** or **down**. Return **the minimum path sum**.

## Constraints
- `1 <= m, n <= 200`.
- `0 <= grid[i][j] <= 1000`.

## Examples
Input: `grid = [[1,3,1],[1,5,1],[4,2,1]]`
Output: `7`
Explanation: path `1→3→1→1→1`.

Input: `grid = [[1,2,3],[4,5,6]]`
Output: `12`

Input: `grid = [[5]]`
Output: `5`
""",
    """def minPathSum(grid):
    m, n = len(grid), len(grid[0])
    dp = [0] * n
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                dp[j] = grid[i][j]
            elif i == 0:
                dp[j] = dp[j - 1] + grid[i][j]
            elif j == 0:
                dp[j] = dp[j] + grid[i][j]
            else:
                dp[j] = min(dp[j], dp[j - 1]) + grid[i][j]
    return dp[n - 1]
""",
    visible=[{"grid": [[1, 3, 1], [1, 5, 1], [4, 2, 1]]}, {"grid": [[1, 2, 3], [4, 5, 6]]},
             {"grid": [[5]]}],
    hidden=[{"grid": [[1]]}, {"grid": [[1, 2, 3]]}, {"grid": [[1], [2], [3]]}],
    gen=lambda r: [_lb_grid_case(r) for _ in range(6)],
    brute=_lb_brute_minpath,
    checks=[({"grid": [[1, 3, 1], [1, 5, 1], [4, 2, 1]]}, 7),
            ({"grid": [[1, 2, 3], [4, 5, 6]]}, 12)])

add("decode-encoded-string", "Decode Encoded String", "medium",
    ["string", "stack"], "decodeString", [("s", "string")], "string",
    """
Given an encoded string `s` using the rule `k[encoded]` (the bracketed part is
repeated `k` times, and encodings may be nested), return **the decoded string**.

## Constraints
- `1 <= len(s) <= 3*10^4`; decoded length fits comfortably in memory.
- `s` contains lowercase letters, digits, and the brackets `[` `]`.
- Digits only appear as repeat counts `k` with `1 <= k <= 300`.

## Examples
Input: `s = "3[a]2[bc]"`
Output: `"aaabcbc"`

Input: `s = "3[a2[c]]"`
Output: `"accaccacc"`

Input: `s = "2[abc]3[cd]ef"`
Output: `"abcabccdcdcdef"`
""",
    """def decodeString(s):
    stack = []
    cur = ""
    num = 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == "[":
            stack.append((cur, num))
            cur = ""
            num = 0
        elif ch == "]":
            prev, k = stack.pop()
            cur = prev + cur * k
        else:
            cur += ch
    return cur
""",
    visible=[{"s": "3[a]2[bc]"}, {"s": "3[a2[c]]"}, {"s": "2[abc]3[cd]ef"}],
    hidden=[{"s": "abc"}, {"s": "1[x]"}, {"s": "2[2[a]b]"}],
    checks=[({"s": "3[a]2[bc]"}, "aaabcbc"), ({"s": "3[a2[c]]"}, "accaccacc"),
            ({"s": "2[2[a]b]"}, "aabaab")])

# ---- Wave 4: binary search & heaps -----------------------------------------

def _lb_mountain(r):
    left = sorted(r.sample(range(0, 40), r.randint(0, 4)))
    right = sorted(r.sample(range(0, 40), r.randint(0, 4)), reverse=True)
    return {"nums": left + [50] + right}


def _lb_points_case(r):
    pts, seen = [], set()
    for _ in range(r.randint(1, 10)):
        x, y = r.randint(-9, 9), r.randint(-9, 9)
        d = x * x + y * y
        if d not in seen:
            seen.add(d)
            pts.append([x, y])
    return {"points": pts, "k": r.randint(1, len(pts))}


def _lb_median_case(r):
    a, b = sorted(ilist(r, 0, 8, -9, 9)), sorted(ilist(r, 0, 8, -9, 9))
    if not a and not b:
        a = [r.randint(-9, 9)]
    return {"nums1": a, "nums2": b}


def _lb_range_case(r):
    k = r.randint(1, 4)
    return {"lists": [sorted(r.randint(-9, 9) for _ in range(r.randint(1, 4)))
                      for _ in range(k)]}


def _lb_brute_range(lists):
    from itertools import product
    best = None
    for combo in product(*lists):
        lo, hi = min(combo), max(combo)
        cand = (hi - lo, lo, hi)
        if best is None or cand < best:
            best = cand
    return [best[1], best[2]]


add("binary-search-insert-position", "Binary Search Insert Position", "easy",
    ["array", "binary-search"], "searchInsert",
    [("nums", "int[]"), ("target", "int")], "int",
    """
Given a sorted array of distinct integers `nums` and a `target`, return **the
index where `target` is found**, or **the index where it should be inserted** to
keep the array sorted. Aim for `O(log n)`.

## Constraints
- `0 <= len(nums) <= 10^5`, sorted ascending with distinct values.
- `-10^9 <= nums[i], target <= 10^9`.

## Examples
Input: `nums = [1,3,5,6], target = 5`
Output: `2`

Input: `nums = [1,3,5,6], target = 2`
Output: `1`

Input: `nums = [1,3,5,6], target = 7`
Output: `4`
""",
    """def searchInsert(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
""",
    visible=[{"nums": [1, 3, 5, 6], "target": 5}, {"nums": [1, 3, 5, 6], "target": 2},
             {"nums": [1, 3, 5, 6], "target": 7}],
    hidden=[{"nums": [], "target": 0}, {"nums": [1, 3, 5, 6], "target": 0},
            {"nums": [1], "target": 1}],
    gen=lambda r: [(lambda a: {"nums": a, "target": r.randint(-12, 12)})(
        sorted(set(ilist(r, 0, 15, -10, 10)))) for _ in range(6)],
    brute=lambda nums, target: __import__("bisect").bisect_left(nums, target),
    checks=[({"nums": [1, 3, 5, 6], "target": 5}, 2), ({"nums": [1, 3, 5, 6], "target": 7}, 4)])

add("find-peak-element", "Find Peak Element", "medium",
    ["array", "binary-search"], "findPeakElement", [("nums", "int[]")], "int",
    """
A **mountain array** `nums` strictly increases to a single peak and then strictly
decreases. Return **the index of the peak element** (the unique maximum). Aim for
`O(log n)`.

## Constraints
- `1 <= len(nums) <= 10^5`.
- `nums` strictly increases then strictly decreases; values are distinct.

## Examples
Input: `nums = [1,3,5,4,2]`
Output: `2`

Input: `nums = [10]`
Output: `0`

Input: `nums = [1,2,3,4]`
Output: `3`
Explanation: a strictly increasing array peaks at its last index.
""",
    """def findPeakElement(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo
""",
    visible=[{"nums": [1, 3, 5, 4, 2]}, {"nums": [10]}, {"nums": [1, 2, 3, 4]}],
    hidden=[{"nums": [5, 4, 3, 2, 1]}, {"nums": [1, 50]}, {"nums": [50, 1]}],
    gen=lambda r: [_lb_mountain(r) for _ in range(6)],
    brute=lambda nums: nums.index(max(nums)),
    checks=[({"nums": [1, 3, 5, 4, 2]}, 2), ({"nums": [10]}, 0)])

add("kth-largest-element", "Kth Largest Element", "medium",
    ["array", "heap", "sorting"], "findKthLargest",
    [("nums", "int[]"), ("k", "int")], "int",
    """
Given an integer array `nums` and an integer `k`, return **the `k`-th largest
element** by value (the element that would be at position `k` from the end if the
array were sorted ascending; duplicates count toward the ranking).

## Constraints
- `1 <= k <= len(nums) <= 10^5`.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [3,2,1,5,6,4], k = 2`
Output: `5`

Input: `nums = [3,2,3,1,2,4,5,5,6], k = 4`
Output: `4`

Input: `nums = [1], k = 1`
Output: `1`
""",
    """def findKthLargest(nums, k):
    import heapq
    return heapq.nlargest(k, nums)[-1]
""",
    visible=[{"nums": [3, 2, 1, 5, 6, 4], "k": 2},
             {"nums": [3, 2, 3, 1, 2, 4, 5, 5, 6], "k": 4}, {"nums": [1], "k": 1}],
    hidden=[{"nums": [2, 1], "k": 2}, {"nums": [7, 7, 7], "k": 2},
            {"nums": [-1, -2, -3], "k": 1}],
    gen=lambda r: [(lambda a: {"nums": a, "k": r.randint(1, len(a))})(ilist(r, 1, 20, -9, 9))
                   for _ in range(6)],
    brute=lambda nums, k: sorted(nums, reverse=True)[k - 1],
    checks=[({"nums": [3, 2, 1, 5, 6, 4], "k": 2}, 5),
            ({"nums": [3, 2, 3, 1, 2, 4, 5, 5, 6], "k": 4}, 4)])

add("median-of-two-sorted-arrays", "Median of Two Sorted Arrays", "hard",
    ["array", "binary-search"], "findMedianSortedArrays",
    [("nums1", "int[]"), ("nums2", "int[]")], "num",
    """
Given two sorted arrays `nums1` and `nums2`, return **the median of all the
numbers combined**, as a floating-point value. If the combined count is even, the
median is the average of the two middle values.

## Constraints
- `0 <= len(nums1), len(nums2)`, and `1 <= len(nums1) + len(nums2) <= 2*10^5`.
- Each array is sorted ascending; `-10^6 <= values <= 10^6`.

## Examples
Input: `nums1 = [1,3], nums2 = [2]`
Output: `2.0`

Input: `nums1 = [1,2], nums2 = [3,4]`
Output: `2.5`

Input: `nums1 = [], nums2 = [1]`
Output: `1.0`
""",
    """def findMedianSortedArrays(nums1, nums2):
    merged = sorted(nums1 + nums2)
    n = len(merged)
    if n % 2:
        return float(merged[n // 2])
    return (merged[n // 2 - 1] + merged[n // 2]) / 2
""",
    visible=[{"nums1": [1, 3], "nums2": [2]}, {"nums1": [1, 2], "nums2": [3, 4]},
             {"nums1": [], "nums2": [1]}],
    hidden=[{"nums1": [2], "nums2": []}, {"nums1": [1, 1], "nums2": [1, 1]},
            {"nums1": [-5, 3], "nums2": [0]}],
    gen=lambda r: [_lb_median_case(r) for _ in range(6)],
    brute=lambda nums1, nums2: float(__import__("statistics").median(nums1 + nums2)),
    checks=[({"nums1": [1, 3], "nums2": [2]}, 2.0),
            ({"nums1": [1, 2], "nums2": [3, 4]}, 2.5)])

add("k-closest-points-to-origin", "K Closest Points to Origin", "medium",
    ["array", "heap", "math"], "kClosest",
    [("points", "int[][]"), ("k", "int")], "int[][]",
    """
Given `points` on the plane (each `[x, y]`) and an integer `k`, return **the `k`
points closest to the origin** by Euclidean distance. The answer may be returned
**in any order**. Every point has a distinct distance from the origin, so the set
of `k` closest points is unique.

## Constraints
- `1 <= k <= len(points) <= 10^4`.
- `-10^4 <= x, y <= 10^4`; all squared distances `x^2 + y^2` are distinct.

## Examples
Input: `points = [[1,3],[-2,2]], k = 1`
Output: `[[-2,2]]`
Explanation: `(-2)^2 + 2^2 = 8 < 1^2 + 3^2 = 10`.

Input: `points = [[3,3],[5,-1],[-2,4]], k = 2`
Output: `[[3,3],[-2,4]]`

Input: `points = [[0,1]], k = 1`
Output: `[[0,1]]`
""",
    """def kClosest(points, k):
    import heapq
    return heapq.nsmallest(k, points, key=lambda p: p[0] * p[0] + p[1] * p[1])
""",
    visible=[{"points": [[1, 3], [-2, 2]], "k": 1},
             {"points": [[3, 3], [5, -1], [-2, 4]], "k": 2}, {"points": [[0, 1]], "k": 1}],
    hidden=[{"points": [[1, 0], [0, 2], [3, 0]], "k": 3},
            {"points": [[2, 2], [1, 1]], "k": 1}],
    gen=lambda r: [_lb_points_case(r) for _ in range(6)],
    brute=lambda points, k: sorted(points, key=lambda p: p[0] * p[0] + p[1] * p[1])[:k],
    checks=[({"points": [[1, 3], [-2, 2]], "k": 1}, [[-2, 2]]),
            ({"points": [[0, 1]], "k": 1}, [[0, 1]])])

add("smallest-range-covering-lists", "Smallest Range Covering Lists", "hard",
    ["heap", "sliding-window", "sorting"], "smallestRange", [("lists", "int[][]")], "int[]",
    """
Given `k` sorted integer lists, find **the smallest range `[l, r]`** that includes
at least one number from each list. A range `[a, b]` is smaller than `[c, d]` if
`b - a < d - c`, or `b - a == d - c` and `a < c`. Return the range as `[l, r]`.

## Constraints
- `1 <= k <= 3000`; each list is non-empty and sorted ascending.
- `-10^5 <= values <= 10^5`.

## Examples
Input: `lists = [[4,10,15,24,26],[0,9,12,20],[5,18,22,30]]`
Output: `[20,24]`

Input: `lists = [[1,2,3],[1,2,3],[1,2,3]]`
Output: `[1,1]`

Input: `lists = [[5]]`
Output: `[5,5]`
""",
    """def smallestRange(lists):
    import heapq
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists)]
    heapq.heapify(heap)
    cur_max = max(lst[0] for lst in lists)
    best = [heap[0][0], cur_max]
    while True:
        val, i, j = heapq.heappop(heap)
        size = cur_max - val
        if size < best[1] - best[0] or (size == best[1] - best[0] and val < best[0]):
            best = [val, cur_max]
        if j + 1 == len(lists[i]):
            break
        nxt = lists[i][j + 1]
        cur_max = max(cur_max, nxt)
        heapq.heappush(heap, (nxt, i, j + 1))
    return best
""",
    visible=[{"lists": [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]},
             {"lists": [[1, 2, 3], [1, 2, 3], [1, 2, 3]]}, {"lists": [[5]]}],
    hidden=[{"lists": [[1], [2], [3]]}, {"lists": [[-5, 0, 5], [-3, 3]]},
            {"lists": [[10, 20, 30], [11, 21, 31]]}],
    gen=lambda r: [_lb_range_case(r) for _ in range(6)],
    brute=_lb_brute_range,
    checks=[({"lists": [[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]}, [20, 24]),
            ({"lists": [[5]]}, [5, 5])])

# ---- Wave 5a: grid BFS / DFS -----------------------------------------------

def _lb_grid01(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    return {"grid": [[r.randint(0, 1) for _ in range(n)] for _ in range(m)]}


def _lb_brute_maxarea(grid):
    from collections import deque
    m, n = len(grid), len(grid[0])
    seen = set()
    best = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1 and (i, j) not in seen:
                q = deque([(i, j)])
                seen.add((i, j))
                area = 0
                while q:
                    x, y = q.popleft()
                    area += 1
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1 \
                                and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            q.append((nx, ny))
                best = max(best, area)
    return best


def _lb_oranges_case(r):
    m, n = r.randint(1, 4), r.randint(1, 4)
    return {"grid": [[r.randint(0, 2) for _ in range(n)] for _ in range(m)]}


def _lb_brute_oranges(grid):
    g = [row[:] for row in grid]
    m, n = len(g), len(g[0])
    minutes = 0
    while True:
        if all(cell != 1 for row in g for cell in row):
            return minutes
        to_rot = []
        for i in range(m):
            for j in range(n):
                if g[i][j] == 2:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ni, nj = i + dx, j + dy
                        if 0 <= ni < m and 0 <= nj < n and g[ni][nj] == 1:
                            to_rot.append((ni, nj))
        if not to_rot:
            return -1
        for i, j in to_rot:
            g[i][j] = 2
        minutes += 1


def _lb_binmatrix_case(r):
    n = r.randint(1, 4)
    return {"grid": [[r.randint(0, 1) for _ in range(n)] for _ in range(n)]}


def _lb_brute_binmatrix(grid):
    from collections import deque
    n = len(grid)
    if grid[0][0] or grid[n - 1][n - 1]:
        return -1
    inf = float("inf")
    dist = [[inf] * n for _ in range(n)]
    dist[0][0] = 1
    q = deque([(0, 0)])
    while q:
        x, y = q.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == 0 \
                            and dist[nx][ny] == inf:
                        dist[nx][ny] = dist[x][y] + 1
                        q.append((nx, ny))
    d = dist[n - 1][n - 1]
    return d if d != inf else -1


add("max-area-of-island", "Max Area of Island", "medium",
    ["matrix", "dfs", "bfs", "union-find"], "maxAreaOfIsland", [("grid", "int[][]")], "int",
    """
Given a binary grid where `1` is land and `0` is water, an **island** is a group
of `1`s connected 4-directionally. Return **the number of cells in the largest
island**, or `0` if there is no land.

## Constraints
- `1 <= len(grid), len(grid[0]) <= 50`.
- Each cell is `0` or `1`.

## Examples
Input: `grid = [[0,1,0,0],[1,1,1,0],[0,1,0,0]]`
Output: `5`

Input: `grid = [[0,0],[0,0]]`
Output: `0`

Input: `grid = [[1]]`
Output: `1`
""",
    """def maxAreaOfIsland(grid):
    m, n = len(grid), len(grid[0])
    seen = [[False] * n for _ in range(m)]
    best = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1 and not seen[i][j]:
                area = 0
                stack = [(i, j)]
                seen[i][j] = True
                while stack:
                    x, y = stack.pop()
                    area += 1
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1 \
                                and not seen[nx][ny]:
                            seen[nx][ny] = True
                            stack.append((nx, ny))
                best = max(best, area)
    return best
""",
    visible=[{"grid": [[0, 1, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0]]},
             {"grid": [[0, 0], [0, 0]]}, {"grid": [[1]]}],
    hidden=[{"grid": [[0]]}, {"grid": [[1, 1], [1, 1]]},
            {"grid": [[1, 0, 1], [0, 0, 0], [1, 0, 1]]}],
    gen=lambda r: [_lb_grid01(r) for _ in range(6)],
    brute=_lb_brute_maxarea,
    checks=[({"grid": [[0, 1, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0]]}, 5),
            ({"grid": [[0, 0], [0, 0]]}, 0)])

add("rotting-oranges", "Rotting Oranges", "medium",
    ["matrix", "bfs"], "orangesRotting", [("grid", "int[][]")], "int",
    """
In a grid each cell is `0` (empty), `1` (fresh orange), or `2` (rotten orange).
Every minute, any fresh orange adjacent (4-directionally) to a rotten orange
becomes rotten. Return **the minimum number of minutes until no fresh orange
remains**, or `-1` if some fresh orange can never rot.

## Constraints
- `1 <= len(grid), len(grid[0]) <= 50`.
- Each cell is `0`, `1`, or `2`.

## Examples
Input: `grid = [[2,1,1],[1,1,0],[0,1,1]]`
Output: `4`

Input: `grid = [[2,1,1],[0,1,1],[1,0,1]]`
Output: `-1`
Explanation: the bottom-left orange is never reached.

Input: `grid = [[0,2]]`
Output: `0`
""",
    """def orangesRotting(grid):
    from collections import deque
    m, n = len(grid), len(grid[0])
    grid = [row[:] for row in grid]
    q = deque()
    fresh = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                q.append((i, j, 0))
            elif grid[i][j] == 1:
                fresh += 1
    minutes = 0
    while q:
        x, y, t = q.popleft()
        minutes = max(minutes, t)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1:
                grid[nx][ny] = 2
                fresh -= 1
                q.append((nx, ny, t + 1))
    return minutes if fresh == 0 else -1
""",
    visible=[{"grid": [[2, 1, 1], [1, 1, 0], [0, 1, 1]]},
             {"grid": [[2, 1, 1], [0, 1, 1], [1, 0, 1]]}, {"grid": [[0, 2]]}],
    hidden=[{"grid": [[0]]}, {"grid": [[1]]}, {"grid": [[2, 2], [1, 1]]}],
    gen=lambda r: [_lb_oranges_case(r) for _ in range(6)],
    brute=_lb_brute_oranges,
    checks=[({"grid": [[2, 1, 1], [1, 1, 0], [0, 1, 1]]}, 4),
            ({"grid": [[2, 1, 1], [0, 1, 1], [1, 0, 1]]}, -1)])

add("shortest-path-in-binary-matrix", "Shortest Path in Binary Matrix", "medium",
    ["matrix", "bfs"], "shortestPathBinaryMatrix", [("grid", "int[][]")], "int",
    """
Given an `n x n` binary grid where `0` is open and `1` is blocked, return **the
length (number of cells) of the shortest clear path** from the top-left cell to
the bottom-right cell, moving in any of the 8 directions through open cells.
Return `-1` if no such path exists.

## Constraints
- `1 <= n <= 100`.
- Each cell is `0` or `1`.

## Examples
Input: `grid = [[0,1],[1,0]]`
Output: `2`

Input: `grid = [[0,0,0],[1,1,0],[1,1,0]]`
Output: `4`

Input: `grid = [[1,0,0],[1,1,0],[1,1,0]]`
Output: `-1`
Explanation: the start cell is blocked.
""",
    """def shortestPathBinaryMatrix(grid):
    from collections import deque
    n = len(grid)
    if grid[0][0] != 0 or grid[n - 1][n - 1] != 0:
        return -1
    q = deque([(0, 0, 1)])
    seen = {(0, 0)}
    while q:
        x, y, d = q.popleft()
        if x == n - 1 and y == n - 1:
            return d
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == 0 \
                        and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append((nx, ny, d + 1))
    return -1
""",
    visible=[{"grid": [[0, 1], [1, 0]]}, {"grid": [[0, 0, 0], [1, 1, 0], [1, 1, 0]]},
             {"grid": [[1, 0, 0], [1, 1, 0], [1, 1, 0]]}],
    hidden=[{"grid": [[0]]}, {"grid": [[1]]}, {"grid": [[0, 0], [0, 0]]}],
    gen=lambda r: [_lb_binmatrix_case(r) for _ in range(6)],
    brute=_lb_brute_binmatrix,
    checks=[({"grid": [[0, 1], [1, 0]]}, 2),
            ({"grid": [[0, 0, 0], [1, 1, 0], [1, 1, 0]]}, 4)])

# ---- Wave 5b: graphs (BFS / topo / shortest path / MST) --------------------

def _lb_dag(r):
    n = r.randint(1, 6)
    edges = []
    for _ in range(r.randint(0, 6)):
        a, b = r.randint(0, n - 1), r.randint(0, n - 1)
        if a != b:
            edges.append([a, b])
    return {"numCourses": n, "prerequisites": edges}


def _lb_brute_order(numCourses, prerequisites):
    from collections import defaultdict
    adj = defaultdict(list)
    indeg = [0] * numCourses
    for a, b in prerequisites:
        adj[b].append(a)
        indeg[a] += 1
    used = [False] * numCourses
    order = []
    for _ in range(numCourses):
        cand = min((i for i in range(numCourses) if not used[i] and indeg[i] == 0),
                   default=None)
        if cand is None:
            return []
        used[cand] = True
        order.append(cand)
        for v in adj[cand]:
            indeg[v] -= 1
    return order


def _lb_alien_case(r):
    return {"words": [
        "".join(r.choice("abc") for _ in range(r.randint(1, 3)))
        for _ in range(r.randint(1, 5))]}


def _lb_brute_alien(words):
    from itertools import permutations
    chars = sorted(set("".join(words)))
    cons = []
    for w1, w2 in zip(words, words[1:]):
        found = False
        for k in range(min(len(w1), len(w2))):
            if w1[k] != w2[k]:
                cons.append((w1[k], w2[k]))
                found = True
                break
        if not found and len(w1) > len(w2):
            return ""
    for perm in permutations(chars):
        pos = {c: i for i, c in enumerate(perm)}
        if all(pos[a] < pos[b] for a, b in cons):
            return "".join(perm)
    return ""


def _lb_bipartite_case(r):
    n = r.randint(1, 6)
    adj = [set() for _ in range(n)]
    for _ in range(r.randint(0, 8)):
        a, b = r.randint(0, n - 1), r.randint(0, n - 1)
        if a != b:
            adj[a].add(b)
            adj[b].add(a)
    return {"graph": [sorted(s) for s in adj]}


def _lb_brute_bipartite(graph):
    n = len(graph)
    parent = list(range(2 * n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u in range(n):
        for v in graph[u]:
            if find(u) == find(v):
                return False
            parent[find(u)] = find(v + n)
            parent[find(u + n)] = find(v)
    return True


def _lb_network_case(r):
    n = r.randint(1, 5)
    times = []
    for _ in range(r.randint(0, 8)):
        u, v = r.randint(1, n), r.randint(1, n)
        if u != v:
            times.append([u, v, r.randint(1, 9)])
    return {"times": times, "n": n, "k": r.randint(1, n)}


def _lb_brute_network(times, n, k):
    inf = float("inf")
    dist = [inf] * (n + 1)
    dist[k] = 0
    for _ in range(n - 1):
        for u, v, w in times:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    res = max(dist[1:n + 1])
    return -1 if res == inf else res


def _lb_cheapest_case(r):
    n = r.randint(2, 5)
    flights = []
    for _ in range(r.randint(0, 8)):
        u, v = r.randint(0, n - 1), r.randint(0, n - 1)
        if u != v:
            flights.append([u, v, r.randint(1, 50)])
    return {"n": n, "flights": flights, "src": r.randint(0, n - 1),
            "dst": r.randint(0, n - 1), "k": r.randint(0, n)}


def _lb_brute_cheapest(n, flights, src, dst, k):
    from collections import defaultdict
    adj = defaultdict(list)
    for u, v, w in flights:
        adj[u].append((v, w))
    best = [float("inf")]

    def dfs(node, stops, cost):
        if cost >= best[0]:
            return
        if node == dst:
            best[0] = cost
            return
        if stops < 0:
            return
        for v, w in adj[node]:
            dfs(v, stops - 1, cost + w)

    dfs(src, k, 0)
    return -1 if best[0] == float("inf") else best[0]


def _lb_mst_case(r):
    n = r.randint(1, 6)
    nodes = list(range(n))
    r.shuffle(nodes)
    edges = []
    for i in range(1, n):
        edges.append([nodes[i], nodes[r.randint(0, i - 1)], r.randint(1, 20)])
    for _ in range(r.randint(0, 6)):
        a, b = r.randint(0, n - 1), r.randint(0, n - 1)
        if a != b:
            edges.append([a, b, r.randint(1, 20)])
    return {"n": n, "edges": edges}


def _lb_brute_mst(n, edges):
    import heapq
    from collections import defaultdict
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))
    seen = [False] * n
    heap = [(0, 0)]
    total = cnt = 0
    while heap and cnt < n:
        w, u = heapq.heappop(heap)
        if seen[u]:
            continue
        seen[u] = True
        total += w
        cnt += 1
        for ww, v in adj[u]:
            if not seen[v]:
                heapq.heappush(heap, (ww, v))
    return total


add("word-ladder-length", "Word Ladder Length", "hard",
    ["graph", "bfs", "string"], "ladderLength",
    [("beginWord", "string"), ("endWord", "string"), ("wordList", "string[]")], "int",
    """
Given `beginWord`, `endWord`, and a `wordList`, a transformation changes exactly
one letter at a time, and every intermediate word must be in `wordList`. Return
**the number of words in the shortest transformation sequence** from `beginWord`
to `endWord` (counting both ends), or `0` if none exists. `beginWord` need not be
in `wordList`.

## Constraints
- `1 <= len(beginWord) <= 10`; all words have the same length and are lowercase.
- `1 <= len(wordList) <= 5000`.

## Examples
Input: `beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]`
Output: `5`
Explanation: hit → hot → dot → dog → cog.

Input: `beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log"]`
Output: `0`

Input: `beginWord = "a", endWord = "c", wordList = ["a","b","c"]`
Output: `2`
""",
    """def ladderLength(beginWord, endWord, wordList):
    from collections import deque
    words = set(wordList)
    if endWord not in words:
        return 0
    q = deque([(beginWord, 1)])
    seen = {beginWord}
    while q:
        w, d = q.popleft()
        if w == endWord:
            return d
        for i in range(len(w)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                nxt = w[:i] + c + w[i + 1:]
                if nxt in words and nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, d + 1))
    return 0
""",
    visible=[{"beginWord": "hit", "endWord": "cog",
              "wordList": ["hot", "dot", "dog", "lot", "log", "cog"]},
             {"beginWord": "hit", "endWord": "cog",
              "wordList": ["hot", "dot", "dog", "lot", "log"]},
             {"beginWord": "a", "endWord": "c", "wordList": ["a", "b", "c"]}],
    hidden=[{"beginWord": "a", "endWord": "a", "wordList": ["a"]},
            {"beginWord": "hot", "endWord": "dog", "wordList": ["hot", "dog"]},
            {"beginWord": "hot", "endWord": "dog", "wordList": ["hot", "dot", "dog"]}],
    checks=[({"beginWord": "hit", "endWord": "cog",
              "wordList": ["hot", "dot", "dog", "lot", "log", "cog"]}, 5),
            ({"beginWord": "a", "endWord": "c", "wordList": ["a", "b", "c"]}, 2),
            ({"beginWord": "hot", "endWord": "dog", "wordList": ["hot", "dog"]}, 0)])

add("course-schedule-ordering", "Course Schedule Ordering", "medium",
    ["graph", "topological-sort"], "findOrder",
    [("numCourses", "int"), ("prerequisites", "int[][]")], "int[]",
    """
There are `numCourses` courses labelled `0..numCourses-1`. Each pair `[a, b]` in
`prerequisites` means course `b` must be taken before course `a`. Return **a valid
ordering of all courses**; if several exist, return the **lexicographically
smallest** one. Return `[]` if no ordering exists.

## Constraints
- `1 <= numCourses <= 2000`, `0 <= len(prerequisites) <= 5000`.
- `prerequisites[i] = [a, b]` with `0 <= a, b < numCourses`.

## Examples
Input: `numCourses = 2, prerequisites = [[1,0]]`
Output: `[0,1]`

Input: `numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]`
Output: `[0,1,2,3]`

Input: `numCourses = 2, prerequisites = [[0,1],[1,0]]`
Output: `[]`
Explanation: the two courses depend on each other.
""",
    """def findOrder(numCourses, prerequisites):
    import heapq
    from collections import defaultdict
    adj = defaultdict(list)
    indeg = [0] * numCourses
    for a, b in prerequisites:
        adj[b].append(a)
        indeg[a] += 1
    heap = [i for i in range(numCourses) if indeg[i] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        u = heapq.heappop(heap)
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    return order if len(order) == numCourses else []
""",
    visible=[{"numCourses": 2, "prerequisites": [[1, 0]]},
             {"numCourses": 4, "prerequisites": [[1, 0], [2, 0], [3, 1], [3, 2]]},
             {"numCourses": 2, "prerequisites": [[0, 1], [1, 0]]}],
    hidden=[{"numCourses": 1, "prerequisites": []},
            {"numCourses": 3, "prerequisites": [[0, 1], [0, 2]]},
            {"numCourses": 3, "prerequisites": [[1, 0], [2, 1], [0, 2]]}],
    gen=lambda r: [_lb_dag(r) for _ in range(8)],
    brute=_lb_brute_order,
    checks=[({"numCourses": 2, "prerequisites": [[1, 0]]}, [0, 1]),
            ({"numCourses": 2, "prerequisites": [[0, 1], [1, 0]]}, [])])

add("alien-dictionary-order", "Alien Dictionary Order", "hard",
    ["graph", "topological-sort", "string"], "alienOrder", [("words", "string[]")], "string",
    """
Given a list of `words` sorted lexicographically by the rules of an unknown
alphabet, derive **a possible character order** as a string. If several orders are
valid, return the **lexicographically smallest** (using normal letter order to
break ties). Return the empty string `""` if the ordering is inconsistent (for
example a word precedes its own prefix).

## Constraints
- `1 <= len(words) <= 1000`; words contain lowercase English letters.

## Examples
Input: `words = ["wrt","wrf","er","ett","rftt"]`
Output: `"wertf"`

Input: `words = ["z","x"]`
Output: `"zx"`

Input: `words = ["z","x","z"]`
Output: `""`
Explanation: the constraints are contradictory.
""",
    """def alienOrder(words):
    import heapq
    from collections import defaultdict
    chars = set("".join(words))
    adj = defaultdict(set)
    indeg = {c: 0 for c in chars}
    for w1, w2 in zip(words, words[1:]):
        found = False
        for k in range(min(len(w1), len(w2))):
            if w1[k] != w2[k]:
                if w2[k] not in adj[w1[k]]:
                    adj[w1[k]].add(w2[k])
                    indeg[w2[k]] += 1
                found = True
                break
        if not found and len(w1) > len(w2):
            return ""
    heap = [c for c in chars if indeg[c] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        c = heapq.heappop(heap)
        order.append(c)
        for nb in sorted(adj[c]):
            indeg[nb] -= 1
            if indeg[nb] == 0:
                heapq.heappush(heap, nb)
    return "".join(order) if len(order) == len(chars) else ""
""",
    visible=[{"words": ["wrt", "wrf", "er", "ett", "rftt"]}, {"words": ["z", "x"]},
             {"words": ["z", "x", "z"]}],
    hidden=[{"words": ["abc", "ab"]}, {"words": ["a"]}, {"words": ["ba", "bc", "ac"]}],
    gen=lambda r: [_lb_alien_case(r) for _ in range(8)],
    brute=_lb_brute_alien,
    checks=[({"words": ["wrt", "wrf", "er", "ett", "rftt"]}, "wertf"),
            ({"words": ["z", "x"]}, "zx"), ({"words": ["abc", "ab"]}, "")])

add("graph-bipartite-check", "Graph Bipartite Check", "medium",
    ["graph", "bfs", "union-find"], "isBipartite", [("graph", "int[][]")], "bool",
    """
Given an undirected graph as adjacency lists (`graph[u]` lists the neighbours of
node `u`), return **`true` if the graph is bipartite** — its nodes can be 2-colored
so that every edge joins nodes of different colors — and `false` otherwise.

## Constraints
- `1 <= len(graph) <= 1000`.
- `graph[u]` contains distinct nodes, never `u`, and the graph is symmetric.

## Examples
Input: `graph = [[1,3],[0,2],[1,3],[0,2]]`
Output: `true`
Explanation: color `{0,2}` vs `{1,3}`.

Input: `graph = [[1,2,3],[0,2],[0,1,3],[0,2]]`
Output: `false`

Input: `graph = [[]]`
Output: `true`
""",
    """def isBipartite(graph):
    color = [0] * len(graph)
    for start in range(len(graph)):
        if color[start] != 0:
            continue
        color[start] = 1
        stack = [start]
        while stack:
            u = stack.pop()
            for v in graph[u]:
                if color[v] == 0:
                    color[v] = -color[u]
                    stack.append(v)
                elif color[v] == color[u]:
                    return False
    return True
""",
    visible=[{"graph": [[1, 3], [0, 2], [1, 3], [0, 2]]},
             {"graph": [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]}, {"graph": [[]]}],
    hidden=[{"graph": [[1], [0]]}, {"graph": [[1, 2], [0, 2], [0, 1]]},
            {"graph": [[], [2], [1]]}],
    gen=lambda r: [_lb_bipartite_case(r) for _ in range(8)],
    brute=_lb_brute_bipartite,
    checks=[({"graph": [[1, 3], [0, 2], [1, 3], [0, 2]]}, True),
            ({"graph": [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]}, False)])

add("network-delay-time", "Network Delay Time", "medium",
    ["graph", "shortest-path", "heap"], "networkDelayTime",
    [("times", "int[][]"), ("n", "int"), ("k", "int")], "int",
    """
A network has `n` nodes labelled `1..n`. Each `times[i] = [u, v, w]` is a directed
edge along which a signal takes `w` time to travel from `u` to `v`. Sending a
signal from node `k`, return **the time for all `n` nodes to receive it**, or `-1`
if some node is unreachable.

## Constraints
- `1 <= n <= 100`, `0 <= len(times) <= n*(n-1)`.
- `1 <= u, v <= n`, `u != v`, `1 <= w <= 100`.

## Examples
Input: `times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2`
Output: `2`

Input: `times = [[1,2,1]], n = 2, k = 1`
Output: `1`

Input: `times = [[1,2,1]], n = 2, k = 2`
Output: `-1`
""",
    """def networkDelayTime(times, n, k):
    import heapq
    from collections import defaultdict
    adj = defaultdict(list)
    for u, v, w in times:
        adj[u].append((v, w))
    dist = {}
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue
        dist[u] = d
        for v, w in adj[u]:
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    if len(dist) < n:
        return -1
    return max(dist.values())
""",
    visible=[{"times": [[2, 1, 1], [2, 3, 1], [3, 4, 1]], "n": 4, "k": 2},
             {"times": [[1, 2, 1]], "n": 2, "k": 1},
             {"times": [[1, 2, 1]], "n": 2, "k": 2}],
    hidden=[{"times": [], "n": 1, "k": 1}, {"times": [[1, 2, 5], [2, 3, 5]], "n": 3, "k": 1},
            {"times": [[1, 2, 1], [2, 1, 1]], "n": 2, "k": 1}],
    gen=lambda r: [_lb_network_case(r) for _ in range(8)],
    brute=_lb_brute_network,
    checks=[({"times": [[2, 1, 1], [2, 3, 1], [3, 4, 1]], "n": 4, "k": 2}, 2),
            ({"times": [[1, 2, 1]], "n": 2, "k": 2}, -1)])

add("cheapest-flight-with-k-stops", "Cheapest Flight With K Stops", "medium",
    ["graph", "shortest-path", "dynamic-programming"], "findCheapestPrice",
    [("n", "int"), ("flights", "int[][]"), ("src", "int"), ("dst", "int"), ("k", "int")], "int",
    """
There are `n` cities `0..n-1` connected by `flights[i] = [u, v, w]` (a flight from
`u` to `v` costing `w`). Return **the cheapest price from `src` to `dst` using at
most `k` stops** (i.e. at most `k+1` flights), or `-1` if no such route exists.

## Constraints
- `1 <= n <= 100`, `0 <= len(flights) <= n*(n-1)`.
- `0 <= u, v < n`, `u != v`, `1 <= w <= 10^4`, `0 <= k < n`.

## Examples
Input: `n = 4, flights = [[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]], src = 0, dst = 3, k = 1`
Output: `700`
Explanation: `0→1→3` costs `700` within 1 stop.

Input: `n = 3, flights = [[0,1,100],[1,2,100],[0,2,500]], src = 0, dst = 2, k = 1`
Output: `200`

Input: `n = 3, flights = [[0,1,100],[1,2,100],[0,2,500]], src = 0, dst = 2, k = 0`
Output: `500`
""",
    """def findCheapestPrice(n, flights, src, dst, k):
    inf = float("inf")
    dist = [inf] * n
    dist[src] = 0
    for _ in range(k + 1):
        nd = dist[:]
        for u, v, w in flights:
            if dist[u] + w < nd[v]:
                nd[v] = dist[u] + w
        dist = nd
    return -1 if dist[dst] == inf else dist[dst]
""",
    visible=[{"n": 4, "flights": [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600],
                                  [2, 3, 200]], "src": 0, "dst": 3, "k": 1},
             {"n": 3, "flights": [[0, 1, 100], [1, 2, 100], [0, 2, 500]],
              "src": 0, "dst": 2, "k": 1},
             {"n": 3, "flights": [[0, 1, 100], [1, 2, 100], [0, 2, 500]],
              "src": 0, "dst": 2, "k": 0}],
    hidden=[{"n": 2, "flights": [], "src": 0, "dst": 1, "k": 1},
            {"n": 2, "flights": [[0, 1, 50]], "src": 0, "dst": 0, "k": 1},
            {"n": 3, "flights": [[0, 1, 2], [1, 2, 3]], "src": 0, "dst": 2, "k": 1}],
    gen=lambda r: [_lb_cheapest_case(r) for _ in range(8)],
    brute=_lb_brute_cheapest,
    checks=[({"n": 4, "flights": [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600],
                                  [2, 3, 200]], "src": 0, "dst": 3, "k": 1}, 700),
            ({"n": 3, "flights": [[0, 1, 100], [1, 2, 100], [0, 2, 500]],
              "src": 0, "dst": 2, "k": 0}, 500)])

add("minimum-spanning-tree-cost", "Minimum Spanning Tree Cost", "medium",
    ["graph", "union-find", "greedy"], "minimumSpanningTree",
    [("n", "int"), ("edges", "int[][]")], "int",
    """
Given a connected, undirected, weighted graph with `n` nodes `0..n-1` and `edges`
where `edges[i] = [u, v, w]`, return **the total weight of a minimum spanning
tree** (the cheapest set of edges connecting all nodes).

## Constraints
- `1 <= n <= 1000`; the graph is connected.
- `edges[i] = [u, v, w]`, `0 <= u, v < n`, `1 <= w <= 10^6`.

## Examples
Input: `n = 4, edges = [[0,1,10],[0,2,6],[0,3,5],[1,3,15],[2,3,4]]`
Output: `19`
Explanation: pick edges of weight `5 + 4 + 10`.

Input: `n = 2, edges = [[0,1,7]]`
Output: `7`

Input: `n = 1, edges = []`
Output: `0`
""",
    """def minimumSpanningTree(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    total = 0
    for w, u, v in sorted((w, u, v) for u, v, w in edges):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
    return total
""",
    visible=[{"n": 4, "edges": [[0, 1, 10], [0, 2, 6], [0, 3, 5], [1, 3, 15], [2, 3, 4]]},
             {"n": 2, "edges": [[0, 1, 7]]}, {"n": 1, "edges": []}],
    hidden=[{"n": 3, "edges": [[0, 1, 1], [1, 2, 2], [0, 2, 3]]},
            {"n": 3, "edges": [[0, 1, 5], [1, 2, 5], [0, 2, 1]]}],
    gen=lambda r: [_lb_mst_case(r) for _ in range(8)],
    brute=_lb_brute_mst,
    checks=[({"n": 4, "edges": [[0, 1, 10], [0, 2, 6], [0, 3, 5], [1, 3, 15], [2, 3, 4]]}, 19),
            ({"n": 1, "edges": []}, 0)])

# ---- Wave 6: grouping, op-replay, tree, linked list, range queries ---------

def _lb_accounts_case(r):
    emails = ["e%d@x.com" % i for i in range(6)]
    return {"accounts": [["A"] + r.sample(emails, r.randint(1, 3))
                         for _ in range(r.randint(1, 5))]}


def _lb_brute_accounts(accounts):
    from collections import defaultdict
    graph = defaultdict(set)
    owner = {}
    for acc in accounts:
        name, emails = acc[0], acc[1:]
        for e in emails:
            owner[e] = name
            graph[emails[0]].add(e)
            graph[e].add(emails[0])
    seen = set()
    res = []
    for e in list(owner):
        if e in seen:
            continue
        comp = []
        stack = [e]
        seen.add(e)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in graph[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        res.append([owner[e]] + sorted(comp))
    return res


def _lb_filedup_case(r):
    return {"files": [["p%d" % i, r.choice(["x", "y", "z"])]
                      for i in range(r.randint(0, 6))]}


def _lb_brute_filedup(files):
    seen = {}
    for path, content in files:
        seen.setdefault(content, []).append(path)
    return [v for v in seen.values() if len(v) >= 2]


def _lb_uf_case(r):
    n = r.randint(2, 6)
    return {"n": n, "operations": [
        [r.choice(["union", "connected"]), r.randint(0, n - 1), r.randint(0, n - 1)]
        for _ in range(r.randint(1, 10))]}


def _lb_brute_uf(n, operations):
    from collections import defaultdict
    adj = defaultdict(set)
    out = []
    for op, a, b in operations:
        if op == "union":
            adj[a].add(b)
            adj[b].add(a)
        else:
            seen = {a}
            stack = [a]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
            out.append(b in seen)
    return out


def _lb_crawl_case(r):
    urls = [("http://a.com/" if i % 2 == 0 else "http://b.com/") + "p%d" % i
            for i in range(6)]
    graph = {u: [r.choice(urls) for _ in range(r.randint(0, 3))] for u in urls}
    return {"startUrl": r.choice(urls), "graph": graph}


def _lb_brute_crawl(startUrl, graph):
    def host(u):
        return u[7:].split("/")[0]

    h = host(startUrl)
    seen = set()
    stack = [startUrl]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        for v in graph.get(u, []):
            if host(v) == h and v not in seen:
                stack.append(v)
    return sorted(seen)


def _lb_cycle_case(r):
    n = r.randint(0, 8)
    head = [r.randint(-9, 9) for _ in range(n)]
    pos = -1 if n == 0 else r.choice([-1] + list(range(n)))
    return {"head": head, "pos": pos}


def _lb_brute_cycle(head, pos):
    n = len(head)
    if n == 0:
        return False
    nxt = list(range(1, n)) + [pos]
    seen = set()
    cur = 0
    while cur != -1:
        if cur in seen:
            return True
        seen.add(cur)
        cur = nxt[cur]
    return False


def _lb_runlen_case(r):
    n = r.randint(1, 12)
    arr = [r.randint(0, 3) for _ in range(n)]
    queries = []
    for _ in range(r.randint(1, 5)):
        lo = r.randint(0, n - 1)
        queries.append([lo, r.randint(lo, n - 1)])
    return {"arr": arr, "queries": queries}


def _lb_brute_runlen(arr, queries):
    from itertools import groupby
    out = []
    for lo, hi in queries:
        sub = arr[lo:hi + 1]
        out.append(max((len(list(g)) for _, g in groupby(sub)), default=0))
    return out


def _lb_compact_case(r):
    samples = []
    t = 0
    for _ in range(r.randint(1, 8)):
        t += r.randint(1, 3)
        samples.append([t, r.choice(["a", "b", "c"])])
    return {"samples": samples}


def _lb_brute_compact(samples):
    from itertools import groupby
    out = []
    for s, grp in groupby(samples, key=lambda x: x[1]):
        ts = [x[0] for x in grp]
        out.append([ts[0], ts[-1], s])
    return out


add("accounts-merge", "Accounts Merge", "medium",
    ["union-find", "hash-table", "graph"], "accountsMerge", [("accounts", "string[][]")],
    "string[][]",
    """
Each entry in `accounts` is `[name, email1, email2, ...]`. Two accounts belong to
the same person if they share **at least one email** (names may repeat across
different people). Merge all accounts of the same person and return **the merged
accounts**. Within each merged account put the name first, then its emails in
**sorted order**. The accounts themselves may be returned **in any order**.

## Constraints
- `1 <= len(accounts) <= 1000`; each account has a name and at least one email.
- Emails are lowercase and unique within an account.

## Examples
Input: `accounts = [["John","a@m.com","b@m.com"],["John","b@m.com","c@m.com"],["Mary","x@m.com"]]`
Output: `[["John","a@m.com","b@m.com","c@m.com"],["Mary","x@m.com"]]`
Explanation: the two John accounts share `b@m.com`.

Input: `accounts = [["A","a@m.com"]]`
Output: `[["A","a@m.com"]]`

Input: `accounts = [["A","a@m.com"],["B","b@m.com"]]`
Output: `[["A","a@m.com"],["B","b@m.com"]]`
""",
    """def accountsMerge(accounts):
    from collections import defaultdict
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    owner = {}
    for acc in accounts:
        name = acc[0]
        first = acc[1]
        for e in acc[1:]:
            owner[e] = name
            parent.setdefault(e, e)
            parent[find(e)] = find(first)
    groups = defaultdict(list)
    for e in owner:
        groups[find(e)].append(e)
    return [[owner[root]] + sorted(emails) for root, emails in groups.items()]
""",
    visible=[{"accounts": [["John", "a@m.com", "b@m.com"], ["John", "b@m.com", "c@m.com"],
                           ["Mary", "x@m.com"]]},
             {"accounts": [["A", "a@m.com"]]},
             {"accounts": [["A", "a@m.com"], ["B", "b@m.com"]]}],
    hidden=[{"accounts": [["A", "a@m.com", "b@m.com"], ["A", "c@m.com"]]},
            {"accounts": [["A", "x@m.com"], ["A", "x@m.com"]]}],
    gen=lambda r: [_lb_accounts_case(r) for _ in range(6)],
    brute=_lb_brute_accounts,
    checks=[({"accounts": [["A", "a@m.com"]]}, [["A", "a@m.com"]])])

add("file-duplicate-groups", "File Duplicate Groups", "medium",
    ["hash-table", "string"], "findDuplicates", [("files", "string[][]")], "string[][]",
    """
Each entry in `files` is `[path, content]`. Return **the groups of paths whose
files have identical content**, including only groups with **two or more** paths.
Neither the order of the groups nor the order of paths within a group matters.

## Constraints
- `0 <= len(files) <= 2*10^4`; paths are unique.

## Examples
Input: `files = [["a","x"],["b","x"],["c","y"]]`
Output: `[["a","b"]]`

Input: `files = [["a","x"]]`
Output: `[]`

Input: `files = [["a","x"],["b","y"],["c","x"],["d","y"]]`
Output: `[["a","c"],["b","d"]]`
""",
    """def findDuplicates(files):
    from collections import defaultdict
    groups = defaultdict(list)
    for path, content in files:
        groups[content].append(path)
    return [paths for paths in groups.values() if len(paths) > 1]
""",
    visible=[{"files": [["a", "x"], ["b", "x"], ["c", "y"]]}, {"files": [["a", "x"]]},
             {"files": [["a", "x"], ["b", "y"], ["c", "x"], ["d", "y"]]}],
    hidden=[{"files": []}, {"files": [["a", "x"], ["b", "y"]]},
            {"files": [["a", "x"], ["b", "x"], ["c", "x"]]}],
    gen=lambda r: [_lb_filedup_case(r) for _ in range(6)],
    brute=_lb_brute_filedup,
    checks=[({"files": [["a", "x"], ["b", "x"], ["c", "y"]]}, [["a", "b"]]),
            ({"files": [["a", "x"]]}, [])])

add("union-find-connectivity-queries", "Union Find Connectivity Queries", "medium",
    ["union-find", "graph"], "connectivity",
    [("n", "int"), ("operations", "any[][]")], "bool[]",
    """
You manage `n` nodes `0..n-1` under a sequence of `operations`. Each operation is
`["union", a, b]` (connect `a` and `b`) or `["connected", a, b]` (query). Return
**a list of booleans, one per `connected` query in order**, indicating whether the
two nodes are in the same connected component at that moment.

## Constraints
- `1 <= n <= 10^4`, `1 <= len(operations) <= 10^5`.
- `0 <= a, b < n`.

## Examples
Input: `n = 5, operations = [["connected",0,1],["union",0,1],["connected",0,1]]`
Output: `[false, true]`

Input: `n = 3, operations = [["union",0,1],["union",1,2],["connected",0,2]]`
Output: `[true]`

Input: `n = 2, operations = [["connected",0,0]]`
Output: `[true]`
""",
    """def connectivity(n, operations):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    out = []
    for op, a, b in operations:
        if op == "union":
            parent[find(a)] = find(b)
        else:
            out.append(find(a) == find(b))
    return out
""",
    visible=[{"n": 5, "operations": [["connected", 0, 1], ["union", 0, 1],
                                     ["connected", 0, 1]]},
             {"n": 3, "operations": [["union", 0, 1], ["union", 1, 2], ["connected", 0, 2]]},
             {"n": 2, "operations": [["connected", 0, 0]]}],
    hidden=[{"n": 4, "operations": [["connected", 0, 3]]},
            {"n": 4, "operations": [["union", 0, 1], ["union", 2, 3], ["connected", 1, 2]]}],
    gen=lambda r: [_lb_uf_case(r) for _ in range(8)],
    brute=_lb_brute_uf,
    checks=[({"n": 5, "operations": [["connected", 0, 1], ["union", 0, 1],
                                     ["connected", 0, 1]]}, [False, True]),
            ({"n": 2, "operations": [["connected", 0, 0]]}, [True])])

add("web-crawler-same-host", "Web Crawler Same Host", "medium",
    ["graph", "bfs", "string"], "crawl",
    [("startUrl", "string"), ("graph", "object")], "string[]",
    """
Starting from `startUrl`, you may follow links given by `graph` (a map from a URL
to the list of URLs it links to). Return **all reachable URLs that share the same
hostname as `startUrl`**, sorted ascending. A URL looks like `http://host/path`;
the hostname is the text between `http://` and the next `/`.

## Constraints
- `1 <= number of URLs <= 10^4`; every URL begins with `http://`.

## Examples
Input: `startUrl = "http://a.com/1", graph = {"http://a.com/1": ["http://a.com/2","http://b.com/9"], "http://a.com/2": [], "http://b.com/9": []}`
Output: `["http://a.com/1","http://a.com/2"]`
Explanation: `b.com` is a different host.

Input: `startUrl = "http://x.org/p", graph = {"http://x.org/p": []}`
Output: `["http://x.org/p"]`

Input: `startUrl = "http://a.com/1", graph = {"http://a.com/1": ["http://a.com/1"]}`
Output: `["http://a.com/1"]`
""",
    """def crawl(startUrl, graph):
    from collections import deque

    def host(u):
        return u[7:].split("/")[0]

    h = host(startUrl)
    seen = {startUrl}
    q = deque([startUrl])
    while q:
        u = q.popleft()
        for v in graph.get(u, []):
            if v not in seen and host(v) == h:
                seen.add(v)
                q.append(v)
    return sorted(seen)
""",
    visible=[{"startUrl": "http://a.com/1",
              "graph": {"http://a.com/1": ["http://a.com/2", "http://b.com/9"],
                        "http://a.com/2": [], "http://b.com/9": []}},
             {"startUrl": "http://x.org/p", "graph": {"http://x.org/p": []}},
             {"startUrl": "http://a.com/1", "graph": {"http://a.com/1": ["http://a.com/1"]}}],
    hidden=[{"startUrl": "http://a.com/1",
             "graph": {"http://a.com/1": ["http://a.com/2"], "http://a.com/2":
                       ["http://a.com/3"], "http://a.com/3": []}},
            {"startUrl": "http://a.com/x",
             "graph": {"http://a.com/x": ["http://c.com/y"], "http://c.com/y": []}}],
    gen=lambda r: [_lb_crawl_case(r) for _ in range(6)],
    brute=_lb_brute_crawl,
    checks=[({"startUrl": "http://x.org/p", "graph": {"http://x.org/p": []}},
             ["http://x.org/p"])])

add("binary-tree-diameter", "Binary Tree Diameter", "easy",
    ["tree", "depth-first-search"], "diameterOfBinaryTree", [("root", "int[]")], "int",
    """
Given the level-order array `root` of a binary tree, return **the diameter** — the
number of **edges** on the longest path between any two nodes (the path need not
pass through the root).

## Constraints
- `0 <= number of nodes <= 10^4`.
- `-100 <= Node.val <= 100`; `null` marks an absent child.

## Examples
Input: `root = [1,2,3,4,5]`
Output: `3`
Explanation: the path `4 → 2 → 1 → 3` (or `5 → 2 → 1 → 3`) has 3 edges.

Input: `root = [1,2,3]`
Output: `2`

Input: `root = [1]`
Output: `0`
""",
    """def diameterOfBinaryTree(root):
    class Node:
        __slots__ = ("val", "left", "right")

        def __init__(self, v):
            self.val, self.left, self.right = v, None, None

    def build(arr):
        if not arr or arr[0] is None:
            return None
        head = Node(arr[0])
        q, i = [head], 1
        while q and i < len(arr):
            cur = q.pop(0)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.left = Node(x); q.append(cur.left)
            if i < len(arr):
                x = arr[i]; i += 1
                if x is not None:
                    cur.right = Node(x); q.append(cur.right)
        return head

    best = [0]

    def height(n):
        if n is None:
            return 0
        lh = height(n.left)
        rh = height(n.right)
        best[0] = max(best[0], lh + rh)
        return 1 + max(lh, rh)

    height(build(root))
    return best[0]
""",
    visible=[{"root": [1, 2, 3, 4, 5]}, {"root": [1, 2, 3]}, {"root": [1]}],
    hidden=[{"root": []}, {"root": [1, 2, None, 3, None, 4]},
            {"root": [4, 2, 7, 1, 3, 6, 9]}],
    checks=[({"root": [1, 2, 3, 4, 5]}, 3), ({"root": [1, 2, 3]}, 2),
            ({"root": [1]}, 0), ({"root": []}, 0),
            ({"root": [1, 2, None, 3, None, 4]}, 3),
            ({"root": [4, 2, 7, 1, 3, 6, 9]}, 4)])

add("linked-list-cycle", "Linked List Cycle", "easy",
    ["linked-list", "two-pointers"], "hasCycle",
    [("head", "int[]"), ("pos", "int")], "bool",
    """
A singly linked list is given as the value array `head`, plus an integer `pos`:
if `pos >= 0`, the last node's `next` points back to the node at index `pos`,
forming a cycle; if `pos == -1` the list has no cycle. Return **`true` if the list
contains a cycle**. Use `O(1)` extra space.

## Constraints
- `0 <= len(head) <= 10^4`, `-1 <= pos < len(head)`.

## Examples
Input: `head = [3,2,0,-4], pos = 1`
Output: `true`
Explanation: the tail connects back to the node with value `2`.

Input: `head = [1,2], pos = 0`
Output: `true`

Input: `head = [1], pos = -1`
Output: `false`
""",
    """def hasCycle(head, pos):
    n = len(head)
    if n == 0:
        return False
    nxt = list(range(1, n)) + [pos]
    slow = fast = 0
    while True:
        fast = nxt[fast]
        if fast == -1:
            return False
        fast = nxt[fast]
        if fast == -1:
            return False
        slow = nxt[slow]
        if slow == fast:
            return True
""",
    visible=[{"head": [3, 2, 0, -4], "pos": 1}, {"head": [1, 2], "pos": 0},
             {"head": [1], "pos": -1}],
    hidden=[{"head": [], "pos": -1}, {"head": [1], "pos": 0},
            {"head": [1, 2, 3, 4], "pos": -1}],
    gen=lambda r: [_lb_cycle_case(r) for _ in range(8)],
    brute=_lb_brute_cycle,
    checks=[({"head": [3, 2, 0, -4], "pos": 1}, True),
            ({"head": [1], "pos": -1}, False)])

add("run-length-queries", "Run Length Queries", "medium",
    ["array", "queries"], "longestRun",
    [("arr", "int[]"), ("queries", "int[][]")], "int[]",
    """
Given an array `arr` and a list of `queries` where each query is `[l, r]` (an
inclusive index range), return **for each query the length of the longest run of
equal consecutive values within `arr[l..r]`**.

## Constraints
- `1 <= len(arr) <= 2000`, `1 <= len(queries) <= 2000`.
- `0 <= l <= r < len(arr)`.

## Examples
Input: `arr = [1,1,2,2,2,3], queries = [[0,2],[1,4],[0,5]]`
Output: `[2,3,3]`

Input: `arr = [5], queries = [[0,0]]`
Output: `[1]`

Input: `arr = [7,7,7,7], queries = [[1,3]]`
Output: `[3]`
""",
    """def longestRun(arr, queries):
    out = []
    for l, r in queries:
        best = cur = 1
        for i in range(l + 1, r + 1):
            cur = cur + 1 if arr[i] == arr[i - 1] else 1
            if cur > best:
                best = cur
        out.append(best)
    return out
""",
    visible=[{"arr": [1, 1, 2, 2, 2, 3], "queries": [[0, 2], [1, 4], [0, 5]]},
             {"arr": [5], "queries": [[0, 0]]},
             {"arr": [7, 7, 7, 7], "queries": [[1, 3]]}],
    hidden=[{"arr": [1, 2, 3], "queries": [[0, 2]]},
            {"arr": [4, 4, 1, 4, 4, 4], "queries": [[0, 1], [2, 5], [0, 5]]}],
    gen=lambda r: [_lb_runlen_case(r) for _ in range(8)],
    brute=_lb_brute_runlen,
    checks=[({"arr": [1, 1, 2, 2, 2, 3], "queries": [[0, 2], [1, 4], [0, 5]]}, [2, 3, 3])])

add("log-event-compaction", "Log Event Compaction", "easy",
    ["array", "simulation"], "compactLog", [("samples", "any[][]")], "any[][]",
    """
Given `samples` as `[timestamp, state]` pairs in strictly increasing timestamp
order, **merge maximal runs of equal consecutive states** into intervals
`[start, end, state]`, where `start` and `end` are the first and last timestamps
of the run. Return the list of intervals in order.

## Constraints
- `1 <= len(samples) <= 10^5`; timestamps strictly increase.

## Examples
Input: `samples = [[0,"on"],[1,"on"],[2,"off"],[5,"off"],[6,"on"]]`
Output: `[[0,1,"on"],[2,5,"off"],[6,6,"on"]]`

Input: `samples = [[3,"a"]]`
Output: `[[3,3,"a"]]`

Input: `samples = [[0,"a"],[1,"b"],[2,"a"]]`
Output: `[[0,0,"a"],[1,1,"b"],[2,2,"a"]]`
""",
    """def compactLog(samples):
    out = []
    for t, s in samples:
        if out and out[-1][2] == s:
            out[-1][1] = t
        else:
            out.append([t, t, s])
    return out
""",
    visible=[{"samples": [[0, "on"], [1, "on"], [2, "off"], [5, "off"], [6, "on"]]},
             {"samples": [[3, "a"]]},
             {"samples": [[0, "a"], [1, "b"], [2, "a"]]}],
    hidden=[{"samples": [[1, "x"], [2, "x"], [3, "x"]]},
            {"samples": [[0, "a"], [10, "a"], [20, "b"]]}],
    gen=lambda r: [_lb_compact_case(r) for _ in range(8)],
    brute=_lb_brute_compact,
    checks=[({"samples": [[0, "on"], [1, "on"], [2, "off"], [5, "off"], [6, "on"]]},
             [[0, 1, "on"], [2, 5, "off"], [6, 6, "on"]])])

# ---- Wave 7: backtracking & skyline ----------------------------------------

def _lb_brute_subsets(nums):
    from itertools import combinations
    out = []
    for k in range(len(nums) + 1):
        out.extend(list(c) for c in combinations(nums, k))
    return out


def _lb_brute_permute(nums):
    res = []

    def bt(cur, rem):
        if not rem:
            res.append(cur[:])
            return
        for i in range(len(rem)):
            bt(cur + [rem[i]], rem[:i] + rem[i + 1:])

    bt([], list(nums))
    return res


def _lb_brute_genparen(n):
    from itertools import product
    out = []
    for combo in product("()", repeat=2 * n):
        s = "".join(combo)
        bal = 0
        ok = True
        for c in s:
            bal += 1 if c == "(" else -1
            if bal < 0:
                ok = False
                break
        if ok and bal == 0:
            out.append(s)
    return out


def _lb_brute_nqueens(n):
    from itertools import permutations
    out = []
    for perm in permutations(range(n)):
        ok = all(abs(perm[i] - perm[j]) != j - i
                 for i in range(n) for j in range(i + 1, n))
        if ok:
            out.append(["".join("Q" if perm[r] == c else "." for c in range(n))
                        for r in range(n)])
    return out


def _lb_skyline_case(r):
    bs = []
    for _ in range(r.randint(0, 5)):
        lo = r.randint(0, 10)
        bs.append([lo, lo + r.randint(1, 5), r.randint(1, 9)])
    return {"buildings": bs}


def _lb_brute_skyline(buildings):
    if not buildings:
        return []
    lo = min(b[0] for b in buildings)
    hi = max(b[1] for b in buildings)
    res = []
    prev = 0
    for x in range(lo, hi + 1):
        h = max((H for L, R, H in buildings if L <= x < R), default=0)
        if h != prev:
            res.append([x, h])
            prev = h
    return res


add("subsets", "Subsets", "medium",
    ["backtracking", "bit-manipulation", "array"], "subsets", [("nums", "int[]")], "int[][]",
    """
Given an array `nums` of **distinct** integers, return **all possible subsets**
(the power set). The solution set must not contain duplicate subsets, and may be
returned in any order (each subset in any order).

## Constraints
- `0 <= len(nums) <= 12`; values are distinct.

## Examples
Input: `nums = [1,2,3]`
Output: `[[],[1],[2],[3],[1,2],[1,3],[2,3],[1,2,3]]`

Input: `nums = []`
Output: `[[]]`

Input: `nums = [0]`
Output: `[[],[0]]`
""",
    """def subsets(nums):
    res = [[]]
    for x in nums:
        res += [s + [x] for s in res]
    return res
""",
    visible=[{"nums": [1, 2, 3]}, {"nums": []}, {"nums": [0]}],
    hidden=[{"nums": [9]}, {"nums": [1, 2]}, {"nums": [4, 5, 6, 7]}],
    gen=lambda r: [{"nums": r.sample(range(0, 9), r.randint(0, 5))} for _ in range(6)],
    brute=_lb_brute_subsets,
    norm=lambda x: sorted([sorted(s) for s in x]),
    checks=[({"nums": []}, [[]]), ({"nums": [0]}, [[], [0]])])

add("permutations", "Permutations", "medium",
    ["backtracking", "array"], "permute", [("nums", "int[]")], "int[][]",
    """
Given an array `nums` of **distinct** integers, return **all possible orderings**
(permutations) of its elements. The list of permutations may be returned in any
order.

## Constraints
- `1 <= len(nums) <= 7`; values are distinct.

## Examples
Input: `nums = [1,2,3]`
Output: `[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]`

Input: `nums = [1]`
Output: `[[1]]`

Input: `nums = [0,1]`
Output: `[[0,1],[1,0]]`
""",
    """def permute(nums):
    from itertools import permutations
    return [list(p) for p in permutations(nums)]
""",
    visible=[{"nums": [1, 2, 3]}, {"nums": [1]}, {"nums": [0, 1]}],
    hidden=[{"nums": [5, 6]}, {"nums": [1, 2, 3, 4]}],
    gen=lambda r: [{"nums": r.sample(range(0, 9), r.randint(1, 5))} for _ in range(6)],
    brute=_lb_brute_permute,
    norm=lambda x: sorted(x),
    checks=[({"nums": [1]}, [[1]]), ({"nums": [0, 1]}, [[0, 1], [1, 0]])])

add("generate-parentheses", "Generate Parentheses", "medium",
    ["backtracking", "string"], "generateParenthesis", [("n", "int")], "string[]",
    """
Given `n` pairs of parentheses, return **all combinations of well-formed
parentheses** of length `2n`. The combinations may be returned in any order.

## Constraints
- `0 <= n <= 8`.

## Examples
Input: `n = 3`
Output: `["((()))","(()())","(())()","()(())","()()()"]`

Input: `n = 1`
Output: `["()"]`

Input: `n = 0`
Output: `[""]`
""",
    """def generateParenthesis(n):
    res = []

    def bt(s, opened, closed):
        if len(s) == 2 * n:
            res.append(s)
            return
        if opened < n:
            bt(s + "(", opened + 1, closed)
        if closed < opened:
            bt(s + ")", opened, closed + 1)

    bt("", 0, 0)
    return res
""",
    visible=[{"n": 3}, {"n": 1}, {"n": 0}],
    hidden=[{"n": 2}, {"n": 4}],
    gen=lambda r: [{"n": r.randint(0, 4)} for _ in range(6)],
    brute=_lb_brute_genparen,
    norm=lambda x: sorted(x),
    checks=[({"n": 1}, ["()"]), ({"n": 0}, [""])])

add("n-queens", "N Queens", "hard",
    ["backtracking"], "solveNQueens", [("n", "int")], "string[][]",
    """
Place `n` queens on an `n x n` board so that no two attack each other (no shared
row, column, or diagonal). Return **all distinct solutions**; each solution is a
list of `n` strings, where each string is a board row using `'Q'` for a queen and
`'.'` for an empty cell. Solutions may be returned in any order.

## Constraints
- `1 <= n <= 9`.

## Examples
Input: `n = 4`
Output: `[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]`

Input: `n = 1`
Output: `[["Q"]]`

Input: `n = 2`
Output: `[]`
Explanation: two queens always attack on a 2x2 board.
""",
    """def solveNQueens(n):
    res = []
    cols, diag, anti, placement = set(), set(), set(), []

    def bt(row):
        if row == n:
            res.append(["".join("Q" if placement[r] == c else "." for c in range(n))
                        for r in range(n)])
            return
        for c in range(n):
            if c in cols or (row - c) in diag or (row + c) in anti:
                continue
            cols.add(c); diag.add(row - c); anti.add(row + c); placement.append(c)
            bt(row + 1)
            cols.discard(c); diag.discard(row - c); anti.discard(row + c); placement.pop()

    bt(0)
    return res
""",
    visible=[{"n": 4}, {"n": 1}, {"n": 2}],
    hidden=[{"n": 3}, {"n": 5}, {"n": 6}],
    gen=lambda r: [{"n": r.randint(1, 6)} for _ in range(4)],
    brute=_lb_brute_nqueens,
    norm=lambda x: sorted(x),
    checks=[({"n": 1}, [["Q"]]), ({"n": 2}, []), ({"n": 3}, [])])

add("skyline-key-points", "Skyline Key Points", "hard",
    ["heap", "sweep-line", "divide-and-conquer"], "getSkyline",
    [("buildings", "int[][]")], "int[][]",
    """
Each building is `[left, right, height]` occupying the half-open strip
`[left, right)`. Return **the skyline as a list of key points `[x, height]`**,
sorted by `x`, where each point marks where the outline's height changes. The
final point has height `0` marking the right end of the rightmost building. No two
consecutive points share the same height.

## Constraints
- `0 <= len(buildings) <= 10^4`.
- `0 <= left < right <= 10^9`, `1 <= height <= 10^9`.

## Examples
Input: `buildings = [[2,9,10],[3,7,15],[5,12,12],[15,20,10],[19,24,8]]`
Output: `[[2,10],[3,15],[7,12],[12,0],[15,10],[20,8],[24,0]]`

Input: `buildings = [[0,2,3],[2,5,3]]`
Output: `[[0,3],[5,0]]`

Input: `buildings = []`
Output: `[]`
""",
    """def getSkyline(buildings):
    import heapq
    events = []
    for left, right, height in buildings:
        events.append((left, -height, right))
        events.append((right, 0, 0))
    events.sort()
    res = []
    live = [(0, float("inf"))]
    for x, neg_h, right in events:
        while live[0][1] <= x:
            heapq.heappop(live)
        if neg_h:
            heapq.heappush(live, (neg_h, right))
        cur = -live[0][0]
        if not res or res[-1][1] != cur:
            res.append([x, cur])
    return res
""",
    visible=[{"buildings": [[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]]},
             {"buildings": [[0, 2, 3], [2, 5, 3]]}, {"buildings": []}],
    hidden=[{"buildings": [[1, 2, 1]]}, {"buildings": [[0, 5, 3], [1, 4, 5]]},
            {"buildings": [[1, 3, 4], [2, 4, 4]]}],
    gen=lambda r: [_lb_skyline_case(r) for _ in range(8)],
    brute=_lb_brute_skyline,
    checks=[({"buildings": [[2, 9, 10], [3, 7, 15], [5, 12, 12], [15, 20, 10], [19, 24, 8]]},
             [[2, 10], [3, 15], [7, 12], [12, 0], [15, 10], [20, 8], [24, 0]]),
            ({"buildings": [[0, 2, 3], [2, 5, 3]]}, [[0, 3], [5, 0]])])

# ---- Wave 8a: design problems as operation-replay --------------------------

def _lb_minstack_case(r):
    ops, size = [], 0
    for _ in range(r.randint(1, 12)):
        if size == 0:
            ops.append(["push", r.randint(-9, 9)])
            size += 1
        else:
            ch = r.choice(["push", "pop", "top", "getMin"])
            if ch == "push":
                ops.append(["push", r.randint(-9, 9)])
                size += 1
            elif ch == "pop":
                ops.append(["pop"])
                size -= 1
            else:
                ops.append([ch])
    return {"operations": ops}


def _lb_brute_minstack(operations):
    stack, out = [], []
    for op in operations:
        name = op[0]
        if name == "push":
            stack.append(op[1])
            out.append(None)
        elif name == "pop":
            stack.pop()
            out.append(None)
        elif name == "top":
            out.append(stack[-1])
        else:
            out.append(min(stack))
    return out


def _lb_lru_case(r):
    ops = []
    for _ in range(r.randint(1, 12)):
        if r.random() < 0.5:
            ops.append(["put", r.randint(0, 4), r.randint(0, 9)])
        else:
            ops.append(["get", r.randint(0, 4)])
    return {"capacity": r.randint(1, 3), "operations": ops}


def _lb_brute_lru(capacity, operations):
    order, data, out = [], {}, []
    for op in operations:
        if op[0] == "put":
            k, v = op[1], op[2]
            if k in data:
                data[k] = v
                order.remove(k)
                order.append(k)
            else:
                if len(data) >= capacity:
                    del data[order.pop(0)]
                data[k] = v
                order.append(k)
            out.append(None)
        else:
            k = op[1]
            if k in data:
                order.remove(k)
                order.append(k)
                out.append(data[k])
            else:
                out.append(-1)
    return out


def _lb_lfu_case(r):
    ops = []
    for _ in range(r.randint(1, 14)):
        if r.random() < 0.5:
            ops.append(["put", r.randint(0, 3), r.randint(0, 9)])
        else:
            ops.append(["get", r.randint(0, 3)])
    return {"capacity": r.randint(1, 3), "operations": ops}


def _lb_brute_lfu(capacity, operations):
    val, freq, tick, t, out = {}, {}, {}, [0], []

    def use(k):
        freq[k] += 1
        t[0] += 1
        tick[k] = t[0]

    for op in operations:
        if op[0] == "get":
            k = op[1]
            if k in val:
                use(k)
                out.append(val[k])
            else:
                out.append(-1)
        else:
            k, v = op[1], op[2]
            if capacity == 0:
                out.append(None)
                continue
            if k in val:
                val[k] = v
                use(k)
            else:
                if len(val) >= capacity:
                    evk = min(val, key=lambda kk: (freq[kk], tick[kk]))
                    del val[evk], freq[evk], tick[evk]
                t[0] += 1
                val[k] = v
                freq[k] = 1
                tick[k] = t[0]
            out.append(None)
    return out


def _lb_medstream_case(r):
    ops = [["addNum", r.randint(-9, 9)]]
    for _ in range(r.randint(1, 12)):
        if r.random() < 0.5:
            ops.append(["addNum", r.randint(-9, 9)])
        else:
            ops.append(["findMedian"])
    return {"operations": ops}


def _lb_brute_medstream(operations):
    import statistics
    data, out = [], []
    for op in operations:
        if op[0] == "addNum":
            data.append(op[1])
            out.append(None)
        else:
            out.append(float(statistics.median(data)))
    return out


def _lb_hit_case(r):
    ops, t = [], 1
    for _ in range(r.randint(1, 12)):
        t += r.randint(0, 150)
        ops.append(["hit", t] if r.random() < 0.6 else ["getHits", t])
    return {"operations": ops}


def _lb_brute_hit(operations):
    hits, out = [], []
    for op in operations:
        if op[0] == "hit":
            hits.append(op[1])
            out.append(None)
        else:
            t = op[1]
            out.append(sum(1 for h in hits if t - 300 < h <= t))
    return out


def _lb_rate_case(r):
    ops, t = [], 0
    for _ in range(r.randint(1, 14)):
        t += r.randint(0, 4)
        ops.append(["request", r.choice(["a", "b"]), t])
    return {"limit": r.randint(1, 3), "window": r.randint(2, 8), "operations": ops}


def _lb_brute_rate(limit, window, operations):
    from collections import defaultdict
    hist, out = defaultdict(list), []
    for op in operations:
        _, user, t = op
        recent = [x for x in hist[user] if x > t - window]
        if len(recent) < limit:
            hist[user].append(t)
            out.append(True)
        else:
            out.append(False)
    return out


add("min-stack", "Min Stack", "medium",
    ["stack", "design"], "minStackOps", [("operations", "any[][]")], "any[]",
    """
Replay a sequence of stack `operations` and return **the list of results**. Each
operation is one of `["push", x]`, `["pop"]`, `["top"]`, `["getMin"]`. `push` and
`pop` return `null`; `top` returns the top value; `getMin` returns the current
minimum. All operations run in `O(1)`.

## Constraints
- `1 <= len(operations) <= 10^4`.
- `pop`, `top`, `getMin` are only issued when the stack is non-empty.
- `-10^9 <= x <= 10^9`.

## Examples
Input: `operations = [["push",-2],["push",0],["push",-3],["getMin"],["pop"],["top"],["getMin"]]`
Output: `[null,null,null,-3,null,0,-2]`

Input: `operations = [["push",5],["top"],["getMin"]]`
Output: `[null,5,5]`

Input: `operations = [["push",1],["push",1],["getMin"],["pop"],["getMin"]]`
Output: `[null,null,1,null,1]`
""",
    """def minStackOps(operations):
    stack, mins, out = [], [], []
    for op in operations:
        name = op[0]
        if name == "push":
            x = op[1]
            stack.append(x)
            mins.append(x if not mins else min(x, mins[-1]))
            out.append(None)
        elif name == "pop":
            stack.pop()
            mins.pop()
            out.append(None)
        elif name == "top":
            out.append(stack[-1])
        else:
            out.append(mins[-1])
    return out
""",
    visible=[{"operations": [["push", -2], ["push", 0], ["push", -3], ["getMin"],
                             ["pop"], ["top"], ["getMin"]]},
             {"operations": [["push", 5], ["top"], ["getMin"]]},
             {"operations": [["push", 1], ["push", 1], ["getMin"], ["pop"], ["getMin"]]}],
    hidden=[{"operations": [["push", 0], ["getMin"]]},
            {"operations": [["push", 3], ["push", 1], ["push", 2], ["getMin"], ["pop"],
                            ["getMin"]]}],
    gen=lambda r: [_lb_minstack_case(r) for _ in range(8)],
    brute=_lb_brute_minstack,
    checks=[({"operations": [["push", -2], ["push", 0], ["push", -3], ["getMin"],
                             ["pop"], ["top"], ["getMin"]]},
             [None, None, None, -3, None, 0, -2])])

add("lru-cache", "LRU Cache", "medium",
    ["design", "hash-table", "linked-list"], "lruCache",
    [("capacity", "int"), ("operations", "any[][]")], "any[]",
    """
Implement a Least-Recently-Used cache of the given `capacity` by replaying
`operations` and returning **the list of results**. Each operation is
`["put", key, value]` (returns `null`) or `["get", key]` (returns the value, or
`-1` if absent). A `get` or `put` counts as a use; when the cache is full a `put`
of a new key evicts the least recently used key. All operations run in `O(1)`
average time.

## Constraints
- `1 <= capacity <= 3000`, `1 <= len(operations) <= 10^4`.
- `0 <= key, value <= 10^9`.

## Examples
Input: `capacity = 2, operations = [["put",1,1],["put",2,2],["get",1],["put",3,3],["get",2],["put",4,4],["get",1],["get",3],["get",4]]`
Output: `[null,null,1,null,-1,null,-1,3,4]`

Input: `capacity = 1, operations = [["put",1,1],["put",2,2],["get",1],["get",2]]`
Output: `[null,null,-1,2]`

Input: `capacity = 2, operations = [["get",1]]`
Output: `[-1]`
""",
    """def lruCache(capacity, operations):
    from collections import OrderedDict
    cache = OrderedDict()
    out = []
    for op in operations:
        if op[0] == "put":
            k, v = op[1], op[2]
            if k in cache:
                cache.move_to_end(k)
            cache[k] = v
            if len(cache) > capacity:
                cache.popitem(last=False)
            out.append(None)
        else:
            k = op[1]
            if k in cache:
                cache.move_to_end(k)
                out.append(cache[k])
            else:
                out.append(-1)
    return out
""",
    visible=[{"capacity": 2, "operations": [["put", 1, 1], ["put", 2, 2], ["get", 1],
                                            ["put", 3, 3], ["get", 2], ["put", 4, 4],
                                            ["get", 1], ["get", 3], ["get", 4]]},
             {"capacity": 1, "operations": [["put", 1, 1], ["put", 2, 2], ["get", 1],
                                            ["get", 2]]},
             {"capacity": 2, "operations": [["get", 1]]}],
    hidden=[{"capacity": 2, "operations": [["put", 2, 1], ["put", 2, 2], ["get", 2]]},
            {"capacity": 2, "operations": [["put", 1, 1], ["get", 1], ["put", 2, 2],
                                           ["put", 3, 3], ["get", 1]]}],
    gen=lambda r: [_lb_lru_case(r) for _ in range(8)],
    brute=_lb_brute_lru,
    checks=[({"capacity": 2, "operations": [["put", 1, 1], ["put", 2, 2], ["get", 1],
                                            ["put", 3, 3], ["get", 2], ["put", 4, 4],
                                            ["get", 1], ["get", 3], ["get", 4]]},
             [None, None, 1, None, -1, None, -1, 3, 4])])

add("lfu-cache", "LFU Cache", "hard",
    ["design", "hash-table"], "lfuCache",
    [("capacity", "int"), ("operations", "any[][]")], "any[]",
    """
Implement a Least-Frequently-Used cache of the given `capacity` by replaying
`operations` and returning **the list of results**. Operations are
`["put", key, value]` (returns `null`) and `["get", key]` (returns the value or
`-1`). Each `get` or successful `put` increments a key's use count. When full, a
`put` of a new key evicts the key with the smallest use count, breaking ties by
**least recently used**.

## Constraints
- `0 <= capacity <= 10^4`, `1 <= len(operations) <= 10^4`.
- `0 <= key, value <= 10^9`.

## Examples
Input: `capacity = 2, operations = [["put",1,1],["put",2,2],["get",1],["put",3,3],["get",2],["get",3],["put",4,4],["get",1],["get",3],["get",4]]`
Output: `[null,null,1,null,-1,3,null,-1,3,4]`

Input: `capacity = 0, operations = [["put",0,0],["get",0]]`
Output: `[null,-1]`

Input: `capacity = 2, operations = [["put",1,1],["get",1],["get",1]]`
Output: `[null,1,1]`
""",
    """def lfuCache(capacity, operations):
    from collections import defaultdict, OrderedDict
    val, freq = {}, {}
    buckets = defaultdict(OrderedDict)
    minf = [0]
    out = []

    def bump(k):
        f = freq[k]
        del buckets[f][k]
        if not buckets[f]:
            del buckets[f]
            if minf[0] == f:
                minf[0] = f + 1
        freq[k] = f + 1
        buckets[f + 1][k] = None

    for op in operations:
        if op[0] == "get":
            k = op[1]
            if k in val:
                bump(k)
                out.append(val[k])
            else:
                out.append(-1)
        else:
            k, v = op[1], op[2]
            if capacity == 0:
                out.append(None)
                continue
            if k in val:
                val[k] = v
                bump(k)
            else:
                if len(val) >= capacity:
                    evk, _ = buckets[minf[0]].popitem(last=False)
                    del val[evk], freq[evk]
                val[k] = v
                freq[k] = 1
                buckets[1][k] = None
                minf[0] = 1
            out.append(None)
    return out
""",
    visible=[{"capacity": 2, "operations": [["put", 1, 1], ["put", 2, 2], ["get", 1],
                                            ["put", 3, 3], ["get", 2], ["get", 3],
                                            ["put", 4, 4], ["get", 1], ["get", 3],
                                            ["get", 4]]},
             {"capacity": 0, "operations": [["put", 0, 0], ["get", 0]]},
             {"capacity": 2, "operations": [["put", 1, 1], ["get", 1], ["get", 1]]}],
    hidden=[{"capacity": 1, "operations": [["put", 1, 1], ["put", 2, 2], ["get", 1],
                                           ["get", 2]]},
            {"capacity": 2, "operations": [["put", 3, 1], ["put", 2, 1], ["put", 2, 2],
                                           ["put", 4, 4], ["get", 2]]}],
    gen=lambda r: [_lb_lfu_case(r) for _ in range(10)],
    brute=_lb_brute_lfu,
    checks=[({"capacity": 2, "operations": [["put", 1, 1], ["put", 2, 2], ["get", 1],
                                            ["put", 3, 3], ["get", 2], ["get", 3],
                                            ["put", 4, 4], ["get", 1], ["get", 3],
                                            ["get", 4]]},
             [None, None, 1, None, -1, 3, None, -1, 3, 4]),
            ({"capacity": 0, "operations": [["put", 0, 0], ["get", 0]]}, [None, -1])])

add("median-from-data-stream", "Median From Data Stream", "hard",
    ["heap", "design"], "medianStream", [("operations", "any[][]")], "any[]",
    """
Replay a stream of `operations` and return **the list of results**. Each operation
is `["addNum", x]` (returns `null`) or `["findMedian"]` (returns the median of all
numbers added so far, as a float — the average of the two middle values when the
count is even).

## Constraints
- `1 <= len(operations) <= 10^5`; a `findMedian` is only issued after at least one
  `addNum`.
- `-10^6 <= x <= 10^6`.

## Examples
Input: `operations = [["addNum",1],["addNum",2],["findMedian"],["addNum",3],["findMedian"]]`
Output: `[null,null,1.5,null,2.0]`

Input: `operations = [["addNum",5],["findMedian"]]`
Output: `[null,5.0]`

Input: `operations = [["addNum",2],["addNum",4],["findMedian"]]`
Output: `[null,null,3.0]`
""",
    """def medianStream(operations):
    import heapq
    small, large, out = [], [], []
    for op in operations:
        if op[0] == "addNum":
            heapq.heappush(small, -op[1])
            heapq.heappush(large, -heapq.heappop(small))
            if len(large) > len(small):
                heapq.heappush(small, -heapq.heappop(large))
            out.append(None)
        else:
            if len(small) > len(large):
                out.append(float(-small[0]))
            else:
                out.append((-small[0] + large[0]) / 2)
    return out
""",
    visible=[{"operations": [["addNum", 1], ["addNum", 2], ["findMedian"], ["addNum", 3],
                             ["findMedian"]]},
             {"operations": [["addNum", 5], ["findMedian"]]},
             {"operations": [["addNum", 2], ["addNum", 4], ["findMedian"]]}],
    hidden=[{"operations": [["addNum", -1], ["addNum", -2], ["addNum", -3], ["findMedian"]]},
            {"operations": [["addNum", 6], ["findMedian"], ["addNum", 10], ["findMedian"]]}],
    gen=lambda r: [_lb_medstream_case(r) for _ in range(8)],
    brute=_lb_brute_medstream,
    checks=[({"operations": [["addNum", 1], ["addNum", 2], ["findMedian"], ["addNum", 3],
                             ["findMedian"]]}, [None, None, 1.5, None, 2.0])])

add("hit-counter", "Hit Counter", "medium",
    ["design", "queue"], "hitCounter", [("operations", "any[][]")], "any[]",
    """
Replay `operations` and return **the list of results**. Each operation is
`["hit", t]` recording a hit at timestamp `t` (returns `null`), or
`["getHits", t]` returning the number of hits in the **past 300 seconds**, i.e.
with timestamp in `(t-300, t]`. Timestamps are non-decreasing across operations.

## Constraints
- `1 <= len(operations) <= 10^5`; timestamps are monotonically non-decreasing.
- `1 <= t <= 2*10^9`.

## Examples
Input: `operations = [["hit",1],["hit",2],["hit",3],["getHits",4],["hit",300],["getHits",300],["getHits",301]]`
Output: `[null,null,null,3,null,4,3]`

Input: `operations = [["hit",1],["getHits",1]]`
Output: `[null,1]`

Input: `operations = [["getHits",100]]`
Output: `[0]`
""",
    """def hitCounter(operations):
    from collections import deque
    hits = deque()
    out = []
    for op in operations:
        if op[0] == "hit":
            hits.append(op[1])
            out.append(None)
        else:
            t = op[1]
            while hits and hits[0] <= t - 300:
                hits.popleft()
            out.append(len(hits))
    return out
""",
    visible=[{"operations": [["hit", 1], ["hit", 2], ["hit", 3], ["getHits", 4],
                             ["hit", 300], ["getHits", 300], ["getHits", 301]]},
             {"operations": [["hit", 1], ["getHits", 1]]},
             {"operations": [["getHits", 100]]}],
    hidden=[{"operations": [["hit", 1], ["hit", 1], ["getHits", 1]]},
            {"operations": [["hit", 10], ["getHits", 350]]}],
    gen=lambda r: [_lb_hit_case(r) for _ in range(8)],
    brute=_lb_brute_hit,
    checks=[({"operations": [["hit", 1], ["hit", 2], ["hit", 3], ["getHits", 4],
                             ["hit", 300], ["getHits", 300], ["getHits", 301]]},
             [None, None, None, 3, None, 4, 3])])

add("rate-limiter", "Rate Limiter", "medium",
    ["design", "queue", "hash-table"], "rateLimiter",
    [("limit", "int"), ("window", "int"), ("operations", "any[][]")], "bool[]",
    """
A sliding-window rate limiter allows at most `limit` requests per user within any
`window` seconds. Replay `operations`, each `["request", userId, timestamp]`, and
return **a list of booleans**: `true` if the request is allowed (fewer than
`limit` of that user's *allowed* requests fall in `(timestamp-window, timestamp]`)
and is then recorded, or `false` if it is rejected. Timestamps are non-decreasing.

## Constraints
- `1 <= limit <= 10^4`, `1 <= window <= 10^9`, `1 <= len(operations) <= 10^5`.
- Timestamps are non-decreasing.

## Examples
Input: `limit = 2, window = 10, operations = [["request","a",1],["request","a",2],["request","a",3],["request","a",11]]`
Output: `[true,true,false,true]`

Input: `limit = 1, window = 5, operations = [["request","a",1],["request","b",1],["request","a",2]]`
Output: `[true,true,false]`

Input: `limit = 3, window = 100, operations = [["request","x",50]]`
Output: `[true]`
""",
    """def rateLimiter(limit, window, operations):
    from collections import defaultdict, deque
    hist = defaultdict(deque)
    out = []
    for op in operations:
        _, user, t = op
        dq = hist[user]
        while dq and dq[0] <= t - window:
            dq.popleft()
        if len(dq) < limit:
            dq.append(t)
            out.append(True)
        else:
            out.append(False)
    return out
""",
    visible=[{"limit": 2, "window": 10, "operations": [["request", "a", 1],
                                                       ["request", "a", 2],
                                                       ["request", "a", 3],
                                                       ["request", "a", 11]]},
             {"limit": 1, "window": 5, "operations": [["request", "a", 1],
                                                      ["request", "b", 1],
                                                      ["request", "a", 2]]},
             {"limit": 3, "window": 100, "operations": [["request", "x", 50]]}],
    hidden=[{"limit": 1, "window": 1, "operations": [["request", "a", 1],
                                                     ["request", "a", 1]]},
            {"limit": 2, "window": 3, "operations": [["request", "a", 1],
                                                     ["request", "a", 2],
                                                     ["request", "a", 5]]}],
    gen=lambda r: [_lb_rate_case(r) for _ in range(10)],
    brute=_lb_brute_rate,
    checks=[({"limit": 2, "window": 10, "operations": [["request", "a", 1],
                                                       ["request", "a", 2],
                                                       ["request", "a", 3],
                                                       ["request", "a", 11]]},
             [True, True, False, True])])

# ---- Wave 8b: design problems as operation-replay (continued) --------------

def _lb_calendar_case(r):
    ops = []
    for _ in range(r.randint(1, 10)):
        s = r.randint(0, 20)
        ops.append(["book", s, s + r.randint(1, 8)])
    return {"operations": ops}


def _lb_brute_calendar(operations):
    booked, out = [], []
    for op in operations:
        _, s, e = op
        conflict = any(max(s, bs) < min(e, be) for bs, be in booked)
        if conflict:
            out.append(False)
        else:
            booked.append((s, e))
            out.append(True)
    return out


def _lb_kv_value_at(operations, upto, key):
    val = None
    for i in range(upto):
        op = operations[i]
        if op[0] == "set" and op[1] == key:
            val = op[2]
        elif op[0] == "delete" and op[1] == key:
            val = None
    return val


def _lb_brute_kv(operations):
    out, snap_points = [], []
    for idx, op in enumerate(operations):
        name = op[0]
        if name in ("set", "delete"):
            out.append(None)
        elif name == "get":
            out.append(_lb_kv_value_at(operations, idx, op[1]))
        elif name == "snapshot":
            snap_points.append(idx)
            out.append(len(snap_points) - 1)
        else:  # getAt
            k, sid = op[1], op[2]
            if 0 <= sid < len(snap_points):
                out.append(_lb_kv_value_at(operations, snap_points[sid], k))
            else:
                out.append(None)
    return out


def _lb_kv_case(r):
    keys, ops = ["a", "b", "c"], []
    for _ in range(r.randint(1, 12)):
        c = r.random()
        if c < 0.4:
            ops.append(["set", r.choice(keys), r.randint(0, 9)])
        elif c < 0.6:
            ops.append(["get", r.choice(keys)])
        elif c < 0.75:
            ops.append(["delete", r.choice(keys)])
        elif c < 0.9:
            ops.append(["snapshot"])
        else:
            ops.append(["getAt", r.choice(keys), r.randint(0, 2)])
    return {"operations": ops}


def _lb_brute_trie(operations):
    words, out = [], []
    for op in operations:
        name, s = op[0], op[1]
        if name == "insert":
            words.append(s)
            out.append(None)
        elif name == "search":
            out.append(s in words)
        else:
            out.append(any(w.startswith(s) for w in words))
    return out


def _lb_trie_case(r):
    ops = []
    for _ in range(r.randint(1, 12)):
        c, w = r.random(), sstr(r, 1, 4, "ab")
        if c < 0.4:
            ops.append(["insert", w])
        elif c < 0.7:
            ops.append(["search", w])
        else:
            ops.append(["startsWith", w])
    return {"operations": ops}


def _lb_brute_autocomplete(k, operations):
    freq, out = {}, []
    for op in operations:
        if op[0] == "add":
            freq[op[1]] = freq.get(op[1], 0) + op[2]
            out.append(None)
        else:
            cands = sorted(s for s in freq if s.startswith(op[1]))
            cands.sort(key=lambda s: -freq[s])
            out.append(cands[:k])
    return out


def _lb_autocomplete_case(r):
    words, ops = ["ab", "abc", "abd", "ba", "bad", "abcd"], []
    for _ in range(r.randint(1, 10)):
        if r.random() < 0.6:
            ops.append(["add", r.choice(words), r.randint(1, 5)])
        else:
            ops.append(["query", r.choice(["a", "ab", "b", "abc", ""])])
    return {"k": r.randint(1, 3), "operations": ops}


def _lb_brute_hashring(operations):
    servers, out = [], []
    for op in operations:
        name = op[0]
        if name == "addServer":
            if op[1] not in servers:
                servers.append(op[1])
            out.append(None)
        elif name == "removeServer":
            if op[1] in servers:
                servers.remove(op[1])
            out.append(None)
        else:
            key = op[1]
            if not servers:
                out.append(None)
            else:
                ss = sorted(servers)
                nxt = [s for s in ss if s >= key]
                out.append(nxt[0] if nxt else ss[0])
    return out


def _lb_hashring_case(r):
    ops = []
    for _ in range(r.randint(1, 12)):
        c = r.random()
        if c < 0.4:
            ops.append(["addServer", r.randint(0, 50)])
        elif c < 0.55:
            ops.append(["removeServer", r.randint(0, 50)])
        else:
            ops.append(["getServer", r.randint(0, 50)])
    return {"operations": ops}


add("calendar-booking", "Calendar Booking", "medium",
    ["design", "intervals", "binary-search"], "calendarBooking",
    [("operations", "int[][]")], "bool[]",
    """
Replay a sequence of booking `operations`, each `["book", start, end]` for the
half-open interval `[start, end)`. Return **a list of booleans**: `true` if the
interval does **not** overlap any previously booked interval (the booking is then
kept), or `false` if it overlaps (and is discarded).

## Constraints
- `1 <= len(operations) <= 10^4`.
- `0 <= start < end <= 10^9`.

## Examples
Input: `operations = [["book",10,20],["book",15,25],["book",20,30]]`
Output: `[true,false,true]`
Explanation: `[15,25)` overlaps `[10,20)`; `[20,30)` touches but does not overlap.

Input: `operations = [["book",0,5],["book",5,10]]`
Output: `[true,true]`

Input: `operations = [["book",1,4],["book",2,3]]`
Output: `[true,false]`
""",
    """def calendarBooking(operations):
    booked, out = [], []
    for op in operations:
        _, s, e = op
        ok = all(not (s < be and bs < e) for bs, be in booked)
        if ok:
            booked.append((s, e))
            out.append(True)
        else:
            out.append(False)
    return out
""",
    visible=[{"operations": [["book", 10, 20], ["book", 15, 25], ["book", 20, 30]]},
             {"operations": [["book", 0, 5], ["book", 5, 10]]},
             {"operations": [["book", 1, 4], ["book", 2, 3]]}],
    hidden=[{"operations": [["book", 0, 10]]},
            {"operations": [["book", 5, 10], ["book", 0, 6], ["book", 0, 5]]}],
    gen=lambda r: [_lb_calendar_case(r) for _ in range(10)],
    brute=_lb_brute_calendar,
    checks=[({"operations": [["book", 10, 20], ["book", 15, 25], ["book", 20, 30]]},
             [True, False, True])])

add("in-memory-key-value-store", "In Memory Key Value Store", "medium",
    ["design", "hash-table"], "kvStore", [("operations", "any[][]")], "any[]",
    """
Replay `operations` against a versioned key-value store and return **the list of
results**. Operations are: `["set", key, value]` → `null`; `["get", key]` → the
current value or `null` if absent; `["delete", key]` → `null`; `["snapshot"]` →
returns a new version id (`0, 1, 2, ...`) capturing the current contents;
`["getAt", key, id]` → the value of `key` in snapshot `id` (or `null` if absent or
`id` is invalid).

## Constraints
- `1 <= len(operations) <= 10^5`.
- Snapshot ids are assigned in increasing order starting from `0`.

## Examples
Input: `operations = [["set","a",1],["snapshot"],["set","a",2],["get","a"],["getAt","a",0],["delete","a"],["get","a"]]`
Output: `[null,0,null,2,1,null,null]`

Input: `operations = [["get","x"]]`
Output: `[null]`

Input: `operations = [["set","k",9],["snapshot"],["delete","k"],["getAt","k",0]]`
Output: `[null,0,null,9]`
""",
    """def kvStore(operations):
    store, snaps, out = {}, [], []
    for op in operations:
        name = op[0]
        if name == "set":
            store[op[1]] = op[2]
            out.append(None)
        elif name == "get":
            out.append(store.get(op[1]))
        elif name == "delete":
            store.pop(op[1], None)
            out.append(None)
        elif name == "snapshot":
            snaps.append(dict(store))
            out.append(len(snaps) - 1)
        else:
            k, sid = op[1], op[2]
            out.append(snaps[sid].get(k) if 0 <= sid < len(snaps) else None)
    return out
""",
    visible=[{"operations": [["set", "a", 1], ["snapshot"], ["set", "a", 2], ["get", "a"],
                             ["getAt", "a", 0], ["delete", "a"], ["get", "a"]]},
             {"operations": [["get", "x"]]},
             {"operations": [["set", "k", 9], ["snapshot"], ["delete", "k"],
                             ["getAt", "k", 0]]}],
    hidden=[{"operations": [["set", "a", 1], ["set", "a", 2], ["get", "a"]]},
            {"operations": [["snapshot"], ["getAt", "a", 5]]}],
    gen=lambda r: [_lb_kv_case(r) for _ in range(10)],
    brute=_lb_brute_kv,
    checks=[({"operations": [["set", "a", 1], ["snapshot"], ["set", "a", 2], ["get", "a"],
                             ["getAt", "a", 0], ["delete", "a"], ["get", "a"]]},
             [None, 0, None, 2, 1, None, None])])

add("trie-prefix-search", "Trie Prefix Search", "medium",
    ["design", "trie", "string"], "trieOps", [("operations", "string[][]")], "any[]",
    """
Replay `operations` against a trie and return **the list of results**. Operations
are `["insert", word]` → `null`; `["search", word]` → `true` if the exact word was
inserted; `["startsWith", prefix]` → `true` if any inserted word starts with the
prefix.

## Constraints
- `1 <= len(operations) <= 10^4`; words are lowercase, length `1..2000`.

## Examples
Input: `operations = [["insert","apple"],["search","apple"],["search","app"],["startsWith","app"],["insert","app"],["search","app"]]`
Output: `[null,true,false,true,null,true]`

Input: `operations = [["search","a"]]`
Output: `[false]`

Input: `operations = [["insert","ab"],["startsWith","abc"]]`
Output: `[null,false]`
""",
    """def trieOps(operations):
    root, out = {}, []
    for op in operations:
        name, s = op[0], op[1]
        if name == "insert":
            node = root
            for ch in s:
                node = node.setdefault(ch, {})
            node["$"] = True
            out.append(None)
        else:
            node, ok = root, True
            for ch in s:
                if ch not in node:
                    ok = False
                    break
                node = node[ch]
            out.append((ok and "$" in node) if name == "search" else ok)
    return out
""",
    visible=[{"operations": [["insert", "apple"], ["search", "apple"], ["search", "app"],
                             ["startsWith", "app"], ["insert", "app"], ["search", "app"]]},
             {"operations": [["search", "a"]]},
             {"operations": [["insert", "ab"], ["startsWith", "abc"]]}],
    hidden=[{"operations": [["insert", "a"], ["insert", "a"], ["search", "a"]]},
            {"operations": [["insert", "abc"], ["startsWith", "ab"], ["search", "ab"]]}],
    gen=lambda r: [_lb_trie_case(r) for _ in range(10)],
    brute=_lb_brute_trie,
    checks=[({"operations": [["insert", "apple"], ["search", "apple"], ["search", "app"],
                             ["startsWith", "app"], ["insert", "app"], ["search", "app"]]},
             [None, True, False, True, None, True])])

add("autocomplete-top-k", "Autocomplete Top K", "hard",
    ["design", "trie", "heap", "sorting"], "autocomplete",
    [("k", "int"), ("operations", "any[][]")], "any[]",
    """
Replay `operations` against an autocomplete index and return **the list of
results**. Operations are `["add", sentence, count]` → `null` (adds `count` to the
sentence's historical frequency), and `["query", prefix]` → the list of up to `k`
sentences that start with `prefix`, ranked by **frequency descending, then
lexicographically ascending**.

## Constraints
- `1 <= k <= 10`, `1 <= len(operations) <= 10^4`.
- Sentences are non-empty lowercase strings (spaces allowed); `1 <= count <= 10^6`.

## Examples
Input: `k = 2, operations = [["add","ice cream",3],["add","icing",2],["add","igloo",5],["query","i"],["query","ic"]]`
Output: `[null,null,null,["igloo","ice cream"],["ice cream","icing"]]`

Input: `k = 2, operations = [["add","cat",1],["add","car",1],["query","ca"]]`
Output: `[null,null,["car","cat"]]`
Explanation: equal frequency, so lexicographic order wins.

Input: `k = 1, operations = [["query","z"]]`
Output: `[[]]`
""",
    """def autocomplete(k, operations):
    freq, out = {}, []
    for op in operations:
        if op[0] == "add":
            s, c = op[1], op[2]
            freq[s] = freq.get(s, 0) + c
            out.append(None)
        else:
            prefix = op[1]
            cands = [s for s in freq if s.startswith(prefix)]
            cands.sort(key=lambda s: (-freq[s], s))
            out.append(cands[:k])
    return out
""",
    visible=[{"k": 2, "operations": [["add", "ice cream", 3], ["add", "icing", 2],
                                     ["add", "igloo", 5], ["query", "i"], ["query", "ic"]]},
             {"k": 2, "operations": [["add", "cat", 1], ["add", "car", 1], ["query", "ca"]]},
             {"k": 1, "operations": [["query", "z"]]}],
    hidden=[{"k": 3, "operations": [["add", "a", 1], ["add", "ab", 1], ["add", "abc", 1],
                                    ["query", "a"]]},
            {"k": 1, "operations": [["add", "x", 1], ["add", "x", 5], ["query", "x"]]}],
    gen=lambda r: [_lb_autocomplete_case(r) for _ in range(10)],
    brute=_lb_brute_autocomplete,
    checks=[({"k": 2, "operations": [["add", "ice cream", 3], ["add", "icing", 2],
                                     ["add", "igloo", 5], ["query", "i"], ["query", "ic"]]},
             [None, None, None, ["igloo", "ice cream"], ["ice cream", "icing"]])])

add("consistent-hash-ring", "Consistent Hash Ring", "medium",
    ["design", "binary-search"], "hashRing", [("operations", "int[][]")], "any[]",
    """
A simplified consistent-hash ring places integer server ids on a ring at their own
value. Replay `operations` and return **the list of results**. Operations are
`["addServer", id]` → `null`; `["removeServer", id]` → `null`; `["getServer", key]`
→ the id of the first server **clockwise** from `key`, i.e. the smallest server id
`>= key`, wrapping to the smallest id if none qualifies. If there are no servers,
return `null`.

## Constraints
- `1 <= len(operations) <= 10^5`.
- `0 <= id, key <= 10^9`; adding an existing id or removing an absent id is a no-op.

## Examples
Input: `operations = [["addServer",10],["addServer",20],["addServer",30],["getServer",5],["getServer",15],["getServer",25],["getServer",35],["removeServer",20],["getServer",15]]`
Output: `[null,null,null,10,20,30,10,null,30]`

Input: `operations = [["getServer",1]]`
Output: `[null]`

Input: `operations = [["addServer",7],["getServer",7]]`
Output: `[null,7]`
""",
    """def hashRing(operations):
    import bisect
    servers, out = [], []
    for op in operations:
        name = op[0]
        if name == "addServer":
            i = bisect.bisect_left(servers, op[1])
            if i == len(servers) or servers[i] != op[1]:
                servers.insert(i, op[1])
            out.append(None)
        elif name == "removeServer":
            i = bisect.bisect_left(servers, op[1])
            if i < len(servers) and servers[i] == op[1]:
                servers.pop(i)
            out.append(None)
        else:
            key = op[1]
            if not servers:
                out.append(None)
            else:
                i = bisect.bisect_left(servers, key)
                out.append(servers[i] if i < len(servers) else servers[0])
    return out
""",
    visible=[{"operations": [["addServer", 10], ["addServer", 20], ["addServer", 30],
                             ["getServer", 5], ["getServer", 15], ["getServer", 25],
                             ["getServer", 35], ["removeServer", 20], ["getServer", 15]]},
             {"operations": [["getServer", 1]]},
             {"operations": [["addServer", 7], ["getServer", 7]]}],
    hidden=[{"operations": [["addServer", 5], ["addServer", 5], ["getServer", 5]]},
            {"operations": [["addServer", 1], ["removeServer", 1], ["getServer", 0]]}],
    gen=lambda r: [_lb_hashring_case(r) for _ in range(10)],
    brute=_lb_brute_hashring,
    checks=[({"operations": [["addServer", 10], ["addServer", 20], ["addServer", 30],
                             ["getServer", 5], ["getServer", 15], ["getServer", 25],
                             ["getServer", 35], ["removeServer", 20], ["getServer", 15]]},
             [None, None, None, 10, 20, 30, 10, None, 30])])

# ===========================================================================
# qb3_large.txt import — Batch 1: grid / matrix
# ===========================================================================

def _qb_sorted_matrix(r):
    m, n = r.randint(1, 5), r.randint(1, 5)
    vals = sorted(r.sample(range(-40, 80), m * n))
    return [vals[i * n:(i + 1) * n] for i in range(m)]


def _qb_noninc_matrix(r):
    m, n = r.randint(1, 6), r.randint(1, 6)
    vals = sorted([r.randint(-15, 15) for _ in range(m * n)], reverse=True)
    return [vals[i * n:(i + 1) * n] for i in range(m)]


def _qb_bin_matrix(r, m_hi=6, n_hi=6, p=0.5):
    m, n = r.randint(1, m_hi), r.randint(1, n_hi)
    return [[1 if r.random() < p else 0 for _ in range(n)] for _ in range(m)]


def _qb_board(r):
    m, n = r.randint(1, 6), r.randint(1, 6)
    return [["O" if r.random() < 0.5 else "X" for _ in range(n)] for _ in range(m)]


def _b_falling(matrix):
    rows, cols = len(matrix), len(matrix[0])
    best = [float("inf")]

    def go(r, c, s):
        s += matrix[r][c]
        if r == rows - 1:
            best[0] = min(best[0], s)
            return
        for nc in (c - 1, c, c + 1):
            if 0 <= nc < cols:
                go(r + 1, nc, s)

    for c in range(cols):
        go(0, c, 0)
    return best[0]


def _b_enclaves(grid):
    from collections import deque
    m, n = len(grid), len(grid[0])
    reach = [[False] * n for _ in range(m)]
    q = deque()
    for r in range(m):
        for c in range(n):
            if (r in (0, m - 1) or c in (0, n - 1)) and grid[r][c] == 1:
                reach[r][c] = True
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1 and not reach[nr][nc]:
                reach[nr][nc] = True
                q.append((nr, nc))
    return sum(1 for r in range(m) for c in range(n)
              if grid[r][c] == 1 and not reach[r][c])


def _b_surround(board):
    from collections import deque
    m, n = len(board), len(board[0])
    safe = [[False] * n for _ in range(m)]
    q = deque()
    for r in range(m):
        for c in range(n):
            if (r in (0, m - 1) or c in (0, n - 1)) and board[r][c] == "O":
                safe[r][c] = True
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and board[nr][nc] == "O" and not safe[nr][nc]:
                safe[nr][nc] = True
                q.append((nr, nc))
    return [["O" if (board[r][c] == "O" and safe[r][c]) else "X"
             for c in range(n)] for r in range(m)]


def _b_squares(matrix):
    m, n = len(matrix), len(matrix[0])
    total = 0
    for r in range(m):
        for c in range(n):
            k = 0
            while (r + k < m and c + k < n and
                   all(matrix[r + i][c + j] == 1
                       for i in range(k + 1) for j in range(k + 1))):
                k += 1
            total += k
    return total


def _b_maxrect(matrix):
    m, n = len(matrix), len(matrix[0])
    pre = [[0] * (n + 1) for _ in range(m + 1)]
    for r in range(m):
        for c in range(n):
            pre[r + 1][c + 1] = (matrix[r][c] + pre[r][c + 1] +
                                 pre[r + 1][c] - pre[r][c])
    best = 0
    for r1 in range(m):
        for r2 in range(r1, m):
            for c1 in range(n):
                for c2 in range(c1, n):
                    area = (r2 - r1 + 1) * (c2 - c1 + 1)
                    s = (pre[r2 + 1][c2 + 1] - pre[r1][c2 + 1] -
                         pre[r2 + 1][c1] + pre[r1][c1])
                    if s == area:
                        best = max(best, area)
    return best


def _b_toeplitz(matrix):
    from collections import defaultdict
    d = defaultdict(set)
    for r in range(len(matrix)):
        for c in range(len(matrix[0])):
            d[r - c].add(matrix[r][c])
    return all(len(s) == 1 for s in d.values())


add("search-sorted-matrix", "Search Sorted Matrix", "medium",
    ["array", "matrix", "binary-search"], "searchMatrix",
    [("matrix", "int[][]"), ("target", "int")], "bool",
    """
Each row of `matrix` is sorted left-to-right, and the first value of every row is
greater than the last value of the previous row — so the whole matrix is sorted if
read row by row. Return **`true` if `target` appears in the matrix**, otherwise
`false`. Aim for `O(log(m*n))` time.

## Constraints
- `1 <= len(matrix), len(matrix[0]) <= 500`
- `-10^9 <= matrix[i][j], target <= 10^9`

## Examples
Input: `matrix = [[1,3,5],[7,9,11]], target = 9`
Output: `true`
Explanation: `9` sits at row 1, column 1.

Input: `matrix = [[1,3,5],[7,9,11]], target = 4`
Output: `false`
Explanation: No cell holds `4`.
""",
    """def searchMatrix(matrix, target):
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = matrix[mid // n][mid % n]
        if v == target:
            return True
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False
""",
    visible=[{"matrix": [[1, 3, 5], [7, 9, 11]], "target": 9},
             {"matrix": [[1, 3, 5], [7, 9, 11]], "target": 4}],
    hidden=[{"matrix": [[5]], "target": 5}, {"matrix": [[5]], "target": 2},
            {"matrix": [[1, 2, 3, 4, 5, 6]], "target": 6},
            {"matrix": [[1], [3], [5], [7]], "target": 4},
            {"matrix": [[r * 8 + c for c in range(8)] for r in range(8)],
             "target": 63}],
    gen=lambda r: [{"matrix": (M := _qb_sorted_matrix(r)),
                    "target": r.choice([r.choice(r.choice(M)),
                                        r.randint(-50, 90)])} for _ in range(8)],
    brute=lambda matrix, target: any(target in row for row in matrix),
    checks=[({"matrix": [[1, 3, 5], [7, 9, 11]], "target": 9}, True),
            ({"matrix": [[1, 3, 5], [7, 9, 11]], "target": 4}, False)])

add("minimum-falling-path-sum", "Minimum Falling Path Sum", "medium",
    ["matrix", "dynamic-programming"], "minFallingPathSum",
    [("matrix", "int[][]")], "int",
    """
A falling path starts at any cell in the top row and chooses one cell per row,
where each step moves to the same column or a diagonally adjacent column in the
next row. Return the **minimum sum** of any falling path through the square
`matrix`.

![Example 1: a minimum falling path through a 3x3 grid](/problems/minimum-falling-path-sum/assets/example-1.svg)

## Constraints
- `1 <= len(matrix) == len(matrix[i]) <= 200`
- `-10^4 <= matrix[i][j] <= 10^4`

## Examples
Input: `matrix = [[2,1,3],[6,5,4],[7,8,9]]`
Output: `13`
Explanation: The path `1 -> 4 -> 8` has the smallest sum, `13`.

Input: `matrix = [[-19,57],[-40,-5]]`
Output: `-59`
Explanation: Take `-19` then `-40`.
""",
    """def minFallingPathSum(matrix):
    rows, cols = len(matrix), len(matrix[0])
    dp = list(matrix[0])
    for r in range(1, rows):
        ndp = [0] * cols
        for c in range(cols):
            best = dp[c]
            if c > 0:
                best = min(best, dp[c - 1])
            if c < cols - 1:
                best = min(best, dp[c + 1])
            ndp[c] = matrix[r][c] + best
        dp = ndp
    return min(dp)
""",
    visible=[{"matrix": [[2, 1, 3], [6, 5, 4], [7, 8, 9]]},
             {"matrix": [[-19, 57], [-40, -5]]}],
    hidden=[{"matrix": [[7]]}, {"matrix": [[1, 2], [3, 4]]},
            {"matrix": [[-1, -1], [-1, -1]]},
            {"matrix": [[100, -100, 100], [-100, 100, -100], [100, -100, 100]]}],
    gen=lambda r: [{"matrix": _rand_square(r)} for _ in range(8)],
    brute=_b_falling,
    checks=[({"matrix": [[2, 1, 3], [6, 5, 4], [7, 8, 9]]}, 13),
            ({"matrix": [[-19, 57], [-40, -5]]}, -59)],
    assets={"example-1.svg": figures.falling_path_svg(
        [[2, 1, 3], [6, 5, 4], [7, 8, 9]], [(0, 1), (1, 2), (2, 1)])})

add("number-of-enclaves", "Number of Enclaves", "medium",
    ["matrix", "graph", "flood-fill"], "numEnclaves",
    [("grid", "int[][]")], "int",
    """
`grid` is a binary matrix where `1` is land and `0` is sea. Moving only up, down,
left, or right through land cells, return the **number of land cells from which you
can never walk off the boundary** of the grid.

![Example 1: enclaves are land cells that cannot reach the border](/problems/number-of-enclaves/assets/example-1.svg)

## Constraints
- `1 <= len(grid), len(grid[0]) <= 500`
- `grid[i][j]` is `0` or `1`

## Examples
Input: `grid = [[0,0,0,0],[1,0,1,0],[0,1,1,0],[0,0,0,0]]`
Output: `3`
Explanation: The three central land cells are walled in by sea.

Input: `grid = [[1,0],[0,1]]`
Output: `0`
Explanation: Every land cell already touches the boundary.
""",
    """def numEnclaves(grid):
    from collections import deque
    m, n = len(grid), len(grid[0])
    grid = [row[:] for row in grid]
    q = deque()
    for r in range(m):
        for c in range(n):
            if (r in (0, m - 1) or c in (0, n - 1)) and grid[r][c] == 1:
                grid[r][c] = 0
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                grid[nr][nc] = 0
                q.append((nr, nc))
    return sum(sum(row) for row in grid)
""",
    visible=[{"grid": [[0, 0, 0, 0], [1, 0, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]]},
             {"grid": [[1, 0], [0, 1]]}],
    hidden=[{"grid": [[0]]}, {"grid": [[1]]},
            {"grid": [[1, 1, 1], [1, 0, 1], [1, 1, 1]]},
            {"grid": [[0, 0, 0], [0, 1, 0], [0, 0, 0]]}],
    gen=lambda r: [{"grid": _qb_bin_matrix(r)} for _ in range(8)],
    brute=_b_enclaves,
    checks=[({"grid": [[0, 0, 0, 0], [1, 0, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]]}, 3),
            ({"grid": [[1, 0], [0, 1]]}, 0)],
    assets={"example-1.svg": figures.islands_svg(
        [[0, 0, 0, 0], [1, 0, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]],
        "1 = land, 0 = sea")})

add("surrounded-regions", "Surrounded Regions", "medium",
    ["matrix", "graph", "flood-fill"], "solve",
    [("board", "string[][]")], "string[][]",
    """
`board` holds the letters `"X"` and `"O"`. Capture every region of `"O"`s that is
**not** connected to the border by flipping those cells to `"X"`; regions touching
any edge survive. Return the modified board.

## Constraints
- `1 <= len(board), len(board[0]) <= 200`
- `board[i][j]` is `"X"` or `"O"`

## Examples
Input: `board = [["X","X","X"],["X","O","X"],["X","X","X"]]`
Output: `[["X","X","X"],["X","X","X"],["X","X","X"]]`
Explanation: The single `"O"` is fully surrounded, so it is captured.

Input: `board = [["O","X"],["X","O"]]`
Output: `[["O","X"],["X","O"]]`
Explanation: Both `"O"` cells lie on the border and are safe.
""",
    """def solve(board):
    if not board or not board[0]:
        return board
    from collections import deque
    m, n = len(board), len(board[0])
    board = [row[:] for row in board]
    q = deque()
    for r in range(m):
        for c in range(n):
            if (r in (0, m - 1) or c in (0, n - 1)) and board[r][c] == "O":
                board[r][c] = "#"
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and board[nr][nc] == "O":
                board[nr][nc] = "#"
                q.append((nr, nc))
    for r in range(m):
        for c in range(n):
            board[r][c] = "O" if board[r][c] == "#" else "X"
    return board
""",
    visible=[{"board": [["X", "X", "X"], ["X", "O", "X"], ["X", "X", "X"]]},
             {"board": [["O", "X"], ["X", "O"]]}],
    hidden=[{"board": [["O"]]}, {"board": [["X"]]},
            {"board": [["X", "X", "X", "X"], ["X", "O", "O", "X"],
                       ["X", "X", "O", "X"], ["X", "O", "X", "X"]]},
            {"board": [["O", "O"], ["O", "O"]]}],
    gen=lambda r: [{"board": _qb_board(r)} for _ in range(8)],
    brute=_b_surround,
    checks=[({"board": [["X", "X", "X"], ["X", "O", "X"], ["X", "X", "X"]]},
             [["X", "X", "X"], ["X", "X", "X"], ["X", "X", "X"]])])

add("count-square-submatrices", "Count Square Submatrices of Ones", "medium",
    ["matrix", "dynamic-programming"], "countSquares",
    [("matrix", "int[][]")], "int",
    """
Given a binary `matrix`, return the **total number of square submatrices made up
entirely of `1`s** (squares of every size, counted separately).

## Constraints
- `1 <= len(matrix), len(matrix[0]) <= 300`
- `matrix[i][j]` is `0` or `1`

## Examples
Input: `matrix = [[1,1],[1,1]]`
Output: `5`
Explanation: Four `1x1` squares plus one `2x2` square.

Input: `matrix = [[1,0],[0,1]]`
Output: `2`
Explanation: Only the two diagonal `1x1` squares are all ones.
""",
    """def countSquares(matrix):
    m, n = len(matrix), len(matrix[0])
    dp = [[0] * n for _ in range(m)]
    total = 0
    for r in range(m):
        for c in range(n):
            if matrix[r][c] == 1:
                if r == 0 or c == 0:
                    dp[r][c] = 1
                else:
                    dp[r][c] = 1 + min(dp[r - 1][c], dp[r][c - 1], dp[r - 1][c - 1])
                total += dp[r][c]
    return total
""",
    visible=[{"matrix": [[1, 1], [1, 1]]}, {"matrix": [[1, 0], [0, 1]]}],
    hidden=[{"matrix": [[0]]}, {"matrix": [[1]]},
            {"matrix": [[0, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]]},
            {"matrix": [[1, 1, 1], [1, 1, 1], [1, 1, 1]]}],
    gen=lambda r: [{"matrix": _qb_bin_matrix(r, p=0.7)} for _ in range(8)],
    brute=_b_squares,
    checks=[({"matrix": [[1, 1], [1, 1]]}, 5), ({"matrix": [[1, 0], [0, 1]]}, 2),
            ({"matrix": [[0, 1, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]]}, 15)])

add("maximal-rectangle", "Maximal Rectangle of Ones", "hard",
    ["matrix", "stack", "monotonic-stack", "dynamic-programming"], "maximalRectangle",
    [("matrix", "int[][]")], "int",
    """
Given a binary `matrix`, return the **area of the largest rectangle** whose cells
are all `1`s.

## Constraints
- `1 <= len(matrix), len(matrix[0]) <= 200`
- `matrix[i][j]` is `0` or `1`

## Examples
Input: `matrix = [[1,0,1],[1,1,1]]`
Output: `3`
Explanation: The bottom row is a `1x3` rectangle of ones.

Input: `matrix = [[0,0],[0,0]]`
Output: `0`
Explanation: There are no `1`s, so the largest rectangle has area `0`.
""",
    """def maximalRectangle(matrix):
    if not matrix or not matrix[0]:
        return 0
    n = len(matrix[0])
    heights = [0] * n
    best = 0
    for row in matrix:
        for c in range(n):
            heights[c] = heights[c] + 1 if row[c] == 1 else 0
        stack = []
        for i in range(n + 1):
            h = heights[i] if i < n else 0
            while stack and heights[stack[-1]] >= h:
                ht = heights[stack.pop()]
                w = i if not stack else i - stack[-1] - 1
                best = max(best, ht * w)
            stack.append(i)
    return best
""",
    visible=[{"matrix": [[1, 0, 1], [1, 1, 1]]}, {"matrix": [[0, 0], [0, 0]]}],
    hidden=[{"matrix": [[1]]}, {"matrix": [[0]]},
            {"matrix": [[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1],
                        [1, 0, 0, 1, 0]]},
            {"matrix": [[1, 1, 1], [1, 1, 1]]}],
    gen=lambda r: [{"matrix": _qb_bin_matrix(r, p=0.65)} for _ in range(8)],
    brute=_b_maxrect,
    checks=[({"matrix": [[1, 0, 1], [1, 1, 1]]}, 3),
            ({"matrix": [[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1],
                         [1, 0, 0, 1, 0]]}, 6)])

add("count-negatives-sorted-matrix", "Count Negative Cells in Sorted Matrix",
    "easy", ["matrix", "binary-search", "two-pointers"], "countNegatives",
    [("grid", "int[][]")], "int",
    """
`grid` is sorted in **non-increasing** order both left-to-right along every row and
top-to-bottom down every column. Return the **count of negative numbers** in the
grid. Aim for `O(m + n)` time.

## Constraints
- `1 <= len(grid), len(grid[0]) <= 1000`
- `-10^9 <= grid[i][j] <= 10^9`

## Examples
Input: `grid = [[4,3,-1],[2,-1,-2],[-1,-2,-3]]`
Output: `6`
Explanation: Six entries are below zero.

Input: `grid = [[3,2],[1,0]]`
Output: `0`
Explanation: Nothing is negative (`0` does not count).
""",
    """def countNegatives(grid):
    n = len(grid[0])
    count = 0
    c = n - 1
    for row in grid:
        while c >= 0 and row[c] < 0:
            c -= 1
        count += n - 1 - c
    return count
""",
    visible=[{"grid": [[4, 3, -1], [2, -1, -2], [-1, -2, -3]]},
             {"grid": [[3, 2], [1, 0]]}],
    hidden=[{"grid": [[-1]]}, {"grid": [[1]]}, {"grid": [[0]]},
            {"grid": [[-1, -2, -3], [-4, -5, -6]]}],
    gen=lambda r: [{"grid": _qb_noninc_matrix(r)} for _ in range(8)],
    brute=lambda grid: sum(1 for row in grid for v in row if v < 0),
    checks=[({"grid": [[4, 3, -1], [2, -1, -2], [-1, -2, -3]]}, 6),
            ({"grid": [[3, 2], [1, 0]]}, 0)])

add("toeplitz-matrix", "Toeplitz Matrix Check", "easy",
    ["matrix"], "isToeplitz", [("matrix", "int[][]")], "bool",
    """
A matrix is **Toeplitz** when every top-left-to-bottom-right diagonal holds a single
repeated value. Return whether `matrix` is Toeplitz.

## Constraints
- `1 <= len(matrix), len(matrix[0]) <= 300`
- `0 <= matrix[i][j] <= 10^9`

## Examples
Input: `matrix = [[1,2,3],[4,1,2],[5,4,1]]`
Output: `true`
Explanation: Each descending diagonal is constant.

Input: `matrix = [[1,2],[2,2]]`
Output: `false`
Explanation: The main diagonal contains both `1` and `2`.
""",
    """def isToeplitz(matrix):
    m, n = len(matrix), len(matrix[0])
    for r in range(1, m):
        for c in range(1, n):
            if matrix[r][c] != matrix[r - 1][c - 1]:
                return False
    return True
""",
    visible=[{"matrix": [[1, 2, 3], [4, 1, 2], [5, 4, 1]]},
             {"matrix": [[1, 2], [2, 2]]}],
    hidden=[{"matrix": [[7]]}, {"matrix": [[1, 2, 3, 4]]}, {"matrix": [[1], [2], [3]]},
            {"matrix": [[3, 7, 0, 9], [5, 3, 7, 0], [9, 5, 3, 7]]}],
    gen=lambda r: [{"matrix": _rand_matrix(r)} for _ in range(6)],
    brute=_b_toeplitz,
    checks=[({"matrix": [[1, 2, 3], [4, 1, 2], [5, 4, 1]]}, True),
            ({"matrix": [[1, 2], [2, 2]]}, False)])

add("diagonal-difference", "Diagonal Sum Difference", "easy",
    ["matrix"], "diagonalDifference", [("matrix", "int[][]")], "int",
    """
Given a **square** `matrix`, return the absolute difference between the sum of its
primary diagonal (top-left to bottom-right) and the sum of its secondary diagonal
(top-right to bottom-left).

## Constraints
- `1 <= len(matrix) == len(matrix[i]) <= 1000`
- `-10^4 <= matrix[i][j] <= 10^4`

## Examples
Input: `matrix = [[1,2,3],[4,5,6],[7,8,9]]`
Output: `0`
Explanation: Both diagonals sum to `15`.

Input: `matrix = [[5,1],[2,3]]`
Output: `5`
Explanation: The diagonals sum to `8` (`5 + 3`) and `3` (`1 + 2`); `|8 - 3| = 5`.
""",
    """def diagonalDifference(matrix):
    n = len(matrix)
    primary = sum(matrix[i][i] for i in range(n))
    secondary = sum(matrix[i][n - 1 - i] for i in range(n))
    return abs(primary - secondary)
""",
    visible=[{"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]},
             {"matrix": [[5, 1], [2, 3]]}],
    hidden=[{"matrix": [[7]]}, {"matrix": [[-1, -2], [-3, -4]]},
            {"matrix": [[11, 2, 4], [4, 5, 6], [10, 8, -12]]}],
    gen=lambda r: [{"matrix": _rand_square(r)} for _ in range(6)],
    brute=lambda matrix: abs(sum(matrix[i][i] for i in range(len(matrix))) -
                             sum(row[len(matrix) - 1 - i]
                                 for i, row in enumerate(matrix))),
    checks=[({"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}, 0),
            ({"matrix": [[5, 1], [2, 3]]}, 5)])

add("strictly-increasing-rows", "Rows with Strictly Increasing Values", "easy",
    ["matrix"], "countIncreasingRows", [("matrix", "int[][]")], "int",
    """
Return how many rows of `matrix` are **strictly increasing** from left to right.

## Constraints
- `1 <= len(matrix), len(matrix[0]) <= 1000`
- `-10^9 <= matrix[i][j] <= 10^9`

## Examples
Input: `matrix = [[1,2,3],[3,2,1],[4,5,6]]`
Output: `2`
Explanation: Rows `0` and `2` strictly increase.

Input: `matrix = [[2,2],[1,3]]`
Output: `1`
Explanation: Row `0` is flat (`2,2`), only row `1` qualifies.
""",
    """def countIncreasingRows(matrix):
    count = 0
    for row in matrix:
        if all(row[i] < row[i + 1] for i in range(len(row) - 1)):
            count += 1
    return count
""",
    visible=[{"matrix": [[1, 2, 3], [3, 2, 1], [4, 5, 6]]},
             {"matrix": [[2, 2], [1, 3]]}],
    hidden=[{"matrix": [[5]]}, {"matrix": [[1], [2], [3]]},
            {"matrix": [[-3, -1, 0], [9, 8, 7], [1, 1, 2]]}],
    gen=lambda r: [{"matrix": _rand_matrix(r)} for _ in range(6)],
    brute=lambda matrix: sum(
        1 for row in matrix
        if all(row[i] < row[i + 1] for i in range(len(row) - 1))),
    checks=[({"matrix": [[1, 2, 3], [3, 2, 1], [4, 5, 6]]}, 2),
            ({"matrix": [[2, 2], [1, 3]]}, 1)])


# ===========================================================================
# qb3_large.txt import — Batch 2: arrays / sorting / sliding-window
# ===========================================================================

def _b_count_smaller(nums):
    return [sum(1 for j in range(i + 1, len(nums)) if nums[j] < nums[i])
            for i in range(len(nums))]


def _b_reverse_pairs(nums):
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums))
               if nums[i] > 2 * nums[j])


def _b_count_range_sum(nums, lower, upper):
    n, cnt = len(nums), 0
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if lower <= s <= upper:
                cnt += 1
    return cnt


def _b_max_gap(nums):
    if len(nums) < 2:
        return 0
    s = sorted(nums)
    return max(s[i + 1] - s[i] for i in range(len(s) - 1))


def _b_nearby_almost(nums, indexDiff, valueDiff):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, min(n, i + indexDiff + 1)):
            if abs(nums[i] - nums[j]) <= valueDiff:
                return True
    return False


def _b_reduce_x(nums, x):
    total = sum(nums)
    target = total - x
    if target < 0:
        return -1
    if target == 0:
        return len(nums)
    best = -1
    n = len(nums)
    for i in range(n):
        s = 0
        for j in range(i, n):
            s += nums[j]
            if s == target:
                best = max(best, j - i + 1)
            elif s > target:
                break
    return -1 if best < 0 else len(nums) - best


def _b_erasure(nums):
    n = len(nums)
    best = 0
    for i in range(n):
        seen = set()
        s = 0
        for j in range(i, n):
            if nums[j] in seen:
                break
            seen.add(nums[j])
            s += nums[j]
            best = max(best, s)
    return best


def _b_prod_less(nums, k):
    n, cnt = len(nums), 0
    for i in range(n):
        p = 1
        for j in range(i, n):
            p *= nums[j]
            if p < k:
                cnt += 1
            else:
                break
    return cnt


def _b_longest_ones(nums, k):
    n, best = len(nums), 0
    for i in range(n):
        zeros = 0
        for j in range(i, n):
            if nums[j] == 0:
                zeros += 1
            if zeros > k:
                break
            best = max(best, j - i + 1)
    return best


def _qb_doubled_case(r):
    if r.random() < 0.6:
        orig = [r.randint(0, 8) for _ in range(r.randint(1, 6))]
        changed = orig + [2 * x for x in orig]
        r.shuffle(changed)
        return {"changed": changed}
    return {"changed": [r.randint(0, 10) for _ in range(r.randint(1, 8))]}


def _b_doubled(changed):
    from collections import Counter
    if len(changed) % 2 != 0:
        return []
    cnt = Counter(changed)
    res = []
    for x in sorted(changed, reverse=True):
        if cnt[x] == 0:
            continue
        if x == 0:
            if cnt[0] < 2:
                return []
            cnt[0] -= 2
            res.append(0)
        else:
            if x % 2 != 0 or cnt[x // 2] == 0:
                return []
            cnt[x] -= 1
            cnt[x // 2] -= 1
            res.append(x // 2)
    return sorted(res)


def _qb_hand_case(r):
    g = r.randint(1, 4)
    if r.random() < 0.6:
        cards = []
        for _ in range(r.randint(1, 4)):
            start = r.randint(1, 8)
            cards += list(range(start, start + g))
        r.shuffle(cards)
        return {"hand": cards, "groupSize": g}
    return {"hand": [r.randint(1, 10) for _ in range(r.randint(1, 10))],
            "groupSize": g}


def _b_straight(hand, groupSize):
    from collections import Counter
    if len(hand) % groupSize != 0:
        return False
    cnt = Counter(hand)
    for _ in range(len(hand) // groupSize):
        start = min(k for k, v in cnt.items() if v > 0)
        for y in range(start, start + groupSize):
            if cnt.get(y, 0) <= 0:
                return False
            cnt[y] -= 1
    return True


def _b_mindev(nums):
    import itertools

    def reach(v):
        s, x = set(), v
        while True:
            s.add(x)
            if x % 2 == 0:
                x //= 2
            else:
                break
        s.add(min(s) * 2)
        return sorted(s)

    sets = [reach(v) for v in nums]
    best = float("inf")
    for combo in itertools.product(*sets):
        best = min(best, max(combo) - min(combo))
    return best


def _qb_median_case(r):
    n = r.randint(1, 12)
    k = r.choice([x for x in range(1, n + 1) if x % 2 == 1])
    return {"nums": [r.randint(-20, 20) for _ in range(n)], "k": k}


def _b_median_window(nums, k):
    import statistics
    return [statistics.median(nums[i:i + k]) for i in range(len(nums) - k + 1)]


add("count-smaller-after-self", "Count Smaller Numbers After Self", "hard",
    ["array", "binary-indexed-tree", "divide-and-conquer"], "countSmaller",
    [("nums", "int[]")], "int[]",
    """
For each index `i`, count how many values to the **right** of `i` are strictly
smaller than `nums[i]`. Return those counts as an array the same length as `nums`.
Aim for `O(n log n)`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `-10^9 <= nums[i] <= 10^9`

## Examples
Input: `nums = [5,2,6,1]`
Output: `[2,1,1,0]`
Explanation: Right of `5` are `2` and `1`; right of `2` is `1`; right of `6` is `1`.

Input: `nums = [-1]`
Output: `[0]`
Explanation: Nothing lies to the right of the only element.
""",
    """def countSmaller(nums):
    srt = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(srt)}
    m = len(srt)
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
    visible=[{"nums": [5, 2, 6, 1]}, {"nums": [-1]}],
    hidden=[{"nums": [2, 2, 2]}, {"nums": [1, 2, 3, 4]}, {"nums": [4, 3, 2, 1]},
            {"nums": [0]}],
    gen=lambda r: [{"nums": ilist(r, 1, 60, -25, 25)} for _ in range(10)],
    brute=_b_count_smaller,
    checks=[({"nums": [5, 2, 6, 1]}, [2, 1, 1, 0]), ({"nums": [-1]}, [0])])

add("reverse-pairs", "Reverse Pairs Count", "hard",
    ["array", "merge-sort", "divide-and-conquer"], "reversePairs",
    [("nums", "int[]")], "int",
    """
Count the pairs of indices `i < j` such that `nums[i] > 2 * nums[j]`. Aim for
`O(n log n)`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `-10^9 <= nums[i] <= 10^9`

## Examples
Input: `nums = [1,3,2,3,1]`
Output: `2`
Explanation: The pairs are `(i=1,j=4)` with `3 > 2*1` and `(i=3,j=4)` with `3 > 2*1`.

Input: `nums = [2,4,3,5,1]`
Output: `3`
Explanation: `(4,1)`, `(3,1)`, and `(5,1)` each satisfy `nums[i] > 2*nums[j]`.
""",
    """def reversePairs(nums):
    def msort(lo, hi):
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        cnt = msort(lo, mid) + msort(mid, hi)
        j = mid
        for i in range(lo, mid):
            while j < hi and nums[i] > 2 * nums[j]:
                j += 1
            cnt += j - mid
        nums[lo:hi] = sorted(nums[lo:hi])
        return cnt

    return msort(0, len(nums))
""",
    visible=[{"nums": [1, 3, 2, 3, 1]}, {"nums": [2, 4, 3, 5, 1]}],
    hidden=[{"nums": [1]}, {"nums": [5, 5, 5]}, {"nums": [-1, -2, -3]},
            {"nums": [2147483647, -2147483647]}],
    gen=lambda r: [{"nums": ilist(r, 1, 60, -15, 15)} for _ in range(10)],
    brute=_b_reverse_pairs,
    checks=[({"nums": [1, 3, 2, 3, 1]}, 2), ({"nums": [2, 4, 3, 5, 1]}, 3)])

add("count-range-sum", "Range Sum Count", "hard",
    ["array", "prefix-sum", "merge-sort"], "countRangeSum",
    [("nums", "int[]"), ("lower", "int"), ("upper", "int")], "int",
    """
Count the number of contiguous subarrays whose sum lies in the inclusive range
`[lower, upper]`. Aim for `O(n log n)`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `-10^9 <= nums[i] <= 10^9`
- `lower <= upper`

## Examples
Input: `nums = [-2,5,-1], lower = -2, upper = 2`
Output: `3`
Explanation: The qualifying subarray sums are `-2`, `2`, and `-1`.

Input: `nums = [0], lower = 0, upper = 0`
Output: `1`
Explanation: The single subarray sums to `0`.
""",
    """def countRangeSum(nums, lower, upper):
    prefix = [0]
    for x in nums:
        prefix.append(prefix[-1] + x)

    def msort(lo, hi):
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        cnt = msort(lo, mid) + msort(mid, hi)
        j = k = mid
        for i in range(lo, mid):
            while j < hi and prefix[j] - prefix[i] < lower:
                j += 1
            while k < hi and prefix[k] - prefix[i] <= upper:
                k += 1
            cnt += k - j
        prefix[lo:hi] = sorted(prefix[lo:hi])
        return cnt

    return msort(0, len(prefix))
""",
    visible=[{"nums": [-2, 5, -1], "lower": -2, "upper": 2},
             {"nums": [0], "lower": 0, "upper": 0}],
    hidden=[{"nums": [1, 2, 3], "lower": 3, "upper": 3},
            {"nums": [-1, -1, -1], "lower": -2, "upper": -1},
            {"nums": [5], "lower": 0, "upper": 4},
            {"nums": [0, 0, 0], "lower": 0, "upper": 0}],
    gen=lambda r: [{"nums": ilist(r, 1, 40, -8, 8),
                    "lower": (lo := r.randint(-10, 5)),
                    "upper": lo + r.randint(0, 12)} for _ in range(10)],
    brute=_b_count_range_sum,
    checks=[({"nums": [-2, 5, -1], "lower": -2, "upper": 2}, 3),
            ({"nums": [0], "lower": 0, "upper": 0}, 1)])

add("maximum-gap", "Maximum Gap After Sorting", "medium",
    ["array", "sorting", "bucket-sort"], "maximumGap",
    [("nums", "int[]")], "int",
    """
Return the **maximum difference between two successive values** once `nums` is
sorted in ascending order. If `nums` has fewer than two elements, return `0`. Aim
for linear time.

## Constraints
- `1 <= len(nums) <= 10^5`
- `0 <= nums[i] <= 10^9`

## Examples
Input: `nums = [3,6,9,1]`
Output: `3`
Explanation: Sorted order is `[1,3,6,9]`; the largest adjacent gap is `3`.

Input: `nums = [10]`
Output: `0`
Explanation: Fewer than two elements means a gap of `0`.
""",
    """def maximumGap(nums):
    if len(nums) < 2:
        return 0
    lo, hi = min(nums), max(nums)
    if lo == hi:
        return 0
    n = len(nums)
    size = max(1, (hi - lo) // (n - 1))
    count = (hi - lo) // size + 1
    buckets = [[None, None] for _ in range(count)]
    for x in nums:
        b = (x - lo) // size
        bmin, bmax = buckets[b]
        buckets[b][0] = x if bmin is None else min(bmin, x)
        buckets[b][1] = x if bmax is None else max(bmax, x)
    best, prev_max = 0, lo
    for bmin, bmax in buckets:
        if bmin is None:
            continue
        best = max(best, bmin - prev_max)
        prev_max = bmax
    return best
""",
    visible=[{"nums": [3, 6, 9, 1]}, {"nums": [10]}],
    hidden=[{"nums": [1, 1, 1]}, {"nums": [0, 100000]}, {"nums": [2, 5]},
            {"nums": [1, 10, 5, 3, 20]}],
    gen=lambda r: [{"nums": ilist(r, 1, 50, 0, 100000)} for _ in range(10)],
    brute=_b_max_gap,
    checks=[({"nums": [3, 6, 9, 1]}, 3), ({"nums": [10]}, 0)])

add("contains-nearby-almost-duplicate", "Contains Nearby Almost Duplicate",
    "hard", ["array", "sliding-window", "ordered-set"],
    "containsNearbyAlmostDuplicate",
    [("nums", "int[]"), ("indexDiff", "int"), ("valueDiff", "int")], "bool",
    """
Return `true` if there exist two indices `i != j` with `|i - j| <= indexDiff` and
`|nums[i] - nums[j]| <= valueDiff`, otherwise `false`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `-10^9 <= nums[i] <= 10^9`
- `0 <= indexDiff, valueDiff`

## Examples
Input: `nums = [1,2,3,1], indexDiff = 3, valueDiff = 0`
Output: `true`
Explanation: The two `1`s are 3 indices apart and equal.

Input: `nums = [1,5,9,1,5,9], indexDiff = 2, valueDiff = 3`
Output: `false`
Explanation: No two values within 2 indices differ by at most 3.
""",
    """def containsNearbyAlmostDuplicate(nums, indexDiff, valueDiff):
    if indexDiff <= 0 or valueDiff < 0:
        return False
    width = valueDiff + 1
    buckets = {}
    for i, x in enumerate(nums):
        b = x // width
        if b in buckets:
            return True
        if b - 1 in buckets and abs(x - buckets[b - 1]) <= valueDiff:
            return True
        if b + 1 in buckets and abs(x - buckets[b + 1]) <= valueDiff:
            return True
        buckets[b] = x
        if i >= indexDiff:
            del buckets[nums[i - indexDiff] // width]
    return False
""",
    visible=[{"nums": [1, 2, 3, 1], "indexDiff": 3, "valueDiff": 0},
             {"nums": [1, 5, 9, 1, 5, 9], "indexDiff": 2, "valueDiff": 3}],
    hidden=[{"nums": [1], "indexDiff": 1, "valueDiff": 0},
            {"nums": [8, 7, 15, 1, 6, 1, 9, 15], "indexDiff": 1, "valueDiff": 3},
            {"nums": [-3, 3], "indexDiff": 2, "valueDiff": 4},
            {"nums": [1, 2, 2, 1], "indexDiff": 0, "valueDiff": 5}],
    gen=lambda r: [{"nums": ilist(r, 1, 40, -25, 25),
                    "indexDiff": r.randint(0, 5),
                    "valueDiff": r.randint(0, 6)} for _ in range(12)],
    brute=_b_nearby_almost,
    checks=[({"nums": [1, 2, 3, 1], "indexDiff": 3, "valueDiff": 0}, True),
            ({"nums": [1, 5, 9, 1, 5, 9], "indexDiff": 2, "valueDiff": 3}, False)])

add("min-operations-reduce-x", "Minimum Operations to Reduce X to Zero",
    "medium", ["array", "sliding-window", "two-pointers"], "minOperations",
    [("nums", "int[]"), ("x", "int")], "int",
    """
Each move you remove the leftmost or rightmost element of `nums` and subtract it
from `x`. Return the **minimum number of moves** to make `x` exactly `0`, or `-1`
if it is impossible.

## Constraints
- `1 <= len(nums) <= 10^5`
- `1 <= nums[i] <= 10^4`
- `1 <= x <= 10^9`

## Examples
Input: `nums = [1,1,4,2,3], x = 5`
Output: `2`
Explanation: Remove `3` then `2` from the right.

Input: `nums = [5,6,7,8,9], x = 4`
Output: `-1`
Explanation: No sequence of end removals sums to `4`.
""",
    """def minOperations(nums, x):
    target = sum(nums) - x
    if target < 0:
        return -1
    if target == 0:
        return len(nums)
    best = -1
    left = s = 0
    for right, v in enumerate(nums):
        s += v
        while s > target and left <= right:
            s -= nums[left]
            left += 1
        if s == target:
            best = max(best, right - left + 1)
    return -1 if best < 0 else len(nums) - best
""",
    visible=[{"nums": [1, 1, 4, 2, 3], "x": 5},
             {"nums": [5, 6, 7, 8, 9], "x": 4}],
    hidden=[{"nums": [3, 2, 20, 1, 1, 3], "x": 10}, {"nums": [1], "x": 1},
            {"nums": [1], "x": 2}, {"nums": [1, 2, 3], "x": 6}],
    gen=lambda r: [{"nums": ilist(r, 1, 40, 1, 10), "x": r.randint(1, 60)}
                   for _ in range(12)],
    brute=_b_reduce_x,
    checks=[({"nums": [1, 1, 4, 2, 3], "x": 5}, 2),
            ({"nums": [5, 6, 7, 8, 9], "x": 4}, -1),
            ({"nums": [3, 2, 20, 1, 1, 3], "x": 10}, 5)])

add("maximum-erasure-value", "Maximum Erasure Value", "medium",
    ["array", "sliding-window", "hash-set"], "maximumUniqueSubarray",
    [("nums", "int[]")], "int",
    """
Return the **maximum sum** over all contiguous subarrays of `nums` whose elements
are all distinct.

## Constraints
- `1 <= len(nums) <= 10^5`
- `1 <= nums[i] <= 10^4`

## Examples
Input: `nums = [4,2,4,5,6]`
Output: `17`
Explanation: The distinct subarray `[2,4,5,6]` sums to `17`.

Input: `nums = [5,2,1,2,5,2,1,2,5]`
Output: `8`
Explanation: `[5,2,1]` is one best distinct subarray.
""",
    """def maximumUniqueSubarray(nums):
    seen = set()
    left = s = best = 0
    for v in nums:
        while v in seen:
            seen.remove(nums[left])
            s -= nums[left]
            left += 1
        seen.add(v)
        s += v
        best = max(best, s)
    return best
""",
    visible=[{"nums": [4, 2, 4, 5, 6]},
             {"nums": [5, 2, 1, 2, 5, 2, 1, 2, 5]}],
    hidden=[{"nums": [1]}, {"nums": [1, 1, 1]}, {"nums": [1, 2, 3, 4, 5]},
            {"nums": [10, 10, 9]}],
    gen=lambda r: [{"nums": ilist(r, 1, 40, 1, 12)} for _ in range(10)],
    brute=_b_erasure,
    checks=[({"nums": [4, 2, 4, 5, 6]}, 17),
            ({"nums": [5, 2, 1, 2, 5, 2, 1, 2, 5]}, 8)])

add("subarray-product-less-than-k", "Subarray Product Less Than K", "medium",
    ["array", "sliding-window", "two-pointers"], "numSubarrayProductLessThanK",
    [("nums", "int[]"), ("k", "int")], "int",
    """
Given an array of **positive** integers `nums` and an integer `k`, return the number
of contiguous subarrays whose product is strictly less than `k`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `1 <= nums[i] <= 1000`
- `0 <= k <= 10^9`

## Examples
Input: `nums = [10,5,2,6], k = 100`
Output: `8`
Explanation: Eight subarrays have product below `100`.

Input: `nums = [1,2,3], k = 0`
Output: `0`
Explanation: A positive product is never below `0`.
""",
    """def numSubarrayProductLessThanK(nums, k):
    if k <= 1:
        return 0
    prod = 1
    left = cnt = 0
    for right, v in enumerate(nums):
        prod *= v
        while prod >= k:
            prod //= nums[left]
            left += 1
        cnt += right - left + 1
    return cnt
""",
    visible=[{"nums": [10, 5, 2, 6], "k": 100}, {"nums": [1, 2, 3], "k": 0}],
    hidden=[{"nums": [1, 1, 1], "k": 2}, {"nums": [5], "k": 5},
            {"nums": [5], "k": 6}, {"nums": [2, 3, 4], "k": 1}],
    gen=lambda r: [{"nums": ilist(r, 1, 35, 1, 10), "k": r.randint(0, 60)}
                   for _ in range(12)],
    brute=_b_prod_less,
    checks=[({"nums": [10, 5, 2, 6], "k": 100}, 8),
            ({"nums": [1, 2, 3], "k": 0}, 0)])

add("max-consecutive-ones-iii", "Maximum Consecutive Ones With Flips", "medium",
    ["array", "sliding-window"], "longestOnes",
    [("nums", "int[]"), ("k", "int")], "int",
    """
Given a binary array `nums` and an integer `k`, return the length of the longest
contiguous subarray containing only `1`s after flipping at most `k` zeros to `1`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `nums[i]` is `0` or `1`
- `0 <= k <= len(nums)`

## Examples
Input: `nums = [1,1,1,0,0,0,1,1,1,1,0], k = 2`
Output: `6`
Explanation: Flip the two zeros at indices 4 and 5 (or 9 and 10) for six ones.

Input: `nums = [0,0,1,1,1,0,0], k = 0`
Output: `3`
Explanation: With no flips the longest run of ones has length `3`.
""",
    """def longestOnes(nums, k):
    left = zeros = best = 0
    for right, v in enumerate(nums):
        if v == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
""",
    visible=[{"nums": [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], "k": 2},
             {"nums": [0, 0, 1, 1, 1, 0, 0], "k": 0}],
    hidden=[{"nums": [0], "k": 0}, {"nums": [0], "k": 1},
            {"nums": [1, 1, 1], "k": 0},
            {"nums": [0, 0, 0, 1], "k": 4}],
    gen=lambda r: [{"nums": [r.randint(0, 1) for _ in range(r.randint(1, 40))],
                    "k": r.randint(0, 5)} for _ in range(12)],
    brute=_b_longest_ones,
    checks=[({"nums": [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], "k": 2}, 6),
            ({"nums": [0, 0, 1, 1, 1, 0, 0], "k": 0}, 3)])

add("find-original-doubled-array", "Find Original Array From Doubled", "medium",
    ["array", "greedy", "sorting"], "findOriginalArray",
    [("changed", "int[]")], "int[]",
    """
`changed` was formed from some `original` array by appending `2*x` for every value
`x` in `original`, then shuffling. Recover `original` and return it **sorted in
ascending order**, or return `[]` if `changed` could not have been formed this way.

## Constraints
- `1 <= len(changed) <= 10^5`
- `0 <= changed[i] <= 10^5`

## Examples
Input: `changed = [1,3,4,2,6,8]`
Output: `[1,3,4]`
Explanation: Doubling `[1,3,4]` gives `[2,6,8]`; together they form `changed`.

Input: `changed = [6,3,0,1]`
Output: `[]`
Explanation: The multiset cannot be split into value/double pairs.
""",
    """def findOriginalArray(changed):
    from collections import Counter
    if len(changed) % 2 != 0:
        return []
    cnt = Counter(changed)
    res = []
    for x in sorted(changed):
        if cnt[x] == 0:
            continue
        if x == 0:
            if cnt[0] < 2:
                return []
            cnt[0] -= 2
            res.append(0)
        else:
            cnt[x] -= 1
            if cnt[2 * x] <= 0:
                return []
            cnt[2 * x] -= 1
            res.append(x)
    return sorted(res)
""",
    visible=[{"changed": [1, 3, 4, 2, 6, 8]}, {"changed": [6, 3, 0, 1]}],
    hidden=[{"changed": [0, 0]}, {"changed": [1]}, {"changed": [2, 1]},
            {"changed": [4, 4, 16, 8, 8, 2]}],
    gen=lambda r: [_qb_doubled_case(r) for _ in range(12)],
    brute=_b_doubled,
    checks=[({"changed": [1, 3, 4, 2, 6, 8]}, [1, 3, 4]),
            ({"changed": [6, 3, 0, 1]}, []), ({"changed": [0, 0]}, [0])])

add("hand-of-straights", "Hand of Straights", "medium",
    ["array", "greedy", "hash-table"], "isNStraightHand",
    [("hand", "int[]"), ("groupSize", "int")], "bool",
    """
Determine whether the cards in `hand` can be partitioned into groups of exactly
`groupSize` cards where each group is `groupSize` **consecutive** values.

## Constraints
- `1 <= len(hand) <= 10^5`
- `1 <= hand[i] <= 10^9`
- `1 <= groupSize <= len(hand)`

## Examples
Input: `hand = [1,2,3,6,2,3,4,7,8], groupSize = 3`
Output: `true`
Explanation: Groups `[1,2,3]`, `[2,3,4]`, `[6,7,8]`.

Input: `hand = [1,2,3,4,5], groupSize = 4`
Output: `false`
Explanation: Five cards cannot split into groups of four.
""",
    """def isNStraightHand(hand, groupSize):
    from collections import Counter
    if len(hand) % groupSize != 0:
        return False
    cnt = Counter(hand)
    for x in sorted(cnt):
        c = cnt[x]
        if c > 0:
            for y in range(x, x + groupSize):
                if cnt[y] < c:
                    return False
                cnt[y] -= c
    return True
""",
    visible=[{"hand": [1, 2, 3, 6, 2, 3, 4, 7, 8], "groupSize": 3},
             {"hand": [1, 2, 3, 4, 5], "groupSize": 4}],
    hidden=[{"hand": [1], "groupSize": 1}, {"hand": [1, 1, 2, 2, 3, 3],
             "groupSize": 3}, {"hand": [8, 10, 12], "groupSize": 3},
            {"hand": [1, 2, 3, 4, 5, 6], "groupSize": 2}],
    gen=lambda r: [_qb_hand_case(r) for _ in range(12)],
    brute=_b_straight,
    checks=[({"hand": [1, 2, 3, 6, 2, 3, 4, 7, 8], "groupSize": 3}, True),
            ({"hand": [1, 2, 3, 4, 5], "groupSize": 4}, False)])

add("minimum-deviation", "Minimum Deviation in Array", "hard",
    ["array", "heap", "greedy"], "minimumDeviation",
    [("nums", "int[]")], "int",
    """
You may repeatedly **double** any odd element or **halve** any even element, any
number of times. Return the **minimum possible deviation** — the smallest achievable
difference between the maximum and minimum element of the array.

## Constraints
- `1 <= len(nums) <= 10^5`
- `1 <= nums[i] <= 10^9`

## Examples
Input: `nums = [1,2,3,4]`
Output: `1`
Explanation: Transform to `[2,2,3,4] -> ... -> [3,3,3,4]`-style values with deviation `1`.

Input: `nums = [4,1,5,20,3]`
Output: `3`
Explanation: The smallest reachable max-minus-min is `3`.
""",
    """def minimumDeviation(nums):
    import heapq
    heap, mn = [], float("inf")
    for x in nums:
        if x % 2 == 1:
            x *= 2
        heap.append(-x)
        mn = min(mn, x)
    heapq.heapify(heap)
    best = float("inf")
    while True:
        mx = -heapq.heappop(heap)
        best = min(best, mx - mn)
        if mx % 2 == 1:
            break
        mx //= 2
        mn = min(mn, mx)
        heapq.heappush(heap, -mx)
    return best
""",
    visible=[{"nums": [1, 2, 3, 4]}, {"nums": [4, 1, 5, 20, 3]}],
    hidden=[{"nums": [1]}, {"nums": [2, 2]}, {"nums": [3, 5]},
            {"nums": [10, 4, 3]}],
    gen=lambda r: [{"nums": ilist(r, 1, 6, 1, 24)} for _ in range(12)],
    brute=_b_mindev,
    checks=[({"nums": [1, 2, 3, 4]}, 1), ({"nums": [4, 1, 5, 20, 3]}, 3)])

add("k-pairs-smallest-sums", "Find K Pairs With Smallest Sums", "medium",
    ["heap", "array"], "kSmallestPairs",
    [("nums1", "int[]"), ("nums2", "int[]"), ("k", "int")], "int[][]",
    """
Given two ascending arrays `nums1` and `nums2` and an integer `k`, return the `k`
pairs `[a, b]` (one value from each array) with the smallest sums `a + b`. Return
them **ordered by increasing sum**, breaking ties by the smaller first value and
then the smaller second value. If fewer than `k` pairs exist, return all of them.

## Constraints
- `1 <= len(nums1), len(nums2) <= 10^4`
- `-10^9 <= nums1[i], nums2[i] <= 10^9`
- `1 <= k <= 1000`

## Examples
Input: `nums1 = [1,7,11], nums2 = [2,4,6], k = 3`
Output: `[[1,2],[1,4],[1,6]]`
Explanation: The three smallest sums all pair `1` from `nums1`.

Input: `nums1 = [1,1,2], nums2 = [1,2,3], k = 2`
Output: `[[1,1],[1,1]]`
Explanation: Both smallest pairs sum to `2`.
""",
    """def kSmallestPairs(nums1, nums2, k):
    import heapq
    if not nums1 or not nums2 or k <= 0:
        return []
    heap = []
    for i in range(min(k, len(nums1))):
        heapq.heappush(heap, (nums1[i] + nums2[0], i, 0))
    res = []
    while heap and len(res) < k:
        _, i, j = heapq.heappop(heap)
        res.append([nums1[i], nums2[j]])
        if j + 1 < len(nums2):
            heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))
    return res
""",
    visible=[{"nums1": [1, 7, 11], "nums2": [2, 4, 6], "k": 3},
             {"nums1": [1, 1, 2], "nums2": [1, 2, 3], "k": 2}],
    hidden=[{"nums1": [1], "nums2": [1], "k": 1},
            {"nums1": [1, 2], "nums2": [3], "k": 5},
            {"nums1": [-5, 0, 3], "nums2": [-2, 4], "k": 4},
            {"nums1": [1, 1, 2], "nums2": [1, 2, 3], "k": 100}],
    gen=lambda r: [{"nums1": sorted(ilist(r, 1, 8, -20, 20)),
                    "nums2": sorted(ilist(r, 1, 8, -20, 20)),
                    "k": r.randint(1, 12)} for _ in range(10)],
    brute=lambda nums1, nums2, k: sorted(
        ([a, b] for a in nums1 for b in nums2),
        key=lambda p: (p[0] + p[1], p[0], p[1]))[:k],
    checks=[({"nums1": [1, 7, 11], "nums2": [2, 4, 6], "k": 3},
             [[1, 2], [1, 4], [1, 6]]),
            ({"nums1": [1, 1, 2], "nums2": [1, 2, 3], "k": 2},
             [[1, 1], [1, 1]])])

add("sliding-window-median", "Sliding Window Median", "hard",
    ["array", "sliding-window", "heap"], "medianSlidingWindow",
    [("nums", "int[]"), ("k", "int")], "int[]",
    """
Given an integer array `nums` and an **odd** window size `k`, return an array of the
medians of every contiguous window of size `k`, left to right. (With odd `k` each
median is the middle value of the sorted window.)

## Constraints
- `1 <= k <= len(nums) <= 10^5`
- `k` is odd
- `-10^9 <= nums[i] <= 10^9`

## Examples
Input: `nums = [1,3,-1,-3,5,3,6,7], k = 3`
Output: `[1,-1,-1,3,5,6]`
Explanation: Each window's middle value after sorting.

Input: `nums = [1,2], k = 1`
Output: `[1,2]`
Explanation: A window of size `1` has the element itself as its median.
""",
    """def medianSlidingWindow(nums, k):
    import bisect
    window = sorted(nums[:k])
    res = [window[k // 2]]
    for i in range(k, len(nums)):
        window.pop(bisect.bisect_left(window, nums[i - k]))
        bisect.insort(window, nums[i])
        res.append(window[k // 2])
    return res
""",
    visible=[{"nums": [1, 3, -1, -3, 5, 3, 6, 7], "k": 3},
             {"nums": [1, 2], "k": 1}],
    hidden=[{"nums": [5], "k": 1}, {"nums": [1, 1, 1, 1], "k": 3},
            {"nums": [7, 6, 5, 4, 3, 2, 1], "k": 5},
            {"nums": [-1, -2, -3, -4, -5], "k": 1}],
    gen=lambda r: [_qb_median_case(r) for _ in range(12)],
    brute=_b_median_window,
    checks=[({"nums": [1, 3, -1, -3, 5, 3, 6, 7], "k": 3},
             [1, -1, -1, 3, 5, 6]), ({"nums": [1, 2], "k": 1}, [1, 2])])


# ===========================================================================
# qb3_large.txt import — Batch 3: stack / greedy / heap
# ===========================================================================

def _qb_carfleet(r):
    target = r.randint(10, 30)
    n = r.randint(1, 6)
    positions = r.sample(range(0, target), n)
    speeds = [r.randint(1, 5) for _ in range(n)]
    return {"target": target, "position": positions, "speed": speeds}


def _b_carfleet(target, position, speed):
    from fractions import Fraction
    cars = sorted(zip(position, speed), reverse=True)
    fleets, cur = 0, Fraction(-1)
    for pos, spd in cars:
        t = Fraction(target - pos, spd)
        if t > cur:
            fleets += 1
            cur = t
    return fleets


def _qb_asteroids(r):
    return {"asteroids": [r.choice([-1, 1]) * r.randint(1, 10)
                          for _ in range(r.randint(0, 8))]}


def _b_asteroids(asteroids):
    a = list(asteroids)
    changed = True
    while changed:
        changed = False
        for i in range(len(a) - 1):
            if a[i] > 0 and a[i + 1] < 0:
                if abs(a[i]) > abs(a[i + 1]):
                    del a[i + 1]
                elif abs(a[i]) < abs(a[i + 1]):
                    del a[i]
                else:
                    del a[i:i + 2]
                changed = True
                break
    return a


def _qb_removek(r):
    L = r.randint(1, 7)
    if L == 1:
        num = str(r.randint(0, 9))
    else:
        num = str(r.randint(1, 9)) + "".join(str(r.randint(0, 9))
                                             for _ in range(L - 1))
    return {"num": num, "k": r.randint(0, L)}


def _b_removek(num, k):
    from itertools import combinations
    n = len(num)
    keep = n - k
    if keep <= 0:
        return "0"
    best = None
    for combo in combinations(range(n), keep):
        val = int("".join(num[i] for i in combo))
        if best is None or val < best:
            best = val
    return str(best)


def _qb_calc_pm(r, depth=0):
    if depth >= 2 or r.random() < 0.5:
        return str(r.randint(0, 20))
    op = r.choice(["+", "-"])
    expr = f"{_qb_calc_pm(r, depth + 1)} {op} {_qb_calc_pm(r, depth + 1)}"
    if r.random() < 0.4:
        expr = f"({expr})"
    return expr


def _qb_calc_md(r):
    parts = [str(r.randint(0, 9))]
    for _ in range(r.randint(1, 5)):
        parts.append(r.choice(["+", "-", "*", "/"]))
        parts.append(str(r.randint(1, 9)))
    sep = " " if r.random() < 0.3 else ""
    return {"s": sep.join(parts)}


def _b_calc2(s):
    import re
    nums = [int(t) if t.isdigit() else t
            for t in re.findall(r"\d+|[+\-*/]", s)]
    stack = [nums[0]]
    i = 1
    while i < len(nums):
        op, val = nums[i], nums[i + 1]
        i += 2
        if op == "*":
            stack[-1] = stack[-1] * val
        elif op == "/":
            p = stack[-1]
            q = abs(p) // val
            stack[-1] = -q if p < 0 else q
        else:
            stack.append(op)
            stack.append(val)
    total = stack[0]
    i = 1
    while i < len(stack):
        op, val = stack[i], stack[i + 1]
        i += 2
        total = total + val if op == "+" else total - val
    return total


def _qb_invalid_parens(r):
    return {"s": "".join(r.choice("()a") for _ in range(r.randint(0, 9)))}


def _b_removeinvalid(s):
    from itertools import combinations

    def valid(t):
        c = 0
        for ch in t:
            if ch == "(":
                c += 1
            elif ch == ")":
                c -= 1
                if c < 0:
                    return False
        return c == 0

    paren_idx = [i for i, ch in enumerate(s) if ch in "()"]
    for r in range(len(paren_idx) + 1):
        results = set()
        for combo in combinations(paren_idx, r):
            cs = set(combo)
            t = "".join(ch for i, ch in enumerate(s) if i not in cs)
            if valid(t):
                results.add(t)
        if results:
            return sorted(results)
    return [""]


def _qb_arrows(r):
    pts = []
    for _ in range(r.randint(1, 6)):
        a = r.randint(0, 12)
        pts.append([a, a + r.randint(0, 6)])
    return {"points": pts}


def _b_arrows(points):
    if not points:
        return 0
    from itertools import combinations
    cand = sorted(set(p for pt in points for p in pt))
    n = len(points)
    for r in range(1, n + 1):
        for combo in combinations(cand, r):
            if all(any(s <= x <= e for x in combo) for s, e in points):
                return r
    return n


def _qb_ipo(r):
    n = r.randint(1, 5)
    return {"k": r.randint(1, n), "w": r.randint(0, 5),
            "profits": [r.randint(1, 10) for _ in range(n)],
            "capital": [r.randint(0, 8) for _ in range(n)]}


def _b_ipo(k, w, profits, capital):
    n = len(profits)
    best = [w]

    def go(cap, used, cnt):
        best[0] = max(best[0], cap)
        if cnt == k:
            return
        for i in range(n):
            if i not in used and capital[i] <= cap:
                go(cap + profits[i], used | {i}, cnt + 1)

    go(w, frozenset(), 0)
    return best[0]


def _qb_refuel(r):
    target = r.randint(10, 40)
    n = min(r.randint(0, 5), target - 1)
    positions = sorted(r.sample(range(1, target), n)) if n > 0 else []
    return {"target": target, "startFuel": r.randint(0, target),
            "stations": [[p, r.randint(1, 20)] for p in positions]}


def _b_refuel(target, startFuel, stations):
    n = len(stations)
    dp = [0] * (n + 1)
    dp[0] = startFuel
    for pos, fuel in stations:
        for t in range(n, 0, -1):
            if dp[t - 1] >= pos:
                dp[t] = max(dp[t], dp[t - 1] + fuel)
    for t in range(n + 1):
        if dp[t] >= target:
            return t
    return -1


def _qb_maxsubscore(r):
    n = r.randint(1, 6)
    return {"nums1": [r.randint(0, 10) for _ in range(n)],
            "nums2": [r.randint(1, 10) for _ in range(n)], "k": r.randint(1, n)}


def _b_maxsubscore(nums1, nums2, k):
    from itertools import combinations
    best = 0
    for combo in combinations(range(len(nums1)), k):
        best = max(best, sum(nums1[i] for i in combo) *
                   min(nums2[i] for i in combo))
    return best


def _qb_jobsched(r):
    n = r.randint(1, 7)
    start, end, profit = [], [], []
    for _ in range(n):
        s = r.randint(0, 10)
        start.append(s)
        end.append(s + r.randint(1, 6))
        profit.append(r.randint(1, 20))
    return {"start": start, "end": end, "profit": profit}


def _b_jobsched(start, end, profit):
    n = len(start)
    best = 0
    for mask in range(1 << n):
        chosen = sorted((i for i in range(n) if mask & (1 << i)),
                        key=lambda i: end[i])
        ok, last_end = True, -10 ** 18
        for i in chosen:
            if start[i] < last_end:
                ok = False
                break
            last_end = end[i]
        if ok:
            best = max(best, sum(profit[i] for i in chosen))
    return best


add("car-fleet", "Car Fleet Count", "medium",
    ["array", "stack", "monotonic-stack", "sorting"], "carFleet",
    [("target", "int"), ("position", "int[]"), ("speed", "int[]")], "int",
    """
Cars drive toward `target` on a one-lane road; car `i` starts at `position[i]` with
constant `speed[i]` and never passes another car (a faster car catches up and then
travels as one **fleet** at the slower car's speed). Return the **number of fleets**
that arrive at `target`.

## Constraints
- `1 <= len(position) == len(speed) <= 10^5`
- `0 < target <= 10^9`, positions are distinct and less than `target`
- `1 <= speed[i] <= 10^6`

## Examples
Input: `target = 12, position = [10,8,0,5,3], speed = [2,4,1,1,3]`
Output: `3`
Explanation: The cars merge into three fleets before reaching `target`.

Input: `target = 10, position = [3], speed = [3]`
Output: `1`
Explanation: A single car is its own fleet.
""",
    """def carFleet(target, position, speed):
    from fractions import Fraction
    cars = sorted(zip(position, speed), reverse=True)
    fleets = 0
    cur = Fraction(-1)
    for pos, spd in cars:
        t = Fraction(target - pos, spd)
        if t > cur:
            fleets += 1
            cur = t
    return fleets
""",
    visible=[{"target": 12, "position": [10, 8, 0, 5, 3], "speed": [2, 4, 1, 1, 3]},
             {"target": 10, "position": [3], "speed": [3]}],
    hidden=[{"target": 100, "position": [0, 2, 4], "speed": [3, 2, 1]},
            {"target": 10, "position": [0, 4, 2], "speed": [2, 1, 3]},
            {"target": 5, "position": [4, 3, 2, 1, 0], "speed": [1, 1, 1, 1, 1]}],
    gen=lambda r: [_qb_carfleet(r) for _ in range(12)],
    brute=_b_carfleet,
    checks=[({"target": 12, "position": [10, 8, 0, 5, 3],
              "speed": [2, 4, 1, 1, 3]}, 3),
            ({"target": 10, "position": [3], "speed": [3]}, 1)])

add("asteroid-collision", "Asteroid Collision", "medium",
    ["array", "stack", "simulation"], "asteroidCollision",
    [("asteroids", "int[]")], "int[]",
    """
Each value in `asteroids` is a non-zero asteroid: the sign is its direction
(positive moves right, negative moves left) and the magnitude is its size. Moving
asteroids collide when a right-mover meets a left-mover; the smaller one explodes,
and equal sizes both explode. Same-direction asteroids never meet. Return the
**state after all collisions**.

## Constraints
- `0 <= len(asteroids) <= 10^4`
- `-1000 <= asteroids[i] <= 1000`, `asteroids[i] != 0`

## Examples
Input: `asteroids = [5,10,-5]`
Output: `[5,10]`
Explanation: `10` and `-5` collide; `10` survives.

Input: `asteroids = [8,-8]`
Output: `[]`
Explanation: Equal opposite asteroids annihilate.
""",
    """def asteroidCollision(asteroids):
    stack = []
    for a in asteroids:
        alive = True
        while alive and a < 0 and stack and stack[-1] > 0:
            if stack[-1] < -a:
                stack.pop()
            elif stack[-1] == -a:
                stack.pop()
                alive = False
            else:
                alive = False
        if alive:
            stack.append(a)
    return stack
""",
    visible=[{"asteroids": [5, 10, -5]}, {"asteroids": [8, -8]}],
    hidden=[{"asteroids": []}, {"asteroids": [-2, -1, 1, 2]},
            {"asteroids": [10, 2, -5]}, {"asteroids": [-5, 5]},
            {"asteroids": [1, -2, -2, -2]}],
    gen=lambda r: [_qb_asteroids(r) for _ in range(12)],
    brute=_b_asteroids,
    checks=[({"asteroids": [5, 10, -5]}, [5, 10]),
            ({"asteroids": [8, -8]}, []),
            ({"asteroids": [10, 2, -5]}, [10])])

add("remove-k-digits", "Remove K Digits", "medium",
    ["string", "stack", "monotonic-stack", "greedy"], "removeKdigits",
    [("num", "string"), ("k", "int")], "string",
    """
Given a non-negative integer as the string `num`, remove exactly `k` digits so the
resulting number is as **small as possible**. Return it as a string with no leading
zeros (use `"0"` if everything is removed or the result is zero).

## Constraints
- `1 <= len(num) <= 10^5`
- `0 <= k <= len(num)`
- `num` has no leading zeros (except `num == "0"`)

## Examples
Input: `num = "1432219", k = 3`
Output: `"1219"`
Explanation: Drop `4`, `3`, and one `2`.

Input: `num = "10", k = 2`
Output: `"0"`
Explanation: Removing both digits leaves `0`.
""",
    """def removeKdigits(num, k):
    stack = []
    for d in num:
        while k and stack and stack[-1] > d:
            stack.pop()
            k -= 1
        stack.append(d)
    if k:
        stack = stack[:-k]
    res = "".join(stack).lstrip("0")
    return res if res else "0"
""",
    visible=[{"num": "1432219", "k": 3}, {"num": "10", "k": 2}],
    hidden=[{"num": "10200", "k": 1}, {"num": "9", "k": 1},
            {"num": "112", "k": 1}, {"num": "1234567890", "k": 9},
            {"num": "0", "k": 0}],
    gen=lambda r: [_qb_removek(r) for _ in range(12)],
    brute=_b_removek,
    checks=[({"num": "1432219", "k": 3}, "1219"), ({"num": "10", "k": 2}, "0"),
            ({"num": "10200", "k": 1}, "200")])

add("basic-calculator", "Basic Calculator With Parentheses", "hard",
    ["string", "stack", "math"], "calculate", [("s", "string")], "int",
    """
Evaluate the arithmetic expression `s` containing non-negative integers, `+`, `-`,
parentheses, and spaces, and return its integer value. (`-` is the binary subtraction
operator and may follow `(`.)

## Constraints
- `1 <= len(s) <= 3*10^5`
- `s` is a valid expression of digits, `+`, `-`, `(`, `)`, and spaces

## Examples
Input: `s = "1 + (2 - 3)"`
Output: `0`
Explanation: The parenthesized part is `-1`.

Input: `s = "(1+(4+5+2)-3)+(6+8)"`
Output: `23`
Explanation: Evaluates left to right respecting parentheses.
""",
    """def calculate(s):
    stack = []
    result = 0
    sign = 1
    num = 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == '+':
            result += sign * num
            num = 0
            sign = 1
        elif ch == '-':
            result += sign * num
            num = 0
            sign = -1
        elif ch == '(':
            stack.append(result)
            stack.append(sign)
            result = 0
            sign = 1
        elif ch == ')':
            result += sign * num
            num = 0
            result *= stack.pop()
            result += stack.pop()
    return result + sign * num
""",
    visible=[{"s": "1 + (2 - 3)"}, {"s": "(1+(4+5+2)-3)+(6+8)"}],
    hidden=[{"s": "0"}, {"s": "  42 "}, {"s": "2-1+2"},
            {"s": "(5)"}, {"s": "1-(2+3)"}, {"s": "10-(2-(3+1))"}],
    gen=lambda r: [{"s": _qb_calc_pm(r)} for _ in range(14)],
    brute=lambda s: eval(s.replace(" ", "")),
    checks=[({"s": "1 + (2 - 3)"}, 0), ({"s": "(1+(4+5+2)-3)+(6+8)"}, 23)])

add("basic-calculator-ii", "Basic Calculator With Multiplication", "medium",
    ["string", "stack", "math"], "calculate", [("s", "string")], "int",
    """
Evaluate the arithmetic expression `s` containing non-negative integers and the
operators `+`, `-`, `*`, `/` (no parentheses), respecting normal precedence.
Integer division **truncates toward zero**. Return the integer result.

## Constraints
- `1 <= len(s) <= 3*10^5`
- `s` is a valid expression; division is never by zero

## Examples
Input: `s = "3+2*2"`
Output: `7`
Explanation: `2*2` is evaluated first.

Input: `s = " 3/2 "`
Output: `1`
Explanation: `3/2` truncates to `1`.
""",
    """def calculate(s):
    stack = []
    num = 0
    op = '+'
    for ch in s + '+':
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch in '+-*/':
            if op == '+':
                stack.append(num)
            elif op == '-':
                stack.append(-num)
            elif op == '*':
                stack.append(stack.pop() * num)
            else:
                prev = stack.pop()
                q = abs(prev) // num
                stack.append(-q if prev < 0 else q)
            op = ch
            num = 0
    return sum(stack)
""",
    visible=[{"s": "3+2*2"}, {"s": " 3/2 "}],
    hidden=[{"s": "0"}, {"s": "14-3/2"}, {"s": "2*3*4"},
            {"s": "100/3/3"}, {"s": "1-1*5"}],
    gen=lambda r: [_qb_calc_md(r) for _ in range(14)],
    brute=_b_calc2,
    checks=[({"s": "3+2*2"}, 7), ({"s": " 3/2 "}, 1), ({"s": "14-3/2"}, 13)])

add("remove-invalid-parentheses", "Remove Invalid Parentheses", "hard",
    ["string", "backtracking", "breadth-first-search"],
    "removeInvalidParentheses", [("s", "string")], "string[]",
    """
Remove the **minimum** number of parentheses to make `s` a valid parenthesization,
and return **all** distinct strings achievable with that minimum number of removals.
The answer may be returned in any order; characters other than `(` and `)` are never
removed.

## Constraints
- `0 <= len(s) <= 25`
- `s` consists of lowercase letters and the characters `(` and `)`

## Examples
Input: `s = "()())()"`
Output: `["(())()","()()()"]`
Explanation: Removing one `)` yields these two valid strings.

Input: `s = ")("`
Output: `[""]`
Explanation: Both parentheses must be removed.
""",
    """def removeInvalidParentheses(s):
    def valid(t):
        c = 0
        for ch in t:
            if ch == '(':
                c += 1
            elif ch == ')':
                c -= 1
                if c < 0:
                    return False
        return c == 0

    level = {s}
    while True:
        found = [t for t in level if valid(t)]
        if found:
            return sorted(found)
        nxt = set()
        for t in level:
            for i in range(len(t)):
                if t[i] in '()':
                    nxt.add(t[:i] + t[i + 1:])
        if not nxt:
            return [""]
        level = nxt
""",
    visible=[{"s": "()())()"}, {"s": ")("}],
    hidden=[{"s": ""}, {"s": "a"}, {"s": "(a)())()"},
            {"s": "((("}, {"s": "()()"}],
    gen=lambda r: [_qb_invalid_parens(r) for _ in range(12)],
    brute=_b_removeinvalid,
    checks=[({"s": "()())()"}, ["(())()", "()()()"]),
            ({"s": ")("}, [""]), ({"s": ""}, [""])])

add("minimum-arrows-burst-balloons", "Minimum Arrows to Burst Balloons", "medium",
    ["array", "greedy", "sorting", "intervals"], "findMinArrowShots",
    [("points", "int[][]")], "int",
    """
Each balloon spans the inclusive horizontal interval `points[i] = [start, end]`. An
arrow shot straight up at coordinate `x` bursts every balloon with `start <= x <=
end`. Return the **minimum number of arrows** needed to burst all balloons.

## Constraints
- `1 <= len(points) <= 10^5`
- `points[i] = [start, end]` with `start <= end`

## Examples
Input: `points = [[10,16],[2,8],[1,6],[7,12]]`
Output: `2`
Explanation: One arrow in `[2,6]` and one in `[10,12]`.

Input: `points = [[1,2],[3,4],[5,6]]`
Output: `3`
Explanation: No balloons overlap, so each needs its own arrow.
""",
    """def findMinArrowShots(points):
    if not points:
        return 0
    points = sorted(points, key=lambda p: p[1])
    arrows = 1
    end = points[0][1]
    for s, e in points[1:]:
        if s > end:
            arrows += 1
            end = e
    return arrows
""",
    visible=[{"points": [[10, 16], [2, 8], [1, 6], [7, 12]]},
             {"points": [[1, 2], [3, 4], [5, 6]]}],
    hidden=[{"points": [[1, 2]]}, {"points": [[1, 2], [2, 3], [3, 4], [4, 5]]},
            {"points": [[0, 9], [0, 9], [0, 9]]},
            {"points": [[1, 6], [2, 8], [7, 12], [10, 16]]}],
    gen=lambda r: [_qb_arrows(r) for _ in range(12)],
    brute=_b_arrows,
    checks=[({"points": [[10, 16], [2, 8], [1, 6], [7, 12]]}, 2),
            ({"points": [[1, 2], [3, 4], [5, 6]]}, 3)])

add("ipo-project-selection", "IPO Project Selection", "hard",
    ["heap", "greedy", "sorting"], "findMaximizedCapital",
    [("k", "int"), ("w", "int"), ("profits", "int[]"), ("capital", "int[]")],
    "int",
    """
You can complete at most `k` projects starting with capital `w`. Project `i` needs
`capital[i]` capital up front (which you must already have) and then adds `profits[i]`
to your capital. Capital is never consumed. Return the **maximum capital** after
finishing at most `k` projects.

## Constraints
- `1 <= k <= 10^5`
- `0 <= w <= 10^9`
- `1 <= len(profits) == len(capital) <= 10^5`

## Examples
Input: `k = 2, w = 0, profits = [1,2,3], capital = [0,1,1]`
Output: `4`
Explanation: Take project 0 (capital 0) then project 2.

Input: `k = 1, w = 2, profits = [1,2,3], capital = [1,1,2]`
Output: `5`
Explanation: Take the project with profit 3.
""",
    """def findMaximizedCapital(k, w, profits, capital):
    import heapq
    projects = sorted(zip(capital, profits))
    available = []
    i = 0
    n = len(projects)
    for _ in range(k):
        while i < n and projects[i][0] <= w:
            heapq.heappush(available, -projects[i][1])
            i += 1
        if not available:
            break
        w += -heapq.heappop(available)
    return w
""",
    visible=[{"k": 2, "w": 0, "profits": [1, 2, 3], "capital": [0, 1, 1]},
             {"k": 1, "w": 2, "profits": [1, 2, 3], "capital": [1, 1, 2]}],
    hidden=[{"k": 3, "w": 0, "profits": [1], "capital": [1]},
            {"k": 1, "w": 0, "profits": [5], "capital": [0]},
            {"k": 10, "w": 0, "profits": [1, 2, 3], "capital": [0, 0, 0]}],
    gen=lambda r: [_qb_ipo(r) for _ in range(12)],
    brute=_b_ipo,
    checks=[({"k": 2, "w": 0, "profits": [1, 2, 3], "capital": [0, 1, 1]}, 4),
            ({"k": 1, "w": 2, "profits": [1, 2, 3], "capital": [1, 1, 2]}, 5)])

add("minimum-refueling-stops", "Minimum Number of Refueling Stops", "hard",
    ["heap", "greedy", "dynamic-programming"], "minRefuelStops",
    [("target", "int"), ("startFuel", "int"), ("stations", "int[][]")], "int",
    """
A car starts with `startFuel` liters and burns one liter per unit distance toward
`target`. Each `stations[i] = [position, fuel]` (sorted by position) can add `fuel`
liters when reached. Return the **minimum number of refueling stops** to reach
`target`, or `-1` if it is impossible.

## Constraints
- `1 <= target, startFuel <= 10^9`
- `0 <= len(stations) <= 500`
- stations are sorted by increasing `position`, all `< target`

## Examples
Input: `target = 100, startFuel = 10, stations = [[10,60],[20,30],[30,30],[60,40]]`
Output: `2`
Explanation: Refuel at positions 10 and 60.

Input: `target = 1, startFuel = 1, stations = []`
Output: `0`
Explanation: The starting fuel already reaches the target.
""",
    """def minRefuelStops(target, startFuel, stations):
    import heapq
    heap = []
    fuel = startFuel
    stops = 0
    i = 0
    n = len(stations)
    while fuel < target:
        while i < n and stations[i][0] <= fuel:
            heapq.heappush(heap, -stations[i][1])
            i += 1
        if not heap:
            return -1
        fuel += -heapq.heappop(heap)
        stops += 1
    return stops
""",
    visible=[{"target": 100, "startFuel": 10,
              "stations": [[10, 60], [20, 30], [30, 30], [60, 40]]},
             {"target": 1, "startFuel": 1, "stations": []}],
    hidden=[{"target": 100, "startFuel": 1, "stations": [[10, 100]]},
            {"target": 100, "startFuel": 50, "stations": [[25, 25], [50, 25]]},
            {"target": 1000, "startFuel": 299,
             "stations": [[13, 21], [26, 115], [100, 47], [225, 99]]}],
    gen=lambda r: [_qb_refuel(r) for _ in range(12)],
    brute=_b_refuel,
    checks=[({"target": 100, "startFuel": 10,
              "stations": [[10, 60], [20, 30], [30, 30], [60, 40]]}, 2),
            ({"target": 1, "startFuel": 1, "stations": []}, 0)])

add("maximum-subsequence-score", "Maximum Subsequence Score", "medium",
    ["heap", "greedy", "sorting"], "maxScore",
    [("nums1", "int[]"), ("nums2", "int[]"), ("k", "int")], "int",
    """
Choose exactly `k` indices. The score is `(sum of the chosen nums1) * (minimum of the
chosen nums2)`. Return the **maximum possible score**.

## Constraints
- `1 <= len(nums1) == len(nums2) <= 10^5`
- `1 <= k <= len(nums1)`
- `0 <= nums1[i] <= 10^5`, `1 <= nums2[i] <= 10^5`

## Examples
Input: `nums1 = [1,3,3,2], nums2 = [2,1,3,4], k = 3`
Output: `12`
Explanation: Indices with nums1 sum 6 and nums2 minimum 2 give 12.

Input: `nums1 = [4,2,3,1,1], nums2 = [7,5,10,9,6], k = 1`
Output: `30`
Explanation: Index 2 gives `3 * 10 = 30`.
""",
    """def maxScore(nums1, nums2, k):
    import heapq
    pairs = sorted(zip(nums2, nums1), reverse=True)
    heap = []
    total = 0
    best = 0
    for n2, n1 in pairs:
        heapq.heappush(heap, n1)
        total += n1
        if len(heap) > k:
            total -= heapq.heappop(heap)
        if len(heap) == k:
            best = max(best, total * n2)
    return best
""",
    visible=[{"nums1": [1, 3, 3, 2], "nums2": [2, 1, 3, 4], "k": 3},
             {"nums1": [4, 2, 3, 1, 1], "nums2": [7, 5, 10, 9, 6], "k": 1}],
    hidden=[{"nums1": [1], "nums2": [1], "k": 1},
            {"nums1": [0, 0, 0], "nums2": [1, 2, 3], "k": 2},
            {"nums1": [10, 10], "nums2": [5, 1], "k": 2}],
    gen=lambda r: [_qb_maxsubscore(r) for _ in range(12)],
    brute=_b_maxsubscore,
    checks=[({"nums1": [1, 3, 3, 2], "nums2": [2, 1, 3, 4], "k": 3}, 12),
            ({"nums1": [4, 2, 3, 1, 1], "nums2": [7, 5, 10, 9, 6], "k": 1}, 30)])

add("maximum-profit-job-scheduling", "Maximum Profit Job Scheduling", "hard",
    ["dynamic-programming", "binary-search", "sorting"], "jobScheduling",
    [("start", "int[]"), ("end", "int[]"), ("profit", "int[]")], "int",
    """
You have `n` jobs; job `i` runs in the half-open interval `[start[i], end[i])` and
pays `profit[i]`. Choose a subset of **non-overlapping** jobs (a job may start exactly
when another ends) to maximize total profit. Return that maximum profit.

## Constraints
- `1 <= len(start) == len(end) == len(profit) <= 5*10^4`
- `0 <= start[i] < end[i] <= 10^9`, `1 <= profit[i] <= 10^4`

## Examples
Input: `start = [1,2,3,3], end = [3,4,5,6], profit = [50,10,40,70]`
Output: `120`
Explanation: Run jobs `[1,3)` and `[3,6)` for `50 + 70`.

Input: `start = [1,1,1], end = [2,3,4], profit = [5,6,4]`
Output: `6`
Explanation: The three jobs all overlap, so take the best single one.
""",
    """def jobScheduling(start, end, profit):
    import bisect
    jobs = sorted(zip(end, start, profit))
    ends = [j[0] for j in jobs]
    n = len(jobs)
    res = [0] * (n + 1)
    for i in range(1, n + 1):
        e, s, p = jobs[i - 1]
        idx = bisect.bisect_right(ends, s)
        res[i] = max(res[i - 1], p + res[idx])
    return res[n]
""",
    visible=[{"start": [1, 2, 3, 3], "end": [3, 4, 5, 6], "profit": [50, 10, 40, 70]},
             {"start": [1, 1, 1], "end": [2, 3, 4], "profit": [5, 6, 4]}],
    hidden=[{"start": [1], "end": [2], "profit": [5]},
            {"start": [1, 2, 3, 4, 6], "end": [3, 5, 10, 6, 9],
             "profit": [20, 20, 100, 70, 60]},
            {"start": [0, 0, 0], "end": [1, 1, 1], "profit": [1, 2, 3]}],
    gen=lambda r: [_qb_jobsched(r) for _ in range(12)],
    brute=_b_jobsched,
    checks=[({"start": [1, 2, 3, 3], "end": [3, 4, 5, 6],
              "profit": [50, 10, 40, 70]}, 120),
            ({"start": [1, 1, 1], "end": [2, 3, 4], "profit": [5, 6, 4]}, 6)])


# ===========================================================================
# qb3_large.txt import — Batch 4a: sequence / palindrome DP
# ===========================================================================

def _qb_minwindow(r):
    return {"s": "".join(r.choice("abc") for _ in range(r.randint(1, 10))),
            "t": "".join(r.choice("abc") for _ in range(r.randint(1, 3)))}


def _b_minwindow(s, t):
    def is_subseq(sub):
        it = iter(sub)
        return all(ch in it for ch in t)

    n = len(s)
    best = None
    for i in range(n):
        for j in range(i, n):
            if is_subseq(s[i:j + 1]):
                if best is None or (j - i + 1) < best[1] - best[0] + 1:
                    best = (i, j)
                break
    return "" if best is None else s[best[0]:best[1] + 1]


def _qb_distinct(r):
    return {"s": "".join(r.choice("ab") for _ in range(r.randint(0, 8))),
            "t": "".join(r.choice("ab") for _ in range(r.randint(0, 4)))}


def _b_numdistinct(s, t):
    from functools import lru_cache

    @lru_cache(None)
    def go(i, j):
        if j == len(t):
            return 1
        if i == len(s):
            return 0
        res = go(i + 1, j)
        if s[i] == t[j]:
            res += go(i + 1, j + 1)
        return res

    return go(0, 0)


def _qb_regex_case(r):
    alpha = "ab"
    s = "".join(r.choice(alpha) for _ in range(r.randint(0, 6)))
    p = ""
    for _ in range(r.randint(0, 5)):
        p += r.choice(alpha + ".")
        if r.random() < 0.4:
            p += "*"
    return {"s": s, "p": p}


def _b_regex(s, p):
    import re
    return re.fullmatch(p, s) is not None


def _qb_scs(r):
    return {"str1": "".join(r.choice("ab") for _ in range(r.randint(0, 7))),
            "str2": "".join(r.choice("ab") for _ in range(r.randint(0, 7)))}


def _b_lcs(a, b):
    from functools import lru_cache

    @lru_cache(None)
    def lcs(i, j):
        if i == len(a) or j == len(b):
            return 0
        if a[i] == b[j]:
            return 1 + lcs(i + 1, j + 1)
        return max(lcs(i + 1, j), lcs(i, j + 1))

    return lcs(0, 0)


def _b_lps(s):
    return _b_lcs(s, s[::-1])


def _qb_pal_str(r):
    return {"s": "".join(r.choice("ab") for _ in range(r.randint(1, 10)))}


def _b_mincut(s):
    from functools import lru_cache
    n = len(s)

    @lru_cache(None)
    def go(i):
        if i == n:
            return -1
        best = float("inf")
        for j in range(i, n):
            if s[i:j + 1] == s[i:j + 1][::-1]:
                best = min(best, 1 + go(j + 1))
        return best

    return go(0)


def _qb_boolexpr(r):
    parts = [r.choice("TF")]
    for _ in range(r.randint(0, 5)):
        parts.append(r.choice("&|^"))
        parts.append(r.choice("TF"))
    return {"expr": "".join(parts)}


def _b_boolparen(expr):
    symbols, ops = expr[0::2], expr[1::2]

    def gen(i, j):
        if i == j:
            yield symbols[i] == "T"
            return
        for k in range(i, j):
            op = ops[k]
            for lv in gen(i, k):
                for rv in gen(k + 1, j):
                    if op == "&":
                        yield lv and rv
                    elif op == "|":
                        yield lv or rv
                    else:
                        yield lv != rv

    return sum(1 for v in gen(0, len(symbols) - 1) if v)


def _qb_arith(r):
    return {"nums": [r.randint(-10, 10) for _ in range(r.randint(1, 12))]}


def _b_arith(nums):
    n = len(nums)
    best = min(n, 1)
    for mask in range(1, 1 << n):
        idx = [i for i in range(n) if mask & (1 << i)]
        if len(idx) < 2:
            continue
        d = nums[idx[1]] - nums[idx[0]]
        if all(nums[idx[t + 1]] - nums[idx[t]] == d for t in range(len(idx) - 1)):
            best = max(best, len(idx))
    return best


def _qb_fib(r):
    n = r.randint(3, 10)
    return {"arr": sorted(r.sample(range(1, 40), n))}


def _b_fib(arr):
    n = len(arr)
    best = 0
    for mask in range(1 << n):
        idx = [i for i in range(n) if mask & (1 << i)]
        if len(idx) < 3:
            continue
        vals = [arr[i] for i in idx]
        if all(vals[t] == vals[t - 1] + vals[t - 2] for t in range(2, len(vals))):
            best = max(best, len(vals))
    return best


def _qb_russian(r):
    return {"envelopes": [[r.randint(1, 12), r.randint(1, 12)]
                          for _ in range(r.randint(1, 8))]}


def _b_russian(envelopes):
    env = sorted(envelopes)
    n = len(env)
    if n == 0:
        return 0
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            if env[j][0] < env[i][0] and env[j][1] < env[i][1]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


add("min-window-subsequence", "Minimum Window Subsequence", "hard",
    ["string", "dynamic-programming", "two-pointers"], "minWindow",
    [("s", "string"), ("t", "string")], "string",
    """
Return the **shortest contiguous substring** of `s` such that `t` is a subsequence
of it. If no such window exists, return `""`. If several windows tie for shortest,
return the one with the smallest starting index.

## Constraints
- `1 <= len(s) <= 2*10^4`
- `1 <= len(t) <= 100`

## Examples
Input: `s = "abcdebdde", t = "bde"`
Output: `"bcde"`
Explanation: `bcde` is the shortest window containing `b`, `d`, `e` in order.

Input: `s = "jmeqksfrsdcmsiwvaovztaqenprpvnbstl", t = "u"`
Output: `""`
Explanation: `u` never appears in `s`.
""",
    """def minWindow(s, t):
    n, m = len(s), len(t)
    best_len = float('inf')
    best_start = -1
    i = 0
    while i < n:
        j = 0
        k = i
        while k < n:
            if s[k] == t[j]:
                j += 1
                if j == m:
                    break
            k += 1
        if j < m:
            break
        end = k
        j = m - 1
        while True:
            if s[k] == t[j]:
                j -= 1
                if j < 0:
                    break
            k -= 1
        start = k
        if end - start + 1 < best_len:
            best_len = end - start + 1
            best_start = start
        i = start + 1
    return "" if best_start < 0 else s[best_start:best_start + best_len]
""",
    visible=[{"s": "abcdebdde", "t": "bde"},
             {"s": "jmeqksfrsdcmsiwvaovztaqenprpvnbstl", "t": "u"}],
    hidden=[{"s": "a", "t": "a"}, {"s": "a", "t": "b"},
            {"s": "abc", "t": "abc"}, {"s": "cnhczmccqouqadqtmjjzl", "t": "mm"},
            {"s": "aaaaa", "t": "aa"}],
    gen=lambda r: [_qb_minwindow(r) for _ in range(12)],
    brute=_b_minwindow,
    checks=[({"s": "abcdebdde", "t": "bde"}, "bcde"),
            ({"s": "jmeqksfrsdcmsiwvaovztaqenprpvnbstl", "t": "u"}, "")])

add("distinct-subsequences", "Distinct Subsequences Count", "hard",
    ["string", "dynamic-programming"], "numDistinct",
    [("s", "string"), ("t", "string")], "int",
    """
Return the number of **distinct subsequences** of `s` that equal `t`. (A subsequence
keeps relative order but may drop characters.)

## Constraints
- `0 <= len(s), len(t) <= 1000`
- The answer fits in a 64-bit integer.

## Examples
Input: `s = "rabbbit", t = "rabbit"`
Output: `3`
Explanation: Drop any one of the three middle `b`s.

Input: `s = "babgbag", t = "bag"`
Output: `5`
Explanation: There are five ways to pick `b`, `a`, `g` in order.
""",
    """def numDistinct(s, t):
    m = len(t)
    dp = [1] + [0] * m
    for ch in s:
        for j in range(m, 0, -1):
            if ch == t[j - 1]:
                dp[j] += dp[j - 1]
    return dp[m]
""",
    visible=[{"s": "rabbbit", "t": "rabbit"}, {"s": "babgbag", "t": "bag"}],
    hidden=[{"s": "", "t": ""}, {"s": "a", "t": ""}, {"s": "", "t": "a"},
            {"s": "aaa", "t": "aa"}, {"s": "abc", "t": "abcd"}],
    gen=lambda r: [_qb_distinct(r) for _ in range(12)],
    brute=_b_numdistinct,
    checks=[({"s": "rabbbit", "t": "rabbit"}, 3),
            ({"s": "babgbag", "t": "bag"}, 5), ({"s": "aaa", "t": "aa"}, 3)])

add("regex-full-match", "Regular Expression Full Match", "hard",
    ["string", "dynamic-programming", "recursion"], "isMatch",
    [("s", "string"), ("p", "string")], "bool",
    """
Implement matching of the **entire** string `s` against pattern `p`, where `.`
matches any single character and `*` matches zero or more of the **preceding**
element. The match must cover all of `s`.

## Constraints
- `0 <= len(s) <= 20`, `0 <= len(p) <= 30`
- `s` is lowercase letters; `p` is lowercase letters, `.`, and `*`
- every `*` has a valid preceding element

## Examples
Input: `s = "aab", p = "c*a*b"`
Output: `true`
Explanation: `c*` matches empty, `a*` matches `aa`, `b` matches `b`.

Input: `s = "mississippi", p = "mis*is*p*."`
Output: `false`
Explanation: No consistent way to consume the whole string.
""",
    """def isMatch(s, p):
    from functools import lru_cache

    @lru_cache(None)
    def dp(i, j):
        if j == len(p):
            return i == len(s)
        first = i < len(s) and (p[j] == s[i] or p[j] == '.')
        if j + 1 < len(p) and p[j + 1] == '*':
            return dp(i, j + 2) or (first and dp(i + 1, j))
        return first and dp(i + 1, j + 1)

    return dp(0, 0)
""",
    visible=[{"s": "aab", "p": "c*a*b"}, {"s": "mississippi", "p": "mis*is*p*."}],
    hidden=[{"s": "", "p": ""}, {"s": "", "p": "a*"}, {"s": "aa", "p": "a"},
            {"s": "ab", "p": ".*"}, {"s": "a", "p": "ab*"}],
    gen=lambda r: [_qb_regex_case(r) for _ in range(16)],
    brute=_b_regex,
    checks=[({"s": "aab", "p": "c*a*b"}, True),
            ({"s": "mississippi", "p": "mis*is*p*."}, False),
            ({"s": "ab", "p": ".*"}, True)])

add("shortest-common-supersequence-length",
    "Shortest Common Supersequence Length", "hard",
    ["string", "dynamic-programming"], "scsLength",
    [("str1", "string"), ("str2", "string")], "int",
    """
Return the **length of the shortest string** that has both `str1` and `str2` as
subsequences.

## Constraints
- `1 <= len(str1), len(str2) <= 1000`
- both strings are lowercase letters

## Examples
Input: `str1 = "abac", str2 = "cab"`
Output: `5`
Explanation: `cabac` is a shortest common supersequence and has length `5`.

Input: `str1 = "aaaaaaaa", str2 = "aaaaaaaa"`
Output: `8`
Explanation: The identical strings are their own supersequence.
""",
    """def scsLength(str1, str2):
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
    visible=[{"str1": "abac", "str2": "cab"},
             {"str1": "aaaaaaaa", "str2": "aaaaaaaa"}],
    hidden=[{"str1": "a", "str2": "b"}, {"str1": "a", "str2": "a"},
            {"str1": "abc", "str2": "def"}, {"str1": "geek", "str2": "eke"}],
    gen=lambda r: [_qb_scs(r) for _ in range(12)],
    brute=lambda str1, str2: len(str1) + len(str2) - _b_lcs(str1, str2),
    checks=[({"str1": "abac", "str2": "cab"}, 5),
            ({"str1": "aaaaaaaa", "str2": "aaaaaaaa"}, 8)])

add("longest-palindromic-subsequence", "Longest Palindromic Subsequence",
    "medium", ["string", "dynamic-programming"], "longestPalindromeSubseq",
    [("s", "string")], "int",
    """
Return the length of the **longest palindromic subsequence** of `s`.

## Constraints
- `1 <= len(s) <= 1000`
- `s` is lowercase letters

## Examples
Input: `s = "bbbab"`
Output: `4`
Explanation: `bbbb` is a palindromic subsequence.

Input: `s = "cbbd"`
Output: `2`
Explanation: `bb` is the longest palindromic subsequence.
""",
    """def longestPalindromeSubseq(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]
""",
    visible=[{"s": "bbbab"}, {"s": "cbbd"}],
    hidden=[{"s": "a"}, {"s": "aa"}, {"s": "ab"}, {"s": "abcba"},
            {"s": "abacdfgdcaba"}],
    gen=lambda r: [_qb_pal_str(r) for _ in range(12)],
    brute=_b_lps,
    checks=[({"s": "bbbab"}, 4), ({"s": "cbbd"}, 2), ({"s": "abcba"}, 5)])

add("min-insertions-palindrome", "Minimum Insertions to Palindrome", "medium",
    ["string", "dynamic-programming"], "minInsertions",
    [("s", "string")], "int",
    """
Return the **minimum number of characters** you must insert anywhere in `s` to make
it a palindrome.

## Constraints
- `1 <= len(s) <= 500`
- `s` is lowercase letters

## Examples
Input: `s = "zzazz"`
Output: `0`
Explanation: `zzazz` is already a palindrome.

Input: `s = "mbadm"`
Output: `2`
Explanation: One palindrome is `mbdadbm`, needing two insertions.
""",
    """def minInsertions(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]
""",
    visible=[{"s": "zzazz"}, {"s": "mbadm"}],
    hidden=[{"s": "a"}, {"s": "ab"}, {"s": "leetcode"}, {"s": "aab"},
            {"s": "abcabc"}],
    gen=lambda r: [_qb_pal_str(r) for _ in range(12)],
    brute=lambda s: len(s) - _b_lps(s),
    checks=[({"s": "zzazz"}, 0), ({"s": "mbadm"}, 2), ({"s": "leetcode"}, 5)])

add("palindrome-partition-min-cuts", "Palindrome Partition Minimum Cuts", "hard",
    ["string", "dynamic-programming"], "minCut", [("s", "string")], "int",
    """
Return the **minimum number of cuts** needed to partition `s` so that every part is
a palindrome.

## Constraints
- `1 <= len(s) <= 2000`
- `s` is lowercase letters

## Examples
Input: `s = "aab"`
Output: `1`
Explanation: One cut gives `"aa" | "b"`, both palindromes.

Input: `s = "a"`
Output: `0`
Explanation: A single character is already a palindrome.
""",
    """def minCut(s):
    n = len(s)
    pal = [[False] * n for _ in range(n)]
    for i in range(n):
        pal[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
    cuts = [0] * n
    for i in range(n):
        if pal[0][i]:
            cuts[i] = 0
        else:
            cuts[i] = min(cuts[k - 1] + 1 for k in range(1, i + 1) if pal[k][i])
    return cuts[n - 1]
""",
    visible=[{"s": "aab"}, {"s": "a"}],
    hidden=[{"s": "ab"}, {"s": "aba"}, {"s": "abccba"}, {"s": "noonabbad"},
            {"s": "cdd"}],
    gen=lambda r: [_qb_pal_str(r) for _ in range(12)],
    brute=_b_mincut,
    checks=[({"s": "aab"}, 1), ({"s": "a"}, 0), ({"s": "abccba"}, 0)])

add("boolean-parenthesization", "Boolean Parenthesization Count", "hard",
    ["string", "dynamic-programming", "interval-dp"], "countWays",
    [("expr", "string")], "int",
    """
`expr` is a boolean expression of operands `T` (true) and `F` (false) separated by
operators `&` (and), `|` (or), and `^` (xor). Return the number of ways to fully
parenthesize `expr` so that it evaluates to **true**.

## Constraints
- `1 <= len(expr) <= 199` with an odd length (operands and operators alternate)
- operands are `T`/`F`; operators are `&`, `|`, `^`

## Examples
Input: `expr = "T|F&T"`
Output: `2`
Explanation: `T|(F&T)` and `(T|F)&T` both evaluate to true.

Input: `expr = "T^F"`
Output: `1`
Explanation: The only parenthesization is true.
""",
    """def countWays(expr):
    from functools import lru_cache
    symbols = expr[0::2]
    ops = expr[1::2]
    n = len(symbols)

    @lru_cache(None)
    def solve(i, j, want):
        if i == j:
            return 1 if (symbols[i] == 'T') == want else 0
        total = 0
        for k in range(i, j):
            op = ops[k]
            lt, lf = solve(i, k, True), solve(i, k, False)
            rt, rf = solve(k + 1, j, True), solve(k + 1, j, False)
            tt, tf, ft, ff = lt * rt, lt * rf, lf * rt, lf * rf
            if op == '&':
                true_ways, false_ways = tt, tf + ft + ff
            elif op == '|':
                true_ways, false_ways = tt + tf + ft, ff
            else:
                true_ways, false_ways = tf + ft, tt + ff
            total += true_ways if want else false_ways
        return total

    return solve(0, n - 1, True)
""",
    visible=[{"expr": "T|F&T"}, {"expr": "T^F"}],
    hidden=[{"expr": "T"}, {"expr": "F"}, {"expr": "T^T^F"},
            {"expr": "F&F&F&T|T"}, {"expr": "T|T|T"}],
    gen=lambda r: [_qb_boolexpr(r) for _ in range(14)],
    brute=_b_boolparen,
    checks=[({"expr": "T|F&T"}, 2), ({"expr": "T^F"}, 1),
            ({"expr": "T^T^F"}, 0)])

add("longest-arithmetic-subsequence", "Longest Arithmetic Subsequence", "medium",
    ["array", "dynamic-programming", "hash-table"], "longestArithSeqLength",
    [("nums", "int[]")], "int",
    """
Return the length of the **longest arithmetic subsequence** of `nums` (a subsequence
whose consecutive differences are all equal).

## Constraints
- `1 <= len(nums) <= 1000`
- `-10^4 <= nums[i] <= 10^4`

## Examples
Input: `nums = [3,6,9,12]`
Output: `4`
Explanation: The whole array has common difference `3`.

Input: `nums = [9,4,7,2,10]`
Output: `3`
Explanation: `[4,7,10]` is arithmetic with difference `3`.
""",
    """def longestArithSeqLength(nums):
    n = len(nums)
    if n <= 1:
        return n
    dp = [{} for _ in range(n)]
    best = 1
    for i in range(n):
        for j in range(i):
            d = nums[i] - nums[j]
            dp[i][d] = dp[j].get(d, 1) + 1
            best = max(best, dp[i][d])
    return best
""",
    visible=[{"nums": [3, 6, 9, 12]}, {"nums": [9, 4, 7, 2, 10]}],
    hidden=[{"nums": [5]}, {"nums": [1, 1, 1, 1]}, {"nums": [20, 1, 15, 3, 10, 5, 8]},
            {"nums": [0, 0]}],
    gen=lambda r: [_qb_arith(r) for _ in range(10)],
    brute=_b_arith,
    checks=[({"nums": [3, 6, 9, 12]}, 4), ({"nums": [9, 4, 7, 2, 10]}, 3)])

add("longest-fibonacci-subsequence", "Longest Fibonacci-Like Subsequence",
    "medium", ["array", "dynamic-programming", "hash-table"],
    "lenLongestFibSubseq", [("arr", "int[]")], "int",
    """
Given a **strictly increasing** array `arr`, return the length of the longest
Fibonacci-like subsequence (length `>= 3` where each element equals the sum of the
previous two). Return `0` if none exists.

## Constraints
- `3 <= len(arr) <= 1000`
- `1 <= arr[i] < arr[i+1] <= 10^9`

## Examples
Input: `arr = [1,2,3,4,5,6,7,8]`
Output: `5`
Explanation: `[1,2,3,5,8]` is Fibonacci-like.

Input: `arr = [1,3,7,11,12,14,18]`
Output: `3`
Explanation: e.g. `[1,11,12]` or `[3,11,14]`.
""",
    """def lenLongestFibSubseq(arr):
    idx = {v: i for i, v in enumerate(arr)}
    n = len(arr)
    dp = {}
    best = 0
    for j in range(n):
        for k in range(j + 1, n):
            i = idx.get(arr[k] - arr[j])
            if i is not None and i < j:
                dp[(j, k)] = dp.get((i, j), 2) + 1
                best = max(best, dp[(j, k)])
    return best if best >= 3 else 0
""",
    visible=[{"arr": [1, 2, 3, 4, 5, 6, 7, 8]},
             {"arr": [1, 3, 7, 11, 12, 14, 18]}],
    hidden=[{"arr": [1, 2, 3]}, {"arr": [1, 5, 9]},
            {"arr": [2, 4, 7, 8, 11, 14, 18, 23]}, {"arr": [1, 2, 4, 8, 16]}],
    gen=lambda r: [_qb_fib(r) for _ in range(10)],
    brute=_b_fib,
    checks=[({"arr": [1, 2, 3, 4, 5, 6, 7, 8]}, 5),
            ({"arr": [1, 3, 7, 11, 12, 14, 18]}, 3), ({"arr": [1, 5, 9]}, 0)])

add("russian-doll-envelopes", "Russian Doll Envelopes", "hard",
    ["array", "dynamic-programming", "binary-search", "sorting"], "maxEnvelopes",
    [("envelopes", "int[][]")], "int",
    """
Each `envelopes[i] = [width, height]`. One envelope fits inside another only if
**both** its width and height are strictly smaller. Return the maximum number of
envelopes you can nest (like Russian dolls).

## Constraints
- `1 <= len(envelopes) <= 10^5`
- `1 <= width, height <= 10^5`

## Examples
Input: `envelopes = [[5,4],[6,4],[6,7],[2,3]]`
Output: `3`
Explanation: `[2,3] -> [5,4] -> [6,7]`.

Input: `envelopes = [[1,1],[1,1],[1,1]]`
Output: `1`
Explanation: Identical envelopes cannot nest.
""",
    """def maxEnvelopes(envelopes):
    import bisect
    envelopes = sorted(envelopes, key=lambda e: (e[0], -e[1]))
    tails = []
    for _, h in envelopes:
        i = bisect.bisect_left(tails, h)
        if i == len(tails):
            tails.append(h)
        else:
            tails[i] = h
    return len(tails)
""",
    visible=[{"envelopes": [[5, 4], [6, 4], [6, 7], [2, 3]]},
             {"envelopes": [[1, 1], [1, 1], [1, 1]]}],
    hidden=[{"envelopes": [[1, 1]]}, {"envelopes": [[2, 3], [3, 4], [4, 5]]},
            {"envelopes": [[4, 5], [4, 6], [6, 7], [2, 3], [1, 1]]},
            {"envelopes": [[5, 5], [6, 4], [6, 6], [3, 3]]}],
    gen=lambda r: [_qb_russian(r) for _ in range(12)],
    brute=_b_russian,
    checks=[({"envelopes": [[5, 4], [6, 4], [6, 7], [2, 3]]}, 3),
            ({"envelopes": [[1, 1], [1, 1], [1, 1]]}, 1)])


# ===========================================================================
# qb3_large.txt import — Batch 4b: classic / interval / game DP
# ===========================================================================

def _qb_burst(r):
    return {"nums": [r.randint(0, 9) for _ in range(r.randint(1, 7))]}


def _b_burst(nums):
    from itertools import permutations
    n = len(nums)
    if n == 0:
        return 0
    best = 0
    for perm in permutations(range(n)):
        present = [True] * n
        coins = 0
        for idx in perm:
            left = idx - 1
            while left >= 0 and not present[left]:
                left -= 1
            right = idx + 1
            while right < n and not present[right]:
                right += 1
            lv = nums[left] if left >= 0 else 1
            rv = nums[right] if right < n else 1
            coins += lv * nums[idx] * rv
            present[idx] = False
        best = max(best, coins)
    return best


def _b_game_first(vals):
    from functools import lru_cache

    @lru_cache(None)
    def best_first(i, j):
        if i > j:
            return 0
        remaining = sum(vals[i:j + 1])
        return max(vals[i] + (remaining - vals[i] - best_first(i + 1, j)),
                   vals[j] + (remaining - vals[j] - best_first(i, j - 1)))

    return best_first(0, len(vals) - 1)


def _qb_pilelist(r):
    return [r.randint(1, 12) for _ in range(r.randint(1, 8))]


def _qb_climb(r):
    return {"cost": [r.randint(0, 20) for _ in range(r.randint(2, 12))]}


def _b_climb(cost):
    from functools import lru_cache
    n = len(cost)

    @lru_cache(None)
    def go(i):
        if i >= n:
            return 0
        return cost[i] + min(go(i + 1), go(i + 2))

    return min(go(0), go(1))


def _qb_deleteearn(r):
    return {"nums": [r.randint(1, 10) for _ in range(r.randint(1, 12))]}


def _b_deleteearn(nums):
    from collections import Counter
    cnt = Counter(nums)
    vals = sorted(cnt)
    earn = {v: v * cnt[v] for v in vals}
    n = len(vals)
    best = 0
    for mask in range(1 << n):
        chosen = [vals[i] for i in range(n) if mask & (1 << i)]
        if all(chosen[t + 1] - chosen[t] != 1 for t in range(len(chosen) - 1)):
            best = max(best, sum(earn[v] for v in chosen))
    return best


def _qb_tickets(r):
    n = r.randint(1, 10)
    return {"days": sorted(r.sample(range(1, 31), n)),
            "costs": [r.randint(1, 5), r.randint(5, 15), r.randint(15, 40)]}


def _b_tickets(days, costs):
    from functools import lru_cache
    n = len(days)

    @lru_cache(None)
    def go(i):
        if i >= n:
            return 0
        r1 = costs[0] + go(i + 1)
        j = i
        while j < n and days[j] < days[i] + 7:
            j += 1
        r7 = costs[1] + go(j)
        j2 = i
        while j2 < n and days[j2] < days[i] + 30:
            j2 += 1
        r30 = costs[2] + go(j2)
        return min(r1, r7, r30)

    return go(0)


def _qb_painthouse(r):
    return {"costs": [[r.randint(1, 20) for _ in range(3)]
                      for _ in range(r.randint(1, 8))]}


def _b_painthouse(costs):
    from functools import lru_cache
    n = len(costs)

    @lru_cache(None)
    def go(i, prev):
        if i == n:
            return 0
        return min(costs[i][col] + go(i + 1, col)
                   for col in range(3) if col != prev)

    return go(0, -1)


def _qb_mct(r):
    return {"arr": [r.randint(1, 15) for _ in range(r.randint(2, 8))]}


def _b_mct(arr):
    from functools import lru_cache

    @lru_cache(None)
    def go(i, j):
        if i == j:
            return 0
        best = float("inf")
        for k in range(i, j):
            best = min(best, go(i, k) + go(k + 1, j) +
                       max(arr[i:k + 1]) * max(arr[k + 1:j + 1]))
        return best

    return go(0, len(arr) - 1)


def _qb_partition(r):
    n = r.randint(1, 10)
    return {"arr": [r.randint(1, 20) for _ in range(n)], "k": r.randint(1, n)}


def _b_partition_max(arr, k):
    from functools import lru_cache
    n = len(arr)

    @lru_cache(None)
    def go(i):
        if i == n:
            return 0
        best, m = 0, 0
        for j in range(i, min(i + k, n)):
            m = max(m, arr[j])
            best = max(best, m * (j - i + 1) + go(j + 1))
        return best

    return go(0)


def _qb_maxscore(r):
    n = r.randint(1, 8)
    m = r.randint(1, min(5, n))
    return {"nums": [r.randint(-10, 10) for _ in range(n)],
            "multipliers": [r.randint(-10, 10) for _ in range(m)]}


def _b_maxscore_mult(nums, multipliers):
    from functools import lru_cache
    m = len(multipliers)

    @lru_cache(None)
    def go(i, lo, hi):
        if i == m:
            return 0
        return max(multipliers[i] * nums[lo] + go(i + 1, lo + 1, hi),
                   multipliers[i] * nums[hi] + go(i + 1, lo, hi - 1))

    return go(0, 0, len(nums) - 1)


def _qb_cherry(r):
    rows, cols = r.randint(1, 5), r.randint(1, 5)
    return {"grid": [[r.randint(0, 4) for _ in range(cols)] for _ in range(rows)]}


def _b_cherry(grid):
    rows, cols = len(grid), len(grid[0])
    neg = float("-inf")
    dp = [[grid[rows - 1][c1] + (grid[rows - 1][c2] if c1 != c2 else 0)
           for c2 in range(cols)] for c1 in range(cols)]
    for rr in range(rows - 2, -1, -1):
        ndp = [[neg] * cols for _ in range(cols)]
        for c1 in range(cols):
            for c2 in range(cols):
                base = grid[rr][c1] + (grid[rr][c2] if c1 != c2 else 0)
                best = neg
                for nc1 in (c1 - 1, c1, c1 + 1):
                    for nc2 in (c2 - 1, c2, c2 + 1):
                        if 0 <= nc1 < cols and 0 <= nc2 < cols:
                            best = max(best, dp[nc1][nc2])
                ndp[c1][c2] = base + best
        dp = ndp
    return dp[0][cols - 1]


add("burst-balloons", "Burst Balloons Maximum Coins", "hard",
    ["array", "dynamic-programming", "interval-dp"], "maxCoins",
    [("nums", "int[]")], "int",
    """
You have balloons with values `nums`. Bursting balloon `i` earns
`left * nums[i] * right` coins, where `left` and `right` are the values of the
currently-adjacent balloons (out-of-range neighbors count as `1`). Return the
**maximum coins** obtainable by bursting all balloons in some order.

## Constraints
- `1 <= len(nums) <= 300`
- `0 <= nums[i] <= 100`

## Examples
Input: `nums = [3,1,5,8]`
Output: `167`
Explanation: Burst order `1, 5, 3, 8` yields `3*1*5 + 3*5*8 + 1*3*8 + 1*8*1 = 167`.

Input: `nums = [1,5]`
Output: `10`
Explanation: Burst `1` (`1*1*5=5`) then `5` (`1*5*1=5`).
""",
    """def maxCoins(nums):
    a = [1] + nums + [1]
    n = len(a)
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n):
        for left in range(0, n - length):
            right = left + length
            for k in range(left + 1, right):
                dp[left][right] = max(
                    dp[left][right],
                    a[left] * a[k] * a[right] + dp[left][k] + dp[k][right])
    return dp[0][n - 1]
""",
    visible=[{"nums": [3, 1, 5, 8]}, {"nums": [1, 5]}],
    hidden=[{"nums": [5]}, {"nums": [0]}, {"nums": [9, 76, 64, 21]},
            {"nums": [1, 2, 3, 4, 5]}],
    gen=lambda r: [_qb_burst(r) for _ in range(10)],
    brute=_b_burst,
    checks=[({"nums": [3, 1, 5, 8]}, 167), ({"nums": [1, 5]}, 10)])

add("stone-game", "Stone Game Winner", "medium",
    ["array", "dynamic-programming", "game-theory"], "stoneGame",
    [("piles", "int[]")], "bool",
    """
`piles[i]` stones sit in a row. Two players alternate, each taking a whole pile from
**either end**; both play optimally to maximize their own stone count. Return `true`
if the **first** player ends with strictly more stones than the second.

## Constraints
- `1 <= len(piles) <= 500`
- `1 <= piles[i] <= 10^4`

## Examples
Input: `piles = [5,3,4,5]`
Output: `true`
Explanation: The first player can guarantee more than half the stones.

Input: `piles = [3,7,2,3]`
Output: `true`
Explanation: Optimal play wins for the first player.
""",
    """def stoneGame(piles):
    n = len(piles)
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = piles[i]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = max(piles[i] - dp[i + 1][j], piles[j] - dp[i][j - 1])
    return dp[0][n - 1] > 0
""",
    visible=[{"piles": [5, 3, 4, 5]}, {"piles": [3, 7, 2, 3]}],
    hidden=[{"piles": [1]}, {"piles": [1, 1]}, {"piles": [2, 1]},
            {"piles": [7, 8, 8, 10]}],
    gen=lambda r: [{"piles": _qb_pilelist(r)} for _ in range(12)],
    brute=lambda piles: 2 * _b_game_first(piles) > sum(piles),
    checks=[({"piles": [5, 3, 4, 5]}, True), ({"piles": [3, 7, 2, 3]}, True),
            ({"piles": [1, 1]}, False)])

add("predict-the-winner", "Predict the Winner", "medium",
    ["array", "dynamic-programming", "game-theory"], "predictTheWinner",
    [("nums", "int[]")], "bool",
    """
Two players alternate taking a number from **either end** of `nums`, adding it to
their score; both play optimally. Return `true` if **player 1** can end with a score
greater than or equal to player 2.

## Constraints
- `1 <= len(nums) <= 20`
- `0 <= nums[i] <= 10^7`

## Examples
Input: `nums = [1,5,2]`
Output: `false`
Explanation: Player 1 cannot avoid finishing behind.

Input: `nums = [1,5,233,7]`
Output: `true`
Explanation: Player 1 can force at least a tie.
""",
    """def predictTheWinner(nums):
    n = len(nums)
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = nums[i]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = max(nums[i] - dp[i + 1][j], nums[j] - dp[i][j - 1])
    return dp[0][n - 1] >= 0
""",
    visible=[{"nums": [1, 5, 2]}, {"nums": [1, 5, 233, 7]}],
    hidden=[{"nums": [0]}, {"nums": [1, 1]}, {"nums": [1, 2]},
            {"nums": [2, 4, 55, 6, 8]}],
    gen=lambda r: [{"nums": _qb_pilelist(r)} for _ in range(12)],
    brute=lambda nums: 2 * _b_game_first(nums) >= sum(nums),
    checks=[({"nums": [1, 5, 2]}, False), ({"nums": [1, 5, 233, 7]}, True)])

add("min-cost-climbing-stairs", "Minimum Cost Climbing Stairs", "easy",
    ["array", "dynamic-programming"], "minCostClimbingStairs",
    [("cost", "int[]")], "int",
    """
`cost[i]` is the price to step on stair `i`. You may start at index `0` or `1`, and
from a stair you climb one or two steps. Return the **minimum total cost** to reach
the top (just past the last stair).

## Constraints
- `2 <= len(cost) <= 1000`
- `0 <= cost[i] <= 999`

## Examples
Input: `cost = [10,15,20]`
Output: `15`
Explanation: Start on stair 1 (cost 15) and step to the top.

Input: `cost = [1,100,1,1,1,100,1,1,100,1]`
Output: `6`
Explanation: Step on the six stairs that cost `1`.
""",
    """def minCostClimbingStairs(cost):
    a, b = 0, 0
    for i in range(2, len(cost) + 1):
        a, b = b, min(b + cost[i - 1], a + cost[i - 2])
    return b
""",
    visible=[{"cost": [10, 15, 20]},
             {"cost": [1, 100, 1, 1, 1, 100, 1, 1, 100, 1]}],
    hidden=[{"cost": [0, 0]}, {"cost": [5, 5]}, {"cost": [1, 2, 3]},
            {"cost": [10, 1, 1, 10]}],
    gen=lambda r: [_qb_climb(r) for _ in range(12)],
    brute=_b_climb,
    checks=[({"cost": [10, 15, 20]}, 15),
            ({"cost": [1, 100, 1, 1, 1, 100, 1, 1, 100, 1]}, 6)])

add("delete-and-earn", "Delete and Earn", "medium",
    ["array", "dynamic-programming", "hash-table"], "deleteAndEarn",
    [("nums", "int[]")], "int",
    """
Pick any value `x` from `nums` to earn `x` points, but doing so deletes **every**
occurrence of `x - 1` and `x + 1`. Repeat until `nums` is empty. Return the
**maximum points** you can earn.

## Constraints
- `1 <= len(nums) <= 2*10^4`
- `1 <= nums[i] <= 10^4`

## Examples
Input: `nums = [3,4,2]`
Output: `6`
Explanation: Take `4` (deletes `3`), then `2`, for `4 + 2 = 6`.

Input: `nums = [2,2,3,3,3,4]`
Output: `9`
Explanation: Take all three `3`s (deletes the `2`s and `4`) for `9`.
""",
    """def deleteAndEarn(nums):
    from collections import Counter
    cnt = Counter(nums)
    hi = max(nums)
    earn = [0] * (hi + 1)
    for v, c in cnt.items():
        earn[v] = v * c
    prev2, prev1 = 0, 0
    for v in range(hi + 1):
        prev2, prev1 = prev1, max(prev1, prev2 + earn[v])
    return prev1
""",
    visible=[{"nums": [3, 4, 2]}, {"nums": [2, 2, 3, 3, 3, 4]}],
    hidden=[{"nums": [1]}, {"nums": [1, 1, 1]}, {"nums": [8, 10, 4, 9, 1, 3, 5, 9, 4, 10]},
            {"nums": [10, 10, 10]}],
    gen=lambda r: [_qb_deleteearn(r) for _ in range(12)],
    brute=_b_deleteearn,
    checks=[({"nums": [3, 4, 2]}, 6), ({"nums": [2, 2, 3, 3, 3, 4]}, 9)])

add("min-ticket-cost", "Minimum Ticket Cost", "medium",
    ["array", "dynamic-programming"], "mincostTickets",
    [("days", "int[]"), ("costs", "int[]")], "int",
    """
You travel on the given `days` (a sorted list within a year, `1..365`). Passes cost
`costs = [oneDay, sevenDay, thirtyDay]` and cover 1, 7, or 30 **consecutive** days
from their purchase. Return the **minimum cost** to cover all travel days.

## Constraints
- `1 <= len(days) <= 365`, days are strictly increasing in `1..365`
- `len(costs) == 3`, `1 <= costs[i] <= 1000`

## Examples
Input: `days = [1,4,6,7,8,20], costs = [2,7,15]`
Output: `11`
Explanation: A 7-day pass on day 1 and another on day 7, plus a 1-day pass for day 20.

Input: `days = [1,2,3,4,5,6,7,8,9,10,30,31], costs = [2,7,15]`
Output: `17`
Explanation: A 30-day pass covers days 1–10, plus a 7-day pass for days 30–31.
""",
    """def mincostTickets(days, costs):
    dayset = set(days)
    last = days[-1]
    dp = [0] * (last + 1)
    for d in range(1, last + 1):
        if d not in dayset:
            dp[d] = dp[d - 1]
        else:
            dp[d] = min(dp[d - 1] + costs[0],
                        dp[max(0, d - 7)] + costs[1],
                        dp[max(0, d - 30)] + costs[2])
    return dp[last]
""",
    visible=[{"days": [1, 4, 6, 7, 8, 20], "costs": [2, 7, 15]},
             {"days": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 30, 31], "costs": [2, 7, 15]}],
    hidden=[{"days": [1], "costs": [2, 7, 15]},
            {"days": [1, 30], "costs": [2, 7, 15]},
            {"days": [1, 2, 3], "costs": [5, 7, 15]},
            {"days": [1, 8, 15, 22, 29], "costs": [3, 12, 40]}],
    gen=lambda r: [_qb_tickets(r) for _ in range(12)],
    brute=_b_tickets,
    checks=[({"days": [1, 4, 6, 7, 8, 20], "costs": [2, 7, 15]}, 11),
            ({"days": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 30, 31],
              "costs": [2, 7, 15]}, 17)])

add("paint-house", "Paint House Minimum Cost", "medium",
    ["array", "dynamic-programming"], "minCost", [("costs", "int[][]")], "int",
    """
There are `n` houses in a row, each painted one of three colors. `costs[i] =
[red, green, blue]` is the cost of each color for house `i`. No two **adjacent**
houses may share a color. Return the **minimum total painting cost**.

## Constraints
- `1 <= len(costs) <= 100`
- `costs[i]` has exactly 3 non-negative values

## Examples
Input: `costs = [[17,2,17],[16,16,5],[14,3,19]]`
Output: `10`
Explanation: Green, blue, green → `2 + 5 + 3 = 10`.

Input: `costs = [[7,6,2]]`
Output: `2`
Explanation: Paint the single house its cheapest color.
""",
    """def minCost(costs):
    if not costs:
        return 0
    a, b, c = costs[0]
    for i in range(1, len(costs)):
        x, y, z = costs[i]
        a, b, c = x + min(b, c), y + min(a, c), z + min(a, b)
    return min(a, b, c)
""",
    visible=[{"costs": [[17, 2, 17], [16, 16, 5], [14, 3, 19]]},
             {"costs": [[7, 6, 2]]}],
    hidden=[{"costs": [[1, 2, 3]]}, {"costs": [[1, 1, 1], [1, 1, 1]]},
            {"costs": [[5, 8, 6], [19, 14, 13], [7, 5, 12], [14, 15, 17]]}],
    gen=lambda r: [_qb_painthouse(r) for _ in range(12)],
    brute=_b_painthouse,
    checks=[({"costs": [[17, 2, 17], [16, 16, 5], [14, 3, 19]]}, 10),
            ({"costs": [[7, 6, 2]]}, 2)])

add("min-cost-tree-leaf-values", "Minimum Cost Tree From Leaf Values", "medium",
    ["array", "dynamic-programming", "stack", "monotonic-stack", "interval-dp"], "mctFromLeafValues",
    [("arr", "int[]")], "int",
    """
Build a binary tree whose leaves are the values of `arr` **in order** (left to
right). Each internal node's value is the product of the largest leaf in its left
subtree and the largest leaf in its right subtree. Return the **minimum possible sum
of all internal node values**.

## Constraints
- `2 <= len(arr) <= 40`
- `1 <= arr[i] <= 15`

## Examples
Input: `arr = [6,2,4]`
Output: `32`
Explanation: Combine `2` and `4` (`8`), then with `6` (`24`); `8 + 24 = 32`.

Input: `arr = [4,11]`
Output: `44`
Explanation: The single internal node is `4 * 11 = 44`.
""",
    """def mctFromLeafValues(arr):
    n = len(arr)
    maxv = [[0] * n for _ in range(n)]
    for i in range(n):
        m = arr[i]
        for j in range(i, n):
            m = max(m, arr[j])
            maxv[i][j] = m
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = min(dp[i][k] + dp[k + 1][j] + maxv[i][k] * maxv[k + 1][j]
                           for k in range(i, j))
    return dp[0][n - 1]
""",
    visible=[{"arr": [6, 2, 4]}, {"arr": [4, 11]}],
    hidden=[{"arr": [1, 2]}, {"arr": [7, 7, 7]}, {"arr": [15, 13, 5, 3, 15]},
            {"arr": [2, 3, 4, 5]}],
    gen=lambda r: [_qb_mct(r) for _ in range(12)],
    brute=_b_mct,
    checks=[({"arr": [6, 2, 4]}, 32), ({"arr": [4, 11]}, 44)])

add("partition-array-max-sum", "Partition Array For Maximum Sum", "medium",
    ["array", "dynamic-programming"], "maxSumAfterPartitioning",
    [("arr", "int[]"), ("k", "int")], "int",
    """
Partition `arr` into contiguous blocks of length **at most** `k`. After
partitioning, every value in a block becomes the block's maximum. Return the
**largest possible sum** of the resulting array.

## Constraints
- `1 <= len(arr) <= 500`
- `1 <= k <= len(arr)`
- `0 <= arr[i] <= 10^9`

## Examples
Input: `arr = [1,15,7,9,2,5,10], k = 3`
Output: `84`
Explanation: Blocks `[1,15,7] [9] [2,5,10]` → `15*3 + 9 + 10*3 = 84`.

Input: `arr = [1,4,1,5,7,3,6,1,9,9,3], k = 4`
Output: `83`
Explanation: An optimal partition gives `83`.
""",
    """def maxSumAfterPartitioning(arr, k):
    n = len(arr)
    dp = [0] * (n + 1)
    for i in range(1, n + 1):
        cur_max = 0
        for j in range(1, min(k, i) + 1):
            cur_max = max(cur_max, arr[i - j])
            dp[i] = max(dp[i], dp[i - j] + cur_max * j)
    return dp[n]
""",
    visible=[{"arr": [1, 15, 7, 9, 2, 5, 10], "k": 3},
             {"arr": [1, 4, 1, 5, 7, 3, 6, 1, 9, 9, 3], "k": 4}],
    hidden=[{"arr": [1], "k": 1}, {"arr": [5, 5, 5], "k": 1},
            {"arr": [1, 2, 3, 4], "k": 4}, {"arr": [7, 1, 7, 1, 7, 1], "k": 2}],
    gen=lambda r: [_qb_partition(r) for _ in range(12)],
    brute=_b_partition_max,
    checks=[({"arr": [1, 15, 7, 9, 2, 5, 10], "k": 3}, 84),
            ({"arr": [1, 4, 1, 5, 7, 3, 6, 1, 9, 9, 3], "k": 4}, 83)])

add("max-score-multiplication", "Maximum Score From Multiplication Operations",
    "hard", ["array", "dynamic-programming"], "maximumScore",
    [("nums", "int[]"), ("multipliers", "int[]")], "int",
    """
For each `multipliers[i]` in order, take a number from **either end** of `nums`,
multiply it by `multipliers[i]`, and add it to your score. After all `m`
multipliers, return the **maximum total score**.

## Constraints
- `1 <= len(multipliers) <= 300 <= len(nums) <= 10^5`
- `-1000 <= nums[i], multipliers[i] <= 1000`

## Examples
Input: `nums = [1,2,3], multipliers = [3,2,1]`
Output: `14`
Explanation: `3*3 + 2*2 + 1*1 = 14`.

Input: `nums = [-5,-3,-3,-2,7,1], multipliers = [-10,-5,3,4,6]`
Output: `102`
Explanation: Optimal end choices yield `102`.
""",
    """def maximumScore(nums, multipliers):
    n, m = len(nums), len(multipliers)
    dp = [0] * (m + 1)
    for i in range(m - 1, -1, -1):
        ndp = [0] * (m + 1)
        for left in range(i, -1, -1):
            right = n - 1 - (i - left)
            ndp[left] = max(multipliers[i] * nums[left] + dp[left + 1],
                            multipliers[i] * nums[right] + dp[left])
        dp = ndp
    return dp[0]
""",
    visible=[{"nums": [1, 2, 3], "multipliers": [3, 2, 1]},
             {"nums": [-5, -3, -3, -2, 7, 1], "multipliers": [-10, -5, 3, 4, 6]}],
    hidden=[{"nums": [1], "multipliers": [5]},
            {"nums": [1, 1, 1], "multipliers": [1, 1]},
            {"nums": [-1, -2, -3, -4], "multipliers": [2, 2]},
            {"nums": [5, 0, 5], "multipliers": [-3, 1, 3]}],
    gen=lambda r: [_qb_maxscore(r) for _ in range(12)],
    brute=_b_maxscore_mult,
    checks=[({"nums": [1, 2, 3], "multipliers": [3, 2, 1]}, 14),
            ({"nums": [-5, -3, -3, -2, 7, 1],
              "multipliers": [-10, -5, 3, 4, 6]}, 102)])

add("cherry-pickup-two-robots", "Cherry Pickup Two Robots", "hard",
    ["matrix", "dynamic-programming"], "cherryPickup",
    [("grid", "int[][]")], "int",
    """
Two robots start at the top-left `(0,0)` and top-right `(0,cols-1)` of `grid` and
move down to the bottom row; each step goes down-left, down, or down-right. A cell's
cherries are collected when a robot enters it (counted once if both robots share a
cell). Return the **maximum cherries** the two robots collect together.

## Constraints
- `1 <= rows, cols <= 70`
- `0 <= grid[i][j] <= 100`

## Examples
Input: `grid = [[3,1,1],[2,5,1],[1,5,5],[2,1,1]]`
Output: `24`
Explanation: The robots take complementary paths collecting `24` cherries.

Input: `grid = [[1,0,0,0,0,0,1],[2,0,0,0,0,3,0]]`
Output: `7`
Explanation: Robot 1 takes `(0,0)=1, (1,0)=2`; robot 2 takes `(0,6)=1, (1,5)=3`;
together `1 + 1 + 2 + 3 = 7`.
""",
    """def cherryPickup(grid):
    rows, cols = len(grid), len(grid[0])
    neg = float('-inf')
    dp = [[grid[rows - 1][c1] + (grid[rows - 1][c2] if c1 != c2 else 0)
           for c2 in range(cols)] for c1 in range(cols)]
    for r in range(rows - 2, -1, -1):
        ndp = [[neg] * cols for _ in range(cols)]
        for c1 in range(cols):
            for c2 in range(cols):
                base = grid[r][c1] + (grid[r][c2] if c1 != c2 else 0)
                best = neg
                for nc1 in (c1 - 1, c1, c1 + 1):
                    for nc2 in (c2 - 1, c2, c2 + 1):
                        if 0 <= nc1 < cols and 0 <= nc2 < cols:
                            best = max(best, dp[nc1][nc2])
                ndp[c1][c2] = base + best
        dp = ndp
    return dp[0][cols - 1]
""",
    visible=[{"grid": [[3, 1, 1], [2, 5, 1], [1, 5, 5], [2, 1, 1]]},
             {"grid": [[1, 0, 0, 0, 0, 0, 1], [2, 0, 0, 0, 0, 3, 0]]}],
    hidden=[{"grid": [[5]]}, {"grid": [[1, 1]]}, {"grid": [[7], [7], [7]]},
            {"grid": [[1, 2, 3], [4, 5, 6]]}],
    gen=lambda r: [_qb_cherry(r) for _ in range(12)],
    brute=_b_cherry,
    checks=[({"grid": [[3, 1, 1], [2, 5, 1], [1, 5, 5], [2, 1, 1]]}, 24),
            ({"grid": [[1, 0, 0, 0, 0, 0, 1], [2, 0, 0, 0, 0, 3, 0]]}, 7)])


# ===========================================================================
# qb3_large.txt import — Batch 5: trees
# ===========================================================================

_TREE_PRE = '''class _N:
    __slots__ = ("v", "l", "r")

    def __init__(self, v):
        self.v, self.l, self.r = v, None, None


def _build(arr):
    if not arr or arr[0] is None:
        return None
    root = _N(arr[0])
    q, i = [root], 1
    while q and i < len(arr):
        cur = q.pop(0)
        if i < len(arr):
            x = arr[i]; i += 1
            if x is not None:
                cur.l = _N(x); q.append(cur.l)
        if i < len(arr):
            x = arr[i]; i += 1
            if x is not None:
                cur.r = _N(x); q.append(cur.r)
    return root


def _ser(root):
    out, q = [], [root]
    while q:
        node = q.pop(0)
        if node is None:
            out.append(None)
            continue
        out.append(node.v)
        q.append(node.l)
        q.append(node.r)
    while out and out[-1] is None:
        out.pop()
    return out


'''


def _b_rightside(root):
    t = _build_tree(root)
    res = []

    def dfs(node, depth):
        if not node:
            return
        if depth == len(res):
            res.append(node.val)
        dfs(node.right, depth + 1)
        dfs(node.left, depth + 1)

    dfs(t, 0)
    return res


def _b_goodnodes(root):
    t = _build_tree(root)
    count = 0
    stack = [(t, float("-inf"))]
    while stack:
        node, mx = stack.pop()
        if not node:
            continue
        if node.val >= mx:
            count += 1
        nm = max(mx, node.val)
        stack.append((node.left, nm))
        stack.append((node.right, nm))
    return count


def _qb_recover_case(r):
    root = _rand_tree_root(r, r.randint(2, 8))
    nodes = []

    def inorder(nd):
        if not nd:
            return
        inorder(nd.left)
        nodes.append(nd)
        inorder(nd.right)

    inorder(root)
    vals = sorted(r.sample(range(1, 80), len(nodes)))
    for nd, v in zip(nodes, vals):
        nd.val = v
    i, j = r.sample(range(len(nodes)), 2)
    nodes[i].val, nodes[j].val = nodes[j].val, nodes[i].val
    return {"root": _serialize_tree(root)}


def _b_recover(root):
    t = _build_tree(root)
    nodes = []

    def inorder(n):
        if not n:
            return
        inorder(n.left)
        nodes.append(n)
        inorder(n.right)

    inorder(t)
    for node, v in zip(nodes, sorted(node.val for node in nodes)):
        node.val = v
    return _serialize_tree(t)


def _b_flatten(root):
    t = _build_tree(root)
    vals = []

    def pre(n):
        if not n:
            return
        vals.append(n.val)
        pre(n.left)
        pre(n.right)

    pre(t)
    if not vals:
        return []
    nodes = [_TN(v) for v in vals]
    for i in range(len(nodes) - 1):
        nodes[i].right = nodes[i + 1]
    return _serialize_tree(nodes[0])


def _qb_complete(r):
    return {"root": [r.randint(0, 100) for _ in range(r.randint(1, 31))]}


def _b_countnodes(root):
    t = _build_tree(root)

    def c(n):
        return 0 if n is None else 1 + c(n.left) + c(n.right)

    return c(t)


def _qb_pathsum(r):
    arr = _rand_tree_arr(r, 1, 10, -8, 8)
    t = _build_tree(arr)
    sums = []

    def dfs(n, s):
        if not n:
            return
        s += n.val
        if not n.left and not n.right:
            sums.append(s)
        dfs(n.left, s)
        dfs(n.right, s)

    dfs(t, 0)
    target = r.choice(sums) if (sums and r.random() < 0.5) else r.randint(-20, 20)
    return {"root": arr, "targetSum": target}


def _b_haspathsum(root, targetSum):
    t = _build_tree(root)
    if not t:
        return False
    found = [False]

    def dfs(n, s):
        s += n.val
        if not n.left and not n.right:
            if s == targetSum:
                found[0] = True
            return
        if n.left:
            dfs(n.left, s)
        if n.right:
            dfs(n.right, s)

    dfs(t, 0)
    return found[0]


def _b_pathsumlist(root, targetSum):
    t = _build_tree(root)
    res = []

    def dfs(n, path):
        if not n:
            return
        path = path + [n.val]
        if not n.left and not n.right and sum(path) == targetSum:
            res.append(path)
        dfs(n.left, path)
        dfs(n.right, path)

    dfs(t, [])
    return res


def _b_width(root):
    from collections import defaultdict
    t = _build_tree(root)
    if not t:
        return 0
    levels = defaultdict(list)

    def dfs(n, depth, pos):
        if not n:
            return
        levels[depth].append(pos)
        dfs(n.left, depth + 1, 2 * pos)
        dfs(n.right, depth + 1, 2 * pos + 1)

    dfs(t, 0, 0)
    return max(max(p) - min(p) + 1 for p in levels.values())


def _qb_symmetric(r):
    if r.random() < 0.5:
        def build_half(depth):
            if depth == 0 or r.random() < 0.3:
                return None
            node = _TN(r.randint(0, 5))
            node.left = build_half(depth - 1)
            node.right = build_half(depth - 1)
            return node

        def mirror(n):
            if n is None:
                return None
            m = _TN(n.val)
            m.left = mirror(n.right)
            m.right = mirror(n.left)
            return m

        root = _TN(r.randint(0, 5))
        left = build_half(3)
        root.left = left
        root.right = mirror(left)
        return {"root": _serialize_tree(root)}
    return {"root": _rand_tree_arr(r, 1, 10, 0, 3)}


def _b_symmetric(root):
    t = _build_tree(root)
    if t is None:
        return True

    def ser(n):
        return [None] if n is None else [n.val] + ser(n.left) + ser(n.right)

    def mir(n):
        return [None] if n is None else [n.val] + mir(n.right) + mir(n.left)

    return ser(t) == mir(t)


def _qb_sortedarr(r):
    return {"nums": sorted(r.sample(range(-30, 30), r.randint(1, 12)))}


def _b_sortedbst(nums):
    def build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = _TN(nums[mid])
        node.left = build(lo, mid - 1)
        node.right = build(mid + 1, hi)
        return node

    return _serialize_tree(build(0, len(nums) - 1))


add("binary-tree-right-side-view", "Binary Tree Right Side View", "medium",
    ["tree", "binary-tree", "breadth-first-search"], "rightSideView",
    [("root", "int[]")], "int[]",
    """
Given a binary tree as a level-order array (`null` marks a missing child), imagine
standing on the right side. Return the values of the nodes visible from top to
bottom — the **rightmost node at each depth**.

## Constraints
- The number of nodes is in `[0, 100]`.
- `-100 <= node value <= 100`

## Examples
Input: `root = [1,2,3,null,5,null,4]`
Output: `[1,3,4]`
Explanation: From the right you see `1`, then `3`, then `4`.

Input: `root = [1,null,3]`
Output: `[1,3]`
Explanation: Only the right spine is visible.
""",
    _TREE_PRE + """def rightSideView(root):
    from collections import deque
    r = _build(root)
    if not r:
        return []
    res = []
    q = deque([r])
    while q:
        n = len(q)
        for i in range(n):
            node = q.popleft()
            if i == n - 1:
                res.append(node.v)
            if node.l:
                q.append(node.l)
            if node.r:
                q.append(node.r)
    return res
""",
    visible=[{"root": [1, 2, 3, None, 5, None, 4]}, {"root": [1, None, 3]}],
    hidden=[{"root": []}, {"root": [1]}, {"root": [1, 2, 3, 4]},
            {"root": [1, 2, 3, 4, None, None, None, 5]}],
    gen=lambda r: [{"root": _rand_tree_arr(r, 0, 14, -50, 50)} for _ in range(12)],
    brute=_b_rightside,
    checks=[({"root": [1, 2, 3, None, 5, None, 4]}, [1, 3, 4]),
            ({"root": [1, None, 3]}, [1, 3]), ({"root": []}, [])])

add("count-good-nodes", "Count Good Nodes in Binary Tree", "medium",
    ["tree", "binary-tree", "depth-first-search"], "goodNodes",
    [("root", "int[]")], "int",
    """
A node `X` is **good** if no node on the path from the root down to `X` has a value
greater than `X` (the root is always good). Return the number of good nodes in the
binary tree (given as a level-order array, `null` = missing child).

## Constraints
- The number of nodes is in `[1, 10^5]`.
- `-10^4 <= node value <= 10^4`

## Examples
Input: `root = [3,1,4,3,null,1,5]`
Output: `4`
Explanation: The good nodes are `3` (root), `4`, `5`, and the deeper `3`.

Input: `root = [3,3,null,4,2]`
Output: `3`
Explanation: `3` (root), the child `3`, and `4` are good.
""",
    _TREE_PRE + """def goodNodes(root):
    r = _build(root)

    def dfs(node, mx):
        if not node:
            return 0
        good = 1 if node.v >= mx else 0
        nm = max(mx, node.v)
        return good + dfs(node.l, nm) + dfs(node.r, nm)

    return dfs(r, float('-inf'))
""",
    visible=[{"root": [3, 1, 4, 3, None, 1, 5]}, {"root": [3, 3, None, 4, 2]}],
    hidden=[{"root": [1]}, {"root": [2, None, 2]}, {"root": [9, 8, 7, 6, 5]},
            {"root": [1, 1, 1, 1, 1]}],
    gen=lambda r: [{"root": _rand_tree_arr(r, 1, 14, -5, 5)} for _ in range(12)],
    brute=_b_goodnodes,
    checks=[({"root": [3, 1, 4, 3, None, 1, 5]}, 4),
            ({"root": [3, 3, None, 4, 2]}, 3)])

add("recover-bst", "Recover Swapped BST", "medium",
    ["tree", "binary-search-tree", "depth-first-search"], "recoverTree",
    [("root", "int[]")], "int[]",
    """
Exactly two nodes of a binary search tree (given as a level-order array) had their
values swapped by mistake. Recover the tree without changing its structure and
return its corrected level-order array.

## Constraints
- The number of nodes is in `[2, 1000]`.
- All node values are distinct; exactly two were swapped.

## Examples
Input: `root = [1,3,null,null,2]`
Output: `[3,1,null,null,2]`
Explanation: Swapping `1` and `3` restores the BST ordering.

Input: `root = [3,1,4,null,null,2]`
Output: `[2,1,4,null,null,3]`
Explanation: Nodes `3` and `2` were swapped; swapping them back restores the BST.
""",
    _TREE_PRE + """def recoverTree(root):
    r = _build(root)
    nodes = []

    def inorder(n):
        if not n:
            return
        inorder(n.l)
        nodes.append(n)
        inorder(n.r)

    inorder(r)
    first = second = prev = None
    for n in nodes:
        if prev and prev.v > n.v:
            if not first:
                first = prev
            second = n
        prev = n
    if first and second:
        first.v, second.v = second.v, first.v
    return _ser(r)
""",
    visible=[{"root": [1, 3, None, None, 2]}, {"root": [3, 1, 4, None, None, 2]}],
    hidden=[{"root": [2, 1]}, {"root": [1, 2]},
            {"root": [5, 3, 8, 2, 4, 7, 10]}],
    gen=lambda r: [_qb_recover_case(r) for _ in range(12)],
    brute=_b_recover,
    checks=[({"root": [1, 3, None, None, 2]}, [3, 1, None, None, 2]),
            ({"root": [3, 1, 4, None, None, 2]}, [2, 1, 4, None, None, 3])])

add("flatten-binary-tree", "Flatten Binary Tree To Linked List", "medium",
    ["tree", "binary-tree", "depth-first-search"], "flatten",
    [("root", "int[]")], "int[]",
    """
Flatten the binary tree (given as a level-order array) into a "linked list" in
**preorder**: every node's left child becomes `null` and its right child is the next
node in preorder. Return the resulting tree as a level-order array (a right-leaning
chain like `[1,null,2,null,3,...]`).

## Constraints
- The number of nodes is in `[0, 2000]`.
- `-100 <= node value <= 100`

## Examples
Input: `root = [1,2,5,3,4,null,6]`
Output: `[1,null,2,null,3,null,4,null,5,null,6]`
Explanation: Preorder is `1,2,3,4,5,6`, laid out as a right-only chain.

Input: `root = []`
Output: `[]`
Explanation: An empty tree stays empty.
""",
    _TREE_PRE + """def flatten(root):
    r = _build(root)
    order = []

    def pre(n):
        if not n:
            return
        order.append(n)
        pre(n.l)
        pre(n.r)

    pre(r)
    for i in range(len(order)):
        order[i].l = None
        order[i].r = order[i + 1] if i + 1 < len(order) else None
    return _ser(r)
""",
    visible=[{"root": [1, 2, 5, 3, 4, None, 6]}, {"root": []}],
    hidden=[{"root": [1]}, {"root": [1, 2]}, {"root": [0]},
            {"root": [4, 2, 6, 1, 3, 5, 7]}],
    gen=lambda r: [{"root": _rand_tree_arr(r, 0, 14, -50, 50)} for _ in range(12)],
    brute=_b_flatten,
    checks=[({"root": [1, 2, 5, 3, 4, None, 6]},
             [1, None, 2, None, 3, None, 4, None, 5, None, 6]),
            ({"root": []}, [])])

add("count-complete-tree-nodes", "Count Complete Tree Nodes", "easy",
    ["tree", "binary-tree", "binary-search"], "countNodes",
    [("root", "int[]")], "int",
    """
Given a **complete** binary tree as a level-order array (every level full except
possibly the last, which is filled left to right), return the number of nodes.

## Constraints
- The number of nodes is in `[0, 5*10^4]`.
- The tree is complete.

## Examples
Input: `root = [1,2,3,4,5,6]`
Output: `6`
Explanation: All six positions hold a node.

Input: `root = [1]`
Output: `1`
Explanation: A single root node.
""",
    _TREE_PRE + """def countNodes(root):
    r = _build(root)

    def cnt(n):
        return 0 if n is None else 1 + cnt(n.l) + cnt(n.r)

    return cnt(r)
""",
    visible=[{"root": [1, 2, 3, 4, 5, 6]}, {"root": [1]}],
    hidden=[{"root": []}, {"root": [1, 2]},
            {"root": [1, 2, 3, 4, 5, 6, 7]},
            {"root": list(range(1, 24))}],
    gen=lambda r: [_qb_complete(r) for _ in range(12)],
    brute=_b_countnodes,
    checks=[({"root": [1, 2, 3, 4, 5, 6]}, 6), ({"root": [1]}, 1),
            ({"root": []}, 0)])

add("path-sum-exists", "Path Sum Exists", "easy",
    ["tree", "binary-tree", "depth-first-search"], "hasPathSum",
    [("root", "int[]"), ("targetSum", "int")], "bool",
    """
Return `true` if the binary tree (level-order array) has a **root-to-leaf** path
whose node values sum to exactly `targetSum`.

## Constraints
- The number of nodes is in `[0, 5000]`.
- `-1000 <= node value, targetSum <= 1000`

## Examples
Input: `root = [5,4,8,11,null,13,4,7,2,null,null,null,1], targetSum = 22`
Output: `true`
Explanation: The path `5 -> 4 -> 11 -> 2` sums to `22`.

Input: `root = [1,2,3], targetSum = 5`
Output: `false`
Explanation: Root-to-leaf sums are `3` and `4`, never `5`.
""",
    _TREE_PRE + """def hasPathSum(root, targetSum):
    r = _build(root)

    def dfs(n, rem):
        if not n:
            return False
        rem -= n.v
        if not n.l and not n.r:
            return rem == 0
        return dfs(n.l, rem) or dfs(n.r, rem)

    return dfs(r, targetSum) if r else False
""",
    visible=[{"root": [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1],
              "targetSum": 22}, {"root": [1, 2, 3], "targetSum": 5}],
    hidden=[{"root": [], "targetSum": 0}, {"root": [1], "targetSum": 1},
            {"root": [1], "targetSum": 0}, {"root": [-2, None, -3], "targetSum": -5}],
    gen=lambda r: [_qb_pathsum(r) for _ in range(12)],
    brute=_b_haspathsum,
    checks=[({"root": [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1],
              "targetSum": 22}, True),
            ({"root": [1, 2, 3], "targetSum": 5}, False)])

add("root-to-leaf-paths-target", "All Root To Leaf Paths With Target Sum",
    "medium", ["tree", "binary-tree", "backtracking"], "pathSum",
    [("root", "int[]"), ("targetSum", "int")], "int[][]",
    """
Return **all root-to-leaf paths** in the binary tree (level-order array) whose node
values sum to `targetSum`. Each path is the list of values from root to leaf; the
paths may be returned in any order.

## Constraints
- The number of nodes is in `[0, 5000]`.
- `-1000 <= node value, targetSum <= 1000`

## Examples
Input: `root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22`
Output: `[[5,4,11,2],[5,8,4,5]]`
Explanation: Two root-to-leaf paths sum to `22`.

Input: `root = [1,2,3], targetSum = 4`
Output: `[[1,3]]`
Explanation: Only `1 -> 3` sums to `4`.
""",
    _TREE_PRE + """def pathSum(root, targetSum):
    r = _build(root)
    res = []
    path = []

    def dfs(n, rem):
        if not n:
            return
        path.append(n.v)
        rem -= n.v
        if not n.l and not n.r and rem == 0:
            res.append(list(path))
        dfs(n.l, rem)
        dfs(n.r, rem)
        path.pop()

    dfs(r, targetSum)
    return res
""",
    visible=[{"root": [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1],
              "targetSum": 22}, {"root": [1, 2, 3], "targetSum": 4}],
    hidden=[{"root": [], "targetSum": 0}, {"root": [1, 2], "targetSum": 0},
            {"root": [1], "targetSum": 1},
            {"root": [0, 1, 1], "targetSum": 1}],
    gen=lambda r: [_qb_pathsum(r) for _ in range(12)],
    brute=_b_pathsumlist,
    checks=[({"root": [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1],
              "targetSum": 22}, [[5, 4, 11, 2], [5, 8, 4, 5]]),
            ({"root": [1, 2, 3], "targetSum": 4}, [[1, 3]])])

add("maximum-width-binary-tree", "Maximum Width of Binary Tree", "medium",
    ["tree", "binary-tree", "breadth-first-search"], "widthOfBinaryTree",
    [("root", "int[]")], "int",
    """
The **width** of a level is the distance between its leftmost and rightmost non-null
nodes, counting the null slots between them as if the tree were a full binary tree.
Return the **maximum width** across all levels of the binary tree (level-order
array).

## Constraints
- The number of nodes is in `[1, 3000]`.
- `-100 <= node value <= 100`

## Examples
Input: `root = [1,3,2,5,3,null,9]`
Output: `4`
Explanation: The bottom level spans positions of `5` and `9` — width `4`.

Input: `root = [1,3,2,5]`
Output: `2`
Explanation: The level with `3` and `2` has width `2`.
""",
    _TREE_PRE + """def widthOfBinaryTree(root):
    from collections import deque
    r = _build(root)
    if not r:
        return 0
    maxw = 0
    q = deque([(r, 0)])
    while q:
        n = len(q)
        first = q[0][1]
        last = 0
        for _ in range(n):
            node, idx = q.popleft()
            idx -= first
            last = idx
            if node.l:
                q.append((node.l, 2 * idx))
            if node.r:
                q.append((node.r, 2 * idx + 1))
        maxw = max(maxw, last + 1)
    return maxw
""",
    visible=[{"root": [1, 3, 2, 5, 3, None, 9]}, {"root": [1, 3, 2, 5]}],
    hidden=[{"root": [1]}, {"root": [1, 1, 1, 1, 1, 1, 1]},
            {"root": [1, 3, 2, 5, None, None, 9, 6, None, 7]},
            {"root": [0, 0, 0, 0, None, None, 0]}],
    gen=lambda r: [{"root": _rand_tree_arr(r, 1, 14, -50, 50)} for _ in range(12)],
    brute=_b_width,
    checks=[({"root": [1, 3, 2, 5, 3, None, 9]}, 4),
            ({"root": [1, 3, 2, 5]}, 2)])

add("symmetric-tree", "Symmetric Tree Check", "easy",
    ["tree", "binary-tree", "depth-first-search"], "isSymmetric",
    [("root", "int[]")], "bool",
    """
Return `true` if the binary tree (level-order array) is a **mirror image of itself**
around its center.

## Constraints
- The number of nodes is in `[0, 1000]`.
- `-100 <= node value <= 100`

## Examples
Input: `root = [1,2,2,3,4,4,3]`
Output: `true`
Explanation: The left and right subtrees mirror each other.

Input: `root = [1,2,2,null,3,null,3]`
Output: `false`
Explanation: The two `3`s sit on the same side, breaking the mirror.
""",
    _TREE_PRE + """def isSymmetric(root):
    r = _build(root)

    def mirror(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a.v == b.v and mirror(a.l, b.r) and mirror(a.r, b.l)

    return mirror(r.l, r.r) if r else True
""",
    visible=[{"root": [1, 2, 2, 3, 4, 4, 3]},
             {"root": [1, 2, 2, None, 3, None, 3]}],
    hidden=[{"root": []}, {"root": [1]}, {"root": [1, 2, 2]},
            {"root": [2, 3, 3, 4, 5, 5, 4]}],
    gen=lambda r: [_qb_symmetric(r) for _ in range(12)],
    brute=_b_symmetric,
    checks=[({"root": [1, 2, 2, 3, 4, 4, 3]}, True),
            ({"root": [1, 2, 2, None, 3, None, 3]}, False)])

add("sorted-array-to-bst", "Convert Sorted Array To Balanced BST", "easy",
    ["tree", "binary-search-tree", "divide-and-conquer"], "sortedArrayToBST",
    [("nums", "int[]")], "int[]",
    """
Given `nums` sorted in non-decreasing order, build a **height-balanced** binary
search tree and return it as a level-order array. When a range has an even number of
elements, take the **left** of the two middle elements as the subtree root (so the
answer is unique).

## Constraints
- `1 <= len(nums) <= 10^4`
- `nums` is sorted in non-decreasing order.

## Examples
Input: `nums = [-10,-3,0,5,9]`
Output: `[0,-10,5,null,-3,null,9]`
Explanation: `0` is the middle root; each half is built recursively.

Input: `nums = [1,3]`
Output: `[1,null,3]`
Explanation: With two elements the left one (`1`) is the root.
""",
    _TREE_PRE + """def sortedArrayToBST(nums):
    def build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = _N(nums[mid])
        node.l = build(lo, mid - 1)
        node.r = build(mid + 1, hi)
        return node

    return _ser(build(0, len(nums) - 1))
""",
    visible=[{"nums": [-10, -3, 0, 5, 9]}, {"nums": [1, 3]}],
    hidden=[{"nums": [0]}, {"nums": [1, 2, 3]}, {"nums": [1, 2, 3, 4]},
            {"nums": [-5, -2, 0, 1, 4, 7, 9]}],
    gen=lambda r: [_qb_sortedarr(r) for _ in range(12)],
    brute=_b_sortedbst,
    checks=[({"nums": [-10, -3, 0, 5, 9]}, [0, -10, 5, None, -3, None, 9]),
            ({"nums": [1, 3]}, [1, None, 3])])


# ===========================================================================
# qb3_large.txt import — Batch 6a: graph paths / traversal / grid
# ===========================================================================

def _qb_simple_graph(r):
    n = r.randint(1, 8)
    possible = [[i, j] for i in range(n) for j in range(i + 1, n)]
    r.shuffle(possible)
    return n, possible[:r.randint(0, len(possible))]


def _b_validpath(n, edges, source, destination):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        parent[find(u)] = find(v)
    return find(source) == find(destination)


def _b_countcomp(n, edges):
    from collections import defaultdict
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen, comp = set(), 0
    for s in range(n):
        if s not in seen:
            comp += 1
            stack = [s]
            seen.add(s)
            while stack:
                x = stack.pop()
                for nb in adj[x]:
                    if nb not in seen:
                        seen.add(nb)
                        stack.append(nb)
    return comp


def _b_hascycle(n, edges):
    from collections import defaultdict
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = set()

    def dfs(node, par):
        seen.add(node)
        for nb in adj[node]:
            if nb not in seen:
                if dfs(nb, node):
                    return True
            elif nb != par:
                return True
        return False

    for s in range(n):
        if s not in seen and dfs(s, -1):
            return True
    return False


def _qb_digraph(r):
    n = r.randint(1, 8)
    graph = [[] for _ in range(n)]
    for u in range(n):
        for v in range(n):
            if u != v and r.random() < 0.25:
                graph[u].append(v)
    return {"graph": graph}


def _b_safe(graph):
    from collections import deque
    n = len(graph)
    rev = [[] for _ in range(n)]
    outdeg = [0] * n
    for u in range(n):
        for v in graph[u]:
            rev[v].append(u)
            outdeg[u] += 1
    q = deque(i for i in range(n) if outdeg[i] == 0)
    safe = [False] * n
    while q:
        node = q.popleft()
        safe[node] = True
        for pu in rev[node]:
            outdeg[pu] -= 1
            if outdeg[pu] == 0:
                q.append(pu)
    return [i for i in range(n) if safe[i]]


def _qb_genetic(r):
    bases = "ACGT"
    L = r.randint(2, 5)
    start = "".join(r.choice(bases) for _ in range(L))
    cur, bank = start, []
    for _ in range(r.randint(0, 5)):
        i = r.randint(0, L - 1)
        cur = cur[:i] + r.choice([x for x in bases if x != cur[i]]) + cur[i + 1:]
        bank.append(cur)
    end = cur if r.random() < 0.7 else "".join(r.choice(bases) for _ in range(L))
    for _ in range(r.randint(0, 4)):
        bank.append("".join(r.choice(bases) for _ in range(L)))
    r.shuffle(bank)
    return {"startGene": start, "endGene": end, "bank": bank}


def _b_minmut(startGene, endGene, bank):
    from collections import deque
    nodes = set(bank) | {startGene}
    if endGene not in nodes:
        return -1
    adj = {x: [y for y in nodes if y != x and
               sum(a != b for a, b in zip(x, y)) == 1] for x in nodes}
    q = deque([(startGene, 0)])
    seen = {startGene}
    while q:
        g, d = q.popleft()
        if g == endGene:
            return d
        for nb in adj[g]:
            if nb not in seen:
                seen.add(nb)
                q.append((nb, d + 1))
    return -1


def _qb_altedges(r):
    n = r.randint(1, 6)

    def edges():
        return [[u, v] for u in range(n) for v in range(n)
                if u != v and r.random() < 0.3]

    return {"n": n, "redEdges": edges(), "blueEdges": edges()}


def _b_altpath(n, redEdges, blueEdges):
    from collections import deque, defaultdict
    red, blue = defaultdict(list), defaultdict(list)
    for u, v in redEdges:
        red[u].append(v)
    for u, v in blueEdges:
        blue[u].append(v)
    dist = {(0, 0): 0, (0, 1): 0}
    q = deque([(0, 0), (0, 1)])
    while q:
        node, c = q.popleft()
        for nc, adj in ((0, red), (1, blue)):
            if nc == c:
                continue
            for v in adj[node]:
                if (v, nc) not in dist:
                    dist[(v, nc)] = dist[(node, c)] + 1
                    q.append((v, nc))
    res = []
    for i in range(n):
        cand = [dist[(i, c)] for c in (0, 1) if (i, c) in dist]
        res.append(min(cand) if cand else -1)
    return res


def _qb_swim(r):
    n = r.randint(1, 5)
    vals = list(range(n * n))
    r.shuffle(vals)
    return {"grid": [vals[i * n:(i + 1) * n] for i in range(n)]}


def _b_swim(grid):
    from collections import deque
    n = len(grid)

    def reachable(t):
        if grid[0][0] > t:
            return False
        seen = [[False] * n for _ in range(n)]
        seen[0][0] = True
        q = deque([(0, 0)])
        while q:
            r, c = q.popleft()
            if r == n - 1 and c == n - 1:
                return True
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if (0 <= nr < n and 0 <= nc < n and not seen[nr][nc]
                        and grid[nr][nc] <= t):
                    seen[nr][nc] = True
                    q.append((nr, nc))
        return False

    lo, hi = grid[0][0], n * n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if reachable(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


def _count_islands(g):
    n, m = len(g), len(g[0])
    seen = [[False] * m for _ in range(n)]
    c = 0
    for r in range(n):
        for cc in range(m):
            if g[r][cc] == 1 and not seen[r][cc]:
                c += 1
                st = [(r, cc)]
                seen[r][cc] = True
                while st:
                    x, y = st.pop()
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < n and 0 <= ny < m and g[nx][ny] == 1
                                and not seen[nx][ny]):
                            seen[nx][ny] = True
                            st.append((nx, ny))
    return c


def _qb_bridge(r):
    for _ in range(80):
        n, m = r.randint(2, 5), r.randint(2, 5)
        g = [[1 if r.random() < 0.35 else 0 for _ in range(m)] for _ in range(n)]
        if _count_islands(g) == 2:
            return {"grid": g}
    return {"grid": [[0, 1], [1, 0]]}


def _b_bridge(grid):
    from collections import deque
    n, m = len(grid), len(grid[0])
    seen = [[False] * m for _ in range(n)]
    islands = []
    for r in range(n):
        for c in range(m):
            if grid[r][c] == 1 and not seen[r][c]:
                comp, st = [], [(r, c)]
                seen[r][c] = True
                while st:
                    x, y = st.pop()
                    comp.append((x, y))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < n and 0 <= ny < m and grid[nx][ny] == 1
                                and not seen[nx][ny]):
                            seen[nx][ny] = True
                            st.append((nx, ny))
                islands.append(comp)
    a, b = islands[0], set(islands[1])
    dist = {cell: 0 for cell in a}
    q = deque(a)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and (nx, ny) not in dist:
                if (nx, ny) in b:
                    return dist[(x, y)]
                if grid[nx][ny] == 0:
                    dist[(nx, ny)] = dist[(x, y)] + 1
                    q.append((nx, ny))
    return -1


def _qb_slashes(r):
    n = r.randint(1, 4)
    return {"grid": ["".join(r.choice([" ", "/", "\\"]) for _ in range(n))
                     for _ in range(n)]}


def _b_slashes(grid):
    from collections import deque
    n = len(grid)
    g = [[0] * (3 * n) for _ in range(3 * n)]
    for r in range(n):
        for c in range(n):
            ch = grid[r][c]
            if ch == '/':
                g[3 * r][3 * c + 2] = g[3 * r + 1][3 * c + 1] = g[3 * r + 2][3 * c] = 1
            elif ch == '\\':
                g[3 * r][3 * c] = g[3 * r + 1][3 * c + 1] = g[3 * r + 2][3 * c + 2] = 1
    seen = [[False] * (3 * n) for _ in range(3 * n)]
    comp = 0
    for i in range(3 * n):
        for j in range(3 * n):
            if g[i][j] == 0 and not seen[i][j]:
                comp += 1
                q = deque([(i, j)])
                seen[i][j] = True
                while q:
                    x, y = q.popleft()
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < 3 * n and 0 <= ny < 3 * n
                                and g[nx][ny] == 0 and not seen[nx][ny]):
                            seen[nx][ny] = True
                            q.append((nx, ny))
    return comp


add("path-exists-undirected", "Path Exists In Undirected Graph", "easy",
    ["graph", "union-find", "breadth-first-search"], "validPath",
    [("n", "int"), ("edges", "int[][]"), ("source", "int"),
     ("destination", "int")], "bool",
    """
There are `n` vertices labeled `0..n-1` and a list of undirected `edges`. Return
`true` if there is a path connecting `source` to `destination`.

## Constraints
- `1 <= n <= 2*10^5`
- `0 <= len(edges) <= 2*10^5`, each `edges[i] = [u, v]`
- `0 <= source, destination < n`

## Examples
Input: `n = 3, edges = [[0,1],[1,2]], source = 0, destination = 2`
Output: `true`
Explanation: `0 -> 1 -> 2` connects them.

Input: `n = 4, edges = [[0,1],[2,3]], source = 0, destination = 3`
Output: `false`
Explanation: The vertices are in different components.
""",
    """def validPath(n, edges, source, destination):
    if source == destination:
        return True
    from collections import deque, defaultdict
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {source}
    q = deque([source])
    while q:
        node = q.popleft()
        if node == destination:
            return True
        for nb in adj[node]:
            if nb not in seen:
                seen.add(nb)
                q.append(nb)
    return False
""",
    visible=[{"n": 3, "edges": [[0, 1], [1, 2]], "source": 0, "destination": 2},
             {"n": 4, "edges": [[0, 1], [2, 3]], "source": 0, "destination": 3}],
    hidden=[{"n": 1, "edges": [], "source": 0, "destination": 0},
            {"n": 2, "edges": [], "source": 0, "destination": 1},
            {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]], "source": 0,
             "destination": 4}],
    gen=lambda r: [{"n": (g := _qb_simple_graph(r))[0], "edges": g[1],
                    "source": r.randint(0, g[0] - 1),
                    "destination": r.randint(0, g[0] - 1)} for _ in range(12)],
    brute=_b_validpath,
    checks=[({"n": 3, "edges": [[0, 1], [1, 2]], "source": 0, "destination": 2},
             True),
            ({"n": 4, "edges": [[0, 1], [2, 3]], "source": 0,
              "destination": 3}, False)])

add("count-connected-components", "Count Connected Components In Graph", "medium",
    ["graph", "union-find", "depth-first-search"], "countComponents",
    [("n", "int"), ("edges", "int[][]")], "int",
    """
Given `n` vertices labeled `0..n-1` and a list of undirected `edges`, return the
number of **connected components** in the graph.

## Constraints
- `1 <= n <= 2000`
- `0 <= len(edges) <= n*(n-1)/2`, each `edges[i] = [u, v]` with `u != v`, no
  duplicate edges

## Examples
Input: `n = 5, edges = [[0,1],[1,2],[3,4]]`
Output: `2`
Explanation: Components `{0,1,2}` and `{3,4}`.

Input: `n = 3, edges = []`
Output: `3`
Explanation: Every vertex is isolated.
""",
    """def countComponents(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    count = n
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            count -= 1
    return count
""",
    visible=[{"n": 5, "edges": [[0, 1], [1, 2], [3, 4]]},
             {"n": 3, "edges": []}],
    hidden=[{"n": 1, "edges": []}, {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]},
            {"n": 4, "edges": [[0, 1], [2, 3], [0, 2]]}],
    gen=lambda r: [{"n": (g := _qb_simple_graph(r))[0], "edges": g[1]}
                   for _ in range(12)],
    brute=_b_countcomp,
    checks=[({"n": 5, "edges": [[0, 1], [1, 2], [3, 4]]}, 2),
            ({"n": 3, "edges": []}, 3)])

add("undirected-cycle", "Graph Contains Undirected Cycle", "medium",
    ["graph", "union-find", "depth-first-search"], "hasCycle",
    [("n", "int"), ("edges", "int[][]")], "bool",
    """
Given `n` vertices labeled `0..n-1` and a list of undirected `edges` (a simple
graph: no self-loops or duplicate edges), return whether the graph contains a
**cycle**.

## Constraints
- `1 <= n <= 2000`
- each `edges[i] = [u, v]` with `u != v`, no duplicate edges

## Examples
Input: `n = 3, edges = [[0,1],[1,2],[2,0]]`
Output: `true`
Explanation: The three edges form a triangle.

Input: `n = 4, edges = [[0,1],[1,2],[2,3]]`
Output: `false`
Explanation: A path graph has no cycle.
""",
    """def hasCycle(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return True
        parent[ru] = rv
    return False
""",
    visible=[{"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]},
             {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]}],
    hidden=[{"n": 1, "edges": []}, {"n": 2, "edges": [[0, 1]]},
            {"n": 5, "edges": [[0, 1], [1, 2], [3, 4], [2, 0]]}],
    gen=lambda r: [{"n": (g := _qb_simple_graph(r))[0], "edges": g[1]}
                   for _ in range(12)],
    brute=_b_hascycle,
    checks=[({"n": 3, "edges": [[0, 1], [1, 2], [2, 0]]}, True),
            ({"n": 4, "edges": [[0, 1], [1, 2], [2, 3]]}, False)])

add("eventual-safe-states", "Eventual Safe States", "medium",
    ["graph", "depth-first-search", "topological-sort"], "eventualSafeNodes",
    [("graph", "int[][]")], "int[]",
    """
`graph` is a directed graph given as an adjacency list (`graph[i]` lists the nodes
`i` points to). A node is **safe** if every path starting from it eventually reaches
a terminal node (one with no outgoing edges) — equivalently, it cannot reach a
cycle. Return all safe nodes in **ascending** order.

## Constraints
- `1 <= len(graph) <= 10^4`
- `graph[i]` contains distinct targets in `0..len(graph)-1`

## Examples
Input: `graph = [[1,2],[2,3],[5],[0],[5],[],[]]`
Output: `[2,4,5,6]`
Explanation: Nodes 5 and 6 are terminal; 2 and 4 only reach them.

Input: `graph = [[1],[2],[0]]`
Output: `[]`
Explanation: All nodes sit on a directed cycle.
""",
    """def eventualSafeNodes(graph):
    n = len(graph)
    color = [0] * n

    def dfs(u):
        if color[u] != 0:
            return color[u] == 2
        color[u] = 1
        for v in graph[u]:
            if not dfs(v):
                return False
        color[u] = 2
        return True

    return [i for i in range(n) if dfs(i)]
""",
    visible=[{"graph": [[1, 2], [2, 3], [5], [0], [5], [], []]},
             {"graph": [[1], [2], [0]]}],
    hidden=[{"graph": [[]]}, {"graph": [[0]]}, {"graph": [[1], [], [3], []]},
            {"graph": [[1, 2], [2], [0]]}],
    gen=lambda r: [_qb_digraph(r) for _ in range(12)],
    brute=_b_safe,
    checks=[({"graph": [[1, 2], [2, 3], [5], [0], [5], [], []]}, [2, 4, 5, 6]),
            ({"graph": [[1], [2], [0]]}, [])])

add("minimum-genetic-mutation", "Minimum Genetic Mutation", "medium",
    ["string", "breadth-first-search", "graph"], "minMutation",
    [("startGene", "string"), ("endGene", "string"), ("bank", "string[]")], "int",
    """
A gene is an 8-character string over `A`, `C`, `G`, `T`. One **mutation** changes a
single character, and every intermediate gene must be in `bank`. Return the minimum
number of mutations to get from `startGene` to `endGene`, or `-1` if impossible.

## Constraints
- `startGene` and `endGene` have equal length over `ACGT`
- `0 <= len(bank) <= 10`

## Examples
Input: `startGene = "AACCGGTT", endGene = "AACCGGTA", bank = ["AACCGGTA"]`
Output: `1`
Explanation: One valid mutation reaches the end gene.

Input: `startGene = "AACCGGTT", endGene = "AAACGGTA", bank = ["AACCGGTA","AACCGCTA","AAACGGTA"]`
Output: `2`
Explanation: A shortest valid chain uses two mutations.
""",
    """def minMutation(startGene, endGene, bank):
    from collections import deque
    if startGene == endGene:
        return 0
    bankset = set(bank)
    if endGene not in bankset:
        return -1
    q = deque([(startGene, 0)])
    seen = {startGene}
    while q:
        gene, d = q.popleft()
        if gene == endGene:
            return d
        for i in range(len(gene)):
            for c in "ACGT":
                if c != gene[i]:
                    ng = gene[:i] + c + gene[i + 1:]
                    if ng in bankset and ng not in seen:
                        seen.add(ng)
                        q.append((ng, d + 1))
    return -1
""",
    visible=[{"startGene": "AACCGGTT", "endGene": "AACCGGTA",
              "bank": ["AACCGGTA"]},
             {"startGene": "AACCGGTT", "endGene": "AAACGGTA",
              "bank": ["AACCGGTA", "AACCGCTA", "AAACGGTA"]}],
    hidden=[{"startGene": "AAAA", "endGene": "AAAA", "bank": []},
            {"startGene": "AAAA", "endGene": "AACA", "bank": ["AACA"]},
            {"startGene": "AAAA", "endGene": "ACGT", "bank": ["AAGA"]}],
    gen=lambda r: [_qb_genetic(r) for _ in range(12)],
    brute=_b_minmut,
    checks=[({"startGene": "AACCGGTT", "endGene": "AACCGGTA",
              "bank": ["AACCGGTA"]}, 1),
            ({"startGene": "AACCGGTT", "endGene": "AAACGGTA",
              "bank": ["AACCGGTA", "AACCGCTA", "AAACGGTA"]}, 2)])

add("shortest-alternating-path", "Shortest Alternating Color Path", "medium",
    ["graph", "breadth-first-search"], "shortestAlternatingPaths",
    [("n", "int"), ("redEdges", "int[][]"), ("blueEdges", "int[][]")], "int[]",
    """
A directed graph on `n` nodes has red edges `redEdges` and blue edges `blueEdges`.
For each node `i`, return the length of the shortest path from node `0` to `i` whose
edge colors **alternate** (no two consecutive edges share a color), or `-1` if no
such path exists.

## Constraints
- `1 <= n <= 100`
- each edge is `[from, to]`; parallel/self edges may appear

## Examples
Input: `n = 3, redEdges = [[0,1]], blueEdges = [[1,2]]`
Output: `[0,1,2]`
Explanation: Red `0->1` then blue `1->2`.

Input: `n = 3, redEdges = [[0,1],[1,2]], blueEdges = []`
Output: `[0,1,-1]`
Explanation: Two red edges cannot be used in a row.
""",
    """def shortestAlternatingPaths(n, redEdges, blueEdges):
    from collections import deque, defaultdict
    red, blue = defaultdict(list), defaultdict(list)
    for u, v in redEdges:
        red[u].append(v)
    for u, v in blueEdges:
        blue[u].append(v)
    dist = [[-1, -1] for _ in range(n)]
    dist[0][0] = dist[0][1] = 0
    q = deque([(0, 0), (0, 1)])
    while q:
        node, last = q.popleft()
        nxt = 1 - last
        for v in (blue[node] if nxt == 1 else red[node]):
            if dist[v][nxt] == -1:
                dist[v][nxt] = dist[node][last] + 1
                q.append((v, nxt))
    res = []
    for a, b in dist:
        if a == -1 and b == -1:
            res.append(-1)
        elif a == -1:
            res.append(b)
        elif b == -1:
            res.append(a)
        else:
            res.append(min(a, b))
    return res
""",
    visible=[{"n": 3, "redEdges": [[0, 1]], "blueEdges": [[1, 2]]},
             {"n": 3, "redEdges": [[0, 1], [1, 2]], "blueEdges": []}],
    hidden=[{"n": 1, "redEdges": [], "blueEdges": []},
            {"n": 2, "redEdges": [[0, 1], [1, 0]], "blueEdges": [[0, 1]]},
            {"n": 5, "redEdges": [[0, 1], [1, 2], [2, 3], [3, 4]],
             "blueEdges": [[1, 2], [2, 3], [3, 4]]}],
    gen=lambda r: [_qb_altedges(r) for _ in range(12)],
    brute=_b_altpath,
    checks=[({"n": 3, "redEdges": [[0, 1]], "blueEdges": [[1, 2]]}, [0, 1, 2]),
            ({"n": 3, "redEdges": [[0, 1], [1, 2]], "blueEdges": []},
             [0, 1, -1])])

add("swim-in-rising-water", "Swim In Rising Water", "hard",
    ["matrix", "heap", "binary-search", "union-find"], "swimInWater",
    [("grid", "int[][]")], "int",
    """
`grid[r][c]` is the elevation of cell `(r, c)`. At time `t` you may stand on any cell
with elevation `<= t`, and you swim instantly between 4-directionally adjacent
available cells. Return the **least time** `t` at which you can travel from the
top-left to the bottom-right cell. `grid` is `n x n` and is a permutation of
`0..n*n-1`.

## Constraints
- `1 <= n <= 50`
- `grid` is an `n x n` permutation of `0 .. n*n-1`

## Examples
Input: `grid = [[0,2],[1,3]]`
Output: `3`
Explanation: The destination has elevation 3, reachable only once `t = 3`.

Input: `grid = [[0,1,2],[5,4,3],[6,7,8]]`
Output: `8`
Explanation: Every route must eventually cross elevation `8`.
""",
    """def swimInWater(grid):
    import heapq
    n = len(grid)
    seen = [[False] * n for _ in range(n)]
    heap = [(grid[0][0], 0, 0)]
    seen[0][0] = True
    res = 0
    while heap:
        t, r, c = heapq.heappop(heap)
        res = max(res, t)
        if r == n - 1 and c == n - 1:
            return res
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not seen[nr][nc]:
                seen[nr][nc] = True
                heapq.heappush(heap, (grid[nr][nc], nr, nc))
    return res
""",
    visible=[{"grid": [[0, 2], [1, 3]]},
             {"grid": [[0, 1, 2], [5, 4, 3], [6, 7, 8]]}],
    hidden=[{"grid": [[0]]}, {"grid": [[0, 1], [3, 2]]},
            {"grid": [[3, 2], [0, 1]]}, {"grid": [[1, 0], [2, 3]]}],
    gen=lambda r: [_qb_swim(r) for _ in range(12)],
    brute=_b_swim,
    checks=[({"grid": [[0, 2], [1, 3]]}, 3),
            ({"grid": [[0, 1, 2], [5, 4, 3], [6, 7, 8]]}, 8)])

add("shortest-bridge", "Shortest Bridge Between Islands", "medium",
    ["matrix", "breadth-first-search", "flood-fill"], "shortestBridge",
    [("grid", "int[][]")], "int",
    """
`grid` is a binary matrix containing **exactly two** islands (4-directionally
connected groups of `1`s). Return the minimum number of `0` cells you must flip to
`1` to connect the two islands into one.

## Constraints
- `2 <= len(grid), len(grid[0]) <= 100`
- exactly two islands are present

## Examples
Input: `grid = [[0,1],[1,0]]`
Output: `1`
Explanation: Flip either water cell to join the two single-cell islands.

Input: `grid = [[1,0,0,1]]`
Output: `2`
Explanation: The two single-cell islands are separated by two water cells, both of
which must be flipped.
""",
    """def shortestBridge(grid):
    from collections import deque
    n, m = len(grid), len(grid[0])

    def nbrs(r, c):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m:
                yield nr, nc

    start = next((r, c) for r in range(n) for c in range(m) if grid[r][c] == 1)
    stack = [start]
    grid[start[0]][start[1]] = 2
    island = []
    while stack:
        r, c = stack.pop()
        island.append((r, c))
        for nr, nc in nbrs(r, c):
            if grid[nr][nc] == 1:
                grid[nr][nc] = 2
                stack.append((nr, nc))
    q = deque((r, c, 0) for r, c in island)
    seen = set(island)
    while q:
        r, c, d = q.popleft()
        for nr, nc in nbrs(r, c):
            if (nr, nc) in seen:
                continue
            if grid[nr][nc] == 1:
                return d
            seen.add((nr, nc))
            q.append((nr, nc, d + 1))
    return -1
""",
    visible=[{"grid": [[0, 1], [1, 0]]}, {"grid": [[1, 0, 0, 1]]}],
    hidden=[{"grid": [[1, 1, 1], [1, 0, 0], [1, 0, 1]]},
            {"grid": [[1, 0, 0], [0, 0, 0], [0, 0, 1]]},
            {"grid": [[1, 1, 0, 0, 0], [1, 0, 0, 0, 0], [0, 0, 0, 0, 1]]},
            {"grid": [[1, 0], [0, 1]]}],
    gen=lambda r: [_qb_bridge(r) for _ in range(12)],
    brute=_b_bridge,
    checks=[({"grid": [[0, 1], [1, 0]]}, 1),
            ({"grid": [[1, 0, 0, 1]]}, 2),
            ({"grid": [[1, 1, 1], [1, 0, 0], [1, 0, 1]]}, 1)])

add("regions-cut-by-slashes", "Regions Cut By Slashes", "medium",
    ["matrix", "union-find", "depth-first-search"], "regionsBySlashes",
    [("grid", "string[]")], "int",
    """
`grid` is an `n x n` board of characters `'/'`, `'\\\\'`, and `' '` (space). Each cell
is a unit square that a slash divides into regions. Return the **number of contiguous
regions** the whole board is divided into.

## Constraints
- `1 <= n <= 30`
- each row is a string of length `n` over `'/'`, `'\\\\'`, `' '`

## Examples
Input: `grid = [" /","/ "]`
Output: `2`
Explanation: The two slashes split the square into two regions.

Input: `grid = [" /","  "]`
Output: `1`
Explanation: A single slash does not fully enclose a separate region.
""",
    """def regionsBySlashes(grid):
    n = len(grid)
    parent = list(range(4 * n * n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    def idx(r, c, t):
        return 4 * (r * n + c) + t

    for r in range(n):
        for c in range(n):
            ch = grid[r][c]
            if ch == ' ':
                union(idx(r, c, 0), idx(r, c, 1))
                union(idx(r, c, 1), idx(r, c, 2))
                union(idx(r, c, 2), idx(r, c, 3))
            elif ch == '/':
                union(idx(r, c, 0), idx(r, c, 3))
                union(idx(r, c, 1), idx(r, c, 2))
            else:
                union(idx(r, c, 0), idx(r, c, 1))
                union(idx(r, c, 2), idx(r, c, 3))
            if r + 1 < n:
                union(idx(r, c, 2), idx(r + 1, c, 0))
            if c + 1 < n:
                union(idx(r, c, 1), idx(r, c + 1, 3))
    return sum(1 for i in range(4 * n * n) if find(i) == i)
""",
    visible=[{"grid": [" /", "/ "]}, {"grid": [" /", "  "]}],
    hidden=[{"grid": ["/"]}, {"grid": [" "]},
            {"grid": ["\\/", "/\\"]}, {"grid": ["//", "/ "]}],
    gen=lambda r: [_qb_slashes(r) for _ in range(12)],
    brute=_b_slashes,
    checks=[({"grid": [" /", "/ "]}, 2), ({"grid": [" /", "  "]}, 1),
            ({"grid": ["/\\", "\\/"]}, 5)])


# ===========================================================================
# qb3_large.txt import — Batch 6b: weighted / advanced graphs
# ===========================================================================

def _qb_calcdiv(r):
    names = "abcdef"
    k = r.randint(1, 5)
    vs = list(names[:k + 1])
    base = {v: r.choice([1, 2, 4, 8]) for v in vs}
    equations, values = [], []
    for i in range(len(vs)):
        for j in range(len(vs)):
            if i != j and r.random() < 0.4:
                a, b = vs[i], vs[j]
                equations.append([a, b])
                values.append(base[a] / base[b])
    pool = vs + ["z"]
    queries = [[r.choice(pool), r.choice(pool)] for _ in range(r.randint(1, 4))]
    return {"equations": equations, "values": values, "queries": queries}


def _b_calcdiv(equations, values, queries):
    ratio = {}
    nodes = set()
    for (a, b), v in zip(equations, values):
        nodes.add(a)
        nodes.add(b)
        ratio[(a, b)] = v
        ratio[(b, a)] = 1.0 / v
        ratio[(a, a)] = ratio[(b, b)] = 1.0
    nl = list(nodes)
    for k in nl:
        for i in nl:
            if (i, k) in ratio:
                for j in nl:
                    if (k, j) in ratio:
                        ratio[(i, j)] = ratio[(i, k)] * ratio[(k, j)]
    return [round(ratio[(x, y)], 5) if (x, y) in ratio else -1.0
            for x, y in queries]


def _qb_itinerary(r):
    airports = ["JFK", "ATL", "SFO", "LAX", "ORD", "DEN"]
    cur, tickets = "JFK", []
    for _ in range(r.randint(1, 8)):
        nxt = r.choice(airports)
        tickets.append([cur, nxt])
        cur = nxt
    r.shuffle(tickets)
    return {"tickets": tickets}


def _b_itinerary(tickets):
    from collections import defaultdict
    graph = defaultdict(list)
    for a, b in tickets:
        graph[a].append(b)
    for k in graph:
        graph[k].sort()
    n = len(tickets)
    result = []

    def dfs(node, path):
        if len(path) == n + 1:
            result.append(list(path))
            return True
        for i in range(len(graph[node])):
            nxt = graph[node][i]
            if nxt is None:
                continue
            graph[node][i] = None
            path.append(nxt)
            if dfs(nxt, path):
                return True
            path.pop()
            graph[node][i] = nxt
        return False

    dfs("JFK", ["JFK"])
    return result[0] if result else []


def _qb_tree_edges(r):
    n = r.randint(1, 10)
    return {"n": n, "edges": [[r.randint(0, v - 1), v] for v in range(1, n)]}


def _b_mht(n, edges):
    from collections import defaultdict, deque
    if n == 1:
        return [0]
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    def height(root):
        seen = {root}
        q = deque([root])
        d = 0
        while q:
            for _ in range(len(q)):
                x = q.popleft()
                for nb in adj[x]:
                    if nb not in seen:
                        seen.add(nb)
                        q.append(nb)
            if q:
                d += 1
        return d

    h = [height(i) for i in range(n)]
    m = min(h)
    return sorted(i for i in range(n) if h[i] == m)


def _qb_connected_graph(r):
    n = r.randint(2, 8)
    edges = [[r.randint(0, v - 1), v] for v in range(1, n)]
    existing = {tuple(sorted(e)) for e in edges}
    extra = [[i, j] for i in range(n) for j in range(i + 1, n)
             if (i, j) not in existing]
    r.shuffle(extra)
    edges += extra[:r.randint(0, len(extra))]
    return {"n": n, "connections": edges}


def _b_bridges(n, connections):
    from collections import defaultdict, deque

    def connected(edges):
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        seen = {0}
        q = deque([0])
        while q:
            x = q.popleft()
            for nb in adj[x]:
                if nb not in seen:
                    seen.add(nb)
                    q.append(nb)
        return len(seen) == n

    bridges = []
    for i in range(len(connections)):
        if not connected(connections[:i] + connections[i + 1:]):
            bridges.append(sorted(connections[i]))
    return sorted(bridges)


def _qb_weighted_graph(r):
    n = r.randint(2, 7)
    edges = [[r.randint(1, v - 1), v, r.randint(1, 9)] for v in range(2, n + 1)]
    existing = {(min(u, v), max(u, v)) for u, v, _ in edges}
    extra = [(i, j) for i in range(1, n + 1) for j in range(i + 1, n + 1)
             if (i, j) not in existing]
    r.shuffle(extra)
    for (u, v) in extra[:r.randint(0, len(extra))]:
        edges.append([u, v, r.randint(1, 9)])
    return {"n": n, "edges": edges}


def _b_restricted(n, edges):
    import heapq
    from collections import defaultdict
    from functools import lru_cache
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    dist = [float("inf")] * (n + 1)
    dist[n] = 0
    heap = [(0, n)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    mod = 10 ** 9 + 7

    @lru_cache(None)
    def count(u):
        if u == n:
            return 1
        return sum(count(v) for v, w in adj[u] if dist[v] < dist[u]) % mod

    return count(1) % mod


def _qb_maxprob(r):
    n = r.randint(2, 6)
    possible = [[i, j] for i in range(n) for j in range(i + 1, n)]
    r.shuffle(possible)
    edges = possible[:r.randint(0, len(possible))]
    probs = [r.choice([0.1, 0.2, 0.25, 0.5, 0.8, 1.0]) for _ in edges]
    return {"n": n, "edges": edges, "succProb": probs,
            "start": r.randint(0, n - 1), "end": r.randint(0, n - 1)}


def _b_maxprob(n, edges, succProb, start, end):
    prob = [0.0] * n
    prob[start] = 1.0
    for _ in range(n - 1):
        updated = False
        for (u, v), p in zip(edges, succProb):
            if prob[u] * p > prob[v]:
                prob[v] = prob[u] * p
                updated = True
            if prob[v] * p > prob[u]:
                prob[u] = prob[v] * p
                updated = True
        if not updated:
            break
    return round(prob[end], 5)


def _qb_redundant(r):
    n = r.randint(3, 7)
    edges = [[r.randint(1, v - 1), v] for v in range(2, n + 1)]
    existing = {(u, v) for u, v in edges}
    candidates = [[a, b] for a in range(1, n + 1) for b in range(1, n + 1)
                  if a != b and (a, b) not in existing]
    edges.append(r.choice(candidates))
    r.shuffle(edges)
    return {"edges": edges}


def _b_redundant(edges):
    from collections import defaultdict, deque
    n = len(edges)

    def is_tree(es):
        parent, nodes = {}, set()
        for u, v in es:
            if v in parent:
                return False
            parent[v] = u
            nodes.add(u)
            nodes.add(v)
        roots = [x for x in nodes if x not in parent]
        if len(roots) != 1:
            return False
        adj = defaultdict(list)
        for u, v in es:
            adj[u].append(v)
        seen, q = set(), deque([roots[0]])
        while q:
            x = q.popleft()
            if x in seen:
                return False
            seen.add(x)
            for nb in adj[x]:
                q.append(nb)
        return len(seen) == len(nodes)

    for i in range(n - 1, -1, -1):
        if is_tree(edges[:i] + edges[i + 1:]):
            return list(edges[i])
    return []


def _qb_sentsim(r):
    words = ["a", "b", "c", "d", "e", "f", "g"]
    pairs = [[r.choice(words), r.choice(words)] for _ in range(r.randint(0, 6))]
    L = r.randint(1, 4)
    return {"sentence1": [r.choice(words) for _ in range(L)],
            "sentence2": [r.choice(words) for _ in range(L)], "pairs": pairs}


def _b_sentsim(sentence1, sentence2, pairs):
    if len(sentence1) != len(sentence2):
        return False
    from collections import defaultdict, deque
    adj = defaultdict(set)
    for a, b in pairs:
        adj[a].add(b)
        adj[b].add(a)

    def connected(x, y):
        if x == y:
            return True
        if x not in adj or y not in adj:
            return False
        seen, q = {x}, deque([x])
        while q:
            c = q.popleft()
            if c == y:
                return True
            for nb in adj[c]:
                if nb not in seen:
                    seen.add(nb)
                    q.append(nb)
        return False

    return all(connected(w1, w2) for w1, w2 in zip(sentence1, sentence2))


def _qb_largestcomp(r):
    return {"nums": r.sample(range(1, 60), r.randint(1, 10))}


def _b_largestcomp(nums):
    from math import gcd
    from collections import Counter
    n = len(nums)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if gcd(nums[i], nums[j]) > 1:
                parent[find(i)] = find(j)
    cnt = Counter(find(i) for i in range(n))
    return max(cnt.values()) if cnt else 0


add("evaluate-division", "Evaluate Division Queries", "medium",
    ["graph", "union-find", "depth-first-search"], "calcEquation",
    [("equations", "string[][]"), ("values", "float[]"),
     ("queries", "string[][]")], "float[]",
    """
Each `equations[i] = [a, b]` with `values[i]` means `a / b = values[i]`. For each
query `[x, y]` return `x / y` derived from the known ratios, or `-1.0` if it cannot
be determined. Round each answer to **5 decimal places**.

## Constraints
- `1 <= len(equations) <= 20`, all values are positive
- variables are lowercase strings

## Examples
Input: `equations = [["a","b"],["b","c"]], values = [2.0,3.0], queries = [["a","c"],["c","a"]]`
Output: `[6.0,0.16667]`
Explanation: `a/c = 2*3 = 6`; `c/a = 1/6 ≈ 0.16667`.

Input: `equations = [["a","b"]], values = [2.0], queries = [["a","e"]]`
Output: `[-1.0]`
Explanation: Variable `e` never appears, so the ratio is unknown.
""",
    """def calcEquation(equations, values, queries):
    from collections import defaultdict
    graph = defaultdict(dict)
    for (a, b), v in zip(equations, values):
        graph[a][b] = v
        graph[b][a] = 1.0 / v

    def query(x, y):
        if x not in graph or y not in graph:
            return -1.0
        seen = {x}
        stack = [(x, 1.0)]
        while stack:
            node, prod = stack.pop()
            if node == y:
                return prod
            for nb, w in graph[node].items():
                if nb not in seen:
                    seen.add(nb)
                    stack.append((nb, prod * w))
        return -1.0

    return [round(query(x, y), 5) for x, y in queries]
""",
    visible=[{"equations": [["a", "b"], ["b", "c"]], "values": [2.0, 3.0],
              "queries": [["a", "c"], ["c", "a"]]},
             {"equations": [["a", "b"]], "values": [2.0],
              "queries": [["a", "e"]]}],
    hidden=[{"equations": [["a", "b"]], "values": [2.0],
             "queries": [["a", "a"], ["x", "x"]]},
            {"equations": [["x", "y"], ["y", "z"]], "values": [4.0, 2.0],
             "queries": [["x", "z"], ["z", "x"], ["x", "x"]]}],
    gen=lambda r: [_qb_calcdiv(r) for _ in range(12)],
    brute=_b_calcdiv,
    checks=[({"equations": [["a", "b"], ["b", "c"]], "values": [2.0, 3.0],
              "queries": [["a", "c"], ["c", "a"]]}, [6.0, 0.16667]),
            ({"equations": [["a", "b"]], "values": [2.0],
              "queries": [["a", "e"]]}, [-1.0])])

add("reconstruct-itinerary", "Reconstruct Itinerary", "hard",
    ["graph", "eulerian-path", "depth-first-search"], "findItinerary",
    [("tickets", "string[][]")], "string[]",
    """
You have a list of airline `tickets = [from, to]`. Among all itineraries that start
at `"JFK"` and use **all** tickets exactly once, return the one that is
**lexicographically smallest** when read as a single list (so the answer is unique).
A valid itinerary is guaranteed to exist.

## Constraints
- `1 <= len(tickets) <= 300`
- airport codes are uppercase 3-letter strings

## Examples
Input: `tickets = [["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]`
Output: `["JFK","MUC","LHR","SFO","SJC"]`
Explanation: The only itinerary using all tickets.

Input: `tickets = [["JFK","KUL"],["JFK","NRT"],["NRT","JFK"]]`
Output: `["JFK","NRT","JFK","KUL"]`
Explanation: Choosing `KUL` first would strand the `NRT` ticket.
""",
    """def findItinerary(tickets):
    from collections import defaultdict
    import heapq
    graph = defaultdict(list)
    for a, b in tickets:
        heapq.heappush(graph[a], b)
    route, stack = [], ["JFK"]
    while stack:
        while graph[stack[-1]]:
            stack.append(heapq.heappop(graph[stack[-1]]))
        route.append(stack.pop())
    return route[::-1]
""",
    visible=[{"tickets": [["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"],
                          ["LHR", "SFO"]]},
             {"tickets": [["JFK", "KUL"], ["JFK", "NRT"], ["NRT", "JFK"]]}],
    hidden=[{"tickets": [["JFK", "ATL"]]},
            {"tickets": [["JFK", "A"], ["A", "JFK"], ["JFK", "B"]]},
            {"tickets": [["JFK", "SFO"], ["JFK", "ATL"], ["SFO", "ATL"],
                         ["ATL", "JFK"], ["ATL", "SFO"]]}],
    gen=lambda r: [_qb_itinerary(r) for _ in range(12)],
    brute=_b_itinerary,
    checks=[({"tickets": [["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"],
                          ["LHR", "SFO"]]},
             ["JFK", "MUC", "LHR", "SFO", "SJC"]),
            ({"tickets": [["JFK", "KUL"], ["JFK", "NRT"], ["NRT", "JFK"]]},
             ["JFK", "NRT", "JFK", "KUL"])])

add("minimum-height-trees", "Minimum Height Trees Roots", "medium",
    ["graph", "tree", "topological-sort"], "findMinHeightTrees",
    [("n", "int"), ("edges", "int[][]")], "int[]",
    """
Given an undirected **tree** of `n` nodes labeled `0..n-1` (so `len(edges) == n-1`),
a node may be chosen as root. Return all root labels that give the tree the
**minimum possible height**. The answer may be in any order.

## Constraints
- `1 <= n <= 2*10^4`
- `edges` forms a valid tree

## Examples
Input: `n = 4, edges = [[1,0],[1,2],[1,3]]`
Output: `[1]`
Explanation: Rooting at `1` gives height `1`.

Input: `n = 6, edges = [[3,0],[3,1],[3,2],[3,4],[5,4]]`
Output: `[3,4]`
Explanation: Both centers give the minimum height.
""",
    """def findMinHeightTrees(n, edges):
    if n == 1:
        return [0]
    from collections import defaultdict
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    leaves = [x for x in range(n) if len(adj[x]) == 1]
    remaining = n
    while remaining > 2:
        remaining -= len(leaves)
        new_leaves = []
        for leaf in leaves:
            nb = adj[leaf].pop()
            adj[nb].discard(leaf)
            if len(adj[nb]) == 1:
                new_leaves.append(nb)
        leaves = new_leaves
    return sorted(leaves)
""",
    visible=[{"n": 4, "edges": [[1, 0], [1, 2], [1, 3]]},
             {"n": 6, "edges": [[3, 0], [3, 1], [3, 2], [3, 4], [5, 4]]}],
    hidden=[{"n": 1, "edges": []}, {"n": 2, "edges": [[0, 1]]},
            {"n": 3, "edges": [[0, 1], [1, 2]]},
            {"n": 7, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6]]}],
    gen=lambda r: [_qb_tree_edges(r) for _ in range(12)],
    brute=_b_mht,
    checks=[({"n": 4, "edges": [[1, 0], [1, 2], [1, 3]]}, [1]),
            ({"n": 6, "edges": [[3, 0], [3, 1], [3, 2], [3, 4], [5, 4]]},
             [3, 4])])

add("critical-connections", "Critical Connections In Network", "hard",
    ["graph", "bridges", "depth-first-search"], "criticalConnections",
    [("n", "int"), ("connections", "int[][]")], "int[][]",
    """
A network of `n` servers `0..n-1` is connected by undirected `connections`. A
**critical connection** (bridge) is an edge whose removal disconnects the network.
Return all critical connections, each as `[min, max]`, sorted ascending.

## Constraints
- `1 <= n <= 10^5`
- the graph is connected; no duplicate edges or self-loops

## Examples
Input: `n = 4, connections = [[0,1],[1,2],[2,0],[1,3]]`
Output: `[[1,3]]`
Explanation: The triangle `0-1-2` has no bridges; only `1-3` is critical.

Input: `n = 2, connections = [[0,1]]`
Output: `[[0,1]]`
Explanation: Removing the only edge splits the network.
""",
    """def criticalConnections(n, connections):
    import sys
    from collections import defaultdict
    sys.setrecursionlimit(300000)
    adj = defaultdict(list)
    for u, v in connections:
        adj[u].append(v)
        adj[v].append(u)
    disc = [-1] * n
    low = [0] * n
    bridges = []
    timer = [0]

    def dfs(u, parent):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        skip_parent = True
        for v in adj[u]:
            if v == parent and skip_parent:
                skip_parent = False
                continue
            if disc[v] == -1:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.append(sorted((u, v)))
            else:
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if disc[i] == -1:
            dfs(i, -1)
    return sorted(bridges)
""",
    visible=[{"n": 4, "connections": [[0, 1], [1, 2], [2, 0], [1, 3]]},
             {"n": 2, "connections": [[0, 1]]}],
    hidden=[{"n": 1, "connections": []},
            {"n": 3, "connections": [[0, 1], [1, 2]]},
            {"n": 5, "connections": [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4]]},
            {"n": 4, "connections": [[0, 1], [1, 2], [2, 3], [3, 0]]}],
    gen=lambda r: [_qb_connected_graph(r) for _ in range(12)],
    brute=_b_bridges,
    checks=[({"n": 4, "connections": [[0, 1], [1, 2], [2, 0], [1, 3]]},
             [[1, 3]]), ({"n": 2, "connections": [[0, 1]]}, [[0, 1]])])

add("number-of-restricted-paths", "Number Of Restricted Paths", "medium",
    ["graph", "dijkstra", "dynamic-programming"], "countRestrictedPaths",
    [("n", "int"), ("edges", "int[][]")], "int",
    """
An undirected weighted graph has nodes `1..n`; `edges[i] = [u, v, w]`. Let `dist(x)`
be the shortest-path distance from `x` to node `n`. A **restricted path** goes from
node `1` to node `n` such that `dist` strictly **decreases** at every step. Return
the number of restricted paths, modulo `10^9 + 7`.

## Constraints
- `1 <= n <= 2*10^4`
- the graph is connected with positive weights

## Examples
Input: `n = 5, edges = [[1,2,3],[1,3,3],[2,3,1],[1,4,2],[5,2,2],[3,5,1],[5,4,10]]`
Output: `3`
Explanation: Three paths from 1 to 5 strictly decrease distance-to-5.

Input: `n = 3, edges = [[1,2,1],[2,3,1],[1,3,3]]`
Output: `2`
Explanation: `dist(1)=2, dist(2)=1, dist(3)=0`. Both `1 -> 2 -> 3` and the direct
`1 -> 3` strictly decrease distance-to-3.
""",
    """def countRestrictedPaths(n, edges):
    import heapq
    from collections import defaultdict
    MOD = 10 ** 9 + 7
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    dist = [float('inf')] * (n + 1)
    dist[n] = 0
    heap = [(0, n)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    dp = [0] * (n + 1)
    dp[n] = 1
    for u in sorted(range(1, n + 1), key=lambda x: dist[x]):
        if u == n:
            continue
        dp[u] = sum(dp[v] for v, w in adj[u] if dist[v] < dist[u]) % MOD
    return dp[1] % MOD
""",
    visible=[{"n": 5, "edges": [[1, 2, 3], [1, 3, 3], [2, 3, 1], [1, 4, 2],
                               [5, 2, 2], [3, 5, 1], [5, 4, 10]]},
             {"n": 3, "edges": [[1, 2, 1], [2, 3, 1], [1, 3, 3]]}],
    hidden=[{"n": 2, "edges": [[1, 2, 1]]},
            {"n": 4, "edges": [[1, 2, 1], [2, 4, 1], [1, 3, 1], [3, 4, 1]]},
            {"n": 3, "edges": [[1, 2, 1], [1, 3, 1], [2, 3, 1]]}],
    gen=lambda r: [_qb_weighted_graph(r) for _ in range(12)],
    brute=_b_restricted,
    checks=[({"n": 5, "edges": [[1, 2, 3], [1, 3, 3], [2, 3, 1], [1, 4, 2],
                                [5, 2, 2], [3, 5, 1], [5, 4, 10]]}, 3),
            ({"n": 3, "edges": [[1, 2, 1], [2, 3, 1], [1, 3, 3]]}, 2)])

add("maximum-probability-path", "Maximum Probability Path", "medium",
    ["graph", "dijkstra", "shortest-path"], "maxProbability",
    [("n", "int"), ("edges", "int[][]"), ("succProb", "float[]"),
     ("start", "int"), ("end", "int")], "float",
    """
An undirected graph on `n` nodes has edges `edges[i] = [a, b]` that succeed with
probability `succProb[i]`. Return the **maximum probability** of reaching `end` from
`start` (the product of edge probabilities along a path), or `0` if `end` is
unreachable. Round the answer to **5 decimal places**.

## Constraints
- `2 <= n <= 10^4`
- `0 <= succProb[i] <= 1`

## Examples
Input: `n = 3, edges = [[0,1],[1,2],[0,2]], succProb = [0.5,0.5,0.2], start = 0, end = 2`
Output: `0.25`
Explanation: `0 -> 1 -> 2` gives `0.5*0.5 = 0.25`, beating the direct `0.2`.

Input: `n = 3, edges = [[0,1]], succProb = [0.5], start = 0, end = 2`
Output: `0.0`
Explanation: Node `2` is unreachable.
""",
    """def maxProbability(n, edges, succProb, start, end):
    import heapq
    from collections import defaultdict
    adj = defaultdict(list)
    for (u, v), p in zip(edges, succProb):
        adj[u].append((v, p))
        adj[v].append((u, p))
    prob = [0.0] * n
    prob[start] = 1.0
    heap = [(-1.0, start)]
    while heap:
        negp, u = heapq.heappop(heap)
        p = -negp
        if u == end:
            return round(p, 5)
        if p < prob[u]:
            continue
        for v, w in adj[u]:
            if p * w > prob[v]:
                prob[v] = p * w
                heapq.heappush(heap, (-prob[v], v))
    return round(prob[end], 5)
""",
    visible=[{"n": 3, "edges": [[0, 1], [1, 2], [0, 2]],
              "succProb": [0.5, 0.5, 0.2], "start": 0, "end": 2},
             {"n": 3, "edges": [[0, 1]], "succProb": [0.5],
              "start": 0, "end": 2}],
    hidden=[{"n": 2, "edges": [[0, 1]], "succProb": [0.8], "start": 0, "end": 1},
            {"n": 2, "edges": [], "succProb": [], "start": 0, "end": 1},
            {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]],
             "succProb": [0.5, 0.5, 0.5], "start": 0, "end": 3}],
    gen=lambda r: [_qb_maxprob(r) for _ in range(12)],
    brute=_b_maxprob,
    checks=[({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]],
              "succProb": [0.5, 0.5, 0.2], "start": 0, "end": 2}, 0.25),
            ({"n": 3, "edges": [[0, 1]], "succProb": [0.5],
              "start": 0, "end": 2}, 0.0)])

add("redundant-directed-connection", "Redundant Directed Connection", "hard",
    ["graph", "union-find", "tree"], "findRedundantDirectedConnection",
    [("edges", "int[][]")], "int[]",
    """
A rooted tree on nodes `1..n` had **one extra directed edge** added, producing
`edges` (with exactly `n` edges). Return the edge that can be removed so the result
is again a rooted tree. If several edges qualify, return the one that appears **last**
in `edges`.

## Constraints
- `3 <= len(edges) <= 1000`
- nodes are labeled `1..n`

## Examples
Input: `edges = [[1,2],[1,3],[2,3]]`
Output: `[2,3]`
Explanation: Node `3` has two parents; removing `[2,3]` restores a tree.

Input: `edges = [[1,2],[2,3],[3,1]]`
Output: `[3,1]`
Explanation: The edge `[3,1]` closes a directed cycle.
""",
    """def findRedundantDirectedConnection(edges):
    n = len(edges)
    parent = [0] * (n + 1)
    cand1 = cand2 = None
    for i, (u, v) in enumerate(edges):
        if parent[v] != 0:
            cand1 = [parent[v], v]
            cand2 = [u, v]
            edges[i] = [0, 0]
            break
        parent[v] = u
    uf = list(range(n + 1))

    def find(x):
        while uf[x] != x:
            uf[x] = uf[uf[x]]
            x = uf[x]
        return x

    for u, v in edges:
        if u == 0:
            continue
        ru, rv = find(u), find(v)
        if ru == rv:
            return cand1 if cand1 else [u, v]
        uf[rv] = ru
    return cand2
""",
    visible=[{"edges": [[1, 2], [1, 3], [2, 3]]},
             {"edges": [[1, 2], [2, 3], [3, 1]]}],
    hidden=[{"edges": [[2, 1], [3, 1], [4, 2], [1, 4]]},
            {"edges": [[1, 2], [2, 3], [3, 4], [4, 1], [1, 5]]},
            {"edges": [[4, 1], [1, 2], [2, 3], [3, 4]]}],
    gen=lambda r: [_qb_redundant(r) for _ in range(12)],
    brute=_b_redundant,
    checks=[({"edges": [[1, 2], [1, 3], [2, 3]]}, [2, 3]),
            ({"edges": [[1, 2], [2, 3], [3, 1]]}, [3, 1])])

add("sentence-similarity", "Sentence Similarity With Synonyms", "medium",
    ["graph", "union-find", "string"], "areSentencesSimilarTwo",
    [("sentence1", "string[]"), ("sentence2", "string[]"),
     ("pairs", "string[][]")], "bool",
    """
Two words are similar if they are equal or connected **transitively** through the
synonym `pairs`. Return whether `sentence1` and `sentence2` are similar: they must
have the same length and each pair of corresponding words must be similar.

## Constraints
- `0 <= len(sentence1), len(sentence2) <= 1000`
- `0 <= len(pairs) <= 2000`

## Examples
Input: `s1 = ["great","acting"], s2 = ["fine","drama"], pairs = [["great","good"],["fine","good"],["acting","drama"]]`
Output: `true`
Explanation: `great~good~fine` and `acting~drama`.

Input: `s1 = ["great"], s2 = ["bad"], pairs = [["great","good"]]`
Output: `false`
Explanation: `bad` is in no synonym group with `great`.
""",
    """def areSentencesSimilarTwo(sentence1, sentence2, pairs):
    if len(sentence1) != len(sentence2):
        return False
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        parent[find(a)] = find(b)
    for w1, w2 in zip(sentence1, sentence2):
        if w1 == w2:
            continue
        if w1 not in parent or w2 not in parent or find(w1) != find(w2):
            return False
    return True
""",
    visible=[{"sentence1": ["great", "acting"], "sentence2": ["fine", "drama"],
              "pairs": [["great", "good"], ["fine", "good"],
                        ["acting", "drama"]]},
             {"sentence1": ["great"], "sentence2": ["bad"],
              "pairs": [["great", "good"]]}],
    hidden=[{"sentence1": [], "sentence2": [], "pairs": []},
            {"sentence1": ["a"], "sentence2": ["a", "b"], "pairs": []},
            {"sentence1": ["a", "b"], "sentence2": ["b", "a"],
             "pairs": [["a", "b"]]}],
    gen=lambda r: [_qb_sentsim(r) for _ in range(12)],
    brute=_b_sentsim,
    checks=[({"sentence1": ["great", "acting"], "sentence2": ["fine", "drama"],
              "pairs": [["great", "good"], ["fine", "good"],
                        ["acting", "drama"]]}, True),
            ({"sentence1": ["great"], "sentence2": ["bad"],
              "pairs": [["great", "good"]]}, False)])

add("largest-component-common-factor", "Largest Component By Common Factor",
    "hard", ["graph", "union-find", "math"], "largestComponentSize",
    [("nums", "int[]")], "int",
    """
Build a graph whose nodes are the values in `nums` (all distinct); connect two values
if they share a **common factor greater than 1**. Return the size of the largest
connected component.

## Constraints
- `1 <= len(nums) <= 2*10^4`
- `1 <= nums[i] <= 10^5`, values are distinct

## Examples
Input: `nums = [4,6,15,35]`
Output: `4`
Explanation: `4-6` (2), `6-15` (3), `15-35` (5) connect everything.

Input: `nums = [20,50,9,63]`
Output: `2`
Explanation: `20-50` (10) and `9-63` (9) form two size-2 components.
""",
    """def largestComponentSize(nums):
    from collections import Counter
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        parent[find(a)] = find(b)

    def primes(x):
        ps = []
        d = 2
        while d * d <= x:
            if x % d == 0:
                ps.append(d)
                while x % d == 0:
                    x //= d
            d += 1
        if x > 1:
            ps.append(x)
        return ps

    for v in nums:
        for p in primes(v):
            union(v, ('p', p))
    cnt = Counter(find(v) for v in nums)
    return max(cnt.values()) if cnt else 0
""",
    visible=[{"nums": [4, 6, 15, 35]}, {"nums": [20, 50, 9, 63]}],
    hidden=[{"nums": [1]}, {"nums": [2, 3, 5, 7]}, {"nums": [6, 10, 15]},
            {"nums": [2, 4, 8, 16, 3]}],
    gen=lambda r: [_qb_largestcomp(r) for _ in range(12)],
    brute=_b_largestcomp,
    checks=[({"nums": [4, 6, 15, 35]}, 4), ({"nums": [20, 50, 9, 63]}, 2),
            ({"nums": [6, 10, 15]}, 3)])


# ===========================================================================
# qb3_large.txt import — Batch 7: linked-list / systems
# ===========================================================================

def _qb_addtwo(r):
    def lst():
        d = [r.randint(0, 9) for _ in range(r.randint(1, 6))]
        if len(d) > 1 and d[-1] == 0:
            d[-1] = r.randint(1, 9)
        return d

    return {"l1": lst(), "l2": lst()}


def _b_addtwo(l1, l2):
    a = int("".join(str(x) for x in reversed(l1)))
    b = int("".join(str(x) for x in reversed(l2)))
    return [int(c) for c in reversed(str(a + b))]


def _qb_reversek(r):
    n = r.randint(0, 10)
    return {"head": [r.randint(0, 50) for _ in range(n)], "k": r.randint(1, 5)}


def _b_reversek(head, k):
    res, i = [], 0
    while i < len(head):
        group = head[i:i + k]
        res += group[::-1] if len(group) == k else group
        i += k
    return res


def _qb_logs(r):
    logs = []
    for _ in range(r.randint(1, 8)):
        ident = r.choice("abcdefg") + str(r.randint(0, 9))
        if r.random() < 0.5:
            content = " ".join(str(r.randint(0, 9)) for _ in range(r.randint(1, 3)))
        else:
            content = " ".join(r.choice(["art", "car", "can", "zoo", "act"])
                                for _ in range(r.randint(1, 3)))
        logs.append(ident + " " + content)
    return {"logs": logs}


def _b_reorderlogs(logs):
    letters, digits = [], []
    for log in logs:
        rest = log.split(" ", 1)[1]
        (digits if rest[0].isdigit() else letters).append(log)
    letters.sort(key=lambda log: (log.split(" ", 1)[1], log.split(" ", 1)[0]))
    return letters + digits


def _b_tictactoe(n, moves):
    res = []
    board = [[0] * n for _ in range(n)]
    for r, c, p in moves:
        board[r][c] = p
        w = 0
        for player in (1, 2):
            won = any(all(board[i][j] == player for j in range(n)) for i in range(n))
            won = won or any(all(board[i][j] == player for i in range(n))
                             for j in range(n))
            won = won or all(board[i][i] == player for i in range(n))
            won = won or all(board[i][n - 1 - i] == player for i in range(n))
            if won:
                w = player
        res.append(w)
    return res


def _qb_ttt(r):
    n = r.randint(2, 4)
    cells = [(i, j) for i in range(n) for j in range(n)]
    r.shuffle(cells)
    moves = [[i, j, 1 if idx % 2 == 0 else 2] for idx, (i, j) in enumerate(cells)]
    res = _b_tictactoe(n, moves)
    cut = len(moves)
    for idx, w in enumerate(res):
        if w != 0:
            cut = idx + 1
            break
    return {"n": n, "moves": moves[:cut]}


def _qb_ledger(r):
    accts = ["a", "b", "c", "d"]
    out = []
    for _ in range(r.randint(0, 8)):
        frm = r.choice(accts)
        to = r.choice([a for a in accts if a != frm])
        out.append([frm, to, r.randint(1, 100)])
    return {"transactions": out}


def _b_ledger(transactions):
    from collections import defaultdict
    incoming, outgoing, accounts = defaultdict(int), defaultdict(int), set()
    for frm, to, amt in transactions:
        outgoing[frm] += amt
        incoming[to] += amt
        accounts.add(frm)
        accounts.add(to)
    return {a: incoming[a] - outgoing[a] for a in accounts}


def _qb_sessionize(r):
    users = ["a", "b", "u"]
    n = r.randint(1, 10)
    times = sorted(r.sample(range(1, 40), n))
    return {"events": [[r.choice(users), t] for t in times], "gap": r.randint(1, 8)}


def _b_sessionize(events, gap):
    from collections import defaultdict
    by_user = defaultdict(list)
    for user, t in events:
        by_user[user].append(t)
    sessions = []
    for user, times in by_user.items():
        times.sort()
        start = prev = times[0]
        for t in times[1:]:
            if t - prev > gap:
                sessions.append([user, [start, prev]])
                start = t
            prev = t
        sessions.append([user, [start, prev]])
    sessions.sort(key=lambda x: (x[1][0], x[1][1], x[0]))
    return sessions


def _qb_kafka(r):
    return {"processed": [r.randint(0, 12) for _ in range(r.randint(1, 12))]}


def _b_kafka(processed):
    s = sorted(set(processed))
    expected, last = 0, -1
    for x in s:
        if x == expected:
            last = x
            expected += 1
        elif x > expected:
            break
    return last


def _qb_multipart(r):
    expected = r.randint(1, 6)
    nums = list(range(1, expected + 1))
    if r.random() < 0.4 and len(nums) > 1:
        nums.remove(r.choice(nums))
    r.shuffle(nums)
    return {"parts": [[pn, r.randint(1, 20)] for pn in nums], "expected": expected}


def _b_multipart(parts, expected):
    nums = {pn for pn, b in parts}
    return [all(i in nums for i in range(1, expected + 1)),
            sum(b for pn, b in parts)]


def _qb_dedup(r):
    keys = ["a", "b", "x", "y"]
    n = r.randint(1, 10)
    times = sorted(r.sample(range(1, 40), n))
    return {"events": [[r.choice(keys), t] for t in times], "window": r.randint(1, 8)}


def _b_dedup(events, window):
    last, delivered = {}, set()
    for i, (key, t) in enumerate(events):
        if key not in last or t - last[key] > window:
            delivered.add(i)
            last[key] = t
    return [list(events[i]) for i in range(len(events)) if i in delivered]


def _qb_reserve(r):
    skus = ["A", "B", "C"]
    stock = {s: r.randint(0, 10) for s in skus if r.random() < 0.7}
    requests = [[r.choice(skus), r.randint(1, 6)] for _ in range(r.randint(1, 8))]
    return {"stock": stock, "requests": requests}


def _b_reserve(stock, requests):
    rem, out = dict(stock), []
    for sku, qty in requests:
        cur = rem.get(sku, 0)
        ok = cur >= qty
        out.append(ok)
        if ok:
            rem[sku] = cur - qty
    return out


add("add-two-numbers", "Add Two Numbers In Linked Lists", "medium",
    ["linked-list", "math"], "addTwoNumbers",
    [("l1", "int[]"), ("l2", "int[]")], "int[]",
    """
Two non-empty lists `l1` and `l2` store the digits of non-negative integers in
**reverse** order (the ones digit first), one digit per element. Return the digits of
their sum in the same reverse-order list format.

## Constraints
- `1 <= len(l1), len(l2) <= 100`
- each element is a digit `0..9`; no leading zero except the number `0` itself

## Examples
Input: `l1 = [2,4,3], l2 = [5,6,4]`
Output: `[7,0,8]`
Explanation: `342 + 465 = 807`, stored as `[7,0,8]`.

Input: `l1 = [9,9], l2 = [1]`
Output: `[0,0,1]`
Explanation: `99 + 1 = 100`.
""",
    """def addTwoNumbers(l1, l2):
    res, carry, i = [], 0, 0
    while i < len(l1) or i < len(l2) or carry:
        d = carry
        if i < len(l1):
            d += l1[i]
        if i < len(l2):
            d += l2[i]
        res.append(d % 10)
        carry = d // 10
        i += 1
    return res
""",
    visible=[{"l1": [2, 4, 3], "l2": [5, 6, 4]}, {"l1": [9, 9], "l2": [1]}],
    hidden=[{"l1": [0], "l2": [0]}, {"l1": [5], "l2": [5]},
            {"l1": [9, 9, 9], "l2": [1]}, {"l1": [1, 2, 3], "l2": [4, 5, 6]}],
    gen=lambda r: [_qb_addtwo(r) for _ in range(12)],
    brute=_b_addtwo,
    checks=[({"l1": [2, 4, 3], "l2": [5, 6, 4]}, [7, 0, 8]),
            ({"l1": [9, 9], "l2": [1]}, [0, 0, 1])])

add("reverse-k-group", "Reverse Nodes In K Group", "hard",
    ["linked-list", "recursion"], "reverseKGroup",
    [("head", "int[]"), ("k", "int")], "int[]",
    """
Given a linked list as an array `head`, reverse its nodes `k` at a time and return
the resulting list. Nodes left over (fewer than `k`) at the end keep their original
order.

## Constraints
- `0 <= len(head) <= 5000`
- `1 <= k <= len(head)` (or `k` may exceed a short list, leaving it unchanged)

## Examples
Input: `head = [1,2,3,4,5], k = 2`
Output: `[2,1,4,3,5]`
Explanation: Reverse each consecutive pair; the trailing `5` stays.

Input: `head = [1,2,3,4,5], k = 3`
Output: `[3,2,1,4,5]`
Explanation: Only the first full group of three is reversed.
""",
    """def reverseKGroup(head, k):
    res, i, n = [], 0, len(head)
    while i + k <= n:
        res.extend(head[i:i + k][::-1])
        i += k
    res.extend(head[i:])
    return res
""",
    visible=[{"head": [1, 2, 3, 4, 5], "k": 2},
             {"head": [1, 2, 3, 4, 5], "k": 3}],
    hidden=[{"head": [], "k": 1}, {"head": [1], "k": 1}, {"head": [1, 2], "k": 3},
            {"head": [1, 2, 3, 4], "k": 4}],
    gen=lambda r: [_qb_reversek(r) for _ in range(12)],
    brute=_b_reversek,
    checks=[({"head": [1, 2, 3, 4, 5], "k": 2}, [2, 1, 4, 3, 5]),
            ({"head": [1, 2, 3, 4, 5], "k": 3}, [3, 2, 1, 4, 5])])

add("log-reordering", "Log Reordering", "medium",
    ["string", "sorting"], "reorderLogFiles", [("logs", "string[]")], "string[]",
    """
Each log is a space-separated string whose first token is an identifier. A
**letter-log** has words after the identifier; a **digit-log** has only digits.
Reorder so all letter-logs come first, sorted by content (then by identifier to
break ties), followed by the digit-logs in their **original** order.

## Constraints
- `1 <= len(logs) <= 100`
- each log has an identifier followed by content that is all letters or all digits

## Examples
Input: `logs = ["d1 8 1","l1 art can","l2 art zero"]`
Output: `["l1 art can","l2 art zero","d1 8 1"]`
Explanation: Letter-logs sorted by content, then the digit-log.

Input: `logs = ["a1 9 2","g1 act car"]`
Output: `["g1 act car","a1 9 2"]`
Explanation: The letter-log moves ahead of the digit-log.
""",
    """def reorderLogFiles(logs):
    def key(log):
        ident, rest = log.split(" ", 1)
        if rest[0].isdigit():
            return (1,)
        return (0, rest, ident)

    return sorted(logs, key=key)
""",
    visible=[{"logs": ["d1 8 1", "l1 art can", "l2 art zero"]},
             {"logs": ["a1 9 2", "g1 act car"]}],
    hidden=[{"logs": ["a1 1 2"]}, {"logs": ["x1 abc", "y1 abc"]},
            {"logs": ["d1 5", "d2 3", "l1 b a", "l2 a b"]}],
    gen=lambda r: [_qb_logs(r) for _ in range(12)],
    brute=_b_reorderlogs,
    checks=[({"logs": ["d1 8 1", "l1 art can", "l2 art zero"]},
             ["l1 art can", "l2 art zero", "d1 8 1"]),
            ({"logs": ["a1 9 2", "g1 act car"]},
             ["g1 act car", "a1 9 2"])])

add("tic-tac-toe-winner", "Tic Tac Toe Winner", "medium",
    ["array", "simulation", "matrix"], "tictactoe",
    [("n", "int"), ("moves", "int[][]")], "int[]",
    """
On an `n x n` tic-tac-toe board, `moves[i] = [row, col, player]` is applied in order
(player is `1` or `2`). For each move, output the player who has just won (completed
a full row, column, or diagonal), or `0` if no one has won yet. Return one result per
move.

## Constraints
- `1 <= n <= 100`
- moves are valid: distinct cells, players alternate

## Examples
Input: `n = 3, moves = [[0,0,1],[1,1,2],[0,1,1],[2,2,2],[0,2,1]]`
Output: `[0,0,0,0,1]`
Explanation: Player 1 completes the top row on the last move.

Input: `n = 2, moves = [[0,0,2],[1,1,2]]`
Output: `[0,2]`
Explanation: Player 2 completes the main diagonal.
""",
    """def tictactoe(n, moves):
    rows = [[0] * n for _ in range(2)]
    cols = [[0] * n for _ in range(2)]
    diag = [0, 0]
    anti = [0, 0]
    res = []
    for r, c, p in moves:
        pi = p - 1
        rows[pi][r] += 1
        cols[pi][c] += 1
        if r == c:
            diag[pi] += 1
        if r + c == n - 1:
            anti[pi] += 1
        if (rows[pi][r] == n or cols[pi][c] == n or diag[pi] == n
                or anti[pi] == n):
            res.append(p)
        else:
            res.append(0)
    return res
""",
    visible=[{"n": 3, "moves": [[0, 0, 1], [1, 1, 2], [0, 1, 1], [2, 2, 2],
                               [0, 2, 1]]},
             {"n": 2, "moves": [[0, 0, 2], [1, 1, 2]]}],
    hidden=[{"n": 1, "moves": [[0, 0, 1]]},
            {"n": 3, "moves": [[0, 0, 1], [0, 1, 2], [1, 1, 1], [0, 2, 2],
                               [2, 2, 1]]},
            {"n": 2, "moves": [[0, 0, 1], [0, 1, 2], [1, 0, 1]]}],
    gen=lambda r: [_qb_ttt(r) for _ in range(12)],
    brute=_b_tictactoe,
    checks=[({"n": 3, "moves": [[0, 0, 1], [1, 1, 2], [0, 1, 1], [2, 2, 2],
                                [0, 2, 1]]}, [0, 0, 0, 0, 1]),
            ({"n": 2, "moves": [[0, 0, 2], [1, 1, 2]]}, [0, 2])])

add("payment-ledger-balance", "Payment Ledger Balance", "easy",
    ["hash-table", "simulation"], "ledgerBalance",
    [("transactions", "[string,string,int][]")], "object",
    """
Each transaction `[from, to, amount]` moves `amount` from account `from` to account
`to`. Return a map from every account that appears to its **net balance** (incoming
minus outgoing).

## Constraints
- `0 <= len(transactions) <= 2*10^5`
- identifiers are non-empty strings; amounts fit in a signed 64-bit integer

## Examples
Input: `transactions = [["a","b",5],["b","c",2]]`
Output: `{"a":-5,"b":3,"c":2}`
Explanation: `a` pays 5; `b` receives 5 and pays 2 (net +3); `c` receives 2.

Input: `transactions = []`
Output: `{}`
Explanation: With no transactions, no account has a balance.
""",
    """def ledgerBalance(transactions):
    bal = {}
    for frm, to, amt in transactions:
        bal[frm] = bal.get(frm, 0) - amt
        bal[to] = bal.get(to, 0) + amt
    return bal
""",
    visible=[{"transactions": [["a", "b", 5], ["b", "c", 2]]},
             {"transactions": []}],
    hidden=[{"transactions": [["a", "b", 10]]},
            {"transactions": [["x", "y", 3], ["y", "x", 3]]},
            {"transactions": [["a", "b", 1], ["a", "c", 2], ["b", "c", 1]]}],
    gen=lambda r: [_qb_ledger(r) for _ in range(12)],
    brute=_b_ledger,
    checks=[({"transactions": [["a", "b", 5], ["b", "c", 2]]},
             {"a": -5, "b": 3, "c": 2}),
            ({"transactions": []}, {})])

add("log-sessionization", "Log Sessionization", "medium",
    ["hash-table", "sorting", "simulation"], "sessionize",
    [("events", "[string,int][]"), ("gap", "int")], "[string,[int,int]][]",
    """
`events` is a list of `[user, time]` pairs sorted by `time`. For each user, group
consecutive events into **sessions**, starting a new session whenever the gap to the
previous event for that user is **strictly greater** than `gap`. Return each session
as `[user, [start_time, end_time]]`, sorted by `start_time`, then `end_time`, then
`user`.

## Constraints
- `0 <= len(events) <= 2*10^5`
- `events` is sorted by `time`; `gap >= 0`

## Examples
Input: `events = [["u",1],["u",3],["u",10]], gap = 5`
Output: `[["u",[1,3]],["u",[10,10]]]`
Explanation: `3 -> 10` exceeds the gap, starting a new session.

Input: `events = [["a",2]], gap = 5`
Output: `[["a",[2,2]]]`
Explanation: A single event is its own session.
""",
    """def sessionize(events, gap):
    cur = {}
    sessions = []
    for user, t in events:
        if user in cur and t - cur[user][1] <= gap:
            cur[user][1] = t
        else:
            if user in cur:
                sessions.append([user, [cur[user][0], cur[user][1]]])
            cur[user] = [t, t]
    for user, (s, e) in cur.items():
        sessions.append([user, [s, e]])
    sessions.sort(key=lambda x: (x[1][0], x[1][1], x[0]))
    return sessions
""",
    visible=[{"events": [["u", 1], ["u", 3], ["u", 10]], "gap": 5},
             {"events": [["a", 2]], "gap": 5}],
    hidden=[{"events": [], "gap": 5},
            {"events": [["a", 1], ["b", 2], ["a", 3]], "gap": 1},
            {"events": [["u", 1], ["u", 2], ["u", 3]], "gap": 0}],
    gen=lambda r: [_qb_sessionize(r) for _ in range(12)],
    brute=_b_sessionize,
    checks=[({"events": [["u", 1], ["u", 3], ["u", 10]], "gap": 5},
             [["u", [1, 3]], ["u", [10, 10]]]),
            ({"events": [["a", 2]], "gap": 5}, [["a", [2, 2]]])])

add("kafka-contiguous-offset", "Kafka Contiguous Offset Commit", "easy",
    ["array", "hash-set"], "contiguousOffset", [("processed", "int[]")], "int",
    """
`processed` lists the offsets that have been handled for one partition (unsorted, and
possibly containing duplicates). Return the largest offset `m` such that **every**
offset from `0` through `m` has been processed, or `-1` if offset `0` is missing.

## Constraints
- `1 <= len(processed) <= 2*10^5`
- `0 <= processed[i]`

## Examples
Input: `processed = [0,2,1,5]`
Output: `2`
Explanation: `0,1,2` are contiguous; `3` is missing.

Input: `processed = [1,2]`
Output: `-1`
Explanation: Offset `0` was never processed.
""",
    """def contiguousOffset(processed):
    s = set(processed)
    i = 0
    while i in s:
        i += 1
    return i - 1
""",
    visible=[{"processed": [0, 2, 1, 5]}, {"processed": [1, 2]}],
    hidden=[{"processed": [0]}, {"processed": [5]},
            {"processed": [0, 1, 2, 3, 4]}, {"processed": [0, 0, 1, 1, 3]}],
    gen=lambda r: [_qb_kafka(r) for _ in range(12)],
    brute=_b_kafka,
    checks=[({"processed": [0, 2, 1, 5]}, 2), ({"processed": [1, 2]}, -1)])

add("object-store-multipart", "Object Store Multipart Completeness", "easy",
    ["hash-set", "array"], "multipartComplete",
    [("parts", "int[][]"), ("expected", "int")], "[bool,int]",
    """
A multipart upload provides `parts`, each `[partNumber, bytes]`. Return a two-element
list `[complete, totalBytes]` where `complete` is `true` only if every part number
`1..expected` is present, and `totalBytes` is the sum of all uploaded part sizes.

## Constraints
- `0 <= len(parts) <= 2*10^5`, `1 <= expected`
- part numbers are positive; sizes fit in a signed 64-bit integer

## Examples
Input: `parts = [[1,5],[3,7],[2,4]], expected = 3`
Output: `[true,16]`
Explanation: Parts 1, 2, 3 are present; total `5+7+4 = 16`.

Input: `parts = [[1,5],[3,7]], expected = 3`
Output: `[false,12]`
Explanation: Part 2 is missing; total bytes are still `12`.
""",
    """def multipartComplete(parts, expected):
    present = set()
    total = 0
    for pn, b in parts:
        present.add(pn)
        total += b
    complete = all(i in present for i in range(1, expected + 1))
    return [complete, total]
""",
    visible=[{"parts": [[1, 5], [3, 7], [2, 4]], "expected": 3},
             {"parts": [[1, 5], [3, 7]], "expected": 3}],
    hidden=[{"parts": [[1, 9]], "expected": 1}, {"parts": [], "expected": 2},
            {"parts": [[2, 4], [1, 6]], "expected": 2}],
    gen=lambda r: [_qb_multipart(r) for _ in range(12)],
    brute=_b_multipart,
    checks=[({"parts": [[1, 5], [3, 7], [2, 4]], "expected": 3}, [True, 16]),
            ({"parts": [[1, 5], [3, 7]], "expected": 3}, [False, 12])])

add("notification-dedup", "Notification Deduplication Window", "medium",
    ["hash-table", "simulation"], "deduplicate",
    [("events", "[string,int][]"), ("window", "int")], "[string,int][]",
    """
`events` is a list of `[key, time]` notifications in time order. A notification is
**delivered** only if the same `key` has not been delivered within the previous
`window` seconds (i.e. the gap to the last delivered time for that key is strictly
greater than `window`). Return the delivered notifications, in order.

## Constraints
- `0 <= len(events) <= 2*10^5`, processed in the given order
- `window >= 0`

## Examples
Input: `events = [["a",1],["a",3],["a",8]], window = 5`
Output: `[["a",1],["a",8]]`
Explanation: The event at `3` is within 5s of the delivered event at `1`, so it is
suppressed; `8` is 7s later and delivered.

Input: `events = [["x",1],["y",2]], window = 5`
Output: `[["x",1],["y",2]]`
Explanation: Different keys never suppress each other.
""",
    """def deduplicate(events, window):
    last = {}
    res = []
    for key, t in events:
        if key not in last or t - last[key] > window:
            res.append([key, t])
            last[key] = t
    return res
""",
    visible=[{"events": [["a", 1], ["a", 3], ["a", 8]], "window": 5},
             {"events": [["x", 1], ["y", 2]], "window": 5}],
    hidden=[{"events": [], "window": 3},
            {"events": [["a", 1], ["a", 2], ["a", 3]], "window": 0},
            {"events": [["a", 1], ["a", 7], ["a", 13]], "window": 5}],
    gen=lambda r: [_qb_dedup(r) for _ in range(12)],
    brute=_b_dedup,
    checks=[({"events": [["a", 1], ["a", 3], ["a", 8]], "window": 5},
             [["a", 1], ["a", 8]]),
            ({"events": [["x", 1], ["y", 2]], "window": 5},
             [["x", 1], ["y", 2]])])

add("inventory-reservation", "Inventory Reservation Acceptance", "easy",
    ["hash-table", "simulation"], "reserve",
    [("stock", "object"), ("requests", "[string,int][]")], "bool[]",
    """
`stock` maps each SKU to its available quantity. Process each request `[sku, qty]` in
order: accept it (returning `true`) only if the remaining quantity for that SKU is at
least `qty`, decrementing the remaining stock; otherwise reject it (`false`). A
missing SKU has zero stock. Return the accept/reject result for each request.

## Constraints
- `0 <= len(requests) <= 2*10^5`
- quantities are non-negative and fit in a signed 64-bit integer

## Examples
Input: `stock = {"A":5}, requests = [["A",3],["A",3],["A",2]]`
Output: `[true,false,true]`
Explanation: After accepting 3, only 2 remain, so the next request for 3 fails; the
final request for 2 fits exactly.

Input: `stock = {}, requests = [["B",1]]`
Output: `[false]`
Explanation: `B` has no stock, so the request is rejected.
""",
    """def reserve(stock, requests):
    remaining = dict(stock)
    res = []
    for sku, qty in requests:
        have = remaining.get(sku, 0)
        if have >= qty:
            remaining[sku] = have - qty
            res.append(True)
        else:
            res.append(False)
    return res
""",
    visible=[{"stock": {"A": 5}, "requests": [["A", 3], ["A", 3], ["A", 2]]},
             {"stock": {}, "requests": [["B", 1]]}],
    hidden=[{"stock": {"A": 0}, "requests": [["A", 1]]},
            {"stock": {"A": 3, "B": 2}, "requests": [["A", 2], ["B", 2], ["A", 2]]},
            {"stock": {"X": 10}, "requests": []}],
    gen=lambda r: [_qb_reserve(r) for _ in range(12)],
    brute=_b_reserve,
    checks=[({"stock": {"A": 5}, "requests": [["A", 3], ["A", 3], ["A", 2]]},
             [True, False, True]),
            ({"stock": {}, "requests": [["B", 1]]}, [False])])


# ===========================================================================
# qb3_large.txt import — Batch 8: design (operations-list)
# ===========================================================================

def _qb_timemap(r):
    keys = ["a", "b", "foo"]
    ts = {k: 0 for k in keys}
    ops = []
    for _ in range(r.randint(1, 12)):
        if r.random() < 0.5:
            k = r.choice(keys)
            ts[k] += r.randint(1, 3)
            ops.append(["set", k, r.choice(["x", "y", "bar", "z"]), ts[k]])
        else:
            ops.append(["get", r.choice(keys), r.randint(0, 20)])
    return {"operations": ops}


def _b_timemap(operations):
    store, out = {}, []
    for op in operations:
        if op[0] == "set":
            _, key, value, t = op
            store.setdefault(key, []).append((t, value))
            out.append(None)
        else:
            _, key, t = op
            best = ""
            for tt, v in store.get(key, []):
                if tt <= t:
                    best = v
            out.append(best)
    return out


def _qb_snaparray(r):
    length = r.randint(1, 4)
    ops, snaps = [], 0
    for _ in range(r.randint(1, 12)):
        c = r.random()
        if c < 0.5:
            ops.append(["set", r.randint(0, length - 1), r.randint(0, 20)])
        elif c < 0.7 or snaps == 0:
            ops.append(["snap"])
            snaps += 1
        else:
            ops.append(["get", r.randint(0, length - 1), r.randint(0, snaps - 1)])
    return {"length": length, "operations": ops}


def _b_snaparray(length, operations):
    cur = [0] * length
    snapshots, out = [], []
    for op in operations:
        if op[0] == "set":
            cur[op[1]] = op[2]
            out.append(None)
        elif op[0] == "snap":
            snapshots.append(list(cur))
            out.append(len(snapshots) - 1)
        else:
            out.append(snapshots[op[2]][op[1]])
    return out


def _qb_lifo_fifo_ops(r, peek_name):
    ops, size = [], 0
    for _ in range(r.randint(1, 14)):
        c = r.random()
        if c < 0.5 or size == 0:
            ops.append(["push", r.randint(0, 20)])
            size += 1
        elif c < 0.7:
            ops.append(["pop"])
            size -= 1
        elif c < 0.85:
            ops.append([peek_name])
        else:
            ops.append(["empty"])
    return {"operations": ops}


def _b_queue(operations):
    q, out = [], []
    for op in operations:
        if op[0] == "push":
            q.append(op[1])
            out.append(None)
        elif op[0] == "pop":
            out.append(q.pop(0))
        elif op[0] == "peek":
            out.append(q[0])
        else:
            out.append(len(q) == 0)
    return out


def _b_stack(operations):
    st, out = [], []
    for op in operations:
        if op[0] == "push":
            st.append(op[1])
            out.append(None)
        elif op[0] == "pop":
            out.append(st.pop())
        elif op[0] == "top":
            out.append(st[-1])
        else:
            out.append(len(st) == 0)
    return out


def _qb_browser(r):
    urls = ["a.com", "b.com", "c.com", "d.com"]
    ops = []
    for _ in range(r.randint(1, 12)):
        c = r.random()
        if c < 0.5:
            ops.append(["visit", r.choice(urls)])
        elif c < 0.75:
            ops.append(["back", r.randint(1, 3)])
        else:
            ops.append(["forward", r.randint(1, 3)])
    return {"homepage": "home.com", "operations": ops}


def _b_browser(homepage, operations):
    back_stack, forward_stack, cur, out = [], [], homepage, []
    for op in operations:
        if op[0] == "visit":
            back_stack.append(cur)
            cur = op[1]
            forward_stack = []
            out.append(None)
        elif op[0] == "back":
            steps = op[1]
            while steps > 0 and back_stack:
                forward_stack.append(cur)
                cur = back_stack.pop()
                steps -= 1
            out.append(cur)
        else:
            steps = op[1]
            while steps > 0 and forward_stack:
                back_stack.append(cur)
                cur = forward_stack.pop()
                steps -= 1
            out.append(cur)
    return out


def _qb_worddict(r):
    pool = ["bad", "dad", "mad", "a", "ab", "abc"]
    ops, added = [], []
    for _ in range(r.randint(1, 12)):
        if r.random() < 0.5 or not added:
            w = r.choice(pool)
            ops.append(["addWord", w])
            added.append(w)
        else:
            base = r.choice(pool)
            ops.append(["search", "".join("." if r.random() < 0.4 else ch
                                           for ch in base)])
    return {"operations": ops}


def _b_worddict(operations):
    words, out = [], []
    for op in operations:
        if op[0] == "addWord":
            words.append(op[1])
            out.append(None)
        else:
            pat = op[1]
            out.append(any(len(w) == len(pat) and
                           all(pc == "." or pc == wc for pc, wc in zip(pat, w))
                           for w in words))
    return out


def _qb_streamchecker(r):
    words = ["".join(r.choice("ab") for _ in range(r.randint(1, 3)))
             for _ in range(r.randint(1, 4))]
    queries = [r.choice("ab") for _ in range(r.randint(1, 12))]
    return {"words": words, "queries": queries}


def _b_streamchecker(words, queries):
    stream, out = "", []
    for q in queries:
        stream += q
        out.append(any(stream.endswith(w) for w in words))
    return out


def _qb_filesystem(r):
    dirs = r.sample(["/a", "/a/b", "/c", "/c/d"], r.randint(1, 4))
    ops = [["mkdir", d] for d in dirs]
    for _ in range(r.randint(0, 4)):
        t = r.choice(["/"] + dirs)
        fname = r.choice(["f", "g", "h"])
        path = ("/" + fname) if t == "/" else (t + "/" + fname)
        ops.append(["addContentToFile", path, r.choice(["hi", "yo"])])
    for t in ["/"] + dirs:
        ops.append(["ls", t])
    return {"operations": ops}


def _b_filesystem(operations):
    files, dirs, out = {}, {"/"}, []
    for op in operations:
        cmd = op[0]
        if cmd == "mkdir":
            cur = ""
            for p in [x for x in op[1].split("/") if x]:
                cur += "/" + p
                dirs.add(cur)
            out.append(None)
        elif cmd == "addContentToFile":
            path, content = op[1], op[2]
            cur = ""
            for p in [x for x in path.split("/") if x][:-1]:
                cur += "/" + p
                dirs.add(cur)
            files[path] = files.get(path, "") + content
            out.append(None)
        elif cmd == "readContentFromFile":
            out.append(files[op[1]])
        else:
            path = op[1]
            if path in files:
                out.append([path.split("/")[-1]])
                continue
            prefix = "/" if path == "/" else path + "/"
            entries = set()
            for f in files:
                if f.startswith(prefix):
                    entries.add(f[len(prefix):].split("/")[0])
            for d in dirs:
                if d != path and d.startswith(prefix):
                    rest = d[len(prefix):]
                    if rest:
                        entries.add(rest.split("/")[0])
            out.append(sorted(entries))
    return out


def _qb_calendar2(r):
    ops = []
    for _ in range(r.randint(1, 12)):
        s = r.randint(0, 20)
        ops.append(["book", s, s + r.randint(1, 10)])
    return {"operations": ops}


def _b_calendar2(operations):
    accepted, out = [], []
    for op in operations:
        _, s, e = op
        trial = accepted + [(s, e)]
        points = sorted(set(x for iv in trial for x in iv))
        ok = True
        for p in points:
            if sum(1 for a, b in trial if a <= p < b) > 2:
                ok = False
                break
        if ok:
            accepted.append((s, e))
            out.append(True)
        else:
            out.append(False)
    return out


def _qb_maxstack(r):
    ops, size = [], 0
    for _ in range(r.randint(1, 14)):
        c = r.random()
        if c < 0.45 or size == 0:
            ops.append(["push", r.randint(0, 15)])
            size += 1
        elif c < 0.6:
            ops.append(["pop"])
            size -= 1
        elif c < 0.72:
            ops.append(["top"])
        elif c < 0.85:
            ops.append(["peekMax"])
        else:
            ops.append(["popMax"])
            size -= 1
    return {"operations": ops}


def _b_maxstack(operations):
    st, out = [], []
    for op in operations:
        c = op[0]
        if c == "push":
            st.append(op[1])
            out.append(None)
        elif c == "pop":
            out.append(st.pop())
        elif c == "top":
            out.append(st[-1])
        elif c == "peekMax":
            out.append(max(st))
        else:
            m = max(st)
            del st[len(st) - 1 - st[::-1].index(m)]
            out.append(m)
    return out


def _qb_allone(r):
    keys = ["a", "b", "c", "d"]
    counts, ops = {}, []
    for _ in range(r.randint(1, 14)):
        c = r.random()
        if c < 0.45:
            k = r.choice(keys)
            ops.append(["inc", k])
            counts[k] = counts.get(k, 0) + 1
        elif c < 0.6 and counts:
            k = r.choice(list(counts))
            ops.append(["dec", k])
            counts[k] -= 1
            if counts[k] == 0:
                del counts[k]
        elif c < 0.8:
            ops.append(["getMaxKey"])
        else:
            ops.append(["getMinKey"])
    return {"operations": ops}


def _b_allone(operations):
    count, out = {}, []
    for op in operations:
        c = op[0]
        if c == "inc":
            count[op[1]] = count.get(op[1], 0) + 1
            out.append(None)
        elif c == "dec":
            k = op[1]
            count[k] = count.get(k, 0) - 1
            if count[k] <= 0:
                count.pop(k, None)
            out.append(None)
        elif c == "getMaxKey":
            if not count:
                out.append("")
            else:
                b = max(count.values())
                out.append(sorted(k for k in count if count[k] == b)[0])
        else:
            if not count:
                out.append("")
            else:
                b = min(count.values())
                out.append(sorted(k for k in count if count[k] == b)[0])
    return out


def _qb_rangesum(r):
    n = r.randint(1, 8)
    nums = [r.randint(-10, 10) for _ in range(n)]
    ops = []
    for _ in range(r.randint(1, 10)):
        if r.random() < 0.5:
            l = r.randint(0, n - 1)
            ops.append(["query", l, r.randint(l, n - 1)])
        else:
            ops.append(["update", r.randint(0, n - 1), r.randint(-10, 10)])
    return {"nums": nums, "operations": ops}


def _b_rangesum(nums, operations):
    arr, out = list(nums), []
    for op in operations:
        if op[0] == "query":
            out.append(sum(arr[op[1]:op[2] + 1]))
        else:
            arr[op[1]] = op[2]
            out.append(None)
    return out


add("time-based-kv-store", "Time Based Key Value Store", "medium",
    ["design", "hash-table", "binary-search"], "timeMap",
    [("operations", "any[][]")], "any[]",
    """
Replay `operations` against a time-keyed store and return the list of results. Each
operation is `["set", key, value, timestamp]` (returns `null`) or
`["get", key, timestamp]`, which returns the value of `key` set at the **largest**
timestamp `<= timestamp`, or `""` if none exists. `set` timestamps for a key are
strictly increasing.

## Constraints
- `1 <= len(operations) <= 2*10^5`
- keys and values are non-empty strings; `1 <= timestamp <= 10^7`

## Examples
Input: `operations = [["set","foo","bar",1],["get","foo",1],["get","foo",3]]`
Output: `[null,"bar","bar"]`
Explanation: The value set at timestamp 1 is still current at timestamp 3.

Input: `operations = [["set","a","x",5],["get","a",4]]`
Output: `[null,""]`
Explanation: There is no value at or before timestamp 4.
""",
    """def timeMap(operations):
    import bisect
    from collections import defaultdict
    times = defaultdict(list)
    vals = defaultdict(list)
    out = []
    for op in operations:
        if op[0] == "set":
            _, key, value, ts = op
            times[key].append(ts)
            vals[key].append(value)
            out.append(None)
        else:
            _, key, ts = op
            arr = times[key]
            i = bisect.bisect_right(arr, ts)
            out.append(vals[key][i - 1] if i > 0 else "")
    return out
""",
    visible=[{"operations": [["set", "foo", "bar", 1], ["get", "foo", 1],
                            ["get", "foo", 3]]},
             {"operations": [["set", "a", "x", 5], ["get", "a", 4]]}],
    hidden=[{"operations": [["get", "z", 1]]},
            {"operations": [["set", "k", "v1", 1], ["set", "k", "v2", 4],
                            ["get", "k", 3], ["get", "k", 4], ["get", "k", 5]]}],
    gen=lambda r: [_qb_timemap(r) for _ in range(12)],
    brute=_b_timemap,
    checks=[({"operations": [["set", "foo", "bar", 1], ["get", "foo", 1],
                             ["get", "foo", 3]]}, [None, "bar", "bar"]),
            ({"operations": [["set", "a", "x", 5], ["get", "a", 4]]},
             [None, ""])])

add("snapshot-array", "Snapshot Array", "medium",
    ["design", "hash-table", "binary-search"], "snapshotArray",
    [("length", "int"), ("operations", "any[][]")], "any[]",
    """
Implement an array of `length` integers (initially `0`) and replay `operations`,
returning the list of results. Operations are `["set", index, value]` (returns
`null`), `["snap"]` (takes a snapshot and returns its id, starting at `0`), and
`["get", index, snap_id]` (returns the value at `index` in that snapshot).

## Constraints
- `1 <= length <= 5*10^4`, `1 <= len(operations) <= 5*10^4`
- snap ids passed to `get` are valid

## Examples
Input: `length = 3, operations = [["set",0,5],["snap"],["set",0,6],["get",0,0]]`
Output: `[null,0,null,5]`
Explanation: Snapshot `0` recorded value `5` at index `0`.

Input: `length = 1, operations = [["snap"],["get",0,0]]`
Output: `[0,0]`
Explanation: Unset entries default to `0`.
""",
    """def snapshotArray(length, operations):
    import bisect
    records = [[(-1, 0)] for _ in range(length)]
    snap_id = 0
    out = []
    for op in operations:
        if op[0] == "set":
            _, index, val = op
            if records[index][-1][0] == snap_id:
                records[index][-1] = (snap_id, val)
            else:
                records[index].append((snap_id, val))
            out.append(None)
        elif op[0] == "snap":
            out.append(snap_id)
            snap_id += 1
        else:
            _, index, sid = op
            arr = records[index]
            i = bisect.bisect_right(arr, (sid, float('inf'))) - 1
            out.append(arr[i][1])
    return out
""",
    visible=[{"length": 3, "operations": [["set", 0, 5], ["snap"], ["set", 0, 6],
                                          ["get", 0, 0]]},
             {"length": 1, "operations": [["snap"], ["get", 0, 0]]}],
    hidden=[{"length": 2, "operations": [["snap"], ["snap"], ["get", 1, 1]]},
            {"length": 1, "operations": [["set", 0, 4], ["set", 0, 7], ["snap"],
                                         ["get", 0, 0]]}],
    gen=lambda r: [_qb_snaparray(r) for _ in range(12)],
    brute=_b_snaparray,
    checks=[({"length": 3, "operations": [["set", 0, 5], ["snap"], ["set", 0, 6],
                                          ["get", 0, 0]]}, [None, 0, None, 5]),
            ({"length": 1, "operations": [["snap"], ["get", 0, 0]]}, [0, 0])])

add("queue-via-stacks", "Queue Using Two Stacks", "easy",
    ["design", "stack", "queue"], "myQueue", [("operations", "any[][]")], "any[]",
    """
Implement a FIFO queue and replay `operations`, returning the list of results.
Operations are `["push", x]` (returns `null`), `["pop"]` (removes and returns the
front), `["peek"]` (returns the front), and `["empty"]` (returns a boolean).

## Constraints
- `1 <= len(operations) <= 1000`
- `pop`/`peek` are only called on a non-empty queue

## Examples
Input: `operations = [["push",1],["push",2],["peek"],["pop"],["empty"]]`
Output: `[null,null,1,1,false]`
Explanation: Elements leave in insertion order.

Input: `operations = [["empty"]]`
Output: `[true]`
Explanation: A fresh queue is empty.
""",
    """def myQueue(operations):
    inn, out_s, out = [], [], []
    for op in operations:
        if op[0] == "push":
            inn.append(op[1])
            out.append(None)
        elif op[0] == "pop":
            if not out_s:
                while inn:
                    out_s.append(inn.pop())
            out.append(out_s.pop())
        elif op[0] == "peek":
            if not out_s:
                while inn:
                    out_s.append(inn.pop())
            out.append(out_s[-1])
        else:
            out.append(len(inn) == 0 and len(out_s) == 0)
    return out
""",
    visible=[{"operations": [["push", 1], ["push", 2], ["peek"], ["pop"],
                            ["empty"]]},
             {"operations": [["empty"]]}],
    hidden=[{"operations": [["push", 5], ["pop"], ["empty"]]},
            {"operations": [["push", 1], ["push", 2], ["push", 3], ["pop"],
                            ["peek"], ["pop"], ["pop"], ["empty"]]}],
    gen=lambda r: [_qb_lifo_fifo_ops(r, "peek") for _ in range(12)],
    brute=_b_queue,
    checks=[({"operations": [["push", 1], ["push", 2], ["peek"], ["pop"],
                             ["empty"]]}, [None, None, 1, 1, False]),
            ({"operations": [["empty"]]}, [True])])

add("stack-via-queues", "Stack Using Queues", "easy",
    ["design", "stack", "queue"], "myStack", [("operations", "any[][]")], "any[]",
    """
Implement a LIFO stack using queues and replay `operations`, returning the list of
results. Operations are `["push", x]` (returns `null`), `["pop"]` (removes and
returns the top), `["top"]` (returns the top), and `["empty"]` (returns a boolean).

## Constraints
- `1 <= len(operations) <= 1000`
- `pop`/`top` are only called on a non-empty stack

## Examples
Input: `operations = [["push",1],["push",2],["top"],["pop"],["empty"]]`
Output: `[null,null,2,2,false]`
Explanation: The most recently pushed value leaves first.

Input: `operations = [["push",7],["pop"],["empty"]]`
Output: `[null,7,true]`
Explanation: After popping the only value, the stack is empty.
""",
    """def myStack(operations):
    from collections import deque
    q = deque()
    out = []
    for op in operations:
        if op[0] == "push":
            q.append(op[1])
            for _ in range(len(q) - 1):
                q.append(q.popleft())
            out.append(None)
        elif op[0] == "pop":
            out.append(q.popleft())
        elif op[0] == "top":
            out.append(q[0])
        else:
            out.append(len(q) == 0)
    return out
""",
    visible=[{"operations": [["push", 1], ["push", 2], ["top"], ["pop"],
                            ["empty"]]},
             {"operations": [["push", 7], ["pop"], ["empty"]]}],
    hidden=[{"operations": [["empty"]]},
            {"operations": [["push", 1], ["push", 2], ["push", 3], ["top"],
                            ["pop"], ["top"], ["empty"]]}],
    gen=lambda r: [_qb_lifo_fifo_ops(r, "top") for _ in range(12)],
    brute=_b_stack,
    checks=[({"operations": [["push", 1], ["push", 2], ["top"], ["pop"],
                             ["empty"]]}, [None, None, 2, 2, False]),
            ({"operations": [["push", 7], ["pop"], ["empty"]]},
             [None, 7, True])])

add("browser-history", "Design Browser History", "medium",
    ["design", "stack", "array"], "browserHistory",
    [("homepage", "string"), ("operations", "any[][]")], "any[]",
    """
Start on `homepage` and replay `operations`, returning the list of results.
Operations are `["visit", url]` (go to `url`, clearing forward history; returns
`null`), `["back", steps]` (move back up to `steps` pages, returning the current
url), and `["forward", steps]` (move forward up to `steps`, returning the current
url). You cannot move past either end.

## Constraints
- `1 <= len(operations) <= 5000`
- urls are non-empty strings; `1 <= steps`

## Examples
Input: `homepage = "a.com", operations = [["visit","b.com"],["visit","c.com"],["back",1],["forward",1]]`
Output: `[null,null,"b.com","c.com"]`
Explanation: Back lands on `b.com`; forward returns to `c.com`.

Input: `homepage = "x.com", operations = [["visit","y.com"],["back",2]]`
Output: `[null,"x.com"]`
Explanation: Back is clamped to the homepage.
""",
    """def browserHistory(homepage, operations):
    hist = [homepage]
    cur = 0
    out = []
    for op in operations:
        if op[0] == "visit":
            hist = hist[:cur + 1]
            hist.append(op[1])
            cur = len(hist) - 1
            out.append(None)
        elif op[0] == "back":
            cur = max(0, cur - op[1])
            out.append(hist[cur])
        else:
            cur = min(len(hist) - 1, cur + op[1])
            out.append(hist[cur])
    return out
""",
    visible=[{"homepage": "a.com", "operations": [["visit", "b.com"],
              ["visit", "c.com"], ["back", 1], ["forward", 1]]},
             {"homepage": "x.com", "operations": [["visit", "y.com"],
              ["back", 2]]}],
    hidden=[{"homepage": "h.com", "operations": [["back", 1], ["forward", 1]]},
            {"homepage": "a", "operations": [["visit", "b"], ["visit", "c"],
              ["back", 1], ["visit", "d"], ["forward", 1]]}],
    gen=lambda r: [_qb_browser(r) for _ in range(12)],
    brute=_b_browser,
    checks=[({"homepage": "a.com", "operations": [["visit", "b.com"],
              ["visit", "c.com"], ["back", 1], ["forward", 1]]},
             [None, None, "b.com", "c.com"]),
            ({"homepage": "x.com", "operations": [["visit", "y.com"],
              ["back", 2]]}, [None, "x.com"])])

add("word-dictionary", "Trie Word Dictionary With Wildcards", "medium",
    ["design", "trie", "depth-first-search"], "wordDictionary",
    [("operations", "any[][]")], "any[]",
    """
Implement a word dictionary and replay `operations`, returning the list of results.
Operations are `["addWord", word]` (returns `null`) and `["search", pattern]`, which
returns `true` if any stored word matches `pattern`, where `.` in the pattern matches
any single character.

## Constraints
- `1 <= len(operations) <= 10^4`
- words and patterns are lowercase letters and `.` (patterns only)

## Examples
Input: `operations = [["addWord","bad"],["addWord","dad"],["search",".ad"],["search","b.."]]`
Output: `[null,null,true,true]`
Explanation: `.ad` matches `bad`/`dad`; `b..` matches `bad`.

Input: `operations = [["addWord","a"],["search","."]]`
Output: `[null,true]`
Explanation: `.` matches `a`.
""",
    """def wordDictionary(operations):
    root = {}
    out = []

    def add(word):
        node = root
        for ch in word:
            node = node.setdefault(ch, {})
        node["$"] = True

    def search(word):
        def dfs(node, i):
            if i == len(word):
                return "$" in node
            ch = word[i]
            if ch == ".":
                return any(dfs(child, i + 1)
                           for k, child in node.items() if k != "$")
            return ch in node and dfs(node[ch], i + 1)

        return dfs(root, 0)

    for op in operations:
        if op[0] == "addWord":
            add(op[1])
            out.append(None)
        else:
            out.append(search(op[1]))
    return out
""",
    visible=[{"operations": [["addWord", "bad"], ["addWord", "dad"],
              ["search", ".ad"], ["search", "b.."]]},
             {"operations": [["addWord", "a"], ["search", "."]]}],
    hidden=[{"operations": [["search", "x"]]},
            {"operations": [["addWord", "ab"], ["search", "a"], ["search", ".."],
              ["search", "a.b"]]}],
    gen=lambda r: [_qb_worddict(r) for _ in range(12)],
    brute=_b_worddict,
    checks=[({"operations": [["addWord", "bad"], ["addWord", "dad"],
              ["search", ".ad"], ["search", "b.."]]},
             [None, None, True, True]),
            ({"operations": [["addWord", "a"], ["search", "."]]},
             [None, True])])

add("stream-of-characters", "Stream Of Characters Suffix Query", "hard",
    ["design", "trie", "string"], "streamChecker",
    [("words", "string[]"), ("queries", "string[]")], "bool[]",
    """
A stream receives one character per query in `queries`. After appending each
character, return `true` if some word in `words` is a **suffix** of the stream so
far. Return one boolean per query.

## Constraints
- `1 <= len(words) <= 2000`, words are lowercase letters
- `1 <= len(queries) <= 4*10^4`, each query is a single lowercase letter

## Examples
Input: `words = ["cd","f","kl"], queries = ["a","b","c","d","f"]`
Output: `[false,false,false,true,true]`
Explanation: After `d` the suffix `cd` matches; after `f`, `f` matches.

Input: `words = ["ab"], queries = ["a","b"]`
Output: `[false,true]`
Explanation: After `b` the suffix `ab` matches.
""",
    """def streamChecker(words, queries):
    root = {}
    max_len = 0
    for w in words:
        node = root
        for ch in reversed(w):
            node = node.setdefault(ch, {})
        node["$"] = True
        max_len = max(max_len, len(w))
    from collections import deque
    stream = deque()
    out = []
    for q in queries:
        stream.appendleft(q)
        while len(stream) > max_len:
            stream.pop()
        node = root
        found = False
        for ch in stream:
            if ch not in node:
                break
            node = node[ch]
            if "$" in node:
                found = True
                break
        out.append(found)
    return out
""",
    visible=[{"words": ["cd", "f", "kl"], "queries": ["a", "b", "c", "d", "f"]},
             {"words": ["ab"], "queries": ["a", "b"]}],
    hidden=[{"words": ["a"], "queries": ["b", "a", "a"]},
            {"words": ["abc", "xyz"], "queries": ["a", "b", "c", "x", "y", "z"]}],
    gen=lambda r: [_qb_streamchecker(r) for _ in range(12)],
    brute=_b_streamchecker,
    checks=[({"words": ["cd", "f", "kl"], "queries": ["a", "b", "c", "d", "f"]},
             [False, False, False, True, True]),
            ({"words": ["ab"], "queries": ["a", "b"]}, [False, True])])

add("in-memory-file-system", "In Memory File System", "hard",
    ["design", "hash-table", "string"], "fileSystem",
    [("operations", "any[][]")], "any[]",
    """
Implement an in-memory file system and replay `operations`, returning the list of
results. Operations are `["mkdir", path]` (create a directory, making parents as
needed; returns `null`), `["addContentToFile", path, content]` (create/append;
returns `null`), `["readContentFromFile", path]` (returns the file's content), and
`["ls", path]`: if `path` is a file, return `[filename]`; if a directory, return its
entry names (files and subdirectories) **sorted** alphabetically.

## Constraints
- `1 <= len(operations) <= 300`
- paths are absolute, using `/` as separator

## Examples
Input: `operations = [["mkdir","/a/b"],["addContentToFile","/a/b/f","hi"],["ls","/a/b"],["readContentFromFile","/a/b/f"]]`
Output: `[null,null,["f"],"hi"]`
Explanation: The file `f` is created under `/a/b` with content `hi`.

Input: `operations = [["ls","/"]]`
Output: `[[]]`
Explanation: The empty root lists nothing.
""",
    """def fileSystem(operations):
    root = {"dirs": {}, "files": {}}

    def get_dir(parts, create=False):
        node = root
        for p in parts:
            if p not in node["dirs"]:
                if not create:
                    return None
                node["dirs"][p] = {"dirs": {}, "files": {}}
            node = node["dirs"][p]
        return node

    out = []
    for op in operations:
        cmd = op[0]
        if cmd == "mkdir":
            get_dir([p for p in op[1].split("/") if p], create=True)
            out.append(None)
        elif cmd == "addContentToFile":
            parts = [p for p in op[1].split("/") if p]
            node = get_dir(parts[:-1], create=True)
            node["files"][parts[-1]] = node["files"].get(parts[-1], "") + op[2]
            out.append(None)
        elif cmd == "readContentFromFile":
            parts = [p for p in op[1].split("/") if p]
            out.append(get_dir(parts[:-1])["files"][parts[-1]])
        else:
            parts = [p for p in op[1].split("/") if p]
            if parts:
                parent = get_dir(parts[:-1])
                if parent and parts[-1] in parent["files"]:
                    out.append([parts[-1]])
                    continue
            node = get_dir(parts)
            out.append(sorted(list(node["dirs"].keys()) +
                              list(node["files"].keys())))
    return out
""",
    visible=[{"operations": [["mkdir", "/a/b"],
              ["addContentToFile", "/a/b/f", "hi"], ["ls", "/a/b"],
              ["readContentFromFile", "/a/b/f"]]},
             {"operations": [["ls", "/"]]}],
    hidden=[{"operations": [["mkdir", "/c"], ["ls", "/"]]},
            {"operations": [["addContentToFile", "/f", "ab"],
              ["addContentToFile", "/f", "cd"], ["readContentFromFile", "/f"],
              ["ls", "/f"]]}],
    gen=lambda r: [_qb_filesystem(r) for _ in range(12)],
    brute=_b_filesystem,
    checks=[({"operations": [["mkdir", "/a/b"],
              ["addContentToFile", "/a/b/f", "hi"], ["ls", "/a/b"],
              ["readContentFromFile", "/a/b/f"]]}, [None, None, ["f"], "hi"]),
            ({"operations": [["ls", "/"]]}, [[]])])

add("calendar-double-booking", "Calendar Double Booking Limit", "medium",
    ["design", "intervals", "sorting"], "myCalendarTwo",
    [("operations", "any[][]")], "bool[]",
    """
Implement a calendar that allows double-booking but never **triple**-booking. Replay
`operations`, each `["book", start, end]` for the half-open interval `[start, end)`.
Return `true` if the event can be added without causing any point to be covered by
three events (and add it), otherwise `false`.

## Constraints
- `1 <= len(operations) <= 1000`
- `0 <= start < end <= 10^9`

## Examples
Input: `operations = [["book",10,20],["book",50,60],["book",10,40],["book",5,15],["book",5,10]]`
Output: `[true,true,true,false,true]`
Explanation: `[5,15)` would triple-book `[10,15)`, so it is rejected.

Input: `operations = [["book",1,5],["book",2,6],["book",6,8]]`
Output: `[true,true,true]`
Explanation: No point is covered three times.
""",
    """def myCalendarTwo(operations):
    bookings = []
    overlaps = []
    out = []
    for op in operations:
        _, s, e = op
        if any(s < oe and os < e for os, oe in overlaps):
            out.append(False)
        else:
            for bs, be in bookings:
                if s < be and bs < e:
                    overlaps.append((max(s, bs), min(e, be)))
            bookings.append((s, e))
            out.append(True)
    return out
""",
    visible=[{"operations": [["book", 10, 20], ["book", 50, 60], ["book", 10, 40],
              ["book", 5, 15], ["book", 5, 10]]},
             {"operations": [["book", 1, 5], ["book", 2, 6], ["book", 6, 8]]}],
    hidden=[{"operations": [["book", 0, 10]]},
            {"operations": [["book", 0, 10], ["book", 0, 10], ["book", 0, 10]]},
            {"operations": [["book", 1, 3], ["book", 2, 4], ["book", 3, 5]]}],
    gen=lambda r: [_qb_calendar2(r) for _ in range(12)],
    brute=_b_calendar2,
    checks=[({"operations": [["book", 10, 20], ["book", 50, 60], ["book", 10, 40],
              ["book", 5, 15], ["book", 5, 10]]},
             [True, True, True, False, True]),
            ({"operations": [["book", 1, 5], ["book", 2, 6], ["book", 6, 8]]},
             [True, True, True])])

add("max-stack", "Max Stack Operations", "hard",
    ["design", "stack", "heap"], "maxStack", [("operations", "any[][]")], "any[]",
    """
Implement a stack that also supports retrieving and removing the maximum. Replay
`operations`, returning the list of results. Operations are `["push", x]` (returns
`null`), `["pop"]` (remove and return the top), `["top"]` (return the top),
`["peekMax"]` (return the maximum), and `["popMax"]` (remove and return the maximum;
if it appears multiple times, remove the one closest to the top).

## Constraints
- `1 <= len(operations) <= 10^4`
- `pop`/`top`/`peekMax`/`popMax` are only called on a non-empty stack

## Examples
Input: `operations = [["push",5],["push",1],["push",5],["top"],["popMax"],["top"]]`
Output: `[null,null,null,5,5,1]`
Explanation: `popMax` removes the most recent `5`, leaving `1` on top.

Input: `operations = [["push",2],["peekMax"]]`
Output: `[null,2]`
Explanation: The only value is the maximum.
""",
    """def maxStack(operations):
    stack = []
    out = []
    for op in operations:
        if op[0] == "push":
            stack.append(op[1])
            out.append(None)
        elif op[0] == "pop":
            out.append(stack.pop())
        elif op[0] == "top":
            out.append(stack[-1])
        elif op[0] == "peekMax":
            out.append(max(stack))
        else:
            m = max(stack)
            for i in range(len(stack) - 1, -1, -1):
                if stack[i] == m:
                    stack.pop(i)
                    break
            out.append(m)
    return out
""",
    visible=[{"operations": [["push", 5], ["push", 1], ["push", 5], ["top"],
              ["popMax"], ["top"]]},
             {"operations": [["push", 2], ["peekMax"]]}],
    hidden=[{"operations": [["push", 1], ["pop"], ["push", 3], ["peekMax"]]},
            {"operations": [["push", 5], ["push", 1], ["push", 5], ["popMax"],
              ["popMax"], ["top"]]}],
    gen=lambda r: [_qb_maxstack(r) for _ in range(12)],
    brute=_b_maxstack,
    checks=[({"operations": [["push", 5], ["push", 1], ["push", 5], ["top"],
              ["popMax"], ["top"]]}, [None, None, None, 5, 5, 1]),
            ({"operations": [["push", 2], ["peekMax"]]}, [None, 2])])

add("all-one", "All One Data Structure", "hard",
    ["design", "hash-table", "linked-list"], "allOne",
    [("operations", "any[][]")], "any[]",
    """
Implement a structure of string keys with positive counts. Replay `operations`,
returning the list of results. Operations are `["inc", key]` (increment, inserting at
1 if absent; returns `null`), `["dec", key]` (decrement, removing at 0; returns
`null`), `["getMaxKey"]`, and `["getMinKey"]`. The getters return a key with the
largest/smallest count (the **lexicographically smallest** such key to break ties),
or `""` if empty.

## Constraints
- `1 <= len(operations) <= 5*10^4`
- `dec` is only called on a key with a positive count

## Examples
Input: `operations = [["inc","a"],["inc","b"],["inc","a"],["getMaxKey"],["getMinKey"]]`
Output: `[null,null,null,"a","b"]`
Explanation: `a` has count 2, `b` has count 1.

Input: `operations = [["inc","x"],["dec","x"],["getMaxKey"]]`
Output: `[null,null,""]`
Explanation: `x` is removed, leaving the structure empty.
""",
    """def allOne(operations):
    count = {}
    out = []
    for op in operations:
        if op[0] == "inc":
            count[op[1]] = count.get(op[1], 0) + 1
            out.append(None)
        elif op[0] == "dec":
            k = op[1]
            count[k] -= 1
            if count[k] == 0:
                del count[k]
            out.append(None)
        elif op[0] == "getMaxKey":
            if not count:
                out.append("")
            else:
                mx = max(count.values())
                out.append(min(k for k, v in count.items() if v == mx))
        else:
            if not count:
                out.append("")
            else:
                mn = min(count.values())
                out.append(min(k for k, v in count.items() if v == mn))
    return out
""",
    visible=[{"operations": [["inc", "a"], ["inc", "b"], ["inc", "a"],
              ["getMaxKey"], ["getMinKey"]]},
             {"operations": [["inc", "x"], ["dec", "x"], ["getMaxKey"]]}],
    hidden=[{"operations": [["getMaxKey"], ["getMinKey"]]},
            {"operations": [["inc", "a"], ["inc", "a"], ["inc", "b"], ["dec", "a"],
              ["getMaxKey"], ["getMinKey"]]}],
    gen=lambda r: [_qb_allone(r) for _ in range(12)],
    brute=_b_allone,
    checks=[({"operations": [["inc", "a"], ["inc", "b"], ["inc", "a"],
              ["getMaxKey"], ["getMinKey"]]}, [None, None, None, "a", "b"]),
            ({"operations": [["inc", "x"], ["dec", "x"], ["getMaxKey"]]},
             [None, None, ""])])

add("range-sum-mutable", "Range Sum Query Mutable", "medium",
    ["design", "binary-indexed-tree", "segment-tree"], "rangeSum",
    [("nums", "int[]"), ("operations", "any[][]")], "any[]",
    """
Given an initial array `nums`, replay `operations` and return the list of results.
Operations are `["query", l, r]` returning the sum `nums[l] + ... + nums[r]`
(inclusive), and `["update", i, val]` setting `nums[i] = val` (returns `null`).

## Constraints
- `1 <= len(nums) <= 3*10^4`, `1 <= len(operations) <= 3*10^4`
- `0 <= l <= r < len(nums)`, `0 <= i < len(nums)`

## Examples
Input: `nums = [1,3,5], operations = [["query",0,2],["update",1,2],["query",0,2]]`
Output: `[9,null,8]`
Explanation: The initial sum is `9`; after `nums[1]=2` the sum is `1+2+5=8`.

Input: `nums = [2], operations = [["query",0,0]]`
Output: `[2]`
Explanation: The only element is `2`.
""",
    """def rangeSum(nums, operations):
    arr = list(nums)
    n = len(arr)
    bit = [0] * (n + 1)

    def add(i, delta):
        i += 1
        while i <= n:
            bit[i] += delta
            i += i & (-i)

    def prefix(i):
        s = 0
        while i > 0:
            s += bit[i]
            i -= i & (-i)
        return s

    for i, v in enumerate(arr):
        add(i, v)
    out = []
    for op in operations:
        if op[0] == "query":
            _, l, r = op
            out.append(prefix(r + 1) - prefix(l))
        else:
            _, i, val = op
            add(i, val - arr[i])
            arr[i] = val
            out.append(None)
    return out
""",
    visible=[{"nums": [1, 3, 5], "operations": [["query", 0, 2], ["update", 1, 2],
              ["query", 0, 2]]},
             {"nums": [2], "operations": [["query", 0, 0]]}],
    hidden=[{"nums": [0, 0, 0], "operations": [["update", 0, 5], ["query", 0, 2]]},
            {"nums": [-1, -2, -3], "operations": [["query", 1, 2], ["update", 2, 3],
              ["query", 0, 2]]}],
    gen=lambda r: [_qb_rangesum(r) for _ in range(12)],
    brute=_b_rangesum,
    checks=[({"nums": [1, 3, 5], "operations": [["query", 0, 2], ["update", 1, 2],
              ["query", 0, 2]]}, [9, None, 8]),
            ({"nums": [2], "operations": [["query", 0, 0]]}, [2])])


# ===========================================================================
# Build: verify each canonical, compute expected outputs, write files
# ===========================================================================

# Judge comparison mode per problem. Default is "exact" (order significant).
# Order-insensitive problems use a relaxed mode so the judge matches the
# statement's "any order" promise (see app/executor/__init__.py).
COMPARE = {
    "three-sum": "set_of_lists",
    "combination-sum": "set_of_lists",
    "group-anagrams": "set_of_lists",
    "top-k-frequent-elements": "unordered",
    "pacific-atlantic-water-flow": "unordered",
    "word-search-ii": "unordered",
    # --- imported from large_bank.txt ---
    "k-closest-points-to-origin": "unordered",
    "accounts-merge": "unordered",
    "file-duplicate-groups": "set_of_lists",
    "subsets": "set_of_lists",
    "permutations": "unordered",
    "generate-parentheses": "unordered",
    "n-queens": "unordered",
    # --- imported from qb3_large.txt ---
    "remove-invalid-parentheses": "unordered",
    "root-to-leaf-paths-target": "unordered",
    "minimum-height-trees": "unordered",
}


def _norm(x):
    return x


def build() -> int:
    rng = random.Random(20240607)
    written = 0
    for p in PROBLEMS:
        ns: dict = {}
        exec(p["solution"], ns)
        fn = ns[p["fn"]]

        # 1) known-answer checks (deepcopy: some solutions mutate their input)
        for inp, exp in p["checks"]:
            got = fn(**copy.deepcopy(inp))
            assert p["norm"](got) == p["norm"](exp), (
                f"{p['slug']}: known-answer check failed for {inp}: got {got!r}, want {exp!r}")

        # 2) assemble inputs (visible + hidden + generated)
        tagged = [("v", inp) for inp in p["visible"]]
        tagged += [("h", inp) for inp in p["hidden"]]
        if p["gen"]:
            tagged += [("h", inp) for inp in p["gen"](rng)]

        cases, vi, hi = [], 0, 0
        for tag, inp in tagged:
            expected = fn(**copy.deepcopy(inp))
            if p["brute"]:
                b = p["brute"](**copy.deepcopy(inp))
                assert p["norm"](expected) == p["norm"](b), (
                    f"{p['slug']}: brute mismatch on {inp}: canon={expected!r} brute={b!r}")
            if tag == "v":
                vi += 1
                name = f"example-{vi}"
            else:
                hi += 1
                name = f"hidden-{hi}"
            cases.append({"name": name, "input": inp, "expected": expected,
                          "weight": 1, "hidden": tag == "h"})

        data = {
            "slug": p["slug"], "title": p["title"], "difficulty": p["difficulty"],
            "topics": p["topics"], "statement_md": p["statement"],
            "function_name": p["fn"],
            "params": [{"name": n, "type": t} for n, t in p["params"]],
            "return_type": p["ret"], "starter_code": stub(p["fn"], p["params"]),
            "canonical_solution": p["solution"], "scoring_type": "weighted",
            "points": 100, "time_limit_ms": 10_000, "memory_limit_mb": 512,
            "compare": COMPARE.get(p["slug"], "exact"),
            "source": p["source"], "tests": cases, "assets": p["assets"],
        }
        content.write_problem_files(data)
        written += 1
        print(f"  [{p['difficulty']:6}] {p['slug']:38} "
              f"({sum(not c['hidden'] for c in cases)} visible / "
              f"{sum(c['hidden'] for c in cases)} hidden)")
    return written


if __name__ == "__main__":
    # Re-import as the package module so the batch modules (which do
    # `from scripts.build_bank import add`) append to THIS same PROBLEMS list,
    # not a second copy created under the name "__main__". Importing the package
    # also runs all the top-level add() calls under scripts.build_bank.
    from scripts import build_bank as _bb  # noqa: E402
    import scripts.bank_new_p  # noqa: F401,E402  (side effect: registers batch problems)

    n = _bb.build()
    print(f"\nWrote {n} problems to content/problems/. Now run: python scripts/seed.py")
