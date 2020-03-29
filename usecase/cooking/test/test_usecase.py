import unittest
import datetime
import os

from usecase.cooking import Cook
from usecase.usecase import Reply
from services.todoAPI.todoist_service import TodoistJSONRemote, TodoistService
from services.todoAPI.test.test_service import TodoistMockRemote
from services.cal.cal_service import CalService, iCloudCaldavRemote
from services.cal.test.test_service import CalMockRemote
from services.yelp import YelpService, YelpServiceRemote
from services.yelp.test.test_service import YelpMock
from services.spoonacular import SpoonacularService, SpoonacularJSONRemote
from services.spoonacular.test.test_service import SpoonacularMOCKRemote

class TestCooking(unittest.TestCase):
    MOCK_LOCATION = 48.784611, 9.174310

    @classmethod
    def setUpClass(self):
        if 'DONOTMOCK' in os.environ:
            self.todoist_service = TodoistService.instance(
                TodoistJSONRemote.instance())
            self.calendar_service = CalService.instance(
                iCloudCaldavRemote.instance())
            self.yelp_service = YelpService.instance(
                YelpServiceRemote.instance())
            self.spoonacle_service = SpoonacularService.instance(
                SpoonacularJSONRemote.instance())
        else:
            print("Mocking remotes...")
            self.todoist_service = TodoistService.instance(
                TodoistMockRemote.instance())
            self.calendar_service = CalService.instance(
                CalMockRemote.instance())
            self.yelp_service = YelpService.instance(
                YelpMock.instance())
            self.spoonacle_service = SpoonacularService.instance(
                SpoonacularMOCKRemote.instance())

        self.use_case = Cook()
        self.use_case.set_services(
            todoist_service=self.todoist_service,
            calendar_service=self.calendar_service,
            yelp_service=self.yelp_service,
            spoonacle_service=self.spoonacle_service
        )

    def test_usecase(self):
        self.use_case.location = self.MOCK_LOCATION
        reply = self.use_case.advance('I like to cook with PORK')
        response_message = self.use_case.get_response()
        self.assertIsInstance(reply, Reply)
        self.assertEquals('pork', self.use_case.ingredient)
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
        self.calendar_service.purge()
