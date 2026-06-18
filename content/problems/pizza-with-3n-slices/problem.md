A circular pizza has `3n` slices with sizes `slices` (clockwise). You repeatedly take
a slice, then your friends take the slices immediately counter-clockwise and clockwise
of your pick. **Return the maximum total size of the slices you can take** (you take
exactly `n` slices, no two adjacent on the circle).

**Examples**
```
slices = [1,2,3,4,5,6]            ->  10
slices = [8,9,8,6,1,1]            ->  16
slices = [4,1,2,5,8,3,1,9,7]      ->  21
```

**Constraints:** `len(slices) % 3 == 0`, `1 <= len(slices) <= 500`,
`1 <= slices[i] <= 1000`.
