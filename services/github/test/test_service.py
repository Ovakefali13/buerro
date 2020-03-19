import unittest
from .. import GithubService, GithubRemote, GithubRealRemote
import os
from datetime import datetime

class GithubMockRemote(GithubRemote):
    def get_notifications(self):
        return [{'type': "Notification type", 'title': "Notification Title"}]

    def connect(self, key):
        pass

class TestGithubService(unittest.TestCase):

    github_service = GithubService.instance()

    if 'DONOTMOCK' in os.environ:
        pass
    else:
        print("Mocking remotes...")
        github_service.set_remote(GithubMockRemote())

    def test_get_notifications_returns_valid_notification(self):
        self.github_service.connect()
        print("Notifications:")
        self.assertTrue(type(self.github_service.get_notifications()[0]['title']) is str)
        self.assertTrue(type(self.github_service.get_notifications()[0]['type']) is str)
