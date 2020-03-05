from ..services.preferences.pref_service import PrefService, PrefRemote, PrefJSONRemote
from ..services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote, SpoonacularRemote

class Recipe:
    ingredient = 'pork'
    preferences_json = ''
    pref_service
    spoonacle_service

    def __init__(self, ingredient):
        self.triggerUseCase(ingredient)

    def trigger_use_case(self, ingredient):
        self.load_preferences()
        if self.check_for_time():
            self.get_recipe(ingredient)
            self.set_shopping_list()
            self.set_calender()
        else:
            print("No time to cook")
        
    def check_for_time(self):
        normalCookingTime = self.preferences_json['normalCookingTime']
        print(normalCookingTime)
        ### Todo: Check in calender for 'normalCookingTime' time
        return True

    def load_preferences(self):
        self.pref_service = PrefService(PrefJSONRemote())
        self.pref_service = self.pref_service.get_preferences('cooking')

    def get_recipe(self, ingredient):
        self.spoonacle_service = SpoonacularService(SpoonacularJSONRemote(), ingredient)
        print(self.spoonacle_service.get_summary())

    def set_shopping_list(self):
        ingredients = self.spoonacle_service.get_ingredients()
        ### add ingredients to the todo list ###

    def set_calender(self):
        cookingTime = self.spoonacle_service.get_cookingTime()
        ### add time to calender ###
    