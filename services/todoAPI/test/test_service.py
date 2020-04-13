import unittest
import os
import json

from .. import TodoistService, TodoistRemote, TodoistJSONRemote
from services.preferences import PrefService, PrefJSONRemote
from util import Singleton


@Singleton
class TodoistMockRemote(TodoistRemote):
    api_token = ""
    pref_service = PrefService(PrefJSONRemote())
    api = None

    def get_projects(self):
        dirname = os.path.dirname(__file__)
        response_json = json.load(open(dirname + "/mock_api_state.json"))
        return response_json["projects"]

    def get_todos(self, project_id):
        response_json = {}
        dirname = os.path.dirname(__file__)
        if project_id == 2230670456:
            response_json = json.load(open(dirname + "/mock_shopping_list.json"))
        elif project_id == 2230686946:
            response_json = json.load(open(dirname + "/mock_buerro.json"))
        elif project_id == 2230686957:
            response_json = json.load(open(dirname + "/mock_data_science.json"))
        return response_json

    def set_todos(self, items, p_id):
        pass

    def delete_todo(self, item, p_id):
        pass


class TestTodoistService(unittest.TestCase):
    if "DONOTMOCK" in os.environ:
        todoist_service = TodoistService.instance(TodoistJSONRemote.instance())
    else:
        print("Mocking remotes...")
        todoist_service = TodoistService.instance(TodoistMockRemote.instance())

    def test_get_project_names(self):
        projects = self.todoist_service.get_project_names()
        self.assertIsInstance(projects, list)

    def test_get_project_id(self):
        id = self.todoist_service.get_project_id("Shopping List")
        self.assertEqual(id, 2230670456)

    def test_get_project_task_names(self):
        test_string = "nutella"
        project_name = "Shopping List"

        self.todoist_service.set_project_todo([test_string], project_name)
        response = False
        text = str(self.todoist_service.get_project_task_names(project_name))
        if text.find(test_string) >= 0:
            response = True
        self.assertIs(response, True)
        self.todoist_service.delete_project_todo(test_string, project_name)

    def test_get_project_items_as_table(self):
        tasks = [
            {
                "content": "Task1",
                "due": {
                    "date": "2016-08-05T07:00:00Z",
                    "timezone": None,
                    "is_recurring": False,
                    "string": "tomorrow at 10:00",
                    "lang": "en",
                },
                "id": 102835615,
                "priority": 3,
            },
            {"content": "Task2", "due": None, "id": 102835617, "priority": 1},
        ]

        table = self.todoist_service.tasks_as_table(tasks)

        expected = {
            "Description": ["Task1", "Task2"],
            "Priority": [3, 1],
            "Due": ["tomorrow at 10:00", None],
        }

        self.assertEqual(table, expected)
