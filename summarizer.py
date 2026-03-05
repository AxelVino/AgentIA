class ConversationSummary:

    def __init__(self):
        self.data = {
            "topics": [],
            "decisions": [],
            "facts": [],
            "notes": ""
        }

    def update(self, new_data: dict):

        for key in self.data:
            if key in new_data:

                if isinstance(self.data[key], list):
                    self.data[key].extend(new_data[key])

                elif isinstance(self.data[key], str):
                    self.data[key] += " " + new_data[key]

    def as_message(self):

        return {
            "role": "system",
            "content": f"Conversation summary: {self.data}"
        }