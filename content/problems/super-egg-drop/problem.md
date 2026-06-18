You have `K` identical eggs and a building with `N` floors. There is a floor `F`
(`0 <= F <= N`) such that an egg breaks if dropped from any floor above `F` and
survives at or below it. Each move you drop one egg from a chosen floor; a broken
egg can't be reused. **Return the minimum number of moves** that guarantees you
determine `F`, in the worst case.

**Examples**
```
K = 1, N = 2   ->  2
K = 2, N = 6   ->  3
K = 3, N = 14  ->  4
```

**Constraints:** `1 <= K <= 100`, `1 <= N <= 10^4`.
