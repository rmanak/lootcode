def maxDiff(num):
    s = str(num)
    a = s
    for ch in s:
        if ch != '9':
            a = s.replace(ch, '9')
            break
    if s[0] != '1':
        b = s.replace(s[0], '1')
    else:
        b = s
        for ch in s[1:]:
            if ch != '0' and ch != s[0]:
                b = s.replace(ch, '0')
                break
    return int(a) - int(b)
