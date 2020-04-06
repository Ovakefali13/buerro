import json
import sys
import os
from github import Github
from datetime import datetime, timedelta, timezone
from abc import ABC, abstractmethod

from services.preferences import PrefService
from util import Singleton

class GithubRemote(ABC):
    @abstractmethod
    def get_notifications(self):
        pass
    @abstractmethod
    def connect(self):
        pass

@Singleton
class GithubRealRemote(GithubRemote):
    g = None
    def connect(self,key):
        self.g = Github(key)

    def get_notifications(self):
        notifications = []
        for n in self.g.get_user().get_notifications(all=True):
            notifications.append({'type':n.subject.type, 'title':n.subject.title})
        return notifications

@Singleton
class GithubService:
    remote = None
    pref = None

    def __init__(self, remote:GithubRemote=None):
        if remote:
            self.remote = remote
        else:
            self.remote = GithubRealRemote.instance()

        self.pref = PrefService().get_preferences('github')

    def set_remote(self,remote):
        self.remote = remote

    def get_notifications(self):
        return self.remote.get_notifications()

    def connect(self):
        try:
            self.remote.connect(os.environ['GITHUB_API_KEY'])
        except:
            if fallback != None:
                self.remote = fallback
