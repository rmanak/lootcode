def solveIterative(A, b, method, tol, maxIterations):
    n = len(A)
    x = [0.0] * n
    iterations = 0
    while iterations < maxIterations:
        new = list(x)
        for i in range(n):
            # Jacobi reads only the previous iterate; Gauss-Seidel reads entries already updated this sweep.
            src = new if method == "gauss-seidel" else x
            s = sum(A[i][j] * src[j] for j in range(n) if j != i)
            new[i] = (b[i] - s) / A[i][i]
        delta = max(abs(p - q) for p, q in zip(new, x))
        x = new
        iterations += 1
        if delta < tol:
            break
    return [x, iterations]
