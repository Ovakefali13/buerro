import unittest
import os
from icalendar import Calendar
import random
import string
from datetime import timedelta, datetime as dt

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
    def date_search(self, start, end):
        events = self.calendar.subcomponents
        return list(
           filter(lambda e: end > e['dtstart'].dt
                   and e['dtstart'].dt > start, events))

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
        event.add('dtstart', dt(2020, 2, 26, 18, 00).astimezone())
        event.add('dtend', dt(2020, 2, 26, 19, 00).astimezone())
        event.add('location', "My Hood")

        self.cal_service.add_event(event)
        all_events = self.cal_service.get_all_events()
        self.assertTrue(len(all_events) > 0)
        self.assertIsInstance(all_events[0], Event)
        self.assertTrue(any(e['summary'] == summary for e in all_events))

    def test_get_events_between(self):
        event = Event()
        summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event.add('summary', summary)
        event.add('dtstart', dt.now().astimezone() + timedelta(minutes=2))
        event.add('dtend', dt.now().astimezone() + timedelta(minutes=12))
        self.cal_service.add_event(event)

        start = dt.now().astimezone()
        end = (dt.now() + timedelta(minutes=15)).astimezone()
        all_events = self.cal_service.get_events_between(start, end)
        self.assertTrue(len(all_events) > 0)
        self.assertIsInstance(all_events[0], Event)
        self.assertTrue(any(e['summary'] == summary for e in all_events))
