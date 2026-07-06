def plusOne(digits):
    n = int("".join(map(str, digits))) + 1
    return [int(c) for c in str(n)]
