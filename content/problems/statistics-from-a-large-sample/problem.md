We sampled integers in the range `0..255`; `count[k]` is how many times the value `k`
appeared (`count` has length 256). Return `[minimum, maximum, mean, median, mode]` as
floating-point numbers, each **rounded to 5 decimal places**. The mode is guaranteed
to be unique. (For an even-sized sample, the median is the average of the two middle
values.)

**Examples**
```
count with {1:1, 2:3, 3:4}        ->  [1.0, 3.0, 2.375, 2.5, 3.0]
count with {1:4, 2:3, 3:2, 4:2}   ->  [1.0, 4.0, 2.18182, 2.0, 1.0]
```

**Constraints:** `count.length == 256`, `1 <= sum(count) <= 10^9`, unique mode.
