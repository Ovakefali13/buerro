from services.preferences.pref_service import PrefService, PrefRemote, PrefJSONRemote
from services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote, SpoonacularRemote
from services.spoonacular.test.test_service import SpoonacularMOCKRemote
from services.todoAPI.todoist_service import TodoistService, TodoistRemote, TodoistJSONRemote
from services.todoAPI.test.test_service import TodoistMockRemote
from services.yelp.yelp_service import YelpService, YelpRequest, YelpServiceRemote
from services.yelp.test.test_service import YelpMock
from services.cal.cal_service import CalService, CaldavRemote, iCloudCaldavRemote
from services.cal.test.test_service import CaldavMockRemote
from services.cal.event import Event
from datetime import datetime, timedelta
from dateutil import tz
import pytz

class Cook:
    ingredient = 'pork'
    ingredient_list = []
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
    cooking_event = None

    def __init__(self, mock:bool=False):
        if mock:
            self.cal_service = CalService.instance()
            self.cal_service.set_remote(CaldavMockRemote())
            self.pref_service = PrefService(PrefJSONRemote())
            self.yelp_service = YelpService.instance()
            self.yelp_service.set_remote(YelpMock())
            self.todoist_service = TodoistService.instance()
            self.todoist_service.set_remote(TodoistMockRemote())
            self.spoonacle_service = SpoonacularService.instance()
            self.spoonacle_service.set_remote(SpoonacularMOCKRemote())
        else:
            self.cal_service = CalService.instance()
            self.cal_service.set_remote(iCloudCaldavRemote())
            self.pref_service = PrefService(PrefJSONRemote())
            self.yelp_service = YelpService.instance()
            self.yelp_service.set_remote(YelpServiceRemote())
            self.todoist_service = TodoistService.instance()
            self.todoist_service.set_remote(TodoistJSONRemote())
            self.spoonacle_service = SpoonacularService.instance()
            self.spoonacle_service.set_remote(SpoonacularJSONRemote())

    def trigger_use_case(self, ingredient):
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
        max_time, self.event_time_start, self.event_time_end = self.cal_service.get_max_available_time_between(now, end_of_day)
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
        
        return self.cal_service.add_event(self.cooking_event)
    
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
    
