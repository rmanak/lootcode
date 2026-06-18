`croakOfFrogs` is several `"croak"` strings interleaved (frogs croak concurrently).
Each frog prints `c, r, o, a, k` in order. **Return the minimum number of frogs**
needed to produce the string, or `-1` if it is not a valid interleaving of complete
`"croak"`s.

**Examples**
```
croakOfFrogs = "croakcroak"  ->  1
croakOfFrogs = "crcoakroak"  ->  2
croakOfFrogs = "croakcrook"  ->  -1
croakOfFrogs = "croakcroa"   ->  -1
```

**Constraints:** `1 <= len(croakOfFrogs) <= 10^5`, characters from `croak`.
