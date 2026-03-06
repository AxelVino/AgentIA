class Summarizer:

    def __init__(self, client, model="gpt-4o-mini"):
        self.client = client
        self.model = model

    def summarize(self, history):

        prompt = f"""
        Compress the following conversation.

        Return JSON with:
        topics
        decisions
        facts
        notes

        Conversation:
        {history}
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return response.choices[0].message.content