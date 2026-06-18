A password is *strong* if it (1) has `6..20` characters, (2) contains at least one
lowercase, one uppercase and one digit, and (3) has no run of three identical
characters in a row. One change = inserting, deleting, or replacing a single
character. **Return the minimum number of changes** to make `s` strong (`0` if it
already is).

**Examples**
```
s = "a"          ->  5
s = "aA1"        ->  3
s = "1337C0d3"   ->  0
s = "aaa123"     ->  1
```

**Constraints:** `0 <= len(s) <= 100`, printable ASCII letters/digits.
