import json
import os
from datetime import datetime

SESSION_DIR = "memory/sessions"
LONG_MEMORY_FILE = "memory/long_memory.json"

def create_session():
    os.makedirs(SESSION_DIR, exist_ok=True)

    session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f"{SESSION_DIR}/session_{session_id}.json"

    with open(path, "w") as f:
        json.dump([], f)

    return path

def load_session(path):
    with open(path, "r") as f:
        return json.load(f)

def save_session(path, history):
    with open(path, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

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