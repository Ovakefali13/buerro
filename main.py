from controller import ControllerFromArgs
from chatbot import Chatbot, BuerroBot
from http.server import HTTPServer
from datetime import datetime
import time
import os
from apscheduler.schedulers.background import BackgroundScheduler

from usecase import Lunchbreak, WorkSession

usecaseByContext = {
    "lunch": Lunchbreak,
    "work": WorkSession
}

hostName = "localhost"
serverPort = 9150

def get_last_location():
    # TODO controller -> (persist) last location -> get here
    # location = Controller.instance().get_last_location() 
    return (48.76533759999999, 9.161932799999999)

def schedule_usecases(scheduler):
    scheduler.add_job(func=tick, trigger='interval', seconds=3)
    scheduler.add_job(func=Lunchbreak().trigger_use_case,
                      args=(get_last_location(),),
                      trigger='interval',
                      hours=1)

def tick():
    print('Tick! The time is: %s' % datetime.now())

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    schedule_usecases(scheduler)
    scheduler.start()

    try:

        chatbot = Chatbot(BuerroBot())

        Controller = ControllerFromArgs(chatbot, usecaseByContext)
        httpd = HTTPServer((hostName, serverPort),
            Controller)
        print("serving at port", serverPort)
        httpd.serve_forever()

        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        httpd.shutdown()

