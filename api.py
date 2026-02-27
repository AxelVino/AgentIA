"""Modulo de solicitudes http"""
import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

def send_message(user_message, model, system_prompt, history_context):

    """Envía un mensaje a la API de Groq y devuelve la respuesta del agente."""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "stream": True,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            *history_context,
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30, stream=True)
    
    fullResponse = ""
    first_token = True

    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")

            if decoded.startswith("data: "):
                data = decoded[6:]

            if data == "[DONE]":
                break

            import json
            chunk = json.loads(data)

            content = chunk["choices"][0]["delta"].get("content", "")
            if first_token:
                print("\r" + " " * 40 + "\r", end="")  # borra el "pensando..."
                first_token = False
            print(content, end="", flush=True)
            fullResponse += content
            time.sleep(0.01)
    print()
    return fullResponse
