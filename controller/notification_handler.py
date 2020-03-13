from services.Singleton import Singleton
from queue import SimpleQueue

@Singleton
class NotificationHandler:

    def __init__(self):
        self.queue = SimpleQueue()

    def wait(self):
        return self.queue.get(block=True, timeout=None)

    def notify(self, notification):
        self.queue.put(notification)

