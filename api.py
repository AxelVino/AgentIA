import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

def send_message(user_message):

    """Envía un mensaje a la API de Groq y devuelve la respuesta del agente."""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "Sos una IA especializada en el rubro de alquileres e inmuebles"
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code == 200:
        contenido = response.json()
        return contenido['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"
