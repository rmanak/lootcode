Given two sequences `pushed` and `popped`, each a permutation of the same distinct
values, **return `true` if they could result from a sequence of push and pop
operations** on an initially empty stack, otherwise `false`.

**Examples**
```
pushed = [1,2,3,4,5], popped = [4,5,3,2,1]  ->  true
pushed = [1,2,3,4,5], popped = [4,3,5,1,2]  ->  false
```

**Constraints:** `0 <= len(pushed) == len(popped) <= 1000`, values are distinct,
`pushed` is a permutation of `popped`.
