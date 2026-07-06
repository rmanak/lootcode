Given the `head` of a **singly linked list** `L0 -> L1 -> ... -> Ln`, reorder it to
`L0 -> Ln -> L1 -> L(n-1) -> L2 -> ...`. Rearrange the nodes themselves (do not just
change their `.val` fields), and return the head of the reordered list.

> **Format:** each node is a `ListNode` with a `.val` and a `.next` pointer (the class is provided — do not redefine it). Lists are shown below as the array of their node values (`[]` = empty list).

**Example:** `head = [1,2,3,4]` -> `[1,4,2,3]`.

**Constraints:** `1 <= number of nodes <= 5*10^4`.
