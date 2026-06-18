Given `words`, a multiset of available `letters`, and a `score` for each of `a..z`,
**return the maximum total score of a subset of `words`** that can be spelled using the
letters (each letter used at most once; a word used at most once).

**Examples**
```
words=["dog","cat","dad","good"], letters=["a","a","c","d","d","d","g","o","o"], ... -> 23
words=["leetcode"], letters=["l","e","t","c","o","d"], ...                          -> 0
```

**Constraints:** `1 <= len(words) <= 14`, `1 <= len(letters) <= 100`, `score` has 26
entries `0..10`.
