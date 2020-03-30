from controller import ControllerFromArgs
from chatbot import Chatbot, BuerroBot
from http.server import HTTPServer
from datetime import datetime
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from usecase import Lunchbreak
from usecase import Github
from handler import UsecaseStore

HOST_NAME = "localhost"
SERVER_PORT = 9150

if 'BACKEND_PORT' in os.environ:
    SERVER_PORT = int(os.environ['BACKEND_PORT'])

class Main:

    def __init__(self):
        self.store = UsecaseStore.instance()

        self.scheduler = BackgroundScheduler(timezone=utc)
        self.schedule_usecases()

        self.chatbot = Chatbot(BuerroBot())

        Controller = ControllerFromArgs(self.scheduler, self.chatbot)
        self.httpd = HTTPServer((HOST_NAME, SERVER_PORT),
            Controller)

    def block_trigger(self, usecase, func, *args, **kwargs):
        running_usecase = self.store.get_running()
        if running_usecase:
            if not running_usecase == usecase:
                self.store.register_fin_callback(func, *args, **kwargs)
        else:
            func(*args, **kwargs)

    def schedule_usecases(self):
        lunchbreak = self.store.get(Lunchbreak)
        lunchbreak.set_default_services()
        self.scheduler.add_job(func=self.block_trigger,
                          args=(lunchbreak, lunchbreak.trigger_proactive_usecase,),
                          kwargs={},
                          trigger='interval',
                          hours=1)
        github = self.store.get(Github)
        github.set_default_services()
        self.scheduler.add_job(func=self.block_trigger,
                          args=(github, github.trigger_proactive_usecase,),
                          kwargs={},
                          trigger='interval',
                          hours=1)

    def start(self):
        try:
            self.scheduler.start()

            print("Backend serving at port", SERVER_PORT)
            self.httpd.serve_forever()

            print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            self.httpd.shutdown()

if __name__ == '__main__':
    main = Main()
    main.start()
