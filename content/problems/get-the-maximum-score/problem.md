`nums1` and `nums2` are strictly increasing arrays of distinct integers. A valid
path starts at index 0 of either array, moves left to right, and may switch to the
other array **only at a value common to both** (each common value is visited once).
The score is the sum of unique values along the path. **Return the maximum score**,
modulo `10^9 + 7`.

**Examples**
```
nums1 = [2,4,5,8,10], nums2 = [4,6,8,9]  ->  30   (path [2,4,6,8,10])
nums1 = [1,3,5,7,9], nums2 = [3,5,100]    ->  109  (path [1,3,5,100])
nums1 = [1,2,3,4,5], nums2 = [6,7,8,9,10] ->  40
```

**Constraints:** `1 <= len(nums1), len(nums2) <= 10^5`, `1 <= nums[i] <= 10^7`,
both strictly increasing.
