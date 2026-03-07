# Estructura del Proyecto — Agent IA GROQ

Documento técnico que describe la arquitectura modular del proyecto, el rol de cada archivo y el flujo de ejecución completo.

---

## Árbol de Archivos

```
Agent_IA_GROQ/
├── main.py                        # Punto de entrada del programa
├── agent.py                       # Clase Assistant (núcleo lógico)
├── api.py                         # Cliente HTTP hacia la API de Groq (streaming + summary injection)
├── logger.py                      # Sistema de logging con nivel TRACE
├── telemetry.py                   # Medición de rendimiento con datos reales de la API
├── token_guard.py                 # (En desarrollo) Protección contra desbordamiento de tokens
├── test.py                        # Script de pruebas y experimentos
├── requirements.txt               # Dependencias del entorno (versiones fijadas)
├── .env                           # Variables de entorno (no versionado)
├── .gitignore                     # Exclusiones de git
├── agent.log                      # Log rotativo (generado en ejecución)
└── memory/                        # Paquete Python de memoria
    ├── __init__.py                # Re-exporta todos los símbolos del paquete
    ├── memory.py                  # Gestión de sesiones y memoria larga
    ├── conversation_summary.py    # Clase ConversationSummary: memoria comprimida estructurada
    ├── summarizer.py              # Clase Summarizer: compresión de historial vía LLM
    ├── sessions/                  # Sesiones de chat por timestamp
    │   └── session_YYYY-MM-DD_HH-MM-SS.json
    ├── long_memory.json           # Preferencias persistentes del usuario
    └── template_memory.json       # Plantilla base de memoria
```

---

## Descripción de Módulos

### `main.py` — Punto de Entrada

**Responsabilidad:** Inicializar el entorno y ejecutar el loop de chat.

- Lee la variable `MODEL` desde el entorno (`.env`).
- Llama a `choose_session()` para que el usuario seleccione o cree una sesión.
- Instancia la clase `Assistant` con nombre, modelo y system prompt.
- Ejecuta el loop `while True` que captura entradas del usuario y delega en `assistant.answer()`.
- Palabras clave de salida: `salir`, `exit`, `quit`.

---

### `agent.py` — Clase `Assistant`

**Responsabilidad:** Núcleo lógico del asistente. Orquesta memoria, compresión de contexto, API y telemetría.

| Atributo / Método              | Descripción                                                                    |
|--------------------------------|--------------------------------------------------------------------------------|
| `name`                         | Nombre visible del asistente (ej: *Cortana*)                                   |
| `model`                        | Modelo principal de Groq a utilizar                                            |
| `system_prompt`                | Instrucciones de personalidad y restricciones del asistente                    |
| `session_file`                 | Ruta del archivo `.json` de sesión activa                                      |
| `history_context`              | Historial cargado desde la sesión (lista de mensajes)                          |
| `summary`                      | Instancia de `ConversationSummary`: memoria comprimida activa                  |
| `summarizer`                   | Instancia de `Summarizer` usando `llama-3.1-8b-instant`                        |
| `long_memory`                  | Diccionario con datos persistentes cargados de `long_memory.json`              |
| `add_history(role, content)`   | Agrega mensaje al historial, limita a `MAX_HISTORY=20` turnos y persiste       |
| `update_long_memory(text)`     | Detecta frases con "me gusta" y guarda preferencias                            |
| `maybe_summarize()`            | Si el historial supera 12 mensajes, comprime los 6 más antiguos con el Summarizer |
| `answer(user_message)`         | Flujo completo: historial → memoria larga → compresión → API → telemetría      |

**Constante clave:** `MAX_HISTORY = 20` (ventana de contexto enviada a la API).

**Lógica de compresión (`maybe_summarize`):**
```
si len(history) > 12:
    old_chunk = history[:6]
    summary_data = summarizer.summarize(old_chunk, current_summary)
    summary.update(summary_data)
    history = history[6:]   ← los 6 viejos son reemplazados por el summary
```

---

