from api import send_message
from logger import logger
from telemetry import Telemetry
from memory.memory_manager import MemoryManager


class Assistant():

    def __init__(self, name, model, system_prompt, session_file):

        self.name = name
        self.model = model

        self.memory = MemoryManager(
            session_file=session_file,
            system_prompt=system_prompt
        )

    def answer(self, user_message):

        telemetry = Telemetry()

        logger.info(f"{self.name} está pensando...")

        telemetry.start()

        self.memory.add_message("user", user_message)

        self.memory.maybe_compress()

        self.memory.update_long_memory(user_message)

        context = self.memory.build_context()

        response = send_message(
            model=self.model,
            context=context,
            assistant_name=self.name
        )

        if response and response.get("content"):

            self.memory.add_message(
                "assistant",
                response["content"]
            )

        telemetry.report(response, context)

        return response