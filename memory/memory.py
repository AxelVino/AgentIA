import json
import os
from datetime import datetime

SESSION_DIR = "memory/sessions"
LONG_MEMORY_FILE = "memory/long_memory.json"

def create_session():
    os.makedirs(SESSION_DIR, exist_ok=True)

    session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f"{SESSION_DIR}/session_{session_id}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "history": [],
                "summary": {}
            },
            f,
            indent=2,
            ensure_ascii=False
        )

    return path

def load_session(path):

    if not os.path.exists(path): #Si no existe la sesion, devuelve un diccionario vacio
        return {"history": [], "summary": {}}

    with open(path, "r", encoding="utf-8") as f: #Abro el archivo en modo lectura
        data = json.load(f)

    # compatibilidad con sesiones viejas
    if isinstance(data, list): #Si el archivo es una lista, lo convierto a diccionario
        return {"history": data, "summary": {}}

    return data

def save_session(path, history, summary):

    #Persisto el summary junto con el historial en cada sesion
    session_data = {
        "history": history,
        "summary": summary,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

def list_sessions():
    if not os.path.exists(SESSION_DIR):
        return []

    files = os.listdir(SESSION_DIR)
    return sorted(files)

def load_long_memory():

    if not os.path.exists(LONG_MEMORY_FILE):
        return {}

    try:
        with open(LONG_MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()

            if not content:   # ← archivo vacío
                return {}

            return json.loads(content)

    except json.JSONDecodeError:
        return {}

def save_long_memory(data):
    os.makedirs("memory", exist_ok=True)

    with open(LONG_MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def trim_history(history):

    MAX_HISTORY = 10

    return history[-MAX_HISTORY:]