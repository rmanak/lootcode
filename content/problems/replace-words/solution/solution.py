def replaceWords(dictionary, sentence):
    roots = set(dictionary)
    out = []
    for w in sentence.split():
        rep = w
        for i in range(1, len(w) + 1):
            if w[:i] in roots:
                rep = w[:i]
                break
        out.append(rep)
    return " ".join(out)
