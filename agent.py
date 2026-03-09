from api import send_message
from logger import logger
from telemetry import Telemetry
from memory.memory_manager import MemoryManager
from memory.rag_memory import RAGMemory


class Assistant():

    def __init__(self, name, model, system_prompt, session_file):

        self.name = name
        self.model = model

        self.memory = MemoryManager(
            session_file=session_file,
            system_prompt=system_prompt
        )
        self.rag_memory = RAGMemory()

    def answer(self, user_message):

        telemetry = Telemetry()

        logger.info(f"{self.name} está pensando...")

        telemetry.start()

        self.memory.add_message("user", user_message)

        self.memory.maybe_compress()

        # 🔎 buscar memorias relevantes (RAG)
        memories = self.rag_memory.search_memories(user_message)

        memory_context = "\n".join(
            [m["content"] for m in memories]
        )

        self.memory.update_long_memory(user_message)

        context = self.memory.build_context()

        if memory_context:
            context.insert(1, {
                "role": "system",
                "content": f"Relevant memories about the user:\n{memory_context}"
            })

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
        # guardar memoria nueva
        self.rag_memory.add_memory(user_message)

        telemetry.report(response, context)

        return response