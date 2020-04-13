import requests
import json
from abc import ABC, abstractmethod
import os

from ..preferences.pref_service import PrefService, PrefJSONRemote, PrefRemote
from util import Singleton

class SpoonacularRemote(ABC):
    @abstractmethod
    def search_recipe_by_id(self, id:str):
        pass

    @abstractmethod
    def search_recipe_by_ingredient(self, ingredient:str):
        pass

@Singleton
class SpoonacularJSONRemote(SpoonacularRemote):
    base_url = 'https://api.spoonacular.com/recipes/'
    api_token = ''
    pref_service = PrefService(PrefJSONRemote())
    diet = ''
    maxCookingTime = 90

    def __init__(self):
        pref_json = self.pref_service.get_preferences("cooking")

        self.api_token = os.environ['SPOONACULAR_API_KEY']
        self.diet = pref_json['diet']
        self.maxCookingTime = pref_json['maxCookingTime']

    def search_recipe_by_ingredient(self, ingredient):
        request_string = self.base_url + 'complexSearch?' + self.get_search_options(ingredient)
        response_string = requests.get(request_string)
        if response_string.status_code != 200:
            print('Error search by ingredient')
            print(request_string)
        response_json = response_string.json()
        return(response_json['results'][0]['id'])

    def get_search_options(self, ingredient):
        search_options = 'includeIngredients=' + ingredient
        search_options += '&diet=' + self.diet
        search_options += '&maxReadyTime=' + str(self.maxCookingTime)
        search_options += '&apiKey=' + self.api_token
        return search_options

    def search_recipe_by_id(self, id):
        request_string = self.base_url + str(id) +'/information?apiKey=' + self.api_token
        response_string = requests.get(request_string)
        if response_string.status_code != 200:
            print('Error search by ID')
            print(request_string)
        response_json = response_string.json()
        return response_json

@Singleton
class SpoonacularService:
    remote = None
    recipe_id = None
    ingredient = ''
    recipe = []

    def __init__(self, remote:SpoonacularRemote=None):
        if remote:
            self.remote = remote
        else:
            self.remote = SpoonacularJSONRemote.instance()

    def set_remote(self, remote):
        self.remote = remote

    def set_ingredient(self, ingredient):
        self.ingredient = ingredient

    def newRecipe(self):
        self.recipe_id = self.remote.search_recipe_by_ingredient(self.ingredient)
        self.recipe = self.remote.search_recipe_by_id(self.recipe_id)

    def get_ingredients(self):
        ingredient_list = []
        for ingredient in self.recipe['extendedIngredients']:
            ingredient_list.append(ingredient['name'] + ' ' + str(ingredient['amount']) + ' ' + ingredient['unit'])
        return ingredient_list
    
    def get_vegetarian(self):
        return self.recipe['vegetarian']
    
    def get_vegan(self):
        return self.recipe['vegan']
    
    def get_cookingTime(self):
        return self.recipe['readyInMinutes']
    
    def get_sourceURL(self):
        return self.recipe['sourceUrl']
    
    def get_healthScore(self):
        return self.recipe['healthScore']
    
    def get_title(self):
        return self.recipe['title']
    
    def get_summary(self):
        return self.recipe['summary']
