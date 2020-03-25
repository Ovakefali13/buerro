import queue

from util import Singleton

from services.todoAPI import TodoistService, TodoistJSONRemote
from services.todoAPI.test import TodoistMockRemote
from services.music import MusicService, SpotifyRemote
from services.music.test import MusicMockRemote
from services.cal import CalService, iCloudCaldavRemote
from services.cal.test import CalMockRemote
from services.vvs import VVSService, VVSEfaJSONRemote
from services.vvs.test import VVSMockRemote
from services.preferences import PrefService, PrefRemote

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
        self.running = usecase

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
