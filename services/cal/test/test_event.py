import unittest
from datetime import datetime, timedelta

from .. import Event


ical_corr="""BEGIN:VEVENT
SUMMARY:Test Event
DTSTART;VALUE=DATE-TIME:20200226T180000
DTEND;VALUE=DATE-TIME:20200226T190000
LOCATION:Test Location
DTSTAMP:2020-02-26T16:00:00Z
UID:0123456789
END:VEVENT"""

ical_corr2="""BEGIN:VEVENT
SUMMARY:Test Event
DTSTART;VALUE=DATE-TIME:20200226T180000
DTEND;VALUE=DATE-TIME:20200226T190000
LOCATION:Test Location
DTSTAMP:2020-02-26T16:00:00Z
UID:0123456788
END:VEVENT"""

ical_corr_with_alarm="""BEGIN:VEVENT
SUMMARY:Test Event
DTSTART;VALUE=DATE-TIME:20200226T180000
DTEND;VALUE=DATE-TIME:20200226T190000
LOCATION:Test Location
DTSTAMP:2020-02-26T16:00:00Z
UID:0123456790
BEGIN:VALARM
ACTION:AUDIO
TRIGGER:-PT15M
END:VALARM
END:VEVENT"""

class TestEvent(unittest.TestCase):
    non_indicative_ical_fields = ['UID', 'DTSTAMP']

    def filter_ical(self, ical):
        rest = []
        for line in ical.splitlines():
            if all([(ignore_field not in line) for ignore_field in self.non_indicative_ical_fields]):
                if len(line) > 0:
                    rest.append(line)
        return rest

    def test_filter_ical(self):
        self.assertEqual(self.filter_ical(ical_corr),
            self.filter_ical(ical_corr2))

    def test_returns_correct_ical(self):
        name = "Test Event"
        start = datetime(2020, 2, 26, 18, 00)
        end = datetime(2020, 2, 26, 19, 00)
        location = "Test Location"
        event = Event(name, start, end, location)
        in_ical = event.to_ical()

        self.assertEqual(self.filter_ical(ical_corr),
            self.filter_ical(in_ical))


    def test_returns_correct_ical_with_event(self):
        name = "Test Event"
        start = datetime(2020, 2, 26, 18, 00)
        end = datetime(2020, 2, 26, 19, 00)
        location = "Test Location"
        event = Event(name, start, end, location)
        event.set_reminder(timedelta(minutes=15))
        in_ical = event.to_ical()

        self.assertEqual(self.filter_ical(ical_corr_with_alarm),
            self.filter_ical(in_ical))


if __name__ == '__main__':
    unittest.main()
