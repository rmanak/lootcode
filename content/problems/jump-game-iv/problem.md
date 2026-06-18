Starting at index `0`, in one step you may move to `i+1`, `i-1`, or any index `j`
with `arr[j] == arr[i]`. **Return the minimum number of steps to reach the last
index.**

**Examples**
```
arr = [100,-23,-23,404,100,23,23,23,3,404]  ->  3
arr = [7]                                    ->  0
arr = [7,6,9,6,9,6,9,7]                      ->  1
```

**Constraints:** `1 <= len(arr) <= 5*10^4`, `-10^8 <= arr[i] <= 10^8`.
