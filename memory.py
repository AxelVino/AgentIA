import json
import os
from datetime import datetime

SESSION_DIR = "memory/sessions"

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
        json.dump(history, f, indent=2)