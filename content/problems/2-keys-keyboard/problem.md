A notepad starts with a single `'A'`. Each step is either **Copy All** (copy the
entire current contents) or **Paste** (append the last copied contents). **Return
the minimum number of steps** to make the notepad contain exactly `n` copies of
`'A'`. (The answer is the sum of the prime factors of `n`.)

**Examples**
```
n = 1  ->  0
n = 3  ->  3   (Copy All, Paste, Paste)
n = 6  ->  5   (A -> AA in 2 steps, then -> AAAAAA in 3)
```

**Constraints:** `1 <= n <= 1000`.
