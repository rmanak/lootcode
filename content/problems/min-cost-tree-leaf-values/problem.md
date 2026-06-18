Build a binary tree whose leaves are the values of `arr` **in order** (left to
right). Each internal node's value is the product of the largest leaf in its left
subtree and the largest leaf in its right subtree. Return the **minimum possible sum
of all internal node values**.

## Constraints
- `2 <= len(arr) <= 40`
- `1 <= arr[i] <= 15`

## Examples
Input: `arr = [6,2,4]`
Output: `32`
Explanation: Combine `2` and `4` (`8`), then with `6` (`24`); `8 + 24 = 32`.

Input: `arr = [4,11]`
Output: `44`
Explanation: The single internal node is `4 * 11 = 44`.
