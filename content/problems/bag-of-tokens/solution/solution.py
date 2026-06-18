def bagOfTokensScore(tokens, P):
    tokens = sorted(tokens)
    lo, hi = 0, len(tokens) - 1
    score = best = 0
    while lo <= hi:
        if P >= tokens[lo]:
            P -= tokens[lo]
            lo += 1
            score += 1
            best = max(best, score)
        elif score > 0:
            P += tokens[hi]
            hi -= 1
            score -= 1
        else:
            break
    return best
