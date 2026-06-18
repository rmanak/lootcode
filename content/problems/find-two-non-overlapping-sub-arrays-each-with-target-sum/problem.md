Find two **non-overlapping** subarrays of `arr`, each summing to `target`, with the
**minimum total length**. **Return that minimum total length**, or `-1` if it is
impossible.

**Examples**
```
arr = [3,2,2,4,3], target = 3        ->  2
arr = [7,3,4,7], target = 7          ->  2
arr = [4,3,2,6,2,3,4], target = 6    ->  -1
arr = [3,1,1,1,5,1,2,1], target = 3  ->  3
```

**Constraints:** `1 <= len(arr) <= 10^5`, `1 <= arr[i] <= 1000`,
`1 <= target <= 10^8`.
