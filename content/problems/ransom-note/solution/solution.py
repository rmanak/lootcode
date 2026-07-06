def canConstruct(ransomNote, magazine):
    from collections import Counter
    need = Counter(ransomNote)
    have = Counter(magazine)
    return all(have[c] >= n for c, n in need.items())
