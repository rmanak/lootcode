A row of dominoes is given as a string: `'L'` pushed left, `'R'` pushed right, `'.'`
upright. Each second, a falling domino pushes the adjacent upright one in its
direction; a domino pushed from both sides stays upright. **Return the final
state.**

**Examples**
```
".L.R...LR..L.."  ->  "LL.RR.LLRRLL.."
"RR.L"            ->  "RR.L"
```

**Constraints:** `0 <= len(dominoes) <= 10^5`, characters `L`, `R`, `.`.
