# Tabular Q-Learning, SARSA and Expected SARSA

Train a tabular action-value function `Q[s][a]` from **recorded experience**.
The episodes are given, so the result is fully determined. Implement the
three classic temporal-difference (TD) control updates.

**Experience.** `episodes` is a list of episodes, processed in order. Each
episode is a list of steps `[s, a, r, s2, done]`: in state $s$ the agent took
action $a$, received reward $r$, and landed in state $s_2$. `done` is `true`
only on an episode's last step, and only when $s_2$ is terminal. An episode
whose last step has `done = false` was cut off: its last $s_2$ is an ordinary
state.

**The update.** Start with every `Q[s][a] = initialQ`. Then, for each step in
order, with $\gamma$ = `gamma` and $\alpha$ = `alpha`, compute the target $y$
for the chosen algorithm, the TD error $\delta$, and update:

$$
y =
\begin{cases}
r & \text{if done} \\
r + \gamma \max_{a'} Q(s_2, a') & \text{q-learning} \\
r + \gamma\, Q(s_2, a_\text{next}) & \text{sarsa} \\
r + \gamma\, \mathbb{E}_\pi\big[Q(s_2, \cdot)\big] & \text{expected-sarsa}
\end{cases}
$$

$$
\begin{aligned}
\delta &= y - Q(s, a) \\
Q(s, a) &\leftarrow Q(s, a) + \alpha\, \delta
\end{aligned}
$$

For `"sarsa"`, $a_\text{next}$ is the next step's action. For
`"expected-sarsa"`, $\pi$ is $\varepsilon$-greedy with $\varepsilon$ =
`epsilon`: with probability $\varepsilon$ it picks one of the $n$ =
`numActions` actions uniformly at random (the greedy one included), otherwise
it picks the greedy action. So

$$
\begin{aligned}
\mathbb{E}_\pi\big[Q(s_2, \cdot)\big] &= (1 - \varepsilon) \max_{a'} Q(s_2, a') \\
&\quad + \frac{\varepsilon}{n} \sum_{a'} Q(s_2, a')
\end{aligned}
$$

- The target is computed from the table **as it stands before this step's
  update**, and every step's update is visible to the steps after it (even
  within the same episode).
- `epsilon` is ignored by the other two algorithms.
- For `"sarsa"`, every episode ends with `done = true`, so $a_\text{next}$
  always exists when it is needed.

**Return `[Q, tdErrors, policy]`**:

- `Q`: the final table, `numStates` rows of `numActions` values.
- `tdErrors`: every step's $\delta$, in processing order.
- `policy`: for each state, the action with the largest final `Q[s][a]`, the
  **lowest action index** on ties. Do this for every state, including ones
  that were never visited.

You may use the Python standard library and **numpy**.

Integers must match exactly. Values are accepted within a relative `1e-6` (or
an absolute `1e-9`). The tests avoid near-ties: whenever two of a state's
actions are within a relative `1e-9` of its best value, both were never
updated, so they still hold exactly `initialQ`.

## Constraints

- `1 <= numStates <= 50` and `1 <= numActions <= 10`
- `1 <= len(episodes) <= 300`, every episode is non-empty, and there are at
  most `5000` steps in total
- In each step, `0 <= s, s2 < numStates`, `0 <= a < numActions` and
  `|r| <= 100`. Each step's `s2` is the next step's `s`
- `algorithm` is `"q-learning"`, `"sarsa"` or `"expected-sarsa"`
- `0 < alpha <= 1`, `0 <= gamma <= 1`, `0 <= epsilon <= 1` and
  `|initialQ| <= 100`

## Examples

All three examples use the same two episodes, with `numStates = 3` and
`numActions = 2`:

```
episodes = [[[0, 1, 1.0, 1, false], [1, 1, 5.0, 2, true]],
            [[0, 0, 0.0, 1, false], [1, 0, 2.0, 0, false], [0, 1, 1.0, 1, false], [1, 1, 5.0, 2, true]]]
```

**Example 1**
```
Input:  numStates = 3, numActions = 2, episodes = (above), algorithm = "q-learning",
        alpha = 0.5, gamma = 0.9, epsilon = 0.0, initialQ = 0.0
Output: [[[1.125, 1.875], [1.50625, 3.75], [0.0, 0.0]], [1.0, 5.0, 2.25, 3.0125, 2.75, 2.5], [1, 1, 0]]
Explanation: episode 1 sets Q[0][1] = 0.5 and then Q[1][1] = 2.5 (a terminal
step, so the target is just 5). In episode 2, the first step's target is
0 + 0.9 · max(Q[1]) = 2.25. The second step's target is
2 + 0.9 · max(1.125, 0.5) = 3.0125, which already uses the Q[0][0] that
episode 2 just updated. State 2 is never updated, so its two zeros tie and
action 0 wins.
```

**Example 2**
```
Input:  the same, with algorithm = "sarsa"
Output: [[[0.0, 1.875], [1.225, 3.75], [0.0, 0.0]], [1.0, 5.0, 0.0, 2.45, 2.75, 2.5], [1, 1, 0]]
Explanation: in episode 2, the first step bootstraps from the action actually
taken next, Q[1][0] = 0, not the greedy Q[1][1] = 2.5, so its target is 0.
The second step bootstraps from Q[0][1] = 0.5: 2 + 0.9 · 0.5 = 2.45.
```

**Example 3**
```
Input:  the same, with algorithm = "expected-sarsa", alpha = 0.25, epsilon = 0.2, initialQ = 2.0
Output: [[[2.101875, 2.51296282421875], [2.4927921875, 3.3125], [2.0, 2.0]],
         [0.7999999999999998, 3.0, 0.4075000000000002, 1.9711687500000004, 1.2518512968750004, 2.25],
         [1, 1, 0]]
Explanation: the first step sees Q[1] = [2, 2], so the expected value is 2 and
the target is 1 + 0.9 · 2 = 2.8 (delta 0.8). Later, Q[1] = [2, 2.75] gives
0.8 · 2.75 + 0.2 · 2.375 = 2.675.
```
