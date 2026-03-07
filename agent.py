#Modulo de logica de envio y muestra de mensaje
from api import send_message
from memory import (
    load_session, 
    save_session, 
    load_long_memory, 
    save_long_memory
)
from logger import logger
from telemetry import Telemetry
from memory.conversation_summary import ConversationSummary
from memory.summarizer import Summarizer
from token_guard import TokenGuard

class Assistant():
    #Clase asistente
    def __init__ (self, name: str, model: str, system_promp: str, session_file) -> None:
        self.name = name
        self.model = model
        self.system_prompt = system_promp

        loaded_data = load_session(session_file) or {} #Si no existe la sesion, devuelve un diccionario vacio 
        self.token_guard = TokenGuard(
            tokenizer_path="tokenizers/llama3_tokenizer.model"
        )
        self.session_file = session_file
        self.history_context = loaded_data.get("history", [])
        self.summary = ConversationSummary()
        self.summary.load_from_dict(loaded_data.get("summary", {}))
        self.summarizer = Summarizer(model="llama-3.1-8b-instant")

        self.long_memory = load_long_memory()

        self.history_threshold = 20
        self.summary_chunk = 8

    def add_history(self, role: str, content: str):

        #Agregar contenido a la memoria larga
        self.history_context.append({"role": role, "content": content})

        save_session(self.session_file, self.history_context, self.summary.data)
    
    def update_long_memory(self, text):

        if "me gusta" in text.lower():
            self.long_memory.setdefault("preferences", []).append(text)
            save_long_memory(self.long_memory)

    def maybe_summarize(self):

        logger.debug(f"Summary actual: {self.summary.data}")

        if len(self.history_context) <= self.history_threshold:
            return

        old_chunk = self.history_context[:self.summary_chunk]

        logger.info("Activando compresión de contexto")

        summary_data = self.summarizer.summarize(
            old_chunk,
            self.summary
        )

        self.summary.update(summary_data)

        #Elimino los mensajes viejos
        self.history_context = self.history_context[self.summary_chunk:]
    
    def maybe_compress(self):

        # DEFENSA 1
        if self.token_guard.should_summarize(
            self.history_context,
            self.summary.to_prompt(),
            self.system_prompt
        ):
            logger.info("TokenGuard activó compresión de history")
            self.maybe_summarize()

        # DEFENSA 2
        if self.token_guard.summary_too_large(
            self.summary.to_prompt()
        ):
            logger.info("Summary demasiado grande, comprimiendo")

            compressed = self.summarizer.compress(
                self.summary.to_prompt()
            )

            self.summary.load_from_dict(compressed)

        # DEFENSA 3
        if self.token_guard.should_trim(
            self.history_context,
            self.summary.to_prompt(),
            self.system_prompt
        ):
            logger.warning("Contexto aún grande, recortando history")

            self.history_context = self.history_context[-10:]

    def answer(self, user_message: str) -> None:

        telemetry = Telemetry()

        logger.info(f"{self.name} está pensando...")

        self.add_history("user", user_message)

        self.maybe_compress()

        print("Historial después de user:", len(self.history_context))

        self.update_long_memory(user_message)
    
        logger.trace(f"Historial antes del envío: {self.history_context}")

        telemetry.start()

        response = send_message(
            model=self.model,
            system_prompt=self.system_prompt,
            history_context=self.history_context,
            assistant_name=self.name,
            summary = self.summary.to_prompt()
        )

        logger.trace(f"Respuesta cruda: {response}")

        print(response["usage"])

        logger.debug(f"Historial final: {self.history_context}")

        # 3️⃣ Solo si hubo respuesta válida, guardar assistant
        if response and response.get("content"):
            self.add_history("assistant", response["content"])
        
        print("Historial después de assistant:", len(self.history_context))

        telemetry.report(response, self.history_context)  

        return response
