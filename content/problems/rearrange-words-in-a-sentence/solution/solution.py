def arrangeWords(text):
    words = text.lower().split()
    words.sort(key=len)
    res = " ".join(words)
    return res[:1].upper() + res[1:]
