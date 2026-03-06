class ConversationSummary:
    """
    Representa la memoria comprimida de la conversación.
    """

    def __init__(self):
        self.data = {
            "topics": [],
            "user_preferences": [],
            "games_recommended": [], #Esto se puede modificar dependiendo de la especialidad del agente
            "facts": [],
            "decisions": [],
            "open_questions": [],
            "important_context": [],
            "notes": ""
        }

    def update(self, new_data: dict):
        """
        Fusiona nueva información del summarizer con la existente.
        """

        for key, value in new_data.items():

            if key not in self.data:
                continue

            if isinstance(self.data[key], list):
                for item in value:
                    if item not in self.data[key]:
                        self.data[key].append(item)

            elif isinstance(self.data[key], str):
                if value:
                    self.data[key] = value

    def to_prompt(self):
        """
        Convierte el summary en texto que el modelo pueda entender.
        """

        return f"""
Conversation memory:

Topics: {self.data['topics']}
User preferences: {self.data['user_preferences']}
Games already recommended: {self.data['games_recommended']}
Facts: {self.data['facts']}
Decisions: {self.data['decisions']}
Open questions: {self.data['open_questions']}
Important context: {self.data['important_context']}
Notes: {self.data['notes']}
"""