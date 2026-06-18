A binary tree with `n` nodes (values `1..n`, all distinct) is given as a LeetCode
**level-order array**. Player 1 colours node `x` red, then Player 2 colours any other
node blue. Players then alternate, each turn colouring an uncoloured node adjacent to
one of their own coloured nodes. Whoever colours more nodes wins. Return `True` if
Player 2 can choose a node guaranteeing a win.

**Example**
```
root = [1,2,3,4,5,6,7,8,9,10,11], n = 11, x = 3   ->  true
```

**Constraints:** `1 <= n <= 100`, node values are a permutation of `1..n`.
