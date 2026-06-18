You create `n` folders in order; at minute `i` you request the name `names[i]`. If a
requested name is already taken, the system appends the smallest suffix `(k)` with
`k` a positive integer making the name unique. Return the list of names actually
assigned, in order.

Note the suffix is added even to a name that already ends in `(k)`.

**Examples**
```
names = ["pes","fifa","gta","pes(2019)"]
  ->  ["pes","fifa","gta","pes(2019)"]
names = ["gta","gta(1)","gta","avalon"]
  ->  ["gta","gta(1)","gta(2)","avalon"]
names = ["kaido","kaido(1)","kaido","kaido(1)"]
  ->  ["kaido","kaido(1)","kaido(2)","kaido(1)(1)"]
```

**Constraints:** `1 <= len(names) <= 5*10^4`, names use lowercase letters, digits and
round brackets, `1 <= len(names[i]) <= 20`.