### `api.py` — Cliente HTTP

**Responsabilidad:** Enviar mensajes a la API de Groq con streaming e inyección opcional de summary.

- Endpoint: `https://api.groq.com/openai/v1/chat/completions`
- Método: `POST` con `stream: True` y `stream_options: {"include_usage": True}`
- Construye el payload con `system_prompt`, `summary` (opcional) y `history_context`:
  ```
  messages = [system_prompt] + [summary_system_msg?] + history_context
  ```
- Procesa el stream línea a línea (`iter_lines`):
  - Imprime cada token en tiempo real con un pequeño delay (`time.sleep(0.002)`).
  - Captura el chunk `usage` al final del stream (tokens reales de la API).
  - Limpia el indicador "pensando..." con escape de consola antes del primer token.
- Maneja errores: `Timeout`, `ConnectionError`, `HTTPError`.

**Firma:**
```python
send_message(model, system_prompt, history_context, assistant_name="IA", summary=None)
```

**Retorno:**
```python
{
    "content": str,   # texto completo de la respuesta
    "usage": dict     # datos de uso reales provistos por la API de Groq
}
```

---

### `memory/` — Paquete de Memoria

El directorio `memory/` es un **paquete Python** (contiene `__init__.py`) que centraliza toda la lógica de persistencia y compresión de contexto.

#### `memory/__init__.py`

Re-exporta todos los símbolos del paquete para permitir imports cortos:
```python
from memory import load_session, ConversationSummary, Summarizer
```

#### `memory/memory.py` — Gestión de Sesiones

| Función                       | Descripción                                                              |
|-------------------------------|--------------------------------------------------------------------------|
| `create_session()`            | Crea un nuevo archivo JSON de sesión con timestamp en `memory/sessions/` |
| `load_session(path)`          | Lee y retorna el historial de una sesión desde su archivo JSON           |
| `save_session(path, history)` | Sobreescribe la sesión con el historial actualizado                      |
| `list_sessions()`             | Lista y ordena los archivos de sesión disponibles                        |
| `load_long_memory()`          | Lee `long_memory.json`; retorna `{}` si no existe, está vacío o es JSON inválido |
| `save_long_memory(data)`      | Persiste el diccionario de memoria larga en `long_memory.json`           |

**Directorio de sesiones:** `memory/sessions/`  
**Formato de archivo:** `session_YYYY-MM-DD_HH-MM-SS.json`

#### `memory/conversation_summary.py` — Clase `ConversationSummary`

**Responsabilidad:** Mantener en memoria la representación comprimida y estructurada de la conversación activa.

**Estructura interna (`self.data`):**

| Campo               | Tipo   | Descripción                                            |
|---------------------|--------|--------------------------------------------------------|
| `topics`            | list   | Temas principales de la conversación                   |
| `user_preferences`  | list   | Preferencias detectadas del usuario                    |
| `games_recommended` | list   | Juegos ya recomendados (evita repetición)              |
| `facts`             | list   | Hechos objetivos mencionados                           |
| `decisions`         | list   | Decisiones tomadas durante la conversación             |
| `open_questions`    | list   | Preguntas sin resolver                                 |
| `important_context` | list   | Contexto relevante para el agente                      |
| `notes`             | str    | Notas libres del summarizer                            |

**Métodos:**

| Método          | Descripción                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| `update(dict)`  | Fusiona nuevo resumen: acumula listas sin duplicar, sobreescribe strings    |
| `to_prompt()`   | Formatea `self.data` como texto legible para inyectar en el prompt          |

#### `memory/summarizer.py` — Clase `Summarizer`

**Responsabilidad:** Comprimir un chunk del historial de conversación en JSON estructurado usando un LLM.

- Usa `send_message()` de `api.py` internamente con el modelo configurado.
- Envía el historial a comprimir junto con el resumen existente.
- Retorna un `dict` con el esquema de `ConversationSummary`.
- Incluye `safe_parse()`: si el JSON falla, intenta extraer el bloque `{...}` del texto; si falla de nuevo, retorna un dict vacío con `notes: "summary failed"`.

