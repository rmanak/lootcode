Decode a string encoded with the rule `k[encoded_string]`, meaning
`encoded_string` repeated `k` times (`k` a positive integer). Encodings may nest.
The input is always valid and digits appear only as repeat counts. **Return the
decoded string.**

**Examples**
```
s = "3[a]2[bc]"      ->  "aaabcbc"
s = "3[a2[c]]"       ->  "accaccacc"
s = "2[abc]3[cd]ef"  ->  "abcabccdcdcdef"
```

**Constraints:** `1 <= len(s) <= 30`, decoded length fits comfortably in memory.
