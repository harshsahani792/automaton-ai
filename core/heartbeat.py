import time
from datetime import datetime


class Heartbeat:
    def __init__(self, interval=60):
        self.interval = interval
        self.running = True

    def pulse(self):
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "HEARTBEAT_OK"
        }

    def wait(self):
        time.sleep(self.interval)

    def stop(self):
        self.running = False
