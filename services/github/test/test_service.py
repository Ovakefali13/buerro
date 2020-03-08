import unittest
from .. import GithubService, GithubRemote, GithubRealRemote
import os
from datetime import datetime

class GithubMockRemote(GithubRemote):
    def get_notifications(self):
        return [{'type': "Notification type", 'title': "Notification Title"}]

    def connect(self):
        pass

class TestGithubService(unittest.TestCase):
    if 'DONOTMOCK' in os.environ:
        remote = GithubRealRemote()
    else:
        print("Mocking remotes...")
        remote = GithubMockRemote()

    github_service = GithubService(remote)

    def test_get_notifications_returns_valid_notification(self):
        self.github_service.connect()
        print("Notifications:")
        self.assertTrue(type(self.github_service.get_notifications()[0]['title']) is str)
        self.assertTrue(type(self.github_service.get_notifications()[0]['type']) is str)
