Given a chemical `formula`, return the count of each atom. An element name starts with
an uppercase letter followed by zero or more lowercase letters; an optional count (only
shown when `> 1`) follows. Formulas can be concatenated and grouped in parentheses with
an optional multiplier, e.g. `(H2O2)3`. Output the elements in **sorted (alphabetical)
order**, each name followed by its total count (omit the count when it is `1`).

**Examples**
```
formula = "H2O"               ->  "H2O"
formula = "Mg(OH)2"           ->  "H2MgO2"
formula = "K4(ON(SO3)2)2"     ->  "K4N2O14S4"
```

**Constraints:** `1 <= len(formula) <= 1000`, a valid formula of letters, digits, `()`.
