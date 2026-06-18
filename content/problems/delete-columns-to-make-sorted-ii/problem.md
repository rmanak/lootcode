Given `strs`, a list of equal-length lowercase strings, you may delete a chosen set
of column indices from every string. **Return the minimum number of columns** you
must delete so the remaining rows are in non-decreasing lexicographic order
(`strs[0] <= strs[1] <= ...`).

**Examples**
```
strs = ["ca","bb","ac"]   ->  1
strs = ["xc","yb","za"]   ->  0
strs = ["zyx","wvu","tsr"] ->  3
```

**Constraints:** `1 <= len(strs) <= 100`, `1 <= len(strs[i]) <= 100`, all equal
length.
