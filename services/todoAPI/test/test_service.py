import unittest
from .. import TodoistService, TodoistRemote, TodoistJSONRemote
from services.preferences import PrefService, PrefJSONRemote
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
            response_json = json.load(open(dirname + '/mock_shopping_list.json'))
        elif project_id == 2230686946:
            response_json = json.load(open(dirname + '/mock_software_engineering.json'))
        elif project_id == 2230686957:
            response_json = json.load(open(dirname + '/mock_data_science.json'))
        return response_json

    def set_todos(self, items, p_id):
        return str(items) + str(p_id)

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

    def test_get_software_engineering_id(self):
        id = self.todoist_service.get_software_engineering_id()
        self.assertEqual(id, 2230686946)
    
    def test_get_software_engineering_items(self):
        list = self.todoist_service.get_software_engineering_items()
        self.assertEqual(list, ['Hello World', 'Test Hello', 'Hello World', 'Test Hello', 'Hello World', 'Test Hello', 'Hello World', 'Test Hello'])

    def test_get_data_science_id(self):
        id = self.todoist_service.get_data_science_id()
        self.assertEqual(id, 2230686957)
    
    def test_get_data_science_items(self):
        list = self.todoist_service.get_data_science_items()
        self.assertEqual(list, [])
    
    def test_set_shopping_list(self):
        return_string = self.todoist_service.set_shopping_list(['Test', 'Test2'])
        self.assertEqual(return_string, "['Test', 'Test2']2230670456")

    def test_set_data_science(self):
        return_string = self.todoist_service.set_data_science(['Test', 'Test2'])
        self.assertEqual(return_string, "['Test', 'Test2']2230686957")
    
    def test_set_software_enigneering(self):
        return_string = self.todoist_service.set_software_enigneering(['Test', 'Test2'])
        self.assertEqual(return_string, "['Test', 'Test2']2230686946")
