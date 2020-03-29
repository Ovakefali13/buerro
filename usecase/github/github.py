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
    state = 0

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
            if self.state == 0:
                if "todo" in message:
                    return Reply({'message': "I will add the issue to your todos."})
                if "cal" in message:
                    time_slot = self.find_available_time_slot()
                    if time_slot:
                        self.state = 1
                        return Reply({'message': "I have found time in your calendar at " + str(time_slot['start']) + ". Would you like to work on the issue at that time?"})
                    else:
                        return Reply({'message': "Sadly I could not find a free time slot in your calendar :/"})
                if "ignore" in message or "nothing" in message:
                    return Reply({'message': "Okay I will ignore the issue."})
            if self.state == 1:
                if "yes" in message:
                    self.state = 0
                    issue = False
                    return Reply({'message': "Okay I will set an event in your calendar at that time :)"})
                if "no" in message:
                    self.state = 0
                    issue = False
                    return Reply({'message': "Okay maybe you want to look for a time yourself :)"})
        else:
            pass
    
    def create_cal_event(self, start, end, name):
        issue_event = Event()
        issue_event.set_title('Work on ' + name)
        issue_event.set_start(start)
        issue_event.set_end(end)
        self.calendar_service.add_event(issue_event)
        return issue_event

    def create_todo_item(self):
        self.todoist_service.set_project_todo("Issue name", "Github Issues")

    def find_available_time_slot(self):
        end_of_day = datetime.now(pytz.utc).replace(hour=23, minute=59, second=59)
        max_time, start, end = self.calendar_service.get_max_available_time_between(
            datetime.now(pytz.utc), end_of_day)
        time_slot = {'start':start, 'end':start + timedelta(minutes=60)}
        if timedelta(minutes=60) > max_time:
            return False
        return time_slot
    
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
        notification.add_message('What should I do about this new Github Issue?')
        notification.set_body('What should I do about this new Github Issue?')
        try:
            notification_handler = NotificationHandler.instance()
            notification_handler.push(notification)
        except:
            print("WARNING: Could not push notification. Maybe you are in test environment?")

    def is_finished(self):
        return self.finished
    