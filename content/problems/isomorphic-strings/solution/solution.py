def isIsomorphic(s, t):
    if len(s) != len(t):
        return False
    st, ts = {}, {}
    for a, b in zip(s, t):
        if a in st and st[a] != b:
            return False
        if b in ts and ts[b] != a:
            return False
        st[a] = b
        ts[b] = a
    return True
