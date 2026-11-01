def binaryMetrics(scores, labels, threshold):
    tp = fp = fn = tn = 0
    for s, y in zip(scores, labels):
        pred = 1 if s >= threshold else 0       # a score equal to the threshold is positive
        if pred == 1 and y == 1:
            tp += 1
        elif pred == 1:
            fp += 1
        elif y == 1:
            fn += 1
        else:
            tn += 1

    def div(a, b):
        return a / b if b else 0.0              # 0/0 counts as 0

    precision = div(tp, tp + fp)
    recall = div(tp, tp + fn)
    f1 = div(2 * precision * recall, precision + recall)
    accuracy = (tp + tn) / len(labels)
    return [[tp, fp, fn, tn], precision, recall, f1, accuracy]
