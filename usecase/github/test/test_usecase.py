import unittest
import datetime
import os

from usecase.github import Github
from usecase.usecase import Reply
from services.todoAPI.todoist_service import TodoistJSONRemote, TodoistService
from services.todoAPI.test.test_service import TodoistMockRemote
from services.cal.cal_service import CalService, iCloudCaldavRemote
from services.cal.test.test_service import CalMockRemote
from services.github.github_service import GithubService

class TestGithub(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        if 'DONOTMOCK' in os.environ:
            self.todoist_service = TodoistService.instance(
                TodoistJSONRemote.instance())
            self.calendar_service = CalService.instance(
                iCloudCaldavRemote.instance())
            # Create real GitHub Service
            
        else:
            print("Mocking remotes...")
            self.todoist_service = TodoistService.instance(
                TodoistMockRemote.instance())
            self.calendar_service = CalService.instance(
                CalMockRemote.instance())
            # Create mock Github Service

        self.use_case = Github()
        self.use_case.set_services(
            todoist_service=self.todoist_service,
            calendar_service=self.calendar_service,
            github_service = None,
        )

    def test_usecase(self):
        self.assertTrue(False)

    def tearDown(self):
        self.calendar_service.purge()
