def multiply(mat1, mat2):
    m, n = len(mat1), len(mat2[0])
    # Non-zero entries of each row of mat2, so each useful product is found directly.
    rows2 = [[(j, v) for j, v in enumerate(row) if v] for row in mat2]
    out = [[0] * n for _ in range(m)]
    for i, row in enumerate(mat1):
        acc = out[i]
        for t, a in enumerate(row):
            if a:
                for j, b in rows2[t]:
                    acc[j] += a * b
    return out
