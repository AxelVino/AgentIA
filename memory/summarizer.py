import json
from api import send_message
from logger import logger


class Summarizer:

    def __init__(self, model):
        self.model = model

    def summarize(self, history_chunk, current_summary):

        prompt = f"""
You are a conversation compression system.

Your task is to summarize the conversation history into structured JSON.

Return ONLY valid JSON.

Schema:

{{
 "topics": [],
 "user_preferences": [],
 "games_recommended": [],
 "facts": [],
 "decisions": [],
 "open_questions": [],
 "important_context": [],
 "notes": ""
}}

Existing summary:
{json.dumps(current_summary.data, indent=2)}

Conversation to compress:
{json.dumps(history_chunk, indent=2)}

Return JSON only.
"""

        response = send_message(
            model=self.model,
            system_prompt="You compress conversations into structured memory.",
            history_context=[],
            assistant_name="Summarizer",
            user_message=prompt
        )

        text = response["content"]

        parsed = self.safe_parse(text)

        return parsed
    
    def safe_parse(self, text):

        try:
            return json.loads(text)

        except json.JSONDecodeError:

            logger.warning("Summary JSON inválido, intentando reparación")

            start = text.find("{")
            end = text.rfind("}") + 1

            if start != -1 and end != -1:

                try:
                    return json.loads(text[start:end])
                except:
                    pass

            logger.error("No se pudo parsear summary")

            return {
                "topics": [],
                "user_preferences": [],
                "games_recommended": [],
                "facts": [],
                "decisions": [],
                "open_questions": [],
                "important_context": [],
                "notes": "summary failed"
            }