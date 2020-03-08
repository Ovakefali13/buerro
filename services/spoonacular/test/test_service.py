import unittest
from .. import SpoonacularService, SpoonacularRemote, SpoonacularJSONRemote
from ...preferences.pref_service import PrefService, PrefJSONRemote
import os
import json

class SpoonacularMOCKRemote(SpoonacularRemote):
    api_token = ''
    pref_service = PrefService(PrefJSONRemote())

    def __init__(self):
        pref_json = self.pref_service.get_preferences("cooking")
        self.api_token = pref_json['spoonacularAPIKey']
        self.diet = pref_json['diet']
        self.maxCookingTime = pref_json['maxCookingTime']

    def search_recipe_by_ingredient(self, ingredient):
        dirname = os.path.dirname(__file__)
        if ingredient == 'pork':
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
    spoonacular_service = SpoonacularService(remote, 'pork')

    def test_get_sourceURL(self):
        self.assertEqual(self.spoonacular_service.get_sourceURL(), "http://www.food.com/recipe/pork-piccata-224998")
    
    def test_get_summary(self):
        self.assertEqual(self.spoonacular_service.get_summary(), "Pork Piccatan is a <b>dairy free</b> main course. This recipe serves 4. For <b>$1.76 per serving</b>, this recipe <b>covers 19%</b> of your daily requirements of vitamins and minerals. One serving contains <b>251 calories</b>, <b>26g of protein</b>, and <b>12g of fat</b>. 2 people have made this recipe and would make it again. A mixture of pepper, center cut pork chops, chicken broth, and a handful of other ingredients are all it takes to make this recipe so tasty. To use up the lemon rind you could follow this main course with the <a href=\"https://spoonacular.com/recipes/lemon-almond-cake-with-lemon-curd-filling-198923\">Lemon-Almond Cake with Lemon Curd Filling</a> as a dessert. From preparation to the plate, this recipe takes approximately <b>17 minutes</b>. All things considered, we decided this recipe <b>deserves a spoonacular score of 68%</b>. This score is good. Similar recipes include <a href=\"https://spoonacular.com/recipes/pork-piccata-my-way-111393\">Pork Piccata My Way</a>, <a href=\"https://spoonacular.com/recipes/pork-piccata-111568\">Pork Piccata</a>, and <a href=\"https://spoonacular.com/recipes/pork-piccata-708193\">Pork Piccata</a>.")
       
    def test_get_ingredients(self):
        self.assertEqual(self.spoonacular_service.get_ingredients(), ['black pepper 0.125 teaspoon', 'capers 2.0 teaspoons', 'chicken broth 1.0 cup', 'fresh parsley 3.0 tablespoons', 'italian seasoned breadcrumbs 0.3333333333333333 cup', 'lemon juice 1.0 tablespoon', 'lemon rind 1.0 teaspoon', 'olive oil 1.0 tablespoon', 'pork chops 16.0 ounce', 'shallot 0.25 cup'])
    
    def test_get_healtScore(self):
        self.assertEqual(self.spoonacular_service.get_healthScore(), 17.0)
    
    def test_get_title(self):
        self.assertEqual(self.spoonacular_service.get_title(), "Pork Piccata")
    
    def test_get_cookingTime(self):
        self.assertEqual(self.spoonacular_service.get_cookingTime(), 17)
    
    def test_get_vegetarian(self):
        self.assertEqual(self.spoonacular_service.get_vegetarian(), False)
    
    def test_get_vegan(self):
        self.assertEqual(self.spoonacular_service.get_vegan(), False)
