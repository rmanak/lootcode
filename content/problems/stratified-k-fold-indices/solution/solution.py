def stratifiedKFold(labels, k, perm):
    position = {idx: pos for pos, idx in enumerate(perm)}       # where each index lands in the shuffle
    by_class = {}
    for idx, lab in enumerate(labels):
        by_class.setdefault(lab, []).append(idx)
    folds = [[] for _ in range(k)]
    f = 0                                                       # the deal continues across classes
    for lab in sorted(by_class):
        for idx in sorted(by_class[lab], key=position.__getitem__):
            folds[f].append(idx)
            f = (f + 1) % k
    return [sorted(fold) for fold in folds]
