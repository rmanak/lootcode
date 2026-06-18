def lengthLongestPath(s):
    maxlen = 0
    depth_len = {0: 0}
    for line in s.split('\n'):
        name = line.lstrip('\t')
        depth = len(line) - len(name)
        if '.' in name:
            maxlen = max(maxlen, depth_len[depth] + len(name))
        else:
            depth_len[depth + 1] = depth_len[depth] + len(name) + 1
    return maxlen
