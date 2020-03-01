import unittest
from datetime import datetime, timedelta

from .. import Event


ical_corr="""BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:Test Event
DTSTART:2020-02-26T18:00:00Z
DTEND:2020-02-26T19:00:00Z
LOCATION:Test Location
DTSTAMP:2020-02-26T16:00:00Z
UID:0123456789
END:VEVENT
END:VCALENDAR"""

ical_corr2="""BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:Test Event
DTSTART:2020-02-26T18:00:00Z
DTEND:2020-02-26T19:00:00Z
LOCATION:Test Location
DTSTAMP:2020-02-26T16:00:00Z
UID:0123456788
END:VEVENT
END:VCALENDAR"""

ical_corr_with_alarm="""BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:Test Event
DTSTART:2020-02-26T18:00:00Z
DTEND:2020-02-26T19:00:00Z
LOCATION:Test Location
DTSTAMP:2020-02-26T16:00:00Z
UID:0123456790
BEGIN:VALARM
TRIGGER:-PT15M
ACTION:AUDIO
END:VALARM
END:VEVENT
END:VCALENDAR"""

class TestEvent(unittest.TestCase):
    non_indicative_ical_fields = ['UID', 'DTSTAMP']

    def filter_ical(self, ical):
        rest = []
        for line in ical.splitlines():
            if all([(ignore_field not in line) for ignore_field in self.non_indicative_ical_fields]):
                if len(line) > 0:
                    rest.append(line)
        return rest

    def check_ical(self, expected, actual):
        #print(self.filter_ical(expected))
        #print(self.filter_ical(actual))
        return self.filter_ical(expected) == self.filter_ical(actual)

    def test_check_ical(self):
        self.assertTrue(self.check_ical(ical_corr, ical_corr2))

    def test_returns_correct_ical(self):
        name = "Test Event"
        start = datetime(2020, 2, 26, 18, 00)
        end = datetime(2020, 2, 26, 19, 00)
        location = "Test Location"
        event = Event(name, start, end, location)
        in_ical = event.to_ical()

        self.assertTrue(self.check_ical(ical_corr, in_ical))
        

    def test_returns_correct_ical_with_event(self):
        name = "Test Event"
        start = datetime(2020, 2, 26, 18, 00)
        end = datetime(2020, 2, 26, 19, 00)
        location = "Test Location"
        event = Event(name, start, end, location)
        event.set_reminder(timedelta(minutes=15))
        in_ical = event.to_ical()

        self.assertTrue(self.check_ical(ical_corr_with_alarm, in_ical))


if __name__ == '__main__':
    unittest.main()
