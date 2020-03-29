from datetime import datetime, timedelta
from dateutil import tz
from usecase.usecase import Reply, Usecase
import pytz
import re

from services.preferences.pref_service import PrefService, PrefRemote, PrefJSONRemote
from services.todoAPI.todoist_service import TodoistService
from services.yelp.yelp_service import YelpService
from services.cal.cal_service import CalService
from services.spoonacular.spoonacular_service import SpoonacularService
from services.cal import Event
from services.yelp import YelpRequest
from handler import Notification, NotificationHandler, LocationHandler, \
    UsecaseStore

class Cook(Usecase):
    ingredient = 'pork'
    ingredient_list = []
    preferences_json = ''
    response_message = ''
    response_url = ''
    response_ingedients = None
    max_cooking_time = None
    event_time_start = None
    event_time_end = None
    cooking_event = None
    no_time = False
    finished = False
    location = None

    def __init__(self):
        self.pref_service = PrefService(PrefJSONRemote())
        self.set_location()

    def set_services(self,
                    todoist_service:TodoistService,
                    calendar_service:CalService,
                    yelp_service:YelpService,
                    spoonacle_service:SpoonacularService):
        self.todoist_service = todoist_service
        self.calendar_service = calendar_service
        self.yelp_service = yelp_service
        self.spoonacle_service = spoonacle_service

    def set_default_services(self):
        self.todoist_service = TodoistService.instance()
        self.calendar_service = CalService.instance()
        self.yelp_service = YelpService.instance()
        self.spoonacle_service = SpoonacularService.instance()

    def advance(self, message):
        if not hasattr(self, 'todoist_service'):
            raise Exception("Set services!")
        message = message.lower()
        if self.no_time:
            p = re.compile(r'^([\w\-]..)')
            message = message + "fill"
            item = p.match(message)
            if str(item[0]) == 'yes':
                self.not_time_to_cook()
                self.no_time = False
                self.finished = True
                return Reply({'message': self.response_message})
            else:
                self.no_time = False
                self.finished = True
                return Reply({'message': 'Ok'})
        else:
            '''
            Tested with
            - I like to cook with pork
            - I have pork and would like to cook
            - I would like to cook and have pork
            - I have some pork and want to cook
            - Do I have time for cooking with pork ?
            - I like to cook with chicken
            - I like to cook with pork and some false information
            - I have chicken and want to cook
            '''
            p = re.compile(r'([\n\r]*with\s*([^\s\r]*)|[\n\r]*have\s(?!time|some)\s*([^\s\r]*))')
            list = p.findall(message)
            if list[0][1] == '':
                self.ingredient = list[0][2]
            else:
                self.ingredient = list[0][1]
            self.no_time = self.trigger_use_case()
            if self.no_time:
                self.finished = False
                return Reply({'message': 'No time to cook. Would you like to get a restaurant in your area? (Yes/No)'})
            else:
                self.finished = True
                return Reply({'message': self.response_message})
    
    def is_finished(self):
        return self.finished

    def trigger_use_case(self):
        self.load_preferences()
        if self.check_for_time():
            self.get_recipe()
            self.set_shopping_list()
            self.set_calender()
            return False
        else:
            return True

    def check_for_time(self):
        now = datetime.now(pytz.utc)
        end_of_day = datetime.now(pytz.utc).replace(hour=23, minute=59, second=59)
        max_time, start, end = self.calendar_service.get_max_available_time_between(
            now, end_of_day)
        self.event_time_start, self.event_time_end = start, end
        self.max_cooking_time = self.preferences_json['maxCookingTime']
        if timedelta(minutes=self.max_cooking_time) > max_time:
            return False
        return True

    def load_preferences(self):
        self.preferences_json = self.pref_service.get_preferences('cooking')

    def get_recipe(self):
        self.spoonacle_service.set_ingredient(self.ingredient)
        self.spoonacle_service.newRecipe()
        self.response_message = self.spoonacle_service.get_summary()
        self.response_url = self.spoonacle_service.get_sourceURL()
        self.response_ingedients = self.spoonacle_service.get_ingredients()

    def set_shopping_list(self):
        self.ingredient_list = self.spoonacle_service.get_ingredients()
        self.todoist_service.set_project_todo(self.ingredient_list, "Shopping List")

    def set_calender(self):
        cooking_time = self.spoonacle_service.get_cookingTime()
        self.cooking_event = Event()
        self.cooking_event.set_title('Cooking')
        self.cooking_event.set_location('Home')
        self.cooking_event.set_start(self.event_time_start + timedelta(minutes=15))
        self.cooking_event.set_end(self.cooking_event.get_start() + timedelta(minutes=cooking_time))
        self.cooking_event.set_url(self.spoonacle_service.get_sourceURL())
        self.cooking_event.set_description(self.response_message)

        return self.calendar_service.add_event(self.cooking_event)

    def not_time_to_cook(self):
        cooking_time = datetime.fromisoformat(str(datetime.utcnow().date()))
        cooking_timestamp = datetime.timestamp(cooking_time)

        search_params = YelpRequest()
        search_params.set_coordinates(self.location)
        search_params.set_time(cooking_timestamp)
        search_params.search_params['radius'] = 10000
        return_json = self.yelp_service.get_next_business(search_params)
        self.response_message = "A restaurant nearby is " + return_json['name'] + " and you can reach them at " + return_json['address'] + " (Phone: " + return_json['phone'] + ")"

    def get_response(self):
        return self.response_message

    def get_ingredient_list(self):
        return self.ingredient_list

    def get_cooking_event(self):
        return self.cooking_event

    def set_location(self):
        lh = LocationHandler.instance()
        lat, lon = lh.get()
        self.location = lat, lon
