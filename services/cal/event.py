import datetime
from icalendar import Event as iCalEvent
from icalendar import Alarm

class Event(iCalEvent):

    def __init__(self, title:str, start:datetime, end:datetime, location:str=""):
        super().__init__()
        self.add('summary', title)
        self.add('dtstart', start)
        self.add('dtend', end)
        self.add('location', location)
        self.add('dtstamp', datetime.datetime.now())

    def format_date(self, dt):
        #2020-02-26T18:00:00Z
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_ical(self):
        ical = super().to_ical()
        ical = ical.replace(b'\r\n',b'\n').strip()
        ical = ical.decode('utf-8')
        return ical

    # reminder should be a datetime.timedelta
    def set_reminder(self, reminder:datetime.timedelta):
        # all types: https://github.com/collective/icalendar/blob/2aa726714ff4a17e47b256da529640b201ebf66b/src/icalendar/prop.py 
        alarm = Alarm()
        alarm.add('trigger', -reminder)
        alarm.add('action', 'AUDIO')
        #TODO alarm.add('repeat', 2)
        self.add_component(alarm)
