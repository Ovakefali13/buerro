import unittest
from .. import TodoistService, TodoistRemote, TodoistJSONRemote
from ...preferences.pref_service import PrefService, PrefJSONRemote
import os
import json

class TodoistMOCKRemote(TodoistRemote):
    base_url = ''
    api_token = ''
    pref_service = PrefService(PrefJSONRemote())

    def __init__(self):
        pref_json = self.pref_service.get_preferences("cooking")
        self.api_token = pref_json['todoistAPIKey']

    def get_todos(self):
        return "Hello World"

    def get_search_options(self):
        search_options = 'includeIngredients=' + ''
        search_options += '&diet=' + ''
        search_options += '&maxReadyTime=' + ''
        search_options += '&apiKey=' + ''
        return search_options
    
    def set_todos(self):
        return "Hello World"

class TestTodoistService(unittest.TestCase):
    if 'DONOTMOCK' in os.environ:
        remote = TodoistJSONRemote()
    else:
        print("Mocking remotes...")
        remote = TodoistMOCKRemote()
    spoonacular_service = TodoistService(remote)

    def test_apiKey(self):
        self.assertEqual(self.remote.api_token, "2140845bf7131e21f43038f0db8e3090d8fd9ffc")
    