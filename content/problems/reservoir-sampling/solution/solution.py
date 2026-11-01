import math


class ReservoirSampler:
    def __init__(self, k):
        self.k = k
        self.seen = 0
        self.reservoir = []

    def add(self, item, u):
        self.seen += 1
        if self.seen <= self.k:
            self.reservoir.append(item)         # the first k items always go in; u is unused
            return
        j = math.floor(u * self.seen)           # uniform over 0 .. seen - 1
        if j < self.k:
            self.reservoir[j] = item

    def sample(self):
        return list(self.reservoir)
