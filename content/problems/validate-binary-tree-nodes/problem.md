There are `n` nodes `0..n-1`; node `i` has children `leftChild[i]` and `rightChild[i]`
(`-1` for none). **Return `true` if and only if the nodes form exactly one valid binary
tree** (one root, every other node has exactly one parent, fully connected, no cycle).

**Examples**
```
n=4, leftChild=[1,-1,3,-1], rightChild=[2,-1,-1,-1]  ->  true
n=2, leftChild=[1,0], rightChild=[-1,-1]             ->  false
```

**Constraints:** `1 <= n <= 10^4`, `-1 <= leftChild[i], rightChild[i] <= n-1`.
