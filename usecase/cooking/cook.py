from services.preferences.pref_service import PrefService, PrefRemote, PrefJSONRemote
from services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote, SpoonacularRemote
from services.todoAPI.todoist_service import TodoistService, TodoistRemote, TodoistJSONRemote
from services.yelp.yelp_service import YelpService, YelpRequest
from services.cal.cal_service import CalService, CaldavRemote, iCloudCaldavRemote
from services.cal.event import Event
from datetime import datetime, timedelta
from dateutil import tz
import pytz

class Cook:
    ingredient = 'pork'
    preferences_json = ''
    pref_service = None
    spoonacle_service = None
    todoist_service = None
    yelp_service = None
    cal_service = None
    response_message = ''
    max_cooking_time = None
    event_time_start = None
    event_time_end = None

    def __init__(self):
        self.cal_service = CalService(iCloudCaldavRemote())
        self.pref_service = PrefService(PrefJSONRemote())
        self.yelp_service = YelpService.instance()
        self.todoist_service = TodoistService(TodoistJSONRemote())

    def trigger_use_case(self, ingredient):
        self.ingredient = ingredient
        self.load_preferences()
        if self.check_for_time():
            self.response_message = self.get_recipe()
            self.set_shopping_list()
            self.set_calender()
        else:
            self.response_message = self.not_time_to_cook()
        
    def check_for_time(self):
        now = datetime.now(pytz.utc)
        #naive = dt.replace(tzinfo=None)
        end_of_day = datetime.now(pytz.utc).replace(hour=23, minute=59, second=59)
        max_time, self.event_time_start, self.event_time_end = self.cal_service.get_max_available_time_between(now, end_of_day)
        self.max_cooking_time = self.preferences_json['maxCookingTime']
        if timedelta(minutes=self.max_cooking_time) > max_time:
            return False
        return True

    def load_preferences(self):
        self.preferences_json = self.pref_service.get_preferences('cooking')

    def get_recipe(self):
        self.spoonacle_service = SpoonacularService(SpoonacularJSONRemote(), self.ingredient)
        return self.spoonacle_service.get_summary()

    def set_shopping_list(self):
        ingredients = self.spoonacle_service.get_ingredients()
        self.todoist_service.set_project_todo(ingredients, "Shopping List")

    def set_calender(self):
        '''cooking_time = self.spoonacle_service.get_cookingTime()

        cooking_event = Event()
        cooking_event.set_title('Cooking')
        cooking_event.set_location('Home')
        cooking_event.set_start(self.event_time_start + timedelta(minutes=15))
        cooking_event.set_end(cooking_event.get_start() + timedelta(minutes=cooking_time))
        
        return self.cal_service.add_event(cooking_event)
        '''
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

    