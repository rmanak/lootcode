def padBatch(sequences, padId, side, padToMultipleOf):
    longest = max(len(s) for s in sequences)
    m = padToMultipleOf
    L = -(-longest // m) * m                   # round up to a multiple of m
    ids, mask, pos, causal = [], [], [], []
    for s in sequences:
        n = len(s)
        pad = L - n
        # The mask comes from the lengths, never from comparing ids to padId:
        # padId can also be a real token.
        if side == "right":
            row_ids = list(s) + [padId] * pad
            row_mask = [1] * n + [0] * pad
        else:
            row_ids = [padId] * pad + list(s)
            row_mask = [0] * pad + [1] * n
        row_pos, k = [], 0
        for bit in row_mask:
            row_pos.append(k if bit else 0)
            k += bit
        ids.append(row_ids)
        mask.append(row_mask)
        pos.append(row_pos)
        causal.append([[1 if (j <= i and row_mask[i] and row_mask[j]) else 0 for j in range(L)]
                       for i in range(L)])
    return [ids, mask, pos, causal]
