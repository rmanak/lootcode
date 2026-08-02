Design an autocomplete index over historically typed sentences. Each sentence has
a cumulative frequency, and a query returns the most popular sentences sharing a
prefix.

Implement the `AutocompleteSystem` class:

- `AutocompleteSystem(int k)` initializes an empty index that returns at most `k`
  suggestions per query.
- `void add(String sentence, int count)` adds `count` to the historical frequency
  of `sentence` (inserting it if it has not been seen).
- `String[] query(String prefix)` returns up to `k` sentences that start with
  `prefix`, ranked by **frequency descending**, then **lexicographically
  ascending** to break ties. Returns an empty list if nothing matches.

**Example 1:**

```
Input
["AutocompleteSystem", "add", "add", "add", "query", "query"]
[[2], ["ice cream", 3], ["icing", 2], ["igloo", 5], ["i"], ["ic"]]

Output
[null, null, null, null, ["igloo", "ice cream"], ["ice cream", "icing"]]
```

Explanation: `"igloo"` (5) outranks `"ice cream"` (3), and only two suggestions are
returned because `k = 2`. Narrowing the prefix to `"ic"` drops `"igloo"`.

**Example 2:**

```
Input
["AutocompleteSystem", "add", "add", "query"]
[[2], ["cat", 1], ["car", 1], ["ca"]]

Output
[null, null, null, ["car", "cat"]]
```

Explanation: equal frequencies, so lexicographic order decides.

**Constraints:**

- `1 <= k <= 10`
- Sentences are non-empty lowercase strings, spaces allowed; `1 <= count <= 10⁶`.
- At most `10⁴` calls will be made to `add` and `query`.
