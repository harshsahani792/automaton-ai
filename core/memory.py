import json
import os
from datetime import datetime


class Memory:
    def __init__(self, file_path="data/memory.json"):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def load(self):
        with open(self.file_path, "r") as f:
            return json.load(f)

    def remember(self, event, details):
        memories = self.load()

        memories.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "details": details
        })

        with open(self.file_path, "w") as f:
            json.dump(memories, f, indent=2)

    def recent(self, limit=5):
        return self.load()[-limit:]
