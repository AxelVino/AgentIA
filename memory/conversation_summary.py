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
    
    def load_from_dict(self, saved_data: dict):
        """
        Rellena la estructura base (defaults) solo con los datos que 
        existan en la sesión guardada, evitando borrar nuevas claves.
        """
        if not saved_data:
            return

        for key in self.data.keys():
            if key in saved_data:
                self.data[key] = saved_data[key]

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
        Convierte el summary en texto para el prompt.
        Retorna None si está completamente vacío.
        """ 
        lines = []
        labels = {
            "topics":            "Topics",
            "user_preferences":  "User preferences",
            "games_recommended": "Games already recommended",
            "facts":             "Facts",
            "decisions":         "Decisions",
            "open_questions":    "Open questions",
            "important_context": "Important context",
            "notes":             "Notes",
        }
        for key, label in labels.items():
            value = self.data.get(key)
            if value:  # ignora listas vacías [] y strings vacíos ""
                lines.append(f"{label}: {value}")
        if not lines:
            return None  # nada que inyectar
        return "Conversation memory:\n" + "\n".join(lines)