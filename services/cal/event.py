import datetime
from datetime import timedelta, datetime as dt
from icalendar import Event as iCalEvent
from icalendar import Alarm, vDatetime

class Event(iCalEvent):
    def __init__(self, ical_ev:iCalEvent=None):
        if ical_ev:
            # TODO losing some information here
            super().__init__()
            for key in ical_ev:
                self.add(key, ical_ev[key])
        else:
            super().__init__()
            now = dt.now().astimezone()
            self.add('dtstamp', now)
            self.add('uid', vDatetime(now).to_ical().decode('utf-8')+'@buerro.com')
            #self.add('uid', '00008')

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

    @classmethod
    def from_ical(self, st):
        return self(super().from_ical(st))

