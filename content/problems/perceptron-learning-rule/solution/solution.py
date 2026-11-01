def perceptron(X, y, maxEpochs):
    d = len(X[0])
    w = [0] * d
    b = 0
    mistakes = []
    for _ in range(maxEpochs):
        count = 0
        for xi, yi in zip(X, y):
            if yi * (sum(a * c for a, c in zip(w, xi)) + b) <= 0:   # 0 counts as a mistake
                w = [a + yi * c for a, c in zip(w, xi)]
                b += yi
                count += 1
        mistakes.append(count)
        if count == 0:          # a clean pass: the data is separated, stop
            break
    return [w, b, mistakes]
