def sumSubarrayMins(A):
    MOD = 10 ** 9 + 7
    n = len(A)
    prev = [-1] * n
    nxt = [n] * n
    stack = []
    for i in range(n):
        while stack and A[stack[-1]] > A[i]:
            stack.pop()
        prev[i] = stack[-1] if stack else -1
        stack.append(i)
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and A[stack[-1]] >= A[i]:
            stack.pop()
        nxt[i] = stack[-1] if stack else n
        stack.append(i)
    res = 0
    for i in range(n):
        res = (res + A[i] * (i - prev[i]) * (nxt[i] - i)) % MOD
    return res % MOD
