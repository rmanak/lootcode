Given distinct integers `arr` (each `> 1`), build binary trees where every non-leaf
node's value equals the **product of its two children** (values may be reused).
**Return the number of such trees**, modulo `10^9 + 7`.

**Examples**
```
arr = [2,4]        ->  3    ([2], [4], [4 -> 2,2])
arr = [2,4,5,10]   ->  7
```

**Constraints:** `1 <= len(arr) <= 1000`, `2 <= arr[i] <= 10^9`, all distinct.
