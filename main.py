"""Main principal"""
import os
from agent import Assistant

def main():
    """Simulacion de un chat"""
    MODEL = os.getenv("MODEL")
    assistant = Assistant(
        "Cortana",
        MODEL,
        "Eres un asistente con conocimientos en profundidad sobre juegos indies. "
        "Segui estas reglas: "
        "Responde siempre de forma clara y profesional. "
        "No inventes informacion. Si no sabes de algo, indicalo. "
        "Siempre pedi mas informacion antes de sugerir opciones. "
        "No hables de temas que no esten relacionados con los juegos indies. "
        "Se amable pero directo. Evita dar vueltas innecesarias."
    )

    print("🧠 Bienvenido al asistente. Escribí tu mensaje (o 'salir' para terminar).")

    while True:
        user_input = input("\n🧑 Tú: ").strip()

        if user_input.lower() in ["salir", "exit", "quit"]:
            print("👋 ¡Hasta luego!")
            break

        assistant.answer(user_input)


if __name__ == "__main__":
    main()