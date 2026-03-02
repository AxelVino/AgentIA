import time
from logger import logger


class Telemetry:

    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.perf_counter()

    def stop(self):
        if self.start_time is None:
            return 0

        duration = time.perf_counter() - self.start_time
        return round(duration, 3)

    @staticmethod
    def estimate_tokens(text: str):

        # aproximación simple (OpenAI ≈ 4 chars/token)
        
        return max(1, len(text) // 4)

    def report(self, response: str, history):
        duration = self.stop()

        tokens = self.estimate_tokens(response)

        logger.info(
            f"Telemetry | ⏱️ {duration}s | 🔢 tokens≈{tokens} | "
            f"📚 mensajes={len(history)}"
        )

        context_size = sum(len(m["content"]) for m in history)

        logger.debug(f"Context size chars={context_size}")