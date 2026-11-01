class ConversationMemory:
    def __init__(self, maxTokens, placeholderTokens):
        pass

    def add(self, role, text, tokens):
        """Append a message ("system", "user", "assistant" or "tool"). Returns nothing."""
        pass

    def getContext(self):
        """Return the [role, text] messages that go into the next model call, oldest first."""
        pass

    def contextTokens(self):
        """Return the total token cost of getContext()."""
        pass
