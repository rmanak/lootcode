# Weighted Sampling Without Replacement

You need to draw $k$ distinct items from $N$, where item $i$ is picked with
probability proportional to its weight `weights[i]`. This is how many systems
choose negative samples, replay-buffer entries or ads. The method of
**Efraimidis and Spirakis** does it in one pass: give each item a random
**key** and keep the $k$ items with the largest keys. With $u_i$ = `u[i]` and
$w_i$ = `weights[i]`:

$$
\operatorname{key}(i) = u_i^{\,1 / w_i}
$$

Here $u_i$ is a uniform random number in $(0, 1)$. A larger weight pushes the
key toward 1, so heavy items tend to win. The draws are given to you, so the
answer is deterministic.

**Return the indices of the $k$ items with the largest keys**, ordered from the
largest key to the smallest. If two keys are exactly equal, the lower index
counts as larger.

**Careful with tiny weights.** With $w_i = 10^{-4}$, $u_i^{\,1/w_i}$ is
$u_i^{\,10000}$. That underflows to exactly $0$ for most $u_i$, and then every
such item ties. Taking the logarithm keeps the order and avoids the underflow:

$$
\log \operatorname{key}(i) = \frac{\log u_i}{w_i}
$$

In the tests, the keys that decide the answer are never within a relative
`1e-9` of each other, except exact ties between items with identical $u_i$ and
weight.

## Constraints

- `1 <= N <= 10⁴`, where `weights` and `u` both have `N` entries
- Every weight is a finite number with `10⁻⁴ <= weights[i] <= 10⁴`
- Every draw is a finite number with `0 < u[i] < 1`
- `1 <= k <= N`

## Examples

**Example 1**
```
Input:  weights = [1.0, 2.0, 4.0], k = 2, u = [0.5, 0.5, 0.5]
Output: [2, 1]
Explanation: with equal draws the heavier item wins. The keys are 0.5,
0.5^(1/2) ≈ 0.707 and 0.5^(1/4) ≈ 0.841.
```

**Example 2**
```
Input:  weights = [1.0, 1.0, 1.0, 1.0], k = 3, u = [0.2, 0.9, 0.2, 0.7]
Output: [1, 3, 0]
Explanation: with equal weights the keys are just the draws. Items 0 and 2 tie
at 0.2, and the lower index, 0, takes the last place.
```

**Example 3**
```
Input:  weights = [10.0, 0.5, 3.0, 1.0], k = 1, u = [0.1, 0.95, 0.6, 0.8]
Output: [1]
Explanation: the log-keys are −0.230, −0.103, −0.170 and −0.223. Item 1 has a
small weight, but its draw of 0.95 is high enough to win.
```
