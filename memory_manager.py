from typing import List

class MemoryManager:
    def __init__(self, max_turns: int = 5):
        """
        Stores last max_turns of conversation.
        max_turns=5 means last 5 user+assistant exchanges kept in memory.
        """
        self.max_turns = max_turns
        self.history = []  # list of {"role": "user/assistant", "content": "..."}

    def add_user_message(self, message: str):
        self.history.append({"role": "user", "content": message})
        self._trim()

    def add_assistant_message(self, message: str):
        self.history.append({"role": "assistant", "content": message})
        self._trim()

    def get_history(self) -> List[dict]:
        return self.history

    def get_history_as_text(self) -> str:
        """Format history as plain text for injecting into LLM prompt"""
        if not self.history:
            return ""
        lines = []
        for msg in self.history:
            role = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def clear(self):
        self.history = []

    def _trim(self):
        """Keep only last max_turns * 2 messages (user + assistant pairs)"""
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]