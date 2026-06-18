For two equal-length arrays, **return the maximum over all `i, j` of**
`|arr1[i] - arr1[j]| + |arr2[i] - arr2[j]| + |i - j|`.

**Examples**
```
arr1 = [1,2,3,4], arr2 = [-1,4,5,6]            ->  13
arr1 = [1,-2,-5,0,10], arr2 = [0,-2,-1,-7,-4]  ->  20
```

**Constraints:** `2 <= len(arr1) == len(arr2) <= 4*10^4`,
`-10^6 <= arr1[i], arr2[i] <= 10^6`.
