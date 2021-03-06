import datetime
from datetime import timedelta, datetime as dt
from icalendar import Event as iCalEvent
from icalendar import Alarm, vDatetime
import pytz
import random
import string


class Event(iCalEvent):
    def __init__(self, ical_ev: iCalEvent = None):
        if ical_ev:
            # TODO losing some information here
            super().__init__()
            for key in ical_ev:
                self.add(key, ical_ev[key])
        else:
            super().__init__()
            now = dt.now().astimezone()
            self.add("dtstamp", now)
            random_id = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=12)
            )
            self.add(
                "uid",
                vDatetime(now).to_ical().decode("utf-8") + random_id + "@buerro.com",
            )
            # self.add('uid', '00008')

    def set_title(self, title: str):
        self.add("summary", title)

    def set_start(self, start: dt):
        self.add("dtstart", start)

    def set_end(self, end: dt):
        self.add("dtend", end)

    def set_location(self, location: str):
        self.add("location", location)

    def set_description(self, description: str):
        self.add("description", description)

    def set_reminder(self, reminder: timedelta):
        # all types: https://github.com/collective/icalendar/blob/2aa726714ff4a17e47b256da529640b201ebf66b/src/icalendar/prop.py
        alarm = Alarm()
        alarm.add("trigger", -reminder)
        alarm.add("action", "AUDIO")
        # TODO alarm.add('repeat', 2)
        self.add_component(alarm)

    def set_url(self, url: str):
        self.add("url", url)

    def set_description(self, note: str):
        self.add("description", note)

    def get_title(self):
        return self["summary"]

    def get_start(self):
        if hasattr(self["dtstart"], "dt"):
            return self["dtstart"].dt
        return self["dtstart"]

    def get_end(self):
        if hasattr(self["dtend"], "dt"):
            return self["dtend"].dt
        return self["dtend"]

    def get_location(self):
        if "location" in self:
            return self["location"]
        else:
            return None

    def to_ical(self):
        ical = super().to_ical()
        ical = ical.replace(b"\r\n", b"\n").strip()
        ical = ical.decode("utf-8")
        return ical

    @classmethod
    def from_ical(self, st):
        return self(super().from_ical(st))

    def check_parameters_and_raise(self):
        min_params = ("summary", "dtstart", "dtend")
        has_min = all(key in self for key in min_params)
        if not has_min:
            raise Exception("Event does not have minimal parameters " + min_params)

    def get_user_timezone(self):
        # in reality: look into DB
        return pytz.timezone("Europe/Berlin")

    def summarize(self):
        self.check_parameters_and_raise()
        start = self.get_start().astimezone(self.get_user_timezone()).strftime("%H:%M")
        end = self.get_end().astimezone(self.get_user_timezone()).strftime("%H:%M")
        if self.get_location():
            location = " at " + self.get_location()
        else:
            location = ""
        return f"{self.get_title()} from {start} until {end}{location}"
