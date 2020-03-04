
import json
import sys
import os
from github import Github
from datetime import datetime, timedelta, timezone
from abc import ABC, abstractmethod

class GithubRemote(ABC):
    @abstractmethod
    def get_notifications(self):
        pass
    @abstractmethod
    def connect(self):
        pass

class GithubRealRemote(GithubRemote):
    g = None
    def connect(self):
        self.g = Github("f6a6862d177552fce7430e754286d9efa38c495f")
    def get_notifications(self):
        notifications = []
        for n in self.g.get_user().get_notifications(all=True):
            notifications.append({'type':n.subject.type, 'title':n.subject.title})
        return notifications


class GithubService:
    remote = None

    def __init__(self, remote):
        self.remote = remote

    def get_notifications(self):
        return self.remote.get_notifications()
    
    def connect(self):
        self.remote.connect()