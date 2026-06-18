Numbers `nums` are written on a chalkboard. Alice and Bob alternately erase exactly
one number, Alice first. If erasing a number makes the XOR of all remaining numbers
equal to `0`, the player who erased it **loses**. If the XOR of all numbers is already
`0` at the start of a player's turn, that player **wins**. Return `true` if and only
if Alice wins with optimal play.

**Example**
```
nums = [1,1,2]   ->  false
```

**Constraints:** `1 <= len(nums) <= 1000`, `0 <= nums[i] < 2^16`.
