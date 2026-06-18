def distinctEchoSubstrings(text):
    n = len(text)
    seen = set()
    for i in range(n):
        for length in range(1, (n - i) // 2 + 1):
            half = text[i:i + length]
            if text[i + length:i + 2 * length] == half:
                seen.add(half + half)
    return len(seen)
