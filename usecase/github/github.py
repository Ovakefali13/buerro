from datetime import datetime, timedelta
from dateutil import tz
from usecase.usecase import Reply, Usecase
import pytz
import re

from services.preferences.pref_service import PrefService, PrefRemote, PrefJSONRemote
from services import TodoistService, CalService, GithubService
from services.cal import Event
from services.yelp import YelpRequest

class Github(Usecase):
    user_asked = False
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
        if user_asked:
            return Reply({'message': "Some reply"})

    
    def is_finished(self):
        return self.finished
        