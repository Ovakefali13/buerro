import unittest
import os
from icalendar import Calendar
import random
import string
from datetime import timedelta, datetime as dt
import pytz

from util import Singleton
from .. import CalService, CalRemote, iCloudCaldavRemote, Event

@Singleton
class CalMockRemote(CalRemote):
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
        if 'DONOTMOCK' in os.environ:
            self.cal_service = CalService.instance(iCloudCaldavRemote.instance())
        else:
            self.cal_service = CalService.instance(CalMockRemote.instance())
            print('Mocking Remote...')

    @classmethod
    def setUp(self):
        self.cal_service.purge()

    def now(self):
        return pytz.utc.localize(dt.now())

    def test_cant_add_with_too_few_params(self):
        summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event = Event()
        event.add('summary', summary)
        self.assertRaises(Exception, self.cal_service.add_event, event)

    def test_add_and_get_event(self):
        summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', pytz.utc.localize(dt(2020, 2, 26, 18, 00)))
        event.add('dtend', pytz.utc.localize(dt(2020, 2, 26, 19, 00)))
        event.add('location', "My Hood")
        event.set_reminder(timedelta(minutes=10))

        self.cal_service.add_event(event)
        all_events = self.cal_service.get_all_events()
        self.assertTrue(len(all_events) > 0)
        self.assertIsInstance(all_events[0], Event)
        self.assertTrue(any(e['summary'] == summary for e in all_events))

    def test_get_events_between(self):
        event = Event()
        summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event.add('summary', summary)
        event.add('dtstart', self.now() + timedelta(minutes=2))
        event.add('dtend', self.now() + timedelta(minutes=12))
        self.cal_service.add_event(event)

        start = self.now()
        end = self.now() + timedelta(minutes=15)
        all_events = self.cal_service.get_events_between(start, end)
        self.assertTrue(len(all_events) > 0)
        self.assertIsInstance(all_events[0], Event)
        self.assertTrue(any(e['summary'] == summary for e in all_events))

    def test_get_next_events(self):
        event = Event()
        summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event.add('summary', summary)
        event.add('dtstart', self.now() + timedelta(minutes=1))
        event.add('dtend', self.now() + timedelta(minutes=10))
        self.cal_service.add_event(event)

        event2 = Event()
        summary2 = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event2.add('summary', summary2)
        event2.add('dtstart', self.now() + timedelta(minutes=2))
        event2.add('dtend', self.now() + timedelta(minutes=10))
        self.cal_service.add_event(event2)

        next_events = self.cal_service.get_next_events()
        self.assertIsInstance(next_events[0], Event)
        self.assertEqual(next_events[0]['summary'], summary)
        self.assertEqual(next_events[1]['summary'], summary2)

    def test_get_max_available_time_between(self):
        def _chop_dt(date:dt):
            return date.replace(microsecond=0)

        start_time = self.now()
        end_time = self.now() + timedelta(hours=4)

        with self.subTest("no events today"):
            max_time, before, after = self.cal_service.get_max_available_time_between(
                start_time, end_time)
            self.assertEqual(max_time, end_time - start_time)
            self.assertEqual(before, start_time)
            self.assertEqual(after, end_time)

        event1 = Event()
        summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event1.add('summary', summary)
        event1.add('dtstart', start_time + timedelta(minutes=15))
        event1.add('dtend', start_time + timedelta(minutes=30))
        self.cal_service.add_event(event1)

        # which is 30 minutes from
        event2 = Event()
        summary2 = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event2_start_time = event1.get_end() + timedelta(minutes=30)
        event2.add('summary', summary2)
        event2.add('dtstart', event2_start_time)
        event2.add('dtend', event2_start_time + timedelta(minutes=15))
        self.cal_service.add_event(event2)

        with self.subTest(msg="rest of the day is empty"):
            max_time, before, after = self.cal_service.get_max_available_time_between(
                start_time, end_time)
            self.assertGreater(max_time, timedelta(minutes=30))
            self.assertEqual(_chop_dt(before), _chop_dt(event2.get_end()))
            self.assertEqual(after, end_time)

        with self.subTest(msg="rest of the day with events of shorter delta"):
            # each of which are 15 minutes apart
            next_event_start_time = event2.get_end() + timedelta(minutes=15)
            while next_event_start_time < end_time:
                next_ev_summary = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
                next_event = Event()
                next_event.add('summary', next_event)
                next_event.add('dtstart', next_event_start_time)
                next_event.add('dtend', next_event_start_time + timedelta(minutes=15))
                self.cal_service.add_event(next_event)

                next_event_start_time = next_event.get_end() + timedelta(minutes=15)

            max_time, before, after = self.cal_service.get_max_available_time_between(
                start_time, end_time)
            self.assertEqual(timedelta(minutes=30), max_time)
            self.assertEqual(_chop_dt(before), _chop_dt(event1.get_end()))
            self.assertEqual(_chop_dt(after), _chop_dt(event2.get_start()))
