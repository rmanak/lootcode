Count triplets of two kinds:
- Type 1: `(i, j, k)` with `nums1[i]^2 == nums2[j] * nums2[k]`, `j < k`.
- Type 2: `(i, j, k)` with `nums2[i]^2 == nums1[j] * nums1[k]`, `j < k`.

**Return the total number of such triplets.**

**Examples**
```
nums1 = [7,4], nums2 = [5,2,8,9]      ->  1
nums1 = [1,1], nums2 = [1,1,1]        ->  9
nums1 = [7,7,8,3], nums2 = [1,2,9,7]  ->  2
```

**Constraints:** `1 <= len(nums1), len(nums2) <= 1000`, `1 <= nums[i] <= 10^5`.
