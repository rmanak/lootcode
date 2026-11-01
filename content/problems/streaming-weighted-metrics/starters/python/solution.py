class WeightedMetrics:
    def __init__(self, threshold):
        pass

    def update(self, scores, labels, weights):
        """Add a batch: probabilities, 0/1 labels and non-negative weights. Returns nothing."""
        pass

    def result(self):
        """Return [accuracy, precision, recall, logLoss] over everything seen since the last reset."""
        pass

    def reset(self):
        """Forget everything seen so far. Returns nothing."""
        pass
