# Agent IA GROQ

Un asistente virtual de inteligencia artificial conversacional para la terminal, potenciado por los modelos ultrarrápidos de la API de [Groq](https://groq.com/).

Este proyecto permite iniciar rápidamente una IA con personalidad configurable, soporte para respuestas fluidas (streaming), memoria de sesión y largo plazo, telemetría de rendimiento y un sistema de logs profesional con nivel TRACE personalizado.

## Funcionalidades

- **Respuestas en Streaming:** Experimenta contestaciones en tiempo real sin esperas prolongadas, con limpieza automática del indicador "pensando...".
- **Selección de Sesión:** Al iniciar, podés elegir retomar una conversación anterior o comenzar una nueva. Las sesiones se guardan automáticamente en `memory/sessions/` como archivos `.json`.
- **Memoria de Largo Plazo:** El asistente detecta preferencias del usuario en tiempo real (ej: frases con "me gusta") y las persiste en `memory/long_memory.json` entre sesiones.
- **Sistema Customizado de Persona:** Configura fácilmente el System Prompt (por defecto, un experto en juegos indie llamado *Cortana*) para cambiar el enfoque, restricciones o comportamiento del asistente.
- **Telemetría Integrada:** Cada respuesta registra el tiempo de respuesta, la cantidad aproximada de tokens generados y el tamaño del historial activo.
- **Logger Profesional con Nivel TRACE:** Sistema de logs con nivel `TRACE` personalizado (más detallado que `DEBUG`). Salida doble: consola con UTF-8 y archivo rotativo `agent.log` (máx. 1 MB, 5 backups). Niveles configurables vía variable de entorno.

## Estructura del Proyecto

```
Agent_IA_GROQ/
├── main.py            # Punto de entrada: selección de sesión e inicio del chat
├── agent.py           # Clase Assistant: lógica de historial, memoria y respuesta
├── api.py             # Cliente HTTP hacia la API de Groq (streaming)
├── memory.py          # Gestión de sesiones y memoria de largo plazo
├── logger.py          # Logger con nivel TRACE, handlers de consola y archivo rotativo
├── telemetry.py       # Medición de tiempo, tokens estimados y tamaño de contexto
├── requirements.txt   # Dependencias del proyecto
├── .env               # Variables de entorno (no incluido en el repositorio)
├── agent.log          # Archivo de log rotativo (generado en ejecución)
└── memory/
    ├── sessions/      # Archivos JSON de sesiones de chat
    ├── long_memory.json      # Preferencias y datos persistentes del usuario
    └── template_memory.json  # Plantilla base para la memoria
```

## Requisitos Previos

1. **Python 3.8 o superior** instalado en tu sistema.
2. Una API Key gratuita y válida de **Groq** ([Consíguela aquí](https://console.groq.com/keys)).

## Instalación

1. Clona el repositorio e ingresa al directorio del proyecto:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd Agent_IA_GROQ
   ```

2. Crea y activa un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Crea un archivo `.env` en el directorio principal con las siguientes variables:
   ```env
   GROQ_API_KEY=tu_api_key_de_groq_aqui
   MODEL=llama3-70b-8192       # o cualquier modelo disponible en Groq
   LOG_LEVEL=INFO              # Niveles: TRACE, DEBUG, INFO, WARNING, ERROR
   ```

## Cómo Usar el Proyecto

Ejecuta el archivo principal:

```bash
python main.py
```

Al arrancar, verás el selector de sesiones:

```
📂 Sesiones disponibles:
1. session_2025-01-15_10-30-00.json
2. session_2025-01-16_14-22-11.json
0. Nueva conversación

Elegí una opción:
```

- **`🧑 Tú:`** — Tu línea para escribir mensajes.
- **`🤖 Cortana:`** — Respuesta del asistente en tiempo real (streaming).

Para salir, escribí `salir`, `exit` o `quit`.

## Niveles de Log

El sistema de logs acepta los siguientes niveles configurables vía `LOG_LEVEL` en `.env`:

| Nivel   | Detalle                                                       |
|---------|---------------------------------------------------------------|
| `TRACE` | Historial completo, respuesta cruda de la API (máx. detalle) |
| `DEBUG` | Historial final tras cada turno, tamaño del contexto          |
| `INFO`  | Estado del asistente, telemetría de rendimiento               |
| `WARNING` | Advertencias del sistema                                   |
| `ERROR` | Errores críticos                                              |

## Dependencias Principales

| Paquete         | Uso                                              |
|-----------------|--------------------------------------------------|
| `groq`          | SDK oficial de Groq para consultas a la API      |
| `requests`      | Cliente HTTP para streaming con la API de Groq   |
| `python-dotenv` | Carga de variables de entorno desde `.env`       |
| `pydantic`      | Validación de datos (requerida por el SDK groq)  |

---
_Creado y estructurado bajo los estándares de una IA lista y modular._
