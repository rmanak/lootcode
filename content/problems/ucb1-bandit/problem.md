A **multi-armed bandit** has $K$ slot machines ("arms") with unknown payout
rates. Each round you pull one arm and see its reward; the goal is to collect
as much as possible over $T$ rounds, which means balancing **exploration**
(trying arms you know little about) against **exploitation** (pulling the arm
that looks best). **UCB1** does this with optimism: it pulls the arm whose
*upper confidence bound* on the mean reward is highest. Simulate it.

The randomness is given. `rewards[a][k]` is the reward (`0` or `1`) that arm
$a$ pays on its $k$-th pull (counting from $0$), so pulling an arm for the
fifth time always pays `rewards[a][4]`. Every list is at least $T$ long.

Rounds are numbered $t = 1, \dots, T$.

- **Rounds $1$ to $K$:** pull each arm once, in order: arm $t - 1$ in round $t$.
- **Every later round $t$:** with $n_a$ the number of times arm $a$ has been
  pulled so far and $\hat\mu_a$ the mean of the rewards it paid, pull

$$
\operatorname*{arg\,max}_{a} \; \hat\mu_a + \sqrt{\frac{2 \ln t}{n_a}}
$$

  (natural log, $t$ the current round). On a tie, the arm with the smallest
  index. The tests promise that arms with different $(n_a, \hat\mu_a)$ never
  come within $10^{-9}$ of each other, so a tie only happens between arms
  with identical statistics.

The bonus shrinks as an arm is pulled more, and grows slowly with time, so an
arm that looks bad is still revisited now and then.

**Return `[totalReward, pulls]`**: the sum of all rewards collected, and the
list of the $T$ arms pulled, in round order.

## Constraints

- `2 <= K <= 10` arms; `K <= T <= 2000`
- Every `rewards[a]` has at least `T` entries, each `0` or `1`

## Examples

**Example 1**
```
Input:  rewards = [[1, 1, 1, 1, 1], [0, 0, 0, 0, 0]], T = 5
Output: [4, [0, 1, 0, 0, 0]]
Explanation: after one pull each, arm 0 has mean 1 and arm 1 mean 0 with the
same bonus, so arm 0 is pulled from then on (its growing count shrinks its
bonus, but not enough to lose its lead of 1 within 5 rounds).
```

**Example 2**
```
Input:  rewards = [[0, 1, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 1, 1]], T = 6
Output: [2, [0, 1, 2, 1, 0, 2]]
Explanation: rounds 1 to 3 pull each arm once (rewards 0, 1, 0). Round 4:
arm 1 leads with 1 + √(2 ln 4) ≈ 2.665 and pays 0. Round 5: arms 0 and 2 both
have one pull and mean 0, so they tie at √(2 ln 5) ≈ 1.794, ahead of arm 1's
0.5 + √(ln 5) ≈ 1.769; the tie goes to arm 0, whose second pull pays 1.
Round 6: arm 2 (≈ 1.893) beats arms 0 and 1 (both ≈ 1.839).
```

**Example 3**
```
Input:  rewards = [[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0]], T = 7
Output: [0, [0, 1, 0, 1, 0, 1, 0]]
Explanation: with every mean at 0 only the bonus matters, and it is largest
for the arm pulled less often. Equal counts tie, and the smaller index wins.
```
