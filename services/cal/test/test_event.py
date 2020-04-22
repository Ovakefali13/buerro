import unittest
from datetime import datetime, timedelta
from icalendar import Event as iCalEvent

from .. import Event


ical_corr = """BEGIN:VEVENT
SUMMARY:Test Event
DTSTART;VALUE=DATE-TIME:20200226T180000
DTEND;VALUE=DATE-TIME:20200226T190000
LOCATION:Test Location
DTSTAMP:2020-02-26T16:00:00Z
UID:0123456789
END:VEVENT"""

ical_corr2 = """BEGIN:VEVENT
SUMMARY:Test Event
DTSTART;VALUE=DATE-TIME:20200226T180000
DTEND;VALUE=DATE-TIME:20200226T190000
LOCATION:Test Location
DTSTAMP:2020-02-26T16:00:00Z
UID:0123456788
END:VEVENT"""

ical_corr_with_alarm = """BEGIN:VEVENT
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
    non_indicative_ical_fields = ["UID", "DTSTAMP"]

    def filter_ical(self, ical):
        rest = []
        for line in ical.splitlines():
            if all(
                [
                    (ignore_field not in line)
                    for ignore_field in self.non_indicative_ical_fields
                ]
            ):
                if len(line) > 0:
                    rest.append(line)
        return rest

    def test_filter_ical(self):
        self.assertEqual(self.filter_ical(ical_corr), self.filter_ical(ical_corr2))

    def test_construct_from_ical_event(self):
        ical_event = iCalEvent()
        ical_event.add("summary", "Test Event")
        ical_event.add("dtstart", datetime(2020, 2, 26, 18, 00))
        ical_event.add("dtend", datetime(2020, 2, 26, 19, 00))
        ical_event.add("location", "Test Location")

        event = Event(ical_event)
        in_ical = event.to_ical()

        self.assertEqual(self.filter_ical(ical_corr), self.filter_ical(in_ical))

    def test_returns_correct_ical(self):
        event = Event()
        event.add("summary", "Test Event")
        event.add("dtstart", datetime(2020, 2, 26, 18, 00))
        event.add("dtend", datetime(2020, 2, 26, 19, 00))
        event.add("location", "Test Location")
        in_ical = event.to_ical()

        self.assertEqual(self.filter_ical(ical_corr), self.filter_ical(in_ical))

    def test_returns_correct_ical_with_event(self):
        event = Event()
        event.add("summary", "Test Event")
        event.add("dtstart", datetime(2020, 2, 26, 18, 00))
        event.add("dtend", datetime(2020, 2, 26, 19, 00))
        event.add("location", "Test Location")
        event.set_reminder(timedelta(minutes=15))
        in_ical = event.to_ical()

        self.assertEqual(
            self.filter_ical(ical_corr_with_alarm), self.filter_ical(in_ical)
        )

    def test_summarize(self):
        event = Event()
        event.add("summary", "Test Event")
        event.add("dtstart", datetime(2020, 2, 26, 18, 00))
        event.add("dtend", datetime(2020, 2, 26, 19, 00))
        event.add("location", "Test Location")

        time_regex = "[0-9]{1,2}:[0-9]{1,2}"
        regex = f"Test Event from {time_regex} until {time_regex} at Test Location"
        self.assertRegex(event.summarize(), regex)
