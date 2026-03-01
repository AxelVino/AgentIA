# Agent IA GROQ

Un asistente virtual de inteligencia artificial conversacional para la terminal, potenciado por los modelos ultrarrápidos de la API de [Groq](https://groq.com/).

Este proyecto permite iniciar rápidamente una IA con personalidad configurable, soporte para respuestas fluidas (streaming) y un gestor eficiente que guarda cada sesión de chat localmente de forma automática.

## Funcionalidades
- **Respuestas en Streaming:** Experimenta contestaciones en tiempo real sin esperas prolongadas.
- **Historial de Sesiones:** Mantiene el contexto de tus conversaciones mientras limitas los tokens enviados a la API (guarda sesiones en archivos `.json` automáticamente).
- **Sistema Customizado de Persona:** Configura de forma fácil descripciones de sistema (System Prompts) para cambiar el enfoque, restricciones o comportamiento de tu asistente virtual (por defecto configurado como un experto en juegos indie llamado *Cortana*).
- **Logs Profesionales:** Depura las interacciones utilizando la consola o mediante registros pesados localizados en el archivo rotativo `agent.log`.

## Requisitos Previos
1. **Python 3.8 o superior** instalado en tu sistema corporativo o local.
2. Contar con una API_KEY gratuita y válida otorgada por **Groq** ([Consiguela aquí](https://console.groq.com/keys)).

## Instalación

1. Clona el repositorio e ingresa al directorio del proyecto:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd Agent_IA_GROQ
   ```

2. Instala las dependencias necesarias. (Se recomienda realizarlo en un entorno virtual).
   ```bash
   pip install requests python-dotenv
   ```

3. Crea un archivo `.env` en el directorio principal (o utiliza el entorno del sistema) e incluye las siguientes variables:
   ```env
   GROQ_API_KEY=tu_api_key_de_groq_aqui
   MODEL=llama3-70b-8192  # o cualquier modelo disponible en la API de Groq
   LOG_LEVEL=INFO  # Niveles disponibles (TRACE, DEBUG, INFO, WARNING, ERROR)
   ```

## Cómo usar el proyecto

Para iniciar la simulación de chat en la terminal, basta con ejecutar el archivo principal de la aplicación:

```bash
python main.py
```

En la consola, serás recibido por el indicativo del bot y se te permitirá conversar de manera fluida usando el teclado.
- **`🧑 Tú: `**: Es tu línea para proveer entradas.
- **`🤖 <NombreAsistente>: `**: Representa el turno del chatbot, indicando previamente el estado ("pensando...").

Ingresa tu consulta. Para finalizar la conversación, simplemente escribe la palabra reservada `salir`, `exit` o `quit`. En tu directorio `memory/sessions/` encontrarás un historial `.json` listo con toda tu charla en formato estándar para LLMs.

---
_Creado y estructurado bajo los estándares de una IA lista y modular._
