You are given `people`, a list of pairs `[h, k]`: `h` is a person's height and `k`
is the number of people in front of this person who have a height **greater than or
equal to** `h`. Reconstruct and return the queue (the unique arrangement of `people`
that satisfies every pair's `k`).

**Example**
```
people = [[7,0],[4,4],[7,1],[5,0],[6,1],[5,2]]
    ->  [[5,0],[7,0],[5,2],[6,1],[4,4],[7,1]]
```

**Constraints:** `1 <= len(people) <= 2000`, the input is always reconstructable.
