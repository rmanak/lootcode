import math


class WeightedMetrics:
    def __init__(self, threshold):
        self.threshold = threshold
        self.reset()

    def reset(self):
        # Running sums over everything seen so far. result() is computed from
        # these, never by averaging per-batch metrics.
        self.tp = self.fp = self.fn = self.tn = 0.0
        self.loss_sum = 0.0
        self.weight = 0.0

    def update(self, scores, labels, weights):
        for p, y, w in zip(scores, labels, weights):
            pred = 1 if p >= self.threshold else 0
            if pred and y:
                self.tp += w
            elif pred:
                self.fp += w
            elif y:
                self.fn += w
            else:
                self.tn += w
            self.loss_sum += w * -(math.log(p) if y else math.log(1.0 - p))
            self.weight += w

    def result(self):
        def div(a, b):
            return a / b if b else 0.0          # 0/0 counts as 0
        return [div(self.tp + self.tn, self.weight), div(self.tp, self.tp + self.fp),
                div(self.tp, self.tp + self.fn), div(self.loss_sum, self.weight)]
