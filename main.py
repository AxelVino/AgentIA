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
        "Experto en juegos indies. Reglas: responde claro y profesional, no inventes info, pedí más datos antes de sugerir, no salgas del tema, sé directo.",
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