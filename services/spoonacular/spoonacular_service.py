import requests
import json
from ..preferences.pref_service import PrefService as ps

API_TOKEN = '0a3a6b562932438aaab0cb05460096de'
class SpoonacularRemote(ABC):
     @abstractmethod
    def search_recipe_by_id(self, id:str):
        pass

    @abstractmethod
    def search_recipe_by_ingredient(self, ingredient:str):
        pass

class SpoonacularJsonRemote(SpoonacularRemote):
    base_url = 'https://api.spoonacular.com/recipes'
    api_token = ''
    pref_service = ps.PrefService

    def __init__(self):
        pref_json = pref_service.get_preferences('general')
        api_token = pref_json['spoonacularAPIKey']

    def search_recipe_by_ingredient(self, ingredient):
        request_string = self.base_url + '/search?query=' + ingredient + '&number=1&apiKey=' + api_token
        response_string = requests.get(request_string)
        if response_string.status_code != 200:
            print('Error search by ingredient')
            print(request_string)
        response_json = response_string.json()
        return(response_json['results'][0]['id'])
    def search_recipe_by_id(self, id):
        request_string = 'https://api.spoonacular.com/recipes/' + str(id) +'/information?apiKey=' + API_TOKEN
        response_string = requests.get(request_string)
        if response_string.status_code != 200:
            print('Error search by ID')
            print(request_string)
        response_json = response_string.json()
        return response_json

class SpoonacularService:
    def get_ingredient_list_by_id(id):
        recipe_json = search_recipe_by_id(id)
        ingredient_list = []
        for ingredient in recipe_json['extendedIngredients']:
            ingredient_list.append(ingredient['name'] + ' ' + str(ingredient['amount']) + ' ' + ingredient['unit'])
        return ingredient_list
    
    def get_ingredient_list_by_ingredient(ingredient):
        return get_ingredient_list_by_id(search_recipe_by_ingredient(ingredient))
    
    def get_recipe_by_ingredient(ingredient):
        return search_recipe_by_id(search_recipe_by_ingredient(ingredient))





#Some example running code
# i=0
# for ingredient in getIngredientListByIngredient('pork'):
    # i+=1
    # print(str(i) + ': ' + ingredient)
