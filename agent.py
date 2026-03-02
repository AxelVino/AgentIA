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

MAX_HISTORY = 20

class Assistant():
    #Clase asistente
    def __init__ (self, name: str, model: str, system_promp: str, session_file) -> None:
        self.name = name
        self.model = model
        self.system_prompt = system_promp

        self.session_file = session_file
        self.history_context = load_session(session_file)

        self.long_memory = load_long_memory()

    def add_history(self, role: str, content: str):

        #Agregar contenido a la memoria larga
        self.history_context.append({"role": role, "content": content})

        # limito el contexto
        self.history_context = self.history_context[-MAX_HISTORY:]

        save_session(self.session_file, self.history_context)
    
    def update_long_memory(self, text):

        if "me gusta" in text.lower():
            self.long_memory.setdefault("preferences", []).append(text)
            save_long_memory(self.long_memory)

    def answer(self, user_message: str) -> None:

        telemetry = Telemetry()

        logger.info(f"{self.name} está pensando...")

        self.add_history("user", user_message)

        self.update_long_memory(user_message)
    
        logger.trace(f"Historial antes del envío: {self.history_context}")

        telemetry.start()

        response = send_message(
            user_message,
            model=self.model,
            system_prompt=self.system_prompt,
            history_context=self.history_context,
            assistant_name=self.name
        )

        logger.trace(f"Respuesta cruda: {response}")

        self.add_history("assistant", response)

        telemetry.report(response, self.history_context)  

        logger.debug(f"Historial final: {self.history_context}")