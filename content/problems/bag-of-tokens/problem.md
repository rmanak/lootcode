You start with power `P` and score `0`. Each token (used at most once) may be played
**face up** (need at least `tokens[i]` power; lose `tokens[i]` power, gain `1` point)
or **face down** (need at least `1` point; gain `tokens[i]` power, lose `1` point).
**Return the largest score reachable.**

**Examples**
```
tokens = [100], P = 50              ->  0
tokens = [100,200], P = 150         ->  1
tokens = [100,200,300,400], P = 200 ->  2
```

**Constraints:** `0 <= len(tokens) <= 1000`, `0 <= tokens[i] < 10^4`,
`0 <= P < 10^4`.
