> **Format:** your function receives the root of the tree as a `TreeNode` (`value`, `left`, `right`). The examples draw each tree. The grey line under a drawing is the same tree in level-order form (`null` = missing child), which is how the tests store it.

A thief has found a new neighborhood to rob. It has a single entrance, the house
at `root`, and every other house has exactly one parent house, so the houses form
a **binary tree**. Each house holds `node.value` dollars.

The houses share an alarm system: if two **directly-linked** houses (a parent and
its child) are both robbed on the same night, the police are called. Houses that
are not linked, such as two siblings or a grandparent and a grandchild, can be
robbed together.

Return **the maximum amount of money the thief can rob without alerting the
police**.

## Examples

**Example 1**

![Example 1: rob the root 3 and the two bottom houses 3 and 1, for 7](/problems/house-robber-iii/assets/example-1.svg)

- **Output:** `7`
- **Explanation:** Rob the root `3` and the two bottom houses `3` and `1`. No two of them are linked, so the total is 3 + 3 + 1 = 7.

**Example 2**

![Example 2: rob the root's two children 4 and 5, for 9](/problems/house-robber-iii/assets/example-2.svg)

- **Output:** `9`
- **Explanation:** Rob the root's children `4` and `5`. Robbing the root instead rules both of them out, and the best total is then 3 + 1 + 3 + 1 = 8.

**Example 3**

![Example 3: rob 3 and 4, which sit on different levels, for 7](/problems/house-robber-iii/assets/example-3.svg)

- **Output:** `7`
- **Explanation:** Rob `3` and `4`. They are on different levels, which is fine because they are not linked. Taking whole alternate levels gives only 2 + 4 = 6 or 1 + 3 = 4.

## Constraints
- The number of nodes is in the range `[1, 10^4]`.
- `0 <= node.value <= 10^4`
