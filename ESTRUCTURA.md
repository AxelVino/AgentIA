# Estructura del Proyecto — Agent IA GROQ

Documento técnico que describe la arquitectura modular del proyecto, el rol de cada archivo y el flujo de ejecución completo.

---

## Árbol de Archivos

```
Agent_IA_GROQ/
├── main.py                        # Punto de entrada del programa
├── agent.py                       # Clase Assistant (núcleo lógico)
├── api.py                         # Cliente HTTP hacia la API de Groq
├── memory.py                      # Gestión de sesiones y memoria larga
├── logger.py                      # Sistema de logging con nivel TRACE
├── telemetry.py                   # Medición de rendimiento por turno
├── requirements.txt               # Dependencias del entorno
├── .env                           # Variables de entorno (no versionado)
├── .gitignore                     # Exclusiones de git
├── agent.log                      # Log rotativo (generado en ejecución)
└── memory/
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

**Responsabilidad:** Núcleo lógico del asistente. Orquesta la memoria, la API y la telemetría.

| Atributo / Método        | Descripción                                                        |
|--------------------------|--------------------------------------------------------------------|
| `name`                   | Nombre visible del asistente (ej: *Cortana*)                       |
| `model`                  | Modelo de Groq a utilizar                                          |
| `system_prompt`          | Instrucciones de personalidad y restricciones del asistente        |
| `session_file`           | Ruta del archivo `.json` de sesión activa                          |
| `history_context`        | Historial cargado desde la sesión (lista de mensajes)              |
| `long_memory`            | Diccionario con datos persistentes cargados de `long_memory.json`  |
| `add_history(role, content)` | Agrega mensaje al historial, limita a `MAX_HISTORY=20` turnos y persiste |
| `update_long_memory(text)` | Detecta frases con "me gusta" y guarda preferencias                |
| `answer(user_message)`   | Flujo completo: telemetría → API → historial → log                 |

**Constante clave:** `MAX_HISTORY = 20` (ventana de contexto enviada a la API).

---

### `api.py` — Cliente HTTP

**Responsabilidad:** Enviar mensajes a la API de Groq y devolver la respuesta en modo streaming.

- Endpoint: `https://api.groq.com/openai/v1/chat/completions`
- Método: `POST` con `stream: True`
- Construye el payload con `system_prompt`, el `history_context` y el mensaje actual del usuario.
- Procesa el stream línea a línea (`iter_lines`), imprime cada token en tiempo real y acumula la respuesta completa.
- Limpia el indicador "pensando..." con escape de consola antes del primer token.
- Maneja errores: `Timeout`, `ConnectionError`, `HTTPError`.

---

### `memory.py` — Gestión de Memoria

**Responsabilidad:** Persistir el historial de sesiones y la memoria de largo plazo.

| Función                   | Descripción                                                         |
|---------------------------|---------------------------------------------------------------------|
| `create_session()`        | Crea un nuevo archivo JSON de sesión con timestamp en `memory/sessions/` |
| `load_session(path)`      | Lee y retorna el historial de una sesión desde su archivo JSON      |
| `save_session(path, history)` | Sobreescribe la sesión con el historial actualizado            |
| `list_sessions()`         | Lista y ordena los archivos de sesión disponibles                   |
| `load_long_memory()`      | Lee `long_memory.json`; retorna `{}` si no existe o está vacío      |
| `save_long_memory(data)`  | Persiste el diccionario de memoria larga en `long_memory.json`      |

**Directorio de sesiones:** `memory/sessions/`  
**Formato de archivo:** `session_YYYY-MM-DD_HH-MM-SS.json`

---

### `logger.py` — Sistema de Logging

**Responsabilidad:** Proveer un logger centralizado con un nivel `TRACE` personalizado y salida dual.

**Configuración:**

| Elemento              | Detalle                                            |
|-----------------------|----------------------------------------------------|
| Nivel TRACE           | Valor numérico `5` (más detallado que `DEBUG=10`) |
| Handler de consola    | `StreamHandler(sys.stdout)` con encoding UTF-8     |
| Handler de archivo    | `RotatingFileHandler` → `agent.log`, máx. 1 MB, 5 backups |
| Formato               | `HH:MM:SS | LEVEL | mensaje`                      |
| Configuración         | `LOG_LEVEL` desde `.env` (default: `INFO`)         |
| Objeto exportado      | `logger` (importado por `agent.py` y `telemetry.py`) |

**Niveles disponibles (de mayor a menor detalle):**

```
TRACE → DEBUG → INFO → WARNING → ERROR
```

---

### `telemetry.py` — Clase `Telemetry`

**Responsabilidad:** Medir y reportar métricas de rendimiento por cada turno de conversación.

| Método                        | Descripción                                               |
|-------------------------------|-----------------------------------------------------------|
| `start()`                     | Registra el tiempo de inicio con `time.perf_counter()`    |
| `stop()`                      | Calcula la duración desde `start()` en segundos           |
| `estimate_tokens(text)`       | Aproxima tokens: `len(text) // 4` (estándar OpenAI ≈ 4 chars/token) |
| `report(response, history)`   | Loguea en `INFO`: duración, tokens estimados y cant. de mensajes. En `DEBUG`: tamaño total del contexto en caracteres |

---

## Flujo de Ejecución

```
python main.py
    │
    ├── choose_session()          ← Seleccionar o crear sesión
    │       └── memory.py
    │
    ├── Assistant.__init__()      ← Cargar sesión + memoria larga
    │       └── memory.py
    │
    └── Loop: usuario escribe
            │
            ├── Assistant.answer()
            │       ├── Telemetry.start()
            │       ├── add_history("user", ...)
            │       ├── update_long_memory(...)   ← detecta preferencias
            │       ├── api.send_message()        ← streaming a Groq
            │       ├── add_history("assistant", ...)
            │       └── Telemetry.report()        ← log de rendimiento
            │
            └── [salir / exit / quit] → fin
```

---

## Diagrama de Dependencias

```
main.py
  ├── agent.py
  │     ├── api.py
  │     ├── memory.py
  │     ├── logger.py
  │     └── telemetry.py
  │           └── logger.py
  └── memory.py
```

---

## Variables de Entorno (`.env`)

| Variable       | Requerida | Descripción                                             | Ejemplo                |
|----------------|-----------|---------------------------------------------------------|------------------------|
| `GROQ_API_KEY` | ✅ Sí     | Clave de autenticación de la API de Groq                | `gsk_...`              |
| `MODEL`        | ✅ Sí     | Modelo a usar (debe existir en Groq)                    | `llama3-70b-8192`      |
| `LOG_LEVEL`    | ❌ No     | Nivel del logger (default: `INFO`)                      | `DEBUG`, `TRACE`       |

---

_Documentación generada en base al estado actual del proyecto._
