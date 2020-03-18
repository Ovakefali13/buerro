import unittest
import datetime
from usecase.cooking import Cook
from services.todoAPI.todoist_service import TodoistJSONRemote, TodoistService
from services.todoAPI.test.test_service import TodoistMockRemote
from services.cal.cal_service import CalService, CaldavRemote, iCloudCaldavRemote
from services.cal.test.test_service import CaldavMockRemote
import os

class TestCooking(unittest.TestCase):
    MOCK_LOCATION = 'Jägerstraße 56, 70174 Stuttgart'
    use_case = None
    todoist_service = None
    calendar_remote = None
    calendar_service = None

    @classmethod
    def setUpClass(self):
        if 'DONOTMOCK' in os.environ:
            self.use_case = Cook()
            self.todoist_service = TodoistService.instance()
            self.todoist_service.set_remote(TodoistJSONRemote())
            self.calendar_remote = iCloudCaldavRemote()
            self.calendar_service = CalService.instance()
            self.calendar_service.set_remote(self.calendar_remote)
        else:
            print("Mocking remotes...")
            self.use_case = Cook(True)
            self.todoist_service = TodoistService.instance()
            self.todoist_service.set_remote(TodoistMockRemote())
            self.calendar_remote = CaldavMockRemote()
            self.calendar_service = CalService.instance()
            self.calendar_service.set_remote(self.calendar_remote)

    def test_trigger_usecase(self):
        self.use_case.trigger_use_case('pork')
        response_message = self.use_case.get_response()
        self.assertIs(type(response_message), str)

        project_name = "Shopping List"
        ingredient_list = self.use_case.get_ingredient_list()
        for item in ingredient_list:
           self.todoist_service.delete_project_todo(item, project_name)
        event = self.use_case.get_cooking_event()
        #event.delete()

    def test_not_time_to_cook(self):
        self.use_case.not_time_to_cook()

        response_message = self.use_case.get_response()

        self.assertIs(type(response_message), str)
        self.assertEquals(response_message[0] + response_message[1] + response_message[2], "A r")

    def tearDown(self):
        self.calendar_remote.purge()
