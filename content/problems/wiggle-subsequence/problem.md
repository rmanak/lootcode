A *wiggle sequence* is one whose successive differences strictly alternate between
positive and negative (a sequence of fewer than two elements is trivially a wiggle
sequence). **Return the length of the longest subsequence of `nums` that is a wiggle
sequence** (a subsequence deletes zero or more elements, keeping the order).

**Examples**
```
nums = [1,7,4,9,2,5]                  ->  6
nums = [1,17,5,10,13,15,10,5,16,8]    ->  7
nums = [1,2,3,4,5,6,7,8,9]            ->  2
```

**Constraints:** `1 <= len(nums) <= 1000`, `0 <= nums[i] <= 1000`.
