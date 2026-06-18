def spellchecker(wordlist, queries):
    def devowel(w):
        return "".join('*' if c in 'aeiou' else c for c in w.lower())
    exact = set(wordlist)
    cap, vow = {}, {}
    for w in wordlist:
        cap.setdefault(w.lower(), w)
        vow.setdefault(devowel(w), w)
    res = []
    for q in queries:
        if q in exact:
            res.append(q)
        elif q.lower() in cap:
            res.append(cap[q.lower()])
        elif devowel(q) in vow:
            res.append(vow[devowel(q)])
        else:
            res.append("")
    return res
