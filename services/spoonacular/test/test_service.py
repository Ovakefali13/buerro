import unittest
from .. import SpoonacularService, SpoonacularRemote, SpoonacularJSONRemote
from ...preferences.pref_service import PrefService, PrefJSONRemote
import os
import json
import re

class SpoonacularMOCKRemote(SpoonacularRemote):
    api_token = ''
    pref_service = PrefService(PrefJSONRemote())
    test_ingredient = None

    def __init__(self):
        pref_json = self.pref_service.get_preferences("cooking")
        self.api_token = pref_json['spoonacularAPIKey']
        self.diet = pref_json['diet']
        self.maxCookingTime = pref_json['maxCookingTime']

    def search_recipe_by_ingredient(self, ingredient):
        dirname = os.path.dirname(__file__)
        if ingredient == self.test_ingredient:
            response_json = json.load(open(dirname + '/mock_general_result_true.json'))
        else: 
            response_json = json.load(open(dirname + '/mock_general_result_false.json'))
        return(response_json['results'][0]['id'])

    def get_search_options(self, ingredient):
        search_options = 'includeIngredients=' + ingredient
        search_options += '&diet=' + self.diet
        search_options += '&maxReadyTime=' + str(self.maxCookingTime)
        search_options += '&apiKey=' + self.api_token
        return search_options
    
    def search_recipe_by_id(self, id):
        dirname = os.path.dirname(__file__)
        if id == 111364:
             response_json = json.load(open(dirname + '/mock_recipe_result_true.json'))
        else:
            response_json = json.load(open(dirname + '/mock_recipe_result_false.json'))
        return response_json

class TestSpoonacularService(unittest.TestCase):
    if 'DONOTMOCK' in os.environ:
        remote = SpoonacularJSONRemote()
    else:
        print("Mocking remotes...")
        remote = SpoonacularMOCKRemote()
    
    test_ingredient = 'pork'
    remote.test_ingredient = test_ingredient
    spoonacular_service = SpoonacularService(remote,  test_ingredient)
    

    def test_get_sourceURL(self):
        import re
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        response = (re.match(regex, self.spoonacular_service.get_sourceURL()) is not None)
        self.assertEqual(response, True)
    
    def test_get_summary(self):
        response = self.spoonacular_service.get_summary()
        self.assertIs(type(response), str)

    def test_get_ingredients(self):
        response = False
        text = str(self.spoonacular_service.get_ingredients())
        if text.find(self.test_ingredient) >= 0:
            response = True
        self.assertIs(response, True)

    def test_get_healtScore(self):
        self.assertIs(type(self.spoonacular_service.get_healthScore()), float)
    
    def test_get_title(self):
        self.assertIs(type(self.spoonacular_service.get_title()), str)
    
    def test_get_cookingTime(self):
        self.assertIs(type(self.spoonacular_service.get_cookingTime()), int)
    
    def test_get_vegetarian(self):
        self.assertEqual(self.spoonacular_service.get_vegetarian(), False)
    
    def test_get_vegan(self):
        self.assertEqual(self.spoonacular_service.get_vegan(), False)
