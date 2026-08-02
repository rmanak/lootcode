> **Note:** `getRandom` is graded only when **exactly one element** remains in the
> set, so the expected result is deterministic. Any correct implementation passes.

Implement the `RandomizedSet` class:

- `RandomizedSet()` initializes the `RandomizedSet` object.
- `bool insert(int val)` inserts an item `val` into the set if not present.
  Returns `true` if the item was not present, `false` otherwise.
- `bool remove(int val)` removes an item `val` from the set if present. Returns
  `true` if the item was present, `false` otherwise.
- `int getRandom()` returns a random element from the current set of elements (it
  is guaranteed that at least one element exists when this method is called). Each
  element must have the **same probability** of being returned.

You must implement the functions of the class such that each function works in
**average** `O(1)` time complexity.

**Example 1:**

```
Input
["RandomizedSet", "insert", "getRandom", "insert", "remove", "getRandom", "remove"]
[[], [1], [], [2], [1], [], [2]]

Output
[null, true, 1, true, true, 2, true]
```

Explanation: `insert(1)` returns `true`; with only `1` in the set `getRandom`
returns `1`; `remove(1)` returns `true`, leaving only `2`.

**Example 2:**

```
Input
["RandomizedSet", "remove", "insert", "insert", "getRandom"]
[[], [5], [5], [5], []]

Output
[null, false, true, false, 5]
```

**Constraints:**

- `-2³¹ <= val <= 2³¹ - 1`
- At most `2 * 10⁵` calls will be made to `insert`, `remove`, and `getRandom`.
- There will be **at least one** element in the data structure when `getRandom` is
  called.
