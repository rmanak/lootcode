Walking left to right past a row of trees, `tree[i]` is the fruit type of tree `i`.
You carry two baskets and each basket holds only one type of fruit. Starting at any
tree, you pick one fruit from each tree moving right and stop when you'd need a
third type. **Return the maximum number of fruits** you can collect — i.e. the
length of the longest contiguous subarray containing at most two distinct values.

**Examples**
```
tree = [1,2,1]                       ->  3
tree = [0,1,2,2]                     ->  3   ([1,2,2])
tree = [1,2,3,2,2]                   ->  4   ([2,3,2,2])
tree = [3,3,3,1,2,1,1,2,3,3,4]       ->  5   ([1,2,1,1,2])
```

**Constraints:** `1 <= len(tree) <= 4*10^4`, `0 <= tree[i] < len(tree)`.
