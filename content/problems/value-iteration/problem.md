# Value Iteration for an MDP

**Value iteration** solves a Markov decision process: it computes how much
long-run discounted reward each state is worth, and which action to take
there. Implement it exactly as specified.

**The MDP.** `transitions[s]` lists the actions available in state $s$. Each
action is a list of outcomes `[p, nextState, reward]`: with probability $p$,
taking the action moves to `nextState` and earns `reward`. A state with **no
actions** is terminal and is worth $0$.

**Sweeps.** Start from $V(s) = 0$ for every state. One sweep computes, for
every state at once from the *previous* sweep's values (a synchronous,
Jacobi-style update, not in-place), with $\gamma$ = `gamma` and the sum over
the action's outcomes $(p, s', r)$:

$$
\begin{aligned}
Q(s, a) &= \sum_{(p,\, s',\, r)} p\, \big(r + \gamma\, V(s')\big) \\
V_\text{new}(s) &= \max_{a} Q(s, a)
\end{aligned}
$$

and $V_\text{new}(s) = 0$ for a terminal state. After each sweep, let
$\delta = \max_s \lvert V_\text{new}(s) - V(s) \rvert$. Replace $V$ with
$V_\text{new}$. **Stop** as soon as $\delta < \theta$ ($\theta$ = `theta`), or
once `maxIterations` sweeps have run.

**Policy.** Using the final $V$, each non-terminal state takes the action with
the largest $Q(s, a)$, the **lowest action index** on ties. Terminal states
get `-1`.

**Return `[V, policy, sweeps]`**, where `sweeps` is the number of sweeps
performed.

You may use the Python standard library and **numpy**.

Integers must match exactly. Values are accepted within a relative `1e-6` (or
an absolute `1e-9`). No sweep's $\delta$ is within a relative `1e-9` of
$\theta$. A state's two best actions differ by more than a relative `1e-9`
unless their outcome lists are identical.

## Constraints

- `1 <= len(transitions) <= 100`, and each state has `0` to `10` actions
- Each action has `1` to `10` outcomes `[p, nextState, reward]`, with
  `0 < p <= 1`, `0 <= nextState < len(transitions)` and `|reward| <= 100`.
  An action's probabilities sum to `1` within `1e-9`
- `0 <= gamma <= 0.99`, `1e-10 <= theta <= 1` and
  `1 <= maxIterations <= 10⁴`

## Examples

**Example 1**
```
Input:  transitions = [[], [[[1.0, 0, 5.0]]], [[[1.0, 1, 0.0]], [[1.0, 2, 1.0]]]],
        gamma = 0.9, theta = 1e-06, maxIterations = 1000
Output: [[0.0, 5.0, 9.999991505039022], [-1, 0, 1], 129]
Explanation: state 0 is terminal, and state 1 earns 5 on its way there. In
state 2, action 0 moves to state 1 (worth 0.9 · 5 = 4.5), while action 1 stays
and earns 1 per step, worth 1 / (1 − 0.9) = 10 in the limit. The changes
shrink by a factor of 0.9 per sweep and first fall below 1e-6 at sweep 129.
```

**Example 2**
```
Input:  transitions = [[[[1.0, 1, 1.5]], [[0.5, 0, 2.0], [0.5, 1, 0.0]], [[1.0, 1, 1.5]]], [[[1.0, 1, 1.0]]]],
        gamma = 0.5, theta = 1e-09, maxIterations = 1000
Output: [[2.4999999990686774, 1.9999999990686774], [0, 0], 31]
Explanation: in state 0, actions 0 and 2 are identical and tie, so the lower
index wins. Action 1 is worth only about 2.125.
```

**Example 3**
```
Input:  the same MDP and gamma as Example 1, theta = 1e-06, maxIterations = 2
Output: [[0.0, 5.0, 4.5], [-1, 0, 1], 2]
Explanation: sweep 1 gives V = [0, 5, 1], because state 2 still saw V[1] = 0.
Sweep 2 gives V[2] = max(0.9 · 5, 1 + 0.9 · 1) = 4.5. The cap stops it there.
The policy uses the final V: action 1 is worth 1 + 0.9 · 4.5 = 5.05, which
beats 4.5.
```
