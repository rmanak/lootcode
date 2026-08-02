class AutocompleteSystem:
    def __init__(self, k):
        self.k = k
        self.freq = {}

    def add(self, sentence, count):
        self.freq[sentence] = self.freq.get(sentence, 0) + count

    def query(self, prefix):
        cands = [s for s in self.freq if s.startswith(prefix)]
        cands.sort(key=lambda s: (-self.freq[s], s))
        return cands[:self.k]
