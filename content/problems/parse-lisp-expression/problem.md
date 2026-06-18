Evaluate a Lisp-like `expression` and **return its integer value**. An expression
is one of:

- an integer (possibly negative), or a variable name;
- `(add e1 e2)` -> `eval(e1) + eval(e2)`;
- `(mult e1 e2)` -> `eval(e1) * eval(e2)`;
- `(let v1 e1 v2 e2 ... vn en expr)` -> assign each `vi` the value of `ei`
  **sequentially**, then evaluate `expr`.

Variables use lexical scope: a name resolves to the value bound in the innermost
enclosing `let`. Names `add`, `let`, `mult` are reserved.

**Examples**
```
(add 1 2)                                   ->  3
(mult 3 (add 2 3))                          ->  15
(let x 2 (mult x (let x 3 y 4 (add x y))))  ->  14
(let x 3 x 2 x)                             ->  2
```

**Constraints:** `1 <= len(expression) <= 2000`; the expression is well-formed and
every value fits in a 32-bit signed integer.
