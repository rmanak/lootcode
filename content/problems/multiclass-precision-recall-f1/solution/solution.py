def multiclassReport(yTrue, yPred, numClasses):
    C = numClasses
    tp, pred_n, true_n = [0] * C, [0] * C, [0] * C
    for t, p in zip(yTrue, yPred):
        pred_n[p] += 1
        true_n[t] += 1
        if t == p:
            tp[t] += 1

    def div(a, b):
        return a / b if b else 0.0              # 0/0 counts as 0

    per_class = []
    for c in range(C):
        p, r = div(tp[c], pred_n[c]), div(tp[c], true_n[c])
        per_class.append([p, r, div(2 * p * r, p + r), true_n[c]])
    n = len(yTrue)
    macro = [sum(row[k] for row in per_class) / C for k in range(3)]
    weighted = [sum(row[k] * row[3] for row in per_class) / n for k in range(3)]
    micro_f1 = sum(tp) / n                      # micro P = micro R = micro F1 = accuracy here
    return [per_class, macro, weighted, micro_f1]
