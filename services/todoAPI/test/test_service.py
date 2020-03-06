import unittest
from .. import TodoistService, TodoistRemote, TodoistJSONRemote
from ...preferences.pref_service import PrefService, PrefJSONRemote
import os
import json

class TodoistMOCKRemote(TodoistRemote):
    api_token = ''
    pref_service = PrefService(PrefJSONRemote())
    api = None

    def get_projects(self):
        dirname = os.path.dirname(__file__)
        response_json = json.load(open(dirname + '/mock_api_state.json'))
        return response_json['projects']

    def get_todos(self, project_id):
        response_json = {}
        dirname = os.path.dirname(__file__)
        if project_id == 2230670456:
            response_json = json.load(open(dirname + '/mock_shoppingList.json'))
        return response_json

    def set_todos(self, items, p_id):
        for item in items:
            self.api.items.add(item, project_id=p_id)
        self.api.commit()

class TestTodoistService(unittest.TestCase):
    if 'DONOTMOCK' in os.environ:
        remote = TodoistJSONRemote()
    else:
        print("Mocking remotes...")
        remote = TodoistMOCKRemote()
    todoist_service = TodoistService(remote)


    def test_get_project_names(self):
        projects = self.todoist_service.get_project_names()
        self.assertEqual(projects, ['Inbox', 'Shopping List', 'Data Science', 'Software Engineering'])
    
    def test_get_shopping_list_id(self):
        id = self.todoist_service.get_shopping_list_id()
        self.assertEqual(id, 2230670456)
    
    def test_get_shopping_list_items(self):
        list = self.todoist_service.get_shopping_list_items()
        self.assertEqual(list, ['Schokolade', 'Nutella', 'Tote Menschen'])
