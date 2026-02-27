import json
from pathlib import Path

MEMORY_FILE = Path("memory.json")


def load_memory():
    """Carga memoria desde disco"""
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except:
            return []
    return []


def save_memory(history):
    """Guarda memoria en disco"""
    MEMORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )