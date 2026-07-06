def lengthOfLastWord(s):
    parts = s.split()
    return len(parts[-1]) if parts else 0
