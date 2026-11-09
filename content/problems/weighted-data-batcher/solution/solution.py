class DataBatcher:
    def __init__(self, names, weights, batchSize):
        self.names = list(names)
        self.weights = list(weights)
        self.total = sum(weights)
        self.batch_size = batchSize
        self.offsets = [0] * len(names)
        self.current = [0] * len(names)

    def nextBatch(self):
        batch = []
        for _ in range(self.batch_size):
            for d, w in enumerate(self.weights):
                self.current[d] += w
            best = 0
            for d in range(1, len(self.names)):
                if self.current[d] > self.current[best]:      # strict: earliest name wins a tie
                    best = d
            self.current[best] -= self.total
            batch.append(f"{self.names[best]}:{self.offsets[best]}")
            self.offsets[best] += 1
        return batch

    def stateDict(self):
        return [list(self.offsets), list(self.current)]

    def loadStateDict(self, state):
        self.offsets = list(state[0])
        self.current = list(state[1])
