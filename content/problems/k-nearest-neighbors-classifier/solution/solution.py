from collections import Counter

import numpy as np


def knnClassify(trainX, trainY, testX, k):
    A = np.asarray(trainX, dtype=float)       # (N, d)
    index = np.arange(len(A))
    preds = []
    for q in np.asarray(testX, dtype=float):
        dist = ((A - q) ** 2).sum(axis=1)     # squared Euclidean
        # Sort by distance, breaking equal distances by training index.
        nearest = np.lexsort((index, dist))[:k]
        votes = Counter(trainY[i] for i in nearest)
        top = max(votes.values())
        preds.append(min(label for label, c in votes.items() if c == top))
    return preds
