Start with an all-zero array the same length as `target`. One operation chooses any
contiguous subarray and increments each of its values by `1`. Return the minimum
number of operations to turn the array into `target`.

**Examples**
```
target = [1,2,3,2,1]   ->  3
target = [3,1,1,2]     ->  4
target = [3,1,5,4,2]   ->  7
```

**Constraints:** `1 <= len(target) <= 10^5`, `1 <= target[i] <= 10^5`.
