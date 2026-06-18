There are `n` boxes. Box `i` is open if `status[i] == 1` and holds `candies[i]`
candies, the keys in `keys[i]` (each opening one box), and the boxes listed in
`containedBoxes[i]`. You start holding the boxes in `initialBoxes`. You may take the
candies from any box you hold that is open (or that you have a key for), and use its
keys and contained boxes. **Return the maximum number of candies you can collect.**

**Examples**
```
status=[1,0,1,0], candies=[7,5,4,100], keys=[[],[],[1],[]],
containedBoxes=[[1,2],[3],[],[]], initialBoxes=[0]   ->  16
status=[1,0,0,0,0,0], candies=[1,1,1,1,1,1], keys=[[1,2,3,4,5],[],[],[],[],[]],
containedBoxes=[[1,2,3,4,5],[],[],[],[],[]], initialBoxes=[0]   ->  6
```

**Constraints:** `1 <= n <= 1000`, `status[i]` in `{0,1}`, `1 <= candies[i] <= 1000`,
all key / box indices valid.
