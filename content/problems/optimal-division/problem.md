The integers `nums` are divided left to right (`a/b/c/...`). By inserting
parentheses you can change the order. **Return the expression (with no redundant
parentheses) that maximizes the result.** The optimal form is unique: with three or
more numbers it is `nums[0]/(nums[1]/nums[2]/.../nums[k])`.

**Example**
```
nums = [1000,100,10,2]  ->  "1000/(100/10/2)"
```

**Constraints:** `1 <= len(nums) <= 10`, `2 <= nums[i] <= 1000`.
