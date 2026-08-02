class MaxStack:
    def __init__(self):
        self.stack = []
        # maxes[i] is the maximum of stack[0..i], so maxes[-1] is the current max.
        self.maxes = []

    def push(self, x):
        self.stack.append(x)
        self.maxes.append(x if not self.maxes else max(x, self.maxes[-1]))

    def pop(self):
        self.maxes.pop()
        return self.stack.pop()

    def top(self):
        return self.stack[-1]

    def peekMax(self):
        return self.maxes[-1]

    def popMax(self):
        m = self.maxes[-1]
        buf = []
        while self.stack[-1] != m:
            buf.append(self.pop())
        self.pop()
        while buf:
            self.push(buf.pop())
        return m
