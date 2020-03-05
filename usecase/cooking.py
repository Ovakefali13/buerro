from services.preferences.pref_service import PrefService, PrefRemote, PrefJSONRemote
from services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote, SpoonacularRemote

class Cooking:
    ingredient = 'pork'
    preferences_json = ''
    pref_service = None
    spoonacle_service = None
    response_message = ''

    def __init__(self, ingredient):
        self.trigger_use_case(ingredient)

    def trigger_use_case(self, ingredient):
        self.load_preferences()
        if self.check_for_time():
            self.response_message = self.get_recipe(ingredient)
            self.set_shopping_list()
            self.set_calender()
        else:
            print("No time to cook")
        
    def check_for_time(self):
        maxCookingTime = self.preferences_json['maxCookingTime']
        ### Todo: Check in calender for 'maxCookingTime' time
        return True

    def load_preferences(self):
        self.pref_service = PrefService(PrefJSONRemote())
        self.preferences_json = self.pref_service.get_preferences('cooking')

    def get_recipe(self, ingredient):
        self.spoonacle_service = SpoonacularService(SpoonacularJSONRemote(), ingredient)
        return self.spoonacle_service.get_summary()

    def set_shopping_list(self):
        ingredients = self.spoonacle_service.get_ingredients()
        ### add ingredients to the todo list ###

    def set_calender(self):
        cookingTime = self.spoonacle_service.get_cookingTime()
        ### add time to calender ###
    def get_response(self):
        return self.response_message

    