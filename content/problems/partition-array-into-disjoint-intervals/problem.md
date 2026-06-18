Partition `nums` into a contiguous `left` and `right` (both non-empty) so that every
element of `left` is `<=` every element of `right`, with `left` as short as
possible. **Return the length of `left`.** A valid partition is guaranteed to exist.

**Examples**
```
nums = [5,0,3,8,6]      ->  3   (left = [5,0,3], right = [8,6])
nums = [1,1,1,0,6,12]   ->  4   (left = [1,1,1,0])
```

**Constraints:** `2 <= len(nums) <= 3*10^4`, `0 <= nums[i] <= 10^6`, a valid
partition exists.
