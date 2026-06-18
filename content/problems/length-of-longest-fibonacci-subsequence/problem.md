Given a strictly increasing array `arr`, **return the length of the longest
subsequence that is Fibonacci-like** (`X[i] + X[i+1] = X[i+2]`, length `>= 3`), or
`0` if none exists.

**Examples**
```
arr = [1,2,3,4,5,6,7,8]      ->  5    ([1,2,3,5,8])
arr = [1,3,7,11,12,14,18]    ->  3
```

**Constraints:** `3 <= len(arr) <= 1000`, strictly increasing positive integers.
