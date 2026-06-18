A binary tree obeys: `root.val == 0`, a left child's value is `2*x + 1`, and a right
child's value is `2*x + 2`, where `x` is the parent's value. The tree is
*contaminated* — every stored value was replaced by `-1` — and is given as a LeetCode
**level-order array** of `-1`/`None` (so it conveys only the tree's **shape**).

First recover the original values from the shape, then for each value in `queries`
report whether that value exists in the recovered tree. Return one bool per query.

**Examples**
```
root = [-1,null,-1],     queries = [1,2]     ->  [false,true]
root = [-1,-1,-1,-1,-1],  queries = [1,3,5]   ->  [true,true,false]
```

**Constraints:** tree height `<= 20`, `1 <= number of nodes <= 10^4`,
`0 <= query value <= 10^6`.
