Each rabbit in a forest has a colour. Some rabbits told you how many **other**
rabbits share their colour; those replies are collected in `answers`. Return the
minimum number of rabbits that could be in the forest consistent with the replies.

Two rabbits giving the same answer `x` may share a colour, but each colour group
that answers `x` holds exactly `x + 1` rabbits.

**Examples**
```
answers = [1,1,2]      ->  5
answers = [10,10,10]   ->  11
answers = []           ->  0
```

**Constraints:** `0 <= len(answers) <= 1000`, `0 <= answers[i] <= 999`.
