import unittest
import caldav
import os
from icalendar import Calendar
import random
import string
from datetime import datetime
import pytz

from .. import CalService, iCloudCaldavRemote, Event

class MockCaldavRemote(Calendar):
    def add_event(self, event:Event):
        self.add_component(event)
    def events(self):
        return self.subcomponents

class TestCalService(unittest.TestCase):
    remote = None
    if 'DONOTMOCK' in os.environ:
        remote = iCloudCaldavRemote()
    else:
        print('Mocking API...')
        remote = MockCaldavRemote()
        remote.add('prodid', '-//My calendar product//mxm.dk//')
        remote.add('version', '2.0')

    cal_service = CalService(remote)

    def test_add_and_get_event(self):
        summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event = Event(summary,
            start=datetime(2020, 2, 26, 18, 00),
            end=datetime(2020, 2, 26, 19, 00),
            location="My Hood")

        self.cal_service.add_event(event)
        all_events = self.cal_service.get_all_events()
        self.assertTrue(len(all_events) > 0)
        self.assertTrue(len(list(
            filter(lambda e: e['summary'] == summary, all_events))) > 0)
