from services.preferences.pref_service import PrefService, PrefRemote, PrefJSONRemote
from services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote, SpoonacularRemote
from services.todoAPI.todoist_service import TodoistService, TodoistRemote, TodoistJSONRemote
from services.yelp.yelp_service import YelpService, YelpRequest
from services.cal.cal_service import CalService, CaldavRemote, iCloudCaldavRemote
from datetime import datetime, timedelta
from dateutil import tz

class Cooking:
    ingredient = 'pork'
    preferences_json = ''
    pref_service = None
    spoonacle_service = None
    todoist_service = None
    yelp_service = None
    cal_service = None
    response_message = ''
    event_time = None

    def __init__(self, ingredient):
        self.trigger_use_case(ingredient)

    def trigger_use_case(self, ingredient):
        self.load_preferences()
        if self.check_for_time():
            self.response_message = self.get_recipe(ingredient)
            self.set_shopping_list()
            self.set_calender()
        else:
            self.response_message = self.not_time_to_cook()
        
    def check_for_time(self):
        self.cal_service = CalService(iCloudCaldavRemote())

        now = datetime.utcnow().date()
        end_of_day = datetime.utcnow().replace(hour=24, minute=0, second=0, microsecond=0)
        
        print("Now: " + now + " EndOfDay: " + end_of_day)
        # self.cal_service.get_max_available_time_between(now, end_of_day)

        max_cooking_time = self.preferences_json['maxCookingTime']
        ### Todo: Check in calender for 'maxCookingTime' time
        return False

    def load_preferences(self):
        self.pref_service = PrefService(PrefJSONRemote())
        self.preferences_json = self.pref_service.get_preferences('cooking')

    def get_recipe(self, ingredient):
        self.spoonacle_service = SpoonacularService(SpoonacularJSONRemote(), ingredient)
        return self.spoonacle_service.get_summary()

    def set_shopping_list(self):
        self.todoist_service = TodoistService(TodoistJSONRemote())
        ingredients = self.spoonacle_service.get_ingredients()
        self.todoist_service.set_project_todo(ingredients, "Shopping List")

    def set_calender(self):
        cookingTime = self.spoonacle_service.get_cookingTime()
        ### add time to calender ###
    
    def not_time_to_cook(self):
        ### not functioning API error ###
        search_params = YelpRequest()
        search_params.set_location('Jaegerstrasse 56, 70174 Stuttgart')
        search_params.set_time(1583160868)
        search_params.search_params['radius'] = 10
        
        self.yelp_service = YelpService.get_instance()
        return self.yelp_service.get_next_business(search_params)

    def get_response(self):
        return self.response_message

    