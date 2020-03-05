import unittest
from .. import SpoonacularService, SpoonacularRemote, SpoonacularJSONRemote
import os
import json

class SpoonacularMOCKRemote(SpoonacularRemote):

    def search_recipe_by_ingredient(self, ingredient):
        dirname = os.path.dirname(__file__)
        if ingredient == 'pork':
            response_json = json.load(open(dirname + '/mock_general_result_true.json'))
        else: 
            response_json = json.load(open(dirname + '/mock_general_result_false.json'))
        return(response_json['results'][0]['id'])

    def search_recipe_by_id(self, id):
        dirname = os.path.dirname(__file__)
        if id == 111364:
             response_json = json.load(open(dirname + '/mock_recipe_result_true.json'))
        else:
            response_json = json.load(open(dirname + '/mock_recipe_result_false.json'))
        return response_json

class TestSpoonacularService(unittest.TestCase):
    remote = SpoonacularJSONRemote()
    remote_mock = SpoonacularMOCKRemote()
    pref_service = SpoonacularService(remote)
    pref_service_mock = SpoonacularService(remote_mock)

    def test_apiKey(self):
        self.assertEqual(self.remote.api_token, "0a3a6b562932438aaab0cb05460096de")
    
    def test_get_recipe_by_ingredient(self):
        json = self.pref_service_mock.get_recipe_by_ingredient('pork')
        self.assertEqual(json['sourceUrl'], "http://www.food.com/recipe/pork-piccata-224998")
    
    # def test_get_ingredient_list_by_id(self):
    #    list = self.pref_service_mock.get_ingredient_list_by_id(111364)
    #    self.assertEqual(list, ['black pepper 0.125 teaspoon', 'capers 2.0 teaspoons', 'chicken broth 1.0 cup', 'fresh parsley 3.0 tablespoons', 'italian seasoned breadcrumbs 0.3333333333333333 cup', 'lemon juice 1.0 tablespoon', 'lemon rind 1.0 teaspoon', 'olive oil 1.0 tablespoon', 'pork chops 16.0 ounce', 'shallot 0.25 cup'])

    def test_get_ingredient_list_by_ingredient(self):
        list = self.pref_service_mock.get_ingredient_list_by_ingredient('pork')
        self.assertEqual(list, ['black pepper 0.125 teaspoon', 'capers 2.0 teaspoons', 'chicken broth 1.0 cup', 'fresh parsley 3.0 tablespoons', 'italian seasoned breadcrumbs 0.3333333333333333 cup', 'lemon juice 1.0 tablespoon', 'lemon rind 1.0 teaspoon', 'olive oil 1.0 tablespoon', 'pork chops 16.0 ounce', 'shallot 0.25 cup'])