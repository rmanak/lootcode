There are `n` engineers; engineer `i` has `speed[i]` and `efficiency[i]`. A team's
performance is `(sum of its members' speeds) * (minimum efficiency among them)`.
Choose **at most `k`** engineers to **maximize performance**; return it modulo
`10^9 + 7`.

**Examples**
```
n=6, speed=[2,10,3,1,5,8], efficiency=[5,4,3,9,7,2], k=2  ->  60   ((10+5)*4)
n=6, speed=[2,10,3,1,5,8], efficiency=[5,4,3,9,7,2], k=3  ->  68   ((2+10+5)*4)
n=6, speed=[2,10,3,1,5,8], efficiency=[5,4,3,9,7,2], k=4  ->  72
```

**Constraints:** `1 <= n <= 10^5`, `1 <= speed[i] <= 10^5`,
`1 <= efficiency[i] <= 10^8`, `1 <= k <= n`. (Take the max before applying the
modulo.)
