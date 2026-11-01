class ConversationMemory:
    def __init__(self, maxTokens, placeholderTokens):
        self.maxTokens = maxTokens
        self.placeholderTokens = placeholderTokens
        self.system = []                     # [role, text, tokens], always kept
        self.units = []                      # atomic groups of [role, text, tokens], oldest first

    def add(self, role, text, tokens):
        msg = [role, text, tokens]
        if role == "system":
            self.system.append(msg)
        elif role == "tool":
            self.units[-1].append(msg)       # a tool result travels with the assistant call it answers
        else:
            self.units.append([msg])         # a user message, or an assistant message that opens a group

    def _window(self):
        """(kept units, number of omitted messages)."""
        system_tokens = sum(m[2] for m in self.system)
        if system_tokens + sum(m[2] for u in self.units for m in u) <= self.maxTokens:
            return self.units, 0
        budget = self.maxTokens - system_tokens - self.placeholderTokens
        kept = []
        for unit in reversed(self.units):
            cost = sum(m[2] for m in unit)
            if kept and cost > budget:       # the newest unit is kept unconditionally
                break                        # contiguous: nothing older than a unit that didn't fit
            kept.append(unit)
            budget -= cost
        kept.reverse()
        omitted = sum(len(u) for u in self.units[:len(self.units) - len(kept)])
        return kept, omitted

    def getContext(self):
        kept, omitted = self._window()
        out = [[role, text] for role, text, _ in self.system]
        if omitted:
            noun = "message" if omitted == 1 else "messages"
            out.append(["system", f"[{omitted} earlier {noun} omitted]"])
        out += [[role, text] for unit in kept for role, text, _ in unit]
        return out

    def contextTokens(self):
        kept, omitted = self._window()
        return (sum(m[2] for m in self.system) + sum(m[2] for u in kept for m in u)
                + (self.placeholderTokens if omitted else 0))
