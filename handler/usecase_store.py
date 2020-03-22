import queue

from util import Singleton

@Singleton
class UsecaseStore:
    def __init__(self):
        # TODO Multi-User: by User
        self.usecase_instances = {}
        self.running = None
        self.callback_queue = queue.Queue()

    def get(self, UsecaseCls):
        if UsecaseCls not in self.usecase_instances:
            usecase = UsecaseCls()
            if hasattr(usecase, 'set_scheduler'):
                if not self.scheduler:
                    raise Exception("scheduler must be set")
                usecase.set_scheduler(self.scheduler)
            self.usecase_instances[UsecaseCls] = usecase
        return self.usecase_instances[UsecaseCls]

    def set_running(self, usecase):
        self.running = usecase

    def get_running(self):
        if self.running:
            return self.running
        return None

    def usecase_finished(self):
        self.running = None
        while not self.callback_queue.empty():
            fun, args = self.callback_queue.get()
            fun(*args)

    def register_fin_callback(self, fun, *args):
        self.callback_queue.put((fun, args))

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler
