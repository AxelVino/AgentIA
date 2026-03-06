class TokenGuard:

    def __init__(self, max_tokens=6000):
        self.max_tokens = max_tokens

    def estimate_context_tokens(self, history):

        total = 0

        for m in history:
            total += len(m["content"]) // 4

        return total

    def should_summarize(self, history):

        tokens = self.estimate_context_tokens(history)

        return tokens > self.max_tokens