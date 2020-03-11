import unittest
import os
from icalendar import Calendar
import random
import string
from datetime import timedelta, datetime as dt
import pytz

from .. import CalService, CaldavRemote, iCloudCaldavRemote, Event

class CaldavMockRemote(CaldavRemote):
    def create_calendar(self):
        self.calendar = Calendar()
        self.calendar.add('prodid', '-//My calendar product//mxm.dk//')
        self.calendar.add('version', '2.0')
    def __init__(self):
        self.create_calendar()
    def add_event(self, event:Event):
        self.calendar.add_component(event)
    def events(self):
        events = self.calendar.subcomponents
        return list(map(lambda e: Event(e), events))
    def purge(self):
        self.create_calendar()
    def date_search(self, start, end=None):
        events = self.events()
        if end is None:
            end = pytz.utc.localize(dt.max)

        def _starts_between(e:Event, start, end):
            return end > e['dtstart'].dt and e['dtstart'].dt > start

        return list(filter(lambda e: _starts_between(e, start, end), events))

class TestCalService(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.remote = None
        if 'DONOTMOCK' in os.environ:
            self.remote = iCloudCaldavRemote()
        else:
            print('Mocking Remote...')
            self.remote = CaldavMockRemote()

        self.cal_service = CalService(self.remote)

    @classmethod
    def setUp(self):
        self.remote.purge()

    def test_cant_add_with_too_few_params(self):
        summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event = Event()
        event.add('summary', summary)
        self.assertRaises(Exception, self.cal_service.add_event, event)

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

    def test_get_next_events(self):
        event = Event()
        summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event.add('summary', summary)
        event.add('dtstart', dt.now().astimezone() + timedelta(minutes=1))
        event.add('dtend', dt.now().astimezone() + timedelta(minutes=10))
        self.cal_service.add_event(event)

        event2 = Event()
        summary2 = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event2.add('summary', summary2)
        event2.add('dtstart', dt.now().astimezone() + timedelta(minutes=2))
        event2.add('dtend', dt.now().astimezone() + timedelta(minutes=10))
        self.cal_service.add_event(event2)

        next_events = self.cal_service.get_next_events()
        self.assertIsInstance(next_events[0], Event)
        self.assertEqual(next_events[0]['summary'], summary)
        self.assertEqual(next_events[1]['summary'], summary2)

