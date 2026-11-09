A driving policy proposes a batch of future **trajectories**, each a sequence
of 2-D waypoints sampled every `dt` seconds. Two quantities feed its training
signal: a **speed-limit penalty**, and the **remaining path length** at each
waypoint (used, for example, to weight progress). Compute both for a whole
batch.

`trajectories[b][k]` is waypoint $k$ of trajectory $b$, a point $[x, y]$ in
metres, with $W$ waypoints per trajectory. Segment $k$ runs from waypoint $k$ to
waypoint $k + 1$ (for $k = 0, \dots, W - 2$); its length $\ell_{b,k}$ is the
Euclidean distance between them, and the speed over it is
$v_{b,k} = \ell_{b,k} / \texttt{dt}$.

The limit changes along the route: `speedLimits[k]` is the limit, in metres
per second, during segment $k$. A trajectory is charged for every metre it
travels above the limit:

$$
\texttt{penalty}_b = \sum_{k=0}^{W-2} \max\!\left(0,\; v_{b,k} - \texttt{speedLimits}[k]\right) \cdot \texttt{dt}
$$

The **remaining distance** at waypoint $k$ is the length of the path still
ahead of it:

$$
\texttt{remaining}_{b,k} = \sum_{j=k}^{W-2} \ell_{b,j}
$$

which is $0$ at the last waypoint. It is a suffix sum: compute it in one
backward pass (or as a reversed cumulative sum), not by re-adding every suffix.

**Return `[penalty, remaining]`**: a list of $B$ penalties and a $B \times W$
list of remaining distances.

You may use **numpy** and the Python standard library.

## Constraints

- `1 <= B <= 100` trajectories, `2 <= W <= 200` waypoints each
- Every coordinate is finite with absolute value `<= 10⁴`
- `speedLimits` has `W − 1` numbers, each in `[0, 100]`
- `0 < dt <= 1`

## Examples

**Example 1**
```
Input:  trajectories = [[[0.0, 0.0], [3.0, 4.0], [6.0, 8.0]]], speedLimits = [40.0, 40.0], dt = 0.1
Output: [[2.0], [[10.0, 5.0, 0.0]]]
Explanation: both segments are 5 m long, covered in 0.1 s: 50 m/s against a
limit of 40. Each is 10 m/s too fast for 0.1 s, a penalty of 1.
```

**Example 2**
```
Input:  trajectories = [[[0.0, 0.0], [1.0, 0.0], [3.0, 0.0], [3.0, 0.5]], [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 3.0]]],
        speedLimits = [5.0, 10.0, 20.0], dt = 0.1
Output: [[1.5, 1.0], [[3.5, 2.5, 0.5, 0.0], [3.0, 3.0, 3.0, 0.0]]]
Explanation: the first trajectory runs at 10, 20 and 5 m/s against limits 5,
10 and 20, so it is over by 5 and 10 m/s: (5 + 10)·0.1 = 1.5. The second stands
still, then jumps 3 m: 30 m/s against 20, a penalty of 1.
```

**Example 3**
```
Input:  trajectories = [[[10.0, 10.0], [7.0, 6.0]]], speedLimits = [2.0], dt = 0.5
Output: [[4.0], [[5.0, 0.0]]]
Explanation: 5 m in 0.5 s is 10 m/s, 8 over the limit for 0.5 s.
```
