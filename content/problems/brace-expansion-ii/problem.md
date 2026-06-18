A grammar over lowercase letters builds sets of words:

- a single letter `x` denotes `{x}`;
- a comma-separated list inside braces is the **union** of its parts, e.g.
  `{a,b,c}` -> `{a,b,c}`;
- writing expressions next to each other is the set of **concatenations**, e.g.
  `{a,b}{c,d}` -> `{ac,ad,bc,bd}`.

Given such an `expression`, return the sorted list of distinct words it represents.

**Examples**
```
"{a,b}{c,{d,e}}"          ->  ["ac","ad","ae","bc","bd","be"]
"{{a,z},a{b,c},{ab,z}}"   ->  ["a","ab","ac","z"]
```

**Constraints:** `1 <= len(expression) <= 60`; characters are `{`, `}`, `,`, or
lowercase letters.
