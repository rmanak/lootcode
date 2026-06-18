You start with a sequence of `len(target)` `'?'` characters and a `stamp` of lowercase
letters. On each turn you may place the stamp over a fully-contained window of the
sequence, overwriting those positions with the stamp's letters. Return `True` if the
sequence can be turned into `target` using any number of stamping turns, otherwise
`False`.

**Examples**
```
stamp = "abc",  target = "ababc"    ->  true
stamp = "abca", target = "aabcaca"  ->  true
stamp = "ab",   target = "aba"      ->  false
```

**Constraints:** `1 <= len(stamp) <= len(target) <= 1000`, lowercase letters only.
