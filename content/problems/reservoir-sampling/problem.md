You are reading a stream of items one at a time. You don't know how long it is,
and it does not fit in memory. You need a uniform random sample of $k$ items
from everything seen so far. **Reservoir sampling** (Algorithm R) keeps a
reservoir of $k$ slots and gives every item seen so far the same chance,
$k / i$, of being in it.

The random numbers are given to you, so the answer is deterministic. Implement
the `ReservoirSampler` class:

- `ReservoirSampler(k)`: an empty reservoir with `k` slots.
- `add(item, u)`: offer the next item of the stream. `u` is a uniform random
  number in $[0, 1)$ drawn for this step. Returns nothing. Let $i$ be the
  number of items added so far, **including** this one (so $i = 1$ for the
  first item):
  - if $i \le k$: put the item in the next empty slot. `u` is not used.
  - otherwise: let $j = \lfloor u \cdot i \rfloor$, a uniform integer in
    $[0, i - 1]$. If $j < k$, the item replaces the one in slot $j$. If not,
    the item is discarded.
- `sample()`: return the reservoir's current contents, slot `0` first. Before
  $k$ items have been added it holds fewer than $k$ items.

The tests are built so that $u \cdot i$ is never within `1e-9` of an integer
unless it is exactly one, and then floating-point multiplication computes it
exactly.

## Constraints

- `1 <= k <= 100`
- Every item is an integer with absolute value `<= 10⁹`
- Every `u` is a number with `0 <= u < 1`
- At most `10⁴` calls to `add`

## Examples

**Example 1**
```
Input:  ["ReservoirSampler", "add", "add", "sample", "add", "sample", "add", "sample", "add", "sample"]
        [[2], [10, 0.9], [20, 0.1], [], [30, 0.5], [], [40, 0.2], [], [50, 0.95], []]
Output: [null, null, null, [10, 20], null, [10, 30], null, [40, 30], null, [40, 30]]
Explanation: the first two items fill the slots, whatever their u.
i = 3: j = floor(0.5 · 3) = 1, so 30 replaces slot 1.
i = 4: j = floor(0.2 · 4) = 0, so 40 replaces slot 0.
i = 5: j = floor(0.95 · 5) = 4, which is not < 2, so 50 is discarded.
```

**Example 2**
```
Input:  ["ReservoirSampler", "sample", "add", "sample", "add", "add", "add", "sample"]
        [[3], [], [7, 0.0], [], [8, 0.3], [9, 0.6], [1, 0.74], []]
Output: [null, [], null, [7], null, null, null, [7, 8, 1]]
Explanation: at i = 4, j = floor(0.74 · 4) = 2, so 1 replaces 9 in slot 2.
```

**Example 3**
```
Input:  ["ReservoirSampler", "add", "add", "add", "sample", "add", "sample"]
        [[1], [5, 0.3], [6, 0.49], [7, 0.34], [], [8, 0.24], []]
Output: [null, null, null, null, [6], null, [8]]
Explanation: at i = 2, j = floor(0.98) = 0, so 6 replaces 5. At i = 3,
j = floor(1.02) = 1, so 7 is discarded. At i = 4, j = floor(0.96) = 0, so 8
replaces 6.
```
