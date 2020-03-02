import unittest
import caldav
import os
from icalendar import Event
import random
import string
from datetime import datetime
import pytz

from .. import CalService, get_icloud_calendar#, Event

class TestCalService(unittest.TestCase):
    calendar = None
    if 'DONOTMOCK' in os.environ:
        calendar = get_icloud_calendar()
    else:
        print('Mocking API...')
        principal = caldav.principal()
        calendar = principal.make_calendar(name="MockCal")

    cal_service = CalService(calendar)

    def test_add_and_get_event(self):
        name = ''.join(random.choices(string.ascii_uppercase + string.digits,k=6))
        event = Event()
        event.add('summary', name)
        event.add('dtstart', datetime(2005,4,4,8,0,0,tzinfo=pytz.utc))
        event.add('dtend', datetime(2005,4,4,10,0,0,tzinfo=pytz.utc))
        event.add('dtstamp', datetime(2005,4,4,0,10,0,tzinfo=pytz.utc))
        event['uid'] = '20050115T101010/27346262376@mxm.dk'
        """
        event.add('summary',
            name,
            start=datetime(2020, 2, 26, 18, 00),
            end=datetime(2020, 2, 26, 19, 00),
            location="My Hood")
        """

        self.cal_service.add_event(event)
        all_events = self.cal_service.get_all_events()
        self.assertTrue(len(all_events) > 0)
        self.assertTrue(len(list(
            filter(lambda e: e.name == name, all_events))) > 0)
