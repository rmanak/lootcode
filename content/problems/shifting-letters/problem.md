`S` is a string of lowercase letters and `shifts` has the same length. To *shift* a
letter means to advance it in the alphabet, wrapping `'z'` to `'a'`. For each `i`,
`shifts[i]` shifts the **first `i + 1` letters** of `S` by `shifts[i]` positions.
Return the final string after all shifts are applied.

**Example**
```
S = "abc", shifts = [3,5,9]   ->  "rpl"
```

**Constraints:** `1 <= len(S) == len(shifts) <= 2*10^4`, `0 <= shifts[i] <= 10^9`.
