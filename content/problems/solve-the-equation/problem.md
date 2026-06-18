Solve a linear equation in the single variable `x`. The equation uses only `+`, `-`,
the variable `x`, and non-negative integer coefficients, with exactly one `=`. Return
the answer as `"x=#value"`. If there is no solution return `"No solution"`; if every
value of `x` works return `"Infinite solutions"`. When a unique solution exists it is
guaranteed to be an integer.

**Examples**
```
"x+5-3+x=6+x-2"     ->  "x=2"
"x=x"               ->  "Infinite solutions"
"2x=x"              ->  "x=0"
"2x+3x-6x=x+2"      ->  "x=-1"
"x=x+2"             ->  "No solution"
```

**Constraints:** the input is a valid equation as described.
