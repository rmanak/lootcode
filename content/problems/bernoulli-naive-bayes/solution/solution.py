import numpy as np


def bernoulliNaiveBayes(X, y, XTest, alpha):
    X = np.asarray(X, float)
    y = np.asarray(y)
    T = np.asarray(XTest, float)
    classes = np.unique(y)
    scores = []
    for c in classes:
        Xc = X[y == c]
        theta = (Xc.sum(axis=0) + alpha) / (len(Xc) + 2 * alpha)
        ll = T @ np.log(theta) + (1 - T) @ np.log1p(-theta)
        scores.append(np.log(len(Xc) / len(X)) + ll)
    return classes[np.argmax(np.stack(scores, axis=1), axis=1)].tolist()
