import unittest
import datetime
from usecase.cooking import Cook
from services.todoAPI.todoist_service import TodoistJSONRemote, TodoistService
from services.todoAPI.test.test_service import TodoistMockRemote
from services.cal.cal_service import CalService, CaldavRemote, iCloudCaldavRemote
from services.cal.test.test_service import CaldavMockRemote
from services.yelp.yelp_service import YelpService
from services.yelp.test.test_service import YelpMock
from services.spoonacular.spoonacular_service import SpoonacularService
from services.spoonacular.test.test_service import SpoonacularMOCKRemote
import os

class TestCooking(unittest.TestCase):
    MOCK_LOCATION = 'Jägerstraße 56, 70174 Stuttgart'
    use_case = None
    todoist_service = None
    calender_remote = None
    calender_service = None
    yelp_service = None

    @classmethod
    def setUpClass(self):
        if 'DONOTMOCK' in os.environ:
            self.use_case = Cook()
            self.todoist_service = TodoistService.instance()
            self.todoist_service.set_remote(TodoistJSONRemote())
            self.calender_remote = iCloudCaldavRemote()
            self.calender_service = CalService(self.calender_remote)  
        else:
            print("Mocking remotes...")
            self.use_case = Cook()
            
            self.calender_remote = CaldavMockRemote()
            self.calender_service = CalService(self.calender_remote)
            self.use_case.cal_service = self.calender_service

            self.yelp_service = YelpService.instance()
            self.yelp_service.set_remote(YelpMock())
            self.use_case.yelp_service = self.yelp_service

            self.todoist_service = TodoistService.instance()
            self.todoist_service.set_remote(TodoistMockRemote())
            self.use_case.todoist_service = self.todoist_service

            self.spoonacle_service = SpoonacularService.instance()
            self.spoonacle_service.set_remote(SpoonacularMOCKRemote())
            self.use_case.spoonacle_service = self.spoonacle_service
            
       
    def test_usecase(self):
        self.use_case.advance({'ingredient': 'pork'})
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
        self.calender_remote.purge()