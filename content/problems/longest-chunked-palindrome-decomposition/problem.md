Split `text` into the largest possible number of non-empty parts
`a_1, a_2, ..., a_k` (concatenating back to `text`) such that `a_i = a_{k+1-i}` for
all `i`. Return the maximum `k`.

**Examples**
```
text = "ghiabcdefhelloadamhelloabcdefghi"   ->  7
text = "merchant"                            ->  1
text = "antaprezatepzapreanta"               ->  11
text = "aaa"                                  ->  3
```

**Constraints:** `1 <= len(text) <= 1000`, lowercase letters.
