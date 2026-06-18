def isNumber(s):
    import re
    return re.fullmatch(r'\s*[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?\s*', s) is not None
