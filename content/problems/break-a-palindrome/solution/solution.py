def breakPalindrome(palindrome):
    n = len(palindrome)
    if n == 1:
        return ""
    s = list(palindrome)
    for i in range(n // 2):
        if s[i] != 'a':
            s[i] = 'a'
            return "".join(s)
    s[-1] = 'b'
    return "".join(s)
