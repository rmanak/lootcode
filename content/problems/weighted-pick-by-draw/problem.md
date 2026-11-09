Weighted random choice is everywhere in ML systems: sampling training
examples by importance, choosing negative samples by frequency, routing
traffic between model versions by percentage. Each item $i$ has a weight
$w_i \ge 0$ and should be chosen with probability $w_i / \sum_j w_j$. In
production the weights also **change** while picks keep coming (an A/B test
shifts traffic, a sample's importance is re-estimated).

To make the picks testable, the randomness is passed in. Lay the items out
on a number line in index order: item $i$ owns the half-open interval
$[P_i, P_i + w_i)$, where $P_i = w_0 + \dots + w_{i-1}$. A draw $r$ with
$0 \le r < \sum_j w_j$ picks the item whose interval contains $r$. (A uniform
random $r$ then picks item $i$ with exactly the probability above.) An item of
weight $0$ owns an empty interval and is never picked.

- `WeightedPicker(weights)` stores the initial weights.
- `pick(r)` returns the index of the item whose interval contains `r`.
- `update(i, weight)` sets item `i`'s weight to `weight`.
- `total()` returns the current sum of the weights.

With up to $10^5$ items and $10^5$ calls in any mix, both `pick` and `update`
must take $O(\log n)$ time.

## Constraints

- `1 <= len(weights) <= 10⁵`; every weight is an integer in `[0, 10¹²]`
- `update` takes an index in range and a weight in `[0, 10¹²]`
- `pick` is only called with `0 <= r < total()`
- At most `10⁵` calls in total

## Examples

**Example 1**

```
Input
["WeightedPicker", "pick", "pick", "pick", "pick", "pick", "total"]
[[[331, 1380, 38]], [0], [330], [331], [1710], [1711], []]

Output
[null, 0, 0, 1, 1, 2, 1749]
```

Explanation: think of three countries weighted by population (in millions).
Item 0 owns [0, 331), item 1 owns [331, 1711) and item 2 owns [1711, 1749). A
draw equal to an interval's start belongs to that interval.

**Example 2**

```
Input
["WeightedPicker", "pick", "pick", "update", "pick", "pick", "total"]
[[[1, 0, 3]], [0], [1], [1, 2], [1], [3], []]

Output
[null, 0, 2, null, 1, 2, 6]
```

Explanation: item 1 starts with weight 0, so r = 1 skips it and lands in
item 2's interval [1, 4). After the update the intervals are [0, 1), [1, 3)
and [3, 6).

**Example 3**

```
Input
["WeightedPicker", "update", "pick", "pick", "update", "pick", "pick", "total"]
[[[5, 5]], [0, 0], [0], [4], [0, 10], [9], [10], []]

Output
[null, null, 1, 1, null, 0, 1, 15]
```

Explanation: once item 0 has weight 0, every draw goes to item 1. `update`
sets the weight to 10 (it does not add 10), and the intervals become [0, 10)
and [10, 15).
