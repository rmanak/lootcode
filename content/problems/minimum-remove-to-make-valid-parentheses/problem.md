`s` consists of `'('`, `')'` and lowercase letters. You may delete parentheses
(at any positions). Return the **minimum number of parentheses you must remove** so
that the remaining string is valid — i.e. every `'('` has a matching later `')'`
and vice versa. (The minimum count is unique even though the resulting string need
not be.)

**Examples**
```
s = "lee(t(c)o)de)"   ->  1     (drop the trailing ')')
s = "a)b(c)d"         ->  1
s = "))(("            ->  4
s = "(a(b(c)d)"       ->  1
```

**Constraints:** `1 <= len(s) <= 10^5`, each character is `'('`, `')'` or a
lowercase letter.
