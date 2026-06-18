You may pick a subset of `nums`, multiply each chosen value by any integer, and sum
them. The array is *good* if some such combination equals `1`. **Return `true` if
the array is good**, else `false`. (True iff `gcd` of all elements is `1`.)

**Examples**
```
nums = [12,5,7,23]  ->  true
nums = [29,6,10]    ->  true
nums = [3,6]        ->  false
```

**Constraints:** `1 <= len(nums) <= 10^5`, `1 <= nums[i] <= 10^9`.
