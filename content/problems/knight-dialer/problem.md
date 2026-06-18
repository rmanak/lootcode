A chess knight stands on a phone keypad and makes `n - 1` knight moves, spelling an
`n`-digit number. The keypad and the moves from each digit are:
```
1 2 3
4 5 6
7 8 9
  0
0 -> 4,6   1 -> 6,8   2 -> 7,9   3 -> 4,8   4 -> 0,3,9
5 -> (none)  6 -> 0,1,7  7 -> 2,6   8 -> 1,3   9 -> 2,4
```
The knight may start on any digit. **Return how many distinct numbers of length `n`
can be dialed, modulo `10^9 + 7`.**

**Examples**
```
n = 1     ->  10
n = 2     ->  20
n = 3     ->  46
n = 3131  ->  136006598
```

**Constraints:** `1 <= n <= 5000`.
