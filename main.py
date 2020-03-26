from controller import ControllerFromArgs
from chatbot import Chatbot, BuerroBot
from http.server import HTTPServer
from datetime import datetime
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from usecase import Lunchbreak, WorkSession

usecaseByContext = {
    "lunch": Lunchbreak,
    "work": WorkSession
}

hostName = "localhost"
serverPort = 9150

def schedule_usecases(scheduler):
    scheduler.add_job(func=Lunchbreak().trigger_proactive_usecase,
                      args=(),
                      trigger='interval',
                      hours=1)

if __name__ == '__main__':
    scheduler = BackgroundScheduler(timezone=utc)
    schedule_usecases(scheduler)
    scheduler.start()

    try:

        chatbot = Chatbot(BuerroBot())

        Controller = ControllerFromArgs(scheduler, chatbot, usecaseByContext)
        httpd = HTTPServer((hostName, serverPort),
            Controller)
        print("serving at port", serverPort)
        httpd.serve_forever()

        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        httpd.shutdown()

