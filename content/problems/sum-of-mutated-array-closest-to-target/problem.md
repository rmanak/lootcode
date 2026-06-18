Choose an integer `value`; replace every element of `arr` greater than `value` with
`value`. **Return the `value` that makes the array's sum as close as possible to
`target`** (smallest such `value` on a tie). The answer need not appear in `arr`.

**Examples**
```
arr = [4,9,3], target = 10  ->  3    (becomes [3,3,3], sum 9)
arr = [2,3,5], target = 10  ->  5
```

**Constraints:** `1 <= len(arr) <= 10^4`, `1 <= arr[i], target <= 10^5`.
