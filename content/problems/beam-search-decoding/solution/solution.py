def beamSearch(logProbs, startToken, eosToken, beamWidth, maxLen):
    vocab = len(logProbs)
    live = [((), 0.0)]          # (generated tokens, score); the start token isn't stored
    finished = []
    for _ in range(maxLen):
        candidates = []
        for seq, score in live:
            row = logProbs[seq[-1] if seq else startToken]
            for t in range(vocab):
                # Extend left to right, one addition per token, so the score
                # is the same float however the beam got there.
                candidates.append((seq + (t,), score + row[t]))
        # Best score first; equal scores in lexicographic order of the tokens.
        candidates.sort(key=lambda c: (-c[1], c[0]))
        live = []
        for seq, score in candidates[:beamWidth]:
            (finished if seq[-1] == eosToken else live).append((seq, score))
        if not live:
            break
    finished.extend(live)       # beams cut off by maxLen count as finished too
    seq, score = min(finished, key=lambda c: (-c[1], c[0]))
    return [list(seq), score]
