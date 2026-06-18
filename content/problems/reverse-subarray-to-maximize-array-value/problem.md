The value of an array is `sum(|nums[i] - nums[i+1]|)`. You may reverse **one**
subarray at most once. **Return the maximum achievable array value.**

**Examples**
```
nums = [2,3,1,5,4]        ->  10
nums = [2,4,9,24,2,1,10]  ->  68
```

**Constraints:** `1 <= len(nums) <= 3*10^4`, `-10^5 <= nums[i] <= 10^5`.
