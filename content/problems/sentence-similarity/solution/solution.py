def areSentencesSimilarTwo(sentence1, sentence2, pairs):
    if len(sentence1) != len(sentence2):
        return False
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        parent[find(a)] = find(b)
    for w1, w2 in zip(sentence1, sentence2):
        if w1 == w2:
            continue
        if w1 not in parent or w2 not in parent or find(w1) != find(w2):
            return False
    return True
