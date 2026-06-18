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
