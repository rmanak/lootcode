A strictly ascending array with **no duplicates** is rotated at an unknown pivot
(e.g. `[0,1,2,4,5,6,7]` -> `[4,5,6,7,0,1,2]`). Given the rotated `nums` and a
`target`, **return the index of `target`**, or `-1` if absent. Aim for `O(log n)`.

**Examples**
```
nums = [4,5,6,7,0,1,2], target = 0  ->  4
nums = [4,5,6,7,0,1,2], target = 3  ->  -1
```

**Constraints:** `1 <= len(nums) <= 5000`, values distinct, `-10^4 <= nums[i] <= 10^4`.
