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
            usecase.set_default_services()
            if hasattr(usecase, 'set_scheduler'):
                if not self.scheduler:
                    raise Exception("scheduler must be set")
                usecase.set_scheduler(self.scheduler)
            self.usecase_instances[UsecaseCls] = usecase
        return self.usecase_instances[UsecaseCls]

    def set_running(self, usecase):
        stored_instance = self.usecase_instances.get(type(usecase), None)
        if stored_instance and stored_instance != usecase:
            raise Exception(("Two separate instances detected. "
                            f"{stored_instance} != {usecase}"))
        self.running = usecase
        self.usecase_instances[type(usecase)] = usecase

    def get_running(self):
        if self.running:
            return self.running
        return None

    def usecase_finished(self):
        self.running = None
        while not self.callback_queue.empty():
            fun, arg_dict = self.callback_queue.get()
            args = arg_dict['args']
            kwargs = arg_dict['kwargs']
            fun(*args, **kwargs)

    def register_fin_callback(self, fun, *args, **kwargs):
        arg_dict = {
            'args': args,
            'kwargs': kwargs
        }
        self.callback_queue.put((fun, arg_dict))

    def set_scheduler(self, scheduler):
        self.scheduler = scheduler

    def purge(self):
        self.__init__()
