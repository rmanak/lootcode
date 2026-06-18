def isValid(code):
    if not code:
        return False
    n = len(code)
    i = 0
    stack = []
    while i < n:
        if code[i] == '<':
            if i + 1 < n and code[i + 1] == '!':
                if not stack:
                    return False
                if code[i:i + 9] != "<![CDATA[":
                    return False
                end = code.find("]]>", i + 9)
                if end == -1:
                    return False
                i = end + 3
            elif i + 1 < n and code[i + 1] == '/':
                end = code.find(">", i)
                if end == -1:
                    return False
                name = code[i + 2:end]
                if not (1 <= len(name) <= 9 and name.isalpha() and name.isupper()):
                    return False
                if not stack or stack[-1] != name:
                    return False
                stack.pop()
                i = end + 1
                if not stack and i < n:
                    return False
            else:
                end = code.find(">", i)
                if end == -1:
                    return False
                name = code[i + 1:end]
                if not (1 <= len(name) <= 9 and name.isalpha() and name.isupper()):
                    return False
                stack.append(name)
                i = end + 1
        else:
            if not stack:
                return False
            i += 1
    return len(stack) == 0
