import requests
import json
from abc import ABC, abstractmethod
from ..preferences.pref_service import PrefService, PrefJSONRemote, PrefRemote

class SpoonacularRemote(ABC):
    @abstractmethod
    def search_recipe_by_id(self, id:str):
        pass

    @abstractmethod
    def search_recipe_by_ingredient(self, ingredient:str):
        pass

class SpoonacularJSONRemote(SpoonacularRemote):
    base_url = 'https://api.spoonacular.com/recipes/'
    api_token = ''
    pref_service = PrefService(PrefJSONRemote())

    def __init__(self):
        pref_json = self.pref_service.get_preferences("general")
        self.api_token = pref_json['spoonacularAPIKey']

    def search_recipe_by_ingredient(self, ingredient):
        request_string = self.base_url + 'search?query=' + ingredient + '&number=1&apiKey=' + self.api_token
        response_string = requests.get(request_string)
        if response_string.status_code != 200:
            print('Error search by ingredient')
            print(request_string)
        response_json = response_string.json()
        return(response_json['results'][0]['id'])
    def search_recipe_by_id(self, id):
        request_string = self.base_url + str(id) +'/information?apiKey=' + self.api_token
        response_string = requests.get(request_string)
        if response_string.status_code != 200:
            print('Error search by ID')
            print(request_string)
        response_json = response_string.json()
        return response_json

class SpoonacularService:
    remote = None
    def __init__(self, remote):
        self.remote = remote

    def get_ingredient_list_by_id(self, id):
        recipe_json = self.remote.search_recipe_by_id(id)
        ingredient_list = []
        for ingredient in recipe_json['extendedIngredients']:
            ingredient_list.append(ingredient['name'] + ' ' + str(ingredient['amount']) + ' ' + ingredient['unit'])
        return ingredient_list
    
    def get_ingredient_list_by_ingredient(self, ingredient):
        return self.get_ingredient_list_by_id(self.remote.search_recipe_by_ingredient(ingredient))
    
    def get_recipe_by_ingredient(self, ingredient):
        return self.remote.search_recipe_by_id(self.remote.search_recipe_by_ingredient(ingredient))

