import numpy as np


class KVCache:
    def __init__(self, dim, maxLen):
        self.dim = dim
        self.max_len = maxLen
        # A ring buffer: once it is full, the next slot to write is the oldest.
        self.keys = np.zeros((maxLen, dim))
        self.values = np.zeros((maxLen, dim))
        self.count = 0                       # entries appended so far, ever

    def append(self, key, value):
        slot = self.count % self.max_len
        self.keys[slot] = key
        self.values[slot] = value
        self.count += 1

    def attend(self, query):
        n = self.size()                      # attention ignores entry order
        scores = self.keys[:n] @ np.asarray(query, dtype=float) / np.sqrt(self.dim)
        weights = np.exp(scores - scores.max())   # every exponent <= 0
        weights /= weights.sum()
        return (weights @ self.values[:n]).tolist()

    def size(self):
        return min(self.count, self.max_len)
