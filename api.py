"""Modulo de solicitudes http"""
import os
import requests
import time
from dotenv import load_dotenv
import json

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")


def send_message(model, context, assistant_name="IA"):

    """Envía un mensaje a la API de Groq y devuelve la respuesta del agente."""

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "stream": True,
        "stream_options": {"include_usage": True},
        "messages": context
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
            stream=True
        )

        response.raise_for_status()

    except requests.exceptions.Timeout:
        return {"content": "⏱️ La IA tardó demasiado en responder.", "usage": None}

    except requests.exceptions.ConnectionError:
        return {"content": "🌐 Error de conexión.", "usage": None}

    except requests.exceptions.HTTPError as e:
        return {"content": f"⚠️ Error API: {e}", "usage": None}

    full_response = ""
    first_token = True
    usage_data = None

    for line in response.iter_lines():

        if not line:
            continue

        decoded = line.decode("utf-8")

        if not decoded.startswith("data: "):
            continue

        data = decoded[6:]

        if data == "[DONE]":
            break

        chunk = json.loads(data)

        # Capturar usage
        if "usage" in chunk:
            usage_data = chunk["usage"]
            continue

        delta = chunk["choices"][0]["delta"]
        content = delta.get("content", "")

        if content:

            if first_token:

                print("\r" + " " * 40 + "\r", end="")
                print(f"🤖 {assistant_name}: ", end="")
                first_token = False

            print(content, end="", flush=True)

            full_response += content

            time.sleep(0.002)

    print()

    return {
        "content": full_response,
        "usage": usage_data
    }