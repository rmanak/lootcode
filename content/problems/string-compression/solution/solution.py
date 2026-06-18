def compress(chars):
    out = []
    i = 0
    n = len(chars)
    while i < n:
        j = i
        while j < n and chars[j] == chars[i]:
            j += 1
        out.append(chars[i])
        if j - i > 1:
            out.append(str(j - i))
        i = j
    return "".join(out)
