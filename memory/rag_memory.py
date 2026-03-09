import json
import os
import time

class RAGMemory:

    def __init__(self, memory_file="memory/memories.json"):
        self.memory_file = memory_file

        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f:
                json.dump([], f)

    def load_memories(self):
        with open(self.memory_file, "r") as f:
            return json.load(f)

    def save_memories(self, memories):
        with open(self.memory_file, "w") as f:
            json.dump(memories, f, indent=2)

    def add_memory(self, content):
        memories = self.load_memories()

        memory = {
            "content": content,
            "timestamp": time.time()
        }

        memories.append(memory)

        self.save_memories(memories)

    def search_memories(self, query, limit=3):
        memories = self.load_memories()

        results = []

        for memory in memories:
            if query.lower() in memory["content"].lower():
                results.append(memory)

        results = sorted(results, key=lambda x: x["timestamp"], reverse=True)

        return results[:limit]