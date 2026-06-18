A subarray is *turbulent* if the comparison sign strictly flips between each adjacent
pair (up, down, up, ... or down, up, down, ...). **Return the length of the longest
turbulent subarray of `A`.**

**Examples**
```
A = [9,4,2,10,7,8,8,1,9]  ->  5
A = [4,8,12,16]           ->  2
A = [100]                 ->  1
```

**Constraints:** `1 <= len(A) <= 4*10^4`, `0 <= A[i] <= 10^9`.
