Bulbs `1..n` start off. At moment `k` (for `k = 0..n-1`) you switch on bulb
`light[k]`. A lit bulb turns **blue** only once every bulb to its left is also on.
**Return the number of moments at which all currently-on bulbs are blue**, i.e. the
on-bulbs are exactly `1..k+1`.

**Examples**
```
light = [2,1,3,5,4]  ->  3
light = [3,2,4,1,5]  ->  2
light = [4,1,2,3]    ->  1
```

**Constraints:** `1 <= n <= 5*10^4`, `light` is a permutation of `1..n`.
