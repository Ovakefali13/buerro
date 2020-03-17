
import json
import sys
import os
from github import Github
from datetime import datetime, timedelta, timezone
from abc import ABC, abstractmethod

from services.preferences import PrefService
from services.singleton import Singleton

class GithubRemote(ABC):
    @abstractmethod
    def get_notifications(self):
        pass
    @abstractmethod
    def connect(self):
        pass

class GithubRealRemote(GithubRemote):
    g = None
    def connect(self,key):
        self.g = Github(key)
    def get_notifications(self):
        notifications = []
        for n in self.g.get_user().get_notifications(all=True):
            notifications.append({'type':n.subject.type, 'title':n.subject.title})
        return notifications


class GithubService:
    remote = None
    pref = None

    def __init__(self, remote):
        self.pref = PrefService().get_preferences('github')
        
        self.remote = remote

    def get_notifications(self):
        return self.remote.get_notifications()
    
    def connect(self):
        self.remote.connect(self.pref['key'])