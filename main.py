from controller import ControllerFromArgs
from chatbot import Chatbot, BuerroBot
from http.server import HTTPServer
from datetime import datetime
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from usecase import Lunchbreak
from handler import UsecaseStore

hostName = "localhost"
serverPort = 9150


if __name__ == '__main__':

    def block_trigger(func, *args, **kwargs):
        if store.get_running() is not None:
            print('Blocked')
            store.register_fin_callback(func, *args, **kwargs)
        else:
            func(*args, **kwargs)

    def tick(test_var):
        print('tick ', test_var)

    def schedule_usecases():
        scheduler.add_job(func=block_trigger,
                          args=(Lunchbreak().trigger_proactive_usecase,),
                          trigger='interval',
                          hours=1)
        scheduler.add_job(func=block_trigger,
                          args=(tick,),
                          kwargs={'test_var': 123},
                          trigger='interval',
                          seconds=10)

    store = UsecaseStore.instance()

    scheduler = BackgroundScheduler(timezone=utc)
    schedule_usecases()
    scheduler.start()

    try:

        chatbot = Chatbot(BuerroBot())

        Controller = ControllerFromArgs(scheduler, chatbot)
        httpd = HTTPServer((hostName, serverPort),
            Controller)
        print("serving at port", serverPort)
        httpd.serve_forever()

        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        httpd.shutdown()

