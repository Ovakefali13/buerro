import datetime
from datetime import timedelta, datetime as dt
from icalendar import Event as iCalEvent
from icalendar import Alarm, vDatetime

class Event(iCalEvent):

    def __init__(self, title:str, start:dt, end:dt, location:str=""):
        super().__init__()
        self.add('summary', title)
        self.add('dtstart', start)
        self.add('dtend', end)
        self.add('location', location)

        now = dt.now()
        self.add('dtstamp', now)
        self.add('uid', vDatetime(now).to_ical().decode('utf-8')+'@buerro.com')
        #self.add('uid', '00008')

    def format_date(self, dt):
        #2020-02-26T18:00:00Z
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_ical(self):
        ical = super().to_ical()
        ical = ical.replace(b'\r\n',b'\n').strip()
        ical = ical.decode('utf-8')
        return ical

    def set_reminder(self, reminder:timedelta):
        # all types: https://github.com/collective/icalendar/blob/2aa726714ff4a17e47b256da529640b201ebf66b/src/icalendar/prop.py 
        alarm = Alarm()
        alarm.add('trigger', -reminder)
        alarm.add('action', 'AUDIO')
        #TODO alarm.add('repeat', 2)
        self.add_component(alarm)
