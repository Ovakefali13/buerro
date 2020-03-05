from ..services.preferences.pref_service import PrefService, PrefRemote, PrefJSONRemote
from ..services.spoonacular.spoonacular_service import SpoonacularService, SpoonacularJSONRemote, SpoonacularRemote

class Recipe:
    ingredient = 'pork'
    preferences_json = ''
    pref_service
    spoonacle_service

    def __init__(self, ingredient):
        self.triggerUseCase(ingredient)

    def triggerUseCase(self, ingredient):
        self.loadPreferences()
        if self.checkForTime():
            self.getRecipe(ingredient)
        else:
            print("No time to cook")
        

    def checkForTime(self):
        normalCookingTime = self.preferences_json['normalCookingTime']
        print(normalCookingTime)
        ### Todo: Check in calender for 'normalCookingTime' time
        return True

    def loadPreferences(self):
        self.pref_service = PrefService(PrefJSONRemote())
        self.pref_service = self.pref_service.get_preferences('cooking')

    def getRecipe(self, ingredient):
        self.spoonacle_service = SpoonacularService(SpoonacularJSONRemote())

    def openMapsRoute(self, choice):
        
    def waitForUserRequest(self):
        
    def timeDiffInHours(self,date1, date2):
    