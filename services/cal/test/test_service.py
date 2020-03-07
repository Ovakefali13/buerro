import unittest
import os
from icalendar import Calendar
import random
import string
from datetime import datetime
import pytz

from .. import CalService, CaldavRemote, iCloudCaldavRemote, Event

class MockCaldavRemote(CaldavRemote):
    def __init__(self):
        self.calendar = Calendar()
        self.calendar.add('prodid', '-//My calendar product//mxm.dk//')
        self.calendar.add('version', '2.0')
    def add_event(self, event:Event):
        self.calendar.add_component(event)
    def events(self):
        return self.calendar.subcomponents

class TestCalService(unittest.TestCase):
    remote = None
    if 'DONOTMOCK' in os.environ:
        remote = iCloudCaldavRemote()
    else:
        print('Mocking API...')
        remote = MockCaldavRemote()

    cal_service = CalService(remote)

    def test_add_and_get_event(self):
        summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', datetime(2020, 2, 26, 18, 00))
        event.add('dtend', datetime(2020, 2, 26, 19, 00))
        event.add('location', "My Hood")

        self.cal_service.add_event(event)
        all_events = self.cal_service.get_all_events()
        self.assertTrue(len(all_events) > 0)
        self.assertIsInstance(all_events[0], Event)
        self.assertTrue(any(e['summary'] == summary for e in all_events))
