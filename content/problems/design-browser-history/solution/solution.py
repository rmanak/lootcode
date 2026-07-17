class BrowserHistory:
    def __init__(self, homepage):
        self.history = [homepage]
        self.cur = 0

    def visit(self, url):
        # Visiting from the current page clears all forward history.
        del self.history[self.cur + 1:]
        self.history.append(url)
        self.cur += 1

    def back(self, steps):
        self.cur = max(0, self.cur - steps)
        return self.history[self.cur]

    def forward(self, steps):
        self.cur = min(len(self.history) - 1, self.cur + steps)
        return self.history[self.cur]
