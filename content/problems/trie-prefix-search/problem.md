A **trie** (prefix tree) is a tree data structure used to efficiently store and
retrieve keys in a set of strings, with applications such as autocomplete and
spell checking.

Implement the `Trie` class:

- `Trie()` initializes the trie object.
- `void insert(String word)` inserts the string `word` into the trie.
- `boolean search(String word)` returns `true` if `word` is in the trie (i.e. was
  inserted before), and `false` otherwise.
- `boolean startsWith(String prefix)` returns `true` if there is a previously
  inserted string that has the prefix `prefix`, and `false` otherwise.

**Example 1:**

```
Input
["Trie", "insert", "search", "search", "startsWith", "insert", "search"]
[[], ["apple"], ["apple"], ["app"], ["app"], ["app"], ["app"]]

Output
[null, null, true, false, true, null, true]
```

Explanation: `search("app")` is `false` until `"app"` itself is inserted, even
though `"apple"` starts with it; `startsWith("app")` is `true` either way.

**Example 2:**

```
Input
["Trie", "search"]
[[], ["a"]]

Output
[null, false]
```

**Constraints:**

- `1 <= word.length, prefix.length <= 2000`
- `word` and `prefix` consist only of lowercase English letters.
- At most `10⁴` calls in total will be made to `insert`, `search`, and `startsWith`.
