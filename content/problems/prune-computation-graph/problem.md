A deep-learning compiler receives a model as a **computation graph**: every
node is an operator (`conv`, `relu`, `add`, …) whose inputs are the outputs of
other nodes. Before running it, the compiler checks that the graph is well
formed, and when only one of the model's outputs is requested it **prunes**
every node that output does not depend on.

`nodes[i]` is `[name, op, inputs]`: a node's unique name, its operator (a
string), and the list of names of the nodes it reads. A node with `op` equal
to `"input"` is a graph input and must have no inputs.

**Validation.** The graph is **valid** when all of these hold:

1. node names are distinct;
2. every name in every `inputs` list is the name of a node;
3. only `"input"` nodes have an empty `inputs` list, and `"input"` nodes have
   none;
4. the graph has no cycle (a node may not depend on itself, directly or
   through other nodes);
5. `output` is the name of a node.

The checks apply to the **whole** graph, including the parts that pruning
would remove.

**Pruning.** The nodes `output` needs are `output` itself and everything it
depends on, directly or indirectly. List them in an execution order: every
node after all of its inputs. Among the nodes that could run next, always
take the one that appears **earliest** in `nodes`.

**Return `[valid, order]`**: whether the graph is valid, and the pruned
execution order as a list of names (empty when the graph is not valid).

## Constraints

- `1 <= len(nodes) <= 5000`; a node has at most `8` inputs (repeats allowed:
  `add(x, x)` reads `x` twice)
- Names and ops are non-empty strings of at most `20` characters

## Examples

**Example 1**
```
Input:  nodes = [["x", "input", []], ["w", "input", []], ["scale", "relu", ["w"]], ["conv1", "conv", ["x", "w"]],
                 ["aux", "pool", ["x"]], ["head", "add", ["conv1", "scale"]]],
        output = "head"
Output: [true, ["x", "w", "scale", "conv1", "head"]]
Explanation: "aux" feeds nothing that "head" needs, so it is pruned. After
"x" and "w", both "scale" and "conv1" can run, and "scale" is listed first.
(A depth-first post-order from "head" would visit "conv1" first.)
```

**Example 2**
```
Input:  nodes = [["x", "input", []], ["h", "relu", ["x"]], ["h", "conv", ["x"]], ["y", "add", ["h", "x"]]],
        output = "y"
Output: [false, []]
Explanation: two nodes are named "h", so "y"'s input is ambiguous.
```

**Example 3**
```
Input:  nodes = [["x", "input", []], ["p", "add", ["x", "q"]], ["q", "relu", ["p"]], ["y", "relu", ["x"]]],
        output = "y"
Output: [false, []]
Explanation: "p" and "q" read each other. "y" does not need either of them,
but the graph as a whole is still invalid.
```

**Example 4**
```
Input:  nodes = [["x", "input", []], ["bias", "const", []], ["y", "add", ["x", "bias"]]], output = "y"
Output: [false, []]
Explanation: "bias" has no inputs but is not an "input" node.
```
