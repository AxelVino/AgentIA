"""Modulo de logica de envio y muestra de mensaje"""
import os  
from api import send_message
from memory import load_memory, save_memory
from logger import logger

DEBUG = os.getenv("DEBUG") == "true"

def debug(self, tittle: str, data):
    if DEBUG:
        print(f"\n[DEBUG] {tittle}")
        print(data)

class Assistant():
    """Clase asistente"""
    def __init__ (self, name: str, model: str, system_promp: str) -> None:
        self.name = name
        self.model = model
        self.system_prompt = system_promp
        self.history_context = load_memory()

    def add_history(self, role: str, content: str):
        """Agregar contenido a la memoria larga"""
        self.history_context.append({"role": role, "content": content})
        save_memory(self.history_context)

    def answer(self, user_message: str) -> None:

    logger.info(f"{self.name} está pensando...")

    self.add_history("user", user_message)

    logger.debug(f"Historial antes del envío: {self.history_context}")

    response = send_message(
        user_message,
        model=self.model,
        system_prompt=self.system_prompt,
        history_context=self.history_context
    )

    logger.debug(f"Respuesta del modelo: {response}")

    self.add_history("assistant", response)

    logger.debug(f"Historial final: {self.history_context}")