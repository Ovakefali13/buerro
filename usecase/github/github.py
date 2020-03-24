from datetime import datetime, timedelta
from dateutil import tz
from usecase.usecase import Reply, Usecase
import pytz
import re

from services.preferences.pref_service import PrefService, PrefRemote, PrefJSONRemote
from services import TodoistService, CalService, GithubService
from services.cal import Event
from services.yelp import YelpRequest

from handler import Notification, NotificationHandler, LocationHandler

class Github(Usecase):
    issue = False
    user_asked = False
    seen_notifications = []
    finished = False

    def __init__(self):
        self.pref_service = PrefService(PrefJSONRemote())

    def set_services(self,
                    todoist_service:TodoistService,
                    calendar_service:CalService,
                    github_service:GithubService):
        self.todoist_service = todoist_service
        self.calendar_service = calendar_service
        self.github_service = github_service
    
    def set_default_services(self):
        self.todoist_service = TodoistService.instance()
        self.calendar_service = CalService.instance()
        self.github_service = GithubService.instance()
    
    def advance(self, message):
        if not self.todoist_service:
            raise Exception("Set services!")
        message = message.lower()
        if self.issue:
            if "todo" in message:
                return Reply({'message': "I will add the issue to your todos."})
            if "cal" in message:
                return Reply({'message': "Let me find a free time slot in your calendar."})
            if "ignore" in message or "nothing" in message:
                return Reply({'message': "Okay I will ignore the issue."})
                pass
        else:
            pass
    
    def trigger_proactive_usecase(self):
        self.github_service.connect()
        notifications = self.github_service.get_notifications()
        if notifications != []:
            for nf in notifications:
                if nf not in self.seen_notifications:
                    self.seen_notifications.append(nf)
                    self.issue = True
                    self.dispatch_proactive_notification_message(nf)
                    break
    
    def dispatch_proactive_notification_message(self,notification):
        notification = Notification('New Github Issue!')
        notification.add_message('What should I do about this new Github Issue? Open Buerro PDA and tell me!')
        notification.set_body('What should I do about this new Github Issue? Open Buerro PDA and tell me!')
        try:
            notification_handler = NotificationHandler.instance()
            notification_handler.push(notification)
        except:
            print("WARNING: Could not push notification. Maybe test environment?")

    def is_finished(self):
        return self.finished
    