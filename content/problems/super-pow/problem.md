Calculate `a^b mod 1337`, where `a` is a positive integer and `b` is an extremely
large positive integer given as an **array of its decimal digits** (most
significant first). **Return the result.**

**Examples**
```
a = 2, b = [3]    ->  8       (2^3 = 8)
a = 2, b = [1,0]  ->  1024    (2^10 = 1024)
```

**Constraints:** `1 <= a <= 2^31 - 1`, `1 <= len(b) <= 2000`, each `b[i]` is a
digit `0..9` with no leading zero.
