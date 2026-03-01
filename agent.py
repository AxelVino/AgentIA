"""Modulo de logica de envio y muestra de mensaje"""
from api import send_message
from memory import create_session, load_session, save_session
from logger import logger

class Assistant():
    """Clase asistente"""
    def __init__ (self, name: str, model: str, system_promp: str) -> None:
        self.name = name
        self.model = model
        self.system_prompt = system_promp

        self.session_file = create_session()
        self.history_context = load_session(self.session_file)

    def add_history(self, role: str, content: str):
        """Agregar contenido a la memoria larga"""
        self.history_context.append({"role": role, "content": content})

        # limito el contexto
        self.history_context = self.history_context[-20:]

        save_session(self.session_file, self.history_context)

    def answer(self, user_message: str) -> None:

        logger.info(f"{self.name} está pensando...")

        self.add_history("user", user_message)

        logger.trace(f"Historial antes del envío: {self.history_context}")

        response = send_message(
            user_message,
            model=self.model,
            system_prompt=self.system_prompt,
            history_context=self.history_context,
            assistant_name=self.name
        )

        logger.trace(f"Respuesta cruda: {response}")

        self.add_history("assistant", response)

        logger.debug(f"Historial final: {self.history_context}")
        