def minIncrementForUnique(A):
    A = sorted(A)
    moves = 0
    prev = None
    for x in A:
        if prev is not None and x <= prev:
            need = prev + 1
            moves += need - x
            prev = need
        else:
            prev = x
    return moves
