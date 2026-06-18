def find132pattern(nums):
    third = float('-inf')
    stack = []
    for x in reversed(nums):
        if x < third:
            return True
        while stack and stack[-1] < x:
            third = stack.pop()
        stack.append(x)
    return False
