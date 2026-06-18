def removeDuplicateLetters(s):
    from collections import Counter
    remaining = Counter(s)
    stack = []
    seen = set()
    for c in s:
        remaining[c] -= 1
        if c in seen:
            continue
        while stack and stack[-1] > c and remaining[stack[-1]] > 0:
            seen.discard(stack.pop())
        stack.append(c)
        seen.add(c)
    return "".join(stack)
