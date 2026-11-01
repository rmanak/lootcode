# Autograd: Backpropagation Through an Expression Graph

Every deep-learning framework is built on **reverse-mode automatic
differentiation**. It runs the computation forward, then walks the graph
backward once, using the chain rule to accumulate the gradient of one output
with respect to every node. Implement that engine for a small expression
graph.

`nodes` is a list of node objects, **in no particular order**: a node may
appear before the nodes it reads. Each has a unique string `id` and an `op`:

| `op` | fields | value |
|------|--------|-------|
| `"input"`, `"const"` | `value` | `value` |
| `"add"`, `"sub"`, `"mul"`, `"div"` | `inputs: [a, b]` | $a + b$, $a - b$, $a \cdot b$, $a / b$ |
| `"neg"` | `inputs: [a]` | $-a$ |
| `"pow"` | `inputs: [a]`, `exponent: p` (a number) | $a^p$ |
| `"exp"`, `"log"` | `inputs: [a]` | $e^a$, $\ln a$ |
| `"tanh"`, `"sigmoid"`, `"relu"` | `inputs: [a]` | $\tanh a$, $\sigma(a) = 1 / (1 + e^{-a})$, $\max(a, 0)$ |

The graph is acyclic. A node may be used by many others, and may even appear
twice in one node's `inputs` (as in `mul(x, x)`).

**Return `[value, grads]`**:

- `value`: the forward value of the node `output`.
- `grads`: for **every** node, in the order of `nodes`, the derivative of
  `output` with respect to that node's value, treating each node as an
  independent variable that feeds the nodes above it. This covers inputs,
  constants and intermediate nodes alike. `output`'s own gradient is `1`. A
  node that `output` does not depend on has gradient `0`, and so does a
  node computed *from* `output`.

The local derivatives follow from the table: $\tanh' = 1 - \tanh^2$,
$\sigma' = \sigma\, (1 - \sigma)$, $\frac{d}{da}\, a^p = p\, a^{p-1}$ ($0$ when
$p = 0$), and $\operatorname{relu}'(a) = 1$ if $a > 0$, else $0$. So the
derivative is **$0$ at exactly $a = 0$**, as in PyTorch. When a node feeds
several users, its gradient is the **sum** over all of them.

You may use the Python standard library and **numpy**.

Answers are accepted when every number is within a relative `1e-6` (or an
absolute `1e-9`) of the expected value. Every value and gradient is finite
and at most $10^{12}$ in absolute value. A relu's input is either exactly $0$
or at least `1e-6` away from it.

## Constraints

- `1 <= len(nodes) <= 500`, ids are unique non-empty strings of at most 20
  characters, and every input names a node in the list. `output` names a node
- `|value| <= 100` for inputs and constants, and `|exponent| <= 10`
- Every operation is defined where it is evaluated: no division by `0`, `log`
  only of positive numbers, a negative base for `pow` only with an integer
  exponent, `0 ** p` only for `p = 0` or `p >= 1`, and inputs to `exp`,
  `tanh` and `sigmoid` within `[−100, 100]`

## Examples

**Example 1**
```
Input:  nodes = [{"id": "f", "op": "add", "inputs": ["p", "x"]}, {"id": "p", "op": "mul", "inputs": ["x", "y"]},
                 {"id": "x", "op": "input", "value": 2.0}, {"id": "y", "op": "input", "value": 3.0}],
        output = "f"
Output: [8.0, [1.0, 1.0, 4.0, 2.0]]
Explanation: f = x · y + x = 8. x feeds both p and f, so its gradient is
y + 1 = 4 (the two contributions add). y's is x = 2. The list is in the order
of nodes: f, p, x, y.
```

**Example 2**
```
Input:  nodes = [{"id": "out", "op": "add", "inputs": ["m", "r"]}, {"id": "m", "op": "mul", "inputs": ["t", "s"]},
                 {"id": "t", "op": "tanh", "inputs": ["c"]}, {"id": "s", "op": "sigmoid", "inputs": ["c"]},
                 {"id": "r", "op": "relu", "inputs": ["d"]}, {"id": "d", "op": "sub", "inputs": ["a", "b"]},
                 {"id": "c", "op": "input", "value": 0.5}, {"id": "a", "op": "input", "value": 1.5},
                 {"id": "b", "op": "const", "value": 1.5}],
        output = "out"
Output: [0.28764913664496794, [1.0, 1.0, 0.6224593312018546, 0.46211715726000974, 1.0, 0.0,
                               0.5981309773153363, 0.0, 0.0]]
Explanation: d = 1.5 − 1.5 = 0 exactly, so relu passes no gradient back to d,
a or b. c feeds both t and s:
s · (1 − t²) + t · s · (1 − s) ≈ 0.4896 + 0.1086 = 0.5981.
```

**Example 3**
```
Input:  nodes = [{"id": "x", "op": "input", "value": 2.0}, {"id": "y", "op": "input", "value": 4.0},
                 {"id": "q", "op": "div", "inputs": ["x", "y"]}, {"id": "cube", "op": "pow", "inputs": ["x"], "exponent": 3},
                 {"id": "lg", "op": "log", "inputs": ["y"]}, {"id": "nx", "op": "neg", "inputs": ["x"]},
                 {"id": "e", "op": "exp", "inputs": ["nx"]}, {"id": "s1", "op": "sub", "inputs": ["cube", "q"]},
                 {"id": "s2", "op": "mul", "inputs": ["lg", "e"]}, {"id": "z", "op": "add", "inputs": ["s1", "s2"]},
                 {"id": "after", "op": "mul", "inputs": ["z", "z"]}, {"id": "unused", "op": "mul", "inputs": ["x", "y"]}],
        output = "z"
Output: [7.687614540011479, [11.562385459988521, 0.15883382080915318, -1.0, 1.0, 0.1353352832366127,
                             0.18761454001147945, 1.3862943611198906, 1.0, 1.0, 1.0, 0.0, 0.0]]
Explanation: z = x³ − x/y + ln(y) · e^(−x). The x gradient is
3x² − 1/y − ln(y) · e^(−x) = 12 − 0.25 − 0.1876. The y gradient is
x/y² + e^(−x)/y = 0.125 + 0.0338. "after" is computed from z and "unused"
doesn't reach z, so both get 0.
```