**Modelo por defecto:** `llama-3.1-8b-instant` (rápido y económico, apropiado para compresión).

---

### `logger.py` — Sistema de Logging

**Responsabilidad:** Proveer un logger centralizado con un nivel `TRACE` personalizado y salida dual.

| Elemento           | Detalle                                                       |
|--------------------|---------------------------------------------------------------|
| Nivel TRACE        | Valor numérico `5` (más detallado que `DEBUG=10`)            |
| Handler de consola | `StreamHandler(sys.stdout)` con encoding UTF-8               |
| Handler de archivo | `RotatingFileHandler` → `agent.log`, máx. 1 MB, 5 backups   |
| Formato            | `HH:MM:SS | LEVEL | mensaje`                                 |
| Configuración      | `LOG_LEVEL` desde `.env` (default: `INFO`)                   |
| Objeto exportado   | `logger` (importado por `agent.py` y `telemetry.py`)         |

---

### `telemetry.py` — Clase `Telemetry`

**Responsabilidad:** Medir y reportar métricas de rendimiento por cada turno de conversación usando datos reales de la API.

| Método                      | Descripción                                                               |
|-----------------------------|---------------------------------------------------------------------------|
| `start()`                   | Registra el tiempo de inicio con `time.time()`                            |
| `stop()`                    | Calcula la duración total desde `start()` en segundos                     |
| `report(response, history)` | Loguea métricas completas usando los datos de `usage` reales de la API    |

---

## Flujo de Ejecución

```
python main.py
    │
    ├── choose_session()             ← Seleccionar o crear sesión
    │       └── memory.memory
    │
    ├── Assistant.__init__()         ← Cargar sesión + memoria larga + inicializar summary
    │       ├── memory.memory
    │       ├── ConversationSummary()
    │       └── Summarizer(model="llama-3.1-8b-instant")
    │
    └── Loop: usuario escribe
            │
            ├── Assistant.answer()
            │       ├── add_history("user", ...)
            │       ├── update_long_memory(...)      ← detecta preferencias
            │       ├── logger.trace (historial)
            │       ├── Telemetry.start()
            │       ├── maybe_summarize()            ← comprime si history > 12
            │       │       ├── Summarizer.summarize(old_chunk, summary)
            │       │       │       └── api.send_message() → LLM compressor
            │       │       └── ConversationSummary.update(summary_data)
            │       ├── api.send_message()           ← streaming a Groq + summary injection
            │       ├── add_history("assistant", ...)
            │       ├── Telemetry.report()           ← log con datos reales de API
            │       └── return response              ← dict {content, usage}
            │
            └── [salir / exit / quit] → fin
```

---

## Diagrama de Dependencias

```
main.py
  ├── agent.py
  │     ├── api.py
  │     ├── memory/
  │     │     ├── __init__.py
  │     │     ├── memory.py
  │     │     ├── conversation_summary.py
  │     │     └── summarizer.py
  │     │           └── api.py
  │     ├── logger.py
  │     └── telemetry.py
  │           └── logger.py
  └── memory/
        └── memory.py
```

---

## Variables de Entorno (`.env`)

| Variable       | Requerida | Descripción                                          | Ejemplo                  |
|----------------|-----------|------------------------------------------------------|--------------------------|
| `GROQ_API_KEY` | ✅ Sí     | Clave de autenticación de la API de Groq             | `gsk_...`                |
| `MODEL`        | ✅ Sí     | Modelo principal (debe existir en Groq)              | `llama3-70b-8192`        |
| `LOG_LEVEL`    | ❌ No     | Nivel del logger (default: `INFO`)                   | `DEBUG`, `TRACE`         |

> **Nota:** El modelo del `Summarizer` está hardcodeado como `llama-3.1-8b-instant` en `agent.py` para mantenerlo rápido y separado del modelo principal.

---

_Documentación actualizada al estado actual del proyecto — 2026-03-06._
