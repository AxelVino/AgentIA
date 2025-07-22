"""Modulo de logica de envio y muestra de mensaje"""
from api import send_message

class Assistant():
    """Clase asistente"""
    def __init__ (self, name: str, model: str, system_promp: str) -> None:
        self.name = name
        self.model = model
        self.system_prompt = system_promp
        self.history_context = []

    def add_history(self, role: str, content: str):
        """Agregar contenido a la memoria corta"""
        self.history_context.append({"role": role, "content": content})

        if len(self.history_context) > 10:
            self.history_context.pop(0)

    def answer(self, user_message: str) -> None:

        """Aplica logica para enviar el mensaje y como mostrar la respuesta"""

        self.add_history("user", user_message)

        response = send_message(
            user_message,
            model=self.model,
            system_prompt=self.system_prompt,
            history_context=self.history_context
            )
        self.add_history("assistant", response)

        print("\n🤖 respuesta del agente " + self.name + ":\n", response)
