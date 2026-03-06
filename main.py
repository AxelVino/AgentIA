"""Main principal"""
import os
from agent import Assistant
from memory.memory import list_sessions, create_session

def choose_session():

    sessions = list_sessions()

    print("\n📂 Sesiones disponibles:")

    if sessions:
        for i, s in enumerate(sessions):
            print(f"{i+1}. {s}")

    print("0. Nueva conversación")

    choice = input("\nElegí una opción: ")

    if choice == "0" or not sessions:
        return create_session()

    index = int(choice) - 1
    return f"memory/sessions/{sessions[index]}"

def main():
    """Simulacion de un chat"""
    MODEL = os.getenv("MODEL")

    session_file = choose_session()

    assistant = Assistant(
        "Cortana",
        MODEL,
        "Eres un asistente con conocimientos en profundidad sobre juegos indies. "
        "Segui estas reglas: "
        "Responde siempre de forma clara y profesional. "
        "No inventes informacion. Si no sabes de algo, indicalo. "
        "Siempre pedi mas informacion antes de sugerir opciones. "
        "No hables de temas que no esten relacionados con los juegos indies. "
        "Se amable pero directo. Evita dar vueltas innecesarias.",
        session_file
    )

    print("🧠 Chat iniciado.")

    while True:
        user_input = input("\n🧑 Tú: ").strip()

        if user_input.lower() in ["salir", "exit", "quit"]:
            print("👋 ¡Hasta luego!")
            break

        assistant.answer(user_input)

if __name__ == "__main__":
    main()