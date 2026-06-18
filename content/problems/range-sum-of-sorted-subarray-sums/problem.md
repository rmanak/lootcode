Compute the sums of all `n*(n+1)/2` non-empty contiguous subarrays of `nums` and sort
them non-decreasingly. **Return the sum of the entries from index `left` to `right`
(1-indexed, inclusive)**, modulo `10^9 + 7`.

**Examples**
```
nums=[1,2,3,4], n=4, left=1, right=5   ->  13
nums=[1,2,3,4], n=4, left=1, right=10  ->  50
```

**Constraints:** `1 <= len(nums) == n <= 10^3`, `1 <= nums[i] <= 100`,
`1 <= left <= right <= n*(n+1)/2`.
