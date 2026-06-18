def generateParenthesis(n):
    res = []

    def bt(s, opened, closed):
        if len(s) == 2 * n:
            res.append(s)
            return
        if opened < n:
            bt(s + "(", opened + 1, closed)
        if closed < opened:
            bt(s + ")", opened, closed + 1)

    bt("", 0, 0)
    return res
