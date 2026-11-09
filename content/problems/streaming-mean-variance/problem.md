Computing the mean and variance of a billion-row dataset means one pass,
constant memory per worker, and partial results from many workers combined at
the end, all without losing accuracy. Build the accumulator.

- `StreamStats()` creates $100$ empty shards, numbered $0$ to $99$.
- `add(shard, x)` adds the value `x` to a shard.
- `merge(dst, src)` moves everything in shard `src` into shard `dst`; `src`
  becomes empty.
- `stats(shard)` returns `[count, mean, populationVariance, sampleVariance]`
  over the values currently in the shard.

With $n$ values and mean $\mu$, the population variance divides the sum of
squared deviations $\sum_i (x_i - \mu)^2$ by $n$ (it is the maximum-likelihood
estimate for Gaussian data), and the sample variance divides it by $n - 1$
(the unbiased estimate). An empty shard reports `[0, 0, 0, 0]`, and a shard
with one value has sample variance $0$.

**One pass, constant memory.** Keep only three numbers per shard: the count
$n$, the mean $\mu$, and $M_2 = \sum_i (x_i - \mu)^2$. **Welford's** update for a
new value $x$:

$$
\begin{aligned}
n &\leftarrow n + 1 \\
\delta &= x - \mu \\
\mu &\leftarrow \mu + \delta / n \\
M_2 &\leftarrow M_2 + \delta\,(x - \mu)
\end{aligned}
$$

where the last step uses the **updated** mean. Merging two shards $(n_a, \mu_a, M_a)$
and $(n_b, \mu_b, M_b)$ (**Chan et al.**): with $n = n_a + n_b$ and
$\delta = \mu_b - \mu_a$,

$$
\begin{aligned}
\mu &= \mu_a + \delta \, \frac{n_b}{n} \\
M_2 &= M_a + M_b + \delta^2 \, \frac{n_a n_b}{n}
\end{aligned}
$$

**Precision.** The obvious formula,
$\text{variance} = \overline{x^2} - \bar x^{\,2}$ from running sums, fails on real
data: for values near $10^8$ with a spread of $1$, both terms are about
$10^{16}$, and their difference is lost to rounding (it can even come out
negative). The tests include such data. Welford's update avoids this; for
the last few digits, also run it on $x - K$ for a fixed reference value $K$
per shard, such as its first value (shifting the data does not change the
variance). Answers are accepted within a
relative error of $10^{-6}$.

You may use the Python standard library.

## Constraints

- Shard ids are in `[0, 100)`; `merge` takes two different shards
- Every value is finite with absolute value `<= 10⁹`
- At most `20000` calls in total

## Examples

**Example 1**

```
Input
["StreamStats", "add", "add", "add", "add", "add", "add", "add", "add", "stats", "stats"]
[[], [0, 2.0], [0, 4.0], [0, 4.0], [0, 4.0], [0, 5.0], [0, 5.0], [0, 7.0], [0, 9.0], [0], [1]]

Output
[null, null, null, null, null, null, null, null, null, [8, 5.0, 4.0, 4.571428571428571], [0, 0.0, 0.0, 0.0]]
```

Explanation: the squared deviations from the mean 5 sum to 32, so the
population variance is 32 / 8 = 4 and the sample variance 32 / 7. Shard 1 is
empty.

**Example 2**

```
Input
["StreamStats", "add", "add", "add", "add", "stats", "merge", "stats", "stats", "add", "stats"]
[[], [1, 1.0], [1, 3.0], [2, 11.0], [2, 13.0], [1], [1, 2], [1], [2], [2, -4.5], [2]]

Output
[null, null, null, null, null, [2, 2.0, 1.0, 2.0], null, [4, 7.0, 26.0, 34.666666666666664], [0, 0.0, 0.0, 0.0],
 null, [1, -4.5, 0.0, 0.0]]
```

Explanation: each shard alone has M2 = 2, but their means differ by 10, so
the merged M2 is 2 + 2 + 10² · 2 · 2 / 4 = 104, and 104 / 4 = 26. After the
merge shard 2 is empty and starts over.

**Example 3**

```
Input
["StreamStats", "add", "add", "add", "add", "merge", "stats"]
[[], [0, 100000000.5], [0, 100000001.5], [0, 100000000.0], [3, 100000002.0], [3, 0], [3]]

Output
[null, null, null, null, null, null, [4, 100000001.0, 0.625, 0.8333333333333334]]
```

Explanation: the deviations from 10⁸ + 1 are −0.5, 0.5, −1 and 1, so
M2 = 2.5. The running-sums formula returns 0 here.
