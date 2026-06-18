Each value in `asteroids` is a non-zero asteroid: the sign is its direction
(positive moves right, negative moves left) and the magnitude is its size. Moving
asteroids collide when a right-mover meets a left-mover; the smaller one explodes,
and equal sizes both explode. Same-direction asteroids never meet. Return the
**state after all collisions**.

## Constraints
- `0 <= len(asteroids) <= 10^4`
- `-1000 <= asteroids[i] <= 1000`, `asteroids[i] != 0`

## Examples
Input: `asteroids = [5,10,-5]`
Output: `[5,10]`
Explanation: `10` and `-5` collide; `10` survives.

Input: `asteroids = [8,-8]`
Output: `[]`
Explanation: Equal opposite asteroids annihilate.
