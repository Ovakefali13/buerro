import unittest
from .. import TodoistService, TodoistRemote, TodoistJSONRemote
from services.preferences import PrefService, PrefJSONRemote
import os
import json

class TodoistMockRemote(TodoistRemote):
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
        pass
    def delete_todo(self, item, p_id):
        pass

class TestTodoistService(unittest.TestCase):
    todoist_service = TodoistService.instance()
    if 'DONOTMOCK' in os.environ:
        todoist_service.set_remote(TodoistJSONRemote())
    else:
        print("Mocking remotes...")
        todoist_service.set_remote(TodoistMockRemote())
    

    def test_get_project_names(self):
        projects = self.todoist_service.get_project_names()
        self.assertEqual(projects, ['Inbox', 'Shopping List', 'Data Science', 'Software Engineering'])

    def test_get_project_id(self):
        id = self.todoist_service.get_project_id("Shopping List")
        self.assertEqual(id, 2230670456)

    def test_get_project_items(self):
        test_string = 'nutella'
        project_name = "Shopping List"

        self.todoist_service.set_project_todo([test_string], project_name)
        response = False
        text = str(self.todoist_service.get_project_items(project_name))
        if text.find(test_string) >= 0:
            response = True
        self.assertIs(response, True)
        self.todoist_service.delete_project_todo(test_string, project_name)
