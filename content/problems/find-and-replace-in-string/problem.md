Apply replacement operations to `S`, all relative to the **original** string and
**simultaneously**. Operation `(indexes[i], sources[i], targets[i])` replaces
`sources[i]` with `targets[i]` only if `sources[i]` occurs at index `indexes[i]` in
the original `S`. Operations do not overlap. **Return the resulting string.**

**Examples**
```
S = "abcd", indexes = [0,2], sources = ["a","cd"], targets = ["eee","ffff"]  ->  "eeebffff"
S = "abcd", indexes = [0,2], sources = ["ab","ec"], targets = ["eee","ffff"] ->  "eeecd"
```

**Constraints:** `0 <= len(indexes) <= 100`, indices in range, lowercase letters.
