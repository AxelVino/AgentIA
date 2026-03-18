from logger import logger
from .memory_retrieval import MemoryRetrieval

from memory import (
    load_session,
    save_session,
    load_long_memory,
    save_long_memory
)

from memory.conversation_summary import ConversationSummary
from memory.summarizer import Summarizer
from memory.token_guard import TokenGuard
from memory.embeddings import embedding_fn


class MemoryManager:

    def __init__(self, session_file, system_prompt):

        self.session_file = session_file
        self.system_prompt = system_prompt
        self.memory_retrieval = MemoryRetrieval()
        self.embedding_fn = embedding_fn

        loaded_data = load_session(session_file) or {}

        # Historial reciente
        self.history = loaded_data.get("history", [])

        # Summary persistente
        self.summary = ConversationSummary()
        self.summary.load_from_dict(
            loaded_data.get("summary", {})
        )

        # Long memory
        self.long_memory = load_long_memory()

        # Summarizer
        self.summarizer = Summarizer(
            model="llama-3.1-8b-instant"
        )

        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Token guard
        self.token_guard = TokenGuard(
            tokenizer_path=os.path.join(base_dir, "tokenizers", "tokenizer.model")
        )

        # Configuración
        self.history_threshold = 20
        self.summary_chunk = 8

    # ------------------------------------------------

    def add_message(self, role: str, content: str):

        self.history.append({
            "role": role,
            "content": content
        })

        self.save()

    # ------------------------------------------------

    def update_long_memory(self, text):

        if "me gusta" in text.lower():

            embedding = self.embedding_fn(text)

            memory = {
                "content": text,
                "embedding": embedding,
                "timestamp": time.time(),
                "importance": 0.5
            }

            if memory not in self.long_memory["preferences"]:
                self.long_memory["preferences"].append(memory)

            save_long_memory(self.long_memory)

    # ------------------------------------------------

    def maybe_summarize(self, force=False):

        logger.debug(f"Summary actual: {self.summary.data}")

        if not force and len(self.history) <= self.history_threshold:
            return

        chunk_size = self.summary_chunk

        if len(self.history) <= chunk_size:
            chunk_size = max(1, len(self.history) - 2)

        old_chunk = self.history[:chunk_size]

        logger.info("Activando compresión de contexto")

        summary_data = self.summarizer.summarize(
            old_chunk,
            self.summary
        )

        self.summary.update(summary_data)

        # eliminar mensajes viejos
        self.history = self.history[chunk_size:]

        self.save()

    # ------------------------------------------------

    def maybe_compress(self):

        # DEFENSA 1 — límite de mensajes
        if len(self.history) > self.history_threshold:

            logger.info(
                "Límite de mensajes alcanzado, resumiendo"
            )

            self.maybe_summarize(force=False)

        # DEFENSA 2 — control de tokens
        if self.token_guard.should_summarize(
            self.history,
            self.summary.to_prompt(),
            self.system_prompt
        ):

            logger.info(
                "TokenGuard activó compresión de history"
            )

            self.maybe_summarize(force=True)

        # DEFENSA 3 — summary demasiado grande
        if self.token_guard.summary_too_large(
            self.summary.to_prompt()
        ):

            logger.info("Summary demasiado grande → rolling summary")

            self.rolling_summary()

        # DEFENSA 4 — trim final
        if self.token_guard.should_trim(
            self.history,
            self.summary.to_prompt(),
            self.system_prompt
        ):

            logger.warning(
                "Contexto aún grande, recortando history"
            )

            self.history = self.history[-10:]

            self.save()

    # ------------------------------------------------

    def build_context(self):

        context = []

        # System prompt
        context.append({
            "role": "system",
            "content": self.system_prompt
        })

        # Summary
        summary_prompt = self.summary.to_prompt()

        if summary_prompt:

            context.append({
                "role": "system",
                "content": summary_prompt
            })

        last_user_message = None

        for msg in reversed(self.history):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
                
        if last_user_message:

            relevant_memories = self.retrieve_memories(
                last_user_message,
                embedding_fn=self.embedding_fn
            )

            if relevant_memories:

                memory_block = "\n".join(
                    [m["content"] for m in relevant_memories]
                )

                context.append({
                    "role": "system",
                    "content": f"Relevant long-term memories:\n{memory_block}"
                })

        # Historial
        context.extend(self.history)

        return context

    # ------------------------------------------------

    def save(self):

        save_session(
            self.session_file,
            self.history,
            self.summary.data
        )

    def rolling_summary(self):

        summary_text = self.summary.to_prompt()
        if not summary_text:
            return
        logger.info("Activando rolling summary")
        compressed = self.summarizer.compress(summary_text)
        self.summary.load_from_dict(compressed)
        self.save()

    def retrieve_memories(self, query, embedding_fn, top_k=3):

        memories_dict = self.load_long_memories()

        memories = []

        for category in memories_dict.values():
            memories.extend(category)

        query_embedding = embedding_fn(query)

        scored_memories = []

        for memory in memories:

            memory_embedding = memory["embedding"]

            similarity = self.memory_retrieval.cosine_similarity(
                query_embedding,
                memory_embedding
            )

            recency = 1 / (1 + (time.time() - memory["timestamp"]))

            importance = memory.get("importance", 0.5)

            score = similarity + recency + importance

            scored_memories.append((score, memory))

        scored_memories.sort(key=lambda x: x[0], reverse=True)

        return [m[1] for m in scored_memories[:top_k]]
        