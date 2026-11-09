A hyperparameter search tries every combination of a set of options, for
example

```
learning_rate: [0.1, 0.2, 0.3]
feature:       ["A", "B", "C"]
batch:         [10, 20, 30]
```

which gives $3 \cdot 3 \cdot 3 = 27$ runs. A distributed search hands run
number $k$ to worker $k$, and each worker must work out its own combination
without listing the whole grid, which can be astronomically large.

`values[t]` is the list of options for the $t$-th hyperparameter. The
combinations are ordered like `itertools.product`: the **last** hyperparameter
changes fastest, then the one before it, and so on. In the example, run $0$ is
`[0.1, "A", 10]`, run $1$ is `[0.1, "A", 20]`, run $3$ is `[0.1, "B", 10]`, and
run $26$ is `[0.3, "C", 30]`.

**Return `[count, combinations]`**: the number of combinations, and for each
index in `queries` the combination at that index (a list with one value per
hyperparameter).

Two edge cases follow from the definition: with no hyperparameters there is
exactly one combination, the empty one; and if any hyperparameter has no
options there are no combinations at all (and no queries).

## Constraints

- `0 <= len(values) <= 30`; each `values[t]` has `0` to `100` options
  (numbers or strings)
- The number of combinations is at most `10¹⁸`
- `0 <= len(queries) <= 10⁴`; every query is in `[0, count)`

## Examples

**Example 1**
```
Input:  values = [[0.1, 0.2, 0.3], ["A", "B", "C"], [10, 20, 30]], queries = [0, 1, 3, 26]
Output: [27, [[0.1, "A", 10], [0.1, "A", 20], [0.1, "B", 10], [0.3, "C", 30]]]
```

**Example 2**
```
Input:  values = [["adam", "sgd"], [1, 2, 3, 4, 5]], queries = [4, 5, 9]
Output: [10, [["adam", 5], ["sgd", 1], ["sgd", 5]]]
Explanation: the second key cycles through its 5 options before the first
key moves on to "sgd".
```

**Example 3**
```
Input:  values = [], queries = [0]
Output: [1, [[]]]
```

**Example 4**
```
Input:  values = [[1, 2], [], ["x"]], queries = []
Output: [0, []]
```
