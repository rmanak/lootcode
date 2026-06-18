def minAddToMakeValid(s):
    open_ = 0
    add = 0
    for c in s:
        if c == '(':
            open_ += 1
        elif open_ > 0:
            open_ -= 1
        else:
            add += 1
    return add + open_
