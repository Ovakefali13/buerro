import unittest
from datetime import datetime, timedelta
import os
import pytz

from usecase.github import Github
from usecase.usecase import Reply
from services.todoAPI.todoist_service import TodoistJSONRemote, TodoistService
from services.todoAPI.test.test_service import TodoistMockRemote
from services.cal.cal_service import CalService, iCloudCaldavRemote
from services.cal.test.test_service import CalMockRemote
from services.github.github_service import GithubService, GithubRealRemote
from services.github.test.test_service import GithubMockRemote

class TestGithub(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        if 'DONOTMOCK' in os.environ:
            self.todoist_service = TodoistService.instance(
                TodoistJSONRemote.instance())
            self.calendar_service = CalService.instance(
                iCloudCaldavRemote.instance())
            self.github_service = GithubService.instance(fallback=GithubMockRemote.instance())
            
        else:
            print("Mocking remotes...")
            self.todoist_service = TodoistService.instance(
                TodoistMockRemote.instance())
            self.calendar_service = CalService.instance(
                CalMockRemote.instance())
            self.github_service = GithubService.instance(remote=GithubMockRemote.instance())

        self.use_case = Github()
        self.use_case.set_services(
            todoist_service=self.todoist_service,
            calendar_service=self.calendar_service,
            github_service = self.github_service,
        )
    
    def test_usecase_should_start_unfinished(self):
        self.assertFalse(self.use_case.finished)
    
    def test_usecase_handles_mock_notification(self):
        if 'DONOTMOCK' not in os.environ:
            self.use_case.trigger_proactive_usecase()
            self.assertTrue(self.use_case.issue)
        else:
            self.assertTrue(True)
    
    def test_usecase_handles_ignore_issue(self):
        if 'DONOTMOCK' not in os.environ:
            self.use_case.trigger_proactive_usecase()
            reply = self.use_case.advance("Ignore the issue.")
            self.assertEqual(reply, {'message': "Okay I will ignore the issue."})
        else:
            self.assertTrue(True)
    
    def test_usecase_handles_todo_and_calendar_entry(self):
        if 'DONOTMOCK' not in os.environ:
            self.use_case.trigger_proactive_usecase()
            reply = self.use_case.advance("Put the issue on my todo list.")
            self.assertEqual(reply, {'message': "I will add the issue to your todos."})
            reply = self.use_case.advance("Find space in my calendar for it.")
            self.assertTrue("calendar" in reply['message'])
        else:
            self.assertTrue(True)
    
    def test_usecase_finds_free_time_slot(self):
        if 'DONOTMOCK' not in os.environ:
            time_slot = self.use_case.find_available_time_slot()
            self.assertTrue(time_slot)
        else:
            self.assertTrue(True)
    
    def test_usecase_can_create_event(self):
        event = self.use_case.create_cal_event(datetime.now(pytz.utc), datetime.now(pytz.utc) + timedelta(minutes=60),"<Issue Name>")
        self.assertEqual(event.get_title(),"Work on <Issue Name>")

    def tearDown(self):
        self.calendar_service.purge()
