Person `A` sends a friend request to person `B` (`A != B`) **unless** any of these
hold: `age[B] <= 0.5*age[A] + 7`, or `age[B] > age[A]`, or
`age[B] > 100 and age[A] < 100`. **Return the total number of friend requests
made.**

**Examples**
```
ages = [16,16]              ->  2
ages = [16,17,18]           ->  2
ages = [20,30,100,110,120]  ->  3
```

**Constraints:** `1 <= len(ages) <= 2*10^4`, `1 <= ages[i] <= 120`.
