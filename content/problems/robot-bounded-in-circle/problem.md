A robot starts at `(0,0)` facing north and repeats `instructions` forever: `'G'`
moves forward one unit, `'L'`/`'R'` turn 90 degrees. **Return `true` if the robot
stays within some bounded circle** (it returns to the origin or does not end facing
north after one pass).

**Examples**
```
instructions = "GGLLGG"  ->  true
instructions = "GG"      ->  false
instructions = "GL"      ->  true
```

**Constraints:** `1 <= len(instructions) <= 100`, characters `G`, `L`, `R`.
