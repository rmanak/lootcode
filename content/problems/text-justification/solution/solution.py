def fullJustify(words, maxWidth):
    res = []
    line = []
    length = 0
    for w in words:
        if length + len(line) + len(w) > maxWidth:
            spaces = maxWidth - length
            if len(line) == 1:
                res.append(line[0] + " " * spaces)
            else:
                gaps = len(line) - 1
                base, extra = divmod(spaces, gaps)
                row = ""
                for i, word in enumerate(line):
                    row += word
                    if i < gaps:
                        row += " " * (base + (1 if i < extra else 0))
                res.append(row)
            line = []
            length = 0
        line.append(w)
        length += len(w)
    last = " ".join(line)
    last += " " * (maxWidth - len(last))
    res.append(last)
    return res
