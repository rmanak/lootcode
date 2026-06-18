`word1` is a *predecessor* of `word2` if inserting exactly one letter into `word1`
(anywhere) makes it equal to `word2`. A *chain* is a sequence where each word is a
predecessor of the next. **Return the length of the longest possible word chain.**

**Examples**
```
words = ["a","b","ba","bca","bda","bdca"]      ->  4
words = ["xbc","pcxbcf","xb","cxbc","pcxbc"]    ->  5
words = ["abcd","dbqca"]                        ->  1
```

**Constraints:** `1 <= len(words) <= 1000`, lowercase letters.
