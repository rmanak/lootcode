import numpy as np


def gaussianNaiveBayes(X, y, XTest):
    X = np.asarray(X, float)
    y = np.asarray(y)
    T = np.asarray(XTest, float)
    classes = np.unique(y)                       # ascending, so argmax's first hit is the smaller label
    scores = []
    for c in classes:
        Xc = X[y == c]
        mu = Xc.mean(axis=0)
        var = ((Xc - mu) ** 2).mean(axis=0) + 1e-9
        ll = -0.5 * np.log(2 * np.pi * var) - (T - mu) ** 2 / (2 * var)
        scores.append(np.log(len(Xc) / len(X)) + ll.sum(axis=1))
    return classes[np.argmax(np.stack(scores, axis=1), axis=1)].tolist()
