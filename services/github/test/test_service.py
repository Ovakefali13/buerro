import unittest
import os
from datetime import datetime

from util import Singleton
from .. import GithubService, GithubRemote, GithubRealRemote

@Singleton
class GithubMockRemote(GithubRemote):
    def get_notifications(self):
        return [{'type': "Issue", 'title': "This is an issue"}]

    def connect(self, key):
        pass

class TestGithubService(unittest.TestCase):

    # Don't want to exceed the limit... mock on DONOTMOCK
    if 'DONOTMOCK_GITHUB' in os.environ:
        github_service = GithubService.instance(GithubRealRemote.instance())
    else:
        print("Mocking remotes...")
        github_service = GithubService.instance(GithubMockRemote.instance())

    def test_get_notifications_returns_valid_notification(self):
        self.github_service.connect()
        self.assertTrue(type(self.github_service.get_notifications()[0]['title']) is str)
        self.assertTrue(type(self.github_service.get_notifications()[0]['type']) is str)
