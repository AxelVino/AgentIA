import time
from logger import logger


class Telemetry:

    def __init__(self):
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time is None:
            return 0
        return round(time.time() - self.start_time, 3)

    def report(self, response: dict, history: list):

        duration = self.stop()

        if not response:
            logger.warning("Telemetry | No response received")
            return

        usage = response.get("usage")

        if not usage:
            logger.warning(
                f"Telemetry | ⏱️ {duration}s | ⚠️ No usage data | "
                f"📚 mensajes={len(history)}"
            )
            return

        logger.info(
            f"Telemetry | "
            f"⏱️ {duration}s | "
            f"🔢 total={usage.get('total_tokens', 0)} | "
            f"📥 prompt={usage.get('prompt_tokens', 0)} | "
            f"📤 completion={usage.get('completion_tokens', 0)} | "
            f"📚 mensajes={len(history)}"
        )

        logger.debug(
            f"Detalles timing | "
            f"queue={usage.get('queue_time', 0):.3f}s | "
            f"prompt_time={usage.get('prompt_time', 0):.3f}s | "
            f"completion_time={usage.get('completion_time', 0):.3f}s | "
            f"total_api_time={usage.get('total_time', 0):.3f}s"
        )

        context_size = sum(len(m["content"]) for m in history)
        logger.debug(f"Context size chars={context_size}")