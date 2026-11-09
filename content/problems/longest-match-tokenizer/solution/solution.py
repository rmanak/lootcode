def tokenize(text, vocab, unkId, mergeUnk):
    longest = max(len(t) for t in vocab)
    out = []
    i, n = 0, len(text)
    prev_unk = False                  # was the last thing emitted an unknown character?
    while i < n:
        for length in range(min(longest, n - i), 0, -1):    # longest candidate first
            piece = text[i:i + length]
            if piece in vocab:
                out.append(vocab[piece])
                i += length
                prev_unk = False
                break
        else:
            if not (mergeUnk and prev_unk):
                out.append(unkId)
            prev_unk = True
            i += 1
    return out
