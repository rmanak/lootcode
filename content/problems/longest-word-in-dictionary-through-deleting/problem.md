Given a string `s` and a list of words `d`, **return the longest word in `d` that
is a subsequence of `s`**. If several share the longest length, return the
lexicographically smallest. If none qualifies, return `""`.

**Examples**
```
s = "abpcplea", d = ["ale","apple","monkey","plea"]  ->  "apple"
s = "abpcplea", d = ["a","b","c"]                     ->  "a"
```

**Constraints:** `1 <= len(s) <= 1000`, `1 <= len(d) <= 1000`, lowercase letters.
