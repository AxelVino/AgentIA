import time


class MemoryRetrieval:

    def __init__(self):
        pass

    def score_memory(self, memory, query_embedding, embedding_fn):

        memory_embedding = embedding_fn(memory["content"])

        similarity = self.cosine_similarity(
            query_embedding,
            memory_embedding
        )

        recency = 1 / (1 + (time.time() - memory["timestamp"]))

        importance = memory.get("importance", 0.5)

        score = similarity + recency + importance

        return score

    def cosine_similarity(self, a, b):

        dot = sum(x*y for x, y in zip(a, b))

        norm_a = sum(x*x for x in a) ** 0.5
        norm_b = sum(x*x for x in b) ** 0.5

        return dot / (norm_a * norm_b)