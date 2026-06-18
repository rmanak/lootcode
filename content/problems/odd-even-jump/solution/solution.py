def oddEvenJumps(A):
    n = len(A)

    def make(indices):
        result = [None] * n
        stack = []
        for i in indices:
            while stack and i > stack[-1]:
                result[stack.pop()] = i
            stack.append(i)
        return result

    idx_asc = sorted(range(n), key=lambda i: (A[i], i))
    odd_next = make(idx_asc)
    idx_desc = sorted(range(n), key=lambda i: (-A[i], i))
    even_next = make(idx_desc)

    odd = [False] * n
    even = [False] * n
    odd[n - 1] = even[n - 1] = True
    for i in range(n - 2, -1, -1):
        if odd_next[i] is not None:
            odd[i] = even[odd_next[i]]
        if even_next[i] is not None:
            even[i] = odd[even_next[i]]
    return sum(odd)
