from langchain_core.chat_history import InMemoryChatMessageHistory


class MemoryStorage:
    def __init__(self):
        self.sessions = {}

    def get_memory(self, session_id: str):

        if session_id not in self.sessions:
            self.sessions[session_id] = InMemoryChatMessageHistory()

        return self.sessions[session_id]


storage = MemoryStorage()
