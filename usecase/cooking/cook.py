from datetime import datetime, timedelta
from dateutil import tz
import pytz

from services.preferences.pref_service import PrefService, PrefRemote, PrefJSONRemote

from services import SpoonacularService, TodoistService, YelpService, CalService
from services.cal import Event
from services.yelp import YelpRequest

class Cook:
    ingredient = 'pork'
    ingredient_list = []
    preferences_json = ''
    response_message = ''
    max_cooking_time = None
    event_time_start = None
    event_time_end = None
    cooking_event = None

    def __init__(self):
        self.pref_service = PrefService(PrefJSONRemote())

    def set_services(self,
                    todoist_service:TodoistService,
                    calendar_service:CalService,
                    yelp_service:YelpService,
                    spoonacle_service:SpoonacularService):
        self.todoist_service = todoist_service
        self.calendar_service = calendar_service
        self.yelp_service = yelp_service
        self.spoonacle_service = spoonacle_service

    def trigger_use_case(self, ingredient):
        if not self.todoist_service:
            raise Exception("Set services!")
        self.ingredient = ingredient
        self.load_preferences()
        #if self.check_for_time():
        if True:
            self.check_for_time()
            self.get_recipe()
            self.set_shopping_list()
            self.set_calender()
        else:
            self.not_time_to_cook()

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
        search_params.set_location('Jägerstraße 56, 70174 Stuttgart')
        search_params.set_time(cooking_timestamp)
        search_params.search_params['radius'] = 1000
        return_json = self.yelp_service.get_next_business(search_params)
        self.response_message = "A restaurant nearby is " + return_json['name'] + "and you can reach them at " + return_json['address'] + "(" + return_json['phone'] + ")"

    def get_response(self):
        return self.response_message

    def get_ingredient_list(self):
        return self.ingredient_list

    def get_cooking_event(self):
        return self.cooking_event

