Design a structure that tracks connectivity among `n` nodes labelled `0` to
`n - 1`. Every node starts in its own component; a `union` merges the components
of two nodes, and a `connected` query reports whether two nodes are in the same
component **at that moment**.

Implement the `UnionFind` class:

- `UnionFind(int n)` initializes the structure with `n` nodes `0..n-1`, each in
  its own component.
- `void union(int a, int b)` merges the components containing `a` and `b`. If they
  are already in the same component, nothing changes.
- `boolean connected(int a, int b)` returns `true` if `a` and `b` are in the same
  component, and `false` otherwise. A node is always connected to itself.

**Example 1:**

```
Input
["UnionFind", "connected", "union", "connected"]
[[5], [0, 1], [0, 1], [0, 1]]

Output
[null, false, null, true]
```

Explanation: `0` and `1` are separate until they are merged.

**Example 2:**

```
Input
["UnionFind", "union", "union", "connected"]
[[3], [0, 1], [1, 2], [0, 2]]

Output
[null, null, null, true]
```

Explanation: connectivity is transitive — merging `0-1` and `1-2` puts `0` and `2`
in one component.

**Constraints:**

- `1 <= n <= 10⁴`
- `0 <= a, b < n`
- At most `10⁵` calls will be made to `union` and `connected`.
